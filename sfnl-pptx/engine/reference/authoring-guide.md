# SFNL deck authoring guide (html2pptx pipeline)

Eén HTML-bestand per slide + één `deck.json` per deck. De build converteert naar een `.pptx`
met bewerkbare tekstvakken, echte shapes, native charts en de officiële SFNL
PowerPoint-layoutgalerij uit het gebundelde sjabloon.

## Workspace

```
output/<YYYY-MM-DD>-<slug>/
  deck.json
  slides/01-cover.html … NN-closing.html
  slides/sfnl.css        # kopie van engine/web/sfnl.css
  slides/chrome/         # kopie van engine/web/assets/chrome/ (officiële cover/divider-PNG's)
  assets/                # gerasterde iconen/gradients (Sharp)
  renders/               # PNG-renders van de visuele loop
  <slug>.pptx
```

Aanmaken: map maken, `engine/web/sfnl.css` naar `slides/` kopiëren en `engine/web/assets/chrome/`
naar `slides/chrome/`. Contentslides starten vanaf `engine/web/scaffold.html` (patronen:
`engine/web/patterns.md`, plus `stat-banner`-archetype).

**Titelslides, sectiedividers en quotes komen verplicht uit de officiële archetypes**
(`engine/web/archetypes/cover-01…04.html`, `divider-01…10.html`, `quote-01.html`). Die zijn
gegenereerd uit het officiële sjabloon (`engine/assets/sfnl-slides.pptx`, via
`python -m scripts.extract_chrome`): de slide-achtergrond is de officiële PNG, de tekstslots
(class `chrome-slot`) staan op de sjabloon-placeholderposities. Kopieer het archetype, vervang
alleen de slotteksten, en verplaats of herstijl de slots niet. `cover-02`/`cover-03` hebben geen
tekstslots (opening/afsluiter). De catalogus met beschrijvingen en het `chrome`-advies per
variant staat in `engine/web/assets/chrome/manifest.json`.

Before choosing a cover/divider/quote archetype, compare required text fields with
`assets/chrome/manifest.json`. If the slide needs title + subtitle + metadata, choose a variant
with those slots or move metadata to notes. Do not add extra text boxes to official archetype
slides unless the manifest explicitly provides a matching slot.

## HTML-regels (hard — de build faalt of verliest tekst bij overtreding)

- Canvas exact `width: 720pt; height: 405pt` op `<body>`.
- **Alle tekst in `<p>`, `<h1>`–`<h6>`, `<ul>` of `<ol>`** — tekst los in een `<div>`/`<span>`
  verdwijnt geluidloos.
- Achtergrond/rand/schaduw alleen op `<div>`; `<table>` wordt niet ondersteund (flex-rijen of
  native via hook).
- **Nooit CSS-gradients** — pre-render PNG via `node engine/web/build/raster.js gradient …`.
- Iconen: `node engine/web/build/raster.js icon fa FaUsers F87F4F 256 assets/users.png`, dan `<img>`.
- Tekst > 12pt eindigt ≥ 0.5in boven de onderrand (de `.content`-marges regelen dit).
- Titels/subtitels **in ALL CAPS getypt** (CSS `text-transform` telt niet).
- Logo en paginanummer **niet** in HTML — `build_deck.js` injecteert die native.
- Charts: reserveer ruimte met `<div id="…" class="placeholder" style="…">` en registreer de
  chart in `deck.json`.

## deck.json

```json
{
  "title": "DEKTITEL",
  "slug": "kebab-slug",
  "language": "nl",
  "author": "Social Finance NL",
  "accent": "orange",
  "hooks": null,
  "slides": [
    { "file": "slides/01-cover.html", "chrome": "none", "notes": "Bron: R1" },
    { "file": "slides/02-x.html", "notes": "Bron: R2, R5",
      "charts": [{
        "placeholder": "chart-main",
        "type": "column",
        "title": null,
        "series": [{ "name": "Reeks", "labels": ["2024", "2025"], "values": [120, 180] }],
        "axis": { "catTitle": "Jaar", "valTitle": "Aantal", "valMin": 0, "valMax": 200, "majorUnit": 50 },
        "colors": ["orange"]
      }] }
  ]
}
```

- `accent`: één accent per deck (default `orange`); `colors` per chart alleen bij betekenisvol
  kleurgebruik (categorieën), namen uit `palette.json` (`orange`, `grapefruit`, `royal`, `sky`,
  `emerald`, `navy`, `dark slate`).
  Chart colors accept palette names plus aliases: `neutral`/`grey`/`gray` → `dark slate`,
  `result` → `orange`, `risk` → `grapefruit`, `positive` → `emerald`.
- `chrome`: `"light"` (default: logo + oranje paginanummer), `"dark"` (wit paginanummer, geen
  logo — voor dividers), `"number"` (alleen oranje paginanummer — voor sjabloonslides die hun
  logo al in het ontwerp dragen, zoals `quote-01`), `"none"` (cover/closing). Voor archetypes:
  volg het advies in `chrome/manifest.json`.
- `notes`: speaker notes; verwijs elke claim naar bronnendossier-regels (R-id's).
- `type`: `column | stackedColumn | bar | line | area | pie | donut | scatter`. Scatter volgt de
  PptxGenJS-conventie: eerste serie = X-waarden, volgende series = Y-waarden.
- `hooks` (escape hatch): pad naar JS-module met
  `module.exports = { afterSlide: async ({ pptx, slide, entry, index, placeholders }) => {…} }`
  voor exotische slides met directe PptxGenJS-calls (bv. `slide.addTable`).

## Bouwen en de verplichte visuele loop

```powershell
node engine/web/build/build_deck.js output/<datum>-<slug>       # bouwt <slug>.pptx
# vanuit sfnl-pptx/engine:
python -m scripts.render ../../output/<datum>-<slug>/<slug>.pptx ../../output/<datum>-<slug>/renders
python -m scripts.qa_text ../../output/<datum>-<slug>/<slug>.pptx
python -m scripts.render --assert-layouts ../../output/<datum>-<slug>/<slug>.pptx 31
```

Elke build eindigt pas na de visuele loop: render → elke PNG bekijken (cutoff, overlap,
onbalans, dode witruimte, contrast, chrome-integriteit) → HTML fixen → rebuild → re-render,
tot schoon. De buildvalidatie (overflow, gradients, tekst-buiten-tags, maatafwijking) is de
eerste QA-poort en faalt luid met alle fouten tegelijk. `build_deck.js` embedt na het schrijven
automatisch de masters/layouts uit `engine/assets/sfnl-sjabloon.potx`; ontbreekt die asset of
faalt de OOXML-merge, dan faalt de build. De `--assert-layouts` check opent de deck via echte
PowerPoint-COM en is de gezaghebbende controle wanneer PowerPoint beschikbaar is.

If `python -m scripts.render --check` reports PowerPoint COM unavailable, the build is not visually
cleared. Use the Codex presentations `container_tools/render_slides.py` artifact-tool renderer
when available to create diagnostic PPTX screenshots/contact sheets, or HTML screenshots as a
weaker fallback. The status remains `GEBLOKKEERD OP RENDER` until a PowerPoint render succeeds.
Report the skipped PowerPoint render explicitly in build QA, review, and proof.

## Eenmalige setup (per machine)

```powershell
cd sfnl-pptx/engine/web/build
npm install
npx playwright install chromium
```

Brand fonts (Gotham Bold, Lato Light, Montserrat Light) moeten lokaal geïnstalleerd zijn;
ze worden nooit embedded.
