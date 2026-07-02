"""Build-layer integration: fixture deck -> valid .pptx via node build_deck.js."""
import shutil
import subprocess
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
BUILD = ENGINE / "web" / "build"
FIXTURES = Path(__file__).parent / "fixtures"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(
    NODE is None or not (BUILD / "node_modules").exists(),
    reason="node or web build deps unavailable",
)


def _workspace(dst_dir, name):
    ws = dst_dir / name
    shutil.copytree(FIXTURES / name, ws)
    shutil.copy(ENGINE / "web" / "sfnl.css", ws / "slides" / "sfnl.css")
    return ws


def _build(ws):
    return subprocess.run([NODE, str(BUILD / "build_deck.js"), str(ws)],
                          capture_output=True, text=True, timeout=300)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    ws = _workspace(tmp_path_factory.mktemp("webdeck"), "webdeck")
    res = _build(ws)
    assert res.returncode == 0, res.stderr + res.stdout
    out = ws / "webdeck.pptx"
    assert out.exists()
    return Presentation(str(out))


def test_all_slides_present(built):
    assert len(list(built.slides)) == 3


def test_title_chrome_lands_on_content_slide(built):
    slide = list(built.slides)[1]
    titles = [s for s in slide.shapes if s.has_text_frame and "DRIE CIJFERS" in s.text_frame.text]
    assert titles, "title text missing"
    assert titles[0].top < Inches(0.9)
    fonts = {r.font.name for p in titles[0].text_frame.paragraphs for r in p.runs}
    assert "Gotham Bold" in fonts


def test_orange_dash_shape_present(built):
    slide = list(built.slides)[1]
    assert "F87F4F" in slide._element.xml


def test_notes_carry_dossier_refs(built):
    slide = list(built.slides)[1]
    assert slide.has_notes_slide
    assert "R1" in slide.notes_slide.notes_text_frame.text


def test_chart_injected_with_brand_colors(built):
    slide = list(built.slides)[2]
    frames = [s for s in slide.shapes if s.has_chart]
    assert frames, "native chart missing"
    assert "F87F4F" in frames[0].chart._chartSpace.xml


def test_page_number_and_logo_chrome(built):
    slides = list(built.slides)
    # cover has chrome none -> no page number '1' textbox bottom-right
    assert not any(s.has_text_frame and s.text_frame.text.strip() == "1" for s in slides[0].shapes)
    two = [s for s in slides[1].shapes if s.has_text_frame and s.text_frame.text.strip() == "2"]
    assert two and two[0].top > Inches(5.0)
    assert any(s.shape_type == 13 for s in slides[1].shapes)  # PICTURE = logo


def test_overflow_deck_fails_loudly(tmp_path):
    ws = _workspace(tmp_path, "webdeck-overflow")
    res = _build(ws)
    assert res.returncode != 0
    assert "overflows body" in (res.stderr + res.stdout)
