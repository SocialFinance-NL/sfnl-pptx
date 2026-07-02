---
name: sfnl-deck-review
description: "QA-review an SFNL PowerPoint deck against the Content/Design/Coherence rubric before delivery. Use after generating or editing an SFNL deck, or when the user asks to check, review, or validate an SFNL .pptx. Adaptive: cheap text checks on template-faithful slides, image render on custom or sensitive slides."
---

# sfnl-deck-review: QA an SFNL deck

Score every deck on three axes: **Content**, **Design**, and **Coherence**. Never declare success
without one completed QA pass.

## Adaptive Procedure

1. **Cheap pass, all slides.** Run `python -m scripts.qa_text <deck.pptx>`. It reports leftover
   placeholders, empty slides, non-brand fonts, and off-brand hardcoded colors. Any `critical`
   finding blocks delivery; fix and rebuild.
2. **Visual exhibit check.** For the deck-spec, confirm every normal content slide uses a visual
   component (`content-cards`, `kpi-trio`, `chart-static`, `process-timeline`, `schema-grid`,
   `image-icon-trio`, `matrix-2x2`, `layer-stack`, `cycle-diagram`, `scenario-cards`,
   `assessment-table`, `mechanism-diagram`, `divider-block`, `stat-banner`, `swimlane-columns`,
   `closing-geometric`, or `custom-freeform`). A `content-text` slide blocks delivery unless
   `notes` explains why a plain text slide is intentional. Inspect visual slides for actual cards,
   icons, boxes, connectors, chart axes/grid, progress bars, image regions, matrices, stacks,
   cycles, tables, mechanism flows, full-bleed panels, stat bars, or swimlane columns; text-only
   white slides are not acceptable. If the deck-spec used the `sfnl-deck-design` storyboard,
   cross-check the build against it — the JSON should match the reviewed plan.
3. **Render pass, custom or sensitive slides only.** Dispatch the `deck-visual-reviewer` subagent
   with the built `.pptx` path and the sensitive/custom slide indices (or run
   `python -m scripts.render --check` then `python -m scripts.render <deck.pptx> <out_dir>` and
   inspect the PNGs yourself if the subagent is unavailable). It checks overflow, overlap,
   misalignment, off-brand visuals, sparse/plain-looking exhibits, monotonous repetition across
   slides, and multi-accent category consistency, and reports findings by severity. On a defect,
   fix the spec or slide, rebuild, and re-render that slide.
4. **Coherence.** Read the action titles in order with the ghost-deck test. Confirm the narrative
   flows and the deck's color model (single accent, or the `accent_map` categories) stays
   consistent through-line.

## Output

Report findings per axis with slide numbers and severity. State clearly whether the deck is
clear to deliver or blocked on critical findings.
