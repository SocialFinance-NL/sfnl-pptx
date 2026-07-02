import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # sfnl-pptx/

def _read_manifest(directory):
    return json.loads((ROOT / directory / "plugin.json").read_text(encoding="utf-8"))


def test_claude_manifest_is_valid_json_with_name():
    manifest = _read_manifest(".claude-plugin")
    assert manifest["name"] == "sfnl-pptx"


def test_codex_manifest_is_ready_for_plugin_ingestion():
    manifest = _read_manifest(".codex-plugin")
    claude_manifest = _read_ma