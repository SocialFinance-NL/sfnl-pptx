"""Load and query the tagged component library."""
from __future__ import annotations

import json
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "assets" / "components" / "index.json"


def load_components() -> dict[str, dict]:
    entries = json.loads(INDEX.read_text(encoding="utf-8"))
    return {c["id"]: c for c in entries}


def find_components(type: str | None = None, tags: list[str] | None = None) -> list[dict]:
    result = []
    for c in load_components().values():
        if type is not None and c["type"] != type:
            continue
        if tags and not set(tags) <= set(c["tags"]):
            continue
        result.append(c)
    return result
