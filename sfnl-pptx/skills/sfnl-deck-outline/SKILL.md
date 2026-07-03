---
name: sfnl-deck-outline
description: Stel interactief de inhoud en structuur van een SFNL-deck vast vóór er een visueel storyboard of HTML ontstaat. Vraagt 0-20 gerichte vragen over doelgroep, doel en structuur (met een optie om te skippen), schrijft daarna een per-slide content-outline weg, en wacht op goedkeuring/commentaar voordat sfnl-deck-design begint. Gebruik als stap 3 van de sfnl-deck pipeline, direct na sfnl-deck-research en vóór sfnl-deck-design.
---

# sfnl-deck-outline: inhoud en structuur vastleggen vóór het storyboard

Deze skill draait tussen het bronnendossier (`sfnl-deck-research`) en het visuele storyboard
(`sfnl-deck-design`). Doel: contentfouten (verkeerde doelgroep, ontbrekend onderdeel, verkeerde
toon) vroeg en goedkoop vangen — als tekst in een outline, niet als storyboard- of HTML-rework.

## Stap 1: schaal- en ambiguïteitsinschatting

Lees de brief/intake en het bronnendossier. Beoordeel drie factoren in proza (geen
rekenformule):

- **Omvang**: verwacht aantal slides — expliciet genoemd, of afgeleid uit scope ("kort
  statusupdate" ≈ 5-8, "volledig voorstel" ≈ 15-25).
- **Ambiguïteit**: hoeveel van {doelgroep, doel/ask, structuurvoorkeur, toon, must-include
  onderdelen, tijdlijn/deadline-context, gevoelige onderwerpen} al beantwoord zijn door de brief
  of het dossier.
- **Complexiteit**: meerdere stakeholders, onderling afhankelijke onderdelen, genuanceerde asks.

Deze drie factoren bepalen samen een doelaantal vragen tussen **0 en 20**. Een heldere,
complete brief voor een grote deck kan op 0-2 vragen uitkomen; een vage aanleiding voor een
korte deck kan alsnog 6-8 vragen opleveren. Bij 0: sla stap 2 over en ga direct naar stap 3,
met de aannames expliciet genoemd in de outline.

## Stap 2: vraagronde

Eerste bericht is altijd de globale skipvraag via `AskUserQuestion`:

> "Ik heb [N] vragen over inhoud en structuur — wil je die doorlopen, of zal ik zelf redelijke
> aannames maken en direct een outline opstellen?"

met een optie "Skip — jij bepaalt". Bij skip: ga direct naar stap 3 en noteer de aannames.

Bij niet-skippen: put vragen uit deze bank, één topic per vraag, nooit meer dan het
ingeschatte aantal, en sla een topic over als de brief het al beantwoordt:

- Doelgroep & hun voorkennis
- Primair doel/ask van de deck
- Gewenste structuur/secties
- Toon-uitzonderingen op de standaardregels in `engine/reference/voice.md`
- Must-include vs. optioneel materiaal
- Gevoeligheden of onderwerpen om te vermijden
- Gewenste lengte/tijdslimiet van de presentatie

`AskUserQuestion` staat maximaal 4 vragen per aanroep toe. Bij meer dan 4 vragen: vuur
opeenvolgende aanroepen van (max) 4 vragen af — bijv. 4+4+4 voor 12 vragen — zodat het voor de
gebruiker als één vlotte ronde aanvoelt, niet als vraag-voor-vraag. Het totaal over alle
aanroepen samen blijft onder de 20.

## Stap 3: outline schrijven

Schrijf naar `output/<YYYY-MM-DD>-<slug>/outline.md`:

```markdown
# <Decknaam> — outline

## Narrative (SCQA)
<Situation → Complication → Question → Answer in een paar zinnen>

## Slides

### 1. <werktitel / concept action title>
- **Sectie**: <sectienaam>
- **Kernpunten**: <bullets>
- **Bronverwijzing**: <dossierregels, bv. T1.1, T3.2 — leeg als geen cijfers>
- **Archetype-hint**: content | cover | divider | quote

### 2. ...

## Open vragen / aannames
<wat is geskipt, welke aannames zijn gemaakt, wat de gebruiker eventueel nog moet aanleveren>
```

Regels:

- Genummerde entries met stabiel anchor (`### N. ...`) zodat commentaar precies te refereren is.
- Geen layoutdetails (regio's, composities, chart-typen, kolomverhoudingen) — dat is het werk
  van `sfnl-deck-design` in de volgende stap.
- Elk cijfer dat in "Kernpunten" staat, verwijst naar een dossierregel uit
  `output/research/<slug>-dossier.md` (zelfde regel als `sfnl-deck-research` Stap 4.1).

## Stap 4: review- en commentaarloop

Zelfde patroon als een spec-review: meld

> "Outline geschreven naar `<pad>`. Bekijk en becommentarieer 'm direct in het bestand (of
> reageer hier) voordat ik met het visuele storyboard begin."

Wacht op reactie. Bij commentaar of wijzigingsverzoek: verwerk, herschrijf de outline, en meld
opnieuw. Er start geen storyboard-werk vóór expliciete goedkeuring.

## Stap 5: handoff

Geef het outline-pad door aan `sfnl-deck-design`. Contentwijzigingen die tijdens het
storyboarden naar boven komen, gaan terug naar de outline (dit bestand), niet naar het
storyboard direct — zelfde discipline als de bestaande stap-terugval-regel in
`sfnl-deck-design` Stap 4.
