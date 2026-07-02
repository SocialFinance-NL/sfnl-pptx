from pathlib import Path
import re
import yaml

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


def test_design_skill_has_name_and_description():
    fm = _frontmatter(SKILLS / "sfnl-deck-design" / "SKILL.md")
    assert "name:" in fm and "description:" in fm


def test_all_skill_frontmatter_is_valid_yaml():
    for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
        frontmatter = yaml.safe_load(_frontmatter(skill_md))
        assert isinstance(frontmatter, dict), skill_md
        assert frontmatter["name"]
        assert frontmatter["description"]
