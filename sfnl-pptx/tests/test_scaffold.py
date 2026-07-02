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
    claude_manifest = _read_manifest(".claude-plugin")

    assert manifest["name"] == "sfnl-pptx"
    assert manifest["version"] == claude_manifest["version"]
    assert manifest["description"] == claude_manifest["description"]
    assert manifest["author"] == claude_manifest["author"]
    assert manifest["license"] == claude_manifest["license"]
    assert manifest["skills"] == "./skills/"

    interface = manifest["interface"]
    assert interface["displayName"] == "SFNL PPTX"
    assert interface["developerName"] == "Social Finance NL"
    assert interface["category"] == "Productivity"
    assert interface["capabilities"] == ["Generate", "Review", "Write"]
    assert 1 <= len(interface["defaultPrompt"]) <= 3
    assert all(len(prompt) <= 128 for prompt in interface["defaultPrompt"])

def test_template_is_bundled_and_nonempty():
    tmpl = ROOT / "engine" / "assets" / "sfnl-template.pptx"
    assert tmpl.exists()
    assert tmpl.stat().st_size > 1_000_000  # real branded template
