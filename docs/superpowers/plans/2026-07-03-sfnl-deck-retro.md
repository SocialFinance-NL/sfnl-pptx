# sfnl-deck-retro Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new internal dev-tooling skill (`sfnl-deck-retro`) and evaluator agent
(`deck-process-reviewer`) to the `sfnl-pptx` plugin, then use them to run one full synthetic
deck through the entire `sfnl-deck` pipeline and produce a prioritized report on the plugin's
own process quality.

**Architecture:** Two new plugin files (a skill, an agent) live alongside the existing five
pipeline skills without modifying any of them. The new skill self-drives a synthetic deck
through the unmodified pipeline, self-approving every human checkpoint, dispatching the new
agent after each stage to critique process (not deck) quality, and logging findings
append-only. A final synthesis step turns the log into one report.

**Tech Stack:** Markdown skill/agent files (Claude Code plugin convention), pytest for
structural/content assertions on those files (existing `sfnl-pptx/tests/test_skills.py`
pattern).

## Global Constraints

- Scope is `sfnl-pptx` only — no generic, plugin-independent evaluator.
- Report-only — the new skill/agent never apply automated patches to the plugin.
- No modifications to `sfnl-deck`, `sfnl-deck-research`, `sfnl-deck-outline`,
  `sfnl-deck-design`, `sfnl-deck-review`, `sfnl-deck-proof`, or the build/render engine.
- Claude self-approves every human-in-the-loop checkpoint during the dogfooding run (outline
  Q&A, storyboard sign-off, key-slide mockup review) — no waiting on a real user.
- The synthetic brief is a fictional org/intervention, never real client data, at least 12
  slides, with at least one bespoke composition to trigger `sfnl-deck-design` Track B.
  (Spec: [`docs/superpowers/specs/2026-07-03-sfnl-deck-retro-design.md`](../specs/2026-07-03-sfnl-deck-retro-design.md))
- Output lands under `output/<date>-sfnl-deck-retro-<slug>/`: `pipeline-retro-log.md`
  (append-only during the run) and `pipeline-retro-report.md` (final synthesis). `output/` is
  gitignored — these are run artifacts, not committed.
- All new skill/agent prose is written in Dutch, matching the rest of the plugin's SKILL.md and
  agent files.

---

### Task 1: `deck-process-reviewer` agent

**Files:**
- Create: `sfnl-pptx/agents/deck-process-reviewer.md`
- Modify: `sfnl-pptx/tests/test_skills.py`

**Interfaces:**
- Produces: an agent named `deck-process-reviewer` (frontmatter `name: deck-process-reviewer`,
  `tools: Read, Glob, Grep`, `model: inherit`), dispatchable via the Agent tool. Task 2's skill
  dispatches it by name and relies on its four output buckets: `Friction`, `Doc gaps`,
  `Automation`, `Late-catches`.

- [ ] **Step 1: Write the failing test**

Add to `sfnl-pptx/tests/test_skills.py` (after the existing `test_all_skills_exist_with_frontmatter`):

```python
def test_deck_process_reviewer_agent_exists_with_frontmatter():
    p = PLUGIN / "agents" / "deck-process-reviewer.md"
    assert p.exists(), p
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    assert m, f"missing frontmatter in {p}"
    assert "name: deck-process-reviewer" in m.group(1)
    assert "tools:" in m.group(1)
    assert "description:" in m.group(1)
```

- [ ] **Step 2: Run test to verify it fails**

Run (from repo root): `cd sfnl-pptx && python -m pytest tests/test_skills.py::test_deck_process_reviewer_agent_exists_with_frontmatter -v`
Expected: FAIL — `AssertionError` on `assert p.exists(), p` (file does not exist yet).

- [ ] **Step 3: Create the agent file**

Create `sfnl-pptx/agents/deck-process-reviewer.md`:

```markdown
---
name: deck-process-reviewer
description: Leest de artifacts en de sturende SKILL.md/reference-doc-sectie van één zojuist afgeronde sfnl-pptx pipeline-stage en rapporteert over procesk waliteit — frictie, doc-gaten, automatiseringskansen, en defecten die een latere stage moest opvangen. Wordt gedispatcht door sfnl-deck-retro na elke stage van een dogfooding-run; nooit tijdens een echte klant-deck-build. Rapporteert alleen — past nooit bestanden aan.
tools: Read, Glob, Grep
model: inherit
---

Je bent een procesQA-specialist voor de `sfnl-pptx`-pipeline (research → outline → storyboard →
HTML/build/visuele loop → review → proof). Je wordt gedispatcht door de `sfnl-deck-retro`
dogfooding-skill nadat **één** pipeline-stage net is afgerond, met:

- de naam van de stage die net is afgerond,
- paden naar de artifacts die die stage produceerde,
- het pad naar de SKILL.md / reference-doc-sectie die de stage hoorde te sturen.

Je beoordeelt het **proces**, niet de deck. `deck-visual-reviewer` beoordeelt of de slides er
goed uitzien; jij beoordeelt of de instructies van de plugin Claude daar zonder omwegen kregen.

## Wat je doet

1. **Lees eerst de sturende doc-sectie.** Begrijp wat de SKILL.md/reference-doc van de stage
   Claude daadwerkelijk opdroeg te doen — de letterlijke instructie, niet wat je zelf van een
   goede pipeline zou verwachten.
2. **Lees de artifacts die de stage produceerde.** Vergelijk wat er werkelijk gebeurde met wat
   de doc zei dat er moest gebeuren.
3. **Classificeer elke observatie in precies één van vier buckets:**
   - `friction` — Claude moest gokken, improviseren, of zelf een ambiguïteit oplossen die de doc
     niet dekte. Benoem het concrete beslismoment en wat Claude koos.
   - `doc-gap` — een instructie was onduidelijk, ontbrak, of werd tegengesproken door wat in de
     praktijk werkte. Citeer de misleidende/ontbrekende regel als je die kunt lokaliseren.
   - `automation` — een handmatige stap die een script of template zou kunnen overnemen. Alleen
     signaleren als de stap mechanisch is (geen oordeel vereist) — bv. herhalend boilerplate,
     niet "kies het juiste layoutpatroon".
   - `late-catch` — een defect zichtbaar in de artifacts van deze stage dat de **vorige** stage
     met zijn eigen rubric had moeten afvangen maar niet deed. Benoem welke eerdere stage en
     welke check daar ontbreekt.
4. **Beoordeel geen deck-inhoud of visuele kwaliteit.** Als het storyboard goed gecomponeerd is
   maar de *instructies om het te produceren* verwarrend waren, is dat een `doc-gap`; de
   compositiekwaliteit zelf valt buiten scope — die dekken `sfnl-deck-review`,
   `sfnl-deck-proof` en `deck-visual-reviewer` op de echte pipeline.
5. **Wees specifiek en falsifieerbaar.** Elke bevinding noemt een bestand (en sectie/regel waar
   mogelijk), geen vage indruk. "Storyboard-instructies onduidelijk" is geen bevinding;
   "Stap 2 van sfnl-deck-design/SKILL.md zegt nergens of de accentkleur vóór of ná de
   patterns.md-patroonkeuze wordt bepaald — Claude koos eerst het patroon, toen de accentkleur,
   en moest één keer terug" is een bevinding.

## Wat je niet doet

- Fix de SKILL.md/reference-docs niet zelf — rapporteer bevindingen terug zodat
  `sfnl-deck-retro` ze kan loggen en synthetiseren.
- Becommentarieer geen deck-designkwaliteit, merkcompliance, of feitelijke juistheid — dat is
  het werk van de visual/review/proof-agents op een echte build, en valt buiten scope voor een
  procesreview.
- Verzin geen bevinding om een bucket te vullen; een lege bucket is een geldig, nuttig resultaat.

## Outputformaat

Eindig met een gestructureerde samenvatting:

```
## Process QA: <stage naam>
Artifacts bekeken: <paden>
Sturende doc: <pad(en)>

### Friction
- <bevinding, met het concrete beslismoment>

### Doc gaps
- <bevinding, met bestand + sectie/regel indien lokaliseerbaar>

### Automation
- <bevinding>

### Late-catches
- <bevinding, met de eerdere stage die dit had moeten afvangen>

(lege bucket: "- none observed")
```
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd sfnl-pptx && python -m pytest tests/test_skills.py::test_deck_process_reviewer_agent_exists_with_frontmatter -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add sfnl-pptx/agents/deck-process-reviewer.md sfnl-pptx/tests/test_skills.py
git commit -m "feat(sfnl-pptx): add deck-process-reviewer agent for pipeline retro"
```

---

### Task 2: `sfnl-deck-retro` skill

**Files:**
- Create: `sfnl-pptx/skills/sfnl-deck-retro/SKILL.md`
- Modify: `sfnl-pptx/tests/test_skills.py`

**Interfaces:**
- Consumes: the `deck-process-reviewer` agent from Task 1 (dispatches it by name after every
  stage).
- Produces: a skill named `sfnl-deck-retro` (frontmatter `name: sfnl-deck-retro`,
  `description:` explicitly internal/dev-tooling). Task 4 invokes it via the Skill tool.

- [ ] **Step 1: Write the failing tests**

Add to `sfnl-pptx/tests/test_skills.py`:

```python
def test_deck_retro_skill_exists_with_frontmatter():
    p = SKILLS / "sfnl-deck-retro" / "SKILL.md"
    assert p.exists(), p
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    assert m, f"missing frontmatter in {p}"
    assert "name: sfnl-deck-retro" in m.group(1)
    assert "description:" in m.group(1)


def test_deck_retro_skill_content():
    text = (SKILLS / "sfnl-deck-retro" / "SKILL.md").read_text(encoding="utf-8")
    for needle in ("deck-process-reviewer", "pipeline-retro-log.md",
                   "pipeline-retro-report.md", "zelf goed"):
        assert needle in text, needle
    assert "klant" in text.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd sfnl-pptx && python -m pytest tests/test_skills.py::test_deck_retro_skill_exists_with_frontmatter tests/test_skills.py::test_deck_retro_skill_content -v`
Expected: FAIL — `AssertionError` on `assert p.exists(), p` (skill directory does not exist yet;
the content test also errors trying to read the missing file).

- [ ] **Step 3: Create the skill file**

Create `sfnl-pptx/skills/sfnl-deck-retro/SKILL.md`:

```markdown
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
vragenronde, storyboard-goedkeuring, key-slide-mockup-review) beantwoordt en keurt Claude zelf
goed, met een korte genoteerde reden waarom — er wordt niet op een echte gebruiker gewacht.

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd sfnl-pptx && python -m pytest tests/test_skills.py -v -k deck_retro`
Expected: PASS (both `test_deck_retro_skill_exists_with_frontmatter` and
`test_deck_retro_skill_content`)

- [ ] **Step 5: Commit**

```bash
git add sfnl-pptx/skills/sfnl-deck-retro/SKILL.md sfnl-pptx/tests/test_skills.py
git commit -m "feat(sfnl-pptx): add sfnl-deck-retro dogfooding skill"
```

---

### Task 3: README dev-tooling section + doc-coverage test

**Files:**
- Modify: `sfnl-pptx/README.md`
- Modify: `sfnl-pptx/tests/test_skills.py`

**Interfaces:**
- Consumes: `sfnl-deck-retro` and `deck-process-reviewer` names from Tasks 1-2 (documented, not
  re-implemented).

- [ ] **Step 1: Write the failing test**

Add to `sfnl-pptx/tests/test_skills.py`, and update the existing `_all_docs()` helper to also
scan the new agent file:

```python
def test_readme_documents_dev_tooling():
    text = (PLUGIN / "README.md").read_text(encoding="utf-8")
    assert "sfnl-deck-retro" in text
    assert "deck-process-reviewer" in text
```

Also change the existing `_all_docs()` function (near the top of the file) from:

```python
def _all_docs():
    return list(SKILLS.rglob("SKILL.md")) + [PLUGIN / "agents" / "deck-visual-reviewer.md",
                                             PLUGIN / "README.md"]
```

to:

```python
def _all_docs():
    return list(SKILLS.rglob("SKILL.md")) + [PLUGIN / "agents" / "deck-visual-reviewer.md",
                                             PLUGIN / "agents" / "deck-process-reviewer.md",
                                             PLUGIN / "README.md"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd sfnl-pptx && python -m pytest tests/test_skills.py::test_readme_documents_dev_tooling -v`
Expected: FAIL — `AssertionError` (`"sfnl-deck-retro" in text` is false; README doesn't mention
it yet). The `_all_docs()` change itself does not need its own failing test — Task 1 already
created `deck-process-reviewer.md`, so adding it to `_all_docs()` is safe immediately and simply
extends `test_no_doc_references_retired_engine`'s coverage.

- [ ] **Step 3: Update the README**

In `sfnl-pptx/README.md`, insert a new section immediately after the existing "Triggers are
described..." line (currently line 40, right before `## How it works`):

```markdown

## Dev tooling (intern)

| Skill / agent | Doel |
|------|------|
| `sfnl-deck-retro` | Interne dogfooding-run: draait een verzonnen deck door de volledige pipeline en levert een verbeterrapport over de plugin zelf. Nooit voor een echte klant-deck. |
| `deck-process-reviewer` (agent) | Dispatched door `sfnl-deck-retro` na elke stage; beoordeelt het proces (frictie, doc-gaten, automatiseringskansen, laat-gevangen missers), niet de deck. |
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd sfnl-pptx && python -m pytest tests/test_skills.py -v`
Expected: PASS — all tests in the file, including the pre-existing ones (confirms the
`_all_docs()` change didn't break `test_no_doc_references_retired_engine`).

- [ ] **Step 5: Commit**

```bash
git add sfnl-pptx/README.md sfnl-pptx/tests/test_skills.py
git commit -m "docs(sfnl-pptx): document sfnl-deck-retro dev tooling in README"
```

---

### Task 4: Full regression check + execute the dogfooding run

**Files:** none created/modified — this task exercises Tasks 1-3's output.

**Interfaces:**
- Consumes: the `sfnl-deck-retro` skill (Task 2) and `deck-process-reviewer` agent (Task 1) as
  a black box, exactly as a real invocation would.

- [ ] **Step 1: Run the full existing test suite**

Run: `cd sfnl-pptx && python -m pytest tests -q`
Expected: PASS, all tests (no regressions from Tasks 1-3's edits to `test_skills.py`).

- [ ] **Step 2: Invoke the new skill to run the dogfooding pipeline**

This step is not a fresh-context subagent task — the dogfooding run itself involves the full
`sfnl-deck` pipeline (research, outline Q&A, storyboard, HTML authoring, `build_deck.js`,
`scripts.render` via PowerPoint COM, `scripts.qa_text`, review, proof) and needs the same
continuity of judgment a real deck build needs. Run it inline in the main session:

Invoke the Skill tool with `skill: "sfnl-deck-retro"`. Let it run to completion, self-approving
every checkpoint per the skill's Step 2. Do not intervene unless the run hits an environment
failure (e.g. `scripts.render --check` reports PowerPoint/COM unavailable) — if so, note that
prerequisite in your report to the user rather than fabricating a render pass.

- [ ] **Step 3: Verify the report artifact**

After the skill finishes, confirm the workspace it created (matching
`output/*-sfnl-deck-retro-*/`) contains both files with non-trivial content:

Run: `ls "output/"*-sfnl-deck-retro-*/pipeline-retro-log.md "output/"*-sfnl-deck-retro-*/pipeline-retro-report.md`
Expected: both files listed (exist).

Run: `grep -c "^## Stage:" "output/"*-sfnl-deck-retro-*/pipeline-retro-log.md`
Expected: `6` (one heading per pipeline stage: research, outline, storyboard, build, review,
proof).

Read `pipeline-retro-report.md` and confirm it has all three required sections: a run summary,
per-stage findings, and a prioritized (`hoog`/`midden`/`laag`) improvement list with file
references.

- [ ] **Step 4: Report to the user**

Summarize the run for the user: the synthetic topic used, slide count, how many
build/visual-loop iterations it took, and the path to `pipeline-retro-report.md`. No commit for
this task — `output/` is gitignored, and the report itself is user-facing input for their next
decision, not a plugin change.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-03-sfnl-deck-retro.md`. Two execution
options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between
tasks, fast iteration. Note: Task 4 Step 2 is a long, judgment-heavy pipeline run best suited to
running inline even under this mode — flag that when we get there.

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution
with checkpoints.

Which approach?
