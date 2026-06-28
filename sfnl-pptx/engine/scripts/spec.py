"""Deck-spec validation. The deck-spec is the single source of truth for a deck."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.components import load_components

VALID_ACCENTS = {"orange", "grapefruit", "royal", "sky", "emerald", "navy"}
VALID_LANGS = {"nl", "en"}


class SpecError(Exception):
    pass


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
        cid = slide.get("component_id")
        if cid not in comps:
            errors.append(f"{where}: unknown component_id {cid!r}")
            continue
        # required slots: top-level string keys of content_schema must be present
        fill = slide.get("content_schema_fill") or {}
        for key, shape in comps[cid]["content_schema"].items():
            if isinstance(shape, str) and not fill.get(key):
                errors.append(f"{where}: missing required content slot {key!r} for component {cid!r}")
    return errors


def load_spec(path) -> dict:
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_spec(spec)
    if errors:
        raise SpecError("invalid deck-spec:\n  - " + "\n  - ".join(errors))
    return spec
