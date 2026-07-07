---
name: sfnl-deck
description: Generate a Social Finance NL branded PowerPoint deck from a brief, outline, or source documents. Use when the user wants a new SFNL/Social Finance NL presentation, slide deck, or pitch deck built from the official sjabloon. Triggers on "SFNL deck", "maak een presentatie", "nieuwe slides in huisstijl", or any request to create, not edit, an SFNL .pptx.
---

# sfnl-deck: generate an SFNL deck

Bouw consultant-kwaliteit decks door **vrije HTML-compositie per slide**, geconverteerd naar
een bewerkbare .pptx via html2pptx + PptxGenJS. Lees vóór het bouwen altijd
`engine/reference/authoring-guide.md` en `engine/web/patterns.md`.

## Pipeline

Idee → research → outline → storyboard → HTML+deck.json → build → visuele loop → review → proof:

1. **Intake.** Brief, outline of brondocumenten. Detecteer taal (NL/EN). Vraag/capture ook
   of er een optioneel **reference file / referentiebestand** is dat laat zien hoe de deck qua
   look of structuur ongeveer moet aanvoelen. Noteer pad, korte samenvatting en welke elementen
   richtinggevend zijn; dit is input voor outline/design, geen vervanging van SFNL brandregels.
2. **Research.** Hand off naar `sfnl-deck-research`: bronnendossier (feiten, cijfers, bronnen,
   viz-kandidaten) vóór er een slide bestaat. Skip alleen wanneer de gebruiker compleet,
   gebronmerkt materiaal aanlevert — noteer dat als bron. Elk cijfer op een slide traceert naar
   een dossierregel.
3. **Outline.** Hand off naar `sfnl-deck-outline`: een geschaalde vraagronde over inhoud en
   structuur (0-20 vragen, met skip-optie), gevolgd door een per-slide content-outline
   (`output/<YYYY-MM-DD>-<slug>/outline.md`) die de gebruiker becommentarieert en goedkeurt
   vóór er storyboard- of HTML-werk begint. Geef een eventueel reference file / referentiebestand
   mee als handoff-veld met pad en samenvatting. Lees `engine/reference/voice.md` voor de
   SCQA-narrative- en action-title-regels die de outline moet volgen.
4. **Storyboard.** Hand off naar `sfnl-deck-design`: leest de goedgekeurde outline en werkt 'm
   uit tot per-slide layoutcompositie (regio's, hiërarchie, patroon uit `patterns.md` of
   archetype, accentgebruik, chart-kandidaten) als tekst-storyboard, goedgekeurd vóór er HTML
   wordt geschreven. Content- of structuurwijzigingen op dit moment gaan terug naar de outline,
   niet naar het storyboard. Als de outline een reference file / referentiebestand noemt, neemt
   design de herbruikbare structuur-/stijlcue's mee en verwerpt conflicterende cue's expliciet
   wanneer SFNL brandregels of officiële archetypes voorgaan. Voor een klein aantal sleutelslides (bespoke composities of
   narratief cruciale slides) volgt daarna een visuele review met snelle HTML-mockups in één
   Artifact (stap 2.5 van `sfnl-deck-design`), tenzij de deck triviaal klein is of de gebruiker
   dat overslaat.
5. **Auteur HTML + deck.json.** Maak de workspace `output/<YYYY-MM-DD>-<slug>/` (kopieer
   `engine/web/sfnl.css` naar `slides/`). Eén HTML-bestand per slide vanaf `engine/web/scaffold.html`
   of een archetype (`engine/web/archetypes/`); charts als `class="placeholder"` + chartspec in
   `deck.json`; speaker notes met dossier-verwijzingen in `deck.json`. Volg de harde HTML-regels
   uit de authoring guide (alle tekst in tekst-tags, geen gradients, ALL CAPS-titels getypt,
   geen logo/paginanummer in HTML).
6. **Build + visuele loop (verplicht, elke build).** `node engine/web/build/build_deck.js
   output/<datum>-<slug>`. De build embedt automatisch de officiële SFNL-layoutgalerij uit
   `engine/assets/sfnl-sjabloon.potx` en faalt hard als die merge niet lukt. Faalt de validatie:
   alle fouten in één keer fixen. Daarna renderen (`python -m scripts.render … renders/` vanuit
   `engine/`), elke PNG inspecteren of de `deck-visual-reviewer` dispatchen, HTML fixen,
   rebuilden — tot schoon. Als PowerPoint COM niet beschikbaar is, gebruik de Codex
   presentations artifact-tool renderer voor diagnostische PPTX-screenshots/contact sheets, maar
   markeer delivery nog steeds als `GEBLOKKEERD OP RENDER`. Draai ook `python -m scripts.qa_text`,
   en wanneer PowerPoint COM beschikbaar is `python -m scripts.render --assert-layouts <deck.pptx> 31`;
   los criticals op.
7. **Review + proof.** Hand off naar `sfnl-deck-review` (adaptieve QA) en vóór klantoplevering
   naar `sfnl-deck-proof` (volledige eindproef). Pas opleveren bij "klaar voor oplevering".

## Regels

- Chrome is heilig: titelblok + oranje dash in de HTML (scaffold), logo + paginanummer komen
  native uit de build.
- **Titelslides, sectiedividers en quote-slides komen altijd uit de officiële archetypes**
  (`engine/web/archetypes/cover-*.html`, `divider-*.html`, `quote-*.html`, gegenereerd uit het
  sjabloon `engine/assets/sfnl-slides.pptx`). Nooit zelf een cover of divider ontwerpen — kies
  een variant uit `engine/web/assets/chrome/manifest.json`, kopieer de chrome-assets mee naar
  `slides/chrome/`, en vervang alleen de teksten in de slots. Gebruik het `chrome`-advies uit
  het manifest (`none`/`dark`/`number`) in deck.json.
- Eén accent per deck (`deck.json.accent`); kleur codeert betekenis (`engine/reference/brand.md`).
- **Volledige hoogte**: elke contentslide vult het canvas met een echte exhibit; half-leeg of
  tekst-zonder-exhibit is een defect. Gebruik `patterns.md` als kookboek, niet als keurslijf —
  pas patronen vrij aan op de boodschap en componeer gerust bespoke exhibits.
- Data die een grafiek verdient wordt een **native chart** (chartspec in deck.json), gevoed
  door de viz-kandidaten uit het dossier.
- Iconen zijn inhoud: rasterize react-icons in merkkleur naar `assets/`
  (`node engine/web/build/raster.js icon …`).
- Complexe visuals gaan native: `<table class="sfnl-table {orange|royal|teal|navy}">` →
  bewerkbare pptx-tabel, `<div data-shape="chevron|pill|circle|arrow-*">` → autoshape,
  `data-connectors` op `<body>` → pijlen tussen node-id's. Kies het patroon uit `patterns.md`
  (`sfnl-table`, `flow-tree`, `veranderttheorie-map`, `effectenkaart`, `chevron-process`,
  `stat-cards`, `stakeholder-ladder`, `icon-tiles`, `chips`, `definition-box`) en bekijk (Read)
  eerst het bijpassende exhibit in `engine/reference/exhibits/` (`manifest.md`).
- Node-dependencies staan in `engine/web/build/` (`npm install` + `npx playwright install
  chromium` eenmalig). Python-scripts draaien vanuit `sfnl-pptx/engine`.
