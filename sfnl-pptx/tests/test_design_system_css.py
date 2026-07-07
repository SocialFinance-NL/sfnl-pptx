import re
from pathlib import Path

CSS = Path(__file__).resolve().parents[1] / "engine" / "web" / "sfnl.css"
PATTERNS = Path(__file__).resolve().parents[1] / "engine" / "web" / "patterns.md"


def _declaration_block(css, selector):
    match = re.search(rf"(?ms)^\s*{re.escape(selector)}\s*\{{(?P<body>.*?)\}}", css)
    assert match, f"{selector} declaration block missing"
    return match.group("body")


def test_body_copy_defaults_to_readable_lato_scale():
    css = CSS.read_text(encoding="utf-8")
    body = _declaration_block(css, "body")
    assert 'font-family: "Lato Light"' in body
    assert "font-size: 16pt" in body
    dense = _declaration_block(css, ".body-dense")
    assert "font-size: 14pt" in dense


def test_editorial_frame_utilities_exist():
    css = CSS.read_text(encoding="utf-8")
    for selector in (".frame-panel", ".frame-band", ".frame-sidebar", ".evidence-box", ".verdict-box"):
        _declaration_block(css, selector)


def test_evidence_and_verdict_boxes_are_not_grey_boxes():
    css = CSS.read_text(encoding="utf-8")
    evidence = _declaration_block(css, ".evidence-box")
    verdict = _declaration_block(css, ".verdict-box")
    assert "background: var(--sfnl-white)" in evidence
    assert "--sfnl-grey" not in evidence
    assert "background: var(--sfnl-orange)" in verdict
    assert "--sfnl-grey" not in verdict


def test_dash_is_not_the_only_brand_marker():
    css = CSS.read_text(encoding="utf-8")
    _declaration_block(css, ".dash")
    _declaration_block(css, ".frame-accent")
    _declaration_block(css, ".slide-title")


def test_patterns_document_exhibit_grammar():
    text = PATTERNS.read_text(encoding="utf-8").lower()
    # New contract: patterns.md leads with the exhibit-derived grammar.
    assert "referentiegrammatica" in text
    assert "exhibit" in text
    assert "--sfnl-" in text          # colors via tokens, never hardcoded hex
    assert "pasteltint" in text
    # Process rules that must survive the rewrite.
    assert "squint test" in text
    assert "all caps" in text
    assert "archetype" in text        # covers/dividers/quotes always from official archetypes
    # New component/pattern vocabulary is documented.
    for needle in ("sfnl-table", "data-shape", "stat-card", "ladder-row", ".chip"):
        assert needle in text, needle
    # Retired rules are gone.
    assert "editorial kadergrid" not in text
    assert "geen html `<table>`" not in text
