---
name: sfnl-deck-design
description: Work out the visual layout of every slide in an SFNL deck before writing any HTML. Use after the outline (sfnl-deck-outline) is approved and before authoring slides/*.html — produces a per-slide storyboard (composition, regions, pattern/archetype, accent use, chart candidates, rationale) that gets reviewed and adjusted cheaply as text before any building happens. Triggers on "werk de layout per slide uit", "storyboard", "design plan", or as step 4 of the sfnl-deck pipeline.
---

# sfnl-deck-design: componeer de slide vóór je haar bouwt

HTML schrijven zonder plan betekent designfouten ontdekken na een build+render-cyclus. Dit
skill front-loadt de compositiebeslissing in een tekst-storyboard. Denk in **layoutcompositie**
— regio's, hiërarchie, vulling van het canvas — niet in catalogus-componenten.

## Wanneer

Tussen de goedgekeurde outline (`sfnl-deck-outline`, `output/<YYYY-MM-DD>-<slug>/outline.md`)
en het schrijven van `slides/*.html`. Nooit rechtstreeks van outline naar HTML. Lees eerst
`engine/web/patterns.md` en bekijk `engine/web/archetypes/`.

Als de outline een **reference file / referentiebestand** bevat, inspecteer het bestand of de
samenvatting voordat je het storyboard schrijft. Extraheer alleen herbruikbare structuur- en
stijlcue's (bijv. sectieritme, type exhibit, dichtheid, navigatie, volgorde). Benoem in het
storyboard hoe elke relevante cue wordt toegepast of bewust verworpen omdat SFNL brandregels,
het editorial kadergrid of officiële archetype-slots voorgaan.

Het editorial kadergrid is de structurele keuze (sidebar, banded exhibit, evidence stack, …); de
**exhibit-grammatica** uit `patterns.md` is de vormentaal die dat kader vult. Voor elke slide die
een tabel, diagram of statcompositie nodig heeft: kies een patroonnaam (`sfnl-table {orange|
royal|teal|navy}`, `flow-tree`, `veranderttheorie-map`, `effectenkaart`, `chevron-process`,
`stat-cards`, `stakeholder-ladder`, `icon-tiles`) en **bekijk (Read) het bijpassende exhibit** uit
`engine/reference/exhibits/manifest.md` voordat je de compositie van die slide vastlegt; herbouw
de grammatica, kopieer nooit inhoud.

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
| `archetype/patroon` | voor cover/divider/quote: **verplicht** een officiële variant (`cover-01`…`cover-04`, `divider-01`…`divider-10`, `quote-01` — catalogus in `engine/web/assets/chrome/manifest.json`); voor contentslides: patroon uit `patterns.md` (`sfnl-table {orange|royal|teal|navy}`, `flow-tree`, `veranderttheorie-map`, `effectenkaart`, `chevron-process`, `stat-cards`, `stakeholder-ladder`, `icon-tiles`, `chips`, `definition-box`), `stat-banner` of "bespoke" |
| `frame model` | editorial kadergrid choice: sidebar, banded exhibit, full matrix, verdict box, evidence stack, chart + conclusion band, or official archetype |
| `type scale` | body density: 18pt sparse / 16pt default / 14pt dense; justify any 14pt use |
| `font emphasis` | where Gotham Bold is allowed: big number, official archetype slot, or none |
| `slot fit` | for cover/divider/quote: required text fields vs. manifest slots; choose another archetype if fields do not fit |
| `reference cue` | reference file / referentiebestand cue applied, or rejected because SFNL brand rules, SFNL-merkregels, editorial kadergrid, or archetype slots take precedence |
| `anti-slop check` | domain-specific artifact, primary/secondary/tertiary hierarchy, no generic decoration, no color-only meaning, squint test / squint-test result |
| `compositie` | regio-indeling in woorden: kolommen/rijen, wat waar, verhouding (bv. "links 2/5 tekst, rechts 3/5 chart-placeholder") |
| `accent` | waar het accent valt (één plek per slide die de boodschap draagt) |
| `chart` | dossier-viz-kandidaat → charttype (column/stackedColumn/bar/line/area/pie/donut/scatter): wordt een chartspec in deck.json |
| `iconen/assets` | welke gerasterde iconen of pre-rendered PNGs nodig zijn |
| `chrome` | light / dark / none |
| `rationale` | één regel: waarom deze compositie de boodschap draagt |

Schrijf dit als markdown-tabel vóór er HTML bestaat. Bespoke composities (funnel,
geldstroom-diagram, stakeholderkaart, parallelle tijdlijnen) zijn welkom: schets regio's en
elementen in het storyboard zodat de HTML-stap mechanisch wordt. Complexe native elementen
waarvoor geen standaardpatroon of tabel-syntax volstaat, kunnen via de per-deck hook — noteer
dat expliciet (tabellen hoeven níét via de hook: `<table class="sfnl-table …">` wordt native en
bewerkbaar, zie `patterns.md`).

Default content-slide approach is editorial kadergrid, not loose cards. Every content slide must
name its frame model. Prefer colored frames, bands, sidebars, evidence boxes, and verdict blocks.
The dash is not a composition. Body copy should be 16pt Lato by default; use 18pt for sparse
slides and 14pt only for dense matrices. Titles/subtitles remain ALL CAPS as a company
requirement, but should use Lato/Montserrat where possible and stay short. Gotham Bold is
display-only. Every content slide must pass the anti-slop check: domain-specific artifact, clear
primary/secondary/tertiary hierarchy, no generic decoration, no color-only meaning, and squint
test pass.

## Stap 2.5: visuele review van sleutelslides

Het tekst-storyboard uit stap 2 is genoeg voor rechttoe-rechtaan composities, maar niet altijd
genoeg om te beoordelen of een bespoke of narratief cruciale slide werkt. Deze stap voegt daarom
een klein, visueel reviewmoment toe vóórdat er HTML voor de hele deck wordt geschreven.

**Moduskeuze.** Standaard: **Track B** — tekst-storyboard plus visuele review van sleutelslides.
Val terug op **Track A** (alleen tekst-storyboard, direct door naar stap 3) wanneer de gebruiker
dat expliciet aangeeft, of wanneer de deck triviaal klein/eenvoudig is (richtlijn: ≤ 6 slides én
geen enkele bespoke compositie in het storyboard). Meld bij terugval kort waarom, bv. "korte deck
zonder bespoke composities, ik sla de visuele review over".

**Sleutelslides markeren.** Markeer in het storyboard een subset als "sleutelslide" op basis van
twee criteria (één is genoeg):

1. **Structureel nieuw/bespoke**: composities buiten de standaardpatronen uit `patterns.md`
   (funnel, geldstroom-diagram, stakeholderkaart, parallelle tijdlijnen, etc.).
2. **Narratief cruciaal**: slides die het kernargument dragen ongeacht layout-complexiteit (SCQA-
   complicatie/antwoord, conclusie-slide, grote-getallen/verdict-slide).

Cover-, divider- en quote-slides worden nooit gemarkeerd — die liggen al vast op officiële
archetypes. Noteer bij elke gemarkeerde rij één regel rationale: waarom deze slide een visuele
check verdient. Richtlijn: 2-5 gemarkeerde slides voor een deck van 15-25 slides — als vrijwel de
hele deck bespoke is, is dat een signaal om de storyboard-fase zelf te herzien, niet om alles te
markeren.

**Mockup: snelle standalone HTML, geen build-pipeline.** Bouw voor elke gemarkeerde slide een
snelle standalone HTML-mockup:

- Gebruikt `sfnl.css`-tokens (kleuren, typografie) voor merkherkenbaarheid.
- Benadert de compositie uit het storyboard: regio-indeling, hiërarchie, accentplek, ruwe
  chart-vorm (een placeholder-vorm volstaat, geen echte data-driven chart nodig).
- Gaat **niet** door `html2pptx`/`build_deck.js` — geen chrome-injectie, geen pixel-exacte
  fontregels, geen paginanummer/logo. Dit is een layout-schets, geen preview van de uiteindelijke
  slide. Benoem dat expliciet bij het presenteren.

**Presentatie en iteratieloop.** Zet alle gemarkeerde mockups in **één Artifact** (stacked
secties of een slide-picker binnen dezelfde pagina) en vraag in één beurt feedback op de hele
batch. Bij gevraagde wijzigingen: pas de storyboard-rij(en) én de mockup(s) aan, redeploy dezelfde
Artifact (zelfde `file_path`/URL), en vraag opnieuw — tot goedkeuring. Schrijf geen HTML voor de
uiteindelijke slide vóór deze goedkeuring.

Na goedkeuring zijn de goedgekeurde composities de autoritatieve referentie voor die slides in
stap 4. Niet-gemarkeerde slides doorlopen de bestaande stap-3-zelfreview en tekst-goedkeuring
ongewijzigd.

## Stap 3: self-review van het hele storyboard

- Vult elke contentslide het canvas? Een slide die "een kaartje linksboven" is, is een defect.
- Geen twee aangrenzende slides met identieke compositie, tenzij bewust ritme (bv. KPI-reeks).
- Elke dossier-viz-kandidaat (`chart`/`kpi`) landt als native chart, big-number of stat-banner —
  cijfers die in bodytekst blijven hangen zijn een gemiste exhibit.
- Multi-accent: elke categorie overal dezelfde kleur; dividers onderling verschillend.
- Cover/divider/quote: alleen officiële archetype-varianten — een zelf ontworpen cover of
  divider is een defect, hoe mooi ook. Kies divider-foto's die bij het sectiethema passen
  (beschrijvingen in het manifest). Doe vóór keuze een archetype-slot preflight tegen
  `engine/web/assets/chrome/manifest.json`: match verplichte titel/subtitel/metadata-velden met
  beschikbare slots, kies een andere variant als de velden niet passen, en voeg geen losse
  tekstboxen toe buiten de manifest slots.
- Reference file / referentiebestand: elke overgenomen cue heeft een reden; elke verworpen cue
  noemt de botsing met SFNL brand rules, SFNL-merkregels, editorial kadergrid of officiële
  archetype-slots.
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
