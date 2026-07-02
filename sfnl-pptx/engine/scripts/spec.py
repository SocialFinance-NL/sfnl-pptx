"""Deck-spec validation. The deck-spec is the single source of truth for a deck."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.components import load_components
from scripts.colors import ACCENT_TO_SLOT, ALLOWED_FONTS
from scripts.icons import ICON_NAMES

VALID_ACCENTS = {"orange", "grapefruit", "royal", "sky", "emerald", "navy"}
VALID_LANGS = {"nl", "en"}
VALID_FILL_COLORS = set(ACCENT_TO_SLOT)
FREEFORM_SHAPE_TYPES = {
    "rect", "rounded-rect", "oval", "triangle", "diamond", "pentagon", "hexagon",
    "chevron", "arrow", "donut", "pie",
}
FREEFORM_TYPES = FREEFORM_SHAPE_TYPES | {
    "line", "connector", "textbox", "icon", "table", "image", "group",
}
CONNECTOR_STYLES = {"straight", "elbow"}
CONNECTOR_ARROWS = {"none", "end", "both"}
ARROW_DIRECTIONS = {"right", "left", "up", "down"}
CHART_TYPES = {
    "column", "stacked-column", "bar", "stacked-bar", "line", "area",
    "pie", "donut", "scatter",
}


class SpecError(Exception):
    pass


def _coord_keys(ptype: str) -> tuple[str, ...]:
    if ptype in ("line", "connector"):
        return ("x1", "y1", "x2", "y2")
    if ptype in ("icon", "table", "image", "group"):
        return ("x", "y", "w")
    return ("x", "y", "w", "h")


def _validate_primitive_list(primitives, where: str, errors: list[str], depth: int = 0) -> None:
    if not isinstance(primitives, list) or not primitives:
        errors.append(f"{where}: requires a non-empty 'primitives' list")
        return
    for j, prim in enumerate(primitives):
        pwhere = f"{where}: primitives[{j}]"
        ptype = prim.get("type")
        if ptype not in FREEFORM_TYPES:
            errors.append(f"{pwhere}: type {ptype!r} must be one of {sorted(FREEFORM_TYPES)}")
            continue
        if ptype == "group":
            if depth >= 2:
                errors.append(f"{pwhere}: groups may nest at most 2 levels deep")
            else:
                _validate_primitive_list(prim.get("primitives"), pwhere, errors, depth + 1)
            continue
        for key in _coord_keys(ptype):
            if not isinstance(prim.get(key), (int, float)):
                errors.append(f"{pwhere}: {key!r} must be numeric (inches) for type {ptype!r}")
        color = prim.get("fill") or prim.get("color")
        if color and color not in VALID_FILL_COLORS:
            errors.append(f"{pwhere}: color {color!r} is not an allowed accent {sorted(VALID_FILL_COLORS)}")
        if ptype == "textbox":
            if not isinstance(prim.get("h"), (int, float)):
                errors.append(f"{pwhere}: 'h' must be numeric (inches) for type 'textbox'")
            if not prim.get("text") and not prim.get("bullets"):
                errors.append(f"{pwhere}: textbox requires 'text' or 'bullets'")
            if prim.get("bullets") is not None and not isinstance(prim["bullets"], list):
                errors.append(f"{pwhere}: 'bullets' must be a list of strings")
            font = prim.get("font")
            if font and font not in ALLOWED_FONTS:
                errors.append(f"{pwhere}: font {font!r} is not in allowed brand set {sorted(ALLOWED_FONTS)}")
        if ptype == "icon" and str(prim.get("icon", "")).lower() not in ICON_NAMES:
            errors.append(f"{pwhere}: icon {prim.get('icon')!r} is not one of {sorted(ICON_NAMES)}")
        if ptype == "arrow" and prim.get("direction") not in (None, *ARROW_DIRECTIONS):
            errors.append(f"{pwhere}: arrow direction {prim.get('direction')!r} must be one of {sorted(ARROW_DIRECTIONS)}")
        if ptype == "connector":
            if prim.get("style") not in (None, *CONNECTOR_STYLES):
                errors.append(f"{pwhere}: connector style {prim.get('style')!r} must be one of {sorted(CONNECTOR_STYLES)}")
            if prim.get("arrow") not in (None, *CONNECTOR_ARROWS):
                errors.append(f"{pwhere}: connector arrow {prim.get('arrow')!r} must be one of {sorted(CONNECTOR_ARROWS)}")
        if ptype == "table":
            rows = prim.get("rows")
            if not isinstance(rows, list) or not rows or not all(isinstance(r, list) and r for r in rows):
                errors.append(f"{pwhere}: table requires 'rows' as a non-empty list of non-empty lists")
            elif len({len(r) for r in rows}) > 1:
                errors.append(f"{pwhere}: table rows must all have the same number of cells")
        if ptype == "image" and not prim.get("path"):
            errors.append(f"{pwhere}: image requires 'path'")


def _validate_freeform_primitives(fill: dict, where: str, errors: list[str]) -> None:
    _validate_primitive_list(fill.get("primitives"), f"{where}: custom-freeform", errors)


def _validate_chart_native(fill: dict, where: str, errors: list[str]) -> None:
    chart_type = fill.get("chart_type")
    if chart_type not in CHART_TYPES:
        errors.append(f"{where}: chart_type {chart_type!r} must be one of {sorted(CHART_TYPES)}")
    series = fill.get("series")
 