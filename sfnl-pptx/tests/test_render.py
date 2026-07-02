"""render.py stays as the COM renderer; deck-level rendering is covered by test_e2e_render."""
from scripts.render import com_available


def test_com_available_returns_bool():
    assert isinstance(com_available(), bool)
