# SFNL layout patterns — referentiegrammatica

De maatstaf is de exhibit-galerij: `engine/reference/exhibits/` (zie `manifest.md`).
Bekijk (Read) het bijpassende exhibit vóór je een tabel, diagram of statcompositie bouwt.
Herbouw de grammatica op de nieuwe inhoud; kopieer nooit tekst of cijfers uit een exhibit.

Fragmenten hieronder horen binnen het scaffold-`<main class="content">` van een contentslide.
Covers, sectiedividers en quotes zijn geen patroon maar een gegeven: gebruik altijd de
officiële archetypes (`archetypes/cover-*`, `divider-*`, `quote-*`; catalogus in
`assets/chrome/manifest.json`) en vervang alleen de slotteksten. Ontwerp ze nooit zelf.

## Stijlconstanten (door alle exhibits heen)

- Afgeronde hoeken (~9pt) op kaarten, tiles en chips; tabellen strak rechthoekig.
- Pasteltinten (`--sfnl-*-tint80`) als vlakvulling; volle merkkleur voor headers, chips en
  accenten. Nooit hex hardcoden — altijd de tokens uit `sfnl.css`.
- Semantische kleurrollen: grapefruit/rood = kosten/risico, emerald/teal = baten/positief,
  navy = totaal/gewicht, oranje = resultaat/accent, royal/sky = proces/structuur.
- Witte tekst en witte lijniconen op volle merkkleur; navy/dark-slate tekst op wit of pastel.
- Titels en subtitels **getypt** in ALL CAPS (`text-transform` telt niet mee in de conversie).
  Houd ze kort en ruim, zodat de caps als merkstem lezen.
- De oranje dash is een merkmarker, geen compositie: de slide moet ook zonder dash werken.
- Alle tekst in `<p>`/`<h1>`-`<h6>`/`<ul>`/`<ol>`; achtergrond/rand alleen op `<div>`; geen
  CSS-gradiënten. Tekst >12pt eindigt ≥0.5in boven de onderrand.
- Iconen dragen betekenis (bronsoort, doelgroep, beslisstatus), geen decoratie. Rasterize
  betekenisvolle react-icons naar merkkleur-PNG's met `node engine/web/build/raster.js icon …`
  en plaats ze met `<img>`. Charts als `<div class="placeholder">` + registratie in
  `deck.json` → `slides[].charts[]`.

## Proceschecks (elke slide)

- **Squint test:** klein of onscherp bekeken is de belangrijkste boodschap het sterkste
  element, daarna de ondersteuning, dan de metadata.
- **Rol per frame:** elk vlak heeft een rol — bewijs, mechanisme, risico, besluit, resultaat of
  vraag. Decoratieve vlakken zonder rol vallen door de review.
- **Kies de juiste grammatica:** match de inhoud aan het patroon hieronder en het bijbehorende
  exhibit; verzin geen nieuwe vormentaal.

## Tabellen (`sfnl-table`) — exhibits: outcome-ledger-table, financial-table-sections, overview-table-orange, sensitivity-table-navy

Grootboek-/overzichts-/inputtabel: caps-headerregel in merkkleur, getinte sectieregels,
€-kolom rechts uitgelijnd met rood=kost / teal=baat, navy totaalband onderaan, kleine bronkolom.
Bekijk (Read) `engine/reference/exhibits/outcome-ledger-table.png`. Kies de preset-klasse
(`orange|royal|teal|navy`) op de kleurrol van de tabel. `<table>` wordt native en bewerkbaar.

```html
<div class="col">
  <table class="sfnl-table orange">
    <tr><th>Effect</th><th>Stakeholder</th><th class="col-num">Waarde</th><th class="col-source">Bron</th></tr>
    <tr class="section-row"><td colspan="4">Kosten</td></tr>
    <tr><td>Zorgkosten diagnostiek</td><td>Zorgverzekeraar</td><td class="col-num val-cost">€ 679.745</td><td class="col-source">NZa 2025</td></tr>
    <tr class="section-row"><td colspan="4">Baten</td></tr>
    <tr><td>Vermeden zorgkosten</td><td>Zorgverzekeraar</td><td class="col-num val-benefit">€ 260.590</td><td class="col-source">NZa 2025</td></tr>
    <tr class="total-row"><td>Netto maatschappelijk resultaat</td><td></td><td class="col-num">€ 4,0 mln</td><td></td></tr>
  </table>
</div>
```

## Flow-tree / beslisboom — exhibit: scenario-decision-tree

Beslisboom: gekleurde nodes (`border-radius`), pijlen met percentagelabels op de takken,
gestippelde takken, chevron-fasekop. Bekijk (Read)
`engine/reference/exhibits/scenario-decision-tree.png`. De pijlen komen uit `data-connectors`
op `<body>` (from/to + `route:"straight"|"elbow"`, `dashed`, `label`); elke node krijgt een `id`.

```html
<!-- Zet de connectors op de <body>-tag van deze slide: -->
<!-- <body data-connectors='[{"from":"d1","to":"d2","label":"60%"},{"from":"d1","to":"d3","route":"elbow","dashed":true,"label":"40%"}]'> -->
<div class="col" style="position: relative;">
  <div data-shape="chevron" style="position:absolute;left:14pt;top:4pt;width:160pt;height:36pt;background:var(--sfnl-orange);">
    <p style="color:var(--sfnl-white);font-size:11pt;padding:6pt;">FASE 1</p>
  </div>
  <div id="d1" style="position:absolute;left:34pt;top:86pt;width:150pt;height:46pt;border-radius:6pt;background:var(--sfnl-royal);">
    <p style="color:var(--sfnl-white);font-size:11pt;padding:6pt;">Uitvoering diagnostiek</p>
  </div>
  <div id="d2" style="position:absolute;left:320pt;top:56pt;width:150pt;height:46pt;border-radius:6pt;background:var(--sfnl-emerald);">
    <p style="color:var(--sfnl-white);font-size:11pt;padding:6pt;">Erfelijke oorzaak aantoonbaar</p>
  </div>
  <div id="d3" style="position:absolute;left:320pt;top:176pt;width:150pt;height:46pt;border-radius:6pt;background:var(--sfnl-sky);">
    <p style="color:var(--sfnl-white);font-size:11pt;padding:6pt;">Geen vervolgonderzoek</p>
  </div>
</div>
```

## Veranderttheorie-map — exhibit: veranderttheorie-map

Volvlak-infographic: navy zijpaneel met het maatschappelijk vraagstuk, dan kolommen met
pill-headers in merkkleur (`data-shape="pill"`), gestapelde getinte nodes eronder, en een
onderband voor aannames/randvoorwaarden. Bekijk (Read)
`engine/reference/exhibits/veranderttheorie-map.png`. Verbind kolommen desgewenst met
`data-connectors` op `<body>` (geef de nodes dan een `id`).

```html
<div class="col" style="flex-direction: row; gap: 8pt;">
  <div class="card-soft" style="width: 120pt; background: var(--sfnl-navy);">
    <p class="label" style="color: var(--sfnl-white);">MAATSCHAPPELIJK VRAAGSTUK</p>
    <p style="color: var(--sfnl-white); font-size: 11pt;">Doodsoorzaken bij jong, onverwacht overlijden blijven vaak onbekend en structureel ongefinancierd.</p>
  </div>
  <div class="col" style="flex: 1; gap: 6pt;">
    <div class="col" style="flex-direction: row; gap: 6pt; flex: 1;">
      <div class="col" style="gap: 6pt;">
        <div data-shape="pill" style="height: 26pt; background: var(--sfnl-emerald);"><p style="color: var(--sfnl-white); font-size: 10pt; text-align: center;">ACTIVITEITEN</p></div>
        <div class="card-soft" style="flex: 1; background: var(--sfnl-emerald-tint80);"><p style="font-size: 11pt;">Landelijke structuur, communicatie en uitvoering van de interventie.</p></div>
      </div>
      <div class="col" style="gap: 6pt;">
        <div data-shape="pill" style="height: 26pt; background: var(--sfnl-sky);"><p style="color: var(--sfnl-white); font-size: 10pt; text-align: center;">OUTPUTS</p></div>
        <div class="card-soft" style="flex: 1; background: var(--sfnl-sky-tint80);"><p style="font-size: 11pt;">Meer en preciezere diagnostiek; betere data over doodsoorzaken.</p></div>
      </div>
      <div class="col" style="gap: 6pt;">
        <div data-shape="pill" style="height: 26pt; background: var(--sfnl-grapefruit);"><p style="color: var(--sfnl-white); font-size: 10pt; text-align: center;">OUTCOMES</p></div>
        <div class="card-soft" style="flex: 1; background: var(--sfnl-grapefruit-tint80);"><p style="font-size: 11pt;">Minder onnodige diagnostiek; verbeterde kennis en richtlijnen.</p></div>
      </div>
      <div class="col" style="gap: 6pt;">
        <div data-shape="pill" style="height: 26pt; background: var(--sfnl-orange);"><p style="color: var(--sfnl-white); font-size: 10pt; text-align: center;">IMPACT</p></div>
        <div class="card-soft" style="flex: 1; background: var(--sfnl-orange-tint80);"><p style="font-size: 11pt;">Doodsoorzaken beter vastgesteld; onnodige zorg voorkomen.</p></div>
      </div>
    </div>
    <div class="card-soft" style="background: var(--sfnl-dark-slate-tint80);"><p style="font-size: 10pt;"><b>AANNAMES &amp; RANDVOORWAARDEN:</b> aantoonbare meerwaarde, structurele financiering, juridische kaders en toepassing door zorgprofessionals.</p></div>
  </div>
</div>
```

## Effectenkaart — exhibit: effectenkaart-matrix

Matrix van gekleurde pills per kolom (outcome → KPI → financiële waarde → stakeholder), met een
geroteerd groepslabel links (`writing-mode: vertical-rl`) dat de stakeholdergroep codeert en
gestippelde verticale scheiders (`border-left: 1pt dashed`) tussen de kolomblokken. Bekijk (Read)
`engine/reference/exhibits/effectenkaart-matrix.png`.

```html
<div class="col" style="gap: 6pt;">
  <div class="col" style="flex-direction: row; gap: 6pt; align-items: stretch;">
    <div style="width: 22pt; background: var(--sfnl-grapefruit); border-radius: 4pt; display: flex; align-items: center; justify-content: center;">
      <p style="writing-mode: vertical-rl; transform: rotate(180deg); color: var(--sfnl-white); font-size: 10pt;">ZORGKOSTEN</p>
    </div>
    <div class="col" style="flex: 1; gap: 6pt;">
      <div class="col" style="flex-direction: row; gap: 6pt;">
        <div class="card-soft" style="flex: 2; background: var(--sfnl-grapefruit);"><p style="color: var(--sfnl-white); font-size: 11pt;">Zorgkosten interventie</p></div>
        <div class="card-soft" style="flex: 2; background: var(--sfnl-grapefruit);"><p style="color: var(--sfnl-white); font-size: 11pt;"># gerelateerde onderzoeken</p></div>
        <div style="width: 1pt; border-left: 1pt dashed var(--sfnl-navy);"></div>
        <div class="card-soft" style="flex: 2; background: var(--sfnl-grapefruit-tint80);"><p style="font-size: 11pt;">Salaris- en zorgkosten</p></div>
        <div class="card-soft" style="flex: 1; background: var(--sfnl-grapefruit-tint80);"><p style="font-size: 10pt;">Zorgverzekeraar</p></div>
      </div>
      <div class="col" style="flex-direction: row; gap: 6pt;">
        <div class="card-soft" style="flex: 2; background: var(--sfnl-grapefruit);"><p style="color: var(--sfnl-white); font-size: 11pt;">Vermeden acute events</p></div>
        <div class="card-soft" style="flex: 2; background: var(--sfnl-grapefruit);"><p style="color: var(--sfnl-white); font-size: 11pt;"># voorkomen events</p></div>
        <div style="width: 1pt; border-left: 1pt dashed var(--sfnl-navy);"></div>
        <div class="card-soft" style="flex: 2; background: var(--sfnl-grapefruit-tint80);"><p style="font-size: 11pt;">Besparing acute zorg</p></div>
        <div class="card-soft" style="flex: 1; background: var(--sfnl-grapefruit-tint80);"><p style="font-size: 10pt;">Zorgverzekeraar</p></div>
      </div>
    </div>
  </div>
</div>
```

## Chevron-procesband — exhibit: chevron-process

Drie fasepijlen (`data-shape="chevron"`) in achtereenvolgende merkkleuren met witte caps-titel,
elk met een getinte detailbox eronder (`.definition-box`); betekenisdragende iconen erboven
(optioneel, via `raster.js` → `<img>`). Bekijk (Read) `engine/reference/exhibits/chevron-process.png`.

```html
<div class="col" style="flex-direction: row; gap: 10pt;">
  <div class="col" style="gap: 8pt;">
    <div data-shape="chevron" style="height: 44pt; background: var(--sfnl-orange);"><p style="color: var(--sfnl-white); font-size: 12pt; text-align: center;">FASE 1: VERANDERTHEORIE</p></div>
    <div class="definition-box" style="flex: 1;"><p>Breng gezamenlijk de verandertheorie en effectenkaart in kaart; selecteer de relevante effecten.</p></div>
  </div>
  <div class="col" style="gap: 8pt;">
    <div data-shape="chevron" style="height: 44pt; background: var(--sfnl-emerald);"><p style="color: var(--sfnl-white); font-size: 12pt; text-align: center;">FASE 2: BUSINESSCASE</p></div>
    <div class="definition-box" style="flex: 1;"><p>Vertaal de effecten naar financiële posten en monetariseer ze op stakeholderniveau.</p></div>
  </div>
  <div class="col" style="gap: 8pt;">
    <div data-shape="chevron" style="height: 44pt; background: var(--sfnl-royal);"><p style="color: var(--sfnl-white); font-size: 12pt; text-align: center;">FASE 3: EINDRAPPORT</p></div>
    <div class="definition-box" style="flex: 1;"><p>Breng de resultaten samen en ga met stakeholders in gesprek over duurzame financiering.</p></div>
  </div>
</div>
```

## Statcomposities — exhibits: hero-stat-kpi, stat-cards-arrow, stat-cards-totalband

Navy statkaarten (`.stat-card`) met een groot Gotham-getal (`.stat-number`, oranje voor input,
teal voor uitkomst) en witte subtekst; input→effect-groepen verbonden door een grote lichte
achtergrondpijl (`data-shape="arrow-right"`); afgesloten met een navy totaalband met oranje
resultaat. Bekijk (Read) `engine/reference/exhibits/stat-cards-arrow.png` en `hero-stat-kpi.png`.

```html
<div class="col" style="gap: 10pt;">
  <div class="col" style="flex-direction: row; gap: 10pt; align-items: center; flex: 1;">
    <div class="stat-card" style="flex: 1;"><p class="stat-number">123</p><p>Extra gerichte doelgroeponderzoeken</p></div>
    <div class="stat-card" style="flex: 1;"><p class="stat-number">123</p><p>Extra preventieve behandelingen</p></div>
    <div data-shape="arrow-right" style="width: 60pt; height: 60pt; background: var(--sfnl-sky-tint80);"></div>
    <div class="stat-card" style="flex: 1;"><p class="stat-number" style="color: var(--sfnl-emerald);">123+</p><p>Voorkomen aandoeningen per jaar</p></div>
  </div>
  <div class="frame-band" style="display: flex; align-items: center; justify-content: space-between;">
    <p>Netto maatschappelijk resultaat</p>
    <p class="display" style="color: var(--sfnl-orange); font-size: 24pt;">€ 4,0 mln</p>
  </div>
</div>
```

## Stakeholder-ladder — exhibit: stakeholder-ladder

Resultaatladder: lichte rijen (`.ladder-row`) met links label + toelichting en rechts een groot
gekleurd bedrag (grapefruit=kost, emerald=baat), afgesloten met een navy totaalrij
(`.ladder-row.total`); conclusiezin eronder. Bekijk (Read)
`engine/reference/exhibits/stakeholder-ladder.png`.

```html
<div class="col" style="gap: 8pt;">
  <div class="ladder-row" style="justify-content: space-between;">
    <div><p style="font-size: 14pt;">Zorgverzekeraar / VWS</p><p class="label">Coördinatie, diagnostiek en behandeling</p></div>
    <p class="display" style="color: var(--sfnl-grapefruit); font-size: 20pt;">+ € 1,2 mln</p>
  </div>
  <div class="ladder-row" style="justify-content: space-between;">
    <div><p style="font-size: 14pt;">Doelgroeponderzoek</p><p class="label">Minder ziektelast door voorkomen incidenten</p></div>
    <p class="display" style="color: var(--sfnl-emerald); font-size: 20pt;">€ 2,1 mln</p>
  </div>
  <div class="ladder-row total" style="justify-content: space-between;">
    <p style="color: var(--sfnl-white); font-size: 14pt;">Netto maatschappelijk resultaat</p>
    <p class="display" style="color: var(--sfnl-orange); font-size: 20pt;">€ 4,0 mln</p>
  </div>
  <p class="label">De grootste baten vallen buiten het zorgbudget, bij doelgroeponderzoek en de maatschappij.</p>
</div>
```

## Icon-tiles & chips — exhibits: icon-tiles-bullets, icon-tile-grid, letter-chips, numbered-card-columns

Icon-tiles (`.icon-tile`, afgeronde gekleurde vierkanten met wit lijnicoon + caps-label) naast
bullettekst; letter-/nummer-chips (`.chip`) + titel + toelichting met chipkleur door het palet;
en genummerde kaartkolommen (`.card-soft` in pasteltint met cirkelnummer-badge en gekleurde
titel). Bekijk (Read) `engine/reference/exhibits/icon-tiles-bullets.png`, `letter-chips.png` en
`numbered-card-columns.png`. Iconen genereer je met `raster.js` (wit lijnicoon op de tilekleur).

```html
<div class="col" style="flex-direction: row; gap: 14pt;">
  <div class="col" style="flex: 1; gap: 8pt;">
    <div class="col" style="flex-direction: row; gap: 10pt; align-items: center;">
      <div class="icon-tile" style="background: var(--sfnl-grapefruit);">
        <img src="assets/icon-communicatie.png" alt="">
        <p>COMMUNICATIE</p>
      </div>
      <ul style="font-size: 12pt;"><li>Drempels verlagen voor deelname en doorverwijzing.</li><li>Laten zien wat het programma oplevert.</li></ul>
    </div>
    <div class="col" style="flex-direction: row; gap: 10pt; align-items: center;">
      <div class="chip" style="background: var(--sfnl-royal);"><p>A</p></div>
      <div><p style="font-size: 14pt;">Verandertheorie</p><p class="label">Hoe de interventie tot impact leidt.</p></div>
    </div>
  </div>
  <div class="card-soft" style="flex: 1; background: var(--sfnl-sky-tint80);">
    <div class="chip" style="border-radius: 17pt; background: var(--sfnl-navy);"><p>1</p></div>
    <p style="color: var(--sfnl-navy); font-size: 14pt; margin-top: 6pt;">Vragenlijst bij intake</p>
    <p class="label">WANNEER — eerste gesprek</p>
    <ul style="font-size: 11pt;"><li>Demografische gegevens</li><li>Nulmeting welbevinden</li></ul>
  </div>
</div>
```

## Native hook

Complexe elementen die HTML niet betrouwbaar bouwt (bijzondere vormen, PowerPoint-native
constructies) kunnen via de per-deck hook (`slide.addTable`, `slide.addShape`; zie de authoring
guide). Tabellen hoeven **niet** meer via de hook: `<table class="sfnl-table …">` wordt native en
bewerkbaar geconverteerd. Gebruik de hook alleen wanneer een patroon hierboven niet volstaat.

```html
<div class="frame-panel royal" style="flex: 1;">
  <p class="label">NATIVE HOOK</p>
  <p>Gebruik de hook voor speciale vormen of PowerPoint-native elementen buiten deze grammatica; documenteer waarom een standaardpatroon niet volstaat.</p>
</div>
```
