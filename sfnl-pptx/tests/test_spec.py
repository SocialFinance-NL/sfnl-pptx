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


def test_valid_accent_map_has_no_errors():
    spec = _valid()
    spec["meta"]["accent_map"] = {"vraagstuk": "grapefruit", "impact": "orange"}
    spec["slides"][0]["category"] = "vraagstuk"
    assert validate_spec(spec) == []


def test_accent_map_with_unknown_accent_flagged():
    spec = _valid()
    spec["meta"]["accent_map"] = {"vraagstuk": "chartreuse"}
    errs = validate_spec(spec)
    assert any("accent_map" in e for e in errs)


def test_empty_accent_map_flagged():
    spec = _valid()
    spec["meta"]["accent_map"] = {}
    errs = validate_spec(spec)
    assert any("accent_map" in e for e in errs)


def test_non_string_category_flagged():
    spec = _valid()
    spec["slides"][0]["category"] = 42
    errs = validate_spec(spec)
    assert any("category" in e for e in errs)


def _freeform_slide(primitives):
    return {
        "id": "ff1", "component_id": "custom-freeform",
        "action_title": "Een vrije compositie voor een uitzonderlijke slide",
        "content_schema_fill": {"title": "Freeform", "primitives": primitives},
    }


def test_valid_freeform_primitives_have_no_errors():
    spec = _valid()
    spec["slides"].append(_freeform_slide([
        {"type": "rect", "x": 1.0, "y": 1.0, "w": 2.0, "h": 1.0, "fill": "sky"},
        {"type": "textbox", "x": 1.0, "y": 2.0, "w": 2.0, "h": 1.0, "text": "Hi", "font": "Lato Light"},
    ]))
    assert validate_spec(spec) == []


def test_freeform_requires_nonempty_primitives():
    spec = _valid()
    spec["slides"].append(_freeform_slide([]))
    errs = validate_spec(spec)
    assert any("primitives" in e for e in errs)


def test_freeform_rejects_unknown_primitive_type():
    spec = _valid()
    spec["slides"].append(_freeform_slide([{"type": "blob", "x": 0, "y": 0, "w": 1, "h": 1}]))
    errs = validate_spec(spec)
    assert any("type" in e for e in errs)


def test_freeform_rejects_off_brand_color():
    spec = _valid()
    spec["slides"].append(_freeform_slide([{"type": "rect", "x": 0, "y": 0, "w": 1, "h": 1, "fill": "chartreuse"}]))
    errs = validate_spec(spec)
    assert any("color" in e.lower() for e in errs)


def test_freeform_rejects_off_brand_font():
    spec = _valid()
    spec["slides"].append(_freeform_slide([
        {"type": "textbox", "x": 0, "y": 0, "w": 1, "h": 1, "text": "Hi", "font": "Comic Sans MS"}
    ]))
    errs = validate_spec(spec)
    assert any("font" in e.lower() for e in errs)


def test_freeform_rejects_unknown_icon():
    spec = _valid()
    spec["slides"].append(_freeform_slide([
        {"type": "icon", "x": 0, "y": 0, "w": 1, "h": 1, "icon": "not-a-real-icon"}
    ]))
    errs = validate_spec(spec)
    assert any("icon" in e.lower() for e in errs)
