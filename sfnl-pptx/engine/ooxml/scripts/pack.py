"""Repack an unpacked .pptx workspace (see unpack.py) back into a .pptx file.

Written for sfnl-deck-edit's OOXML escape hatch. Condenses the pretty-printed XML back
down (drops whitespace-only text nodes and comments — but never touches text *inside*
<a:t> run-text elements, where whitespace is meaningful) and re-zips.

Usage:
    python -m ooxml.scripts.pack workspace_dir output.pptx
"""
from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path

import defusedxml.minidom
from xml.dom.minidom import Node

# Elements whose text content is significant and must not be whitespace-stripped.
_PRESERVE_WHITESPACE_TAGS = {"a:t"}


def _strip_insignificant_whitespace(element) -> None:
    for child in list(element.childNodes):
        if child.nodeType == Node.COMMENT_NODE:
            element.removeChild(child)
        elif child.nodeType == Node.TEXT_NODE:
            if element.tagName not in _PRESERVE_WHITESPACE_TAGS and not child.data.strip():
                element.removeChild(child)
        elif child.nodeType == Node.ELEMENT_NODE:
            _strip_insignificant_whitespace(child)


def _condense_xml_file(xml_file: Path) -> None:
    dom = defusedxml.minidom.parseString(xml_file.read_bytes())
    _strip_insignificant_whitespace(dom.documentElement)
    xml_file.write_bytes(dom.toxml(encoding="UTF-8"))


def pack(workspace_dir: str | Path, output_path: str | Path) -> None:
    workspace_dir = Path(workspace_dir)
    output_path = Path(output_path)

    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / "content"
        shutil.copytree(workspace_dir, staged)

        for xml_file in [*staged.rglob("*.xml"), *staged.rglob("*.rels")]:
            _condense_xml_file(xml_file)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            output_path.unlink()
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for file_path in sorted(staged.rglob("*")):
                if file_path.is_file():
                    archive.write(file_path, file_path.relative_to(staged).as_posix())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace_dir", help="Directory previously produced by unpack.py")
    parser.add_argument("output", help="Output .pptx file")
    args = parser.parse_args()

    pack(args.workspace_dir, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
