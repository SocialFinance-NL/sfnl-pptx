"""Embed the official SFNL sjabloon's slide masters + layouts into a built deck.

Runs after ``build_deck.js`` writes the deck's .pptx. The generated deck carries exactly
one PptxGenJS-authored slide master with one layout; this script copies the sjabloon's
two masters and ~30 layouts in *alongside* it (never replacing or reordering what's
already there), so PowerPoint's New Slide / Layout gallery offers the official SFNL
layouts for slides a user adds by hand later. The deck's own generated slides are never
touched.

Works directly on the OOXML zip parts (zipfile + lxml), not python-pptx's object model:
python-pptx has no API for merging masters across presentations, and since this only
relocates whole parts (never edits slide/layout drawing content), none is needed.

Run from ``sfnl-pptx/engine``:

    python -m scripts.merge_template output/<datum>-<slug>/<slug>.pptx
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

from lxml import etree

ENGINE = Path(__file__).resolve().parents[1]
TEMPLATE = ENGINE / "assets" / "sfnl-sjabloon.potx"

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

CT_SLIDE_MASTER = "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"
CT_SLIDE_LAYOUT = "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"
CT_THEME = "application/vnd.openxmlformats-officedocument.theme+xml"
REL_SLIDE_MASTER = R_NS + "/slideMaster"
REL_SLIDE_LAYOUT = R_NS + "/slideLayout"
REL_THEME = R_NS + "/theme"
REL_IMAGE = R_NS + "/image"

# Only the two masters that slide layouts actually use. theme3/4 and the extra media
# they might pull in belong to the sjabloon's notes/handout masters and are irrelevant
# to the New Slide gallery.
SOURCE_MASTERS = ["slideMaster1.xml", "slideMaster2.xml"]
SOURCE_LAYOUT_COUNT = 30
SOURCE_THEMES = ["theme1.xml", "theme2.xml"]

EXTENSION_CONTENT_TYPES = {
    "png": "image/png", "jpeg": "image/jpeg", "jpg": "image/jpg",
    "emf": "image/x-emf", "wmf": "image/x-wmf", "gif": "image/gif",
    "tiff": "image/tiff", "bmp": "image/bmp", "svg": "image/svg+xml",
}


class TemplateMergeError(RuntimeError):
    """Raised when the sjabloon can't be embedded — callers should fail the build."""


def _serialize(root) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _next_index(deck_names, ct_text: str, folder: str, prefix: str) -> int:
    """Smallest starting index N such that ``ppt/<folder>/<prefix><N>.xml`` is free,
    checked against both physical part names and [Content_Types].xml Overrides (the
    build pipeline can leave orphaned Overrides for parts it no longer writes, so
    trusting physical names alone risks colliding with a stale-but-declared slot)."""
    part_pat = re.compile(rf"^ppt/{folder}/{prefix}(\d+)\.xml$")
    ct_pat = re.compile(rf'PartName="/ppt/{folder}/{prefix}(\d+)\.xml"')
    seen = {int(m.group(1)) for name in deck_names if (m := part_pat.match(name))}
    seen |= {int(m) for m in ct_pat.findall(ct_text)}
    return max(seen, default=0) + 1


def _max_rid(rels_text: str) -> int:
    return max((int(m) for m in re.findall(r'Id="rId(\d+)"', rels_text)), default=0)


def _max_global_id(presentation_xml: bytes, master_xmls: list[bytes]) -> int:
    """Highest numeric id= across sldId / sldMasterId / sldLayoutId. Per the OOXML
    spec these three share one presentation-wide id space."""
    text = presentation_xml.decode("utf-8")
    ids = [int(m) for m in re.findall(r'<p:(?:sldId|sldMasterId)\b[^>]*\bid="(\d+)"', text)]
    for master_xml in master_xmls:
        ids += [int(m) for m in re.findall(r'<p:sldLayoutId\b[^>]*\bid="(\d+)"', master_xml.decode("utf-8"))]
    return max(ids, default=0)


def _existing_layout_count(deck_names) -> int:
    return sum(1 for name in deck_names if re.match(r"^ppt/slideLayouts/slideLayout\d+\.xml$", name))


def merge(deck_path: Path, template_path: Path = TEMPLATE) -> None:
    deck_path = Path(deck_path)
    if not template_path.exists():
        raise TemplateMergeError(
            f"SFNL sjabloon not bundled at {template_path} — cannot embed brand layouts. "
            "This is a hard failure: a deck without the sjabloon's layouts does not meet "
            "the plugin's brand requirements."
        )

    with zipfile.ZipFile(template_path) as zf:
        tpl = {name: zf.read(name) for name in zf.namelist()}
    with zipfile.ZipFile(deck_path) as zf:
        deck = {name: zf.read(name) for name in zf.namelist()}

    existing_layouts = _existing_layout_count(deck.keys())
    merged = _merge_parts(deck, tpl)

    tmp_path = deck_path.with_suffix(".merging.pptx")
    with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in merged.items():
            zf.writestr(name, data)
    tmp_path.replace(deck_path)

    _round_trip_check(deck_path, expected_total_layouts=existing_layouts + SOURCE_LAYOUT_COUNT)


def _merge_parts(deck: dict, tpl: dict) -> dict:
    deck = dict(deck)
    ct_text = deck["[Content_Types].xml"].decode("utf-8")

    master_start = _next_index(deck.keys(), ct_text, "slideMasters", "slideMaster")
    layout_start = _next_index(deck.keys(), ct_text, "slideLayouts", "slideLayout")
    theme_start = _next_index(deck.keys(), ct_text, "theme", "theme")

    master_map = {
        f"slideMasters/{old}": f"slideMasters/slideMaster{master_start + i}.xml"
        for i, old in enumerate(SOURCE_MASTERS)
    }
    layout_map = {
        f"slideLayouts/slideLayout{n}.xml": f"slideLayouts/slideLayout{layout_start + n - 1}.xml"
        for n in range(1, SOURCE_LAYOUT_COUNT + 1)
    }
    theme_map = {
        f"theme/{old}": f"theme/theme{theme_start + i}.xml"
        for i, old in enumerate(SOURCE_THEMES)
    }

    used_media = sorted({
        m
        for rels_name in tpl
        if rels_name.startswith("ppt/slideMasters/_rels/") or rels_name.startswith("ppt/slideLayouts/_rels/")
        for m in re.findall(r'Target="\.\./media/([^"]+)"', tpl[rels_name].decode("utf-8"))
    })
    media_map = {f"media/{name}": f"media/sfnl-tmpl-{name}" for name in used_media}

    rename = {**master_map, **layout_map, **theme_map, **media_map}
    rel_type_map = {
        REL_SLIDE_MASTER: master_map,
        REL_SLIDE_LAYOUT: layout_map,
        REL_THEME: theme_map,
        REL_IMAGE: media_map,
    }

    def remap_rels(rels_xml: bytes) -> bytes:
        root = etree.fromstring(rels_xml)
        for rel in root:
            rel_type = rel.get("Type")
            target = rel.get("Target")
            mapping = rel_type_map.get(rel_type)
            if mapping and target and target.startswith("../"):
                key = target[len("../"):]
                if key in mapping:
                    rel.set("Target", "../" + mapping[key])
        return _serialize(root)

    # -- fresh, presentation-wide-unique ids for the incoming masters + layouts --
    # Must consider every slideMaster already in the deck (their sldLayoutId values
    # share the same id space) plus the incoming sjabloon masters, not just one side.
    existing_master_bodies = [
        data for name, data in deck.items()
        if re.match(r"^ppt/slideMasters/slideMaster\d+\.xml$", name)
    ]
    incoming_master_bodies = [tpl[f"ppt/slideMasters/{old}"] for old in SOURCE_MASTERS]
    next_id = _max_global_id(
        deck["ppt/presentation.xml"], existing_master_bodies + incoming_master_bodies
    ) + 1

    def take_id() -> int:
        nonlocal next_id
        value = next_id
        next_id += 1
        return value

    new_master_rids = []
    pres_rels_text = deck["ppt/_rels/presentation.xml.rels"].decode("utf-8")
    rid_counter = _max_rid(pres_rels_text)

    for old_name in SOURCE_MASTERS:
        rid_counter += 1
        new_master_rids.append(f"rId{rid_counter}")

        master_xml = tpl[f"ppt/slideMasters/{old_name}"]
        master_rels = tpl[f"ppt/slideMasters/_rels/{old_name}.rels"]

        master_root = etree.fromstring(master_xml)
        for layout_id_el in master_root.iter(f"{{{P_NS}}}sldLayoutId"):
            layout_id_el.set("id", str(take_id()))

        new_master_name = master_map[f"slideMasters/{old_name}"]
        deck[f"ppt/{new_master_name}"] = _serialize(master_root)
        deck[f"ppt/slideMasters/_rels/{Path(new_master_name).name}.rels"] = remap_rels(master_rels)

    for n in range(1, SOURCE_LAYOUT_COUNT + 1):
        old_name = f"slideLayouts/slideLayout{n}.xml"
        new_name = layout_map[old_name]
        deck[f"ppt/{new_name}"] = tpl[f"ppt/{old_name}"]  # layout bodies carry no ids to fix
        old_rels = f"ppt/slideLayouts/_rels/slideLayout{n}.xml.rels"
        deck[f"ppt/slideLayouts/_rels/{Path(new_name).name}.rels"] = remap_rels(tpl[old_rels])

    for old_name in SOURCE_THEMES:
        new_name = theme_map[f"theme/{old_name}"]
        deck[f"ppt/{new_name}"] = tpl[f"ppt/theme/{old_name}"]

    for old_name in used_media:
        new_name = media_map[f"media/{old_name}"]
        deck[f"ppt/{new_name}"] = tpl[f"ppt/media/{old_name}"]

    # -- presentation.xml: register the two new masters --
    pres_root = etree.fromstring(deck["ppt/presentation.xml"])
    sld_master_id_lst = pres_root.find(f"{{{P_NS}}}sldMasterIdLst")
    for rid in new_master_rids:
        el = etree.SubElement(sld_master_id_lst, f"{{{P_NS}}}sldMasterId")
        el.set("id", str(take_id()))
        el.set(f"{{{R_NS}}}id", rid)
    deck["ppt/presentation.xml"] = _serialize(pres_root)

    # -- presentation.xml.rels: point the new rIds at the new master parts --
    pres_rels_root = etree.fromstring(deck["ppt/_rels/presentation.xml.rels"])
    for rid, old_name in zip(new_master_rids, SOURCE_MASTERS):
        el = etree.SubElement(pres_rels_root, f"{{{PKG_REL_NS}}}Relationship")
        el.set("Id", rid)
        el.set("Type", REL_SLIDE_MASTER)
        el.set("Target", master_map[f"slideMasters/{old_name}"])
    deck["ppt/_rels/presentation.xml.rels"] = _serialize(pres_rels_root)

    # -- [Content_Types].xml: declare the new parts --
    ct_root = etree.fromstring(deck["[Content_Types].xml"])
    ct_ns = ct_root.nsmap[None] if None in ct_root.nsmap else list(ct_root.nsmap.values())[0]

    def add_override(part_name: str, content_type: str) -> None:
        el = etree.SubElement(ct_root, f"{{{ct_ns}}}Override")
        el.set("PartName", f"/ppt/{part_name}")
        el.set("ContentType", content_type)

    for new_name in master_map.values():
        add_override(new_name, CT_SLIDE_MASTER)
    for new_name in layout_map.values():
        add_override(new_name, CT_SLIDE_LAYOUT)
    for new_name in theme_map.values():
        add_override(new_name, CT_THEME)

    existing_defaults = {
        el.get("Extension").lower()
        for el in ct_root.findall(f"{{{ct_ns}}}Default")
    }
    needed_exts = {name.rsplit(".", 1)[1].lower() for name in used_media}
    for ext in sorted(needed_exts - existing_defaults):
        if ext not in EXTENSION_CONTENT_TYPES:
            raise TemplateMergeError(
                f"sjabloon media uses unrecognized extension .{ext} with no known "
                "OPC content type — add it to EXTENSION_CONTENT_TYPES before merging"
            )
        el = etree.SubElement(ct_root, f"{{{ct_ns}}}Default")
        el.set("Extension", ext)
        el.set("ContentType", EXTENSION_CONTENT_TYPES[ext])
    deck["[Content_Types].xml"] = _serialize(ct_root)

    return deck


def _round_trip_check(deck_path: Path, expected_total_layouts: int) -> None:
    """Cheap corruption check: python-pptx must be able to re-open the merged file
    and see every expected slide layout. This does not prove PowerPoint itself will
    accept the file without a repair prompt — see scripts.render for that check."""
    from pptx import Presentation

    try:
        prs = Presentation(str(deck_path))
    except Exception as exc:  # noqa: BLE001 - re-raised with build-facing context
        raise TemplateMergeError(f"merged deck failed to re-open with python-pptx: {exc}") from exc

    total_layouts = sum(len(master.slide_layouts) for master in prs.slide_masters)
    if total_layouts != expected_total_layouts:
        raise TemplateMergeError(
            f"expected {expected_total_layouts} slide layouts after merge, found {total_layouts}"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.merge_template <deck.pptx>", file=sys.stderr)
        sys.exit(2)
    merge(Path(sys.argv[1]))
    print("merged SFNL sjabloon layouts into", sys.argv[1])
