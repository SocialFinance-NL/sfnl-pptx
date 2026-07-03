# SFNL-sjabloon inbedden in gegenereerde decks (layoutgalerij)

## Probleem

De v2 build-pipeline (html2pptx + PptxGenJS) bouwt content-slides from scratch zonder ooit
een echte slide master/layout van het officiële SFNL-sjabloon te gebruiken. Covers/dividers/
quotes krijgen de officiële look via gerasterde PNG-achtergronden (chrome-archetypes), niet via
echte OOXML-masters. Gevolg: een gegenereerde `.pptx` bevat geen enkele SFNL-layout. Als een
gebruiker de deck opent in PowerPoint en handmatig een slide toevoegt (Start > Nieuwe dia),
krijgt die alleen generieke PowerPoint-layouts te zien — niets in huisstijl om vanuit te werken.

Daarnaast staan de bronbestanden voor de huisstijl (`01 SFNL_sjabloon.potx`, `sfnl-slides.pptx`)
niet betrouwbaar onder versiebeheer: een blanket `.gitignore`-regel (`*.potx`, `*.pptx`) negeert
ze, waardoor een verse checkout van deze repo ze mist tenzij ze met force zijn toegevoegd. Dat is
vandaag zelfs voor het bestaande `sfnl-slides.pptx` niet gebeurd.

## Doel

Elke door de sfnl-pptx-plugin gegenereerde `.pptx` bevat na de build de volledige set officiële
SFNL slide masters + layouts (uit `01 SFNL_sjabloon.potx`), zodat een gebruiker die de deck opent
in PowerPoint via "Nieuwe dia" / de layout-galerij een SFNL-branded layout kan kiezen om
handmatig een slide toe te voegen — zonder de huisstijl zelf te hoeven nabootsen. Dit gebeurt
zonder de bestaande gegenereerde slides op enige manier te veranderen. Het bronsjabloon wordt
onderdeel van de plugin zelf (bundled + getrackt in git), niet iets dat los aangeleverd moet
worden.

## Scope

- Alleen de build-pipeline van sfnl-pptx (`build_deck.js` + nieuwe post-build stap). Geen
  wijziging aan hoe content-slides zelf worden opgebouwd (HTML/PptxGenJS-architectuur blijft
  ongewijzigd), geen wijziging aan de chrome-archetypes voor covers/dividers/quotes.
- Volledige layoutset (alle ~30 layouts, beide masters uit het sjabloon) wordt meegenomen — geen
  curatie/subset.
- Inclusief: bundelen van `01 SFNL_sjabloon.potx` als plugin-asset + git-tracking fixen voor
  zowel dit nieuwe bestand als het bestaande `sfnl-slides.pptx`.
- Buiten scope: het daadwerkelijk gebruiken van deze layouts vanuit de generatie-pipeline zelf
  voor content-slides (die blijven PptxGenJS/HTML-based); documentatie-updates voor
  eindgebruikers (auteursgids) zijn optioneel, niet vereist voor deze iteratie.

## Architectuur / pipeline-plaatsing

Nieuw script: `sfnl-pptx/engine/scripts/merge_template.py`, draait direct na `build_deck.js` en
vóór `qa_text.py`/`render.py`:

```
build_deck.js      → schrijft deck.pptx
merge_template.py  → merget masters/layouts uit sfnl-sjabloon.potx in deck.pptx (in place)
qa_text.py         → bestaande tekst-/merk-QA (ongewijzigd)
render.py          → bestaande visuele-QA-loop (ongewijzigd)
```

Het script werkt op de ruwe OOXML zip-parts (via `zipfile` + `lxml`), niet via python-pptx's
objectmodel — python-pptx heeft geen API om masters tussen presentaties te mergen, en omdat we
alleen XML-parts verplaatsen is dat ook niet nodig. Bron is altijd het gebundelde
`sfnl-sjabloon.potx` (niet de `sfnl-slides.pptx`-sampler, die alleen voor de chrome-archetypes
dient).

## Bundelen van het bronsjabloon

- `01 SFNL_sjabloon.potx` wordt gekopieerd naar `sfnl-pptx/engine/assets/sfnl-sjabloon.potx`
  (hernoemd naar de bestaande naamgevingsconventie: lowercase, koppeltekens).
- `.gitignore` krijgt een uitzondering voor de gebundelde template-assets (bv.
  `!sfnl-pptx/engine/assets/*.pptx` en `!sfnl-pptx/engine/assets/*.potx`), zodat deze bestanden
  daadwerkelijk getrackt worden ondanks de blanket `*.pptx`/`*.potx`-regel.
- Zowel het nieuwe `sfnl-sjabloon.potx` als het bestaande, tot nu toe untracked
  `sfnl-slides.pptx` worden met deze fix toegevoegd aan git — zodat een verse checkout van de
  repo (of een geïnstalleerde plugin) alle drie de template-assets bevat zonder handmatige stap.
- `merge_template.py` verwijst naar het bronbestand via een pad relatief aan het script zelf
  (zelfde patroon als `extract_chrome.py`:
  `Path(__file__).resolve().parents[1] / "assets" / "sfnl-sjabloon.potx"`), dus onafhankelijk
  van waar de plugin gecheckout/geïnstalleerd is.

## Merge-mechaniek

Voor elke build:

1. Open `deck.pptx` en `sfnl-sjabloon.potx` als zip-archieven.
2. Kopieer: beide slide masters, alle ~30 slide layouts, het/de theme-part(s) waarnaar ze
   verwijzen, en alle media (afbeeldingen) die deze layouts gebruiken.
3. Hernummer part-bestandsnamen en relatie-ID's (`rId#`) van elk gekopieerd onderdeel zodat niets
   botst met de bestaande parts in de deck — dit is het meest foutgevoelige onderdeel.
4. Voeg `Override`-entries toe aan `[Content_Types].xml` voor de nieuwe parts.
5. Voeg de nieuwe master(s) toe aan `presentation.xml`'s `<p:sldMasterIdLst>`, ná de bestaande
   PptxGenJS-gegenereerde master, plus bijbehorende relaties in `presentation.xml.rels`.
6. Hernoem de binnenkomende slide master(s) naar iets herkenbaars (bv. "SFNL Sjabloon") zodat het
   een herkenbare eigen groep vormt in PowerPoint's Ontwerp-tab / layout-galerij, los van de
   default-master van de gegenereerde content.

Toevoegen ná de bestaande master (in plaats van vervangen/herordenen) betekent dat de al
gegenereerde slides volledig ongemoeid blijven — dit is puur additief.

## Foutafhandeling & validatie

- **Hard falen, niet stil overslaan.** Als `sfnl-sjabloon.potx` ontbreekt, of de merge een
  exception gooit (onverwachte part-structuur, kapotte XML), faalt de build met een duidelijke
  foutmelding. Er wordt nooit een deck opgeleverd die stilzwijgend het sjabloon mist.
- **Round-trip-check:** direct na het mergen wordt het bestand opnieuw geopend met python-pptx
  om grove corruptie vroeg te detecteren.
- **Gezaghebbende check:** de bestaande PowerPoint-COM-tooling (gebruikt door `render.py`) wordt
  uitgebreid met een assertie dat `Presentation.Designs.Count` met één is toegenomen en dat
  `CustomLayouts.Count` van het nieuwe design overeenkomt met het aantal layouts in het sjabloon.
  Dit is de echte test — python-pptx kan soepeler zijn dan PowerPoint zelf (dat een
  "repareren?"-prompt kan tonen), dus een daadwerkelijke PowerPoint-open is het bewijs dat de
  merge structureel klopt.
- **Handmatige acceptatietest** (eenmalig bij oplevering, niet per build): genereer een deck,
  open in echte PowerPoint, gebruik Start → Nieuwe dia/Lay-out, controleer dat alle officiële
  SFNL-layouts verschijnen onder een herkenbare naam, voeg er één in en controleer dat deze
  correct rendert met bewerkbare placeholders, en controleer dat de bestaande gegenereerde
  slides ongewijzigd blijven.

## Bekende trade-off

Doordat alle ~30 layouts + beide masters worden meegenomen (in plaats van een curated subset),
neemt de bestandsgrootte van elke gegenereerde deck merkbaar toe (een flink deel van de ~16MB van
het sjabloon zit in achtergrondgrafiek van deze layouts). Dit is een bewust aanvaarde kost voor
volledige fidelity.

## Wijzigingen aan bestaande bestanden

- Nieuw: `sfnl-pptx/engine/scripts/merge_template.py`.
- Nieuw asset: `sfnl-pptx/engine/assets/sfnl-sjabloon.potx` (gekopieerd van root
  `01 SFNL_sjabloon.potx`).
- `.gitignore`: uitzonderingsregels voor gebundelde template-assets onder
  `sfnl-pptx/engine/assets/`.
- Git: `sfnl-pptx/engine/assets/sfnl-slides.pptx` en `sfnl-pptx/engine/assets/sfnl-sjabloon.potx`
  worden toegevoegd aan versiebeheer.
- Build-orkestratie (waar `build_deck.js` wordt aangeroepen, vermoedelijk in
  `sfnl-pptx/skills/sfnl-deck/SKILL.md` of een build-script): nieuwe stap voor
  `merge_template.py` tussen build en QA.
- `render.py` (of een nieuw validatiescript ernaast): COM-assertie op
  `Designs.Count`/`CustomLayouts.Count`.

## Out of scope

- Het daadwerkelijk gebruiken van de geïmporteerde SFNL-layouts door de generatie-pipeline zelf
  voor content-slides (blijft PptxGenJS/HTML).
- Een curated subset van layouts (optie C uit de brainstorm) — expliciet niet gekozen.
- Herbouwen van de pipeline op python-pptx (optie B) — expliciet afgewezen, te ingrijpend t.o.v.
  de recente v2-herontwerp-investering.
- Documentatie-update van de auteursgids voor eindgebruikers over hoe ze de geïmporteerde
  layouts het beste gebruiken (mogelijk vervolgwerk).
- Automatisch periodiek hersynchroniseren van `sfnl-sjabloon.potx` als het officiële sjabloon
  wijzigt (blijft een handmatige kopieerstap, net als vandaag bij het bronbestand van
  `extract_chrome.py`).
