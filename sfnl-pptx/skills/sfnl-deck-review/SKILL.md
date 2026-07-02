---
name: sfnl-deck-review
description: "QA-review an SFNL PowerPoint deck against the Content/Design/Coherence rubric before delivery. Use after generating or editing an SFNL deck, or when the user asks to check, review, or validate an SFNL .pptx. Core: the mandatory render-inspect-fix loop over every slide, plus cheap text QA."
---

# sfnl-deck-review: QA an SFNL deck

Score op drie assen: **Content**, **Design**, **Coherence**. Nooit succes rapporteren zonder
één afgeronde QA-pass. De kern is de **visuele loop — verplicht voor elke build en over álle
slides**, niet alleen "sensitive" slides.

## Procedure

1. **Tekst-QA, alle slides.** `python -m scripts.qa_text <deck.pptx>` (vanuit `engine/`):
   leftover scaffold-tekst, niet-ALL-CAPS-titels, off-brand fonts/kleuren (buiten
   `engine/web/tokens.json`), lege slides. Elke `critical` blokkeert: HTML fixen, rebuilden.
2. **Visuele loop, alle slides.** Render alles:
   `python -m scripts.render <deck.pptx> <workspace>/renders`. Dispatch de
   `deck-visual-reviewer` (hele-deck-pass) of inspecteer elke PNG zelf op: tekst-cutoff,
   overlap, onbalans, dode witruimte, contrast, **chrome-integriteit** (titel + dash, logo,
   paginanummer aanwezig en op hun plek), half-lege slides, monotonie. Elke bevinding: fix de
   HTML (of deck.json/chartspec) → `node engine/web/build/build_deck.js <workspace>` →
   re-render → opnieuw beoordelen. **Herhaal tot schoon.**
3. **Exhibit-check.** Elke contentslide draagt een echte exhibit die het canvas vult (kaarten,
   big numbers, chart, swimlanes, matrix, diagram). Tekst-zonder-exhibit blokkeert tenzij de
   notes uitleggen waarom dat bewust is. Check de build tegen het storyboard van
   `sfnl-deck-design`.
4. **Coherence.** Action titles in volgorde (ghost-deck-test); accentgebruik consistent met het
   gekozen kleurmodel.

## Output

Bevindingen per as met slide-nummers en severity, plus het aantal loop-rondes. Eindig met:
clear to deliver / geblokkeerd op N criticals.

## Handoff naar de eindproef

Deze review is de adaptieve QA tijdens het bouwen. Vóór klantoplevering volgt altijd
`sfnl-deck-proof`. "Review passed" betekent "klaar voor de eindproef", niet "klaar voor de klant".
