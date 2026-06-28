import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # sfnl-pptx/

def test_manifest_is_valid_json_with_name():
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "sfnl-pptx"

def test_template_is_bundled_and_nonempty():
    tmpl = ROOT / "engine" / "assets" / "sfnl-template.pptx"
    assert tmpl.exists()
    assert tmpl.stat().st_size > 1_000_000  # real branded template
