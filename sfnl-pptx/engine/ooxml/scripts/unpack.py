"""Unpack a .pptx into a directory of pretty-printed XML, for hand-editing.

Written for sfnl-deck-edit's OOXML escape hatch (edits scripts.inventory/replace/rearrange
and scripts.insert_chrome_slide can't reach — tables, charts, grouped shapes, image swaps).
Pair with pack.py (repack) and validate.py (check before repacking).

Usage:
    python -m ooxml.scripts.unpack input.pptx workspace_dir
"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

import defusedxml.minidom


def _extract_safely(pptx_path: str | Path, output_dir: Path) -> None:
    """Extract a .pptx (zip) archive, rejecting entries that would escape output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_root = output_dir.resolve()
    with zipfile.ZipFile(pptx_path) as archive:
        for member in archive.namelist():
            destination = (output_root / member).resolve()
            if not destination.is_relative_to(output_root):
                raise ValueError(f"Refusing to extract unsafe zip entry: {member}")
        archive.extractall(output_root)


def _pretty_print_xml(output_dir: Path) -> None:
    for xml_file in [*output_dir.rglob("*.xml"), *output_dir.rglob("*.rels")]:
        dom = defusedxml.minidom.parseString(xml_file.read_bytes())
        xml_file.write_bytes(dom.toprettyxml(indent="  ", encoding="utf-8"))


def unpack(pptx_path: str | Path, output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    _extract_safely(pptx_path, output_dir)
    _pretty_print_xml(output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Input .pptx file")
    parser.add_argument("output_dir", help="Directory to unpack into")
    args = parser.parse_args()

    unpack(args.input, args.output_dir)
    print(f"Unpacked {args.input} into {args.output_dir}")


if __name__ == "__main__":
    main()
