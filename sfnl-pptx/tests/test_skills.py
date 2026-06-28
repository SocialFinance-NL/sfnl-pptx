from pathlib import Path
import re

SKILLS = Path(__file__).resolve().parents[1] / "skills"


def _frontmatter(p):
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    assert m, f"missing frontmatter in {p}"
    return m.group(1)


def test_deck_skill_has_name_and_description():
    fm = _frontmatter(SKILLS / "sfnl-deck" / "SKILL.md")
    assert "name:" in fm and "description:" in fm


def test_review_skill_has_name_and_description():
    fm = _frontmatter(SKILLS / "sfnl-deck-review" / "SKILL.md")
    assert "name:" in fm and "description:" in fm
