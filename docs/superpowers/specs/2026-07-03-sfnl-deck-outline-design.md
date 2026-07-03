# sfnl-deck-outline: interactieve content-outline vóór storyboard

## Probleem

De sfnl-deck pipeline gaat vandaag direct van research (bronnendossier) naar narrative/titels
naar visueel storyboard (`sfnl-deck-design`). De narrative-stap is een monoloog: Claude bepaalt
zelf structuur, secties en action titles zonder de gebruiker gericht te bevragen over inhoud en
structuur, en zonder een expliciet reviewmoment vóórdat er storyboard- of HTML-werk gebeurt.
Fouten in de contentkeuzes (verkeerde doelgroep, ontbrekend onderdeel, verkeerde toon) worden nu
pas zichtbaar als er al een storyboard of zelfs slides staan.

## Doel

Voeg een interactieve outline-stap toe tussen research en storyboard: een korte, schaalbare
vraagronde over inhoud en structuur, gevolgd door een beknopte per-slide outline die de
gebruiker kan becommentariëren vóór er ook maar één storyboard-regel of HTML-bestand ontstaat.

## Pipeline-wijziging

`sfnl-deck` (`sfnl-pptx/skills/sfnl-deck/SKILL.md`) krijgt een nieuwe stap 3, die de huidige
stap 3 ("Narrative en titels") vervangt:

1. Intake
2. Research → `sfnl-deck-research` (ongewijzigd)
3. **Outline** → `sfnl-deck-outline` (nieuw)
4. Storyboard → `sfnl-deck-design` (ongewijzigd, consumeert de goedgekeurde outline)
5. Auteur HTML + build (ongewijzigd)
6. Review + proof (ongewijzigd)

`sfnl-deck-design` blijft ongewijzigd; het leest voortaan `output/<datum>-<slug>/outline.md` in
plaats van losse narrative-aantekeningen.

## Nieuwe skill: sfnl-deck-outline

### Stap 1: schaal- en ambiguïteitsinschatting

Voordat er iets gevraagd wordt, beoordeelt Claude drie factoren op basis van de brief en het
bronnendossier:

- **Omvang**: verwacht aantal slides (expliciet genoemd, of afgeleid uit scope — "kort
  statusupdate" ≈ 5-8, "volledig voorstel" ≈ 15-25).
- **Ambiguïteit**: hoeveel van {doelgroep, doel/ask, structuurvoorkeur, toon, must-include
  onderdelen, tijdlijn/deadline-context, gevoelige onderwerpen} al beantwoord zijn door de brief
  of het dossier.
- **Complexiteit**: meerdere stakeholders, onderling afhankelijke onderdelen, genuanceerde asks —
  dingen die niet met één simpel antwoord op te lossen zijn.

Dit is een inschatting in proza, geen rekenformule. De drie factoren bepalen samen een
doelaantal vragen tussen **0 en 20**. Een heldere, complete brief voor een grote deck kan alsnog
op 0-2 vragen uitkomen; een vage aanleiding voor een korte deck kan alsnog 6-8 vragen opleveren.

### Stap 2: vraagronde

- Het eerste bericht is altijd de globale skipvraag: *"Ik heb [N] vragen over inhoud en
  structuur — wil je die doorlopen, of zal ik zelf redelijke aannames maken en direct een
  outline opstellen?"* met een optie "Skip — jij bepaalt".
- Bij niet-skippen: vragen komen uit een vragenbank (doelgroep & voorkennis, primair doel/ask,
  gewenste structuur/secties, toon-uitzonderingen op `voice.md`, must-include vs. optioneel
  materiaal, gevoeligheden om te vermijden, gewenste lengte/tijdslimiet). Nooit meer vragen dan
  het ingeschatte aantal; sla een topic over als de brief het al beantwoordt.
- `AskUserQuestion` staat maximaal 4 vragen per aanroep toe. Bij een groter aantal vuurt Claude
  opeenvolgende aanroepen van (max) 4 vragen af — bijv. 4+4+4 voor 12 vragen — zodat het voor de
  gebruiker als één vlotte ronde aanvoelt in plaats van vraag-voor-vraag. Het totaal over alle
  aanroepen samen blijft onder de 20.

### Stap 3: outline schrijven

Schrijf naar `output/<YYYY-MM-DD>-<slug>/outline.md`:

- Bovenaan: de SCQA-narrative in een paar zinnen (Situation → Complication → Question → Answer).
- Daarna per slide een genummerde entry met een stabiel anchor (`### 4. ...`) zodat commentaar
  precies te refereren is:

  ```markdown
  ### 4. Kosten dalen 18% na interventie
  - **Sectie**: Resultaten
  - **Kernpunten**: ...
  - **Bronverwijzing**: T3.2, T3.4
  - **Archetype-hint**: content | cover | divider | quote
  ```

- Geen layoutdetails (regio's, composities, chart-typen) — dat blijft het werk van
  `sfnl-deck-design` in de volgende stap.
- Sluit af met eventuele open vragen/aannames die zijn gemaakt tijdens het skippen of
  gedeeltelijk beantwoorden van de vraagronde.

### Stap 4: review- en commentaarloop

Zelfde patroon als de spec-review in de brainstorming-flow: *"Outline geschreven naar `<pad>`.
Bekijk en becommentarieer 'm direct in het bestand (of reageer hier) voordat ik met het visuele
storyboard begin."* De gebruiker kan commentaar toevoegen in het bestand of in de chat; Claude
leest, verwerkt, en bevestigt opnieuw totdat de gebruiker akkoord geeft. Er start geen
storyboard-werk vóór die goedkeuring.

### Stap 5: handoff

Geef het outline-pad door aan `sfnl-deck-design`. Die stap leest de goedgekeurde outline als
input voor de per-slide layoutcompositie; content- of structuurwijzigingen op dat moment gaan
terug naar de outline, niet naar het storyboard (zelfde discipline als de bestaande
stap-terugval-regel in `sfnl-deck-design`).

## Wijzigingen aan bestaande bestanden

- `sfnl-pptx/skills/sfnl-deck/SKILL.md`: pipeline-lijst bijwerken (stap 3 wordt de nieuwe
  outline-stap; stap 4 verwijst naar de outline in plaats van losse narrative-notities).
- Nieuw bestand: `sfnl-pptx/skills/sfnl-deck-outline/SKILL.md`.
- `sfnl-pptx/skills/sfnl-deck-design/SKILL.md`: "Wanneer"-sectie bijwerken zodat die verwijst
  naar de outline als input in plaats van "narrative/titels" in het algemeen.

## Out of scope

- Geen wijziging aan `sfnl-deck-research` (bronnendossier-stap blijft exact zoals die is).
- Geen apart tool/UI voor commentaar — hergebruikt het bestaande bestand-review-patroon.
- Geen wijziging aan de HTML-, build-, of review/proof-stappen verderop in de pipeline.
