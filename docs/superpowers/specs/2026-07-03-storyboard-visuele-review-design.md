# sfnl-deck-design: visuele review van sleutelslides vóór HTML-authoring

## Probleem

`sfnl-deck-design` produceert vandaag één tekst-storyboard (markdown-tabel) voor de hele deck,
dat als geheel wordt goedgekeurd vóór er HTML wordt geschreven. Dat werkt voor rechttoe-
rechtaan composities, maar bij bespoke of narratief cruciale slides (funnels, geldstroom-
diagrammen, het SCQA-antwoord, een grote-getallen-conclusie) is een tekstrij vaak niet genoeg om
te beoordelen of de compositie werkt — dat wordt nu pas zichtbaar na de volledige build+render-
cyclus in stap 6, wat duur is om te herstellen.

## Doel

Voeg een tweede, visueel reviewmoment toe binnen `sfnl-deck-design`, alléén voor een klein
aantal sleutelslides, tussen het tekst-storyboard (stap 2) en de HTML-authoring (stap 4). De
rest van de deck doorloopt de bestaande tekst-only goedkeuring ongewijzigd.

## Moduskeuze

`sfnl-deck-design` kiest per deck tussen twee tracks:

- **Track A (autonoom, huidig gedrag)**: alleen het tekst-storyboard, in zijn geheel goedgekeurd.
- **Track B (default): tekst-storyboard + visuele review van sleutelslides.**

Claude start standaard op Track B. Claude valt terug op Track A wanneer:
- de gebruiker dat expliciet aangeeft, of
- de deck triviaal klein/eenvoudig is (richtlijn: ≤ 6 slides én geen enkele bespoke compositie
  in het storyboard).

Bij terugval naar Track A meldt Claude kort waarom (bv. "korte deck zonder bespoke composities,
ik sla de visuele review over").

## Sleutelslides markeren

Nadat het volledige tekst-storyboard (stap 2 van `sfnl-deck-design`) is opgesteld, markeert
Claude een subset als "sleutelslide" op basis van twee criteria (beide tellen mee, één is
genoeg):

1. **Structureel nieuw/bespoke**: composities buiten de standaardpatronen uit `patterns.md`
   (funnel, geldstroom-diagram, stakeholderkaart, parallelle tijdlijnen, etc.).
2. **Narratief cruciaal**: slides die het kernargument dragen ongeacht layout-complexiteit (SCQA-
   complicatie/antwoord, conclusie-slide, grote-getallen/verdict-slide).

Cover-, divider- en quote-slides worden nooit gemarkeerd — die zijn al vastgelegd op officiële
archetypes en hebben geen compositiekeuze. Bij elke gemarkeerde rij noteert Claude één regel
rationale: waarom deze slide een visuele check verdient.

Geen harde bovengrens op het aantal gemarkeerde slides, maar in de praktijk is dit een klein
deel van de deck (richtlijn: 2-5 slides voor een deck van 15-25 slides). Als vrijwel de hele
deck bespoke is, is dat een signaal dat de storyboard-fase zelf opnieuw doordacht moet worden,
niet dat alles gemarkeerd moet worden.

## Mockup: snelle standalone HTML, geen build-pipeline

Voor elke gemarkeerde slide bouwt Claude een **snelle standalone HTML-mockup**:

- Gebruikt `sfnl.css`-tokens (kleuren, typografie) voor merkherkenbaarheid.
- Benadert de compositie uit het storyboard: regio-indeling, hiërarchie, accentplek, ruwe
  chart-vorm (geen echte data-driven native chart nodig — een placeholder-vorm volstaat).
- Gaat **niet** door `html2pptx`/`build_deck.js` — geen chrome-injectie, geen pixel-exacte
  fontregels, geen paginanummer/logo. Dit is een layout-schets, geen preview van de uiteindelijke
  slide.
- Claude benoemt dit expliciet bij het presenteren, zodat de gebruiker de mockup beoordeelt op
  compositie en niet op pixelperfecte afwerking.

## Presentatie en iteratieloop

Alle gemarkeerde mockups gaan in **één Artifact** (stacked secties of een slide-picker binnen
dezelfde pagina), zodat ze in één keer naast elkaar te beoordelen zijn. Claude vraagt in één
beurt feedback op de hele batch.

Bij gevraagde wijzigingen: Claude past de betreffende storyboard-rij(en) én de mockup(s) aan,
redeployt dezelfde Artifact (zelfde `file_path`/URL), en vraagt opnieuw. Dit herhaalt zich tot
goedkeuring. Er wordt geen HTML voor de uiteindelijke slide geschreven vóór deze goedkeuring.

Na goedkeuring worden de goedgekeurde composities de autoritatieve referentie voor die slides in
stap 4 (HTML + deck.json authoring) van `sfnl-deck-design`. Niet-gemarkeerde slides doorlopen de
bestaande stap-3-zelfreview en tekst-goedkeuring zoals nu.

## Wijzigingen aan bestaande bestanden

- `sfnl-pptx/skills/sfnl-deck-design/SKILL.md`: nieuwe **Stap 2.5: visuele review van
  sleutelslides** tussen de huidige stap 2 (storyboard per slide) en stap 3 (self-review). Bevat
  de moduskeuze, markeercriteria, mockup-aanpak en de Artifact-iteratieloop.
- `sfnl-pptx/skills/sfnl-deck/SKILL.md`: stap 4 ("Storyboard") van de pipeline-beschrijving
  uitbreiden met een verwijzing naar de nieuwe visuele deelstap.

## Out of scope

- Geen wijziging aan de build/render-engine (`build_deck.js`, `html2pptx.js`, `raster.js`) —
  mockups gebruiken die pipeline niet.
- Geen wijziging aan stap 6 (build + visuele loop) of stap 7 (review/proof) van `sfnl-deck`.
- Geen wijziging aan de archetype-regels voor cover/divider/quote.
- Geen apart bestand/tool voor de mockups buiten de Artifact-tool; geen permanente opslag van
  mockup-HTML in de workspace (het storyboard-document blijft de autoritatieve bron, niet de
  mockup-bestanden).
