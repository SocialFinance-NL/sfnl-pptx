"""schemeClr-first color + brand-font helpers. Colors are written as theme
references so slides auto-track the sjabloon palette; we never emit srgbClr."""
from __future__ import annotations

from pptx.oxml.ns import qn
from pptx.util import Pt

ACCENT_TO_SLOT = {
    "orange": "accent1",
    "grapefruit": "accent2",
    "royal": "accent3",
    "sky": "accent4",
    "emerald": "accent5",
    "navy": "dk2",
}

# Only these three may be set on a run by the build; QA accepts only these.
ALLOWED_FONTS = {"Montserrat Light", "Lato Light", "Gotham Bold"}

# Brand roles → font: display/headings = Gotham Bold, body/labels = Lato Light,
# secondary/quiet = Montserrat Light.


def _scheme_slot(accent: str) -> str:
    try:
        return ACCENT_TO_SLOT[accent]
    except KeyError:
        raise KeyError(f"unknown accent {accent!r}; choose from {sorted(ACCENT_TO_SLOT)}")


def set_scheme_fill(shape, accent: str) -> None:
    """Solid-fill a shape with a theme schemeClr (no hardcoded hex)."""
    slot = _scheme_slot(accent)
    spPr = shape.fill._xPr  # the <p:spPr> (or equivalent) element
    # remove any existing fill children
    for tag in ("a:noFill", "a:solidFill", "a:gradFill", "a:blipFill", "a:pattFill", "a:grpFill"):
        for el in spPr.findall(qn(tag)):
            spPr.remove(el)
    solid = spPr.makeelement(qn("a:solidFill"), {})
    scheme = solid.makeelement(qn("a:schemeClr"), {"val": slot})
    solid.append(scheme)
    spPr.append(solid)


def set_run_scheme_color(run, accent: str) -> None:
    """Color a text run with a theme schemeClr."""
    slot = _scheme_slot(accent)
    rPr = run._r.get_or_add_rPr()
    for el in rPr.findall(qn("a:solidFill")):
        rPr.remove(el)
    solid = rPr.makeelement(qn("a:solidFill"), {})
    scheme = solid.makeelement(qn("a:schemeClr"), {"val": slot})
    solid.append(scheme)
    rPr.insert(0, solid)


def set_run_font(run, font_name: str, size_pt: float | None = None, bold: bool | None = None) -> None:
    if font_name not in ALLOWED_FONTS:
        raise ValueError(f"font {font_name!r} not in allowed brand set {sorted(ALLOWED_FONTS)}")
    run.font.name = font_name
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.font.bold = bold
