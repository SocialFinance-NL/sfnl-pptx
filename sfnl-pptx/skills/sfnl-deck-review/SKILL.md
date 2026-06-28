---
name: sfnl-deck-review
description: QA-review an SFNL PowerPoint deck against the Content/Design/Coherence rubric before delivery. Use after generating or editing an SFNL deck, or when the user asks to check, review, or validate an SFNL .pptx. Adaptive: cheap text checks on template-faithful slides, image render on custom or sensitive slides.
---

# sfnl-deck-review: QA an SFNL deck

Score every deck on three axes: **Content**, **Design**, and **Coherence**. Never declare success
without one completed QA pass.

## Adaptive Procedure

1. **Cheap pass, all slides.** Run `python -m scripts.qa_text <deck.pptx>`. It reports leftover
   placeholders, empty slides, non-brand fonts, and off-brand hardcoded colors. Any `critical`
   finding blocks delivery; fix and rebuild.
2. **Render pass, custom or sensitive slides only.** Preflight with `python -m scripts.render
   --check`. Then run `python -m scripts.render <deck.pptx> <out_dir>` for risky slide indices.
   Inspect the PNGs for overflow, overlap, misalignment, and off-brand visuals. On a defect, fix
   the spec or slide, rebuild, and re-render that slide.
3. **Coherence.** Read the action titles in order with the ghost-deck test. Confirm the narrative
   flows and one accent carries the through-line.

## Output

Report findings per axis with slide numbers and severity. State clearly whether the deck is
clear to deliver or blocked on critical findings.
