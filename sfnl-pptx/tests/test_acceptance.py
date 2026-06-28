"""Phase 1 acceptance: a brief -> deck-spec -> .pptx -> QA, end to end."""

from pptx import Presentation

from scripts.build_from_spec import build_deck
from scripts.qa_text import qa_deck
from scripts.spec import validate_spec

DECK_SPEC = {
    "schema_version": "1.0",
    "meta": {
        "title": "Impactmeting voor gemeenten",
        "lang": "nl",
        "accent": "emerald",
        "output": "output/2026-06-28-impactmeting-gemeenten.pptx",
    },
    "narrative": (
        "Gemeenten investeren in preventie maar zien de opbrengst niet; SFNL maakt "
        "de maatschappelijke waarde meetbaar zodat investeren in preventie loont."
    ),
    "slides": [
        {
            "id": "s1",
            "type": "title",
            "component_id": "title-standard",
            "action_title": "SFNL maakt de waarde van preventie zichtbaar",
            "content_schema_fill": {
                "title": "Impactmeting voor gemeenten",
                "subtitle": "Social Finance NL",
            },
        },
        {
            "id": "s2",
            "type": "section",
            "component_id": "section-divider",
            "action_title": "Preventie loont, maar de opbrengst blijft onzichtbaar",
            "content_schema_fill": {"title": "Het probleem", "subtitle": "Waarom meten loont"},
        },
        {
            "id": "s3",
            "type": "kpi",
            "component_id": "kpi-trio",
            "sensitive": True,
            "action_title": "Drie cijfers tonen het rendement van preventie",
            "content_schema_fill": {
                "title": "Wat een MBC oplevert",
                "kpis": [
                    {"value": "3,2x", "label": "SROI"},
                    {"value": "EUR1,4M", "label": "Vermeden kosten"},
                    {"value": "87%", "label": "Doelgroep bereikt"},
                ],
            },
        },
        {
            "id": "s4",
            "type": "closing",
            "component_id": "closing",
            "action_title": "Samen maken we preventie een rendabele investering",
            "content_schema_fill": {
                "title": "Laten we starten",
                "subtitle": "Social Finance NL",
            },
        },
    ],
}


def test_acceptance_end_to_end(tmp_path):
    assert validate_spec(DECK_SPEC) == []
    out = build_deck(DECK_SPEC, tmp_path / "deck.pptx")
    prs = Presentation(str(out))
    assert len(prs.slides) == 4
    report = qa_deck(out)
    assert report["critical"] == 0, report["findings"]
