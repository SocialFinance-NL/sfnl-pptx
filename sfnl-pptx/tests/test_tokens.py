"""sfnl.css tokens must match palette.json (spec §6 test requirement)."""
import json
import re
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1] / "engine"


def _palette():
    return json.loads((ENGINE / "assets" / "palette.json").read_text(encoding="utf-8"))


def test_css_base_tokens_match_palette():
    css = (ENGINE / "web" / "sfnl.css").read_text(encoding="utf-8")
    pal = _palette()
    for name, slot in pal["by_name"].items():
        var = "--sfnl-" + name.replace(" ", "-")
        hexv = pal["by_slot"][slot]["hex"]
        assert re.search(re.escape(var) + r":\s*#" + hexv, css, re.I), f"{var} missing/mismatched"


def test_tokens_json_covers_palette():
    allowed = set(json.loads((ENGINE / "web" / "tokens.json").read_text(encoding="utf-8"))["allowed_hex"])
    for info in _palette()["by_slot"].values():
        assert info["hex"].upper() in allowed
