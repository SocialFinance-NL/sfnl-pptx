from pptx.util import Emu
import pytest

from scripts.merge_template import TEMPLATE as SJABLOON_PATH, TemplateMergeError, merge
from scripts.office.template import load_template_presentation, TEMPLATE_PATH


def test_template_path_exists():
    assert TEMPLATE_PATH.exists()


def test_sjabloon_source_is_bundled():
    assert SJABLOON_PATH.exists()


def test_merge_fails_loudly_when_sjabloon_is_missing(tmp_path):
    missing_template = tmp_path / "missing-sjabloon.potx"
    with pytest.raises(TemplateMergeError, match="SFNL sjabloon not bundled"):
        merge(tmp_path / "deck.pptx", template_path=missing_template)


def test_loads_as_clean_widescreen_presentation():
    prs = load_template_presentation()
    assert round(Emu(prs.slide_width).inches, 2) == 13.33
    assert round(Emu(prs.slide_height).inches, 2) == 7.5
    assert len(prs.slide_masters) == 2
    assert len(prs.slides) == 0  # sampler slides stripped

def test_all_layouts_intact_after_strip():
    prs = load_template_presentation()
    total_layouts = sum(len(m.slide_layouts) for m in prs.slide_masters)
    assert total_layouts == 30
