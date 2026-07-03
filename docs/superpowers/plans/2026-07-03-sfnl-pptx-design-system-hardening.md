# SFNL PPTX Design System Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the `sfnl-pptx` plugin so generated decks look deliberate, consultant-grade, and SFNL-branded instead of AI-sloppy, while also folding in the dogfooding reliability lessons.

**Architecture:** Introduce an "editorial kadergrid" design approach as the default content-slide system: larger Lato-led typography, strong colored frames and bands, fewer decorative dash dependencies, company-required ALL CAPS titles/subtitles with better typographic handling, and explicit pattern rules that force one full-canvas exhibit per slide. Keep official cover/divider/quote archetypes intact, but add preflight and guidance so generated content slides use the new system consistently.

**Tech Stack:** Python tests with `pytest`/`python-pptx`, Node build layer with `pptxgenjs`/Playwright, HTML/CSS slide source, markdown skills/reference docs.

---

## Design Direction

The new default style is **editorial kadergrid**:

- Body copy uses Lato at **16pt default**, with 14pt only for dense tables/matrices and 18pt for sparse explanation.
- ALL CAPS titles and subtitles remain mandatory as a company requirement. The improvement is typographic: use Lato/Montserrat-led content-slide titles, larger size, more breathing room, and short action titles so caps read as brand voice rather than shouting.
- Gotham Bold is restricted to official archetype title slots, big numbers, and very short display moments. Content-slide titles move away from Gotham Bold unless conversion tests prove this breaks brand QA.
- The orange dash stops being the main visual device. It remains as a small brand marker where useful, but slides should be carried by colored frames, bands, rule lines, and full-height panels.
- Layouts use hard-edged editorial structure: colored sidebars, top bands, section labels, framed evidence blocks, full-width matrices, and boxed conclusions.
- Cards become flatter and more purposeful: 4pt radius max, clearer borders, fewer pale floating rectangles.
- Multi-color use is semantic, not decorative: orange = recommendation/result, royal/sky = system/process, emerald = managed/positive, grapefruit = risk/leak.

## Research Synthesis: Anti-Slop Rules

Sources used to refine this plan:

- Nielsen Norman Group on visual hierarchy: hierarchy is built with color/contrast, scale, and grouping; busy layouts with equal-weight elements lose focus; use the squint test to verify hierarchy. Source: https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
- Nielsen Norman Group on aesthetic/minimalist design: visual quality matters for trust, but every low-information element competes with useful content; communicate rather than decorate. Source: https://www.nngroup.com/articles/aesthetic-minimalist-design/
- Microsoft PowerPoint accessibility guidance: use sufficient contrast, larger sans-serif text, whitespace, unique titles, readable order, and do not rely on color alone. Source: https://support.microsoft.com/en-US/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities
- W3C WCAG 2.2 contrast guidance: normal text needs 4.5:1 contrast; large text has a 3:1 threshold; thin fonts can appear lower contrast in practice. Source: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- U.S. Web Design System typography guidance: readable text needs medium density and deliberate line-height. Source: https://designsystem.digital.gov/components/typography/
- AutoPresent slide-generation research: structured, programmatic slide generation and iterative refinement are stronger than raw end-to-end image generation for editable slides. Source: https://arxiv.org/abs/2501.00912
- Contemporary anti-slop commentary: generic AI output reads as low-effort; anti-slop work foregrounds craft, specificity, texture, and technical/specialist visual codes. Sources: https://www.vogue.com/article/the-anti-ai-slop-playbook and https://www.theguardian.com/technology/2026/jun/08/anti-slop-ai-art

Translate those sources into plugin rules:

1. **Specificity over polish.** Each slide must include a domain-specific artifact: a formula, process map, evidence row, source-backed number, decision table, risk register, or mechanism diagram. Generic icon rows and vague three-card layouts fail review.
2. **One reading order.** Each slide declares a primary takeaway, secondary support, and tertiary metadata. If the squint test cannot identify those levels, the slide fails.
3. **Readable by construction.** Default body copy is 16pt Lato; dense areas may go to 14pt only with a reason. 12pt is for labels, axes, or metadata, not body prose.
4. **ALL CAPS with restraint.** Titles/subtitles stay ALL CAPS because this is a company requirement. To avoid the AI-slop/all-caps wall effect, titles must be short, Lato/Montserrat-led, high-contrast, and surrounded by enough whitespace.
5. **Color never carries meaning alone.** Every color-coded status also needs text, position, label, or shape.
6. **Frames are structural, not decorative.** A colored frame must encode a role: result, risk, mechanism, evidence, decision, or ask.
7. **Iterative visual refinement is required.** The generator should produce a diagnostic screenshot/contact sheet and run an anti-slop checklist before claiming visual progress, even when PowerPoint COM is unavailable.

## File Structure

- Modify `sfnl-pptx/engine/web/sfnl.css`: base typography, chrome styles, frame utilities, card styling, larger readable text scale.
- Modify `sfnl-pptx/engine/web/scaffold.html`: new default content-slide skeleton with frame-first structure.
- Modify `sfnl-pptx/engine/web/patterns.md`: replace card-heavy snippets with editorial kadergrid patterns.
- Modify `sfnl-pptx/engine/reference/brand.md`: document the new typography and color-use rules.
- Modify `sfnl-pptx/engine/reference/authoring-guide.md`: add render fallback status and archetype-slot preflight rules.
- Modify `sfnl-pptx/skills/sfnl-deck-design/SKILL.md`: force storyboard decisions to name frame type, density, typography scale, semantic colors, and archetype slot fit.
- Modify `sfnl-pptx/skills/sfnl-deck/SKILL.md`: update pipeline rules to require the editorial system and degraded render status.
- Modify `sfnl-pptx/skills/sfnl-deck-review/SKILL.md`: review against the new visual rubric and handle render unavailable explicitly.
- Modify `sfnl-pptx/skills/sfnl-deck-proof/SKILL.md`: make `render unavailable = GEBLOKKEERD` explicit.
- Modify `sfnl-pptx/skills/sfnl-deck-research/SKILL.md`: standardize viz enum and T-ID rules.
- Modify `sfnl-pptx/engine/web/build/chart_spec.js`: add documented neutral chart alias support or clear error guidance.
- Modify `sfnl-pptx/tests/test_web_build.py`: update expectations from "Gotham + dash" to "readable title + frame marker".
- Modify `sfnl-pptx/tests/test_skills.py`: assert new docs mention editorial frame system, render blocked status, and archetype-slot preflight.
- Add `sfnl-pptx/tests/test_design_system_css.py`: lightweight CSS/documentation regression tests.
- Add `sfnl-pptx/tests/test_chart_colors.py`: chart color alias/enumeration tests.
- Add `sfnl-pptx/tests/fixtures/webdeck-editorial/`: one small fixture deck using the new pattern system.

## Task 1: Lock the New Visual Contract in Tests

**Files:**
- Create: `sfnl-pptx/tests/test_design_system_css.py`
- Modify: `sfnl-pptx/tests/test_web_build.py`

- [ ] **Step 1: Add CSS regression tests**

Create `sfnl-pptx/tests/test_design_system_css.py`:

```python
from pathlib import Path

CSS = Path(__file__).resolve().parents[1] / "engine" / "web" / "sfnl.css"
PATTERNS = Path(__file__).resolve().parents[1] / "engine" / "web" / "patterns.md"


def test_body_copy_defaults_to_readable_lato_scale():
    css = CSS.read_text(encoding="utf-8")
    assert 'font-family: "Lato Light"' in css
    assert "font-size: 16pt" in css
    assert ".body-dense" in css and "font-size: 14pt" in css


def test_editorial_frame_utilities_exist():
    css = CSS.read_text(encoding="utf-8")
    for selector in (".frame-panel", ".frame-band", ".frame-sidebar", ".evidence-box", ".verdict-box"):
        assert selector in css


def test_dash_is_not_the_only_brand_marker():
    css = CSS.read_text(encoding="utf-8")
    assert ".dash" in css
    assert ".frame-accent" in css
    assert ".slide-title" in css


def test_patterns_document_editorial_kadergrid():
    text = PATTERNS.read_text(encoding="utf-8").lower()
    assert "editorial kadergrid" in text
    assert "16pt" in text
    assert "squint test" in text
    assert "all caps" in text
    assert "kader" in text
```

- [ ] **Step 2: Run the new tests and verify they fail**

Run: `pytest sfnl-pptx/tests/test_design_system_css.py -v`

Expected: failures for missing `16pt`, missing frame utilities, `squint test`, and `editorial kadergrid`.

- [ ] **Step 3: Update web build test expectations**

In `sfnl-pptx/tests/test_web_build.py`, replace the old `test_title_chrome_lands_on_content_slide` and `test_orange_dash_shape_present` assertions with expectations that allow the new title/font system:

```python
def test_title_chrome_lands_on_content_slide(built):
    slide = list(built.slides)[1]
    titles = [s for s in slide.shapes if s.has_text_frame and "DRIE CIJFERS" in s.text_frame.text]
    assert titles, "title text missing"
    assert titles[0].top < Inches(0.9)
    fonts = {r.font.name for p in titles[0].text_frame.paragraphs for r in p.runs}
    assert fonts & {"Lato Light", "Montserrat Light"}
    assert titles[0].text_frame.text == titles[0].text_frame.text.upper()


def test_content_slide_has_brand_frame_marker(built):
    slide = list(built.slides)[1]
    xml = slide._element.xml
    assert any(color in xml for color in ("F87F4F", "3B62C1", "45B6E2", "6AC6BA", "F95D63"))
```

- [ ] **Step 4: Run affected tests and verify expected failures**

Run: `pytest sfnl-pptx/tests/test_web_build.py sfnl-pptx/tests/test_design_system_css.py -v`

Expected: CSS tests still fail until implementation; existing build tests should still build the fixture.

## Task 2: Implement the Editorial Kadergrid CSS

**Files:**
- Modify: `sfnl-pptx/engine/web/sfnl.css`
- Modify: `sfnl-pptx/engine/web/scaffold.html`

- [ ] **Step 1: Update the base typography**

Change the editable part of `sfnl.css` so content slides default to larger Lato:

```css
body {
  width: 720pt; height: 405pt;
  background: var(--sfnl-white);
  font-family: "Lato Light", "Lato", Arial, sans-serif;
  font-size: 16pt; color: var(--sfnl-dark-slate);
  line-height: 1.22;
  display: flex; flex-direction: column;
}
h1, h2, h3 { font-family: "Lato Light", "Lato", Arial, sans-serif; color: var(--sfnl-navy); }
.display, .big-number { font-family: "Gotham Bold", Arial, sans-serif; }
.quiet { font-family: "Montserrat Light", "Montserrat", Arial, sans-serif; }
```

- [ ] **Step 2: Replace chrome dependency with frame-friendly chrome**

Update the chrome block in `sfnl.css`:

```css
.chrome-header { margin: 26pt 26pt 0 26pt; display: flex; flex-direction: column; gap: 6pt; }
.slide-title {
  font-family: "Lato Light", "Lato", Arial, sans-serif;
  font-size: 22pt;
  line-height: 1.08;
  letter-spacing: 0;
  color: var(--sfnl-navy);
}
.slide-subtitle {
  font-family: "Montserrat Light", "Montserrat", Arial, sans-serif;
  font-size: 12pt;
  color: var(--sfnl-dark-slate);
}
.dash { width: 18pt; height: 2pt; background: var(--sfnl-orange); margin-top: 2pt; }
.frame-accent { height: 5pt; background: var(--sfnl-orange); }
```

- [ ] **Step 3: Add frame utilities**

Append these utilities below the existing helpers:

```css
.content { flex: 1; display: flex; gap: 14pt; margin: 14pt 26pt 38pt 26pt; min-height: 0; }
.col { display: flex; flex-direction: column; gap: 10pt; flex: 1; min-height: 0; }
.frame-panel { border: 2pt solid var(--sfnl-navy); border-radius: 2pt; padding: 12pt 14pt; background: var(--sfnl-white); }
.frame-panel.orange { border-color: var(--sfnl-orange); }
.frame-panel.royal { border-color: var(--sfnl-royal); }
.frame-panel.emerald { border-color: var(--sfnl-emerald); }
.frame-panel.grapefruit { border-color: var(--sfnl-grapefruit); }
.frame-band { padding: 8pt 12pt; background: var(--sfnl-navy); color: var(--sfnl-white); }
.frame-band p, .frame-band h2, .frame-band h3 { color: var(--sfnl-white); }
.frame-sidebar { width: 112pt; padding: 12pt; background: var(--sfnl-orange); }
.frame-sidebar p, .frame-sidebar h2, .frame-sidebar h3 { color: var(--sfnl-white); }
.evidence-box { border-left: 6pt solid var(--sfnl-royal); background: var(--sfnl-grey-95); padding: 10pt 12pt; }
.verdict-box { background: var(--sfnl-orange); border-radius: 2pt; padding: 14pt; }
.verdict-box p, .verdict-box h2, .verdict-box h3 { color: var(--sfnl-white); }
.card { background: var(--sfnl-grey-95); border-radius: 2pt; padding: 12pt 14pt; flex: 1; }
.card-accent { background: var(--sfnl-orange-tint80); border-top: 4pt solid var(--sfnl-orange); }
.big-number { font-size: 34pt; color: var(--sfnl-orange); line-height: 1; }
.label {
  font-family: "Montserrat Light", "Montserrat", Arial, sans-serif;
  font-size: 10pt; color: var(--sfnl-dark-slate); letter-spacing: 0;
}
.kicker {
  font-family: "Montserrat Light", "Montserrat", Arial, sans-serif;
  font-size: 10pt; color: var(--sfnl-dark-slate); letter-spacing: 0;
}
.body-dense { font-size: 14pt; line-height: 1.16; }
.body-large { font-size: 18pt; line-height: 1.18; }
```

- [ ] **Step 4: Update the scaffold**

Modify `sfnl-pptx/engine/web/scaffold.html` to demonstrate the new frame-first default:

```html
<main class="content">
  <div class="frame-sidebar">
    <p class="label" style="color: #FEFFFF;">KADER</p>
    <p>Gebruik dit vlak voor de centrale lens of conclusie.</p>
  </div>
  <div class="col">
    <div class="frame-panel royal" style="flex: 1;">
      <p>Vrije compositie: vervang dit door een volledige exhibit met heldere kaders, grotere Lato-tekst en semantische kleurvlakken.</p>
    </div>
  </div>
</main>
```

- [ ] **Step 5: Run CSS tests**

Run: `pytest sfnl-pptx/tests/test_design_system_css.py -v`

Expected: all tests pass.

## Task 3: Rewrite the Pattern Cookbook Around Kaders

**Files:**
- Modify: `sfnl-pptx/engine/web/patterns.md`

- [ ] **Step 1: Replace the opening principles**

At the top of `patterns.md`, add:

```markdown
# SFNL layout patterns — editorial kadergrid

Default style: every content slide has a deliberate frame structure. Avoid loose pale cards floating in whitespace. Use one full-canvas exhibit with colored kaders, bands, sidebars, evidence boxes, and clear hierarchy.

- Body text is normally 16pt Lato Light; use 18pt for sparse explanatory slides and 14pt only for dense matrices.
- Titles and subtitles remain ALL CAPS because this is a company requirement; keep them short and spacious so the caps read as brand voice.
- Gotham Bold is reserved for big numbers, official archetype slots, and short display emphasis. Do not use it as the default body/title voice.
- The orange dash is a brand marker, not the composition. The slide should still work if the dash is removed.
- Use 2pt square-ish frames and colored bands more often than soft cards.
- Semantic color: orange = recommendation/result, royal/sky = process/system, emerald = managed/positive, grapefruit = risk/leak.
- Run the squint test: blurred or viewed small, the primary takeaway should still be the strongest element, followed by support and metadata.
- Every frame must have a role: evidence, mechanism, risk, decision, result, or ask. Decoration-only frames fail review.
```

- [ ] **Step 2: Replace KPI pattern with framed KPI band**

Add this snippet:

```html
<div class="col" style="gap: 10pt;">
  <div class="frame-band"><p class="body-large">De businesscase draait op één hard criterium: vermeden escalatie.</p></div>
  <div class="col" style="flex-direction: row; gap: 10pt;">
    <div class="frame-panel royal" style="flex: 1;"><p class="big-number">8.400</p><p class="label">JONGEREN</p><p>Beginnende betalingsachterstand.</p></div>
    <div class="frame-panel" style="flex: 1;"><p class="big-number" style="color: var(--sfnl-navy);">€ 4.700</p><p class="label">SCHULD</p><p>Gemiddeld bij 21 jaar.</p></div>
    <div class="verdict-box" style="flex: 1;"><p class="big-number" style="color: #FEFFFF;">€ 12.000</p><p class="label" style="color: #FEFFFF;">VERMEDEN KOSTEN</p><p>Per voorkomen wettelijk traject.</p></div>
  </div>
</div>
```

- [ ] **Step 3: Add patterns for sidebar, evidence stack, and verdict**

Add sections named:

```markdown
## Sidebar + exhibit
## Evidence stack met gekleurde kaders
## Verdict met ask-blok
## Risicomatrix met functionele kleur
## Chart + conclusieband
```

Each section must include a complete HTML snippet using `frame-sidebar`, `frame-panel`, `frame-band`, `evidence-box`, or `verdict-box`.

- [ ] **Step 4: Remove guidance that over-centers cards and dashes**

Edit existing examples so they no longer describe the dash as mandatory visual center and no longer default every repeated element to `.card`. Keep `.card` only as a lower-emphasis fallback.

- [ ] **Step 5: Run docs regression**

Run: `pytest sfnl-pptx/tests/test_design_system_css.py sfnl-pptx/tests/test_skills.py -v`

Expected: CSS tests pass; skill tests may still fail until doc updates in later tasks.

## Task 4: Update Brand and Authoring Docs

**Files:**
- Modify: `sfnl-pptx/engine/reference/brand.md`
- Modify: `sfnl-pptx/engine/reference/authoring-guide.md`

- [ ] **Step 1: Update typography guidance in `brand.md`**

Replace the typography bullets with:

```markdown
- **Lato Light is the default slide voice** for content slides. Body copy is normally 16pt; use 18pt for sparse explanatory slides and 14pt only for dense matrices or labels.
- **Gotham Bold is display-only**: official archetype slots, big numbers, and short emphasis. Do not use Gotham Bold as the default content-slide title/body style.
- **Montserrat Light is secondary**: labels, metadata, small section markers.
- Titles and subtitles remain ALL CAPS across content slides and official archetypes because this is a company requirement. Content-slide action titles may use Lato Light or Montserrat Light; they still need strong hierarchy, enough whitespace, and readable line lengths.
```

- [ ] **Step 2: Update composition guidance in `brand.md`**

Add:

```markdown
**Editorial kadergrid:** content slides should be framed by visible structure: colored sidebars, top/bottom bands, evidence boxes, full-width matrices, or verdict panels. The orange dash is a minor brand marker, not the main composition. Avoid pale floating card rows unless the cards form a full exhibit.
```

- [ ] **Step 3: Add archetype-slot preflight to `authoring-guide.md`**

Add to the archetypes section:

```markdown
Before choosing a cover/divider/quote archetype, compare required text fields with `assets/chrome/manifest.json`. If the slide needs title + subtitle + metadata, choose a variant with those slots or move metadata to notes. Do not add extra text boxes to official archetype slides unless the manifest explicitly provides a matching slot.
```

- [ ] **Step 4: Add render-unavailable protocol to `authoring-guide.md`**

Add to the visual loop section:

```markdown
If `python -m scripts.render --check` reports PowerPoint COM unavailable, the build is not visually cleared. You may create HTML screenshots as a diagnostic fallback, but the status remains `GEBLOKKEERD OP RENDER` until a PowerPoint render succeeds. Report the skipped render explicitly in build QA, review, and proof.
```

- [ ] **Step 5: Run documentation tests**

Run: `pytest sfnl-pptx/tests/test_skills.py sfnl-pptx/tests/test_design_system_css.py -v`

Expected: tests pass after corresponding skill assertions are added in Task 6.

## Task 5: Fix Chart Color Semantics

**Files:**
- Modify: `sfnl-pptx/engine/web/build/chart_spec.js`
- Create: `sfnl-pptx/tests/test_chart_colors.py`
- Modify: `sfnl-pptx/engine/reference/authoring-guide.md`

- [ ] **Step 1: Add failing tests for neutral aliases**

Create `sfnl-pptx/tests/test_chart_colors.py`:

```python
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "engine" / "web" / "build"


def test_chart_spec_accepts_neutral_alias():
    script = """
    const { chartArgs } = require('./chart_spec');
    const palette = require('../../assets/palette.json');
    const spec = { type: 'column', colors: ['neutral', 'orange'], series: [
      { name: 'A', labels: ['M1'], values: [1] },
      { name: 'B', labels: ['M1'], values: [2] }
    ]};
    const out = chartArgs(spec, palette, 'orange');
    console.log(JSON.stringify(out.options.chartColors));
    """
    res = subprocess.run(["node", "-e", script], cwd=BUILD, capture_output=True, text=True, timeout=30)
    assert res.returncode == 0, res.stderr
    colors = json.loads(res.stdout)
    assert colors[0] == "233348"
    assert colors[1] == "F87F4F"
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `pytest sfnl-pptx/tests/test_chart_colors.py -v`

Expected: failure because `neutral` is unknown.

- [ ] **Step 3: Implement aliases in `chart_spec.js`**

Change `colorHex`:

```javascript
const COLOR_ALIASES = {
  neutral: 'dark slate',
  grey: 'dark slate',
  gray: 'dark slate',
  risk: 'grapefruit',
  positive: 'emerald',
  result: 'orange',
};

function colorHex(palette, name) {
  const resolved = COLOR_ALIASES[name] || name;
  const slot = palette.by_name[resolved];
  if (!slot) {
    const allowed = [...Object.keys(palette.by_name), ...Object.keys(COLOR_ALIASES)].join(', ');
    throw new Error(`unknown color name "${name}" (allowed: ${allowed})`);
  }
  return palette.by_slot[slot].hex.toUpperCase();
}
```

- [ ] **Step 4: Document aliases**

In `authoring-guide.md`, extend the chart color section:

```markdown
Chart colors accept palette names plus aliases: `neutral`/`grey`/`gray` → `dark slate`, `result` → `orange`, `risk` → `grapefruit`, `positive` → `emerald`.
```

- [ ] **Step 5: Run tests**

Run: `pytest sfnl-pptx/tests/test_chart_colors.py sfnl-pptx/tests/test_web_build.py -v`

Expected: pass.

## Task 6: Update Skills to Generate Better Storyboards

**Files:**
- Modify: `sfnl-pptx/skills/sfnl-deck-design/SKILL.md`
- Modify: `sfnl-pptx/skills/sfnl-deck/SKILL.md`
- Modify: `sfnl-pptx/skills/sfnl-deck-review/SKILL.md`
- Modify: `sfnl-pptx/skills/sfnl-deck-proof/SKILL.md`
- Modify: `sfnl-pptx/tests/test_skills.py`

- [ ] **Step 1: Add skill tests**

Append to `sfnl-pptx/tests/test_skills.py`:

```python
def test_design_skill_requires_editorial_kadergrid():
    text = (SKILLS / "sfnl-deck-design" / "SKILL.md").read_text(encoding="utf-8").lower()
    for needle in ("editorial kadergrid", "frame", "16pt", "squint test", "all caps", "gotham bold"):
        assert needle in text


def test_review_and_proof_block_when_render_unavailable():
    review = (SKILLS / "sfnl-deck-review" / "SKILL.md").read_text(encoding="utf-8").lower()
    proof = (SKILLS / "sfnl-deck-proof" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "render unavailable" in review or "render niet beschikbaar" in review
    assert "geblokkeerd" in proof and ("render unavailable" in proof or "render niet beschikbaar" in proof)


def test_deck_design_mentions_archetype_slot_preflight():
    text = (SKILLS / "sfnl-deck-design" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "manifest.json" in text
    assert "slot" in text
```

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest sfnl-pptx/tests/test_skills.py -v`

Expected: new tests fail.

- [ ] **Step 3: Update `sfnl-deck-design` storyboard table**

Add fields to the storyboard table:

```markdown
| `frame model` | editorial kadergrid choice: sidebar, banded exhibit, full matrix, verdict box, evidence stack, chart + conclusion band, or official archetype |
| `type scale` | body density: 18pt sparse / 16pt default / 14pt dense; justify any 14pt use |
| `font emphasis` | where Gotham Bold is allowed: big number, official archetype slot, or none |
| `slot fit` | for cover/divider/quote: required text fields vs. manifest slots; choose another archetype if fields do not fit |
| `anti-slop check` | domain-specific artifact, primary/secondary/tertiary hierarchy, no generic decoration, no color-only meaning, squint-test result |
```

- [ ] **Step 4: Add design rules to `sfnl-deck-design`**

Add:

```markdown
Default content-slide approach is editorial kadergrid, not loose cards. Every content slide must name its frame model. Prefer colored frames, bands, sidebars, evidence boxes, and verdict blocks. The dash is not a composition. Body copy should be 16pt Lato by default; use 18pt for sparse slides and 14pt only for dense matrices. Titles/subtitles remain ALL CAPS as a company requirement, but should use Lato/Montserrat where possible and stay short. Gotham Bold is display-only. Every content slide must pass the anti-slop check: domain-specific artifact, clear primary/secondary/tertiary hierarchy, no generic decoration, no color-only meaning, and squint-test pass.
```

- [ ] **Step 5: Update review/proof render unavailable status**

In `sfnl-deck-review/SKILL.md`, add:

```markdown
If `scripts.render --check` reports PowerPoint COM unavailable, do not mark the review clear. HTML screenshots may be used as a diagnostic fallback, but final status is `GEBLOKKEERD: render niet beschikbaar`.
```

In `sfnl-deck-proof/SKILL.md`, add:

```markdown
Geen PowerPoint-render = verdict `GEBLOKKEERD`. A fallback based on HTML screenshots or text QA must be listed under `Niet uitgevoerd` and cannot be called ready for delivery.
```

- [ ] **Step 6: Run skill tests**

Run: `pytest sfnl-pptx/tests/test_skills.py -v`

Expected: pass.

## Task 7: Standardize Research and Outline Handoff

**Files:**
- Modify: `sfnl-pptx/skills/sfnl-deck-research/SKILL.md`
- Modify: `sfnl-pptx/skills/sfnl-deck-outline/SKILL.md`
- Modify: `sfnl-pptx/skills/sfnl-deck-retro/SKILL.md`
- Modify: `sfnl-pptx/tests/test_skills.py`

- [ ] **Step 1: Add tests for handoff rules**

Append:

```python
def test_research_skill_standardizes_ids_and_viz_enum():
    text = (SKILLS / "sfnl-deck-research" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "t#.#" in text
    for needle in ("funnel", "timeline", "matrix", "scenario", "quote"):
        assert needle in text


def test_outline_skill_has_consistency_rules_section():
    text = (SKILLS / "sfnl-deck-outline" / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "cross-slide" in text or "consistentieregels" in text
```

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest sfnl-pptx/tests/test_skills.py -v`

Expected: new tests fail.

- [ ] **Step 3: Update research skill**

Add:

```markdown
Use stable row IDs in the format `T<slide-number>.<row-number>` when the dossier follows a known slide list. Every downstream number, claim, and visual candidate refers to these IDs.

Viz enum: `kpi`, `chart`, `proces`, `funnel`, `timeline`, `matrix`, `scenario`, `quote`, `schema`, `-`. This list is shared with `sfnl-deck-design`; use these exact labels unless a new label is added to both docs.
```

- [ ] **Step 4: Update outline skill**

Add an output section:

```markdown
## Cross-slide consistentieregels

List any invariant the build/proof stage must preserve, e.g. "slides 6, 11 and 13 all use the cautious scenario value €1.01m". These are not open questions; they are proof obligations.
```

- [ ] **Step 5: Run tests**

Run: `pytest sfnl-pptx/tests/test_skills.py -v`

Expected: pass.

## Task 8: Add an Editorial Fixture Deck

**Files:**
- Create: `sfnl-pptx/tests/fixtures/webdeck-editorial/deck.json`
- Create: `sfnl-pptx/tests/fixtures/webdeck-editorial/slides/01-cover.html`
- Create: `sfnl-pptx/tests/fixtures/webdeck-editorial/slides/02-frame-kpi.html`
- Create: `sfnl-pptx/tests/fixtures/webdeck-editorial/slides/03-chart-verdict.html`
- Modify: `sfnl-pptx/tests/test_web_build.py`

- [ ] **Step 1: Create fixture deck.json**

Use:

```json
{
  "title": "EDITORIAL FIXTURE",
  "slug": "webdeck-editorial",
  "language": "nl",
  "author": "Social Finance NL",
  "accent": "orange",
  "hooks": null,
  "slides": [
    { "file": "slides/01-cover.html", "chrome": "none", "notes": "Bron: R1" },
    { "file": "slides/02-frame-kpi.html", "chrome": "light", "notes": "Bron: R2, R3" },
    { "file": "slides/03-chart-verdict.html", "chrome": "light", "notes": "Bron: R4",
      "charts": [{ "placeholder": "chart-main", "type": "column",
        "series": [{ "name": "Instroom", "labels": ["M1", "M2"], "values": [20, 28] },
                   { "name": "Uitstroom", "labels": ["M1", "M2"], "values": [0, 4] }],
        "axis": { "catTitle": "Maand", "valTitle": "Aantal" },
        "colors": ["neutral", "result"] }] }
  ]
}
```

- [ ] **Step 2: Create fixture slides**

Use existing `cover-01` for slide 1. For slides 2 and 3, use `frame-sidebar`, `frame-panel`, `frame-band`, and `verdict-box`. Keep text short enough to avoid overflow.

- [ ] **Step 3: Add build test**

In `test_web_build.py`, add:

```python
def test_editorial_fixture_builds(tmp_path):
    ws = _workspace(tmp_path, "webdeck-editorial")
    res = _build(ws)
    assert res.returncode == 0, res.stderr + res.stdout
    prs = Presentation(str(ws / "webdeck-editorial.pptx"))
    assert len(prs.slides) == 3
    assert any(s.has_chart for s in prs.slides[2].shapes)
```

- [ ] **Step 4: Run fixture test**

Run: `pytest sfnl-pptx/tests/test_web_build.py::test_editorial_fixture_builds -v`

Expected: pass.

## Task 9: Run the Full Local Validation Suite

**Files:**
- No source edits unless failures require targeted fixes.

- [ ] **Step 1: Run focused tests**

Run:

```powershell
pytest sfnl-pptx/tests/test_design_system_css.py sfnl-pptx/tests/test_chart_colors.py sfnl-pptx/tests/test_web_build.py sfnl-pptx/tests/test_skills.py -v
```

Expected: pass.

- [ ] **Step 2: Run broader plugin tests**

Run:

```powershell
pytest sfnl-pptx/tests -v
```

Expected: pass, except tests explicitly skipped because Node deps or PowerPoint COM are unavailable.

- [ ] **Step 3: Check render capability**

Run:

```powershell
cd sfnl-pptx/engine
python -m scripts.render --check
```

Expected when COM is unavailable: non-zero exit and clear output `PowerPoint COM: NOT available`. The pipeline docs must now classify this as blocked, not as passed.

- [ ] **Step 4: Build an example deck**

Run:

```powershell
node sfnl-pptx/engine/web/build/build_deck.js sfnl-pptx/tests/fixtures/webdeck-editorial
```

Expected: `webdeck-editorial.pptx` exists and has 3 slides with one chart.

## Task 10: Dogfood the New Design System

**Files:**
- Create: `output/<date>-sfnl-deck-retro-<slug>/` from a new retro run.
- No plugin source edits in this task unless a blocking crash is found.

- [ ] **Step 1: Run a new small dogfood deck**

Use `sfnl-deck-retro` on a new fictional 12-15 slide topic. Require at least:

- one KPI slide using framed KPI band,
- one chart + conclusion band,
- one risk matrix with semantic grapefruit/emerald,
- one verdict slide with `verdict-box`,
- no content slide where the orange dash is the main visual structure.

- [ ] **Step 2: Evaluate visual output against acceptance criteria**

Acceptance checklist:

- Body copy visually reads at 16pt by default, with 14pt only for dense cells/labels, not 10pt.
- Content slides are structured by frames/bands/sidebars, not loose cards.
- Gotham Bold is not used as default body/title voice on content slides.
- Titles and subtitles remain ALL CAPS, but are short, readable, and not Gotham-heavy.
- Every content slide has a domain-specific artifact and passes a squint-test review.
- The deck still passes `qa_text`.
- If PowerPoint COM is unavailable, report final status as blocked and keep HTML screenshots as diagnostic only.

- [ ] **Step 3: Update the implementation notes**

Append lessons to the new dogfood `pipeline-retro-report.md`. Do not patch plugin docs from the report automatically.

## Self-Review

- Spec coverage: covers user-requested visual direction, larger Lato typography, reduced Gotham usage, fewer dash-dependent slides, brighter frames/kaders, and the retro reliability findings.
- Placeholder scan: no TBD/TODO placeholders remain.
- Type consistency: file paths and test names are consistent across tasks.
- Scope check: this is one coherent plugin improvement project; implementation can be split by tasks if needed.
