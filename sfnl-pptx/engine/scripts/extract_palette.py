"""Generate palette.json from the sjabloon theme1.xml. schemeClr-first: the build
never hardcodes hex; this file exists for QA (detecting off-brand hex) and for
human-readable names mapping to theme slots."""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

from scripts.office.template import TEMPLATE_PATH

ASSETS = Path(__file__).resolve().parents[1] / "assets"

# Human names for theme slots, per the verified SFNL palette.
SLOT_NAMES = {
    "dk1": "Dark slate", "lt1": "White", "dk2": "Navy", "lt2": "White",
    "accent1": "Orange", "accent2": "Grapefruit", "accent3": "Royal",
    "accent4": "Sky", "accent5": "Emerald", "accent6": "Navy",
    "hlink": "Royal", "folHlink": "Navy",
}


def extract_palette() -> dict:
    data = zipfile.ZipFile(TEMPLATE_PATH).read("ppt/theme/theme1.xml").decode("utf-8")
    scheme = re.search(r"<a:clrScheme\b.*?</a:clrScheme>", data, re.S).group(0)
    by_slot: dict[str, dict] = {}
    for m in re.finditer(
        r'<a:(\w+)>\s*<a:(?:srgbClr|sysClr)\s+val="([0-9A-Fa-f]+)"(?:\s+lastClr="([0-9A-Fa-f]+)")?',
        scheme,
    ):
        slot, val, last = m.groups()
        hex_val = (last or val).upper()
        by_slot[slot] = {"hex": hex_val, "name": SLOT_NAMES.get(slot, slot)}
    by_name: dict[str, str] = {}
    for slot, info in by_slot.items():
        by_name.setdefault(info["name"].lower(), slot)
    result = {"by_slot": by_slot, "by_name": by_name}
    (ASSETS / "palette.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    extract_palette()
    print("wrote", ASSETS / "palette.json")
