# SFNL PowerPoint Plugin — Design Spec

**Date:** 2026-06-26
**Status:** Approved architecture (Approach A), pending spec review
**Author:** Brainstormed with Xavier (SFNL)

---

## 1. Purpose

A Claude Code **plugin** that produces Social Finance NL (SFNL) branded PowerPoint decks
directly from the officially-ordered **sjablon** (`01 SFNL_sjabloon.potx`), with three core
capabilities:

1. **Generate** consultant-quality decks from a brief, outline, or source documents — both
   standard slides (title, dividers) *and* invented non-standard slides (KPIs, graphs,
   timelines) that stay inside brand guardrails.
2. **Edit** existing decks efficiently (this is where token waste is real — minimize it).
3. **Think / Review** every deck against a structured quality rubric before declaring done.

The non-negotiable cross-cutting goal is **token efficiency**.

The plugin ships the sjablon and all tooling so the user never has to provide the template.

---

## 2. Design decisions (locked via 20-question interview)

| # | Decision | Choice |
|---|----------|--------|
| 1 | Relationship to old skills | **New plugin; keep old skills installed** (retire later) |
| 2 | Sjablon source | **Bundle the `.potx` inside the plugin** |
| 3 | Build engine | **Both available, choose per slide** (python-pptx-on-template is backbone; pptxgenjs when its API is genuinely easier) |
| 4 | Audience | **Just me / power users** (capability over hand-holding) |
| 5 | Slide library | **Core structural set now**, architected for an extensible, searchable library later |
| 6 | Token strategy | **Optimized by us** → spec-first + parameterized scripts + component snippets |
| 7 | Language | **NL & EN equally** |
| 8 | Input modes | **Generation skill** (brief/outline/source → outline → deck) + **separate efficient edit skill** |
| 9 | Component search | **Tagged JSON index + thumbnails** |
| 10 | QA depth | **Adaptive by slide type** — render custom/sensitive slides; cheap checks on template-faithful ones |
| 11 | Edit approach | **Adaptive by edit type** (XML surgery / slide regenerate / diff) |
| 12 | Voice | **Built in natively** (SFNL register + consultant theme + anti-AI) |
| 13 | Render runtime | **Fastest/best on Windows** — LibreOffice not installed; one-time install OR PowerPoint COM |
| 14 | Charts | **Both** native editable OOXML charts + styled visuals, per case |
| 15 | Fonts | **Installed locally, don't embed** |
| 16 | Plugin contents | **Bundled scripts + bundled assets**; **no MCP** (skills+scripts suffice) |
| 17 | Custom-slide engine | python-pptx on template clone + pptxgenjs, chosen per slide |
| 18 | Library seed | **Start core, grow deliberately** |
| 19 | Output | **Sensible default** (dated descriptive filename in an output folder), overridable |
| 20 | Creative latitude | **Inventive within guardrails** (palette/type/spacing/master hard-locked) |

---

## 3. Research-derived principles

From a survey of the best published work (sources at bottom):

- **PPTAgent** — represent slides as **composable editing actions**, not full-XML regeneration;
  reference slides carry a **functional type + content schema** (declared slots); evaluate on
  three axes (**Content / Design / Coherence**).
- **academic-pptx-skill** — consultant content discipline: **action titles** (full-sentence
  takeaways), **SCQA** narrative spine, **ghost-deck test** (titles alone tell the story),
  **one exhibit per slide**, **conclusion-anchored ending**.
- **Anthropic `pptx/editing.md`** — token-efficient edit recipe: unpack → **structural changes
  first** (`<p:sldId>`) → edit only isolated `slide{N}.xml` → `clean` → `pack`; subagents edit
  slides in parallel.
- **Presenton / PPT Master** — "follow your own template" is table-stakes; our differentiation is
  sjablon fidelity + SFNL voice + consultant rules + token discipline + precise editing.

---

## 4. Sjablon facts (discovered from `01 SFNL_sjabloon.potx`)

**Authoritative theme palette** (use via `schemeClr`, NEVER hardcode — these differ from the old
skill's wrong hex values):

| Name | Sjablon hex | Theme slot (approx) |
|------|-------------|---------------------|
| Navy | `201B5C` | dk2 / text |
| Dark slate | `233348` | dk1 |
| Orange | `F87F4F` | accent1 |
| Grapefruit | `F95D63` | accent2 |
| Royal | `3B62C1` | accent3 |
| Sky | `45B6E2` | accent4 |
| Emerald | `6AC6BA` | accent5 |
| White | `FFFFFF` / `FEFFFF` | lt1 |

**Layouts:** 30 across 2 masters. Key ones to clone from:
- `Leeg` (blank), `Titel`, `Titel, subtitel`, `1_Titel, subtitel, tekst`
- `Titel, subtitel, twee tekstvakken` (+3 variants) — two-column
- `Quote`
- `1_Titelslide` … `7_Titelslide` — title-slide variants
- `1..12_sectieslide_stijl1` and `1..6_sectieslide_stijl2` — section dividers (two style families)

**Fonts:** theme major/minor resolve to Calibri; **brand fonts (Montserrat / Lato / Gotham) are
applied at placeholder level**. QA must verify *actual* run fonts, not the theme default. Fonts
are installed locally and are **not embedded** in output.

**Build implication:** Build on a clone of the sjablon. Reference colors with `schemeClr`
(accent1 = orange, etc.) so slides auto-track the brand and survive any future palette tweak.
The plugin's `brand.md` / palette index is **generated from the sjablon**, not hand-typed.

---

## 5. Architecture (Approach A — "pipeline plugin")

```
sfnl-pptx/                          (the plugin)
├─ .claude-plugin/plugin.json       manifest
├─ skills/
│  ├─ sfnl-deck/                    GENERATE: brief/outline/source → deck-spec → build → QA
│  │  └─ SKILL.md
│  ├─ sfnl-deck-edit/               EDIT: token-efficient, adaptive-by-edit-type
│  │  └─ SKILL.md
│  └─ sfnl-deck-review/             REVIEW/QA module (callable standalone or by the others)
│     └─ SKILL.md
├─ engine/                          shared, NOT loaded into context unless needed
│  ├─ assets/
│  │  ├─ 01 SFNL_sjabloon.potx      the bundled sjablon (swap point)
│  │  ├─ palette.json               generated from sjablon theme
│  │  └─ components/                tagged component library (grows over time)
│  │     ├─ index.json              tagged index (type, schema, tags, thumb, renderer)
│  │     └─ thumbs/                 small preview images
│  ├─ scripts/
│  │  ├─ office/ (unpack.py, pack.py, clean.py, add_slide.py)  ← from Anthropic recipe
│  │  ├─ build_from_spec.py         deck-spec JSON → .pptx (python-pptx backbone)
│  │  ├─ render.py                  .pptx → slide images (COM or LibreOffice)
│  │  ├─ qa_text.py                 brand/text grep checks
│  │  └─ charts/ (native OOXML chart helpers, styled-shape helpers)
│  └─ reference/
│     ├─ brand.md                   palette + typography + spacing rules (schemeClr-first)
│     └─ voice.md                   consultant + SFNL content rules (NL/EN)
```

**Why three skills, not one:** skills load in isolation, so generating a deck never pulls edit
logic into context (token efficiency). `sfnl-deck-review` is shared so both generate and edit
use the same rubric.

---

## 6. The deck-spec (single source of truth for a deck)

Generation is **spec-first**: one thinking pass produces a compact JSON spec; a cheap
deterministic pass builds it. Editing mutates the spec or the file directly.

```jsonc
{
  "meta": { "title": "...", "lang": "nl|en", "client": "...", "accent": "emerald",
            "output": "<path>.pptx" },
  "narrative": "SCQA one-paragraph spine for the whole deck",
  "slides": [
    {
      "id": "s1",
      "type": "title|section|content-cards|kpi|chart|timeline|quote|comparison|custom",
      "layout": "Titel, subtitel",        // sjablon layout to clone, or "Leeg" for custom
      "renderer": "template|python-pptx|pptxgenjs",
      "action_title": "Full-sentence takeaway (consultant rule)",
      "content_schema_fill": { /* slots defined by the component */ },
      "sensitive": false,                  // true → force visual render in QA
      "notes": "speaker notes / rationale"
    }
  ]
}
```

`content_schema_fill` keys are dictated by the chosen component's declared **content_schema**
(PPTAgent-style) — the model fills slots, it does not free-design standard slides.

---

## 7. `sfnl-deck` (generate) pipeline

1. **Intake** — accept one-line brief, outline/bullets, or source docs. Detect language.
2. **Narrative & outline** — build the SCQA spine; draft **action titles** for every slide;
   run the **ghost-deck test** (titles in sequence must tell the story). One thinking pass.
3. **Layout selection** — for each slide pick a component from `index.json` (tagged search) or,
   when content warrants, design a **custom** slide on `Leeg` within guardrails.
4. **Emit deck-spec** (Section 6).
5. **Build** — `build_from_spec.py`:
   - `template`/`python-pptx` slides: clone the chosen sjablon layout, fill placeholders/shapes,
     colors via `schemeClr`.
   - `pptxgenjs` slides: only when its drawing API is genuinely easier (replicate master once).
   - charts: native OOXML when data may change; styled shapes when precision matters.
6. **QA** — hand off to `sfnl-deck-review` (Section 9).
7. **Deliver** — save to default output path; report what was built and any QA findings.

Content rules enforced natively (`voice.md`): action titles, SCQA, one-exhibit-per-slide,
no trailing periods on short text, CAPS where the brand dictates, conclusion-anchored ending,
anti-AI-writing register, NL/EN consultant tone.

---

## 8. `sfnl-deck-edit` (edit existing) — adaptive by edit type

Always start from the **Anthropic recipe**: `unpack.py` → structural changes first → edit only
the isolated `slide{N}.xml` → `clean.py` → `pack.py`. Subagents handle parallel slide edits.

| Edit type | Strategy |
|-----------|----------|
| Small text / number change | **Targeted XML surgery** — edit specific `<a:t>` runs only |
| Restyle / brand-fix | grep-driven find/replace of fonts/colors → `schemeClr` |
| Replace a whole slide | **Slide-level regenerate** from a component/spec, swap `<p:sldId>` |
| Structural (add/remove/reorder) | Manipulate `<p:sldId>` before any content edit |

Token rule: never read the whole deck. Use `markitdown` for a cheap text map, then read only the
target slide XML.

---

## 9. `sfnl-deck-review` — QA rubric + adaptive rendering

**Rubric (from PPTEval):** score every deck on three axes —
- **Content** — accuracy, action titles present, one message per slide, no placeholder leftovers.
- **Design** — brand compliance (schemeClr, fonts, spacing), no overflow/overlap, alignment.
- **Coherence** — ghost-deck test passes, narrative flows, consistent motif.

**Adaptive rendering (token-aware):**
- **Template-faithful slides** (cloned standard layouts): cheap checks only — `qa_text.py`
  (brand/text grep) + `markitdown` content scan. No render.
- **Custom or `sensitive: true` slides**: **render to images** and have a **fresh-eyes subagent**
  inspect for layout/overflow/brand bugs, then fix-and-reverify loop.

Never declare success without at least one fix-and-verify cycle on rendered slides.

---

## 10. Component library + tagged index

`engine/assets/components/index.json` — one entry per component:

```jsonc
{
  "id": "kpi-trio",
  "name": "Three big-number KPIs",
  "type": "kpi",
  "tags": ["data", "metrics", "3-up", "no-chart"],
  "content_schema": { "kpis": [ { "value": "", "label": "", "delta": "" } ] },  // 3 items
  "renderer": "python-pptx",
  "source_layout": "Leeg",
  "thumb": "thumbs/kpi-trio.png",
  "density": "low"
}
```

Retrieval is a **cheap grep over `index.json`** by `type`/`tags`/`density` (deterministic, fast),
with thumbnails available when visual disambiguation helps. Seeded with the **core structural
set**; grows deliberately. A future "capture this slide as a component" helper can append entries.

**Core set at launch:** title, section divider, agenda/inhoud, content-with-cards, KPI big-number,
simple chart, two-column comparison, quote, closing/contact.

---

## 11. Rendering toolchain (Windows)

Decision: **MS PowerPoint is installed → default to PowerPoint COM** (Windows-native, zero extra
install, truest fidelity). `render.py` drives PowerPoint COM (via PowerShell automation) to export
slide images; LibreOffice remains a documented fallback but is not required. Render is only invoked
for custom/sensitive slides, keeping cost low.

---

## 12. Token-efficiency strategy (summary)

- **Skills load in isolation** — generate never loads edit logic.
- **Spec-first** — think once into a compact JSON, then deterministic build.
- **Components fill slots** — no free-designing standard slides.
- **`schemeClr`-first** — no re-deriving palette per slide.
- **Adaptive QA** — render only what's risky.
- **Edit reads only the target slide**, never the whole deck.
- **Scripts do deterministic heavy lifting** — model writes specs/diffs, not boilerplate XML.

---

## 13. Phasing

- **Phase 1 (MVP):** plugin skeleton + bundled sjablon + `palette.json`/`brand.md`/`voice.md`
  generated from the sjablon + `sfnl-deck` (generate) with the core component set +
  python-pptx-on-template backbone + adaptive QA. Build one real deck end-to-end.
- **Phase 2:** `sfnl-deck-edit` with the full adaptive edit strategies.
- **Phase 3:** extensible library tooling (capture-as-component, richer tagged search),
  pptxgenjs + native-chart renderers, broader non-standard slide catalog.

---

## 14. Out of scope (YAGNI)

- No MCP server (skills + scripts suffice for a single power user).
- No team-distribution hardening yet (build for power use first).
- No font embedding (fonts installed locally).
- No automatic migration/retirement of the old skills (kept installed in parallel).

---

## 15. Resolved settings

1. **Render:** MS PowerPoint installed → default to **PowerPoint COM**.
2. **Output:** default to **`./output/`** in the project, dated descriptive filenames, overridable.
3. **Home & VCS:** plugin built **in this repo** (`Powerpoints design/`); **git initialized**, spec
   committed as the first commit.

*(All Section-13 phases proceed against these settings. The implementation plan targets Phase 1.)*

---

## Sources

- PPTAgent — https://github.com/icip-cas/pptagent
- academic-pptx-skill — https://github.com/Gabberflast/academic-pptx-skill
- Anthropic pptx editing.md — https://github.com/anthropics/skills/blob/main/skills/pptx/editing.md
- Presenton — https://github.com/presenton/presenton
- PPT Master — https://github.com/hugohe3/ppt-master
- SlidesGPT API — https://slidesgpt.com/docs/getting-started/generate-presentation
- python-pptx slides — https://python-pptx.readthedocs.io/en/latest/user/slides.html
- PptxGenJS masters — https://gitbrent.github.io/PptxGenJS/docs/masters.html
