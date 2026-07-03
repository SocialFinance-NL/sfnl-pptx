# sfnl-pptx

Generate and QA **Social Finance NL** branded PowerPoint decks.

The plugin works **composition-first**: the agent authors one free-form HTML file per slide on a
shared SFNL scaffold plus a `deck.json` manifest, and a Node build layer (vendored `html2pptx` +
PptxGenJS) converts them into a `.pptx` with editable text boxes, real shapes, and native
editable charts. Every build ends with a mandatory visual loop: render every slide to PNG,
inspect, fix the HTML, rebuild — until clean. Colors come from the generated brand tokens and
only the three brand fonts are used.

> **Self-contained — no template upload required.** The SFNL chrome (title treatment, orange
> dash, logo, page number) is built into `engine/web/sfnl.css` + `build_deck.js`. The original
> sjabloon stays bundled at `engine/assets/sfnl-template.pptx` purely as visual reference.

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
     ─▶ slides/*.html + deck.json ─▶ build_deck.js (html2pptx + PptxGenJS) ─▶ deck.pptx
     ─▶ visuele loop (render.py ─▶ inspect PNGs ─▶ fix HTML ─▶ rebuild, tot schoon)
     ─▶ review ─▶ proof (full render + feitenproef + rapport)
```

1. **Author** slides per [`engine/reference/authoring-guide.md`](engine/reference/authoring-guide.md),
   starting from `engine/web/scaffold.html` / `engine/web/archetypes/`, with layout patterns from
   [`engine/web/patterns.md`](engine/web/patterns.md).
2. **Build** with `node engine/web/build/build_deck.js output/<datum>-<slug>` (built-in
   validation fails loudly on overflow, gradients, text outside text tags, dimension mismatch).
3. **Render + inspect** with `python -m scripts.render <deck.pptx> <out_dir>` (from
   `sfnl-pptx/engine`) — mandatory for every build, all slides.
4. **Text-QA** with `python -m scripts.qa_text <deck.pptx>`.

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
│                           sfnl-deck-review, sfnl-deck-proof (SKILL.md each)
├── agents/                 deck-visual-reviewer (render + inspect subagent)
├── engine/
│   ├── assets/             bundled sjabloon + sfnl-slides.pptx (officiële covers/dividers)
│   │                       + generated palette.json
│   ├── reference/          authoring-guide.md, brand.md, voice.md
│   ├── scripts/            qa_text, render, extract_palette, extract_chrome (python)
│   └── web/                sfnl.css, tokens.json, scaffold.html, archetypes/, patterns.md,
│                           assets/ (logo, chrome/ officiële slide-PNG's + manifest),
│                           build/ (html2pptx, build_deck, charts, raster, tests)
└── tests/                  pytest suite
```
