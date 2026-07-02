# SFNL Brand Reference (generated palette + design rules)

> Palette is generated from the sjabloon theme1.xml — see `engine/assets/palette.json`.
> Always color via `schemeClr` (the build does this); never hardcode hex.

## Palette (theme slots)

| Name | Hex | schemeClr slot |
|------|-----|----------------|
| Navy | 201B5C | dk2 / accent6 / folHlink |
| Dark slate | 233348 | dk1 |
| Orange | F87F4F | accent1 |
| Grapefruit | F95D63 | accent2 |
| Royal | 3B62C1 | accent3 / hlink |
| Sky | 45B6E2 | accent4 |
| Emerald | 6AC6BA | accent5 |
| White | FEFFFF / FFFFFF | lt1 / lt2 |

**Accent rule:** one accent encodes one meaning per deck (`meta.accent`). Orange is the
default action/highlight color; emerald/sky/royal for categorical series.

**Multi-accent mode:** decks that need a reference-deck-style color-coded canvas (one accent per
pillar/column, e.g. problem = grapefruit, activities = emerald, impact = orange, reused
consistently across dozens of slides) can opt into `meta.accent_map` + per-slide `category` — see
`deck-spec.md`. This is additive: decks that never set `accent_map` stay single-accent.

**Tints and shades:** `scripts.colors.set_scheme_fill_tint`/`set_scheme_fill_shade` derive pastel
card backgrounds and dark banner/header bands from a theme accent via `lumMod`/`lumOff` — still
zero hardcoded hex, just a lighter/darker reading of the same `schemeClr` slot. Used by the
`pastel-tint` card variant, `swimlane-columns` column bodies, and `closing-geometric`.

**Icons:** `scripts/icons.py` draws vector pictograms from native pptx autoshapes (no raster/SVG
assets): `target`, `people`, `growth`, `idea`, `house`, `book`, `calendar`, `compass`,
`partnership`, `check`, `flag`, `scale`, `money`, `clock`, `gear`. Use these at large scale
(1.5in+) on `divider-block` and `custom-freeform`; the older text-glyph icons in
`build_from_spec.ICON_GLYPHS` remain for small icon bubbles inside cards/nodes/steps.

## Typography

- **Only three fonts are allowed:** Gotham Bold (display/headings), Lato Light (body/labels),
  Montserrat Light (secondary/quiet). The build sets no other font on a run; QA rejects others.
- **Titels en subtitels staan altijd in ALL CAPS.** De build dwingt dit af (`_caps` in
  `build_from_spec.py`) op template- én custom slides; QA meldt afwijkingen als critical.
  Uitzondering: de `quote`-component, waar de titelplaceholder lopende citaattekst bevat.
- Template-faithful slides leave runs empty and inherit fonts from the branded layouts — do not
  override them. Set fonts explicitly only on custom slides (drawn on the sjabloon's
  `Titel, subtitel` layout).
- Theme major/minor resolve to Calibri Light / Calibri — never 