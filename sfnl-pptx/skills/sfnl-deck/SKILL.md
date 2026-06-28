---
name: sfnl-deck
description: Generate a Social Finance NL branded PowerPoint deck from a brief, outline, or source documents. Use when the user wants a new SFNL/Social Finance NL presentation, slide deck, or pitch deck built from the official sjabloon. Triggers on "SFNL deck", "maak een presentatie", "nieuwe slides in huisstijl", or any request to create, not edit, an SFNL .pptx.
---

# sfnl-deck: generate an SFNL deck

Build consultant-quality, on-brand decks on the bundled sjabloon. Work spec-first: think once
into a compact deck-spec JSON, then build deterministically.

## Pipeline

1. **Intake.** Accept a one-line brief, an outline, or source docs. Detect language: NL or EN.
2. **Narrative and titles.** Read `engine/reference/voice.md`. Write the SCQA `narrative`, then
   draft an **action title** for every slide. Run the **ghost-deck test** before building.
3. **Layout selection.** For each slide pick a component via `engine/scripts/components.py`.
   Use `find_components(type=..., tags=...)`. Use `Leeg`-based custom components only when a
   standard layout cannot carry the message.
4. **Emit deck-spec.** Write the JSON using the schema in the design spec. Validate it with
   `scripts.spec.validate_spec`; fix every error before building.
5. **Build.** Run `python -m scripts.build_from_spec <spec.json> [out.pptx]`. Default output is
   `output/<YYYY-MM-DD>-<slug>.pptx`. Colors are `schemeClr`; never hardcode hex.
6. **QA.** Hand off to the `sfnl-deck-review` skill. Do not declare done until QA passes.

## Rules

- Run scripts from `sfnl-pptx/engine`, or set `PYTHONPATH` so `import scripts.*` resolves.
- Brand palette and typography live in `engine/reference/brand.md`.
- Voice and content discipline live in `engine/reference/voice.md`.
- One accent per deck (`meta.accent`); it carries the narrative through-line.
