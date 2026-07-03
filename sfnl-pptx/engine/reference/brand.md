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

- **Lato Light is the default slide voice** for content slides. Body copy normally uses 16pt;
  use 18pt for sparse explanatory slides and 14pt only for dense matrices or labels.
- **Gotham Bold is display-only**: official archetype slots, big numbers, and short emphasis.
  Do not use Gotham Bold as the default content-slide title/body style.
- **Montserrat Light is secondary**: labels, metadata, small section markers.
- Titles and subtitles remain ALL CAPS across content slides and official archetypes because
  this is a company requirement. Content-slide action titles may use Lato Light or Montserrat
  Light; they still need hierarchy, whitespace, and readable line lengths.

Fonts zijn lokaal geïnstalleerd, nooit embedded. Fallback-stacks in `sfnl.css` zijn alleen
vangnet voor rendering. QA wijst andere fonts af.

## Chrome (vast op elke contentslide)

Titelblok linksboven (Lato Light of Montserrat Light, navy, ALL CAPS, met duidelijke hiërarchie)
met een kleine oranje dash als brand marker; SFNL-logo linksonder en oranje paginanummer
rechtsonder (native geïnjecteerd door `build_deck.js`).
Titelslides, sectiedividers en quotes gebruiken de officiële sjabloonontwerpen — de archetypes
`cover-*`/`divider-*`/`quote-*` in `engine/web/archetypes/` (gegenereerd uit
`engine/assets/sfnl-slides.pptx`); nooit zelf ontwerpen. Het bewaarde
`engine/assets/sfnl-template.pptx` dient alleen nog als visuele referentie voor
chrome-getrouwheid.

## Compositie

- 16:9, canvas 720×405pt. Eén exhibit per slide.
- **Volledige hoogte**: content vult het canvas; half-lege slides zijn een defect.
- Royale, gelijke marges (26pt zijkanten). Big-numbers-patroon voor KPI's.
- Iconen zijn inhoud, geen decoratie: gerasterde react-icons in merkkleur (`build/raster.js`).

**Editorial kadergrid:** content slides should be framed by visible structure: colored sidebars,
top/bottom bands, evidence boxes, full-width matrices, or verdict panels. The orange dash is a
minor brand marker, not the main composition. Avoid pale floating card rows unless the cards form
a full exhibit.
