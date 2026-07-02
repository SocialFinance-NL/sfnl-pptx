from scripts.components import load_components, find_components
from scripts.extract_layouts import extract_layouts

def test_core_components_present():
    comps = load_components()
    assert {"title-standard", "section-divider", "content-cards", "kpi-trio",
            "quote", "closing"} <= set(comps)

def test_every_source_layout_exists_in_sjabloon():
    layout_names = {l["name"] for l in extract_layouts()}
    for c in load_components().values():
        assert c["source_layout"] in layout_names, c["id"]

def test_template_components_declare_placeholder_idx():
    for c in load_components().values():
        if c["renderer"] == "template":
            for slot in c["slots"].values():
                assert isinstance(slot["placeholder_idx"], int)

def test_find_by_type():
    ids = {c["id"] for c in find_components(type="kpi")}
    assert "kpi-trio" in ids
