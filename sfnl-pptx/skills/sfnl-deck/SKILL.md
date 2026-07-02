---
name: sfnl-deck
description: Generate a Social Finance NL branded PowerPoint deck from a brief, outline, or source documents. Use when the user wants a new SFNL/Social Finance NL presentation, slide deck, or pitch deck built from the official sjabloon. Triggers on "SFNL deck", "maak een presentatie", "nieuwe slides in huisstijl", or any request to create, not edit, an SFNL .pptx.
---

# sfnl-deck: generate an SFNL deck

Bouw consultant-kwaliteit decks door **vrije HTML-compositie per slide**, geconverteerd naar
een bewerkbare .pptx via html2pptx + PptxGenJS. Lees vóór het bouwen altijd
`engine/reference/authoring-guide.md` en `engine/web/patterns.md`.

## Pipeline

Idee → research → narrative → storyboard → HTML+deck.json → build → visuele loop → review → proof:

1. **Intake.** Brief, outline of brondocumenten. Detecteer taal (NL/EN).
2. **Research.** Hand off naar `sfnl-deck-research`: bronnendossier (feiten, cijfers, bronnen,
   viz-kandidaten) vóór er een slide bestaat. Skip alleen wanneer de gebruiker compleet,
   gebronmerkt materiaal aanlevert — noteer dat als bron. Elk cijfer op een slide traceert naar
   een dossierregel.
3. **Narrative en titels.** Lees `engine/reference/voice.md`. SCQA-narrative, action title per
   slide, ghost-deck-test vóór het bouwen.
4. **Storyboard.** Hand off naar `sfnl-deck-design`: per slide de layoutcompositie (regio's,
   hiërarchie, patroon uit `patterns.md` of archetype, accentgebruik, chart-kandidaten) als
   tekst-storyboard, goedgekeurd vóór er HTML wordt geschreven.
5. **Auteur HTML + deck.json.** Maak de workspace `output/<YYYY-MM-DD>-<slug>/` (kopieer
   `engine/web/sfnl.css` naar `slides/`). Eén HTML-bestand per slide vanaf `engine/web/scaffold.html`
   of een archetype (`engine/web/archetypes/`); charts als `class="placeholder"` + chartspec in
   `deck.json`; speaker notes met dossier-verwijzingen in `deck.json`. Volg de harde HTML-regels
   uit de authoring guide (alle tekst in tekst-tags, geen gradients, ALL CAPS-titels getypt,
   geen logo/paginanummer in HTML).
6. **Build + visuele loop (verplicht, elke build).** `node engine/web/build/build_deck.js
   output/<datum>-<slug>`. Faalt de validatie: alle fouten in één keer fixen. Daarna renderen
   (`python -m scripts.render … renders/` vanuit `engine/`), elke PNG inspecteren of de
   `deck-visual-reviewer` dispatchen, HTML fixen, rebuilden — tot schoon. Draai ook
   `python -m scripts.qa_text` en los criticals op.
7. **Review + proof.** Hand off naar `sfnl-deck-review` (adaptieve QA) en vóór klantoplevering
   naar `sfnl-deck-proof` (volledige eindproef). Pas opleveren bij "klaar voor oplevering".

## Regels

- Chrome is heilig: titelblok + oranje dash in de HTML (scaffold), logo + paginanummer komen
  native uit de build. Full-bleed archetypes regelen hun eigen chrome (`chrome: "dark"|"none"`).
- Eén accent per deck (`deck.json.accent`); kleur codeert betekenis (`engine/reference/brand.md`).
- **Volledige hoogte**: elke contentslide vult het canvas met een echte exhibit; half-leeg of
  tekst-zonder-exhibit is een defect. Gebruik `patterns.md` als kookboek, niet als keurslijf —
  pas patronen vrij aan op de boodschap en componeer gerust bespoke exhibits.
- Data die een grafiek verdient wordt een **native chart** (chartspec in deck.json), gevoed
  door de viz-kandidaten uit het dossier.
- Iconen zijn inhoud: rasterize react-icons in merkkleur naar `assets/`
  (`node engine/web/build/raster.js icon …`).
- Node-dependencies staan in `engine/web/build/` (`npm install` + `npx playwright install
  chromium` eenmalig). Python-scripts draaien vanuit `sfnl-pptx/engine`.
