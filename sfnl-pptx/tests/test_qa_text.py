from pathlib import Path
import json
from scripts.build_from_spec import build_deck
from scripts.qa_text import qa_deck

FIX = Path(__file__).resolve().parent / "fixtures" / "sample_spec.json"

def test_clean_deck_has_no_critical_findings(tmp_path):
    spec = json.loads(FIX.read_text(encoding="utf-8"))
    deck = build_deck(spec, tmp_path / "demo.pptx")
    report = qa_deck(deck)
    assert report["critical"] == 0, report["findings"]

def test_detects_leftover_placeholder(tmp_path):
    from pptx import Presentation
    from scripts.office.template import load_template_presentation
    from scripts.extract_layouts import find_layout
    prs = load_template_presentation()
    slide = prs.slides.add_slide(find_layout(prs, "Titel, subtitel"))
    slide.placeholders[0].text = "Click to edit Master title style"
    out = tmp_path / "bad.pptx"; prs.save(str(out))
    report = qa_deck(out)
    assert any("placeholder" in f["message"].lower() for f in report["findings"])
