# Design: consultant-grade visuals voor sfnl-pptx (tabellen, diagrammen, infographics)

**Datum:** 2026-07-07
**Status:** goedgekeurd ontwerp, wacht op implementatieplan
**Aanleiding:** de plugin kan geen complexe visuals maken — geen tabellen, geen pijlen/connectors,
geen infographics. Alles komt uit als rechthoekige "ugly boxes". Voor consultant-PowerPoints is
dat onvoldoende.

## Referentiemateriaal

Twee echte SFNL-eindrapporten zijn slide-voor-slide geanalyseerd:

1. *Impact meetplan Welzijn op Recept* (Venlo, maart 2026, 22 slides)
2. *MBC Postmortale diagnostiek* (Hartstichting, juni 2026, 82 slides)

De geëxtraheerde visuele grammatica staat in de **exhibit-galerij**:
`sfnl-pptx/engine/reference/exhibits/` — 18 gecureerde PNG's + `manifest.md`. Die galerij is
onderdeel van dit ontwerp (component 5) en de permanente kwaliteitsmaatstaf voor de skills.

Kernbevindingen:

- **Gestylede native tabellen zijn het werkpaard** (±35 van 104 slides): gekleurde headerregel,
  getinte sectieregels, totaalbanden, rechts uitgelijnde €-kolommen met rood=kost/teal=baat,
  bronkolom.
- **Diagramslides** gebruiken echte connectors: veranderttheorie-kaarten, beslisbomen met
  percentagelabels op takken, effectenkaart-matrices met gestippelde scheiders en geroteerde labels.
- **Infographic-patronen**: chevron-procesbanden, big-number statkaarten met achtergrondpijl,
  stakeholder-resultaatladders, icon-tiles, letter/nummer-chips, getinte definitieboxen.
- **De stijl is zachter dan patterns.md nu voorschrijft**: afgeronde hoeken (~8-12pt),
  pasteltinten, ruime padding — terwijl patterns.md "2pt square-ish frames" eist en tabellen
  verbiedt. Besluit: **de designtaal wordt herijkt op de echte deliverables** (optie "align to
  references", bevestigd door Xavier).

Gekozen aanpak: **hybride** (bevestigd door Xavier) — HTML blijft het enige authoring-oppervlak;
de converter krijgt tabellen en een kleine shape/connector-vocabulaire; patronen en skills worden
herbouwd rond de referentiegrammatica. Alles blijft **bewerkbare native PowerPoint-shapes**.

## Component 1 — Native tabellen (`<table>` → PptxGenJS `addTable`)

`html2pptx.js` leert HTML `<table>`-elementen vertalen naar echte, bewerkbare
PowerPoint-tabellen.

- **Styling via CSS-klassen** die mappen op SFNL-presets (afgeleid uit de exhibits):
  - `sfnl-table` basis + accentmodifier (`orange` / `royal` / `teal` / `navy`): gekleurde
    headerregel (witte caps-tekst), witte body, subtiele rijbanding.
  - Rijrollen: `section-row` (getinte tussenkop ín de tabel), `total-row` (vet, grijze of navy
    band), gewone dataregels.
  - Kolom/celsemantiek: `col-num` (rechts uitgelijnd), `val-cost` (rood), `val-benefit` (teal),
    `col-source` (kleiner, gedempt).
- **Conversie**: cel-per-cel tekstextractie met bestaande inline-formatting parser; kolombreedtes
  uit de gerenderde layout (Playwright-meting), rijhoogtes auto met minimum.
- **Buildvalidatie** (zelfde luide-faal-filosofie als de rest): celoverflow-detectie, minimum
  10pt celtekst, tabel-past-op-canvas check, verboden geneste tabellen.
- De regel "geen `<table>`" en de flex-row-matrix-workaround verdwijnen uit patterns.md; de
  `hooks` escape hatch blijft bestaan voor exotische gevallen.

## Component 2 — Shape- en connectorvocabulaire in de converter

Kleine, gesloten set nieuwe primitieven, geauthored als `<div data-shape="…">`:

- **Shapes**: `chevron`, `pill`, `circle`, `arrow-right/left/up/down` (blokpijlen), naast de
  bestaande rect/roundRect. Elke shape mapt 1:1 op een native PptxGenJS-shapetype — bewerkbaar
  in PowerPoint. Tekst in de shape volgt de bestaande tekstregels (`<p>` etc.).
- **Connectors**: nodes krijgen `id`'s; een slide-niveau `data-connectors` spec (JSON-attribuut
  op `<body>`, zodat diagramdefinitie en layout in hetzelfde bestand leven) declareert
  `from → to` met stijl: `straight` | `elbow`, arrowhead aan/uit, kleur, dashed, optioneel
  tekstlabel (voor percentages op takken). De build berekent ankerpunten uit de gerenderde
  elementposities: **HTML/flexbox doet de layout, de engine routeert alleen de lijnen.**
- **Geroteerde labels**: `data-rotate="270"` voor groepslabels zoals op de effectenkaart.
- Validatie: connector die naar onbekend id verwijst → buildfout; overlappende
  connector-eindpunten → waarschuwing in het buildrapport.

## Component 3 — Patroon- en tokenbibliotheek uit de referenties

- **patterns.md wordt herbouwd** rond de geëxtraheerde grammatica, met copy-paste fragmenten
  voor: gestylede tabellen (4 varianten), veranderttheorie-kaart, beslis-/flowboom,
  effectenkaart-matrix, chevron-procesband, big-number statkaarten met achtergrondpijl,
  stakeholder-resultaatladder, icon-tiles, letter/nummer-chips, definitieboxen, voetnootbanden.
- **sfnl.css** krijgt ondersteunende tokens: pasteltint-variabelen per merkkleur
  (`--sfnl-*-tint`), afgeronde-kaartklassen, icon-tile-stijlen, tabelpreset-klassen.
- **Stijlprincipes** (vervangen de kadergrid-regels): afgeronde hoeken op kaarten/tiles,
  tabellen strak; kleurrollen zoals in de exhibits (rood=kost, teal=baat, navy=totaal,
  oranje=resultaat, royal/sky=proces); witte lijniconen op volle merkkleur; ruime padding.
- Het stat-banner-archetype blijft; covers/dividers/quotes blijven verplicht uit de officiële
  chrome-archetypes (ongewijzigd).

## Component 4 — Skill-updates

- **sfnl-deck-design**: krijgt de nieuwe patroonvocabulaire zodat storyboards per slide
  "effectenkaart", "chevron-process", "sfnl-table navy" etc. kunnen specificeren, en de
  instructie om bij twijfel de bijpassende exhibit-PNG te bekijken.
- **sfnl-deck** (authoring guide): tabelregels, shape/connector-syntax, verwijzing naar de
  galerij.
- **sfnl-deck-review + deck-visual-reviewer agent**: QA-criteria voor de nieuwe elementen —
  connector-aanhechting, tabeloverflow, bandingconsistentie, kleurrolcorrectheid.
- Versiebump + README-update.

## Component 5 — Exhibit-referentiegalerij (permanent onderdeel van de prompt)

`engine/reference/exhibits/` bevat 18 gecureerde referentie-PNG's + `manifest.md` (welk exhibit
welke les leert + stijlconstanten). De skills (design, authoring, review) verwijzen er expliciet
naar en instrueren om de relevante PNG's daadwerkelijk te bekijken (Read) wanneer een slide een
tabel, diagram of statcompositie nodig heeft. Regels:

- Grammatica herbouwen en aanpassen op de inhoud — nooit pixel-voor-pixel kopiëren.
- Inhoud is klantvertrouwelijk (Hartstichting, WoR Venlo): alleen stijlreferentie, nooit
  tekst/cijfers overnemen; de galerij blijft lokaal in de pluginrepo.

## Testen

- Fixture-decks onder `tests/fixtures/`: één tabelzware set (alle 4 tabelvarianten incl.
  section/total rows) en één diagramzware set (flowboom met connectors + labels, chevron-band,
  effectenkaart-fragment).
- Build-level assertions op de gegenereerde OOXML (tabel aanwezig, shapetypes, connectorlijnen).
- De verplichte visuele loop (render → inspect → fix) blijft de eindpoort.

## Buiten scope (YAGNI)

- Geen nieuwe charttypes (de 8 native types volstaan; radar evt. later).
- Geen SVG-import.
- Geen auto-layout van diagrammen (flexbox doet layout; engine routeert alleen connectors).
- Geen themawissel/tweede stijlregister.
