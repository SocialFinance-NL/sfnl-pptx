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
    "dark_slate": "dk1",
    "white": "lt1",
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


def _apply_scheme_fill(xPr, slot: str) -> None:
    for tag in ("a:noFill", "a:solidFill", "a:gradFill", "a:blipFill", "a:pattFill", "a:grpFill"):
        for el in xPr.findall(qn(tag)):
            xPr.remove(el)
    solid = xPr.makeelement(qn("a:solidFill"), {})
    scheme = solid.makeelement(qn("a:schemeClr"), {"val": slot})
    solid.append(scheme)
    xPr.append(solid)


def set_scheme_fill(shape, accent: str) -> None:
    """Solid-fill a shape with a theme schemeClr (no hardcoded hex)."""
    _apply_scheme_fill(shape.fill._xPr, _scheme_slot(accent))


def set_fillformat_scheme(fill_format, accent: str) -> None:
    """Solid-fill any FillFormat (table cell, chart series, ...) with a theme schemeClr."""
    fill_format.solid()
    _apply_scheme_fill(fill_format._xPr, _scheme_slot(accent))


def set_scheme_line(shape, accent: str, width_pt: float | None = None) -> None:
    """Color a shape or connector line with a theme schemeClr."""
    slot = _scheme_slot(accent)
    if width_pt is not None:
        shape.line.width = Pt(width_pt)
    ln = shape.line._get_or_add_ln()
    for tag in ("a:noFill", "a:solidFill", "a:gradFill", "a:pattFill"):
        for el in ln.findall(qn(tag)):
            ln.remove(el)
    solid = ln.makeelement(qn("a:solidFill"), {})
    scheme = solid.makeelement(qn("a:schemeClr"), {"val": slot})
    solid.append(scheme)
    ln.append(solid)


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


def _clear_fill(spPr) -> None:
    for tag in ("a:noFill", "a:solidFill", "a:gradFill", "a:blipFill", "a:pattFill", "a:grpFill"):
        for el in spPr.findall(qn(tag)):
            spPr.remove(el)


def set_scheme_fill_tint(shape, accent: str, tint_pct: float) -> None:
    """Solid-fill with a pastel tint of a theme accent, via lumMod/lumOff (no hardcoded hex).

    ``tint_pct`` is 0-100: higher = lighter/more washed out (PowerPoint's "Lighter 80%"
    swatch is ``tint_pct=80``). Use for pastel card backgrounds in the reference-deck style.
    """
    slot = _scheme_slot(accent)
    spPr = shape.fill._xPr
    _clear_fill(spPr)
    solid = spPr.makeelement(qn("a:solidFill"), {})
    scheme = solid.makeelement(qn("a:schemeClr"), {"val": slot})
    scheme.append(scheme.makeelement(qn("a:lumMod"), {"val": str(round((100 - tint_pct) * 1000))}))
    scheme.append(scheme.makeelement(qn("a:lumOff"), {"val": str(round(tint_pct * 1000))}))
    solid.append(scheme)
    spPr.append(solid)


def set_scheme_fill_shade(shape, accent: str, shade_pct: float) -> None:
    """Solid-fill with a darker shade of a theme accent, via lumMod (no hardcoded hex).

    ``shade_pct`` is 0-100: higher = darker (PowerPoint's "Darker 25%" swatch is
    ``shade_pct=25``). Use for dark stat-banner bars and swimlane header bands.
    """
    slot = _scheme_slot(accent)
    spPr = shape.fill._xPr
    _clear_fill(spPr)
    solid = spPr.makeelement(qn("a:solidFill"), {})
    scheme = solid.makeelement(qn("a:schemeClr"), {"val": slot})
    scheme.append(scheme.makeelement(qn("a:lumMod"), {"val": str(round((100 - shade_pct) * 1000))}))
    solid.append(scheme)
    spPr.append(solid)


def resolve_accent(meta: dict | None, category: str | None, default: str) -> str:
    """Resolve a slide's accent, honoring an opt-in ``meta.accent_map`` (category -> accent).

    Decks that never set ``accent_map`` are unaffected: every slide keeps using ``default``
    (the deck's single ``meta.accent``), preserving the one-accent-per-deck mode.
    """
    if category:
        accent_map = (meta or {}).get("accent_map") or {}
        mapped = accent_map.get(category)
        if mapped in ACCENT_TO_SLOT:
            return mapped
    return default
