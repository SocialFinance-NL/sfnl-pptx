---
name: sfnl-deck-design
description: Work out the visual layout of every slide in an SFNL deck before writing the deck-spec JSON. Use after the narrative and action titles are drafted and before authoring deck-spec.json — produces a per-slide storyboard (component, color category, icon, variant, rationale) that gets reviewed and adjusted cheaply as text before any building happens. Triggers on "werk de layout per slide uit", "storyboard", "design plan", or as step 3 of the sfnl-deck pipeline.
---

# sfnl-deck-design: plan the layout before you build it

Deciding a slide's visual treatment while writing deck-spec JSON means design mistakes are only
caught after a build+render cycle. This skill front-loads that decision into a plain-text
storyboard that is cheap to review and revise, so the JSON authoring step becomes a mechanical
translation, not a design exercise.

## When this runs

Between **narrative and titles** (SCQA spine + action titles drafted, per `voice.md`) and
**emit deck-spec** in the `sfnl-deck` pipeline. Never skip straight from action titles to JSON.

## Step 1: Decide the color model for this deck

- **Single-accent** (default): one `meta.accent` carries the whole deck's through-line. Right for
  short pitch decks, single-topic updates, decks with no recurring cross-slide categories.
- **Multi-accent** (`meta.accent_map`): one accent per recurring conceptual pillar (e.g.
  vraagstuk/activiteiten/outcomes/impact), reused across many slides — the reference-deck pattern.
  Choose this once the deck has 3+ categories that each recur across multiple slides (a
  theory-of-change deck, a multi-workstream program update). Forcing multi-accent onto a short
  deck just adds noise; forcing single-accent onto a long categorical deck flattens the structure
  the reader needs. Name every category up front and assign it a fixed accent — never let the
  same category take different colors on different slides.

## Step 2: Build the storyboard

For every slide, in order, decide and record:

| Field | What to decide |
|---|---|
| `id` | matches the eventual deck-spec slide id |
| `action_title` | already drafted; carry it over verbatim |
| `category` | (multi-accent decks only) which pillar this slide belongs to, or "-" |
| `component_id` | the single visual component from the full catalogue (`engine/reference/deck-spec.md`) that best carries this slide's message |
| `icon` | icon name(s) from `engine/scripts/icons.py`'s vector library, chosen for meaning, not decoration |
| `variant` | any `visual.variant` choice (`pastel-tint`, `chevron`, `panel_side`, ...) or "-" |
| `rationale` | one line: why this component over the alternatives |

Write this as a markdown table before touching JSON. Query the catalogue with
`find_components(type=..., tags=...)` when unsure what fits; do not default to the same 2-3
components out of habit — the catalogue now includes full-bleed dividers (`divider-block`), dark
stat banners (`stat-banner`), color-coded swimlane canvases (`swimlane-columns`), and an abstract
geometric closer (`closing-geometric`) precisely to break the all-cards, all-white-background
sameness a small catalogue produces.

Two tools deserve deliberate attention in every storyboard:

- **`chart-native`** for real data. When the bronnendossier marks rows as viz-kandidaat `chart`,
  prefer an editable native chart (column, stacked-column, bar, stacked-bar, line, area, pie,
  donut, scatter) over `chart-static` — the client can edit the numbers afterwards and the
  colors track the theme. Use `chart-static` only for stylized single-series bars where the
  decorative grid look is the point.
- **`custom-freeform` (bespoke exhibit)** when the slide's message has a shape no named
  component matches — a funnel, a geldstroom-diagram, a stakeholderkaart, a timeline met
  parallelle sporen. The primitive set (shapes incl. chevron/diamond/hexagon/donut/pie, arrows,
  connectors with arrowheads, tables, icons, bullet textboxes, groups) composes consultancy-
  grade one-off diagrams while staying on-brand and editable. Choosing bespoke is a design
  decision, not a failure: record in `rationale` why the bespoke shape carries the message
  better than the nearest named component. Sketch the composition (elements + positions in
  inches) in the storyboard row so the JSON step stays mechanical. Only when the same bespoke
  pattern recurs across decks does it signal a missing named component (a future engine change).

## Step 3: Self-review the storyboard

Before moving to JSON, check the whole table at once:

- No two adjacent slides share the same `component_id` unless the content is genuinely a direct
  continuation (e.g. two consecutive KPI slides in a results section).
- Every category (multi-accent decks) maps to exactly one accent everywhere it appears.
- Every divider/section-break slide has a distinct icon from every other divider in the deck.
- Every content slide has a real visual component; a `content-text` row must carry a `rationale`
  that justifies the exception (matches the deck-spec.md visual-first rule).
- Every `custom-freeform` row has a sketched composition and a rationale naming the rejected
  nearest named component. Bespoke exhibits are welcome where the message demands them; five
  near-identical bespoke slides in one deck is the signal that a named component is missing.
- Every dossier-row marked viz-kandidaat `chart` or `kpi` actually appears as a `chart-native`,
  `chart-static`, `kpi-trio`, or `stat-banner` slide — numbers that stay buried in body text
  are a missed exhibit.
- Scan for monotony: if 5+ consecutive content slides all use `content-cards`, vary component
  choice or introduce a `divider-block`/`stat-banner` beat to break the rhythm, matching how the
  reference deck alternates cards, swimlanes, chevron process diagrams, and stat banners rather
  than repeating one shape.

Fix the storyboard, not the JSON, when something is wrong here — it is far cheaper to edit a
table row than to rebuild and re-render a slide.

## Step 4: Translate to deck-spec.json

Once the storyboard is confirmed, each row becomes one deck-spec slide entry: `category` becomes
the slide's `category` field, `component_id`/`icon`/`variant` become `component_id` and the
`visual`/`content_schema_fill` values, per the schema in `engine/reference/deck-spec.md`. This
step should require no new design judgment — if it does, the storyboard was incomplete; go back
to Step 2 for that slide.

## Handoff

After deck-spec.json is built (`sfnl-deck`'s step 5), hand off to `sfnl-deck-review`. The
storyboard from this skill is also the fastest way to explain *why* a slide looks the way it does
during that review — keep it alongside the spec, not just in scratch memory.
