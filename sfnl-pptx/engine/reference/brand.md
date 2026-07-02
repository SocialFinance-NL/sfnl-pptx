# SFNL Brand Reference (hex tokens + design rules)

> Bron: `engine/assets/palette.json` (gegenereerd uit de sjabloon-theme). CSS-tokens en de
> toegestane hex-set worden daarvan afgeleid door `engine/web/build/generate_tokens.js`
> (`engine/web/sfnl.css`, `engine/web/tokens.json`).

## Palette

| Naam | Hex | CSS-token |
|------|-----|-----------|
| Navy | #201B5C | `--sfnl-navy` |
| Dark slate | #233348 | `--sfnl-dark-slate` |
| Orange | #F87F4F | `--sfnl-orange` |
| Grapefruit | #F95D63 | `--sfnl-grapefruit` |
| Royal | #3B62C1 | `--sfnl-royal` |
| Sky | #45B6E2 | `--sfnl-sky` |
| Emerald | #6AC6BA | `--sfnl-emerald` |
| White | #FEFFFF | `--sfnl-white` |

**Accentregel:** één accent per deck (`deck.json.accent`, default orange) draagt de rode draad;
kleur codeert betekenis. Meerdere accenten alleen wanneer categorieën over veel slides terugkeren
(één vaste kleur per categorie, overal consequent).

**Tinten en schaduwen:** per kleur precomputed (`-tint80/-tint60/-tint40/-shade25`, plus greys
uit dark slate: `--sfnl-grey-95/-85/-70`) — dezelfde luminantie-wiskunde als PowerPoints
lumMod/lumOff, deterministisch. Gebruik tinten voor pastel-kaarten, shades voor donkere banden.
Geen andere hex introduceren: `qa_text` markeert alles buiten `tokens.json` als off-brand.

## Typografie

- **Alleen drie fonts:** Gotham Bold (display/koppen), Lato Light (body/labels), Montserrat
  Light (secundair/rustig). QA wijst andere fonts af.
- **Titels en subtitels altijd in ALL CAPS — in de HTML getypt** (CSS `text-transform` overleeft
  de conversie niet). Uitzondering: quote-slides, waar de kop lopende citaattekst draagt.
- Fonts zijn lokaal geïnstalleerd, nooit embedded. Fallback-stacks in `sfnl.css` zijn alleen
  vangnet voor rendering.

## Chrome (vast op elke contentslide)

Titelblok linksboven (Gotham Bold 18pt navy, ALL CAPS) met oranje dash eronder; SFNL-logo
linksonder en oranje paginanummer rechtsonder (native geïnjecteerd door `build_deck.js`).
Full-bleed archetypes (cover, divider, closing) hebben eigen chrome-regels — zie
`engine/web/archetypes/`. Het bewaarde `engine/assets/sfnl-template.pptx` dient alleen nog als
visuele referentie voor chrome-getrouwheid.

## Compositie

- 16:9, canvas 720×405pt. Eén exhibit per slide.
- **Volledige hoogte**: content vult het canvas; half-lege slides zijn een defect.
- Royale, gelijke marges (26pt zijkanten). Big-numbers-patroon voor KPI's.
- Iconen zijn inhoud, geen decoratie: gerasterde react-icons in merkkleur (`build/raster.js`).
