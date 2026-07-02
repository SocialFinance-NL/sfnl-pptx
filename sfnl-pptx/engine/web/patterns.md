# SFNL layout patterns — cookbook, geen catalogus

Kopieer, pas aan, componeer. Merkregels reizen mee:

- **Eén accent per deck** (default `deck.json.accent`); kleur codeert betekenis, nooit decoratie.
- **Big numbers**: groot cijfer (Gotham Bold, accentkleur), klein label eronder (Montserrat Light caps).
- **Volledige hoogte**: de content vult het canvas; een half-lege slide is een defect.
- **Ruime, gelijke marges**; chrome (titel + dash) altijd aanwezig op contentslides.
- Tekstregels: alle tekst in `<p>/<h1>-<h6>/<ul>/<ol>`; achtergrond/rand alleen op `<div>`;
  geen CSS-gradients (pre-render via Sharp); titels in ALL CAPS getypt.

Fragmenten hieronder horen binnen het scaffold's `<main class="content">`.

## KPI-rij met grote cijfers

```html
<div class="col" style="flex-direction: row; gap: 14pt;">
  <div class="card"><p class="big-number">31%</p><p class="label" style="margin-top: 6pt;">MINDER UITVAL</p><p style="margin-top: 8pt;">Eén regel duiding bij het cijfer.</p></div>
  <div class="card"><p class="big-number">124</p><p class="label" style="margin-top: 6pt;">TRAJECTEN</p><p style="margin-top: 8pt;">Eén regel duiding.</p></div>
  <div class="card"><p class="big-number">€ 0,9M</p><p class="label" style="margin-top: 6pt;">BESPARING</p><p style="margin-top: 8pt;">Eén regel duiding.</p></div>
</div>
```

## Twee-koloms exhibit (tekst + chart)

```html
<div class="col" style="flex: 2;">
  <p class="kicker">WAT WE ZIEN</p>
  <ul style="margin-top: 6pt;"><li>Eerste observatie.</li><li>Tweede observatie.</li></ul>
</div>
<div class="col" style="flex: 3;">
  <div id="chart-main" class="placeholder" style="flex: 1;"></div>
</div>
```

Registreer `chart-main` in `deck.json` → `slides[].charts[]` (zie authoring guide).

## Swimlane-kolommen (categorie per kleur — multi-accent decks)

```html
<div class="col">
  <div style="background: var(--sfnl-grapefruit); border-radius: 4pt; padding: 6pt 10pt;"><p class="label" style="color: #FFFFFF;">VRAAGSTUK</p></div>
  <div class="card" style="background: var(--sfnl-grapefruit-tint80);"><p>Inhoud…</p></div>
</div>
<div class="col">
  <div style="background: var(--sfnl-emerald); border-radius: 4pt; padding: 6pt 10pt;"><p class="label" style="color: #FFFFFF;">ACTIVITEITEN</p></div>
  <div class="card" style="background: var(--sfnl-emerald-tint80);"><p>Inhoud…</p></div>
</div>
<div class="col">
  <div style="background: var(--sfnl-orange); border-radius: 4pt; padding: 6pt 10pt;"><p class="label" style="color: #FFFFFF;">IMPACT</p></div>
  <div class="card" style="background: var(--sfnl-orange-tint80);"><p>Inhoud…</p></div>
</div>
```

## Proces-stappen

```html
<div class="col" style="flex-direction: row; gap: 8pt; align-items: stretch;">
  <div class="card card-accent" style="flex: 1;"><p class="kicker">STAP 1</p><p style="margin-top: 6pt;"><b>Verkennen</b></p><p>Korte omschrijving.</p></div>
  <div class="card" style="flex: 1;"><p class="kicker">STAP 2</p><p style="margin-top: 6pt;"><b>Ontwerpen</b></p><p>Korte omschrijving.</p></div>
  <div class="card" style="flex: 1;"><p class="kicker">STAP 3</p><p style="margin-top: 6pt;"><b>Uitvoeren</b></p><p>Korte omschrijving.</p></div>
</div>
```

(Voor echte pijlpunten/chevrons: rasterize een PNG via Sharp in `assets/` en gebruik `<img>`.)

## 2×2-matrix

```html
<div class="col" style="display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 10pt;">
  <div class="card card-accent"><p class="kicker">HOOG / LAAG</p><p>Kwadrant.</p></div>
  <div class="card"><p class="kicker">HOOG / HOOG</p><p>Kwadrant.</p></div>
  <div class="card"><p class="kicker">LAAG / LAAG</p><p>Kwadrant.</p></div>
  <div class="card"><p class="kicker">LAAG / HOOG</p><p>Kwadrant.</p></div>
</div>
```

## Scenario-kaarten

```html
<div class="col" style="flex-direction: row;">
  <div class="card" style="border-top: 3pt solid var(--sfnl-orange);"><p class="kicker">SCENARIO A</p><p class="big-number" style="font-size: 20pt; margin-top: 6pt;">€ 1,2M</p><p style="margin-top: 6pt;">Aannames in één regel.</p></div>
  <div class="card" style="border-top: 3pt solid var(--sfnl-orange);"><p class="kicker">SCENARIO B</p><p class="big-number" style="font-size: 20pt; margin-top: 6pt;">€ 2,1M</p><p style="margin-top: 6pt;">Aannames in één regel.</p></div>
</div>
```

## Evidence stack / lagenmodel

```html
<div class="col" style="justify-content: center; gap: 6pt;">
  <div style="background: var(--sfnl-navy); border-radius: 4pt; padding: 8pt 14pt;"><p style="color: #FFFFFF;"><b>Impact</b> — maatschappelijk resultaat</p></div>
  <div style="background: var(--sfnl-royal); border-radius: 4pt; padding: 8pt 14pt; margin: 0 24pt;"><p style="color: #FFFFFF;"><b>Outcomes</b> — gedragsverandering</p></div>
  <div style="background: var(--sfnl-sky); border-radius: 4pt; padding: 8pt 14pt; margin: 0 48pt;"><p style="color: #FFFFFF;"><b>Output</b> — geleverde trajecten</p></div>
</div>
```

## Cyclus / mechanisme

Posities absoluut binnen een relatief gepositioneerde container; verbindingslijnen als dunne
`<div>`s (bv. `height: 1.5pt; background: var(--sfnl-grey-70);`), knopen als cirkels
(`border-radius: 50%`). Pijlpunten: PNG via Sharp (`build/raster.js`).

## Assessment-tabel

Gebruik geen HTML `<table>` (niet ondersteund) — bouw rijen als flex-divs:

```html
<div class="col" style="gap: 4pt;">
  <div style="display: flex; gap: 4pt;">
    <div style="flex: 2; background: var(--sfnl-navy); padding: 5pt 8pt;"><p class="label" style="color: #FFFFFF;">CRITERIUM</p></div>
    <div style="flex: 1; background: var(--sfnl-navy); padding: 5pt 8pt;"><p class="label" style="color: #FFFFFF;">OORDEEL</p></div>
  </div>
  <div style="display: flex; gap: 4pt;">
    <div style="flex: 2; background: var(--sfnl-grey-95); padding: 5pt 8pt;"><p>Haalbaarheid</p></div>
    <div style="flex: 1; background: var(--sfnl-emerald-tint60); padding: 5pt 8pt;"><p><b>Sterk</b></p></div>
  </div>
</div>
```

Complexe tabellen kunnen ook native: via de per-deck hook (`slide.addTable`, zie authoring guide).

## Iconen

Rasterize react-icons naar merkkleur-PNGs in de workspace `assets/` (zie authoring guide,
`build/raster.js`) en plaats met `<img style="width: 22pt; height: 22pt;">`. Iconen zijn inhoud,
geen decoratie: kies op betekenis.
