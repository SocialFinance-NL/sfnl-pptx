"""E2E smoke: fixture deck -> build_deck.js -> PowerPoint COM render (spec §6)."""
import pytest

from scripts.render import com_available, render_deck
from tests.test_web_build import BUILD, NODE, _build, _workspace

pytestmark = pytest.mark.skipif(
    NODE is None or not (BUILD / "node_modules").exists() or not com_available(),
    reason="node deps or PowerPoint COM unavailable",
)


def test_build_and_render_full_fixture_deck(tmp_path):
    ws = _workspace(tmp_path, "webdeck")
    res = _build(ws)
    assert res.returncode == 0, res.stderr + res.stdout
    images = render_deck(ws / "webdeck.pptx", ws / "renders")
    assert len(images) == 3
    # flat full-bleed slides (e.g. the navy cover) compress to just a few KB
    assert all(p.exists() and p.stat().st_size > 1_000 for p in images)
