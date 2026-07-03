"""Skills/docs must reference the html2pptx pipeline and nothing retired."""
import re
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"

RETIRED = ("build_from_spec", "deck-spec.md", "scripts.spec", "components.py",
           "find_components", "custom-freeform", "chart-native", "scripts/icons.py")


def _all_docs():
    return list(SKILLS.rglob("SKILL.md")) + [PLUGIN / "agents" / "deck-visual-reviewer.md",
                                             PLUGIN / "agents" / "deck-process-reviewer.md",
                                             PLUGIN / "README.md"]


def test_all_skills_exist_with_frontmatter():
    for name in ("sfnl-deck", "sfnl-deck-research", "sfnl-deck-design",
                 "sfnl-deck-review", "sfnl-deck-proof", "sfnl-deck-edit"):
        p = SKILLS / name / "SKILL.md"
        assert p.exists(), name
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        assert m, f"missing frontmatter in {p}"
        assert f"name: {name}" in m.group(1)
        assert "description:" in m.group(1)


def test_deck_process_reviewer_agent_exists_with_frontmatter():
    p = PLUGIN / "agents" / "deck-process-reviewer.md"
    assert p.exists(), p
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    assert m, f"missing frontmatter in {p}"
    assert "name: deck-process-reviewer" in m.group(1)
    assert "tools:" in m.group(1)
    assert "description:" in m.group(1)


def test_no_doc_references_retired_engine():
    for doc in _all_docs():
        text = doc.read_text(encoding="utf-8")
        for marker in RETIRED:
            assert marker not in text, f"{doc} still references {marker}"


def test_deck_skill_mandates_new_pipeline():
    text = (SKILLS / "sfnl-deck" / "SKILL.md").read_text(encoding="utf-8")
    for needle in ("authoring-guide.md", "patterns.md", "build_deck.js", "visuele loop"):
        assert needle in text


def test_review_skill_mandates_full_render_loop():
    text = (SKILLS / "sfnl-deck-review" / "SKILL.md").read_text(encoding="utf-8")
    assert "scripts.render" in text and "alle slides" in text.lower()


def test_deck_retro_skill_exists_with_frontmatter():
    p = SKILLS / "sfnl-deck-retro" / "SKILL.md"
    assert p.exists(), p
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    assert m, f"missing frontmatter in {p}"
    assert "name: sfnl-deck-retro" in m.group(1)
    assert "description:" in m.group(1)


def test_deck_retro_skill_content():
    text = (SKILLS / "sfnl-deck-retro" / "SKILL.md").read_text(encoding="utf-8")
    for needle in ("deck-process-reviewer", "pipeline-retro-log.md",
                   "pipeline-retro-report.md", "zelf goed"):
        assert needle in text, needle
    assert "klant" in text.lower()


def test_reference_docs():
    ref = PLUGIN / "engine" / "reference"
    assert (ref / "authoring-guide.md").exists()
    assert (ref / "editing-guide.md").exists()
    assert not (ref / "deck-spec.md").exists()
    assert "schemeClr" not in (ref / "brand.md").read_text(encoding="utf-8")


def test_edit_skill_mandates_backup_and_qa():
    text = (SKILLS / "sfnl-deck-edit" / "SKILL.md").read_text(encoding="utf-8")
    for needle in ("original.pptx", "scripts.qa_text", "scripts.render"):
        assert needle in text
    assert "zonder HTML-bron" in text or "no HTML source" in text


def test_readme_documents_dev_tooling():
    text = (PLUGIN / "README.md").read_text(encoding="utf-8")
    assert "sfnl-deck-retro" in text
    assert "deck-process-reviewer" in text
    assert "sfnl-deck-edit" in text


def test_design_skill_requires_editorial_kadergrid():
    text = (SKILLS / "sfnl-deck-design" / "SKILL.md").read_text(encoding="utf-8").lower()
    for needle in ("editorial kadergrid", "frame", "16pt", "squint test", "all caps", "gotham bold"):
        assert needle in text


def test_review_and_proof_block_when_render_unavailable():
    review = (SKILLS / "sfnl-deck-review" / "SKILL.md").read_text(encoding="utf-8").lower()
    proof = (SKILLS / "sfnl-deck-proof" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "render unavailable" in review or "render niet beschikbaar" in review
    assert "geblokkeerd" in proof and ("render unavailable" in proof or "render niet beschikbaar" in proof)


def test_deck_design_mentions_archetype_slot_preflight():
    text = (SKILLS / "sfnl-deck-design" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "manifest.json" in text
    assert "slot" in text


def test_research_skill_standardizes_ids_and_viz_enum():
    text = (SKILLS / "sfnl-deck-research" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "t#.#" in text
    for needle in ("funnel", "timeline", "matrix", "scenario", "quote"):
        assert needle in text


def test_outline_skill_has_consistency_rules_section():
    text = (SKILLS / "sfnl-deck-outline" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "cross-slide" in text or "consistentieregels" in text


def test_reference_file_handoff_is_documented():
    deck = (SKILLS / "sfnl-deck" / "SKILL.md").read_text(encoding="utf-8").lower()
    outline = (SKILLS / "sfnl-deck-outline" / "SKILL.md").read_text(encoding="utf-8").lower()
    design = (SKILLS / "sfnl-deck-design" / "SKILL.md").read_text(encoding="utf-8").lower()

    for text in (deck, outline, design):
        assert "reference file" in text or "referentiebestand" in text
    assert "handoff" in outline and ("reference path" in outline or "referentiepad" in outline)
    assert "sfnl brand" in design or "sfnl brandregels" in design or "sfnl-merkregels" in design
