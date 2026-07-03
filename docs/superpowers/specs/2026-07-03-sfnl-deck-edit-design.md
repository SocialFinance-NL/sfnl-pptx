# sfnl-deck-edit: editing an existing SFNL .pptx with no HTML source

## Motivation

`sfnl-pptx` builds decks composition-first: HTML per slide + `deck.json` → `build_deck.js` →
`.pptx`, with a mandatory render/inspect/fix loop. For decks built this way, "the review found a
problem" is fixed by editing the HTML and rebuilding — that loop already exists
(`sfnl-deck-review`, `sfnl-deck-proof`).

That loop only works when the HTML source exists. It doesn't for:
- A colleague who built a deck by hand, copying slides from the SFNL sjabloon and typing
  directly in PowerPoint.
- An older SFNL deck that predates `sfnl-deck`.

For those files, the only tool today is opening PowerPoint by hand. `pptx-official`
(`~/.claude/skills/pptx-official`) has scripts for exactly this — `inventory.py`, `replace.py`,
`rearrange.py`, and an OOXML unpack/edit/validate/pack escape hatch — but they were never ported
into `sfnl-pptx`, and they know nothing about SFNL brand rules.

## Scope

**In scope**: editing a `.pptx` that is already in SFNL style (built from the sjabloon by hand,
or an old `sfnl-deck` output edited outside the pipeline) and has no `output/<date>-<slug>/`
HTML/`deck.json` workspace behind it. Operations: text/content edits, slide reorder/duplicate/
delete within the file, inserting an additional official cover/divider/quote slide, and
structural edits (tables, images, charts, shapes) via raw OOXML when the above can't reach them.

**Out of scope** (revisit later if needed): rebranding a foreign/non-SFNL template (swapping an
arbitrary deck's fonts/colors/layout wholesale to SFNL style) and cross-file transplant of literal
slide XML from `sfnl-slides.pptx` (see "Chrome slide insertion" below for why).

**Handoff rule**: if the target file has a matching `output/<date>-<slug>/slides/*.html`
workspace, this skill is the wrong tool — use `sfnl-deck-review`/`sfnl-deck-design` (fix HTML,
rebuild) instead. `sfnl-deck-edit` should check for this and redirect rather than duplicate that
path.

## Architecture

Same posture as the rest of the plugin: Python scripts under `engine/scripts/`, invoked as
`python -m scripts.<name>` from `sfnl-pptx/engine`, documented in a reference guide, driven by a
`SKILL.md`. No Node/HTML/build_deck.js involvement — this path never touches the HTML pipeline.

```
existing .pptx ─▶ inventory.py ─▶ text-inventory.json ─▶ (agent + user agree edit plan)
                                                        ─▶ replace.py         (text edits)
                                                        ─▶ rearrange.py       (reorder/dup/delete)
                                                        ─▶ insert_chrome_slide.py (new cover/divider/quote)
                                                        ─▶ ooxml unpack→edit→validate→pack (everything else)
                 ─▶ qa_text.py + render.py + visual inspection ─▶ edited .pptx
```

## Components

All new/ported scripts live in `sfnl-pptx/engine/scripts/`, alongside the existing
`qa_text.py`/`render.py`/`extract_chrome.py`/`extract_palette.py`.

### `inventory.py` (ported from pptx-official, near-verbatim)
Extracts every text shape's position, size, paragraph formatting, and overflow/overlap status
into JSON, keyed `slide-N`/`shape-N`. No SFNL-specific changes needed — it already reports
`font_name`/`color`/`theme_color` per paragraph, which is enough for the agent to spot off-brand
values by eye against `engine/reference/brand.md` before writing replacements. Porting notes:
drop the `platform`/font-file-lookup code path for Windows-only use (font metrics for overflow
estimation should prefer the three installed SFNL fonts — Gotham Bold, Lato Light, Montserrat
Light — over the macOS/Linux font-dir search pptx-official ships, since this plugin only runs on
Windows with those fonts installed locally per `README.md` prerequisites).

### `replace.py` (ported from pptx-official, near-verbatim)
Applies a replacement JSON (same shape as `inventory.py`'s output, with a `paragraphs` array for
shapes that should get new text) to the deck, clearing any shape not explicitly given new
paragraphs, and failing loudly if text overflow gets worse than the original. **No automatic
brand-correction** — if the replacement JSON doesn't specify `font_name`/`color`, whatever the
shape already had is kept as-is. This matches the plugin's existing philosophy (`qa_text.py`
flags off-brand values, it never silently rewrites them) and avoids the edit skill making
unrequested changes. Off-brand fonts/colors already present, or introduced by a replacement JSON
that the agent wrote carelessly, surface in the mandatory `qa_text.py` pass afterward.

### `rearrange.py` (ported from pptx-official, verbatim)
Duplicate/reorder/delete slides within one file by index sequence
(`python -m scripts.rearrange input.pptx output.pptx 0,3,3,5`). No SFNL-specific changes —
this is pure python-pptx slide-list surgery, format-agnostic.

### `insert_chrome_slide.py` (new — not a port)
Inserts one official cover/divider/quote slide into the target deck at a given position, sourced
from `engine/web/assets/chrome/manifest.json` + its PNGs — **the same source of truth the HTML
archetypes use**, not a copy of raw slide XML from `sfnl-slides.pptx`. Mechanism:
1. Add a blank slide (`prs.slide_layouts[6]` or the target's own blank layout).
2. Add the manifest entry's PNG (`engine/web/assets/chrome/<key>.png`) as a full-bleed picture
   (`add_picture` at `0,0` sized to the target's slide dimensions), sent to the back.
3. For each `slots[]` entry in the manifest, add a text box at its `left_pt`/`top_pt`/`width_pt`/
   `height_pt`, one run styled with the entry's `font`/`size_pt`/`color`/`align`/`bold`, seeded
   with the manifest's `sample` text (or caller-supplied text, see CLI below).

CLI: `python -m scripts.insert_chrome_slide target.pptx output.pptx <manifest-key> <position> [--title "..."] [--subtitle "..."] [--body "..."]`
(text args map to whichever `slots[].role` values the chosen key has; a key with no slots, e.g.
`cover-02`, takes none). `<position>` is the 0-based index the new slide lands at (existing slides
at and after that index shift right); passing the current slide count appends at the end.

**Why not copy real slide XML from `sfnl-slides.pptx`**: that deck's layouts/master/theme are
foreign to the target file. Reconciling `p:sldLayoutId`/`p:sldMasterId` references, merging two
themes, and re-pointing media relationships across files is exactly the kind of fragile OOXML
surgery this design avoids elsewhere. The PNG+slots recipe already produces a pixel-identical
result (it's what `build_deck.js` does for chrome slides today) with none of that risk, and it
means both insertion paths (HTML archetype, direct edit) draw from one manifest — if the sjabloon
changes and `extract_chrome.py` regenerates the manifest/PNGs, both paths pick it up.

### OOXML escape hatch: `unpack.py` / `pack.py` / `validate.py` (ported from pptx-official)
For edits none of the above reach — tables, charts, grouped shapes, image swaps, arbitrary XML.
Ported near-verbatim from `~/.claude/skills/pptx-official/ooxml/` (`scripts/unpack.py`,
`scripts/pack.py`, `scripts/validate.py`, `scripts/validation/{base,pptx}.py`, and the `schemas/`
tree). Only the PPTX validator path is needed — trim `DOCXSchemaValidator`/`RedliningValidator` wiring
out of the ported `validate.py`'s CLI so the ported surface only claims what this plugin actually
uses.
Lives at `engine/ooxml/` (scripts + schemas), mirroring the upstream skill's internal layout,
invoked as `python -m ooxml.scripts.unpack` etc. from `engine/`.

### Reused unchanged: `qa_text.py`, `render.py`
Both already operate on any `.pptx` via python-pptx/COM regardless of how it was built. No
changes needed. These are the mandatory QA/visual-loop tools for this skill, same as they are for
`sfnl-deck-review`.

## Workflow (`skills/sfnl-deck-edit/SKILL.md`)

1. **Confirm applicability.** Check for a matching `output/<date>-<slug>/slides/*.html`
   workspace for the target file; if found, stop and redirect to `sfnl-deck-review`/
   `sfnl-deck-design`. Otherwise proceed.
2. **Snapshot.** Create `output/<date>-<slug>-edit/`, copy the target file in as
   `original.pptx`. All operations below write to a new file in this workspace — never overwrite
   `original.pptx` in place, so the user can diff/revert.
3. **Inventory.** `python -m scripts.inventory original.pptx text-inventory.json`. Read it in
   full (no range limits — matches the existing convention in `pptx-official`'s own workflow
   docs). Note any existing overflow/overlap and any font/color that isn't one of the three brand
   fonts or a `tokens.json` hex, so the user knows what's already off-brand before edits start.
4. **Agree the edit plan with the user**: which slides/shapes get new text, any reorder/
   duplicate/delete, any new chrome slide to insert, anything that needs the OOXML escape hatch.
5. **Apply**, in this order (chrome insertion and rearrange first, since they change slide
   indices; text replacement last against the final slide order):
   - `insert_chrome_slide.py` for new cover/divider/quote slides.
   - `rearrange.py` for reorder/duplicate/delete.
   - `replace.py` for text/content edits, built from a replacement JSON derived from the fresh
     inventory of the post-rearrange file.
   - OOXML unpack → targeted XML edit → `validate.py` → pack for anything else, one change at a
     time, validating after each edit (matches `ooxml.md`'s existing discipline).
6. **QA.** `python -m scripts.qa_text edited.pptx`; resolve all `critical` findings, review
   `warn` findings with the user. Then `python -m scripts.render edited.pptx renders/` and
   inspect every touched slide (dispatch `deck-visual-reviewer` the same way `sfnl-deck-review`
   does) for layout defects the text-level QA can't see — overflow after font substitution,
   picture placement, chrome integrity on inserted slides.
7. **Report.** Summarize what changed, slide by slide, and hand back the path to the edited file.
   Never overwrite the user's original file unless they explicitly ask for that as the final step.

## Error handling

- `replace.py` already fails loudly (raises, non-zero exit) on: shapes referenced that don't
  exist in the inventory, and replacements that make text overflow worse than the original. Both
  ported as-is — these are exactly the failure modes that matter here.
- `insert_chrome_slide.py` fails loudly on: unknown manifest key, position out of range, a
  caller-supplied slot role that doesn't exist on the chosen key (e.g. passing `--body` to
  `cover-02`, which has no slots).
- OOXML `validate.py` fails loudly on schema violations — never pack an unvalidated edit.
- No step silently mutates the user's original file; every operation reads one file and writes
  another inside the dated edit workspace.

## Testing

Follow existing `tests/` conventions (`tests/test_qa_text.py`'s in-memory `Presentation()`
fixture style):
- `tests/test_inventory.py` — build a small in-memory deck, assert extracted positions/overflow/
  paragraph properties match expectations.
- `tests/test_replace.py` — round-trip: inventory → replacement JSON → apply → re-inventory,
  assert text/formatting landed correctly; assert overflow-worsened and unknown-shape cases raise.
- `tests/test_rearrange.py` — assert duplicate/delete/reorder produce the expected final slide
  count and order (port pptx-official's own test intent if it has one, otherwise write fresh).
- `tests/test_insert_chrome_slide.py` — assert the inserted slide has a full-bleed picture and
  text boxes matching the chosen manifest key's slots, for at least one key with slots
  (`divider-01`) and one without (`cover-02`); assert unknown key/position raise.
- `tests/test_ooxml.py` — unpack → pack round-trip on a small fixture produces a byte-identical
  or at least openable `.pptx`; `validate.py` catches a deliberately broken XML fixture.
- Extend `tests/test_skills.py`: add `sfnl-deck-edit` to the `test_all_skills_exist_with_frontmatter`
  tuple; add a `test_edit_skill_mandates_qa_and_backup` asserting the new `SKILL.md` mentions
  `scripts.qa_text`, `scripts.render`, and "original.pptx" (backup-first discipline); add the new
  reference doc to `test_reference_docs`.

## File layout (additions)

```
sfnl-pptx/
├── skills/
│   └── sfnl-deck-edit/          SKILL.md (new)
├── engine/
│   ├── scripts/
│   │   ├── inventory.py         (new, ported)
│   │   ├── replace.py           (new, ported)
│   │   ├── rearrange.py         (new, ported)
│   │   └── insert_chrome_slide.py  (new)
│   ├── ooxml/                   (new, ported)
│   │   ├── scripts/{unpack,pack,validate}.py
│   │   ├── scripts/validation/{base,pptx}.py
│   │   └── schemas/...
│   └── reference/
│       └── editing-guide.md     (new — OOXML editing conventions, ported/trimmed from
│                                  pptx-official's ooxml.md, SFNL-scoped)
└── tests/
    ├── test_inventory.py        (new)
    ├── test_replace.py          (new)
    ├── test_rearrange.py        (new)
    ├── test_insert_chrome_slide.py  (new)
    └── test_ooxml.py            (new)
```

`README.md`'s skill table and layout section get a one-line addition each for `sfnl-deck-edit`.
No `plugin.json` change needed — skills are auto-discovered from `skills/`.

## Open risks / notes for the plan

- `insert_chrome_slide.py`'s picture-as-background approach needs the target deck's slide
  dimensions to match `sfnl-slides.pptx`'s (720×405pt / 16:9) for the PNG to fill edge-to-edge
  without distortion — worth a guard that compares `prs.slide_width`/`slide_height` and fails
  loudly (not silently stretches) on mismatch.
- `inventory.py`'s font-file lookup (used only for overflow-width estimation) should be trimmed
  to Windows font paths, since that's the only supported platform for this plugin per the
  existing prerequisites.
- The `deck-visual-reviewer` agent's description currently says "Decks are built by the sfnl-pptx
  html2pptx engine" — its actual job (render + inspect PNGs for defects) doesn't depend on that,
  but the wording could read as pipeline-specific. Small optional fix in the plan: broaden that
  one line so it's clear the agent also covers hand-edited decks.
