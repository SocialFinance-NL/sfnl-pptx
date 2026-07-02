"""Cheap brand/text/XML QA over a built deck (no rendering)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from pptx import Presentation

from scripts.colors import ALLOWED_FONTS

ASSETS = Path(__file__).resolve().parents[1] / "assets"

LEFTOVER_MARKERS = ("click to edit", "tijdelijke aanduiding", "text placeholder", "lorem ipsum")


def _brand_hexes() -> set[str]:
    pal = json.loads((ASSETS / "palette.json").read_text(encoding="utf-8"))
    return {info["hex"].upper() for info in pal["by_slot"].values()}


def qa_deck(pptx_path) -> dict:
    prs = Presentation(str(pptx_path))
    brand = _brand_hexes()
    findings = []
    for si, slide in enumerate(prs.slides):
        texts = []
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            t = shape.text_frame.text
            texts.append(t)
            if (shape.is_placeholder and slide.slide_layout.name != "Quote"
                    and shape.placeholder_format.idx in (0, 1, 13, 14)
                    and t.strip() and t != t.upper()):
                findings.append({"slide": si, "axis": "Design", "severity": "critical",
                                 "message": f"titel/subtitel niet in ALL CAPS: {t!r}"})
            low = t.lower()
            for marker in LEFTOVER_MARKERS:
                if marker in low:
                    findings.append({"slide": si, "axis": "Content", "severity": "critical",
                                     "message": f"leftover placeholder text: {t!r}"})
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    fn = run.font.name
                    if fn and fn not in ALLOWED_FONTS:
                        findings.append({"slide": si, "axis": "Design", "severity": "warn",
                                         "message": f"non-brand font {fn!r}"})
        if not any(t.strip() for t in texts):
            findings.append({"slide": si, "axis": "Content", "severity": "warn",
                             "message": "slide has no text"})
        xml = slide._element.xml
        for hexv in set(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', xml)):
            if hexv.upper() not in brand:
                findings.append({"slide": si, 