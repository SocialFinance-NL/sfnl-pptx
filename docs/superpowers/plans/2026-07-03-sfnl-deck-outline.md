# sfnl-deck-outline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Insert a new interactive outline stage (`sfnl-deck-outline`) into the sfnl-deck
pipeline, between research and storyboard, per
`docs/superpowers/specs/2026-07-03-sfnl-deck-outline-design.md`.

**Architecture:** One new skill file (`sfnl-pptx/skills/sfnl-deck-outline/SKILL.md`) that owns
the scale/ambiguity assessment, the `AskUserQuestion` round, the outline document, and the
comment/approval loop. Two existing skill files get their pipeline references updated so the
new stage is wired in and the old "Narrative en titels" step is retired.

**Tech Stack:** Markdown skill files (Claude Code skill format), no code/build changes. This
project has no test runner for skill content — "testing" here means a targeted self-review
against the spec and a grep check that no stale references remain.

## Global Constraints

- All new skill prose is in Dutch, matching the existing sfnl-pptx skill files
  (`sfnl-deck`, `sfnl-deck-design`, `sfnl-deck-research` are all NL).
- Question count ceiling is **20** (not 12 — the spec was revised upward during brainstorming).
- `AskUserQuestion` allows max 4 questions per call — the skill must instruct batching in
  consecutive calls of up to 4, never claim a single call can exceed 4.
- No layout/composition detail belongs in the outline document — that stays the responsibility
  of `sfnl-deck-design` (per spec, Step 3).
- Outline file path: `output/<YYYY-MM-DD>-<slug>/outline.md` (same workspace convention already
  used for `slides/*.html` in `sfnl-deck/SKILL.md` step 5).

---

### Task 1: Create the `sfnl-deck-outline` skill

**Files:**
- Create: `sfnl-pptx/skills/sfnl-deck-outline/SKILL.md`

**Interfaces:**
- Consumes: the brief/intake text and `output/research/<slug>-dossier.md` produced by
  `sfnl-deck-research` (per `sfnl-pptx/skills/sfnl-deck-research/SKILL.md` Step 4 handoff).
- Produces: `output/<YYYY-MM-DD>-<slug>/outline.md` — consumed by `sfnl-deck-design` (Task 3
  updates that skill's "Wanneer" section to read this file).

- [ ] **Step 1: Write the skill file**

Create `sfnl-pptx/skills/sfnl-deck-outline/SKILL.md` with this exact content:

```markdown
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
```

- [ ] **Step 2: Verify no placeholders or stale references**

Run:
```
grep -n "TBD\|TODO\|placeholder-tekst" "sfnl-pptx/skills/sfnl-deck-outline/SKILL.md"
```
Expected: no output (grep exits non-zero / prints nothing).

- [ ] **Step 3: Commit**

```bash
git add sfnl-pptx/skills/sfnl-deck-outline/SKILL.md
git commit -m "feat(sfnl-pptx): add sfnl-deck-outline skill for interactive content outline"
```

---

### Task 2: Wire the new stage into `sfnl-deck/SKILL.md`

**Files:**
- Modify: `sfnl-pptx/skills/sfnl-deck/SKILL.md:12-39` (the `## Pipeline` section)

**Interfaces:**
- Consumes: nothing new (orchestration text only).
- Produces: updated step list referenced by anyone reading the sfnl-deck pipeline (Task 3 relies
  on this step numbering being final).

- [ ] **Step 1: Replace the pipeline section**

In `sfnl-pptx/skills/sfnl-deck/SKILL.md`, find this exact block (current lines 12-39):

```markdown
## Pipeline

Idee → research → narrative → storyboard → HTML+deck.json → build → visuele loop → review → proof:

1. **Intake.** Brief, outline of brondocumenten. Detecteer taal (NL/EN).
2. **Research.** Hand off naar `sfnl-deck-research`: bronnendossier (feiten, cijfers, bronnen,
   viz-kandidaten) vóór er een slide bestaat. Skip alleen wanneer de gebruiker compleet,
   gebronmerkt materiaal aanlevert — noteer dat als bron. Elk cijfer op een slide traceert naar
   een dossierregel.
3. **Narrative en titels.** Lees `engine/reference/voice.md`. SCQA-narrative, action title per
   slide, ghost-deck-test vóór het bouwen.
4. **Storyboard.** Hand off naar `sfnl-deck-design`: per slide de layoutcompositie (regio's,
   hiërarchie, patroon uit `patterns.md` of archetype, accentgebruik, chart-kandidaten) als
   tekst-storyboard, goedgekeurd vóór er HTML wordt geschreven.
5. **Auteur HTML + deck.json.** Maak de workspace `output/<YYYY-MM-DD>-<slug>/` (kopieer
   `engine/web/sfnl.css` naar `slides/`). Eén HTML-bestand per slide vanaf `engine/web/scaffold.html`
   of een archetype (`engine/web/archetypes/`); charts als `class="placeholder"` + chartspec in
   `deck.json`; speaker notes met dossier-verwijzingen in `deck.json`. Volg de harde HTML-regels
   uit de authoring guide (alle tekst in tekst-tags, geen gradients, ALL CAPS-titels getypt,
   geen logo/paginanummer in HTML).
6. **Build + visuele loop (verplicht, elke build).** `node engine/web/build/build_deck.js
   output/<datum>-<slug>`. Faalt de validatie: alle fouten in één keer fixen. Daarna renderen
   (`python -m scripts.render … renders/` vanuit `engine/`), elke PNG inspecteren of de
   `deck-visual-reviewer` dispatchen, HTML fixen, rebuilden — tot schoon. Draai ook
   `python -m scripts.qa_text` en los criticals op.
7. **Review + proof.** Hand off naar `sfnl-deck-review` (adaptieve QA) en vóór klantoplevering
   naar `sfnl-deck-proof` (volledige eindproef). Pas opleveren bij "klaar voor oplevering".
```

Replace it with:

```markdown
## Pipeline

Idee → research → outline → storyboard → HTML+deck.json → build → visuele loop → review → proof:

1. **Intake.** Brief, outline of brondocumenten. Detecteer taal (NL/EN).
2. **Research.** Hand off naar `sfnl-deck-research`: bronnendossier (feiten, cijfers, bronnen,
   viz-kandidaten) vóór er een slide bestaat. Skip alleen wanneer de gebruiker compleet,
   gebronmerkt materiaal aanlevert — noteer dat als bron. Elk cijfer op een slide traceert naar
   een dossierregel.
3. **Outline.** Hand off naar `sfnl-deck-outline`: een geschaalde vraagronde over inhoud en
   structuur (0-20 vragen, met skip-optie), gevolgd door een per-slide content-outline
   (`output/<YYYY-MM-DD>-<slug>/outline.md`) die de gebruiker becommentarieert en goedkeurt
   vóór er storyboard- of HTML-werk begint. Lees `engine/reference/voice.md` voor de
   SCQA-narrative- en action-title-regels die de outline moet volgen.
4. **Storyboard.** Hand off naar `sfnl-deck-design`: leest de goedgekeurde outline en werkt 'm
   uit tot per-slide layoutcompositie (regio's, hiërarchie, patroon uit `patterns.md` of
   archetype, accentgebruik, chart-kandidaten) als tekst-storyboard, goedgekeurd vóór er HTML
   wordt geschreven. Content- of structuurwijzigingen op dit moment gaan terug naar de outline,
   niet naar het storyboard.
5. **Auteur HTML + deck.json.** Maak de workspace `output/<YYYY-MM-DD>-<slug>/` (kopieer
   `engine/web/sfnl.css` naar `slides/`). Eén HTML-bestand per slide vanaf `engine/web/scaffold.html`
   of een archetype (`engine/web/archetypes/`); charts als `class="placeholder"` + chartspec in
   `deck.json`; speaker notes met dossier-verwijzingen in `deck.json`. Volg de harde HTML-regels
   uit de authoring guide (alle tekst in tekst-tags, geen gradients, ALL CAPS-titels getypt,
   geen logo/paginanummer in HTML).
6. **Build + visuele loop (verplicht, elke build).** `node engine/web/build/build_deck.js
   output/<datum>-<slug>`. Faalt de validatie: alle fouten in één keer fixen. Daarna renderen
   (`python -m scripts.render … renders/` vanuit `engine/`), elke PNG inspecteren of de
   `deck-visual-reviewer` dispatchen, HTML fixen, rebuilden — tot schoon. Draai ook
   `python -m scripts.qa_text` en los criticals op.
7. **Review + proof.** Hand off naar `sfnl-deck-review` (adaptieve QA) en vóór klantoplevering
   naar `sfnl-deck-proof` (volledige eindproef). Pas opleveren bij "klaar voor oplevering".
```

- [ ] **Step 2: Verify the old step 3 wording is gone**

Run:
```
grep -n "Narrative en titels" "sfnl-pptx/skills/sfnl-deck/SKILL.md"
```
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add sfnl-pptx/skills/sfnl-deck/SKILL.md
git commit -m "feat(sfnl-pptx): wire sfnl-deck-outline into the sfnl-deck pipeline"
```

---

### Task 3: Point `sfnl-deck-design` at the approved outline

**Files:**
- Modify: `sfnl-pptx/skills/sfnl-deck-design/SKILL.md:1-15` (frontmatter description + "Wanneer"
  section)

**Interfaces:**
- Consumes: `output/<YYYY-MM-DD>-<slug>/outline.md` produced by `sfnl-deck-outline` (Task 1).
- Produces: no interface change — this task only updates prose, not the storyboard table format
  or self-review checklist further down the file.

- [ ] **Step 1: Update the frontmatter description**

Find this exact line (current line 3):

```
description: Work out the visual layout of every slide in an SFNL deck before writing any HTML. Use after the narrative and action titles are drafted and before authoring slides/*.html — produces a per-slide storyboard (composition, regions, pattern/archetype, accent use, chart candidates, rationale) that gets reviewed and adjusted cheaply as text before any building happens. Triggers on "werk de layout per slide uit", "storyboard", "design plan", or as step 4 of the sfnl-deck pipeline.
```

Replace with:

```
description: Work out the visual layout of every slide in an SFNL deck before writing any HTML. Use after the outline (sfnl-deck-outline) is approved and before authoring slides/*.html — produces a per-slide storyboard (composition, regions, pattern/archetype, accent use, chart candidates, rationale) that gets reviewed and adjusted cheaply as text before any building happens. Triggers on "werk de layout per slide uit", "storyboard", "design plan", or as step 4 of the sfnl-deck pipeline.
```

- [ ] **Step 2: Update the "Wanneer" section**

Find this exact block (current lines 12-15):

```markdown
## Wanneer

Tussen narrative/titels en het schrijven van `slides/*.html`. Nooit rechtstreeks van titels
naar HTML. Lees eerst `engine/web/patterns.md` en bekijk `engine/web/archetypes/`.
```

Replace with:

```markdown
## Wanneer

Tussen de goedgekeurde outline (`sfnl-deck-outline`, `output/<YYYY-MM-DD>-<slug>/outline.md`)
en het schrijven van `slides/*.html`. Nooit rechtstreeks van outline naar HTML. Lees eerst
`engine/web/patterns.md` en bekijk `engine/web/archetypes/`.
```

- [ ] **Step 3: Verify old wording is gone**

Run:
```
grep -n "narrative/titels" "sfnl-pptx/skills/sfnl-deck-design/SKILL.md"
```
Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add sfnl-pptx/skills/sfnl-deck-design/SKILL.md
git commit -m "docs(sfnl-pptx): sfnl-deck-design reads the approved outline, not narrative notes"
```

---

## Final verification (after all tasks)

- [ ] **Step 1: Confirm all three files are consistent**

Run:
```
grep -rn "sfnl-deck-outline" sfnl-pptx/skills/
```
Expected: matches in `sfnl-deck-outline/SKILL.md` (self-reference), `sfnl-deck/SKILL.md` (step
3 + step 4 handoff note), and `sfnl-deck-design/SKILL.md` ("Wanneer" section + description).

- [ ] **Step 2: Confirm no orphaned references to the old step name**

Run:
```
grep -rn "Narrative en titels\|narrative/titels" sfnl-pptx/skills/
```
Expected: no output.
