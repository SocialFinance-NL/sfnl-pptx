# sfnl-pptx

Generate and QA **Social Finance NL** branded PowerPoint decks.

The plugin works **composition-first**: the agent authors one free-form HTML file per slide on a
shared SFNL scaffold plus a `deck.json` manifest, and a Node build layer (vendored `html2pptx` +
PptxGenJS) converts them into a `.pptx` with editable text boxes, real shapes, and native
editable charts. Every build ends with a mandatory visual loop: render every slide to PNG,
inspect, fix the HTML, rebuild — until clean. Colors come from the generated brand tokens and
only the three brand fonts are used.

> **Self-contained — no template upload required.** The SFNL chrome (title treatment, orange
> dash, logo, page number) is built into `engine/web/sfnl.css` + `build_deck.js`. The official
> source sjabloon is bundled at `engine/assets/sfnl-sjabloon.potx`; every build embeds its
> masters/layouts into the generated `.pptx` so PowerPoint's New Slide / Layout gallery contains
> the official SFNL layouts.

> **Covers and section dividers are never invented.** Title slides, section dividers and quote
> slides always use the official designs from `engine/assets/sfnl-slides.pptx`, exposed as
> ready-made archetypes (`engine/web/archetypes/cover-*`, `divider-*`, `quote-*`) with the
> official slide render as background and text slots on the sjabloon placeholder positions.
> Regenerate after a sjabloon update with `python -m scripts.extract_chrome` (from `engine/`);
> the catalog lives in `engine/web/assets/chrome/manifest.json`.

## Plugin manifests

- Claude: `.claude-plugin/plugin.json`
- Codex: `.codex-plugin/plugin.json`, with `skills` pointing to `./skills/` and Codex interface
  metadata for plugin ingestion.

## Skills

| Skill | Use it to |
|-------|-----------|
| `sfnl-deck` | Build a new SFNL deck from a brief, outline, or source docs (orchestrates the full pipeline). |
| `sfnl-deck-research` | Turn an idea into a bronnendossier (feiten, cijfers, bronnen) before any slide is written. |
| `sfnl-deck-design` | Storyboard every slide (composition, regions, accent, chart candidates, rationale) before authoring HTML. |
| `sfnl-deck-review` | QA against the Content / Design / Coherence rubric; core is the full render-inspect-fix loop. |
| `sfnl-deck-proof` | Full pre-delivery proof: render every slide, whole-deck visual review, fact-check against the dossier, proefrapport. |
| `sfnl-deck-edit` | Edit an existing SFNL `.pptx` with no HTML source: backup, inventory, text/slide/chrome/OOXML edits, QA and render. |

Triggers are described in each skill's frontmatter — e.g. "maak een presentatie", "nieuwe slides
in huisstijl", "SFNL deck", "review/check this SFNL .pptx", or "final proof / klaar voor de klant".

## Dev tooling (intern)

| Skill / agent | Doel |
|------|------|
| `sfnl-deck-retro` | Interne dogfooding-run: draait een verzonnen deck door de volledige pipeline en levert een verbeterrapport over de plugin zelf. Nooit voor een echte klant-deck. |
| `deck-process-reviewer` (agent) | Dispatched door `sfnl-deck-retro` na elke stage; beoordeelt het proces (frictie, doc-gaten, automatiseringskansen, laat-gevangen missers), niet de deck. |

## How it works

```
idee ─▶ research (bronnendossier) ─▶ narrative + action titles ─▶ storyboard
     ─▶ slides/*.html + deck.json ─▶ build_deck.js (html2pptx + PptxGenJS + sjabloon merge)
     ─▶ deck.pptx
     ─▶ visuele loop (render.py ─▶ inspect PNGs ─▶ fix HTML ─▶ rebuild, tot schoon)
     ─▶ review ─▶ proof (full render + feitenproef + rapport)
```

1. **Author** slides per [`engine/reference/authoring-guide.md`](engine/reference/authoring-guide.md),
   starting from `engine/web/scaffold.html` / `engine/web/archetypes/`, with layout patterns from
   [`engine/web/patterns.md`](engine/web/patterns.md).
2. **Build** with `node engine/web/build/build_deck.js output/<datum>-<slug>` (built-in
   validation fails loudly on overflow, gradients, text outside text tags, dimension mismatch,
   and missing/corrupt bundled sjabloon layouts).
3. **Render + inspect** with `python -m scripts.render <deck.pptx> <out_dir>` (from
   `sfnl-pptx/engine`) — mandatory for every build, all slides.
4. **Text-QA** with `python -m scripts.qa_text <deck.pptx>`.
5. **Layout-gallery QA** when PowerPoint COM is available:
   `python -m scripts.render --assert-layouts <deck.pptx> 31`.
6. **Existing deck edits** use `sfnl-deck-edit`: copy the deck to `original.pptx`, inventory it,
   apply targeted edits, then run the same text-QA and render loop.

## Complexe visuals

Vier native capabilities boven op vrije HTML-compositie:

- **Tabellen** — HTML `<table class="sfnl-table {orange|royal|teal|navy}">` (met
  `section-row`/`total-row`, `col-num`/`val-cost`/`val-benefit`/`col-source`) converteert naar een
  echte, bewerkbare PowerPoint-tabel.
- **Shapes** — `<div data-shape="chevron|pill|circle|arrow-right|arrow-left|arrow-up|arrow-down">`
  wordt een native autoshape.
- **Connectors** — `data-connectors` op `<body>` verbindt genoemde node-`id`'s met pijlen
  (straight/elbow, dashed, labels).
- **Exhibit-galerij** — `engine/reference/exhibits/` (catalogus: `manifest.md`) is de
  referentiegrammatica voor tabellen, diagrammen en statcomposities; bekijk (Read) het
  bijpassende exhibit vóór het bouwen, en herbouw de grammatica in plaats van hem te kopiëren.

De exhibits zijn geanonimiseerd (namen en cijfers zijn templatewaarden), maar de layoutherkomst
blijft klantprojecten, en de git-geschiedenis van vóór de anonimisatie bevat nog de
niet-geanonimiseerde PNG's — een reden om deze repo privé te houden.

## Prerequisites

- **Node.js 20+**. One-time setup: `cd engine/web/build && npm install && npx playwright install chromium`.
- **Python 3.13+** with **[python-pptx](https://python-pptx.readthedocs.io/)** (text QA).
- **Render pass (Windows):** Microsoft PowerPoint plus **pywin32** for PNG export via COM.
  Check availability with `python -m scripts.render --check`.
- The three brand fonts (Gotham Bold, Lato Light, Montserrat Light) installed locally. Fonts are
  never embedded.

## Reference docs

| File | Contents |
|------|----------|
| [`engine/reference/authoring-guide.md`](engine/reference/authoring-guide.md) | Workspace, HTML rules, deck.json + chart spec schema, build & visual loop. |
| [`engine/web/patterns.md`](engine/web/patterns.md) | Layout pattern cookbook (KPI rows, swimlanes, matrices, …). |
| [`engine/reference/brand.md`](engine/reference/brand.md) | Palette (hex tokens), typography, chrome, composition rules. |
| [`engine/reference/voice.md`](engine/reference/voice.md) | SCQA narrative, action titles, big numbers, register. |
| [`engine/reference/editing-guide.md`](engine/reference/editing-guide.md) | Editing existing `.pptx` files without HTML source: inventory, replacements, chrome insertion, OOXML. |

## Testing

```bash
cd sfnl-pptx && python -m pytest tests -q     # python: tokens, build integration, qa, E2E render
cd sfnl-pptx/engine/web/build && npm test     # node: html2pptx, tokens, charts, raster, archetypes
```

## Layout

```
sfnl-pptx/
├── .codex-plugin/          Codex plugin manifest
├── .claude-plugin/         Claude plugin manifest
├── skills/                 sfnl-deck, sfnl-deck-research, sfnl-deck-design,
│                           sfnl-deck-review, sfnl-deck-proof, sfnl-deck-edit
│                           (SKILL.md each)
├── agents/                 deck-visual-reviewer (render + inspect subagent)
├── engine/
│   ├── assets/             bundled sjabloon assets (`sfnl-sjabloon.potx`,
│   │                       `sfnl-template.pptx`, `sfnl-slides.pptx`) + palette.json
│   ├── ooxml/              unpack/validate/pack escape hatch for existing-deck edits
│   ├── reference/          authoring-guide.md, editing-guide.md, brand.md, voice.md
│   ├── scripts/            qa_text, render, inventory, replace, rearrange,
│   │                       insert_chrome_slide, extract_palette, extract_chrome (python)
│   └── web/                sfnl.css, tokens.json, scaffold.html, archetypes/, patterns.md,
│                           assets/ (logo, chrome/ officiële slide-PNG's + manifest),
│                           build/ (html2pptx, build_deck, charts, raster, tests)
└── tests/                  pytest suite
```
