---
name: sfnl-deck-retro
description: Interne dev-tooling skill voor sfnl-pptx-onderhouders — draait een verzonnen deck door de volledige sfnl-deck pipeline (research → outline → storyboard → build/visuele loop → review → proof) met Claude als self-approver op elk checkpoint, dispatcht na elke stage de deck-process-reviewer agent, en levert één geprioriteerd verbeterrapport over de PLUGIN zelf (skills, engine, docs) — niet over de gebouwde deck. Trigger alleen op expliciete verzoeken als "draai een dogfooding-run/retro voor sfnl-pptx", "evalueer de sfnl-deck pipeline", of "/sfnl-deck-retro". Een gewoon "maak een presentatie"-verzoek gaat altijd naar sfnl-deck, nooit naar deze skill.
---

# sfnl-deck-retro: dogfooding-run + procesevaluatie van de sfnl-pptx pipeline

Draai de volledige sfnl-deck pipeline op een verzonnen scenario en laat na elke stage de
`deck-process-reviewer` agent oordelen over het **proces** (frictie, doc-gaten,
automatiseringskansen, laat-gevangen missers) — niet over de deck. Eindigt in één
verbeterrapport over de plugin zelf. Nooit gebruiken tijdens een echte klant-deck-build.

## Stap 1: synthetische brief + workspace

Verzin een fictieve maatschappelijke organisatie en interventie (nooit een bestaande klant of
echte data). De brief moet, binnen 12-15 slides, minstens bevatten:

- Een cover en minstens één sectiedivider (officiële archetypes uit
  `engine/web/archetypes/cover-*.html` / `divider-*.html`).
- Een KPI- of grote-getallen-slide.
- Eén bespoke compositie buiten `engine/web/patterns.md` (bv. een funnel of
  geldstroomdiagram) — dit moet Track B van `sfnl-deck-design` triggeren (visuele review van
  sleutelslides via een Artifact-mockup).
- Een tijdlijn, een quote-slide (archetype `quote-*.html`), en een vergelijkingsmatrix.
- Minstens één native chart (chartspec in `deck.json`).
- Een conclusie-/verdictslide.

Kies bewust minstens 12 slides — bij ≤ 6 slides zonder bespoke compositie valt
`sfnl-deck-design` terug op Track A en wordt de visuele-review-stap nooit getest.

Maak de workspace `output/<datum>-sfnl-deck-retro-<slug>/` (slug afgeleid van het verzonnen
onderwerp, bv. `output/2026-07-04-sfnl-deck-retro-microkrediet-fonds/`). Maak hierin direct
`pipeline-retro-log.md` aan (leeg, met alleen een titelregel) — deze wordt append-only gevuld
in stap 2.

## Stap 2: doorloop de pipeline, self-approve, log per stage

Volg exact de stappen van `sfnl-pptx/skills/sfnl-deck/SKILL.md` — geen enkele aanpassing aan
die skill of aan `sfnl-deck-research`, `sfnl-deck-outline`, `sfnl-deck-design`,
`sfnl-deck-review`, of `sfnl-deck-proof`. Bij elk mens-in-de-loop-checkpoint (outline-
vragenronde, storyboard-goedkeuring, key-slide-mockup-review) beantwoordt en keurt Claude zelf goed, met een korte genoteerde reden waarom — er wordt niet op een echte gebruiker gewacht.

Voor elk van de zes stages — **research, outline, storyboard (incl. eventuele Track-B
mockup-review), HTML-authoring + build + visuele loop, review, proof** — geldt na afronding van
die stage:

1. **Noteer zelf** (één of twee regels) hoeveel iteraties de stage kostte waar dat relevant is
   (bv. aantal build/visuele-loop-rondes tot schoon, aantal outline-vragen gesteld).
2. **Dispatch `deck-process-reviewer`** via de Agent-tool met:
   - de naam van de stage,
   - de paden naar de artifacts die de stage net produceerde (bronnendossier, outline.md,
     storyboard-document, `slides/*.html` + `deck.json`, `renders/*.png`, qa_text-uitvoer,
     review-/proof-rapport — wat van toepassing is),
   - het pad naar de SKILL.md / reference-doc-sectie die de stage hoorde te sturen.
3. **Append** de ruwe output van de agent aan `pipeline-retro-log.md`, onder een kop
   `## Stage: <naam>` gevolgd door je eigen iteratienotitie uit punt 1 en daarna de agent-
   output ongewijzigd.

Ga pas door naar de volgende stage nadat de huidige stage's log-entry is weggeschreven.

## Stap 3: synthese naar eindrapport

Na de proof-stage: lees `pipeline-retro-log.md` in zijn geheel terug en schrijf
`pipeline-retro-report.md` in dezelfde workspace:

1. **Samenvatting**: het verzonnen onderwerp, aantal slides, totaal aantal build/visuele-loop-
   iteraties, en de zes doorlopen stages.
2. **Per stage**: de bevindingen uit het log, letterlijk overgenomen per bucket
   (`friction`/`doc-gap`/`automation`/`late-catch`).
3. **Geprioriteerde verbeterlijst** (`hoog`/`midden`/`laag`): dedupliceer bevindingen die door
   meerdere stages heen hetzelfde onderliggende doc-gat raken (noteer bij welke stages het
   opdook), en ken een prioriteit toe:
   - **hoog**: zou bij een echte klant-deck tot een zichtbaar defect leiden, of leidt er nu al
     structureel toe dat een latere stage moet corrigeren wat een eerdere stage had moeten
     voorkomen (elke `late-catch` opgeschaald naar minstens `midden`, naar `hoog` als het om een
     chrome/merk-defect gaat).
   - **midden**: kost herhaaldelijk frictie of iteraties maar leidt niet tot een zichtbaar
     defect.
   - **laag**: automatiseringskans of polish zonder impact op de output.
   Elke regel verwijst naar een concreet bestand (bv. `skills/sfnl-deck-outline/SKILL.md`,
   `engine/web/patterns.md`).

Rapporteer aan de gebruiker met het pad naar `pipeline-retro-report.md`. Pas hier niets
automatisch aan in de plugin — het rapport is input voor de gebruiker, geen uit te voeren taak.

## Regels

- Alleen `sfnl-pptx`. Geen wijziging aan `sfnl-deck`, `sfnl-deck-research`,
  `sfnl-deck-outline`, `sfnl-deck-design`, `sfnl-deck-review`, `sfnl-deck-proof`, of de
  build/render-engine — deze skill observeert de bestaande pipeline, ze verandert hem niet.
  (Uitzondering: als deze dogfooding-run zelf bugs blootlegt die de build laten crashen, mag je
  die crash fixen om de run te kunnen afmaken — meld dat expliciet als aparte bevinding, niet
  stilzwijgend.)
- Rapport-only: geen automatische patches op basis van het eindrapport.
- Nooit een echte klant, echte data, of een bestaand `output/`-project als onderwerp gebruiken.
- Nooit triggeren op een gewoon deck-verzoek — dat blijft altijd `sfnl-deck`.
