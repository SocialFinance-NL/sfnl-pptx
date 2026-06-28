from scripts.extract_layouts import extract_layouts, find_layout
from scripts.office.template import load_template_presentation


def test_known_layouts_present():
    names = {l["name"] for l in extract_layouts()}
    assert {"Titel, subtitel", "Leeg", "1_Titelslide", "1_sectieslide_stijl1"} <= names


def test_titel_subtitel_placeholder_indices():
    cat = {l["name"]: l for l in extract_layouts()}
    idxs = {p["idx"] for p in cat["Titel, subtitel"]["placeholders"]}
    assert idxs == {0, 1}


def test_title_slide_uses_idx_13_14():
    cat = {l["name"]: l for l in extract_layouts()}
    idxs = {p["idx"] for p in cat["1_Titelslide"]["placeholders"]}
    assert idxs == {13, 14}


def test_leeg_has_no_placeholders():
    cat = {l["name"]: l for l in extract_layouts()}
    assert cat["Leeg"]["placeholders"] == []


def test_find_layout_returns_object():
    prs = load_template_presentation()
    layout = find_layout(prs, "Titel, subtitel")
    assert layout.name == "Titel, subtitel"
