# Deck-spec schema & component catalogue

The deck-spec is the single source of truth for a deck. Author it once, validate it with
`scripts.spec.validate_spec`, then build deterministically with `scripts.build_from_spec`.
This file is the authoritative schema; `scripts/spec.py` is the enforcing implementation.

## Top-level shape

```json
{
  "schema_version": "1.0",
  "meta": { "title": "...", "lang": "nl", "accent": "emerald", "output": "output/demo.pptx" },
  "narrative": "One-paragraph SCQA spine for the whole deck.",
  "slides": [ { "...": "see Slide" } ]
}
```

| Key | Required | Notes |
|-----|----------|-------|
| `meta.title` | **yes** | Deck title; validation fails without it. |
| `meta.lang` | **yes** | `"nl"` or `"en"`. Match the brief's language. |
| `meta.accent` | no | One of `orange`, `grapefruit`, `royal`, `sky`, `emerald`, `navy`. Defaults to `orange` at build time. In single-accent mode (no `accent_map`), this one accent carries the through-line for the whole deck. |
| `meta.accent_map` | no | Opt-in multi-accent mode: `{ "category-name": "accent" }`. Any slide whose `category` matches a key uses that accent instead of `meta.accent`. Decks that omit this stay single-accent. |
| `meta.output` | no | Destination path used when `build_from_spec` is run without an explicit out-path. |
| `narrative` | no (strongly advised) | The SCQA spine. Write it before drafting slides; see `voice.md`. |
| `schema_version` | no | Informational; not enforced. |
| `slides` | **yes** | Non-empty array; see below. |

## Slide shape

```json
{
  "id": "s2",
  "type": "kpi",
  "component_id": "kpi-trio",
  "action_title": "Drie cijfers vatten de impact samen",
  "sensitive": true,
  "visual": {"x": 0.65, "y": 2.15, "card_width": 2.7, "icon_size": 0.5},
  "content_schema_fill": { "...": "shape depends on component_id" }
}
```

| Key | Required | Notes |
|-----|----------|-------|
| `id` | **yes** | Unique across the deck. |
| `action_title` | **yes** | Full-sentence takeaway (consultant rule). Not a label. |
| `component_id` | **yes** | Must exist in the catalogue below. |
| `content_schema_fill` | per component | Must contain every **string-typed** slot of the component's `content_schema`. List/object slots (bullets, cards, kpis, series) are not validation-required but are needed to render meaningful content. |
| `visual` | no | Per-slide visual controls. These override the component's defaults for geometry (`x`, `y`, widths, heights, gaps), icon sizing, progress bars, and variants. Use this whenever the default layout does not fit the slide's content. |
| `type` | no | Informational tag (`title`, `kpi`, `closing`, …); not enforced. |
| `sensitive` | no | Marks a slide for the render pass in `sfnl-deck-review` (custom/risky slides). |
| `category` | no | Free-text category label (e.g. `vraagstuk`, `activiteiten`, `impact`). Looked up against `meta.accent_map` to resolve this slide's accent; ignored if `accent_map` is absent or has no matching key. |

**Validation rule of thumb:** every key whose `content_schema` value is a plain `""` string is
mandatory in `content_schema_fill`. Keys whose value is a list or object (e.g. `body`, `cards`,
`kpis`, `series`, `left`, `right`) are optional to the validator but required for a usable slide.

## Visual-first rule

Default content slides must use a visual component: `content-cards`, `kpi-trio`, `chart-native`,
`chart-static`, `process-timeline`, `schema-grid`, `image-icon-trio`, `matrix-2x2`,
`layer-stack`, `cycle-diagram`, `scenario-cards`, `assessment-table`, `mechanism-diagram`,
`divider-block`, `stat-banner`, `swimlane-columns`, `closing-geometric`, or `custom-freeform`.
Use `content-text` only when the user explicitly asks for a plain text slide, legal/contract
wording requires it, or the slide is a temporary working note. In that case, state the reason in
`notes`.

Every visual component accepts a slide-level `visual` object. Common controls:

| Control | Meaning |
|---------|---------|
| `x`, `y` | top-left position in inches |
| `card_width`, `card_height` | card/KPI panel dimensions |
| `box_width`, `box_height` | schema node dimensions |
| `step_width`, `step_height` | process arrow dimensions |
| `width`, `height` | chart plot area dimensions |
| `gap`, `row_gap` | horizontal/vertical spacing |
| `icon_size` | icon bubble diameter |
| `columns` | schema grid column count |
| `progress`, `progress_label` | optional KPI/status bar |
| `variant` | renderer variant: `icon-top` (default cards), `pastel-tint` (content-cards — light tint card body instead of white), `chevron` (process-timeline — chevron badges instead of arrows) |
| `panel_width`, `panel_side` | divider-block: color panel width in inches and `left`/`right` placement |
| `banner_height` | stat-banner: height of each dark result bar |
| `header_height` | swimlane-columns: height of the colored column header band |

## Multi-accent mode (color-coded categories)

By default a deck is single-accent: every slide uses `meta.accent`. For decks that need the
reference-deck pattern of one accent per conceptual pillar (e.g. problem = coral, activities =
teal, impact = orange, reused consistently across dozens of slides), set `meta.accent_map` and
tag each slide with a matching `category`:

```json
"meta": {
  "title": "...", "lang": "nl", "accent": "orange",
  "accent_map": {"vraagstuk": "grapefruit", "activiteiten": "emerald", "impact": "orange"}
},
"slides": [
  {"id": "s2", "category": "vraagstuk", "component_id": "divider-block", "...": "..."}
]
```

A slide without `category`, or a `category` with no entry in `accent_map`, falls back to
`meta.accent`. Component renderers that accept a per-item `color` override (cards, KPIs,
swimlane columns, ...) still take precedence over the resolved slide accent for that one item.

## Component catalogue

Two renderers exist. `template` clones a branded layout and fills placeholders — leave fonts
empty so they inherit. `python-pptx` draws on the sjabloon's **`Titel, subtitel` layout**, so the
original template frame — white canvas, orange streepje, and title/subtitle placeholders — stays
fully intact; visual components are placed on the white area below (`y` >= ~2.0in). Shapes use
`schemeClr` colors set by the build (Gotham Bold / Lato Light, accent + navy). Every `python-pptx`
component accepts an optional `subtitle` next to its required `title`. Only the full-bleed
components `divider-block` and `closing-geometric` build on the blank `Leeg` layout.

**Titles and subtitles are always rendered ALL CAPS** — the build enforces this (write specs in
normal case; the builder uppercases). Exception: `quote`, whose title slot holds running quote
text. Query the catalogue at runtime with `find_components(type=..., tags=...)`.

| id | renderer | type | Required fill (string slots) | List/object fill |
|----|----------|------|------------------------------|------------------|
| `title-standard` | template | title | `title`, `subtitle` | — |
| `section-divider` | template | section | `title`, `subtitle` | — |
| `content-text` | template | content | `title`, `subtitle` | `body`: list of bullet strings |
| `comparison-two-col` | template | comparison | `title`, `subtitle` | `left`, `right`: lists of bullet strings |
| `quote` | template | quote | `title`, `attribution` | — |
| `closing` | template | closing | `title`, `subtitle` | — |
| `content-cards` | python-pptx | content-cards | `title` | `cards`: up to 3 `{heading, body, icon, color}` |
| `kpi-trio` | python-pptx | kpi | `title` | `kpis`: up to 4 `{value, label, color}` plus optional `visual.progress` |
| `chart-static` | python-pptx | chart | `title` | `series`: list of `{label, value, color}` (value is a number) |
| `chart-native` | python-pptx | chart | `title`, `chart_type` | `categories`, `series`: native **editable** PowerPoint chart (column, stacked-column, bar, stacked-bar, line, area, pie, donut, scatter) |
| `process-timeline` | python-pptx | process | `title` | `steps`: up to 5 `{label, detail, color, icon}` |
| `schema-grid` | python-pptx | schema | `title` | `nodes`: `{heading, body, color, icon}` plus optional `connections` |
| `image-icon-trio` | python-pptx | image-icon-trio | `title` | `items`: up to 3 `{heading, body, icon, image, color}` |
| `matrix-2x2` | python-pptx | matrix | `title`, `x_axis`, `y_axis` | `quadrants`: 4 `{heading, body, color}` |
| `layer-stack` | python-pptx | layer-stack | `title` | `layers`: up to 7 `{label, detail, color}` |
| `cycle-diagram` | python-pptx | cycle | `title`, `center` | `steps`: up to 6 `{label, color, icon}` |
| `scenario-cards` | python-pptx | scenario | `title` | `scenarios`: up to 3 `{heading, subtitle, color, pros, cons}` |
| `assessment-table` | python-pptx | assessment | `title` | `columns`, `rows`: `{criterion, description, score, color}` |
| `mechanism-diagram` | python-pptx | mechanism | `title` | `center`, `nodes`, `flows`: role-and-flow diagram |
| `divider-block` | python-pptx | divider | `title`, `icon` | `subtitle`: full-bleed color panel with a large vector pictogram, alternative to `section-divider` |
| `stat-banner` | python-pptx | stat | `title` | `banners`: up to 3 `{context, value, label}` dark result bars |
| `swimlane-columns` | python-pptx | swimlane | `title` | `columns`: up to 6 `{heading, color, items}` color-coded theory-of-change columns |
| `closing-geometric` | python-pptx | closing | `title` | `subtitle`: full-bleed abstract geometric closer (circle + triangles) |
| `custom-freeform` | python-pptx | freeform | `title` | `primitives`: declarative shape list — the bespoke exhibit builder (see below) |

### Fill shapes by renderer

**Template, single-line slot** — a string becomes the placeholder text:

```json
"content_schema_fill": { "title": "Impact in cijfers", "subtitle": "Social Finance NL" }
```

**Template, bullet slot** — a list becomes one paragraph per item (first item is the first line):

```json
"content_schema_fill": { "title": "Agenda", "subtitle": "Vandaag", "body": ["Probleem", "Aanpak", "Resultaat"] }
```

**`kpi-trio`** — up to four big-number KPI panels, optionally with a progress/status bar:

```json
"content_schema_fill": { "title": "Impact in cijfers",
  "kpis": [ {"value": "3,2x", "label": "SROI", "color": "emerald"} ] },
"visual": {"x": 0.65, "card_width": 2.7, "progress": 0.36, "progress_label": "36% terugontvangen"}
```

**`content-cards`** — up to three icon cards:

```json
"content_schema_fill": { "title": "Drie sporen",
  "cards": [ {"heading": "Spoor 1", "body": "Korte toelichting", "icon": "check", "color": "sky"} ] },
"visual": {"x": 1.1, "card_width": 2.8, "icon_size": 0.48}
```

**`chart-static`** — bars with grid and labels, scaled to the largest value:

```json
"content_schema_fill": { "title": "Kosten per jaar",
  "series": [ {"label": "2023", "value": 100}, {"label": "2024", "value": 82} ] }
```

**`chart-native`** — a real, editable PowerPoint chart, theme-colored via `schemeClr`. The
client can change the numbers afterwards in PowerPoint; prefer this over `chart-static` for any
serious data exhibit. `chart_type` is one of `column`, `stacked-column`, `bar`, `stacked-bar`,
`line`, `area`, `pie`, `donut`, `scatter`:

```json
"content_schema_fill": { "title": "Kosten en baten per jaar", "chart_type": "column",
  "categories": ["2023", "2024", "2025"],
  "series": [ {"name": "Kosten", "values": [100, 82, 71], "color": "navy"},
              {"name": "Baten", "values": [40, 65, 90], "color": "emerald"} ] },
"visual": {"x": 0.95, "y": 1.95, "width": 11.4, "height": 4.6,
           "data_labels": true, "number_format": "#.##0", "legend": true}
```

Notes: pie/donut take one series and color per slice via optional `slice_colors` (list of
accents); `scatter` series use `x_values`/`y_values` instead of `categories`/`values`; `legend`
defaults to on for multi-series and pie/donut; `data_labels` and `number_format` are optional.
Fonts on axes, legend, and labels are set to the brand set by the build.

**`process-timeline`** — colored process arrows:

```json
"content_schema_fill": { "title": "Onze aanpak",
  "steps": [ {"label": "1. Ontwikkelen", "detail": "Verandertheorie", "color": "orange", "icon": "1"} ] },
"visual": {"x": 0.85, "step_width": 2.45, "gap": 0.22}
```

**`schema-grid`** — boxed schema/organogram with optional connectors:

```json
"content_schema_fill": { "title": "Organisatie",
  "nodes": [ {"heading": "Team HR", "body": "People en ontwikkeling", "color": "sky", "icon": "people"} ],
  "connections": [ {"from": 0, "to": 1} ] },
"visual": {"columns": 4, "box_width": 2.25, "box_height": 1.2}
```

**`matrix-2x2`** — decision matrix with two axes:

```json
"content_schema_fill": { "title": "Impact versus risico", "x_axis": "Risico", "y_axis": "Effect",
  "quadrants": [ {"heading": "Strategisch", "body": "Bouwen", "color": "emerald"} ] },
"visual": {"x": 0.95, "y": 1.95, "width": 6.8, "height": 4.2}
```

**`layer-stack`** — indented evidence or maturity stack:

```json
"content_schema_fill": { "title": "Evidence-lagen",
  "layers": [ {"label": "Niveau 5", "detail": "Strategische beslissing", "color": "navy"} ] },
"visual": {"width": 8.8, "layer_height": 0.58, "indent": 0.36}
```

**`cycle-diagram`** — continuous loop with a center label:

```json
"content_schema_fill": { "title": "Continu verbeteren", "center": "Continu",
  "steps": [ {"label": "Plannen", "color": "orange", "icon": "1"} ] },
"visual": {"center_x": 6.65, "center_y": 3.9, "radius": 1.65, "node_size": 0.92}
```

**`scenario-cards`** — three option cards with pros and watchouts:

```json
"content_schema_fill": { "title": "Drie scenario's",
  "scenarios": [ {"heading": "Scenario A", "subtitle": "Status quo", "color": "sky",
    "pros": ["Bekende werkwijze"], "cons": ["Risico op stilstand"]} ] },
"visual": {"card_width": 3.55, "card_height": 4.25}
```

**`assessment-table`** — criteria, description, and score table:

```json
"content_schema_fill": { "title": "Afwegingskader", "columns": ["Criterium", "Toelichting", "Score"],
  "rows": [ {"criterion": "Draagvlak", "description": "Steun bij partners", "score": "Middel", "color": "orange"} ] },
"visual": {"width": 10.9, "row_height": 0.62}
```

**`mechanism-diagram`** — central budget/mechanism with role nodes and labeled flows:

```json
"content_schema_fill": { "title": "Mechaniek",
  "center": {"heading": "Maatwerkbudget", "body": "beheerd door uitvoerder", "color": "orange"},
  "nodes": [ {"heading": "Financier", "body": "fonds of gemeente", "color": "royal", "icon": "money"} ],
  "flows": [ {"from": "center", "to": 0, "label": "Budget"} ] },
"visual": {"center_x": 6.4, "center_y": 3.75, "radius_x": 3.6, "radius_y": 1.75}
```

**`divider-block`** — full-bleed color panel with a large vector icon, text on the other half:

```json
"content_schema_fill": { "title": "Het vraagstuk", "subtitle": "Waarom dit ertoe doet", "icon": "target" },
"category": "vraagstuk",
"visual": {"panel_width": 5.3, "panel_side": "left"}
```

Icon names come from the native vector icon library (`engine/scripts/icons.py`, no raster/SVG
assets): `target`, `people`, `growth`, `idea`, `house`, `book`, `calendar`, `compass`,
`partnership`, `check`, `flag`, `scale`, `money`, `clock`, `gear`.

**`stat-banner`** — dark result bars with a bold accent-colored number, the reference deck's
"formula bar" pattern for calculation/impact slides:

```json
"content_schema_fill": { "title": "Financiele impact",
  "banners": [ {"context": "Besparing per deelnemer per jaar", "value": "€593", "label": "netto voordeel"} ] },
"visual": {"width": 11.6, "banner_height": 1.15}
```

**`swimlane-columns`** — colored-header columns with dense bullet rows (theory-of-change canvas):

```json
"content_schema_fill": { "title": "Verandertheorie",
  "columns": [ {"heading": "Vraagstuk", "color": "grapefruit", "items": ["Eenzaamheid", "Isolatie"]} ] },
"visual": {"header_height": 0.52}
```

**`closing-geometric`** — full-bleed accent panel with an abstract circle+triangle motif:

```json
"content_schema_fill": { "title": "Dank u wel", "subtitle": "Social Finance NL" }
```

**`custom-freeform`** — the bespoke exhibit builder. Use it whenever the slide's message has a
shape no named component matches: funnels, geldstromen, stakeholderkaarten, parallelle
tijdlijnen, one-off diagrams. Choosing bespoke is a design decision, not a fallback. Every
primitive still resolves through `schemeClr` accents and the three allowed fonts — this bypasses
the fixed catalogue, not the brand rules, and everything stays editable in PowerPoint:

```json
"content_schema_fill": { "title": "Geldstroom in één beeld",
  "primitives": [
    {"type": "chevron", "x": 0.9, "y": 2.0, "w": 2.2, "h": 0.9, "fill": "emerald", "text": "Fase 1"},
    {"type": "arrow", "direction": "right", "x": 3.3, "y": 2.0, "w": 1.0, "h": 0.9, "fill": "sky"},
    {"type": "hexagon", "x": 4.6, "y": 1.85, "w": 1.3, "h": 1.2, "fill": "orange", "text": "Hub"},
    {"type": "connector", "style": "elbow", "arrow": "both", "x1": 6.0, "y1": 2.4, "x2": 8.0, "y2": 3.6, "color": "navy"},
    {"type": "textbox", "x": 0.9, "y": 3.4, "w": 4.0, "h": 1.4, "bullets": ["Punt een", "Punt twee"], "size": 12},
    {"type": "table", "x": 5.4, "y": 4.4, "w": 6.5, "header": true, "first_col_bold": true,
     "rows": [["Criterium", "Score"], ["Draagvlak", "Hoog"]]},
    {"type": "icon", "x": 11.0, "y": 2.0, "w": 1.2, "icon": "money", "color": "orange"},
    {"type": "group", "x": 0.9, "y": 5.2, "w": 3.0, "primitives": [
       {"type": "oval", "x": 0.9, "y": 5.2, "w": 0.8, "h": 0.8, "fill": "emerald"},
       {"type": "rect", "x": 1.9, "y": 5.4, "w": 1.6, "h": 0.4, "fill": "sky"} ]}
  ]
}
```

Primitive types:

| type | needs | optional |
|------|-------|----------|
| `rect`, `rounded-rect`, `oval`, `triangle`, `diamond`, `pentagon`, `hexagon`, `chevron`, `donut`, `pie` | `x`, `y`, `w`, `h` | `fill`, `line`, `rotation`, `text` (centered white Gotham Bold label; tune with `font`, `size`, `bold`, `text_color`) |
| `arrow` | `x`, `y`, `w`, `h` | `direction` (`right`/`left`/`up`/`down`), `fill`, `rotation`, `text` |
| `line` | `x1`, `y1`, `x2`, `y2` | `color`, `width_pt` |
| `connector` | `x1`, `y1`, `x2`, `y2` | `style` (`straight`/`elbow`), `arrow` (`none`/`end`/`both`, default `end`), `color`, `width_pt` |
| `textbox` | `x`, `y`, `w`, `h`, and `text` or `bullets` (list) | `font`, `size`, `color`, `bold`, `align`, `anchor` |
| `icon` | `x`, `y`, `w`, `icon` (vector library name) | `color`, `bg` |
| `table` | `x`, `y`, `w`, `rows` (list of equal-length lists) | `header` (default true: navy header row), `col_widths`, `row_height`, `size`, `header_size`, `first_col_bold`, `color` |
| `image` | `x`, `y`, `w`, `path` | `h` |
| `group` | `x`, `y`, `w`, `primitives` (child list, absolute inches) | nesting max 2 levels |

`validate_spec` rejects unknown primitive types, non-brand colors/fonts, unknown icon names,
ragged table rows, and over-deep groups before the deck ever builds.

## Minimal valid deck

```json
{
  "meta": {"title": "SFNL demo", "lang": "nl", "accent": "emerald", "output": "output/demo.pptx"},
  "narrative": "Situatie-Complicatie-Vraag-Antwoord spine voor de demo.",
  "slides": [
    {"id": "s1", "component_id": "title-standard",
     "action_title": "SFNL maakt maatschappelijke waarde meetbaar",
     "content_schema_fill": {"title": "Maatschappelijke waarde, meetbaar gemaakt", "subtitle": "Social Finance NL"}},
    {"id": "s2", "component_id": "kpi-trio", "sensitive": true,
     "action_title": "Drie cijfers vatten de impact samen",
     "content_schema_fill": {"title": "Impact in cijfers",
       "kpis": [{"value": "3,2x", "label": "SROI"}, {"value": "€1,4M", "label": "Vermeden kosten"}, {"value": "87%", "label": "Doelgroep bereikt"}]}},
    {"id": "s3", "component_id": "closing",
     "action_title": "Samen bouwen we aan duurzame financiering",
     "content_schema_fill": {"title": "Dank", "subtitle": "Social Finance NL"}}
  ]
}
```
