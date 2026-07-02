---
name: sfnl-deck-design
description: Work out the visual layout of every slide in an SFNL deck before writing any HTML. Use after the narrative and action titles are drafted and before authoring slides/*.html — produces a per-slide storyboard (composition, regions, pattern/archetype, accent use, chart candidates, rationale) that gets reviewed and adjusted cheaply as text before any building happens. Triggers on "werk de layout per slide uit", "storyboard", "design plan", or as step 4 of the sfnl-deck pipeline.
---

# sfnl-deck-design: componeer de slide vóór je haar bouwt

HTML schrijven zonder plan betekent designfouten ontdekken na een build+render-cyclus. Dit
skill front-loadt de compositiebeslissing in een tekst-storyboard. Denk in **layoutcompositie**
— regio's, hiërarchie, vulling van het canvas — niet in catalogus-componenten.

## Wanneer

Tussen narrative/titels en het schrijven van `slides/*.html`. Nooit rechtstreeks van titels
naar HTML. Lees eerst `engine/web/patterns.md` en bekijk `engine/web/archetypes/`.

## Stap 1: kleurmodel

- **Single-accent** (default): één `deck.json.accent` draagt de rode draad van de hele deck.
- **Multi-accent**: alleen bij 3+ terugkerende categorieën over veel slides (één vaste kleur
  per categorie, overal consequent; leg de mapping vast in het storyboard). Multi-accent op een
  korte deck voegt alleen ruis toe; single-accent op een lange categorische deck vlakt de
  structuur af die de lezer nodig heeft.

## Stap 2: storyboard per slide

| Veld | Beslissing |
|---|---|
| `file` | wordt de bestandsnaam `slides/NN-….html` |
| `action_title` | verbatim uit de narrative-stap |
| `archetype/patroon` | archetype (cover/divider/quote/closing/stat-banner) of patroon uit `patterns.md`, of "bespoke" |
| `compositie` | regio-indeling in woorden: kolommen/rijen, wat waar, verhouding (bv. "links 2/5 tekst, rechts 3/5 chart-placeholder") |
| `accent` | waar het accent valt (één plek per slide die de boodschap draagt) |
| `chart` | dossier-viz-kandidaat → charttype (column/stackedColumn/bar/line/area/pie/donut/scatter): wordt een chartspec in deck.json |
| `iconen/assets` | welke gerasterde iconen of pre-rendered PNGs nodig zijn |
| `chrome` | light / dark / none |
| `rationale` | één regel: waarom deze compositie de boodschap draagt |

Schrijf dit als markdown-tabel vóór er HTML bestaat. Bespoke composities (funnel,
geldstroom-diagram, stakeholderkaart, parallelle tijdlijnen) zijn welkom: schets regio's en
elementen in het storyboard zodat de HTML-stap mechanisch wordt. Complexe native elementen
(tabellen e.d.) kunnen via de per-deck hook — noteer dat expliciet.

## Stap 3: self-review van het hele storyboard

- Vult elke contentslide het canvas? Een slide die "een kaartje linksboven" is, is een defect.
- Geen twee aangrenzende slides met identieke compositie, tenzij bewust ritme (bv. KPI-reeks).
- Elke dossier-viz-kandidaat (`chart`/`kpi`) landt als native chart, big-number of stat-banner —
  cijfers die in bodytekst blijven hangen zijn een gemiste exhibit.
- Multi-accent: elke categorie overal dezelfde kleur; dividers onderling verschillend.
- Ritme over de hele deck: wissel kaarten, banners, charts, dividers — monotonie is een defect.

Fix het storyboard, niet de HTML, als hier iets mis is — een tabelrij aanpassen is veel
goedkoper dan een slide rebuilden en re-renderen.

## Stap 4: vertaal naar HTML + deck.json

Elke storyboard-rij wordt één HTML-bestand + één `deck.json`-entry, per
`engine/reference/authoring-guide.md`. Vereist deze stap nieuw designoordeel, dan was het
storyboard onvolledig: terug naar stap 2 voor die slide.

## Handoff

Na het bouwen: `sfnl-deck-review`. Bewaar het storyboard naast de workspace — het is de snelste
uitleg waarom een slide eruitziet zoals ze eruitziet.
