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
| `meta.accent` | no | One of `orange`, `grapefruit`, `royal`, `sky`, `emerald`, `navy`. Defaults to `orange` at build time. One accent per deck carries the through-line. |
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
  "content_schema_fill": { "...": "shape depends on component_id" }
}
```

| Key | Required | Notes |
|-----|----------|-------|
| `id` | **yes** | Unique across the deck. |
| `action_title` | **yes** | Full-sentence takeaway (consultant rule). Not a label. |
| `component_id` | **yes** | Must exist in the catalogue below. |
| `content_schema_fill` | per component | Must contain every **string-typed** slot of the component's `content_schema`. List/object slots (bullets, cards, kpis, series) are not validation-required but are needed to render meaningful content. |
| `type` | no | Informational tag (`title`, `kpi`, `closing`, …); not enforced. |
| `sensitive` | no | Marks a slide for the render pass in `sfnl-deck-review` (custom/risky slides). |

**Validation rule of thumb:** every key whose `content_schema` value is a plain `""` string is
mandatory in `content_schema_fill`. Keys whose value is a list or object (e.g. `body`, `cards`,
`kpis`, `series`, `left`, `right`) are optional to the validator but required for a usable slide.

## Component catalogue

Two renderers exist. `template` clones a branded layout and fills placeholders — leave fonts
empty so they inherit. `python-pptx` draws on the blank `Leeg` layout with `schemeClr` colors set
by the build (Gotham Bold / Lato Light, accent + navy). Query at runtime with
`find_components(type=..., tags=...)`.

| id | renderer | type | Required fill (string slots) | List/object fill |
|----|----------|------|------------------------------|------------------|
| `title-standard` | template | title | `title`, `subtitle` | — |
| `section-divider` | template | section | `title`, `subtitle` | — |
| `content-text` | template | content | `title`, `subtitle` | `body`: list of bullet strings |
| `comparison-two-col` | template | comparison | `title`, `subtitle` | `left`, `right`: lists of bullet strings |
| `quote` | template | quote | `title`, `attribution` | — |
| `closing` | template | closing | `title`, `subtitle` | — |
| `content-cards` | python-pptx | content-cards | `title` | `cards`: up to 3 `{heading, body}` |
| `kpi-trio` | python-pptx | kpi | `title` | `kpis`: up to 3 `{value, label}` |
| `chart-static` | python-pptx | chart | `title` | `series`: list of `{label, value}` (value is a number) |

### Fill shapes by renderer

**Template, single-line slot** — a string becomes the placeholder text:

```json
"content_schema_fill": { "title": "Impact in cijfers", "subtitle": "Social Finance NL" }
```

**Template, bullet slot** — a list becomes one paragraph per item (first item is the first line):

```json
"content_schema_fill": { "title": "Agenda", "subtitle": "Vandaag", "body": ["Probleem", "Aanpak", "Resultaat"] }
```

**`kpi-trio`** — up to three big-number KPIs, centered:

```json
"content_schema_fill": { "title": "Impact in cijfers",
  "kpis": [ {"value": "3,2x", "label": "SROI"}, {"value": "€1,4M", "label": "Vermeden kosten"} ] }
```

**`content-cards`** — up to three cards:

```json
"content_schema_fill": { "title": "Drie sporen",
  "cards": [ {"heading": "Spoor 1", "body": "Korte toelichting"} ] }
```

**`chart-static`** — bars scaled to the largest value:

```json
"content_schema_fill": { "title": "Kosten per jaar",
  "series": [ {"label": "2023", "value": 100}, {"label": "2024", "value": 82} ] }
```

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
