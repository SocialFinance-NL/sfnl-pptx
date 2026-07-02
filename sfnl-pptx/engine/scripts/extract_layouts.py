"""Catalog every sjabloon slide layout and its placeholder indices, so the build
can address placeholders by idx (title/section layouts use idx 13/14, not 0/1)."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.office.template import load_template_presentation

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def extract_layouts() -> list[dict]:
    prs = load_template_presentation()
    out: list[dict] = []
    for mi, master in enumerate(prs.slide_masters):
        for li, layout in enumerate(master.slide_layouts):
            phs = [
                {
                    "idx": ph.placeholder_format.idx,
                    "type": str(ph.placeholder_format.type),
                    "name": ph.name,
                }
                for ph in layout.placeholders
            ]
            out.append(
                {"name": layout.name, "master_index": mi, "layout_index": li, "placeholders": phs}
            )
    (ASSETS / "layouts.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def find_layout(prs, name: str):
    """Return the first slide layout matching `name` across all masters."""
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            if layout.name == name:
                return layout
    raise KeyError(f"layout not found in sjabloon: {name!r}")


if __name__ == "__main__":
    extract_layouts()
    print("wrote", ASSETS / "layouts.json")
