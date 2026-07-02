from pathlib import Path

VOICE = Path(__file__).resolve().parents[1] / "engine" / "reference" / "voice.md"


def test_voice_reference_covers_core_rules():
    text = VOICE.read_text(encoding="utf-8").lower()
    for rule in ["action title", "scqa", "ghost-deck", "one exhibit", "conclusion-anchored"]:
        assert rule in text, rule
