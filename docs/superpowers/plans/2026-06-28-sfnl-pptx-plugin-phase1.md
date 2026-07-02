# SFNL PowerPoint Plugin — Phase 0 + Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Claude Code plugin (`sfnl-pptx`) that generates and QA-reviews Social Finance NL branded PowerPoint decks from the bundled official sjabloon, end-to-end, with python-pptx.

**Architecture:** A "pipeline plugin": three skills (`sfnl-deck` generate, `sfnl-deck-review` QA; `sfnl-deck-edit` deferred to Phase 2) orchestrate deterministic Python scripts in `engine/`. The model thinks once into a compact **deck-spec JSON**; `build_from_spec.py` deterministically clones sjabloon layouts (filling placeholders by index) or draws custom slides on the blank `Leeg` layout, always coloring via `schemeClr`. QA is adaptive: cheap text/XML checks on template-faithful slides, PowerPoint-COM image render + fresh-eyes inspection on custom/sensitive slides.

**Tech Stack:** Python 3.13, python-pptx 1.0.2, pywin32 (PowerPoint COM render), pytest. Windows-native. No MCP.

## Global Constraints

- **Plugin root:** everything lives under `sfnl-pptx/` in this repo. Manifest at `sfnl-pptx/.claude-plugin/plugin.json`.
- **Bundled template:** `sfnl-pptx/engine/assets/sfnl-template.pptx` — a copy of the repo-root `SFNL Slides.pptx` the user exported (a one-slide-per-layout sampler of the official sjabloon, same theme/masters/layouts). The plugin must never ask the user for the template. The repo-root `01 SFNL_sjabloon.potx` is kept only as the original source reference; the build does not use it.
- **Why the .pptx, not the .potx:** python-pptx cannot open a `.potx` directly (content type `…template.main+xml`). `SFNL Slides.pptx` opens directly and carries the identical theme (accent1 `F87F4F`, accent5 `6AC6BA`, …), 2 masters, and all 30 layouts. Always load it through `load_template_presentation()` (Task 1), which opens it and **strips the sampler slides** so the build starts from a clean 0-slide deck with every layout intact. Never mutate the bundled file (work on the in-memory Presentation).
- **Authoritative palette (verified from theme1.xml — use `schemeClr`, NEVER hardcode hex):** Navy `201B5C` (dk2/accent6/folHlink), Dark slate `233348` (dk1), Orange `F87F4F` (accent1), Grapefruit `F95D63` (accent2), Royal `3B62C1` (accent3/hlink), Sky `45B6E2` (accent4), Emerald `6AC6BA` (accent5), White `FEFFFF`/`FFFFFF` (lt1/lt2).
- **Slide size:** 16:9, 13.33in × 7.5in (12192000 × 6858000 EMU).
- **Placeholder-by-index rule:** title/section layouts (`1_Titelslide`, `*_sectieslide_*`) expose body placeholders at **idx 13 (title text) and idx 14 (subtitle text)**, NOT idx 0/1. `Titel, subtitel` uses idx 0 (title) + idx 1 (subtitle). `Leeg` has zero placeholders. The component index (Task 4) records the exact slot→idx map per component; build code addresses placeholders by idx only.
- **Allowed fonts (installed locally, never embedded):** **only Montserrat Light, Lato Light, Gotham Bold.** These are the only fonts the build may set on a run, and the only ones QA accepts. (Template-faithful slides leave runs empty and inherit fonts from the branded layouts — QA only checks fonts we explicitly set.)
- **Output:** default `./output/` (already git-ignored), dated descriptive filenames, overridable via `meta.output`.
- **Content rules (voice.md):** action titles (full-sentence takeaways), SCQA spine, one exhibit per slide, no trailing periods on short text, conclusion-anchored ending, anti-AI register, NL/EN consultant tone.
- **Commit cadence:** one commit per task minimum. Work on a feature branch off `main` (current branch is `master`; confirm branch before first commit).
- **Test runner:** `python -m pytest sfnl-pptx/tests/ -v` from repo root. All paths below are relative to repo root `C:/Users/XavierFriesen/.projects SFNL/Powerpoints design`.

---

## File Structure

```
sfnl-pptx/
├─ .claude-plugin/plugin.json
├─ skills/
│  ├─ sfnl-deck/SKILL.md                 (Task 11)
│  └─ sfnl-deck-review/SKILL.md          (Task 11)
├─ engine/
│  ├─ assets/
│  │  ├─ sfnl-template.pptx              (Task 0, copied from repo-root SFNL Slides.pptx)
│  │  ├─ palette.json                    (Task 2, generated)
│  │  ├─ layouts.json                    (Task 3, generated)
│  │  └─ components/index.json           (Task 4, authored)
│  ├─ scripts/
│  │  ├─ __init__.py
│  │  ├─ office/template.py              (Task 1)
│  │  ├─ extract_palette.py              (Task 2)
│  │  ├─ extract_layouts.py              (Task 3)
│  │  ├─ spec.py                         (Task 5)
│  │  ├─ colors.py                       (Task 6)
│  │  ├─ build_from_spec.py              (Task 7)
│  │  ├─ render.py                       (Task 8)
│  │  └─ qa_text.py                      (Task 9)
│  └─ reference/
│     ├─ brand.md                        (Task 2, generated header + authored rules)
│     └─ voice.md                        (Task 10)
└─ tests/
   ├─ conftest.py                        (Task 1)
   ├─ fixtures/                          (Task 7)
   └─ test_*.py
```

---

### Task 0: Plugin scaffold + bundled template (Phase 0)

**Files:**
- Create: `sfnl-pptx/.claude-plugin/plugin.json`
- Create: `sfnl-pptx/engine/scripts/__init__.py` (empty package marker)
- Create: `sfnl-pptx/engine/assets/sfnl-template.pptx` (copy of repo-root `SFNL Slides.pptx`)
- Create: `sfnl-pptx/tests/test_scaffold.py`

**Interfaces:**
- Produces: the plugin directory tree; `plugin.json` manifest; bundled template at the canonical asset path used by every later task.

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/test_scaffold.py
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # sfnl-pptx/

def test_manifest_is_valid_json_with_name():
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "sfnl-pptx"

def test_template_is_bundled_and_nonempty():
    tmpl = ROOT / "engine" / "assets" / "sfnl-template.pptx"
    assert tmpl.exists()
    assert tmpl.stat().st_size > 1_000_000  # real branded template
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_scaffold.py" -v`
Expected: FAIL (FileNotFoundError / path missing).

- [ ] **Step 3: Create the directories and manifest**

```bash
mkdir -p "sfnl-pptx/.claude-plugin" "sfnl-pptx/skills" "sfnl-pptx/engine/assets/components" \
         "sfnl-pptx/engine/scripts/office" "sfnl-pptx/engine/reference" "sfnl-pptx/tests/fixtures"
touch "sfnl-pptx/engine/scripts/__init__.py" "sfnl-pptx/engine/scripts/office/__init__.py"
```

`sfnl-pptx/.claude-plugin/plugin.json`:

```json
{
  "name": "sfnl-pptx",
  "version": "0.1.0",
  "description": "Generate and QA Social Finance NL branded PowerPoint decks from the official sjabloon.",
  "author": "Social Finance NL"
}
```

- [ ] **Step 4: Copy the bundled template**

```bash
cp "SFNL Slides.pptx" "sfnl-pptx/engine/assets/sfnl-template.pptx"
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_scaffold.py" -v`
Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add "sfnl-pptx/.claude-plugin/plugin.json" "sfnl-pptx/engine" "sfnl-pptx/tests/test_scaffold.py"
git commit -m "feat(sfnl-pptx): scaffold plugin and bundle sjabloon template"
```

Note: the root-level `01 SFNL_sjabloon.potx` (original sjabloon) and `SFNL Slides.pptx` (the user's
export) are source references; keep them. The bundled `sfnl-template.pptx` is what the plugin uses.
Do **not** add the PowerPoint lock file `~$SFNL Slides.pptx` to git.

---

### Task 1: Template loader (open bundled .pptx + strip sampler slides)

**Files:**
- Create: `sfnl-pptx/engine/scripts/office/template.py`
- Create: `sfnl-pptx/tests/conftest.py`
- Create: `sfnl-pptx/tests/test_template.py`

**Interfaces:**
- Produces:
  - `TEMPLATE_PATH: pathlib.Path` — absolute path to the bundled `sfnl-template.pptx`.
  - `load_template_presentation() -> pptx.presentation.Presentation` — opens the bundled template, removes its sampler slides, and returns a clean 0-slide Presentation (16:9, 2 masters, all 30 layouts intact).

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/conftest.py
import sys
from pathlib import Path
ENGINE = Path(__file__).resolve().parents[1] / "engine"
sys.path.insert(0, str(ENGINE))  # so `import scripts.xxx` works
```

```python
# sfnl-pptx/tests/test_template.py
from pptx.util import Emu
from scripts.office.template import load_template_presentation, TEMPLATE_PATH

def test_template_path_exists():
    assert TEMPLATE_PATH.exists()

def test_loads_as_clean_widescreen_presentation():
    prs = load_template_presentation()
    assert round(Emu(prs.slide_width).inches, 2) == 13.33
    assert round(Emu(prs.slide_height).inches, 2) == 7.5
    assert len(prs.slide_masters) == 2
    assert len(prs.slides) == 0  # sampler slides stripped

def test_all_layouts_intact_after_strip():
    prs = load_template_presentation()
    total_layouts = sum(len(m.slide_layouts) for m in prs.slide_masters)
    assert total_layouts == 30
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_template.py" -v`
Expected: FAIL (ModuleNotFoundError: scripts.office.template).

- [ ] **Step 3: Write the implementation**

```python
# sfnl-pptx/engine/scripts/office/template.py
"""Load the bundled SFNL template as a clean, editable python-pptx Presentation.

The bundled `sfnl-template.pptx` is a one-slide-per-layout sampler exported from
the official sjabloon. It opens directly in python-pptx (unlike a .potx) and
carries the brand theme, both masters, and all 30 layouts. We strip its sampler
slides so the build starts from an empty deck; the masters and layouts remain.
The bundled file on disk is never modified — stripping happens on the in-memory
Presentation copy.
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation

TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "assets" / "sfnl-template.pptx"


def load_template_presentation() -> Presentation:
    """Open the bundled template and remove all sampler slides (layouts kept)."""
    prs = Presentation(str(TEMPLATE_PATH))
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        sldIdLst.remove(sldId)
    return prs
```

Note: `prs.slides._sldIdLst` is python-pptx internal API but stable across 1.x; removing
`<p:sldId>` entries drops the slides while leaving masters/layouts untouched (verified).

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_template.py" -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add "sfnl-pptx/engine/scripts/office/template.py" "sfnl-pptx/tests/conftest.py" "sfnl-pptx/tests/test_template.py"
git commit -m "feat(sfnl-pptx): load bundled template as clean editable presentation"
```

---

### Task 2: Palette extraction → `palette.json` + `brand.md` header

**Files:**
- Create: `sfnl-pptx/engine/scripts/extract_palette.py`
- Create: `sfnl-pptx/engine/assets/palette.json` (generated by running the script)
- Create: `sfnl-pptx/engine/reference/brand.md` (generated header + authored rules)
- Create: `sfnl-pptx/tests/test_palette.py`

**Interfaces:**
- Consumes: `template.TEMPLATE_PATH`.
- Produces:
  - `extract_palette() -> dict` — `{"by_slot": {"accent1": {"hex": "F87F4F", "name": "Orange"}, ...}, "by_name": {"orange": "accent1", ...}}`.
  - `palette.json` on disk with that structure.
  - `SLOT_NAMES: dict[str,str]` — slot→human-name map used to label colors.

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/test_palette.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_palette.py" -v`
Expected: FAIL (ModuleNotFoundError, and palette.json missing).

- [ ] **Step 3: Write the implementation**

```python
# sfnl-pptx/engine/scripts/extract_palette.py
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
```

- [ ] **Step 4: Generate palette.json**

Run: `cd "sfnl-pptx/engine" && python -m scripts.extract_palette`
Expected: prints `wrote .../palette.json`. (Run from `sfnl-pptx/engine` so `scripts` is importable, or set PYTHONPATH.)

- [ ] **Step 5: Author `brand.md`**

`sfnl-pptx/engine/reference/brand.md`:

```markdown
# SFNL Brand Reference (generated palette + design rules)

> Palette is generated from the sjabloon theme1.xml — see `engine/assets/palette.json`.
> Always color via `schemeClr` (the build does this); never hardcode hex.

## Palette (theme slots)

| Name | Hex | schemeClr slot |
|------|-----|----------------|
| Navy | 201B5C | dk2 / accent6 / folHlink |
| Dark slate | 233348 | dk1 |
| Orange | F87F4F | accent1 |
| Grapefruit | F95D63 | accent2 |
| Royal | 3B62C1 | accent3 / hlink |
| Sky | 45B6E2 | accent4 |
| Emerald | 6AC6BA | accent5 |
| White | FEFFFF / FFFFFF | lt1 / lt2 |

**Accent rule:** one accent encodes one meaning per deck (`meta.accent`). Orange is the
default action/highlight color; emerald/sky/royal for categorical series.

## Typography

- **Only three fonts are allowed:** Gotham Bold (display/headings), Lato Light (body/labels),
  Montserrat Light (secondary/quiet). The build sets no other font on a run; QA rejects others.
- Template-faithful slides leave runs empty and inherit fonts from the branded layouts — do not
  override them. Set fonts explicitly only on custom (`Leeg`-based) slides.
- Theme major/minor resolve to Calibri Light / Calibri — never use these for brand text; clone
  branded layouts instead.
- Fonts are installed locally, never embedded.

## Spacing & layout

- 16:9, 13.33in × 7.5in.
- One exhibit per slide. Generous margins; do not crowd the master's safe area.
- Big-number pattern for KPIs: large numeral, small label beneath.
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_palette.py" -v`
Expected: 3 passed.

- [ ] **Step 7: Commit**

```bash
git add "sfnl-pptx/engine/scripts/extract_palette.py" "sfnl-pptx/engine/assets/palette.json" "sfnl-pptx/engine/reference/brand.md" "sfnl-pptx/tests/test_palette.py"
git commit -m "feat(sfnl-pptx): extract theme palette and author brand reference"
```

---

### Task 3: Layout catalog → `layouts.json`

**Files:**
- Create: `sfnl-pptx/engine/scripts/extract_layouts.py`
- Create: `sfnl-pptx/engine/assets/layouts.json` (generated)
- Create: `sfnl-pptx/tests/test_layouts.py`

**Interfaces:**
- Consumes: `load_template_presentation()`.
- Produces:
  - `extract_layouts() -> list[dict]` — one entry per layout: `{"name": str, "master_index": int, "layout_index": int, "placeholders": [{"idx": int, "type": str, "name": str}]}`.
  - `find_layout(prs, name) -> pptx layout object` — locate a layout by name across masters (used by the build).
  - `layouts.json` on disk.

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/test_layouts.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_layouts.py" -v`
Expected: FAIL (ModuleNotFoundError).

- [ ] **Step 3: Write the implementation**

```python
# sfnl-pptx/engine/scripts/extract_layouts.py
"""Catalog every sjabloon slide layout and its placeholder indices, so the build
can address placeholders by idx (title/section layouts use idx 13/14, not 0/1)."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.office.template import load_template_presentation

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def extract_layouts() -> list[dict]:
    prs = load_template_presentation()
    out: list[dict] = []
    for mi, master in enumerate(prs.slide_masters):
        for li, layout in enumerate(master.slide_layouts):
            phs = [
                {
                    "idx": ph.placeholder_format.idx,
                    "type": str(ph.placeholder_format.type),
                    "name": ph.name,
                }
                for ph in layout.placeholders
            ]
            out.append(
                {"name": layout.name, "master_index": mi, "layout_index": li, "placeholders": phs}
            )
    (ASSETS / "layouts.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def find_layout(prs, name: str):
    """Return the first slide layout matching `name` across all masters."""
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            if layout.name == name:
                return layout
    raise KeyError(f"layout not found in sjabloon: {name!r}")


if __name__ == "__main__":
    extract_layouts()
    print("wrote", ASSETS / "layouts.json")
```

- [ ] **Step 4: Generate layouts.json**

Run: `cd "sfnl-pptx/engine" && python -m scripts.extract_layouts`
Expected: prints `wrote .../layouts.json`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_layouts.py" -v`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add "sfnl-pptx/engine/scripts/extract_layouts.py" "sfnl-pptx/engine/assets/layouts.json" "sfnl-pptx/tests/test_layouts.py"
git commit -m "feat(sfnl-pptx): catalog sjabloon layouts and placeholder indices"
```

---

### Task 4: Component library index (core set)

**Files:**
- Create: `sfnl-pptx/engine/assets/components/index.json` (authored)
- Create: `sfnl-pptx/engine/scripts/components.py`
- Create: `sfnl-pptx/tests/test_components.py`

**Interfaces:**
- Consumes: `extract_layouts()` (to validate every `source_layout` exists), `palette.json`.
- Produces:
  - `load_components() -> dict[str, dict]` — component id → entry.
  - Component entry shape: `{"id", "name", "type", "tags": [str], "renderer": "template"|"python-pptx", "source_layout": str, "slots": {slot_name: {"placeholder_idx": int}}, "content_schema": {...}, "density": str}`.
  - `find_components(type=None, tags=None) -> list[dict]` — cheap filter for layout selection.

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/test_components.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_components.py" -v`
Expected: FAIL (ModuleNotFoundError; index.json missing).

- [ ] **Step 3: Author the component index**

`sfnl-pptx/engine/assets/components/index.json` (core set; placeholder indices verified against the sjabloon — title/section use 13/14):

```json
[
  {
    "id": "title-standard",
    "name": "Title slide",
    "type": "title",
    "tags": ["opening", "cover"],
    "renderer": "template",
    "source_layout": "1_Titelslide",
    "slots": {
      "title": {"placeholder_idx": 13},
      "subtitle": {"placeholder_idx": 14}
    },
    "content_schema": {"title": "", "subtitle": ""},
    "density": "low"
  },
  {
    "id": "section-divider",
    "name": "Section divider",
    "type": "section",
    "tags": ["divider", "transition"],
    "renderer": "template",
    "source_layout": "1_sectieslide_stijl1",
    "slots": {
      "title": {"placeholder_idx": 13},
      "subtitle": {"placeholder_idx": 14}
    },
    "content_schema": {"title": "", "subtitle": ""},
    "density": "low"
  },
  {
    "id": "content-text",
    "name": "Title + subtitle + body text",
    "type": "content",
    "tags": ["text", "agenda", "inhoud"],
    "renderer": "template",
    "source_layout": "1_Titel, subtitel, tekst",
    "slots": {
      "title": {"placeholder_idx": 0},
      "subtitle": {"placeholder_idx": 1},
      "body": {"placeholder_idx": 10}
    },
    "content_schema": {"title": "", "subtitle": "", "body": ["bullet"]},
    "density": "medium"
  },
  {
    "id": "comparison-two-col",
    "name": "Two-column comparison",
    "type": "comparison",
    "tags": ["compare", "2-up", "columns"],
    "renderer": "template",
    "source_layout": "Titel, subtitel, twee tekstvakken",
    "slots": {
      "title": {"placeholder_idx": 0},
      "subtitle": {"placeholder_idx": 1},
      "left": {"placeholder_idx": 12},
      "right": {"placeholder_idx": 13}
    },
    "content_schema": {"title": "", "subtitle": "", "left": ["bullet"], "right": ["bullet"]},
    "density": "medium"
  },
  {
    "id": "quote",
    "name": "Quote",
    "type": "quote",
    "tags": ["quote", "testimonial"],
    "renderer": "template",
    "source_layout": "Quote",
    "slots": {
      "title": {"placeholder_idx": 0},
      "attribution": {"placeholder_idx": 1}
    },
    "content_schema": {"title": "", "attribution": ""},
    "density": "low"
  },
  {
    "id": "content-cards",
    "name": "Content with cards",
    "type": "content-cards",
    "tags": ["cards", "3-up", "custom"],
    "renderer": "python-pptx",
    "source_layout": "Leeg",
    "slots": {},
    "content_schema": {"title": "", "cards": [{"heading": "", "body": ""}]},
    "density": "medium"
  },
  {
    "id": "kpi-trio",
    "name": "Three big-number KPIs",
    "type": "kpi",
    "tags": ["data", "metrics", "3-up", "no-chart"],
    "renderer": "python-pptx",
    "source_layout": "Leeg",
    "slots": {},
    "content_schema": {"title": "", "kpis": [{"value": "", "label": ""}]},
    "density": "low"
  },
  {
    "id": "chart-static",
    "name": "Simple static bar chart",
    "type": "chart",
    "tags": ["data", "chart", "bars", "custom"],
    "renderer": "python-pptx",
    "source_layout": "Leeg",
    "slots": {},
    "content_schema": {"title": "", "series": [{"label": "", "value": 0}]},
    "density": "medium"
  },
  {
    "id": "closing",
    "name": "Closing / contact",
    "type": "closing",
    "tags": ["closing", "contact", "thanks"],
    "renderer": "template",
    "source_layout": "1_Titelslide",
    "slots": {
      "title": {"placeholder_idx": 13},
      "subtitle": {"placeholder_idx": 14}
    },
    "content_schema": {"title": "", "subtitle": ""},
    "density": "low"
  }
]
```

- [ ] **Step 4: Write the loader**

```python
# sfnl-pptx/engine/scripts/components.py
"""Load and query the tagged component library."""
from __future__ import annotations

import json
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "assets" / "components" / "index.json"


def load_components() -> dict[str, dict]:
    entries = json.loads(INDEX.read_text(encoding="utf-8"))
    return {c["id"]: c for c in entries}


def find_components(type: str | None = None, tags: list[str] | None = None) -> list[dict]:
    result = []
    for c in load_components().values():
        if type is not None and c["type"] != type:
            continue
        if tags and not set(tags) <= set(c["tags"]):
            continue
        result.append(c)
    return result
```

Note: placeholder indices above are verified against the bundled template. Only `1_Titelslide`
among the title-slide family carries the text body placeholders (idx 13/14) — `5_/6_/7_Titelslide`
expose only date/slide-number placeholders, which is why `closing` reuses `1_Titelslide`. The
Task-4 test `test_every_source_layout_exists_in_sjabloon` checks layouts exist but not idxs, so any
future component must confirm its idxs against generated `layouts.json`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_components.py" -v`
Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add "sfnl-pptx/engine/assets/components/index.json" "sfnl-pptx/engine/scripts/components.py" "sfnl-pptx/tests/test_components.py"
git commit -m "feat(sfnl-pptx): seed core component library with tagged index"
```

---

### Task 5: Deck-spec schema + validator

**Files:**
- Create: `sfnl-pptx/engine/scripts/spec.py`
- Create: `sfnl-pptx/tests/test_spec.py`

**Interfaces:**
- Consumes: `load_components()` (to validate `component_id` and required schema slots).
- Produces:
  - `validate_spec(spec: dict) -> list[str]` — returns a list of human-readable error strings; empty list means valid.
  - `load_spec(path) -> dict` — read + validate, raising `SpecError` on any error.
  - `class SpecError(Exception)`.

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/test_spec.py
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
    bad = _valid(); del bad["slides"][0]["action_title"]
    p = tmp_path / "spec.json"; p.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(SpecError):
        load_spec(p)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_spec.py" -v`
Expected: FAIL (ModuleNotFoundError).

- [ ] **Step 3: Write the implementation**

```python
# sfnl-pptx/engine/scripts/spec.py
"""Deck-spec validation. The deck-spec is the single source of truth for a deck."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.components import load_components

VALID_ACCENTS = {"orange", "grapefruit", "royal", "sky", "emerald", "navy"}
VALID_LANGS = {"nl", "en"}


class SpecError(Exception):
    pass


def validate_spec(spec: dict) -> list[str]:
    errors: list[str] = []
    comps = load_components()

    meta = spec.get("meta") or {}
    if not meta.get("title"):
        errors.append("meta.title is required")
    if meta.get("lang") not in VALID_LANGS:
        errors.append(f"meta.lang must be one of {sorted(VALID_LANGS)}")
    if meta.get("accent") and meta["accent"] not in VALID_ACCENTS:
        errors.append(f"meta.accent {meta.get('accent')!r} is not an allowed accent {sorted(VALID_ACCENTS)}")

    slides = spec.get("slides")
    if not slides:
        errors.append("spec must contain at least one slide")
        return errors

    seen_ids = set()
    for i, slide in enumerate(slides):
        where = f"slide[{i}] (id={slide.get('id')!r})"
        sid = slide.get("id")
        if not sid:
            errors.append(f"{where}: id is required")
        elif sid in seen_ids:
            errors.append(f"{where}: duplicate id")
        else:
            seen_ids.add(sid)
        if not slide.get("action_title"):
            errors.append(f"{where}: action_title is required (consultant rule)")
        cid = slide.get("component_id")
        if cid not in comps:
            errors.append(f"{where}: unknown component_id {cid!r}")
            continue
        # required slots: top-level string keys of content_schema must be present
        fill = slide.get("content_schema_fill") or {}
        for key, shape in comps[cid]["content_schema"].items():
            if isinstance(shape, str) and not fill.get(key):
                errors.append(f"{where}: missing required content slot {key!r} for component {cid!r}")
    return errors


def load_spec(path) -> dict:
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_spec(spec)
    if errors:
        raise SpecError("invalid deck-spec:\n  - " + "\n  - ".join(errors))
    return spec
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_spec.py" -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add "sfnl-pptx/engine/scripts/spec.py" "sfnl-pptx/tests/test_spec.py"
git commit -m "feat(sfnl-pptx): add deck-spec validator"
```

---

### Task 6: schemeClr color + font helpers

**Files:**
- Create: `sfnl-pptx/engine/scripts/colors.py`
- Create: `sfnl-pptx/tests/test_colors.py`

**Interfaces:**
- Produces:
  - `ACCENT_TO_SLOT: dict[str,str]` — accent name → theme slot (`{"orange":"accent1", ..., "navy":"dk2"}`).
  - `set_scheme_fill(shape, accent: str)` — set a shape's solid fill to a theme `schemeClr` (no hardcoded hex), mutating its `spPr`.
  - `set_run_scheme_color(run, accent: str)` — set a text run color to a `schemeClr`.
  - `set_run_font(run, font_name: str, size_pt: float | None = None, bold: bool | None = None)` — apply an allowed brand font.

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/test_colors.py
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from scripts.colors import set_scheme_fill, set_run_scheme_color, set_run_font, ACCENT_TO_SLOT

def _blank_slide():
    prs = Presentation()
    return prs.slides.add_slide(prs.slide_layouts[6])

def test_accent_map_covers_brand_accents():
    assert ACCENT_TO_SLOT["orange"] == "accent1"
    assert ACCENT_TO_SLOT["emerald"] == "accent5"
    assert ACCENT_TO_SLOT["navy"] == "dk2"

def test_scheme_fill_uses_schemeclr_not_hex():
    slide = _blank_slide()
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(1), Inches(2), Inches(1))
    set_scheme_fill(shp, "emerald")
    xml = shp.fill._xPr.xml
    assert "schemeClr" in xml and 'val="accent5"' in xml
    assert "srgbClr" not in xml

def test_run_font_applies_name_and_size():
    slide = _blank_slide()
    tb = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(3), Inches(1))
    run = tb.text_frame.paragraphs[0].add_run()
    run.text = "Hi"
    set_run_font(run, "Gotham Bold", size_pt=28, bold=True)
    assert run.font.name == "Gotham Bold"
    assert run.font.size == Pt(28)
    assert run.font.bold is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_colors.py" -v`
Expected: FAIL (ModuleNotFoundError).

- [ ] **Step 3: Write the implementation**

```python
# sfnl-pptx/engine/scripts/colors.py
"""schemeClr-first color + brand-font helpers. Colors are written as theme
references so slides auto-track the sjabloon palette; we never emit srgbClr."""
from __future__ import annotations

from pptx.oxml.ns import qn
from pptx.util import Pt

ACCENT_TO_SLOT = {
    "orange": "accent1",
    "grapefruit": "accent2",
    "royal": "accent3",
    "sky": "accent4",
    "emerald": "accent5",
    "navy": "dk2",
}

# Only these three may be set on a run by the build; QA accepts only these.
ALLOWED_FONTS = {"Montserrat Light", "Lato Light", "Gotham Bold"}

# Brand roles → font: display/headings = Gotham Bold, body/labels = Lato Light,
# secondary/quiet = Montserrat Light.


def _scheme_slot(accent: str) -> str:
    try:
        return ACCENT_TO_SLOT[accent]
    except KeyError:
        raise KeyError(f"unknown accent {accent!r}; choose from {sorted(ACCENT_TO_SLOT)}")


def set_scheme_fill(shape, accent: str) -> None:
    """Solid-fill a shape with a theme schemeClr (no hardcoded hex)."""
    slot = _scheme_slot(accent)
    spPr = shape.fill._xPr  # the <p:spPr> (or equivalent) element
    # remove any existing fill children
    for tag in ("a:noFill", "a:solidFill", "a:gradFill", "a:blipFill", "a:pattFill", "a:grpFill"):
        for el in spPr.findall(qn(tag)):
            spPr.remove(el)
    solid = spPr.makeelement(qn("a:solidFill"), {})
    scheme = solid.makeelement(qn("a:schemeClr"), {"val": slot})
    solid.append(scheme)
    spPr.append(solid)


def set_run_scheme_color(run, accent: str) -> None:
    """Color a text run with a theme schemeClr."""
    slot = _scheme_slot(accent)
    rPr = run._r.get_or_add_rPr()
    for el in rPr.findall(qn("a:solidFill")):
        rPr.remove(el)
    solid = rPr.makeelement(qn("a:solidFill"), {})
    scheme = solid.makeelement(qn("a:schemeClr"), {"val": slot})
    solid.append(scheme)
    rPr.insert(0, solid)


def set_run_font(run, font_name: str, size_pt: float | None = None, bold: bool | None = None) -> None:
    if font_name not in ALLOWED_FONTS:
        raise ValueError(f"font {font_name!r} not in allowed brand set {sorted(ALLOWED_FONTS)}")
    run.font.name = font_name
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.font.bold = bold
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_colors.py" -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add "sfnl-pptx/engine/scripts/colors.py" "sfnl-pptx/tests/test_colors.py"
git commit -m "feat(sfnl-pptx): schemeClr color and brand-font helpers"
```

---

### Task 7: `build_from_spec.py` — deck builder

**Files:**
- Create: `sfnl-pptx/engine/scripts/build_from_spec.py`
- Create: `sfnl-pptx/tests/fixtures/sample_spec.json`
- Create: `sfnl-pptx/tests/test_build.py`

**Interfaces:**
- Consumes: `load_template_presentation()`, `find_layout()`, `load_components()`, `colors.*`, `validate_spec()`.
- Produces:
  - `build_deck(spec: dict, out_path: str | Path) -> Path` — validates, builds the .pptx, writes it, returns the path.
  - Internal builders: `_build_template_slide(prs, comp, slide_spec)` (clone layout, fill placeholders by idx) and `_build_custom_slide(prs, comp, slide_spec, accent)` (draw on `Leeg`).

**Build approach for template slides:** `prs.slides.add_slide(layout)` from the matched sjabloon layout, then for each `(slot, fill_value)` write text into the placeholder whose `placeholder_format.idx` equals the component's `slots[slot]["placeholder_idx"]`. List fills become one paragraph per item.

**Build approach for custom slides (`Leeg`):** add the blank layout, then draw textboxes/shapes positioned in EMU; color via `set_scheme_fill`/`set_run_scheme_color`; fonts via `set_run_font`. Implement `kpi-trio` (three big numbers across), `content-cards` (three cards), and `chart-static` (bars sized to values) — minimal but real.

- [ ] **Step 1: Write the failing test + fixture**

`sfnl-pptx/tests/fixtures/sample_spec.json`:

```json
{
  "schema_version": "1.0",
  "meta": {"title": "SFNL demo", "lang": "nl", "accent": "emerald", "output": "output/demo.pptx"},
  "narrative": "Situatie-Complicatie-Vraag-Antwoord spine voor de demo.",
  "slides": [
    {"id": "s1", "type": "title", "component_id": "title-standard",
     "action_title": "SFNL maakt maatschappelijke waarde meetbaar",
     "content_schema_fill": {"title": "Maatschappelijke waarde, meetbaar gemaakt", "subtitle": "Social Finance NL"}},
    {"id": "s2", "type": "kpi", "component_id": "kpi-trio", "sensitive": true,
     "action_title": "Drie cijfers vatten de impact samen",
     "content_schema_fill": {"title": "Impact in cijfers",
       "kpis": [{"value": "3,2x", "label": "SROI"}, {"value": "€1,4M", "label": "Vermeden kosten"}, {"value": "87%", "label": "Doelgroep bereikt"}]}},
    {"id": "s3", "type": "closing", "component_id": "closing",
     "action_title": "Samen bouwen we aan duurzame financiering",
     "content_schema_fill": {"title": "Dank", "subtitle": "Social Finance NL"}}
  ]
}
```

```python
# sfnl-pptx/tests/test_build.py
from pathlib import Path
from pptx import Presentation
from scripts.build_from_spec import build_deck
import json

FIX = Path(__file__).resolve().parent / "fixtures" / "sample_spec.json"

def test_build_produces_openable_deck(tmp_path):
    spec = json.loads(FIX.read_text(encoding="utf-8"))
    out = build_deck(spec, tmp_path / "demo.pptx")
    assert out.exists()
    prs = Presentation(str(out))           # re-opens without error => not corrupt
    assert len(prs.slides) == 3

def test_title_text_lands_in_placeholder(tmp_path):
    spec = json.loads(FIX.read_text(encoding="utf-8"))
    out = build_deck(spec, tmp_path / "demo.pptx")
    prs = Presentation(str(out))
    text = "\n".join(sh.text for sh in prs.slides[0].shapes if sh.has_text_frame)
    assert "meetbaar gemaakt" in text

def test_custom_kpi_slide_has_no_hardcoded_hex(tmp_path):
    spec = json.loads(FIX.read_text(encoding="utf-8"))
    out = build_deck(spec, tmp_path / "demo.pptx")
    prs = Presentation(str(out))
    kpi_xml = prs.slides[1]._element.xml
    assert "3,2x" in kpi_xml
    # custom shapes must color via schemeClr, never srgbClr
    assert "srgbClr" not in kpi_xml
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_build.py" -v`
Expected: FAIL (ModuleNotFoundError).

- [ ] **Step 3: Write the implementation**

```python
# sfnl-pptx/engine/scripts/build_from_spec.py
"""Deterministically build a .pptx from a validated deck-spec, on a clone of the
sjabloon. Template slides clone branded layouts and fill placeholders by idx;
custom slides draw on the blank `Leeg` layout with schemeClr colors."""
from __future__ import annotations

from pathlib import Path

from pptx.util import Emu, Inches, Pt
from pptx.enum.text import PP_ALIGN

from scripts.office.template import load_template_presentation
from scripts.extract_layouts import find_layout
from scripts.components import load_components
from scripts.spec import validate_spec, SpecError
from scripts.colors import set_run_scheme_color, set_run_font

SLIDE_W = Emu(12192000)
SLIDE_H = Emu(6858000)


def _placeholder_by_idx(slide, idx: int):
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == idx:
            return ph
    raise KeyError(f"placeholder idx {idx} not found on slide")


def _set_placeholder_text(ph, value) -> None:
    tf = ph.text_frame
    if isinstance(value, list):
        tf.text = str(value[0]) if value else ""
        for item in value[1:]:
            p = tf.add_paragraph()
            p.text = str(item)
    else:
        tf.text = str(value)


def _build_template_slide(prs, comp, slide_spec):
    layout = find_layout(prs, comp["source_layout"])
    slide = prs.slides.add_slide(layout)
    fill = slide_spec.get("content_schema_fill", {})
    for slot_name, slot_def in comp["slots"].items():
        if slot_name in fill:
            ph = _placeholder_by_idx(slide, slot_def["placeholder_idx"])
            _set_placeholder_text(ph, fill[slot_name])
    return slide


def _add_title(slide, text, accent):
    box = slide.shapes.add_textbox(Inches(0.9), Inches(0.6), Inches(11.5), Inches(1.0))
    run = box.text_frame.paragraphs[0].add_run()
    run.text = text
    set_run_font(run, "Gotham Bold", size_pt=28, bold=True)
    set_run_scheme_color(run, "navy")
    return slide


def _build_custom_slide(prs, comp, slide_spec, accent):
    slide = prs.slides.add_slide(find_layout(prs, "Leeg"))
    fill = slide_spec.get("content_schema_fill", {})
    if fill.get("title"):
        _add_title(slide, fill["title"], accent)

    if comp["id"] == "kpi-trio":
        kpis = fill.get("kpis", [])[:3]
        n = max(len(kpis), 1)
        col_w = Inches(3.6)
        gap = Inches(0.4)
        total = col_w * n + gap * (n - 1)
        start = Emu(int((SLIDE_W - total) / 2))
        y = Inches(2.6)
        for i, kpi in enumerate(kpis):
            x = Emu(int(start + i * (col_w + gap)))
            vbox = slide.shapes.add_textbox(x, y, col_w, Inches(1.4))
            vrun = vbox.text_frame.paragraphs[0].add_run()
            vrun.text = str(kpi.get("value", ""))
            vbox.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            set_run_font(vrun, "Gotham Bold", size_pt=54, bold=True)
            set_run_scheme_color(vrun, accent)
            lbox = slide.shapes.add_textbox(x, Inches(4.0), col_w, Inches(0.8))
            lrun = lbox.text_frame.paragraphs[0].add_run()
            lrun.text = str(kpi.get("label", ""))
            lbox.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            set_run_font(lrun, "Lato Light", size_pt=18)
            set_run_scheme_color(lrun, "navy")

    elif comp["id"] == "content-cards":
        cards = fill.get("cards", [])[:3]
        n = max(len(cards), 1)
        col_w = Inches(3.6); gap = Inches(0.4)
        total = col_w * n + gap * (n - 1)
        start = Emu(int((SLIDE_W - total) / 2)); y = Inches(2.4)
        for i, card in enumerate(cards):
            x = Emu(int(start + i * (col_w + gap)))
            box = slide.shapes.add_textbox(x, y, col_w, Inches(2.6))
            tf = box.text_frame; tf.word_wrap = True
            hrun = tf.paragraphs[0].add_run(); hrun.text = str(card.get("heading", ""))
            set_run_font(hrun, "Gotham Bold", size_pt=20, bold=True)
            set_run_scheme_color(hrun, accent)
            p = tf.add_paragraph(); brun = p.add_run(); brun.text = str(card.get("body", ""))
            set_run_font(brun, "Lato Light", size_pt=14)
            set_run_scheme_color(brun, "navy")

    elif comp["id"] == "chart-static":
        series = fill.get("series", [])
        max_v = max((s.get("value", 0) for s in series), default=1) or 1
        base_y = Inches(5.6); max_h = Inches(2.8)
        n = max(len(series), 1)
        col_w = Inches(1.4); gap = Inches(0.5)
        total = col_w * n + gap * (n - 1)
        start = Emu(int((SLIDE_W - total) / 2))
        from pptx.enum.shapes import MSO_SHAPE
        from scripts.colors import set_scheme_fill
        for i, s in enumerate(series):
            h = Emu(int(max_h * (s.get("value", 0) / max_v)))
            x = Emu(int(start + i * (col_w + gap)))
            bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Emu(int(base_y - h)), col_w, h)
            bar.line.fill.background()
            set_scheme_fill(bar, accent)
            lbox = slide.shapes.add_textbox(x, base_y, col_w, Inches(0.5))
            lrun = lbox.text_frame.paragraphs[0].add_run(); lrun.text = str(s.get("label", ""))
            lbox.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            set_run_font(lrun, "Lato Light", size_pt=12); set_run_scheme_color(lrun, "navy")
    return slide


def build_deck(spec: dict, out_path) -> Path:
    errors = validate_spec(spec)
    if errors:
        raise SpecError("invalid deck-spec:\n  - " + "\n  - ".join(errors))
    comps = load_components()
    accent = (spec.get("meta") or {}).get("accent", "orange")
    prs = load_template_presentation()
    for slide_spec in spec["slides"]:
        comp = comps[slide_spec["component_id"]]
        if comp["renderer"] == "template":
            _build_template_slide(prs, comp, slide_spec)
        else:
            _build_custom_slide(prs, comp, slide_spec, accent)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return out


if __name__ == "__main__":
    import sys, json
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    dest = sys.argv[2] if len(sys.argv) > 2 else (spec.get("meta", {}).get("output") or "output/deck.pptx")
    print("built", build_deck(spec, dest))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_build.py" -v`
Expected: 3 passed. If `load_template_presentation()` produces slides that already exist in the template, confirm the template ships with zero slides (it does — it's a sjabloon); `prs.slides` starts empty.

- [ ] **Step 5: Commit**

```bash
git add "sfnl-pptx/engine/scripts/build_from_spec.py" "sfnl-pptx/tests/fixtures/sample_spec.json" "sfnl-pptx/tests/test_build.py"
git commit -m "feat(sfnl-pptx): build decks from spec on the sjabloon clone"
```

---

### Task 8: `render.py` — PowerPoint COM render + preflight

**Files:**
- Create: `sfnl-pptx/engine/scripts/render.py`
- Create: `sfnl-pptx/tests/test_render.py`

**Interfaces:**
- Produces:
  - `com_available() -> bool` — True if PowerPoint COM automation can be started.
  - `render_deck(pptx_path, out_dir, slide_indices=None) -> list[Path]` — export slide(s) to PNG via COM; returns image paths.
  - CLI: `python -m scripts.render --check` (exit 0 if COM works, else non-zero with remediation) and `python -m scripts.render <deck.pptx> <out_dir>`.

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/test_render.py
import pytest
from scripts.render import com_available, render_deck
from scripts.build_from_spec import build_deck
import json
from pathlib import Path

FIX = Path(__file__).resolve().parent / "fixtures" / "sample_spec.json"

def test_com_available_returns_bool():
    assert isinstance(com_available(), bool)

@pytest.mark.skipif(not com_available(), reason="PowerPoint COM not available")
def test_render_produces_images(tmp_path):
    spec = json.loads(FIX.read_text(encoding="utf-8"))
    deck = build_deck(spec, tmp_path / "demo.pptx")
    imgs = render_deck(deck, tmp_path / "imgs", slide_indices=[1])
    assert imgs and all(p.exists() and p.stat().st_size > 0 for p in imgs)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_render.py" -v`
Expected: FAIL (ModuleNotFoundError).

- [ ] **Step 3: Write the implementation**

```python
# sfnl-pptx/engine/scripts/render.py
"""Render slides to PNG via PowerPoint COM (Windows default). LibreOffice is a
documented fallback only and is not implemented here."""
from __future__ import annotations

import sys
from pathlib import Path


def com_available() -> bool:
    try:
        import win32com.client  # noqa: F401
        import pythoncom
    except Exception:
        return False
    try:
        pythoncom.CoInitialize()
        app = win32com.client.Dispatch("PowerPoint.Application")
        app.Quit()
        return True
    except Exception:
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def render_deck(pptx_path, out_dir, slide_indices=None) -> list[Path]:
    """Export slides to PNG. slide_indices are 0-based; None renders all."""
    import win32com.client
    import pythoncom

    pptx_path = Path(pptx_path).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    pythoncom.CoInitialize()
    app = win32com.client.Dispatch("PowerPoint.Application")
    images: list[Path] = []
    try:
        pres = app.Presentations.Open(str(pptx_path), WithWindow=False)
        try:
            total = pres.Slides.Count
            targets = range(total) if slide_indices is None else slide_indices
            for i in targets:
                slide = pres.Slides(i + 1)  # COM is 1-based
                dest = out_dir / f"slide_{i + 1:02d}.png"
                slide.Export(str(dest), "PNG", 1280, 720)
                images.append(dest)
        finally:
            pres.Close()
    finally:
        app.Quit()
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass
    return images


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--check":
        ok = com_available()
        print("PowerPoint COM:", "available" if ok else "NOT available")
        if not ok:
            print("Remediation: ensure Microsoft PowerPoint is installed and pywin32 is present.")
        sys.exit(0 if ok else 1)
    deck, out = sys.argv[1], sys.argv[2]
    for p in render_deck(deck, out):
        print("rendered", p)
```

- [ ] **Step 4: Run preflight + tests**

Run: `cd "sfnl-pptx/engine" && python -m scripts.render --check`
Expected: `PowerPoint COM: available`, exit 0.

Run: `python -m pytest "sfnl-pptx/tests/test_render.py" -v`
Expected: 2 passed (render test actually runs since COM is available).

- [ ] **Step 5: Commit**

```bash
git add "sfnl-pptx/engine/scripts/render.py" "sfnl-pptx/tests/test_render.py"
git commit -m "feat(sfnl-pptx): PowerPoint COM render with preflight check"
```

---

### Task 9: `qa_text.py` — brand/text/XML checks

**Files:**
- Create: `sfnl-pptx/engine/scripts/qa_text.py`
- Create: `sfnl-pptx/tests/test_qa_text.py`

**Interfaces:**
- Consumes: `palette.json` (brand hex set), `colors.ALLOWED_FONTS`, the built `.pptx`.
- Produces:
  - `qa_deck(pptx_path) -> dict` — `{"findings": [{"slide": int, "axis": "Content|Design", "severity": "critical|warn", "message": str}], "critical": int}`.
  - Checks: (a) no leftover placeholder text (`Click to edit`, `Tijdelijke aanduiding`), (b) every slide has non-empty text, (c) run fonts ∈ ALLOWED_FONTS, (d) any `srgbClr` in slide XML that is NOT a brand hex is flagged Design/warn.

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/test_qa_text.py
from pathlib import Path
import json
from scripts.build_from_spec import build_deck
from scripts.qa_text import qa_deck

FIX = Path(__file__).resolve().parent / "fixtures" / "sample_spec.json"

def test_clean_deck_has_no_critical_findings(tmp_path):
    spec = json.loads(FIX.read_text(encoding="utf-8"))
    deck = build_deck(spec, tmp_path / "demo.pptx")
    report = qa_deck(deck)
    assert report["critical"] == 0, report["findings"]

def test_detects_leftover_placeholder(tmp_path):
    from pptx import Presentation
    from scripts.office.template import load_template_presentation
    from scripts.extract_layouts import find_layout
    prs = load_template_presentation()
    slide = prs.slides.add_slide(find_layout(prs, "Titel, subtitel"))
    slide.placeholders[0].text = "Click to edit Master title style"
    out = tmp_path / "bad.pptx"; prs.save(str(out))
    report = qa_deck(out)
    assert any("placeholder" in f["message"].lower() for f in report["findings"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_qa_text.py" -v`
Expected: FAIL (ModuleNotFoundError).

- [ ] **Step 3: Write the implementation**

```python
# sfnl-pptx/engine/scripts/qa_text.py
"""Cheap brand/text/XML QA over a built deck (no rendering)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from pptx import Presentation

from scripts.colors import ALLOWED_FONTS

ASSETS = Path(__file__).resolve().parents[1] / "assets"

LEFTOVER_MARKERS = ("click to edit", "tijdelijke aanduiding", "text placeholder", "lorem ipsum")


def _brand_hexes() -> set[str]:
    pal = json.loads((ASSETS / "palette.json").read_text(encoding="utf-8"))
    return {info["hex"].upper() for info in pal["by_slot"].values()}


def qa_deck(pptx_path) -> dict:
    prs = Presentation(str(pptx_path))
    brand = _brand_hexes()
    findings = []
    for si, slide in enumerate(prs.slides):
        texts = []
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            t = shape.text_frame.text
            texts.append(t)
            low = t.lower()
            for marker in LEFTOVER_MARKERS:
                if marker in low:
                    findings.append({"slide": si, "axis": "Content", "severity": "critical",
                                     "message": f"leftover placeholder text: {t!r}"})
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    fn = run.font.name
                    if fn and fn not in ALLOWED_FONTS:
                        findings.append({"slide": si, "axis": "Design", "severity": "warn",
                                         "message": f"non-brand font {fn!r}"})
        if not any(t.strip() for t in texts):
            findings.append({"slide": si, "axis": "Content", "severity": "warn",
                             "message": "slide has no text"})
        xml = slide._element.xml
        for hexv in set(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', xml)):
            if hexv.upper() not in brand:
                findings.append({"slide": si, "axis": "Design", "severity": "warn",
                                 "message": f"off-brand hardcoded color #{hexv.upper()}"})
    critical = sum(1 for f in findings if f["severity"] == "critical")
    return {"findings": findings, "critical": critical}


if __name__ == "__main__":
    import sys
    print(json.dumps(qa_deck(sys.argv[1]), indent=2, ensure_ascii=False))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_qa_text.py" -v`
Expected: 2 passed. If the clean-deck test reports a non-brand-font critical, note the check only flags fonts as `warn` (not critical), so `critical == 0` holds; leftover-placeholder is the only critical here.

- [ ] **Step 5: Commit**

```bash
git add "sfnl-pptx/engine/scripts/qa_text.py" "sfnl-pptx/tests/test_qa_text.py"
git commit -m "feat(sfnl-pptx): text/brand QA checks over built deck"
```

---

### Task 10: `voice.md` content/voice reference

**Files:**
- Create: `sfnl-pptx/engine/reference/voice.md`
- Create: `sfnl-pptx/tests/test_voice_reference.py`

**Interfaces:**
- Produces: `voice.md` — the consultant + SFNL content rules the `sfnl-deck` skill loads when drafting. No code; the test only asserts the reference exists and names the key rules so the skill can rely on them.

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/test_voice_reference.py
from pathlib import Path

VOICE = Path(__file__).resolve().parents[1] / "engine" / "reference" / "voice.md"

def test_voice_reference_covers_core_rules():
    text = VOICE.read_text(encoding="utf-8").lower()
    for rule in ["action title", "scqa", "ghost-deck", "one exhibit", "conclusion-anchored"]:
        assert rule in text, rule
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_voice_reference.py" -v`
Expected: FAIL (FileNotFoundError).

- [ ] **Step 3: Author `voice.md`**

`sfnl-pptx/engine/reference/voice.md`:

```markdown
# SFNL Deck Voice & Content Rules (NL/EN)

These rules are enforced while drafting the deck-spec — content discipline, not styling.

## Narrative
- **SCQA spine:** the whole deck is one Situation → Complication → Question → Answer arc.
  Write it once in `narrative` before drafting slides.
- **Conclusion-anchored ending:** the closing slide states the answer/ask, not "thank you" alone.

## Titles
- **Action titles:** every slide title is a full-sentence takeaway (the "so what"), not a label.
  "Kosten dalen 18% na interventie" — not "Kosten".
- **Ghost-deck test:** read all action titles in sequence; they must tell the story alone.
  If they don't, fix the narrative before building.

## Slides
- **One exhibit per slide:** one chart, one table, or one idea — never two competing messages.
- **Less text:** short fragments over sentences in body copy; no trailing periods on short text.
- **Big numbers:** lead KPI slides with the numeral; the label is secondary and small.

## Register (anti-AI)
- Concrete, specific, declarative. No "in today's fast-paced world", no "delve", no hedging filler.
- NL and EN are equal first-class; match the brief's language. Consultant tone: confident, plain.
- Color encodes meaning: one accent per deck for the through-line; don't decorate at random.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_voice_reference.py" -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add "sfnl-pptx/engine/reference/voice.md" "sfnl-pptx/tests/test_voice_reference.py"
git commit -m "feat(sfnl-pptx): author consultant/SFNL voice reference"
```

---

### Task 11: Skills — `sfnl-deck` (generate) + `sfnl-deck-review` (QA)

**Files:**
- Create: `sfnl-pptx/skills/sfnl-deck/SKILL.md`
- Create: `sfnl-pptx/skills/sfnl-deck-review/SKILL.md`
- Create: `sfnl-pptx/tests/test_skills.py`

**Interfaces:**
- Produces: two skills with valid YAML frontmatter (`name`, `description`) that orchestrate the engine scripts. These are the user-facing entry points; they reference `engine/` scripts and references by relative path.

- [ ] **Step 1: Write the failing test**

```python
# sfnl-pptx/tests/test_skills.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest "sfnl-pptx/tests/test_skills.py" -v`
Expected: FAIL (FileNotFoundError).

- [ ] **Step 3: Author `sfnl-deck/SKILL.md`**

```markdown
---
name: sfnl-deck
description: Generate a Social Finance NL branded PowerPoint deck from a brief, outline, or source documents. Use when the user wants a new SFNL/Social Finance NL presentation, slide deck, or pitch deck built from the official sjabloon. Triggers on "SFNL deck", "maak een presentatie", "nieuwe slides in huisstijl", or any request to create (not edit) an SFNL .pptx.
---

# sfnl-deck — generate an SFNL deck

Build consultant-quality, on-brand decks on the bundled sjabloon. Spec-first: think once
into a compact deck-spec JSON, then build deterministically.

## Pipeline

1. **Intake.** Accept a one-line brief, an outline, or source docs. Detect language (NL/EN).
2. **Narrative & titles.** Read `engine/reference/voice.md`. Write the SCQA `narrative`, then
   draft an **action title** for every slide. Run the **ghost-deck test** before building.
3. **Layout selection.** For each slide pick a component via `engine/scripts/components.py`
   (`find_components(type=..., tags=...)`). Use `Leeg`-based custom components (kpi-trio,
   content-cards, chart-static) only when a standard layout can't carry the message.
4. **Emit deck-spec.** Write the JSON (schema in the design spec §7). Validate it:
   `python -m scripts.spec` style via `validate_spec` — fix every error before building.
5. **Build.** `python -m scripts.build_from_spec <spec.json> [out.pptx]`. Default output is
   `output/<YYYY-MM-DD>-<slug>.pptx`. Colors are schemeClr; never hardcode hex.
6. **QA.** Hand off to the `sfnl-deck-review` skill. Do not declare done until QA passes.

## Rules
- Run all scripts from `sfnl-pptx/engine` (so `import scripts.*` resolves), or set PYTHONPATH.
- Brand palette and typography: `engine/reference/brand.md`. Voice: `engine/reference/voice.md`.
- One accent per deck (`meta.accent`); it carries the through-line.
```

- [ ] **Step 4: Author `sfnl-deck-review/SKILL.md`**

```markdown
---
name: sfnl-deck-review
description: QA-review an SFNL PowerPoint deck against the Content/Design/Coherence rubric before delivery. Use after generating or editing an SFNL deck, or when the user asks to check, review, or validate an SFNL .pptx. Adaptive: cheap text checks on template-faithful slides, image render on custom/sensitive slides.
---

# sfnl-deck-review — QA an SFNL deck

Score every deck on three axes (PPTEval): **Content**, **Design**, **Coherence**.
Never declare success without one completed QA pass.

## Adaptive procedure

1. **Cheap pass (all slides).** Run `python -m scripts.qa_text <deck.pptx>`. It reports leftover
   placeholders, empty slides, non-brand fonts, and off-brand hardcoded colors. Any `critical`
   finding blocks delivery — fix and rebuild.
2. **Render pass (custom or `sensitive: true` slides only).** Preflight `python -m scripts.render
   --check`. Then `python -m scripts.render <deck.pptx> <out_dir>` for the risky slide indices.
   Inspect the PNGs with fresh eyes for overflow, overlap, misalignment, off-brand visuals.
   On a defect: fix the spec/slide, rebuild, re-render that slide.
3. **Coherence.** Read the action titles in order (ghost-deck test). Confirm the narrative flows
   and one accent carries the through-line.

## Output
Report findings per axis with slide numbers and severity. State clearly whether the deck is
clear-to-deliver or blocked on criticals.
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest "sfnl-pptx/tests/test_skills.py" -v`
Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add "sfnl-pptx/skills" "sfnl-pptx/tests/test_skills.py"
git commit -m "feat(sfnl-pptx): add generate and review skills"
```

---

### Task 12: End-to-end acceptance — generate one real deck

**Files:**
- Create: `sfnl-pptx/tests/test_acceptance.py`

**Interfaces:**
- Consumes: the whole pipeline. This task proves Phase 1 acceptance criteria 1–6.

- [ ] **Step 1: Write the acceptance test**

```python
# sfnl-pptx/tests/test_acceptance.py
"""Phase 1 acceptance: a brief -> deck-spec -> .pptx -> QA, end to end."""
import json
from pathlib import Path
from pptx import Presentation
from scripts.build_from_spec import build_deck
from scripts.spec import validate_spec
from scripts.qa_text import qa_deck

# A hand-authored deck-spec standing in for the model's one thinking pass from a brief:
# "Pitch SFNL's impact measurement approach to a municipality, in Dutch."
DECK_SPEC = {
    "schema_version": "1.0",
    "meta": {"title": "Impactmeting voor gemeenten", "lang": "nl", "accent": "emerald",
             "output": "output/2026-06-28-impactmeting-gemeenten.pptx"},
    "narrative": "Gemeenten investeren in preventie maar zien de opbrengst niet; SFNL maakt "
                 "de maatschappelijke waarde meetbaar zodat investeren in preventie loont.",
    "slides": [
        {"id": "s1", "type": "title", "component_id": "title-standard",
         "action_title": "SFNL maakt de waarde van preventie zichtbaar",
         "content_schema_fill": {"title": "Impactmeting voor gemeenten", "subtitle": "Social Finance NL"}},
        {"id": "s2", "type": "section", "component_id": "section-divider",
         "action_title": "Preventie loont, maar de opbrengst blijft onzichtbaar",
         "content_schema_fill": {"title": "Het probleem", "subtitle": "Waarom meten loont"}},
        {"id": "s3", "type": "kpi", "component_id": "kpi-trio", "sensitive": True,
         "action_title": "Drie cijfers tonen het rendement van preventie",
         "content_schema_fill": {"title": "Wat een MBC oplevert",
            "kpis": [{"value": "3,2x", "label": "SROI"}, {"value": "€1,4M", "label": "Vermeden kosten"},
                     {"value": "87%", "label": "Doelgroep bereikt"}]}},
        {"id": "s4", "type": "closing", "component_id": "closing",
         "action_title": "Samen maken we preventie een rendabele investering",
         "content_schema_fill": {"title": "Laten we starten", "subtitle": "Social Finance NL"}},
    ],
}

def test_acceptance_end_to_end(tmp_path):
    assert validate_spec(DECK_SPEC) == []                       # criterion 1
    out = build_deck(DECK_SPEC, tmp_path / "deck.pptx")
    prs = Presentation(str(out))                                # criterion 2: opens clean
    assert len(prs.slides) == 4
    report = qa_deck(out)                                       # criterion 5
    assert report["critical"] == 0, report["findings"]
```

- [ ] **Step 2: Run the acceptance test**

Run: `python -m pytest "sfnl-pptx/tests/test_acceptance.py" -v`
Expected: 1 passed.

- [ ] **Step 3: Generate the real deck into `./output/` and render its custom slide**

```bash
cd "sfnl-pptx/engine"
python -m scripts.build_from_spec ../tests/fixtures/sample_spec.json ../../output/2026-06-28-sfnl-demo.pptx
python -m scripts.render --check
python -m scripts.render ../../output/2026-06-28-sfnl-demo.pptx ../../output/render-check
```
Expected: a `.pptx` under `output/`, COM check passes, PNGs in `output/render-check/`. Open the
.pptx in PowerPoint once to confirm no repair prompt (criterion 2 & 4).

- [ ] **Step 4: Run the full suite**

Run: `python -m pytest "sfnl-pptx/tests/" -v`
Expected: all tasks' tests pass.

- [ ] **Step 5: Commit**

```bash
git add "sfnl-pptx/tests/test_acceptance.py"
git commit -m "test(sfnl-pptx): end-to-end Phase 1 acceptance"
```

---

## Self-Review

**Spec coverage:**
- §2 decisions: plugin (Task 0), bundled potx (Task 0/1), python-pptx-on-template (Task 7), core component set (Task 4), schemeClr-first (Task 6), NL/EN voice (Task 10), COM render (Task 8), output default (Task 7/12). ✓
- §5 sjabloon facts: palette (Task 2), layouts + placeholder indices (Task 3), fonts allow-list (Task 6/9). ✓
- §6 architecture tree: every Phase-1 file mapped to a task; `sfnl-deck-edit` and `charts/` deliberately deferred (§9, §14 Phase 2/3). ✓
- §7 deck-spec: Task 5 validator + Task 7 builder. ✓
- §8 generate pipeline: Task 11 `sfnl-deck`. ✓
- §10 review rubric + adaptive render: Task 8 + 9 + 11 `sfnl-deck-review`. ✓
- §11 component index: Task 4. ✓
- §12 render toolchain + preflight: Task 8. ✓
- §14 Phase-1 acceptance criteria 1–6: Task 12 (+ Task 8 for criterion 4). ✓
- Out of scope (§15): no MCP, no edit skill, no charts engine, no font embedding — all honored.

**Placeholder scan:** every code step contains complete, runnable code; no TBD/TODO. The one manual-verification note (Task 4, `5_Titelslide` indices) is an explicit check against generated `layouts.json`, not a code gap.

**Type consistency:** `load_template_presentation`, `find_layout`, `load_components`/`find_components`, `validate_spec`/`SpecError`, `set_scheme_fill`/`set_run_scheme_color`/`set_run_font`/`ACCENT_TO_SLOT`/`ALLOWED_FONTS`, `build_deck`, `com_available`/`render_deck`, `qa_deck` — names are used identically across producing and consuming tasks. ✓

## Execution Handoff

See the offer in the chat response.
