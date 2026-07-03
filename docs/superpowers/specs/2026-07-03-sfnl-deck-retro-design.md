# sfnl-deck-retro: dogfooding-run + procesevaluatie van de sfnl-pptx pipeline

## Probleem

De sfnl-pptx pipeline (research → outline → storyboard → HTML/build/visuele loop → review →
proof) is nooit end-to-end doorlopen puur om het proces zelf te beoordelen. Losse verbeteringen
komen nu ad hoc tot stand — via losse observaties tijdens echte deck-builds, of via handmatige
notities zoals de bestaande memory-les over sfnl-pptx-lessen die naar andere plugins zijn
doorvertaald. Er is geen herhaalbare manier om de vijf pipeline-skills gezamenlijk te testen op
een synthetisch scenario en systematisch te achterhalen waar instructies onduidelijk zijn, waar
Claude moet improviseren, of waar een latere stap fouten opvangt die een eerdere stap had moeten
voorkomen.

## Doel

Een herhaalbare dogfooding-run: een nieuwe, synthetische deck-brief loopt door de volledige
sfnl-deck pipeline, met na elke stage een procesevaluatie door een gespecialiseerde agent. De
evaluaties worden aan het eind samengevoegd tot één geprioriteerd verbeterrapport over de
plugin zelf (skills, engine, docs) — niet over de gebouwde deck.

## Scope

- Alleen `sfnl-pptx`. Geen generieke, plugin-onafhankelijke evaluator.
- Rapport-only: de evaluator stelt voor, past niets automatisch aan.
- Eén dogfooding-run per invocatie van de nieuwe skill; geen wijziging aan de vijf bestaande
  pipeline-skills (`sfnl-deck`, `sfnl-deck-research`, `sfnl-deck-outline`, `sfnl-deck-design`,
  `sfnl-deck-review`, `sfnl-deck-proof`) of aan de build/render-engine.

## Synthetische brief

De nieuwe skill genereert zelf een fictieve SFNL-achtige brief (geen echte klantdata), ontworpen
om zoveel mogelijk van de plugin te raken in één deck van ~12-15 slides:

- Cover + minimaal één sectiedivider (officiële archetypes).
- Een KPI/grote-getallen-slide.
- Eén bespoke compositie buiten `patterns.md` (funnel of geldstroomdiagram) — triggert Track B
  van `sfnl-deck-design` (visuele review van sleutelslides).
- Een tijdlijn, een quote-slide, en een vergelijkingsmatrix.
- Minstens één native chart (chartspec in deck.json).
- Een conclusie-/verdict-slide.

Doelbewust groot genoeg om niet in de Track A-fallback (≤6 slides, geen bespoke composities) te
vallen.

## Uitvoering: Claude self-approve

Claude doorloopt alle mens-in-de-loop-checkpoints (outline-vragen, storyboard-goedkeuring,
mockup-review) zelf, met eigen oordeel, zodat de run in één sessie ononderbroken doorloopt. Dit
levert geen echte gebruikersfrictie op bij goedkeuringsmomenten — dat is een bewust aanvaarde
beperking van deze dogfooding-opzet, geen tekortkoming die opgelost hoeft te worden.

## Nieuwe skill: sfnl-deck-retro

Bestand: `sfnl-pptx/skills/sfnl-deck-retro/SKILL.md`.

Interne dev-tooling skill, niet klantgericht. Frontmatter-description maakt expliciet dat dit
een interne QA/dogfooding-skill is voor pluginontwikkelaars, zodat hij nooit per ongeluk
triggert op een echt klantverzoek ("maak een presentatie" moet `sfnl-deck` blijven raken, niet
deze skill).

Stappen:

1. **Genereer de synthetische brief** (zie hierboven) en start een workspace onder
   `output/<datum>-sfnl-deck-retro-<slug>/`.
2. **Doorloop de sfnl-deck pipeline** stage voor stage, zelfde volgorde als
   `sfnl-pptx/skills/sfnl-deck/SKILL.md`: research → outline → storyboard → HTML+deck.json →
   build + visuele loop → review → proof. Claude self-approvet elk checkpoint.
3. **Na elke stage: dispatch `deck-process-reviewer`** (zie hieronder) met:
   - de naam van de stage,
   - paden naar de artifacts die de stage net produceerde (bronnendossier, outline.md,
     storyboard, HTML/deck.json, renders, qa_text-output, review-/proof-rapport),
   - de SKILL.md/reference-doc-sectie die de stage hoorde te sturen.
4. **Log toevoegen.** Elke evaluatie wordt direct weggeschreven naar
   `output/<datum>-sfnl-deck-retro-<slug>/pipeline-retro-log.md` (append-only), zodat een
   onderbreking geen eerdere bevindingen kost.
5. **Synthese.** Na de laatste stage (proof) leest Claude het volledige log terug en
   dedupliceert/prioriteert de bevindingen tot het eindrapport (zie Output).

## Nieuwe agent: deck-process-reviewer

Bestand: `sfnl-pptx/agents/deck-process-reviewer.md`. Tools: `Read, Glob, Grep` (alleen-lezen,
zelfde toolprofiel als `deck-visual-reviewer`, maar dan voor tekst-artifacts/proces in plaats van
gerenderde PNG's).

Beoordeelt per stage het **proces**, niet de deck-kwaliteit:

- **Frictie**: waar moest Claude gokken, improviseren, of ambiguïteit zelf oplossen omdat de
  docs het niet dekten?
- **Doc-gaten**: instructies die onduidelijk, ontbrekend, of tegengesproken door de praktijk
  waren (wat werkte, staat niet zo in de SKILL.md/reference-doc).
- **Automatiseringskansen**: een handmatige stap die een script zou kunnen overnemen.
- **Laat-gevangen missers**: een defect dat pas in een latere stage (bv. review/proof) werd
  gevonden, terwijl de producerende stage dit met zijn eigen rubric had moeten afvangen.

Output per dispatch: korte, genummerde bevindingen met een severity-achtig label
(`friction` / `doc-gap` / `automation` / `late-catch`) en een concrete verwijzing naar het
bestand (en waar mogelijk sectie/regel) dat de bevinding raakt.

## Output: eindrapport

`output/<datum>-sfnl-deck-retro-<slug>/pipeline-retro-report.md`:

- Korte samenvatting van de dogfooding-run (brief, aantal slides, aantal build/visuele-loop-
  iteraties, totale doorlooptijd in stages).
- Per pipeline-stage: de bevindingen uit het log, ontdubbeld.
- Eén geprioriteerde lijst verbetervoorstellen (`hoog` / `midden` / `laag`), elk met een
  concrete verwijzing naar het te wijzigen bestand (bv. `skills/sfnl-deck-outline/SKILL.md`,
  `engine/web/patterns.md`). Geen automatische patches — de gebruiker beslist wat opgevolgd
  wordt.

## Wijzigingen aan bestaande bestanden

- `sfnl-pptx/README.md`: nieuwe rij/sectie die `sfnl-deck-retro` als interne dev-tooling-skill
  noemt (los van de klantgerichte skills-tabel), zodat het doel duidelijk is voor toekomstige
  onderhouders.
- Geen wijzigingen aan `sfnl-deck`, `sfnl-deck-research`, `sfnl-deck-outline`,
  `sfnl-deck-design`, `sfnl-deck-review`, `sfnl-deck-proof`, of de build/render-engine.

## Out of scope

- Geen generieke/plugin-onafhankelijke evaluator (mogelijk toekomstig vervolg voor
  sfnl-offerte/sfnl-mbc/sfnl-aanbesteding, expliciet niet nu).
- Geen automatisch toegepaste patches/PR's vanuit het rapport.
- Geen wijziging aan bestaande pipeline-skills of engine.
- Geen herhaalde/geplande runs (bv. cron) — dit is een los te starten skill, geen achtergrondtaak.
