import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK_SPEC = ROOT / "engine" / "reference" / "deck-spec.md"
INDEX = ROOT / "engine" / "assets" / "components" / "index.json"
DECK_SKILL = ROOT / "skills" / "sfnl-deck" / "SKILL.md"


def test_deck_spec_reference_exists():
    assert DECK_SPEC.is_file()


def test_deck_spec_covers_every_component():
    text = DECK_SPEC.read_text(encoding="utf-8")
    ids = [c["id"] for c in json.loads(INDEX.read_text(encoding="utf-8"))]
    for cid in ids:
        assert cid in text, f"component {cid!r} missing from deck-spec.md"


def test_deck_spec_documents_required_meta_keys():
    text = DECK_SPEC.read_text(encoding="utf-8").lower()
    for key in ["meta.title", "meta.lang", "meta.accent", "action_title", "content_schema_fill"]:
        assert key.lower() in text, key


def test_deck_skill_points_at_deck_spec():
    text = DECK_SKILL.read_text(encoding="utf-8")
    assert "engine/reference/deck-spec.md" in text
