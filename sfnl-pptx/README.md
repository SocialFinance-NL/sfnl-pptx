# sfnl-pptx

Generate and QA **Social Finance NL** branded PowerPoint decks from the official sjabloon.

The plugin works **spec-first**: the agent thinks once into a compact deck-spec JSON, then the engine
builds the `.pptx` deterministically on a clone of the bundled SFNL template. Colors are always
`schemeClr` (never hardcoded hex) and only the three brand fonts are used.

> **Self-contained — no template upload required.** The SFNL sjabloon is bundled at
> `engine/assets/sfnl-template.pptx` (theme, both masters, all 30 layouts) and loaded directly by
> the build. You never need to supply, upload, or point at a `.potx` file.

## Plugin manifests

- Claude: `.claude-plugin/plugin.json`
- Codex: `.codex-plugin/plugin.json`, with `skills` pointing to `./skills/` and Codex interface
  metadata for plugin ingestion.

## Skills

| Skill | Use it to |
|-------|-----------|
| `sfnl-deck` | Build a new SFNL deck from a brief, outline, or source docs (orchestrates the full pipeline). |
| `sfnl-deck-research` | Turn an idea into a bronnendossier (feiten, cijfers, bronnen) before any slide is written. |
| `sfnl-deck-design` | Storyboard every slide (component, accent, icon, rationale) before authoring JSON. |
| `sfnl-deck-review` | Adaptive QA against the Content / Design / Coherence rubric while building. |
| `sfnl-deck-proof` | Full pre-delivery proof: render every slide, whole-deck visual review, fact-check against the dossier, proefrapport. |

Triggers are described in each skill's frontmatter — e.g. "maak een presentatie", "nieuwe slides
in huisstijl", "SFNL deck", "review/check this SFNL .pptx", or "final proof / klaar voor de klant".

## How it works

```
idee ─▶ research (bronnendossier) ─▶ narrative + action titles ─▶ storyboard
     ─▶ deck-spec.json ─▶ validate ─▶ build_from_spec ─▶ deck.pptx
     ─▶ review (qa_text + render sensitive) ─▶ proof (full render + feitenproef + rapport)
```

1. **Author** a deck-spec following [`engine/reference/deck-spec.md`](engine/reference/deck-spec.md).
2. **Validate** with `scripts.spec.validate_spec` (also run by the build).
3. **Build** with `python -m scripts.build_from_spec <spec.json> [out.pptx]`.
4. **QA** with `python -m scripts.qa_text <deck.pptx>` (cheap text checks) and, for custom or
   sensitive slides, `python -m scripts.render <deck.pptx> <out_dir>` (PNG render).

Run all scripts from `sfnl-pptx/engine`, or set `PYTHONPATH` so `import scripts.*` resolves.

## Prerequisites

- **Python 3.13+** with **[python-pptx](https://python-pptx.readthedocs.io/)** (build + text QA).
- **Render pass (optional, Windows only):** Microsoft PowerPoint plus **pywin32**, used to export
  slides to PNG via COM automation. Check availability with `python -m scripts.render --check`.
  LibreOffice is a documented fallback only and is not implemented.
- The three brand fonts (Gotham Bold, Lato Light, Montserrat Light) installed locally for correct
  on-screen rendering. Fonts are never embedded.

## Reference docs

| File | Contents |
|------|----------|
| [`engine/reference/deck-spec.md`](engine/reference/deck-spec.md) | Deck-spec JSON schema + full component catalogue. |
| [`engine/reference/brand.md`](engine/reference/brand.md) | Palette (theme slots), typography, spacing rules. |
| [`engine/reference/voice.md`](engine/reference/voice.md) | SCQA narrative, action titles, big numbers, register. |

## Testing

```bash
cd sfnl-pptx/engine
python -m pytest ../tests -q
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
│   ├── assets/             bundled template + generated palette/layouts/components
│   ├── reference/          deck-spec.md, brand.md, voice.md
│   └── scripts/            build_from_spec, spec, components, qa_text, render, colors, ...
└── tests/                  pytest suite
```
