# Storyboard visuele review van sleutelslides — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a second, visual review checkpoint to the `sfnl-deck-design` skill — after the text
storyboard, before HTML authoring — that shows the user quick HTML mockups of a small set of
"key" slides (bespoke-composition or narratively-pivotal) in a single Artifact, and loops on
feedback until approved. Default track for every deck; a documented fallback keeps the current
fully-autonomous behavior for trivial decks or on user request.

**Architecture:** This is a documentation-only change — no application code, no build/render
engine changes. It edits the two skill instruction files that drive Claude's own behavior during
deck generation: `sfnl-pptx/skills/sfnl-deck-design/SKILL.md` (adds a new "Stap 2.5") and
`sfnl-pptx/skills/sfnl-deck/SKILL.md` (updates the one-line pipeline description of step 4 to
mention the new sub-step). Because the "engineer" executing each task is Claude following
markdown instructions, "testing" a task means verifying the file's structure and content match
the plan exactly — there is no code to compile or run.

**Tech Stack:** Markdown skill files (`SKILL.md`), consumed by Claude at runtime. No new
tooling, dependencies, or scripts.

## Global Constraints

- All prose in `sfnl-pptx/skills/*/SKILL.md` is written in Dutch, matching the existing files —
  do not introduce English prose into these files.
- Follow the existing heading style exactly: `## Stap N: <titel>` (Dutch, sentence case after the
  colon), matching the surrounding steps.
- Do not renumber or rewrite any existing step other than the one line specified in Task 2 —
  this is an additive change to `sfnl-deck-design`'s step sequence (existing Stap 3 and Stap 4
  keep their numbers and content unchanged).
- Do not touch `sfnl-pptx/engine/**`, `sfnl-pptx/README.md`, or any file other than the two named
  in "Wijzigingen aan bestaande bestanden" in the spec — confirmed via grep that no other file
  references `sfnl-deck-design`'s internal step numbers.
- Source of truth for content: `docs/superpowers/specs/2026-07-03-storyboard-visuele-review-design.md`.
  Every requirement in that spec must be traceable to a line in the edited files.

---

### Task 1: Add "Stap 2.5" to `sfnl-deck-design/SKILL.md`

**Files:**
- Modify: `sfnl-pptx/skills/sfnl-deck-design/SKILL.md:43-45` (insert new section between the end
  of Stap 2 and the `## Stap 3: self-review van het hele storyboard` heading)

**Interfaces:**
- Consumes: nothing from other tasks (first task).
- Produces: the `## Stap 2.5: visuele review van sleutelslides` heading, which Task 2 references
  by name from `sfnl-deck/SKILL.md`. Any later reader of `sfnl-deck-design/SKILL.md` must find
  this section positioned after Stap 2 and before Stap 3.

- [ ] **Step 1: Locate the exact insertion point**

Read `sfnl-pptx/skills/sfnl-deck-design/SKILL.md` and confirm these are the current lines
immediately before and after the intended insertion point:

```
Schrijf dit als markdown-tabel vóór er HTML bestaat. Bespoke composities (funnel,
geldstroom-diagram, stakeholderkaart, parallelle tijdlijnen) zijn welkom: schets regio's en
elementen in het storyboard zodat de HTML-stap mechanisch wordt. Complexe native elementen
(tabellen e.d.) kunnen via de per-deck hook — noteer dat expliciet.

## Stap 3: self-review van het hele storyboard
```

If the file has drifted from this (e.g. line numbers differ), search for the literal string
`## Stap 3: self-review van het hele storyboard` — that heading is the fixed anchor for this
insertion regardless of line-number drift.

- [ ] **Step 2: Insert the new section**

Insert the following block immediately before `## Stap 3: self-review van het hele storyboard`
(i.e. right after the `(tabellen e.d.) kunnen via de per-deck hook — noteer dat expliciet.` line):

```markdown
## Stap 2.5: visuele review van sleutelslides

Het tekst-storyboard uit stap 2 is genoeg voor rechttoe-rechtaan composities, maar niet altijd
genoeg om te beoordelen of een bespoke of narratief cruciale slide werkt. Deze stap voegt daarom
een klein, visueel reviewmoment toe vóórdat er HTML voor de hele deck wordt geschreven.

**Moduskeuze.** Standaard: **Track B** — tekst-storyboard plus visuele review van sleutelslides.
Val terug op **Track A** (alleen tekst-storyboard, direct door naar stap 3) wanneer de gebruiker
dat expliciet aangeeft, of wanneer de deck triviaal klein/eenvoudig is (richtlijn: ≤ 6 slides én
geen enkele bespoke compositie in het storyboard). Meld bij terugval kort waarom, bv. "korte deck
zonder bespoke composities, ik sla de visuele review over".

**Sleutelslides markeren.** Markeer in het storyboard een subset als "sleutelslide" op basis van
twee criteria (één is genoeg):

1. **Structureel nieuw/bespoke**: composities buiten de standaardpatronen uit `patterns.md`
   (funnel, geldstroom-diagram, stakeholderkaart, parallelle tijdlijnen, etc.).
2. **Narratief cruciaal**: slides die het kernargument dragen ongeacht layout-complexiteit (SCQA-
   complicatie/antwoord, conclusie-slide, grote-getallen/verdict-slide).

Cover-, divider- en quote-slides worden nooit gemarkeerd — die liggen al vast op officiële
archetypes. Noteer bij elke gemarkeerde rij één regel rationale: waarom deze slide een visuele
check verdient. Richtlijn: 2-5 gemarkeerde slides voor een deck van 15-25 slides — als vrijwel de
hele deck bespoke is, is dat een signaal om de storyboard-fase zelf te herzien, niet om alles te
markeren.

**Mockup: snelle standalone HTML, geen build-pipeline.** Bouw voor elke gemarkeerde slide een
snelle standalone HTML-mockup:

- Gebruikt `sfnl.css`-tokens (kleuren, typografie) voor merkherkenbaarheid.
- Benadert de compositie uit het storyboard: regio-indeling, hiërarchie, accentplek, ruwe
  chart-vorm (een placeholder-vorm volstaat, geen echte data-driven chart nodig).
- Gaat **niet** door `html2pptx`/`build_deck.js` — geen chrome-injectie, geen pixel-exacte
  fontregels, geen paginanummer/logo. Dit is een layout-schets, geen preview van de uiteindelijke
  slide. Benoem dat expliciet bij het presenteren.

**Presentatie en iteratieloop.** Zet alle gemarkeerde mockups in **één Artifact** (stacked
secties of een slide-picker binnen dezelfde pagina) en vraag in één beurt feedback op de hele
batch. Bij gevraagde wijzigingen: pas de storyboard-rij(en) én de mockup(s) aan, redeploy dezelfde
Artifact (zelfde `file_path`/URL), en vraag opnieuw — tot goedkeuring. Schrijf geen HTML voor de
uiteindelijke slide vóór deze goedkeuring.

Na goedkeuring zijn de goedgekeurde composities de autoritatieve referentie voor die slides in
stap 4. Niet-gemarkeerde slides doorlopen de bestaande stap-3-zelfreview en tekst-goedkeuring
ongewijzigd.

```

- [ ] **Step 3: Verify placement and surrounding content**

Run:
```bash
grep -n "^## Stap" "sfnl-pptx/skills/sfnl-deck-design/SKILL.md"
```

Expected output — five step headings in this exact order (line numbers will differ from this
example but the sequence and text must match):
```
17:## Stap 1: kleurmodel
25:## Stap 2: storyboard per slide
<N>:## Stap 2.5: visuele review van sleutelslides
<N>:## Stap 3: self-review van het hele storyboard
<N>:## Stap 4: vertaal naar HTML + deck.json
```

If `Stap 2.5` is missing, out of order, or duplicated, fix the insertion before continuing.

- [ ] **Step 4: Commit**

```bash
git add "sfnl-pptx/skills/sfnl-deck-design/SKILL.md"
git commit -m "docs(sfnl-pptx): add key-slide visual review step to sfnl-deck-design"
```

---

### Task 2: Reference the new sub-step from `sfnl-deck/SKILL.md`

**Files:**
- Modify: `sfnl-pptx/skills/sfnl-deck/SKILL.md:23-25` (step 4, "Storyboard", of the pipeline
  list)

**Interfaces:**
- Consumes: the `## Stap 2.5: visuele review van sleutelslides` heading name produced by Task 1
  (referenced by name only, not by line number, so Task 1 landing at a different line does not
  break this task).
- Produces: nothing consumed by later tasks (last task in this plan).

- [ ] **Step 1: Locate the exact text to replace**

Confirm this is the current text of pipeline step 4 in
`sfnl-pptx/skills/sfnl-deck/SKILL.md`:

```
4. **Storyboard.** Hand off naar `sfnl-deck-design`: per slide de layoutcompositie (regio's,
   hiërarchie, patroon uit `patterns.md` of archetype, accentgebruik, chart-kandidaten) als
   tekst-storyboard, goedgekeurd vóór er HTML wordt geschreven.
```

- [ ] **Step 2: Replace with the updated description**

Replace the block above with:

```
4. **Storyboard.** Hand off naar `sfnl-deck-design`: per slide de layoutcompositie (regio's,
   hiërarchie, patroon uit `patterns.md` of archetype, accentgebruik, chart-kandidaten) als
   tekst-storyboard, goedgekeurd vóór er HTML wordt geschreven. Voor een klein aantal
   sleutelslides (bespoke composities of narratief cruciale slides) volgt daarna een visuele
   review met snelle HTML-mockups in één Artifact (stap 2.5 van `sfnl-deck-design`), tenzij de
   deck triviaal klein is of de gebruiker dat overslaat.
```

- [ ] **Step 3: Verify the file still reads consistently**

Run:
```bash
grep -n "Storyboard\|sleutelslide" "sfnl-pptx/skills/sfnl-deck/SKILL.md"
```

Expected: the step-4 line and the new sentence both appear, step numbering (1-7) elsewhere in the
file is unchanged, and no other pipeline step mentions "sleutelslide" (this is the only place it
should appear in this file).

- [ ] **Step 4: Commit**

```bash
git add "sfnl-pptx/skills/sfnl-deck/SKILL.md"
git commit -m "docs(sfnl-pptx): mention key-slide visual review in sfnl-deck pipeline overview"
```

---

## Post-plan verification

- [ ] **Step 1: Confirm no other file needs updating**

Run:
```bash
grep -rln "sfnl-deck-design" "sfnl-pptx" --include="*.md" | grep -v "skills/sfnl-deck-design/SKILL.md\|skills/sfnl-deck/SKILL.md"
```

Expected: either no output, or output limited to files unrelated to step-by-step pipeline
descriptions (e.g. `.claude-plugin/plugin.json` is not markdown and won't match; if any `.md`
file does appear, read it and confirm it doesn't reference internal step numbers of
`sfnl-deck-design` — if it does, that's a gap this plan missed and must be patched with the same
wording used in Task 1).

- [ ] **Step 2: Re-read both edited files end to end**

Read `sfnl-pptx/skills/sfnl-deck-design/SKILL.md` and `sfnl-pptx/skills/sfnl-deck/SKILL.md` fully
and confirm: Dutch prose throughout, heading style matches surrounding sections, no leftover
merge artifacts or duplicated headings.
