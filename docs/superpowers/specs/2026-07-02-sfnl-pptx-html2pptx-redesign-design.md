# sfnl-pptx v2 — html2pptx-based generation core

**Date:** 2026-07-02
**Status:** Approved by Xavier (design sections 1–6 approved in session)

## Problem

The current plugin builds decks spec-first: a deck-spec JSON is rendered by a python-pptx
engine (`build_from_spec.py`) using a fixed component catalogue on the bundled sjabloon.
Output is functional but ugly: slides sit half-empty at the top, spacing is uneven,
typography hierarchy is weak, and the rigid component catalogue cannot express what a
slide actually needs. It has a "components stamped on a canvas" look instead of composed,
designed slides.

The `pptx-official` skill (`~/.claude/skills/pptx-official/`) achieves much better results
through two mechanisms the plugin lacks:

1. **Free-form HTML/CSS layout per slide**, converted to PowerPoint with exact positioning
   via `html2pptx.js` + PptxGenJS (editable text boxes, real shapes, native charts).
2. **A mandatory visual validation loop**: render slides to images, inspect for cutoff /
   overlap / imbalance, fix, re-render until clean.

## Decision

Rebuild the sfnl-pptx generation core on the html2pptx workflow, adjusted to the SFNL
template and style.

Constraints confirmed by Xavier:

- **Pain points:** layout & composition, visual richness, typography, rigid components —
  all four must be addressed.
- **Template nativeness may be dropped.** The sjabloon reduces to fixed chrome that must
  always be present: the title treatment (Gotham Bold, ALL CAPS, navy, orange dash),
  the SFNL logo bottom-left, and the orange page number bottom-right. Below the title the
  white canvas is free for creative composition. schemeClr / master-placeholder
  nativeness is no longer required; text and shapes must remain editable in PowerPoint.
- **Scope: rebuild the generation core.** Research / design / review / proof skills stay,
  adapted. The deck-spec → python-pptx engine is retired.

## 1. Architecture & pipeline

Seven pipeline steps survive; the middle changes from *spec → python-pptx* to
*HTML → PptxGenJS*:

```
idee → research (bronnendossier) → narrative + action titles → storyboard
     → slides/*.html + deck.json → build_deck.js (html2pptx + PptxGenJS) → deck.pptx
     → visual loop (render.py → inspect PNGs → fix HTML → rebuild)
     → review → proof
```

- Claude authors **one HTML file per slide** (720pt × 405pt, 16:9) on a shared SFNL
  scaffold, plus a **`deck.json` manifest**: slide order, per-slide speaker notes (with
  bronnendossier row ids), chart definitions keyed to placeholder ids, and deck metadata
  (title, language, author, accent choice).
- A generic Node build script (`build_deck.js`) converts the HTML slides into one `.pptx`
  with editable text boxes, real shapes, and native editable PptxGenJS charts.
- Each deck gets a **workspace folder** `output/<YYYY-MM-DD>-<slug>/` containing
  `slides/*.html`, `assets/` (rasterized icons, images), `deck.json`, render PNGs, and the
  final `.pptx` — so the HTML source stays next to the deliverable for later edits.

## 2. SFNL design system (`engine/web/`)

Replaces the rigid component catalogue.

- **`sfnl.css`** — single stylesheet with:
  - Brand tokens **generated from `engine/assets/palette.json`** (single source of truth):
    navy `#201B5C`, dark slate `#233348`, orange `#F87F4F`, grapefruit `#F95D63`,
    royal `#3B62C1`, sky `#45B6E2`, emerald `#6AC6BA`, white — plus derived pastel tints
    and dark shades as **precomputed hex values** matching the old lumMod/lumOff tints
    (no runtime `color-mix`, so converted colors are deterministic).
  - Typography hierarchy: **Gotham Bold** (display/headings), **Lato Light** (body/labels),
    **Montserrat Light** (secondary/quiet). Titles and subtitles ALL CAPS. Font stacks
    include web-safe fallbacks.
  - **Fixed chrome classes**: title block top-left with orange dash beneath, SFNL logo
    bottom-left, orange page number bottom-right. Chrome is present on every content
    slide; full-bleed archetypes (cover, divider, closing) have their own chrome rules
    mirroring the sjabloon.
- **`scaffold.html`** — canonical slide skeleton: chrome + free content region. Below the
  title, layout is free flexbox/grid CSS.
- **Slide archetypes** as HTML examples faithful to the sjabloon look: cover, section
  divider (navy full-bleed), quote, closing (geometric), dark stat banner.
- **`patterns.md`** — a *cookbook, not a catalogue*: proven layout patterns (KPI row with
  big numbers, two-column exhibit, swimlane columns, process chevrons, 2×2 matrix,
  scenario cards, evidence stack, cycle, mechanism diagram, assessment table) as
  copy-paste HTML fragments that Claude adapts freely. Brand rules travel with the
  cookbook: one accent per deck by default, color encodes meaning, big-numbers pattern,
  **full-height composition** (content fills the canvas; no half-empty slides), generous
  but even margins.
- **Icons**: react-icons rasterized to brand-colored PNGs via Sharp (per pptx-official
  guidance), cached in the deck workspace `assets/`. Replaces the autoshape icon library
  (`icons.py`). No CSS gradients ever — gradients are pre-rendered PNGs via Sharp.

## 3. Build layer (`engine/web/build/`)

- **`html2pptx.js` vendored** from pptx-official into the plugin (self-contained), adapted
  for Windows: `tmpDir` defaults that work without `/tmp`, path handling.
- **`build_deck.js`** — generic runner:
  1. Reads `deck.json`.
  2. Converts each HTML slide via `html2pptx()` (pptx layout `LAYOUT_16x9`).
  3. Fills `class="placeholder"` regions with **native PptxGenJS charts** from JSON chart
     specs (column, stacked, bar, line, area, pie, donut, scatter), applying SFNL
     `chartColors` (hex **without** `#`), axis titles, and single-accent discipline.
  4. Adds speaker notes (with dossier row references) per slide.
  5. Writes `output/<date>-<slug>/<slug>.pptx`.
  - **Escape hatch**: `deck.json` may reference an optional per-deck JS hook module for
    exotic slides needing direct PptxGenJS calls.
- html2pptx's built-in validation (overflow, CSS gradients, text-outside-text-tags,
  dimension mismatch) is the first QA gate at build time; build fails loudly with all
  collected errors.

## 4. Visual validation loop & QA

- After every build: **render every slide to PNG** with the existing PowerPoint COM
  renderer (`engine/scripts/render.py`). No LibreOffice/poppler dependency.
- Claude inspects every render (the `deck-visual-reviewer` agent does whole-deck passes)
  for: text cutoff, overlap, imbalance, dead whitespace, contrast failures, chrome
  integrity (title/logo/page number present and positioned).
- Fix HTML → rebuild → re-render **until clean**. The loop is mandatory for every build,
  not just "sensitive slides".
- **`qa_text.py` adapted**: keeps three-fonts rule, ALL-CAPS titles rule, language checks
  on the final `.pptx`; drops schemeClr enforcement (brand hex is now by design).

## 5. Skills & docs restructure

| Skill / doc | Fate |
|---|---|
| `sfnl-deck` | Rewritten around the new pipeline; mandates reading the authoring guide + `patterns.md`, and the visual loop. |
| `sfnl-deck-research` | Unchanged. |
| `sfnl-deck-design` | Storyboard now thinks in layout composition (regions, hierarchy, accent use per slide) instead of catalogue components. |
| `sfnl-deck-review` | Kept; absorbs the render-inspect loop as its core. |
| `sfnl-deck-proof` | Kept, unchanged in spirit (full render, feitenproef, proefrapport). |
| `agents/deck-visual-reviewer` | Kept, updated to new pipeline paths. |
| `engine/reference/deck-spec.md` | Replaced by an **HTML authoring guide** (scaffold usage, deck.json schema, chart spec schema, html2pptx rules digest). |
| `engine/reference/brand.md` | Updated: hex tokens instead of schemeClr, same brand rules. |
| `engine/reference/voice.md` | Unchanged. |

## 6. Retired code, tests, dependencies

**Retired:** `build_from_spec.py`, `spec.py`, `components.py`, `icons.py`,
`extract_layouts.py`, `layouts.json`, `assets/components/index.json`, deck-spec tests and
fixtures. `extract_palette.py` + `palette.json` stay (token source). `render.py`,
`qa_text.py` stay. The bundled `sfnl-template.pptx` stays only as visual reference for
chrome fidelity (no longer the build substrate).

**Tests (pytest + Node):**
- Token generation: `sfnl.css` tokens match `palette.json`.
- Build: fixture deck (HTML slides + deck.json) → valid `.pptx`; text, shapes, notes
  present; chart injected into placeholder with SFNL colors.
- Validation gate: overflowing fixture slide fails the build with a clear error.
- `qa_text` rules on the fixture output (fonts, ALL CAPS).
- End-to-end smoke: build + COM render of the fixture deck (skipped when PowerPoint
  unavailable).

**New dependencies:** Node.js with `pptxgenjs`, `playwright` (Chromium), `sharp`,
`react-icons`, `react`, `react-dom`. Python side unchanged (python-pptx for qa_text,
pywin32 for render). Brand fonts (Gotham Bold, Lato Light, Montserrat Light) must remain
installed locally — unchanged from v1; fonts are never embedded.

## Risk

html2pptx officially recommends web-safe fonts. We use locally installed
Gotham/Montserrat/Lato in both Playwright rendering (text measurement) and the final
`.pptx` text runs. If conversion glitches appear (metrics/wrapping), fallback: render HTML
with a metric-compatible web-safe stack while writing the brand font names into the pptx
text runs. This risk is checked early in implementation with a spike slide.
