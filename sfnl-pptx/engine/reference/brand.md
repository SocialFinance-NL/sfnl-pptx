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

## Typography

- **Only three fonts are allowed:** Gotham Bold (display/headings), Lato Light (body/labels),
  Montserrat Light (secondary/quiet). The build sets no other font on a run; QA rejects others.
- Template-faithful slides leave runs empty and inherit fonts from the branded layouts — do not
  override them. Set fonts explicitly only on custom (`Leeg`-based) slides.
- Theme major/minor resolve to Calibri Light / Calibri — never use these for brand text; clone
  branded layouts instead.
- Fonts are installed locally, never embedded.

## Spacing & layout

- 16:9, 13.33in × 7.5in.
- One exhibit per slide. Generous margins; do not crowd the master's safe area.
- Big-number pattern for KPIs: large numeral, small label beneath.
