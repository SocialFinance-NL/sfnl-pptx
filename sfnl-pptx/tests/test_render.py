import pytest
from scripts.render import com_available, render_deck
from scripts.build_from_spec import build_deck
import json
from pathlib import Path

FIX = Path(__file__).resolve().parent / "fixtures" / "sample_spec.json"


def test_com_available_returns_bool():
    assert isinstance(com_available(), bool)


@pytest.mark.skipif(not com_available(), reason="PowerPoint COM not available")
def test_render_produces_images(tmp_path):
    spec = json.loads(FIX.read_text(encoding="utf-8"))
    deck = build_deck(spec, tmp_path / "demo.pptx")
    imgs = render_deck(deck, tmp_path / "imgs", slide_indices=[1])
    assert imgs and all(p.exists() and p.stat().st_size > 0 for p in imgs)
