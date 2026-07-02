import json
from pathlib import Path
from scripts.extract_palette import extract_palette

ASSETS = Path(__file__).resolve().parents[1] / "engine" / "assets"

def test_extracts_brand_accents():
    pal = extract_palette()
    assert pal["by_slot"]["accent1"]["hex"].upper() == "F87F4F"  # orange
    assert pal["by_slot"]["accent5"]["hex"].upper() == "6AC6BA"  # emerald
    assert pal["by_slot"]["dk2"]["hex"].upper() == "201B5C"      # navy

def test_name_lookup_round_trips():
    pal = extract_palette()
    assert pal["by_name"]["emerald"] == "accent5"

def test_palette_json_is_written_and_matches():
    pal = extract_palette()
    on_disk = json.loads((ASSETS / "palette.json").read_text(encoding="utf-8"))
    assert on_disk["by_slot"]["accent1"]["hex"].upper() == pal["by_slot"]["accent1"]["hex"].upper()
