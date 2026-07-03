"""Lightweight structural validation for an unpacked .pptx workspace (see unpack.py).

Written for sfnl-deck-edit's OOXML escape hatch. This is NOT full OOXML schema (XSD)
conformance validation — it checks the failure modes that actually happen from
hand-editing slide XML: malformed XML, broken relationship references, and duplicate
IDs. After packing, the existing mandatory QA/render pass (scripts.qa_text,
scripts.render) already reopens the file via python-pptx / PowerPoint, which is the
strongest available check that the result is structurally sound.

Usage:
    python -m ooxml.scripts.validate workspace_dir
"""
from __future__ import annotations

import argparse
from pathlib import Path

from lxml import etree

_PARSER = etree.XMLParser(resolve_entities=False, no_network=True)
_RELS_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
_EXTERNAL_SCHEMES = ("http://", "https://", "mailto:")

# element local-name -> uniqueness scope ("file": unique within one XML file,
# "global": unique across the whole unpacked package)
_UNIQUE_ID_TAGS = {
    "sldid": "file",
    "sldmasterid": "global",
    "sldlayoutid": "global",
}


def _local_tag(element) -> str:
    tag = element.tag
    return tag.split("}")[-1].lower() if isinstance(tag, str) else str(tag).lower()


def check_well_formed(root_dir: Path) -> list[str]:
    errors = []
    for xml_file in sorted({*root_dir.rglob("*.xml"), *root_dir.rglob("*.rels")}):
        try:
            etree.parse(str(xml_file), parser=_PARSER)
        except etree.XMLSyntaxError as exc:
            errors.append(f"{xml_file.relative_to(root_dir)}: not well-formed — {exc}")
    return errors


def check_rels_targets(root_dir: Path) -> list[str]:
    errors = []
    for rels_file in sorted(root_dir.rglob("*.rels")):
        try:
            tree = etree.parse(str(rels_file), parser=_PARSER)
        except etree.XMLSyntaxError:
            continue  # already reported by check_well_formed
        # <part>/_rels/<file>.rels targets resolve relative to <part>/;
        # the root _rels/.rels targets resolve relative to the package root.
        base_dir = rels_file.parent.parent
        for rel in tree.getroot().findall("r:Relationship", namespaces=_RELS_NS):
            target = rel.get("Target") or ""
            if rel.get("TargetMode") == "External" or target.startswith(_EXTERNAL_SCHEMES):
                continue
            if not (base_dir / target).resolve().is_file():
                errors.append(f"{rels_file.relative_to(root_dir)}: broken reference to {target!r}")
    return errors


def check_unique_ids(root_dir: Path) -> list[str]:
    errors = []
    global_seen: dict[str, Path] = {}
    for xml_file in sorted(root_dir.rglob("*.xml")):
        try:
            tree = etree.parse(str(xml_file), parser=_PARSER)
        except etree.XMLSyntaxError:
            continue  # already reported by check_well_formed
        file_seen: set[str] = set()
        relative = xml_file.relative_to(root_dir)
        for element in tree.getroot().iter():
            scope = _UNIQUE_ID_TAGS.get(_local_tag(element))
            id_value = element.get("id")
            if scope is None or id_value is None:
                continue
            if scope == "file":
                if id_value in file_seen:
                    errors.append(f"{relative}: duplicate id {id_value!r} on <{_local_tag(element)}>")
                file_seen.add(id_value)
            elif id_value in global_seen:
                errors.append(
                    f"{relative}: id {id_value!r} on <{_local_tag(element)}> "
                    f"already used in {global_seen[id_value]}"
                )
            else:
                global_seen[id_value] = relative
    return errors


def validate(workspace_dir: str | Path) -> list[str]:
    root_dir = Path(workspace_dir)
    errors = check_well_formed(root_dir)
    errors += check_rels_targets(root_dir)
    errors += check_unique_ids(root_dir)
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace_dir", help="Directory previously produced by unpack.py")
    args = parser.parse_args()

    errors = validate(args.workspace_dir)
    if errors:
        print(f"FAILED — {len(errors)} issue(s):")
        for error in errors:
            print(f"  {error}")
        raise SystemExit(1)
    print("PASSED — no structural issues found")


if __name__ == "__main__":
    main()
