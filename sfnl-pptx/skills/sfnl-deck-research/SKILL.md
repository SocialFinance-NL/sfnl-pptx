---
name: sfnl-deck-research
description: Onderbouw een SFNL-deck met bronnen voordat er ook maar één slide geschreven wordt. Zet een idee, brief of losse aanleiding om in een bronnendossier met feiten, cijfers en herleidbare bronnen dat de narrative- en contentstap voedt. Gebruik als stap 2 van de sfnl-deck pipeline, of los wanneer de gebruiker vraagt om "onderbouw dit", "zoek cijfers voor deze presentatie", "research voor de deck", of een deck-onderwerp aanlevert zonder feitenmateriaal.
---

# sfnl-deck-research: van idee naar bronnendossier

Een consultancy-waardige deck staat of valt met kloppende cijfers en herleidbare claims. Deze
skill draait vóór de narrative-stap en levert één artefact op: het **bronnendossier**. Alles wat
daarna op een slide belandt aan feiten, cijfers of causale claims moet naar een dossierregel
herleidbaar zijn.

## Wanneer dit draait

Direct na de intake van `sfnl-deck` (stap 1), vóór narrative en action titles. Sla deze stap
alleen over als de gebruiker een compleet, reeds onderbouwd dossier of brondocument aanlevert —
noteer dat dan expliciet als de bron.

## Stap 1: Claimlijst opstellen

Lees de brief of het idee en schrijf uit welke beweringen de deck moet dragen. Onderscheid:

- **Feitelijke claims** — "eenzaamheid onder 75-plussers stijgt" — vereisen een externe bron.
- **Cijfers** — kosten, aantallen, percentages, SROI-ratio's — vereisen een exacte waarde met
  eenheid, jaartal en bron.
- **Causale claims** — "aanpak X leidt tot minder zorggebruik" — vereisen evidence (evaluaties,
  peer-reviewed onderzoek, eerdere SFNL-projecten).
- **Eigen materiaal** — projectresultaten, offertes, klantdata — komt uit aangeleverde documenten;
  citeer het document en de vindplaats.

Vraag de gebruiker alleen om input als een claim fundamenteel is én nergens te vinden.

## Stap 2: Bronnen zoeken

Zoek per claim gericht, met voorkeur voor Nederlandse primaire bronnen: CBS, SCP, RIVM, WODC,
NJi, Movisie, CPB, ministeries, gemeentelijke monitors, en peer-reviewed literatuur. Gebruik
websearch en aangeleverde documenten. Regels:

- Noteer altijd publicatiejaar; markeer bronnen ouder dan 5 jaar.
- Neem het exacte cijfer over, niet een afronding uit een secundaire bron.
- Nooit een cijfer verzinnen of extrapoleren zonder dat te markeren. Geen bron gevonden?
  Markeer de regel als `[aanname]` en meld dit expliciet aan de gebruiker.
- Bij tegenstrijdige bronnen: neem beide op en benoem het verschil.

## Stap 3: Dossier schrijven

Schrijf het dossier naar `output/research/<slug>-dossier.md` met deze structuur per thema:

```markdown
## <Thema / slide-onderwerp>

| # | Claim/cijfer | Waarde | Jaar | Bron | Betrouwbaarheid | Viz? |
|---|--------------|--------|------|------|-----------------|------|
| T1.1 | Aantal eenzame 75-plussers in NL | 630.000 | 2024 | [CBS Statline](https://...) | hoog | kpi |
| T1.2 | Zorgkosten per eenzame oudere | €2.100/jr | 2023 | [RIVM](https://...) | middel | chart |
```

- **Betrouwbaarheid**: hoog (primaire bron/CBS/peer-reviewed), middel (sectorrapport,
  onderzoeksbureau), laag (nieuwsbericht, enkele casus), aanname (geen bron).
- **Viz?**: markeer welke regels zich lenen voor visualisatie en met welk component:
  `kpi` (big numbers/stat-banner), `chart` (native chart via chartspec), `proces`, `schema`, of `-`.
  Dit voedt de storyboard-stap van `sfnl-deck-design` direct.
- Sluit af met een sectie **Gaten en aannames**: wat is niet gevonden, welke aannames zijn
  gedaan, en wat de gebruiker eventueel zelf moet aanleveren.

## Stap 4: Handoff

Geef het dossierpad door aan de narrative-stap van `sfnl-deck`. Vanaf dat moment gelden twee
regels voor de rest van de pipeline:

1. Elk cijfer op een slide verwijst naar een dossierregel (bijv. `T1.1`); zet de bronvermelding
   in de speaker notes van de slide, niet op de slide zelf, tenzij de gebruiker bronnen op de
   slide wil.
2. De proof-stap (`sfnl-deck-proof`) controleert de slides tegen het dossier; cijfers die niet
   in het dossier staan blokkeren de oplevering.
