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
    if not isinstance(series, list) or not series:
        errors.append(f"{where}: chart-native requires a non-empty 'series' list")
        return
    for j, s in enumerate(series):
        swhere = f"{where}: series[{j}]"
        if chart_type == "scatter":
            for key in ("x_values", "y_values"):
                vals = s.get(key)
                if not isinstance(vals, list) or not all(isinstance(v, (int, float)) for v in vals):
                    errors.append(f"{swhere}: scatter series requires numeric list {key!r}")
        else:
            vals = s.get("values")
            if not isinstance(vals, list) or not vals or not all(isinstance(v, (int, float)) for v in vals):
                errors.append(f"{swhere}: 'values' must be a non-empty numeric list")
        color = s.get("color")
        if color and color not in VALID_FILL_COLORS:
            errors.append(f"{swhere}: color {color!r} is not an allowed accent {sorted(VALID_FILL_COLORS)}")
    if chart_type not in ("scatter",) and not fill.get("categories"):
        errors.append(f"{where}: chart-native requires 'categories' for chart_type {chart_type!r}")
    for color in fill.get("slice_colors", []) or []:
        if color not in VALID_FILL_COLORS:
            errors.append(f"{where}: slice_colors entry {color!r} is not an allowed accent {sorted(VALID_FILL_COLORS)}")


def validate_spec(spec: dict) -> list[str]:
    errors: list[str] = []
    comps = load_components()

    meta = spec.get("meta") or {}
    if not meta.get("title"):
        errors.append("meta.title is required")
    if meta.get("lang") not in VALID_LANGS:
        errors.append(f"meta.lang must be one of {sorted(VALID_LANGS)}")
    if meta.get("accent") and meta["accent"] not in VALID_ACCENTS:
        errors.append(f"meta.accent {meta.get('accent')!r} is not an allowed accent {sorted(VALID_ACCENTS)}")
    accent_map = meta.get("accent_map")
    if accent_map is not None:
        if not isinstance(accent_map, dict) or not accent_map:
            errors.append("meta.accent_map must be a non-empty object mapping category -> accent")
        else:
            for category, accent in accent_map.items():
                if accent not in VALID_ACCENTS:
                    errors.append(
                        f"meta.accent_map[{category!r}] = {accent!r} is not an allowed accent {sorted(VALID_ACCENTS)}"
                    )

    slides = spec.get("slides")
    if not slides:
        errors.append("spec must contain at least one slide")
        return errors

    seen_ids = set()
    for i, slide in enumerate(slides):
        where = f"slide[{i}] (id={slide.get('id')!r})"
        sid = slide.get("id")
        if not sid:
            errors.append(f"{where}: id is required")
        elif sid in seen_ids:
            errors.append(f"{where}: duplicate id")
        else:
            seen_ids.add(sid)
        if not slide.get("action_title"):
            errors.append(f"{where}: action_title is required (consultant rule)")
        category = slide.get("category")
        if category is not None and not isinstance(category, str):
            errors.append(f"{where}: category must be a string")
        cid = slide.get("component_id")
        if cid not in comps:
            errors.append(f"{where}: unknown component_id {cid!r}")
            continue
        # required slots: top-level string keys of content_schema must be present
        fill = slide.get("content_schema_fill") or {}
        for key, shape in comps[cid]["content_schema"].items():
            if isinstance(shape, str) and not fill.get(key):
                errors.append(f"{where}: missing required content slot {key!r} for component {cid!r}")
        if cid == "custom-freeform":
            _validate_freeform_primitives(fill, where, errors)
        if cid == "chart-native":
            _validate_chart_native(fill, where, errors)
    return errors


def load_spec(path) -> dict:
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_spec(spec)
    if errors:
        raise SpecError("invalid deck-spec:\n  - " + "\n  - ".join(errors))
    return spec
