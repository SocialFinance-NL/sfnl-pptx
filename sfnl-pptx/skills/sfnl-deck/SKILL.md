---
name: sfnl-deck
description: Generate a Social Finance NL branded PowerPoint deck from a brief, outline, or source documents. Use when the user wants a new SFNL/Social Finance NL presentation, slide deck, or pitch deck built from the official sjabloon. Triggers on "SFNL deck", "maak een presentatie", "nieuwe slides in huisstijl", or any request to create, not edit, an SFNL .pptx.
---

# sfnl-deck: generate an SFNL deck

Build consultant-quality, on-brand decks on the bundled sjabloon. Work spec-first: think once
into a compact deck-spec JSON, then build deterministically.

## Pipeline

Idea → research → narrative → storyboard → spec → build → review → proof. Zeven stappen:

1. **Intake.** Accept a one-line brief, an outline, or source docs. Detect language: NL or EN.
2. **Research.** Hand off to the `sfnl-deck-research` skill: turn the idea into a
   **bronnendossier** (feiten, cijfers, bronnen, viz-kandidaten) before any slide is written.
   Skip only when the user supplies complete, already-sourced material — record that as the
   source. Every number that later lands on a slide must trace to a dossier row.
3. **Narrative and titles.** Read `engine/reference/voice.md`. Write the SCQA `narrative`, then
   draft an **action title** for every slide. Run the **ghost-deck test** before building.
4. **Design the layout, slide by slide.** Hand off to the `sfnl-deck-design` skill to decide the
   deck's color model (single- vs multi-accent) and build a per-slide storyboard — component,
   category, icon, variant, rationale — before any JSON is written. The catalogue includes icon
   cards, KPI panels, native editable charts, process arrows/chevrons, schema/organogram,
   image+icon trio, matrix, evidence stack, cycle, scenario cards, assessment table, mechanism
   diagram, full-bleed color dividers, dark stat banners, color-coded swimlane canvases, and an
   abstract geometric closer. Query `engine/scripts/components.py`
   (`find_components(type=..., tags=...)`) while building the storyboard. `content-text` is an
   exception, not the default: use it only when the user explicitly asks for plain text or
   legal/contract wording requires it, and record the reason. When no named component carries
   the slide's message, design a **bespoke exhibit** with `custom-freeform` — a full member of
   the toolkit, not a last resort. Its primitive set (shapes, arrows, chevrons, connectors with
   arrowheads, tables, icons, bullet textboxes, groups) is rich enough to compose consultancy-
   grade one-off diagrams; record in the rationale why a bespoke exhibit beats the nearest
   named component. For data that deserves a real graph, use `chart-native` (editable
   PowerPoint charts: column, stacked, bar, line, area, pie, donut, scatter) fed by the
   dossier's viz-kandidaten.
5. **Emit deck-spec.** Translate the confirmed storyboard into JSON using the schema and
   component catalogue in `engine/reference/deck-spec.md`. Validate it with
   `scripts.spec.validate_spec`; fix every error before building. Put source references
   (dossier row ids) in speaker notes.
6. **Build + review.** Run `python -m scripts.build_from_spec <spec.json> [out.pptx]`. Default
   output is `output/<YYYY-MM-DD>-<slug>.pptx`. Colors are `schemeClr`; never hardcode hex.
   Then hand off to `sfnl-deck-review` for adaptive QA; fix and rebuild until no critical
   findings remain.
7. **Proof.** Before anything goes to a client, hand off to `sfnl-deck-proof`: full render of
   every slide, whole-deck visual review, fact-check against the bronnendossier, language pass,
   and a written proefrapport. Do not declare the deck deliverable until the proof verdict is
   "klaar voor oplevering".

## Rules

- The SFNL template is bundled at `engine/assets/sfnl-template.pptx` and loaded automatically by
  the build. Never ask the user to upload, supply, or point at a `.potx` — the deck is always built
  on the bundled sjabloon.
- Run scripts from `sfnl-pptx/engine`, or set `PYTHONPATH` so `import scripts.*` resolves.
- Deck-spec JSON schema and the full component catalogue live in `engine/reference/deck-spec.md`.
- Brand palette and typography live in `engine/reference/brand.md`.
- Voice and content discipline live in `engine/reference/voice.md`.
- One accent per deck (`meta.accent`) by default; it carries the narrative through-line. Decks
  with 3+ recurring categories across many slides may opt into `meta.accent_map` (multi-accent
  mode, one accent per category) — decided in step 3, documented in `deck-spec.md`.
- Every normal content slide must have a visual exhibit: cards with icon bubbles, KPI/status
  panels, native editable charts, process arrows or chevrons, schema boxes/connectors, image/icon
  columns, 2x2 matrices, layer stacks, cycles, scenario cards, assessment tables, mechanism
  diagrams, full-bleed color dividers, dark stat banners, color-coded swimlane columns, an
  abstract geometric closer, or a bespoke `custom-freeform` composition.
- Tune `visual` per slide when needed. Available controls include `x`, `y`, `card_width`,
  `card_height`, `box_width`, `box_height`, `step_width`, `step_height`, `width`, `height`, `gap`,
  `row_gap`, `columns`, `icon_size`, `progress`, `progress_label`, and `variant`.
- Icons are content, not decoration. For small icon bubbles inside cards/nodes/steps, choose from
  the text-glyph set (`check`, `gear`, `heart`, `people`, `target`, `money`, `chart`, `idea`, or a
  short custom label). For large-scale icons on `divider-block` and `custom-freeform`, use the
  vector icon library in `engine/scripts/icons.py` (`target`, `people`, `growth`, `idea`, `house`,
  `book`, `calendar`, `compass`, `partnership`, `check`, `flag`, `scale`, `money`, `clock`,
  `gear`). Either way, adjust size/location through the slide's `visual` object.
- The standalone HTML template in user references is a pattern source, not an exact template:
  translate useful layouts into these components and update colors, spacing, typography, and
  density so output still follows the bundled SFNL PowerPoint sjabloon.
