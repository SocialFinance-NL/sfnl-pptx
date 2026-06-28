import pytest
from scripts.spec import validate_spec, load_spec, SpecError


def _valid():
    return {
        "schema_version": "1.0",
        "meta": {"title": "T", "lang": "nl", "accent": "emerald", "output": "output/x.pptx"},
        "narrative": "S-C-Q-A spine.",
        "slides": [
            {"id": "s1", "type": "title", "component_id": "title-standard",
             "action_title": "Wij maatschappelijke waarde meetbaar.",
             "content_schema_fill": {"title": "Wij maken impact meetbaar", "subtitle": "SFNL"}}
        ],
    }


def test_valid_spec_has_no_errors():
    assert validate_spec(_valid()) == []


def test_missing_action_title_flagged():
    spec = _valid()
    del spec["slides"][0]["action_title"]
    errs = validate_spec(spec)
    assert any("action_title" in e for e in errs)


def test_unknown_component_flagged():
    spec = _valid()
    spec["slides"][0]["component_id"] = "does-not-exist"
    assert any("component" in e.lower() for e in validate_spec(spec))


def test_unknown_accent_flagged():
    spec = _valid()
    spec["meta"]["accent"] = "chartreuse"
    assert any("accent" in e.lower() for e in validate_spec(spec))


def test_load_spec_raises_on_invalid(tmp_path):
    import json
    bad = _valid()
    del bad["slides"][0]["action_title"]
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(SpecError):
        load_spec(p)
