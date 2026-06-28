"""Deterministically build a .pptx from a validated deck-spec, on a clone of the
sjabloon. Template slides clone branded layouts and fill placeholders by idx;
custom slides draw on the blank `Leeg` layout with schemeClr colors."""
from __future__ import annotations

from pathlib import Path

from pptx.util import Emu, Inches, Pt
from pptx.enum.text import PP_ALIGN

from scripts.office.template import load_template_presentation
from scripts.extract_layouts import find_layout
from scripts.components import load_components
from scripts.spec import validate_spec, SpecError
from scripts.colors import set_run_scheme_color, set_run_font

SLIDE_W = Emu(12192000)
SLIDE_H = Emu(6858000)


def _placeholder_by_idx(slide, idx: int):
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == idx:
            return ph
    raise KeyError(f"placeholder idx {idx} not found on slide")


def _set_placeholder_text(ph, value) -> None:
    tf = ph.text_frame
    if isinstance(value, list):
        tf.text = str(value[0]) if value else ""
        for item in value[1:]:
            p = tf.add_paragraph()
            p.text = str(item)
    else:
        tf.text = str(value)


def _build_template_slide(prs, comp, slide_spec):
    layout = find_layout(prs, comp["source_layout"])
    slide = prs.slides.add_slide(layout)
    fill = slide_spec.get("content_schema_fill", {})
    for slot_name, slot_def in comp["slots"].items():
        if slot_name in fill:
            ph = _placeholder_by_idx(slide, slot_def["placeholder_idx"])
            _set_placeholder_text(ph, fill[slot_name])
    return slide


def _add_title(slide, text, accent):
    box = slide.shapes.add_textbox(Inches(0.9), Inches(0.6), Inches(11.5), Inches(1.0))
    run = box.text_frame.paragraphs[0].add_run()
    run.text = text
    set_run_font(run, "Gotham Bold", size_pt=28, bold=True)
    set_run_scheme_color(run, "navy")
    return slide


def _build_custom_slide(prs, comp, slide_spec, accent):
    slide = prs.slides.add_slide(find_layout(prs, "Leeg"))
    fill = slide_spec.get("content_schema_fill", {})
    if fill.get("title"):
        _add_title(slide, fill["title"], accent)

    if comp["id"] == "kpi-trio":
        kpis = fill.get("kpis", [])[:3]
        n = max(len(kpis), 1)
        col_w = Inches(3.6)
        gap = Inches(0.4)
        total = col_w * n + gap * (n - 1)
        start = Emu(int((SLIDE_W - total) / 2))
        y = Inches(2.6)
        for i, kpi in enumerate(kpis):
            x = Emu(int(start + i * (col_w + gap)))
            vbox = slide.shapes.add_textbox(x, y, col_w, Inches(1.4))
            vrun = vbox.text_frame.paragraphs[0].add_run()
            vrun.text = str(kpi.get("value", ""))
            vbox.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            set_run_font(vrun, "Gotham Bold", size_pt=54, bold=True)
            set_run_scheme_color(vrun, accent)
            lbox = slide.shapes.add_textbox(x, Inches(4.0), col_w, Inches(0.8))
            lrun = lbox.text_frame.paragraphs[0].add_run()
            lrun.text = str(kpi.get("label", ""))
            lbox.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            set_run_font(lrun, "Lato Light", size_pt=18)
            set_run_scheme_color(lrun, "navy")

    elif comp["id"] == "content-cards":
        cards = fill.get("cards", [])[:3]
        n = max(len(cards), 1)
        col_w = Inches(3.6); gap = Inches(0.4)
        total = col_w * n + gap * (n - 1)
        start = Emu(int((SLIDE_W - total) / 2)); y = Inches(2.4)
        for i, card in enumerate(cards):
            x = Emu(int(start + i * (col_w + gap)))
            box = slide.shapes.add_textbox(x, y, col_w, Inches(2.6))
            tf = box.text_frame; tf.word_wrap = True
            hrun = tf.paragraphs[0].add_run(); hrun.text = str(card.get("heading", ""))
            set_run_font(hrun, "Gotham Bold", size_pt=20, bold=True)
            set_run_scheme_color(hrun, accent)
            p = tf.add_paragraph(); brun = p.add_run(); brun.text = str(card.get("body", ""))
            set_run_font(brun, "Lato Light", size_pt=14)
            set_run_scheme_color(brun, "navy")

    elif comp["id"] == "chart-static":
        series = fill.get("series", [])
        max_v = max((s.get("value", 0) for s in series), default=1) or 1
        base_y = Inches(5.6); max_h = Inches(2.8)
        n = max(len(series), 1)
        col_w = Inches(1.4); gap = Inches(0.5)
        total = col_w * n + gap * (n - 1)
        start = Emu(int((SLIDE_W - total) / 2))
        from pptx.enum.shapes import MSO_SHAPE
        from scripts.colors import set_scheme_fill
        for i, s in enumerate(series):
            h = Emu(int(max_h * (s.get("value", 0) / max_v)))
            x = Emu(int(start + i * (col_w + gap)))
            bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Emu(int(base_y - h)), col_w, h)
            bar.line.fill.background()
            set_scheme_fill(bar, accent)
            lbox = slide.shapes.add_textbox(x, base_y, col_w, Inches(0.5))
            lrun = lbox.text_frame.paragraphs[0].add_run(); lrun.text = str(s.get("label", ""))
            lbox.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            set_run_font(lrun, "Lato Light", size_pt=12); set_run_scheme_color(lrun, "navy")
    return slide


def build_deck(spec: dict, out_path) -> Path:
    errors = validate_spec(spec)
    if errors:
        raise SpecError("invalid deck-spec:\n  - " + "\n  - ".join(errors))
    comps = load_components()
    accent = (spec.get("meta") or {}).get("accent", "orange")
    prs = load_template_presentation()
    for slide_spec in spec["slides"]:
        comp = comps[slide_spec["component_id"]]
        if comp["renderer"] == "template":
            _build_template_slide(prs, comp, slide_spec)
        else:
            _build_custom_slide(prs, comp, slide_spec, accent)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return out


if __name__ == "__main__":
    import sys, json
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    dest = sys.argv[2] if len(sys.argv) > 2 else (spec.get("meta", {}).get("output") or "output/deck.pptx")
    print("built", build_deck(spec, dest))
