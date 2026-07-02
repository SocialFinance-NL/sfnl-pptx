# sfnl-pptx v2 — html2pptx Generation Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the deck-spec → python-pptx generation core with an HTML-per-slide → html2pptx/PptxGenJS pipeline (SFNL design system, deck.json manifest, mandatory visual loop), per the approved spec `docs/superpowers/specs/2026-07-02-sfnl-pptx-html2pptx-redesign-design.md`.

**Architecture:** Claude authors one HTML file per slide (720pt × 405pt) on a shared SFNL scaffold plus a `deck.json` manifest; a Node script (`build_deck.js`) converts slides via a vendored, Windows-adapted `html2pptx.js` into one `.pptx` with editable text/shapes and native PptxGenJS charts, then the existing COM renderer drives a mandatory render-inspect-fix loop. Python keeps only `render.py`, `qa_text.py`, `extract_palette.py`.

**Tech Stack:** Node.js (pptxgenjs, playwright/Chromium, sharp, react-icons, react, react-dom), Python (python-pptx, pywin32, pytest), PowerPoint COM for rendering.

## Global Constraints

- Slide canvas: HTML body exactly `width: 720pt; height: 405pt` (16:9); PptxGenJS layout `LAYOUT_16x9` (10in × 5.625in). The sjabloon is 13.33in × 7.5in — all chrome geometry from it is scaled by **0.75**.
- Brand palette (from `engine/assets/palette.json`, single source of truth): navy `#201B5C`, dark slate `#233348`, orange `#F87F4F`, grapefruit `#F95D63`, royal `#3B62C1`, sky `#45B6E2`, emerald `#6AC6BA`, white `#FEFFFF`/`#FFFFFF`.
- Exactly three brand fonts: **Gotham Bold** (display/headings), **Lato Light** (body/labels), **Montserrat Light** (secondary/quiet). Titles and subtitles ALL CAPS (typed in caps in HTML source). Fonts installed locally, never embedded.
- html2pptx rules: all text inside `<p>`/`<h1>`-`<h6>`/`<ul>`/`<ol>`; no CSS gradients ever (pre-render PNGs via Sharp); backgrounds/borders/shadows only on `<div>`; text > 12pt must end ≥ 0.5in above the bottom edge.
- PptxGenJS colors: hex **without** `#` (with `#` corrupts the file).
- One accent per deck by default (`deck.json` `accent`); color encodes meaning.
- Deck workspace: `output/<YYYY-MM-DD>-<slug>/` containing `slides/*.html`, `assets/`, `deck.json`, `renders/`, and `<slug>.pptx`.
- Rendering: PowerPoint COM only (`engine/scripts/render.py`), no LibreOffice/poppler.
- Visual loop is mandatory for every build, not just sensitive slides.
- Retired (must be deleted, not adapted): `build_from_spec.py`, `spec.py`, `components.py`, `icons.py`, `extract_layouts.py`, `colors.py`, `layouts.json`, `assets/components/index.json`, deck-spec tests and fixtures. `extract_palette.py`, `palette.json`, `render.py`, `qa_text.py` (adapted), `office/template.py` stay. `sfnl-template.pptx` stays as visual reference only.
- All paths below are relative to repo root `C:\Users\XavierFriesen\.projects SFNL\Powerpoints design\` unless absolute. Python tests run from `sfnl-pptx/`: `python -m pytest tests/ -q` (tests/conftest.py puts `engine/` on sys.path). Node tests run from `sfnl-pptx/engine/web/build/`: `npm test`.

## Chrome geometry (extracted from the sjabloon, scaled ×0.75)

| Element | Sjabloon (in) | Our canvas | Notes |
|---|---|---|---|
| Title | x 0.48, y 0.60, 24pt Gotham Bold | left 26pt, top 32pt, 18pt | navy, ALL CAPS |
| Subtitle | y 1.04, 14pt Montserrat Light | ~top 56pt (flow), 10.5pt | dark slate, ALL CAPS |
| Orange dash | x 0.56, y 1.72, 0.28×0.06in | 15pt × 3.2pt at ~y 93pt (flow) | orange |
| Logo (media/image7.png) | 0.36, 7.07, 1.10×0.30in | x 0.27, y 5.3025, w 0.825, h 0.225 (inches) | injected natively by build_deck.js |
| Page number | 12.60, 7.12, 0.62×0.24in | x 9.45, y 5.34, w 0.465, h 0.18 (inches) | Montserrat Light 9pt orange, right-aligned, injected natively |

---

### Task 1: Node build workspace + vendored, Windows-adapted html2pptx.js

**Files:**
- Create: `sfnl-pptx/engine/web/build/package.json`
- Create: `sfnl-pptx/engine/web/build/html2pptx.js` (vendored copy of `C:\Users\XavierFriesen\.claude\skills\pptx-official\scripts\html2pptx.js`, then adapted)
- Create: `sfnl-pptx/engine/web/build/test/html2pptx.test.js`
- Create: `sfnl-pptx/engine/web/build/test/fixtures/minimal.html`
- Create: `sfnl-pptx/engine/web/build/test/fixtures/overflow.html`
- Modify: `.gitignore` (add `node_modules/`)

**Interfaces:**
- Produces: `html2pptx(htmlFile, pres, options)` → `{ slide, placeholders: [{id,x,y,w,h}] }`, requireable from `engine/web/build/`. Default `tmpDir` works on Windows. All later tasks require it as `require('./html2pptx')`.

- [ ] **Step 1: Create package.json and install dependencies**

```json
{
  "name": "sfnl-web-build",
  "private": true,
  "description": "SFNL html2pptx deck build layer",
  "scripts": {
    "test": "node --test test/"
  },
  "dependencies": {
    "playwright": "^1.53.0",
    "pptxgenjs": "^4.0.1",
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "react-icons": "^5.5.0",
    "sharp": "^0.34.2"
  }
}
```

Add `node_modules/` on its own line to `.gitignore`. Then run:

```powershell
cd "sfnl-pptx\engine\web\build"
npm install
npx playwright install chromium
```

Expected: install succeeds; `node_modules/` exists; commit `package.json` + `package-lock.json`.

- [ ] **Step 2: Write the failing test**

`test/fixtures/minimal.html`:

```html
<!DOCTYPE html>
<html>
<head>
<style>
  html { background: #ffffff; }
  body { width: 720pt; height: 405pt; margin: 0; padding: 0; background: #ffffff;
         font-family: Arial, sans-serif; display: flex; flex-direction: column; }
  .wrap { margin: 40pt; }
  h1 { font-size: 18pt; color: #201B5C; }
  p { font-size: 10pt; color: #233348; }
</style>
</head>
<body>
  <div class="wrap">
    <h1>MINIMAL SLIDE</h1>
    <p>Een regel tekst.</p>
    <div id="chart-1" class="placeholder" style="width: 300pt; height: 180pt;"></div>
  </div>
</body>
</html>
```

`test/fixtures/overflow.html` (identical head/body CSS, but content that overflows):

```html
<!DOCTYPE html>
<html>
<head>
<style>
  html { background: #ffffff; }
  body { width: 720pt; height: 405pt; margin: 0; padding: 0; background: #ffffff;
         font-family: Arial, sans-serif; display: flex; flex-direction: column; }
</style>
</head>
<body>
  <div style="margin: 20pt;">
    <div style="height: 500pt; background: #F87F4F;"><p>TE HOOG</p></div>
  </div>
</body>
</html>
```

`test/html2pptx.test.js`:

```javascript
const test = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const pptxgen = require('pptxgenjs');
const html2pptx = require('../html2pptx');

const fixture = (name) => path.join(__dirname, 'fixtures', name);

test('converts a minimal HTML slide and reports placeholders', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  const { slide, placeholders } = await html2pptx(fixture('minimal.html'), pptx);
  assert.ok(slide, 'slide created');
  assert.equal(placeholders.length, 1);
  assert.equal(placeholders[0].id, 'chart-1');
  const out = path.join(os.tmpdir(), `sfnl-min-${process.pid}.pptx`);
  await pptx.writeFile({ fileName: out });
  assert.ok(fs.existsSync(out));
  fs.unlinkSync(out);
});

test('overflowing slide fails loudly with overflow message', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  await assert.rejects(() => html2pptx(fixture('overflow.html'), pptx), /overflows body/);
});
```

- [ ] **Step 3: Run test to verify it fails**

Run (from `sfnl-pptx/engine/web/build`): `npm test`
Expected: FAIL — `Cannot find module '../html2pptx'`.

- [ ] **Step 4: Vendor and adapt html2pptx.js**

Copy `C:\Users\XavierFriesen\.claude\skills\pptx-official\scripts\html2pptx.js` (978 lines) to `sfnl-pptx/engine/web/build/html2pptx.js` unchanged, then make exactly these Windows adaptations:

1. Top of file, extend requires (after `const sharp = require('sharp');`):

```javascript
const os = require('os');
const { pathToFileURL, fileURLToPath } = require('url');

// Convert a file:// URL (as produced by the browser DOM) back to an OS path.
function fileUrlToPath(src) {
  return src.startsWith('file://') ? fileURLToPath(src) : src;
}
```

2. Line ~898, tmpDir default: replace `tmpDir = process.env.TMPDIR || '/tmp',` with:

```javascript
    tmpDir = process.env.TMPDIR || os.tmpdir(),
```

3. Line ~924, page navigation: replace `await page.goto(`file://${filePath}`);` with:

```javascript
      await page.goto(pathToFileURL(filePath).href);
```

4. In `addBackground` (~line 123): replace the ternary

```javascript
    let imagePath = slideData.background.path.startsWith('file://')
      ? slideData.background.path.replace('file://', '')
      : slideData.background.path;
```

with:

```javascript
    let imagePath = fileUrlToPath(slideData.background.path);
```

5. In `addElements` image branch (~line 136): replace
`let imagePath = el.src.startsWith('file://') ? el.src.replace('file://', '') : el.src;` with:

```javascript
      let imagePath = fileUrlToPath(el.src);
```

Do not change anything else (font handling already reduces a font stack to its first family at lines ~784/~823).

- [ ] **Step 5: Run tests to verify they pass**

Run: `npm test`
Expected: 2 passing.

- [ ] **Step 6: Commit**

```powershell
git add -A "sfnl-pptx/engine/web/build" .gitignore
git commit -m "feat(sfnl-pptx): vendor html2pptx with Windows adaptations and Node build workspace"
```

---

### Task 2: Brand-font spike (risk gate from the spec)

**Files:**
- Create: `sfnl-pptx/engine/web/build/test/fixtures/spike-fonts.html`
- Create: `sfnl-pptx/engine/web/build/test/fonts.test.js`

**Interfaces:**
- Consumes: `html2pptx` from Task 1.
- Produces: a go/no-go decision on using locally installed Gotham Bold / Lato Light / Montserrat Light in Playwright + pptx runs. If NO-GO: adopt the spec's fallback (render HTML with metric-compatible web-safe stacks, write brand font names into pptx runs via a post-processing map) and record that decision in the plan file before continuing.

- [ ] **Step 1: Write the spike slide**

`test/fixtures/spike-fonts.html`:

```html
<!DOCTYPE html>
<html>
<head>
<style>
  html { background: #ffffff; }
  body { width: 720pt; height: 405pt; margin: 0; padding: 0; background: #ffffff;
         display: flex; flex-direction: column; }
  .wrap { margin: 32pt 26pt; }
  h1 { font-family: "Gotham Bold", Arial, sans-serif; font-size: 18pt; color: #201B5C; margin: 0; }
  p.body { font-family: "Lato Light", Arial, sans-serif; font-size: 11pt; color: #233348; }
  p.quiet { font-family: "Montserrat Light", Arial, sans-serif; font-size: 10.5pt; color: #233348; }
</style>
</head>
<body>
  <div class="wrap">
    <h1>SPIKE: GOTHAM BOLD KOPTEKST OVER TWEE REGELS OM AFBREKEN TE TESTEN MET LANGE WOORDEN</h1>
    <p class="body">Lato Light lopende tekst met een langere zin zodat regelafbreking en metrics zichtbaar worden in de conversie naar PowerPoint.</p>
    <p class="quiet">MONTSERRAT LIGHT SECUNDAIRE REGEL IN ALL CAPS</p>
  </div>
</body>
</html>
```

- [ ] **Step 2: Write the failing test** — `test/fonts.test.js`:

```javascript
const test = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const os = require('node:os');
const pptxgen = require('pptxgenjs');
const html2pptx = require('../html2pptx');

test('brand fonts land as fontFace in the pptx XML', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  await html2pptx(path.join(__dirname, 'fixtures', 'spike-fonts.html'), pptx);
  const out = path.join(os.tmpdir(), `sfnl-spike-${process.pid}.pptx`);
  await pptx.writeFile({ fileName: out });
  // pptx is a zip; slide XML must reference the exact brand font names
  const AdmLike = require('node:child_process');
  const py = AdmLike.spawnSync('python', ['-c', `
import zipfile, sys
x = zipfile.ZipFile(sys.argv[1]).read('ppt/slides/slide1.xml').decode('utf-8')
for f in ("Gotham Bold", "Lato Light", "Montserrat Light"):
    assert f in x, f
print("ok")
`, out], { encoding: 'utf-8' });
  assert.match(py.stdout, /ok/, py.stderr);
});
```

- [ ] **Step 3: Run and make pass**

Run: `npm test` — the fonts test fails until fixture+conversion behave; fix only real defects (e.g. font stack leakage) inside the vendored file if they appear. Expected end state: PASS.

- [ ] **Step 4: Visual verification (manual gate)**

```powershell
cd "sfnl-pptx\engine\web\build"
node -e "const p=require('pptxgenjs');const h=require('./html2pptx');(async()=>{const x=new p();x.layout='LAYOUT_16x9';await h('test/fixtures/spike-fonts.html',x);await x.writeFile({fileName:'../../../../output/spike-fonts.pptx'});})()"
cd "..\..\.."
python -m scripts.render ..\output\spike-fonts.pptx ..\output\spike-render
```

(run render from `sfnl-pptx/engine` so `scripts.render` resolves). Read `output/spike-render/slide_01.png` and check: Gotham Bold headline (not a serif/Arial substitute), no clipped text, wrapping matches intent. If the render shows substituted fonts or bad metrics → adopt the spec fallback and document it here before proceeding.

- [ ] **Step 5: Commit**

```powershell
git add -A "sfnl-pptx/engine/web/build/test"
git commit -m "test(sfnl-pptx): brand-font spike passes html2pptx conversion (risk gate)"
```

---

### Task 3: Token generation — palette.json → sfnl.css tokens + tokens.json

**Files:**
- Create: `sfnl-pptx/engine/web/build/generate_tokens.js`
- Create: `sfnl-pptx/engine/web/sfnl.css` (marker block only; Task 4 adds the rest)
- Create: `sfnl-pptx/engine/web/build/test/tokens.test.js`
- Create: `sfnl-pptx/tests/test_tokens.py`
- Generated (committed): `sfnl-pptx/engine/web/tokens.json`

**Interfaces:**
- Consumes: `engine/assets/palette.json` (`by_slot`, `by_name` — see current file).
- Produces:
  - CSS custom properties in `sfnl.css` between `/* @tokens:begin */` and `/* @tokens:end */`: `--sfnl-<name>` for the 8 base colors (names from `by_name`, spaces → dashes), plus for each non-white color `--sfnl-<name>-tint80|-tint60|-tint40|-shade25`, plus greys `--sfnl-grey-95|-grey-85|-grey-70` (tints of dark slate).
  - `engine/web/tokens.json`: `{ "allowed_hex": ["201B5C", ...] }` — every token hex, uppercase, no `#` (consumed by qa_text in Task 9).
  - Node exports: `applyLum(hex, lumMod, lumOff)`, `tint(hex, pct)`, `shade(hex, pct)`, `buildTokens(palette)`.

- [ ] **Step 1: Write the failing Node test** — `test/tokens.test.js`:

```javascript
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { tint, shade, buildTokens } = require('../generate_tokens');

test('tint/shade boundary behaviour', () => {
  assert.equal(tint('F87F4F', 100), 'FFFFFF');
  assert.equal(tint('F87F4F', 0), 'F87F4F');
  assert.equal(shade('F87F4F', 100), '000000');
  assert.equal(shade('F87F4F', 0), 'F87F4F');
});

test('tint lightens monotonically, shade darkens, deterministic', () => {
  const lum = (hex) => ['0,2', '2,4', '4,6'].map(r => parseInt(hex.slice(...r.split(',').map(Number)), 16)).reduce((a, b) => a + b, 0);
  assert.ok(lum(tint('3B62C1', 80)) > lum(tint('3B62C1', 40)));
  assert.ok(lum(tint('3B62C1', 40)) > lum('3B62C1'));
  assert.ok(lum(shade('3B62C1', 25)) < lum('3B62C1'));
  assert.equal(tint('6AC6BA', 60), tint('6AC6BA', 60));
});

test('buildTokens covers every brand color with tints and greys', () => {
  const palette = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', '..', 'assets', 'palette.json'), 'utf-8'));
  const tokens = buildTokens(palette);
  for (const name of ['navy', 'dark-slate', 'orange', 'grapefruit', 'royal', 'sky', 'emerald', 'white']) {
    assert.ok(tokens[`--sfnl-${name}`], `missing --sfnl-${name}`);
  }
  assert.ok(tokens['--sfnl-orange-tint80']);
  assert.ok(tokens['--sfnl-navy-shade25']);
  assert.ok(tokens['--sfnl-grey-95']);
  assert.ok(!tokens['--sfnl-white-tint80'], 'white gets no tints');
});
```

- [ ] **Step 2: Run to verify failure** — `npm test` → FAIL: cannot find `../generate_tokens`.

- [ ] **Step 3: Implement `generate_tokens.js`**

```javascript
#!/usr/bin/env node
/* Generate SFNL brand tokens from engine/assets/palette.json into
   engine/web/sfnl.css (between @tokens markers) and engine/web/tokens.json.
   Tints/shades replicate PowerPoint lumMod/lumOff: HSL luminance scaling. */
const fs = require('fs');
const path = require('path');

const WEB = path.join(__dirname, '..');
const PALETTE = path.join(WEB, '..', 'assets', 'palette.json');

function hexToHsl(hex) {
  const r = parseInt(hex.slice(0, 2), 16) / 255;
  const g = parseInt(hex.slice(2, 4), 16) / 255;
  const b = parseInt(hex.slice(4, 6), 16) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  const l = (max + min) / 2;
  if (max === min) return { h: 0, s: 0, l };
  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h;
  if (max === r) h = (g - b) / d + (g < b ? 6 : 0);
  else if (max === g) h = (b - r) / d + 2;
  else h = (r - g) / d + 4;
  return { h: h * 60, s, l };
}

function hslToHex(h, s, l) {
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = l - c / 2;
  const [r, g, b] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x]
    : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
  const to = (v) => Math.round((v + m) * 255).toString(16).padStart(2, '0').toUpperCase();
  return to(r) + to(g) + to(b);
}

function applyLum(hex, lumMod, lumOff) {
  const { h, s, l } = hexToHsl(hex.toUpperCase());
  return hslToHex(h, s, Math.min(1, Math.max(0, l * lumMod + lumOff)));
}
const tint = (hex, pct) => applyLum(hex, (100 - pct) / 100, pct / 100);
const shade = (hex, pct) => applyLum(hex, (100 - pct) / 100, 0);

function buildTokens(palette) {
  const tokens = {};
  const hexOf = (name) => palette.by_slot[palette.by_name[name]].hex.toUpperCase();
  for (const name of Object.keys(palette.by_name)) {
    const key = name.replace(/\s+/g, '-');
    const hex = hexOf(name);
    tokens[`--sfnl-${key}`] = hex;
    if (name === 'white') continue;
    tokens[`--sfnl-${key}-tint80`] = tint(hex, 80);
    tokens[`--sfnl-${key}-tint60`] = tint(hex, 60);
    tokens[`--sfnl-${key}-tint40`] = tint(hex, 40);
    tokens[`--sfnl-${key}-shade25`] = shade(hex, 25);
  }
  const slate = hexOf('dark slate');
  tokens['--sfnl-grey-95'] = tint(slate, 95);
  tokens['--sfnl-grey-85'] = tint(slate, 85);
  tokens['--sfnl-grey-70'] = tint(slate, 70);
  return tokens;
}

function main() {
  const palette = JSON.parse(fs.readFileSync(PALETTE, 'utf-8'));
  const tokens = buildTokens(palette);
  const block = ['/* @tokens:begin (generated by build/generate_tokens.js — do not edit by hand) */', ':root {']
    .concat(Object.entries(tokens).map(([k, v]) => `  ${k}: #${v};`))
    .concat(['}', '/* @tokens:end */']).join('\n');
  const cssPath = path.join(WEB, 'sfnl.css');
  let css = fs.existsSync(cssPath) ? fs.readFileSync(cssPath, 'utf-8') : '/* @tokens:begin */\n/* @tokens:end */\n';
  css = css.replace(/\/\* @tokens:begin[\s\S]*?@tokens:end \*\//, block);
  fs.writeFileSync(cssPath, css);
  fs.writeFileSync(path.join(WEB, 'tokens.json'),
    JSON.stringify({ allowed_hex: [...new Set(Object.values(tokens))].sort() }, null, 2));
  console.log('wrote', cssPath, 'and tokens.json');
}

if (require.main === module) main();
module.exports = { applyLum, tint, shade, buildTokens };
```

Create the initial `engine/web/sfnl.css` containing exactly:

```css
/* @tokens:begin */
/* @tokens:end */
```

Then run: `node generate_tokens.js` — sfnl.css token block populated, `tokens.json` written.

- [ ] **Step 4: Run Node tests** — `npm test` → tokens tests PASS.

- [ ] **Step 5: Write pytest guard** — `sfnl-pptx/tests/test_tokens.py`:

```python
"""sfnl.css tokens must match palette.json (spec §6 test requirement)."""
import json
import re
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1] / "engine"


def _palette():
    return json.loads((ENGINE / "assets" / "palette.json").read_text(encoding="utf-8"))


def test_css_base_tokens_match_palette():
    css = (ENGINE / "web" / "sfnl.css").read_text(encoding="utf-8")
    pal = _palette()
    for name, slot in pal["by_name"].items():
        var = "--sfnl-" + name.replace(" ", "-")
        hexv = pal["by_slot"][slot]["hex"]
        assert re.search(re.escape(var) + r":\s*#" + hexv, css, re.I), f"{var} missing/mismatched"


def test_tokens_json_covers_palette():
    allowed = set(json.loads((ENGINE / "web" / "tokens.json").read_text(encoding="utf-8"))["allowed_hex"])
    for info in _palette()["by_slot"].values():
        assert info["hex"].upper() in allowed
```

Run: `python -m pytest tests/test_tokens.py -q` (from `sfnl-pptx/`) → PASS.

- [ ] **Step 6: Commit**

```powershell
git add -A "sfnl-pptx/engine/web" "sfnl-pptx/tests/test_tokens.py"
git commit -m "feat(sfnl-pptx): brand token generation from palette.json (css vars + tokens.json)"
```

---

### Task 4: SFNL stylesheet (chrome + typography) and scaffold.html

**Files:**
- Modify: `sfnl-pptx/engine/web/sfnl.css` (append below the token block)
- Create: `sfnl-pptx/engine/web/scaffold.html`
- Create: `sfnl-pptx/engine/web/assets/sfnl-logo.png` (extracted from the sjabloon)
- Create: `sfnl-pptx/engine/web/build/test/scaffold.test.js`

**Interfaces:**
- Consumes: tokens from Task 3; `html2pptx` from Task 1.
- Produces: CSS classes every slide uses: `.chrome-header`, `.slide-title`, `.slide-subtitle`, `.dash`, `.content`, helpers (`.card`, `.big-number`, `.label`, `.quiet`, `.bleed-navy`). `scaffold.html` as the canonical skeleton (slides `<link rel="stylesheet" href="sfnl.css">` — the css is copied into each workspace's `slides/`).

- [ ] **Step 1: Extract the logo from the sjabloon**

```powershell
cd "sfnl-pptx"
python -c "import zipfile, pathlib; pathlib.Path('engine/web/assets').mkdir(parents=True, exist_ok=True); pathlib.Path('engine/web/assets/sfnl-logo.png').write_bytes(zipfile.ZipFile('engine/assets/sfnl-template.pptx').read('ppt/media/image7.png'))"
```

Expected: `engine/web/assets/sfnl-logo.png` exists (~3 KB). Read it to confirm it is the SFNL wordmark.

- [ ] **Step 2: Write the failing Node test** — `test/scaffold.test.js`:

```javascript
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('../html2pptx');

// scaffold links sfnl.css relatively; copy both to a temp dir like a real workspace
function stageScaffold() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sfnl-scaffold-'));
  const web = path.join(__dirname, '..', '..');
  fs.copyFileSync(path.join(web, 'scaffold.html'), path.join(dir, 'slide.html'));
  fs.copyFileSync(path.join(web, 'sfnl.css'), path.join(dir, 'sfnl.css'));
  return path.join(dir, 'slide.html');
}

test('scaffold converts cleanly with title chrome', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  const { slide } = await html2pptx(stageScaffold(), pptx);
  assert.ok(slide);
  const out = path.join(os.tmpdir(), `sfnl-scaffold-${process.pid}.pptx`);
  await pptx.writeFile({ fileName: out });
  const { spawnSync } = require('node:child_process');
  const py = spawnSync('python', ['-c', `
import zipfile, sys
x = zipfile.ZipFile(sys.argv[1]).read('ppt/slides/slide1.xml').decode('utf-8')
assert "Gotham Bold" in x
assert "ACTION TITLE" in x
assert "F87F4F" in x  # orange dash shape
print("ok")
`, out], { encoding: 'utf-8' });
  assert.match(py.stdout, /ok/, py.stderr);
});
```

- [ ] **Step 3: Run to verify failure** — `npm test` → FAIL (`scaffold.html` missing).

- [ ] **Step 4: Append design-system CSS to sfnl.css** (below `/* @tokens:end */`):

```css

/* ============ SFNL design system — do edit below this line ============
   Canvas: 720pt × 405pt (pptxgenjs LAYOUT_16x9).
   Rules digest: all text in <p>/<h1>-<h6>/<ul>/<ol>; backgrounds/borders only on <div>;
   no CSS gradients (pre-render PNG via Sharp); text >12pt ends >=0.5in above bottom. */

* { box-sizing: border-box; margin: 0; padding: 0; }
html { background: #ffffff; }
body {
  width: 720pt; height: 405pt;
  background: var(--sfnl-white);
  font-family: "Lato Light", "Lato", Arial, sans-serif;
  font-size: 10pt; color: var(--sfnl-dark-slate);
  display: flex; flex-direction: column;
}
h1, h2, h3 { font-family: "Gotham Bold", Arial, sans-serif; color: var(--sfnl-navy); }
.quiet { font-family: "Montserrat Light", "Montserrat", Arial, sans-serif; }

/* ---- Fixed chrome (content slides): title block + orange dash. Logo and page
   number are injected natively by build_deck.js — never author them in HTML. ---- */
.chrome-header { margin: 32pt 26pt 0 26pt; }
.slide-title { font-size: 18pt; line-height: 1.15; letter-spacing: 0.02em; }
.slide-subtitle {
  font-family: "Montserrat Light", "Montserrat", Arial, sans-serif;
  font-size: 10.5pt; color: var(--sfnl-dark-slate); margin-top: 5pt;
}
.dash { width: 15pt; height: 3.2pt; background: var(--sfnl-orange); margin-top: 8pt; }

/* ---- Free content region: fill the canvas, no half-empty slides ---- */
.content { flex: 1; display: flex; gap: 14pt; margin: 14pt 26pt 40pt 26pt; min-height: 0; }
.col { display: flex; flex-direction: column; gap: 10pt; flex: 1; min-height: 0; }

/* ---- Helpers ---- */
.card { background: var(--sfnl-grey-95); border-radius: 6pt; padding: 12pt 14pt; flex: 1; }
.card-accent { background: var(--sfnl-orange-tint80); }
.big-number { font-family: "Gotham Bold", Arial, sans-serif; font-size: 30pt; color: var(--sfnl-orange); line-height: 1; }
.label {
  font-family: "Montserrat Light", "Montserrat", Arial, sans-serif;
  font-size: 8.5pt; color: var(--sfnl-dark-slate); letter-spacing: 0.06em;
}
.kicker { font-family: "Gotham Bold", Arial, sans-serif; font-size: 9pt; color: var(--sfnl-orange); letter-spacing: 0.1em; }

/* ---- Full-bleed archetypes (cover, divider, closing) ---- */
.bleed-navy { background: var(--sfnl-navy); }
.bleed-navy h1, .bleed-navy h2, .bleed-navy p { color: #FFFFFF; }
.bleed-center { flex: 1; display: flex; flex-direction: column; justify-content: center; margin: 0 60pt; }
```

- [ ] **Step 5: Write `scaffold.html`**

```html
<!DOCTYPE html>
<html>
<!-- SFNL slide scaffold — kopieer per slide, canvas 720pt × 405pt.
     Titels/subtitels ALTIJD in ALL CAPS typen (CSS text-transform telt niet in de conversie).
     Logo + paginanummer NIET in HTML zetten: build_deck.js voegt die native toe. -->
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="sfnl.css">
</head>
<body>
  <header class="chrome-header">
    <h1 class="slide-title">ACTION TITLE IN ALL CAPS</h1>
    <p class="slide-subtitle">OPTIONELE SUBTITEL — VERWIJDER DEZE REGEL ALS ER GEEN IS</p>
    <div class="dash"></div>
  </header>
  <main class="content">
    <div class="col">
      <p>Vrije compositie: vervang dit door de exhibit van deze slide (flex/grid, kaarten, cijfers, placeholder voor een chart). Vul de volledige hoogte.</p>
    </div>
  </main>
</body>
</html>
```

- [ ] **Step 6: Run tests** — `npm test` → scaffold test PASS.
- [ ] **Step 7: Commit**

```powershell
git add -A "sfnl-pptx/engine/web"
git commit -m "feat(sfnl-pptx): SFNL design system stylesheet, scaffold, and extracted logo"
```

---

### Task 5: Slide archetypes + patterns.md cookbook

**Files:**
- Create: `sfnl-pptx/engine/web/archetypes/cover.html`
- Create: `sfnl-pptx/engine/web/archetypes/divider.html`
- Create: `sfnl-pptx/engine/web/archetypes/quote.html`
- Create: `sfnl-pptx/engine/web/archetypes/closing.html`
- Create: `sfnl-pptx/engine/web/archetypes/stat-banner.html`
- Create: `sfnl-pptx/engine/web/patterns.md`
- Create: `sfnl-pptx/engine/web/build/test/archetypes.test.js`

**Interfaces:**
- Consumes: `sfnl.css` classes from Task 4; `html2pptx` from Task 1.
- Produces: five copy-paste archetype HTML files (validated to convert cleanly) and the layout cookbook. Archetype chrome contract for deck.json (Task 8): cover/closing → `"chrome": "none"`, divider → `"chrome": "dark"`, quote/stat-banner → default `"light"`.

- [ ] **Step 1: Write the failing test** — `test/archetypes.test.js`:

```javascript
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('../html2pptx');

const WEB = path.join(__dirname, '..', '..');
const NAMES = ['cover', 'divider', 'quote', 'closing', 'stat-banner'];

test('every archetype converts without validation errors', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sfnl-arch-'));
  fs.copyFileSync(path.join(WEB, 'sfnl.css'), path.join(dir, 'sfnl.css'));
  for (const name of NAMES) {
    fs.copyFileSync(path.join(WEB, 'archetypes', `${name}.html`), path.join(dir, `${name}.html`));
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    await assert.doesNotReject(() => html2pptx(path.join(dir, `${name}.html`), pptx), `${name} failed`);
  }
});
```

Run `npm test` → FAIL (archetypes missing).

- [ ] **Step 2: Write the archetypes** (all link `sfnl.css` the same way as scaffold; head omitted below is identical: `<meta charset="utf-8"><link rel="stylesheet" href="sfnl.css">`).

`cover.html`:

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><link rel="stylesheet" href="sfnl.css"></head>
<body class="bleed-navy">
  <div class="bleed-center">
    <p class="kicker">SOCIAL FINANCE NL</p>
    <h1 style="font-size: 30pt; margin-top: 10pt;">DEKTITEL IN ALL CAPS<br>OVER TWEE REGELS</h1>
    <div class="dash" style="margin-top: 14pt;"></div>
    <p class="quiet" style="margin-top: 14pt; font-size: 11pt; color: #FFFFFF;">ONDERTITEL — KLANT — DATUM</p>
  </div>
</body>
</html>
```

`divider.html`:

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><link rel="stylesheet" href="sfnl.css"></head>
<body class="bleed-navy">
  <div class="bleed-center">
    <p class="kicker">DEEL 1</p>
    <h1 style="font-size: 26pt; margin-top: 8pt;">SECTIETITEL IN ALL CAPS</h1>
    <div class="dash" style="margin-top: 12pt;"></div>
  </div>
</body>
</html>
```

`quote.html`:

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><link rel="stylesheet" href="sfnl.css"></head>
<body>
  <div class="bleed-center" style="margin: 0 80pt;">
    <div class="dash" style="width: 24pt; height: 4pt;"></div>
    <h1 style="font-size: 20pt; margin-top: 16pt; line-height: 1.35;">"Het citaat staat hier, in Gotham Bold, groot genoeg om de hele slide te dragen."</h1>
    <p class="quiet" style="margin-top: 16pt; font-size: 10pt;">NAAM — ROL, ORGANISATIE</p>
  </div>
</body>
</html>
```

`closing.html` (geometric, per sjabloon closer):

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><link rel="stylesheet" href="sfnl.css"></head>
<body class="bleed-navy">
  <div style="position: absolute; right: 40pt; top: 40pt; width: 110pt; height: 110pt; border-radius: 50%; background: var(--sfnl-orange);"></div>
  <div style="position: absolute; right: 120pt; top: 170pt; width: 70pt; height: 70pt; border-radius: 50%; background: var(--sfnl-emerald);"></div>
  <div style="position: absolute; right: 60pt; bottom: 60pt; width: 46pt; height: 46pt; border-radius: 50%; background: var(--sfnl-sky);"></div>
  <div class="bleed-center" style="margin-right: 260pt;">
    <h1 style="font-size: 28pt;">DANK</h1>
    <div class="dash" style="margin-top: 12pt;"></div>
    <p class="quiet" style="margin-top: 14pt; font-size: 10pt; color: #FFFFFF;">NAAM · E-MAIL · SOCFIN.NL</p>
  </div>
</body>
</html>
```

`stat-banner.html` (content chrome + dark band with big numbers):

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><link rel="stylesheet" href="sfnl.css"></head>
<body>
  <header class="chrome-header">
    <h1 class="slide-title">DE RESULTATEN IN DRIE CIJFERS</h1>
    <div class="dash"></div>
  </header>
  <main class="content">
    <div style="flex: 1; display: flex; gap: 14pt; background: var(--sfnl-navy); border-radius: 6pt; padding: 24pt;">
      <div style="flex: 1;">
        <p class="big-number">124</p>
        <p class="label" style="color: #FFFFFF; margin-top: 8pt;">DEELNEMERS BEREIKT</p>
      </div>
      <div style="flex: 1;">
        <p class="big-number">€ 2,4M</p>
        <p class="label" style="color: #FFFFFF; margin-top: 8pt;">MAATSCHAPPELIJKE WAARDE</p>
      </div>
      <div style="flex: 1;">
        <p class="big-number">68%</p>
        <p class="label" style="color: #FFFFFF; margin-top: 8pt;">DUURZAME UITSTROOM</p>
      </div>
    </div>
  </main>
</body>
</html>
```

- [ ] **Step 3: Write `patterns.md`** — the cookbook (fragments assume the scaffold's `<main class="content">`):

````markdown
# SFNL layout patterns — cookbook, geen catalogus

Kopieer, pas aan, componeer. Merkregels reizen mee:

- **Eén accent per deck** (default `deck.json.accent`); kleur codeert betekenis, nooit decoratie.
- **Big numbers**: groot cijfer (Gotham Bold, accentkleur), klein label eronder (Montserrat Light caps).
- **Volledige hoogte**: de content vult het canvas; een half-lege slide is een defect.
- **Ruime, gelijke marges**; chrome (titel + dash) altijd aanwezig op contentslides.
- Tekstregels: alle tekst in `<p>/<h1>-<h6>/<ul>/<ol>`; achtergrond/rand alleen op `<div>`;
  geen CSS-gradients (pre-render via Sharp); titels in ALL CAPS getypt.

## KPI-rij met grote cijfers

```html
<div class="col" style="flex-direction: row; gap: 14pt;">
  <div class="card"><p class="big-number">31%</p><p class="label" style="margin-top: 6pt;">MINDER UITVAL</p><p style="margin-top: 8pt;">Eén regel duiding bij het cijfer.</p></div>
  <div class="card"><p class="big-number">124</p><p class="label" style="margin-top: 6pt;">TRAJECTEN</p><p style="margin-top: 8pt;">Eén regel duiding.</p></div>
  <div class="card"><p class="big-number">€ 0,9M</p><p class="label" style="margin-top: 6pt;">BESPARING</p><p style="margin-top: 8pt;">Eén regel duiding.</p></div>
</div>
```

## Twee-koloms exhibit (tekst + chart)

```html
<div class="col" style="flex: 2;">
  <p class="kicker">WAT WE ZIEN</p>
  <ul style="margin-top: 6pt;"><li>Eerste observatie.</li><li>Tweede observatie.</li></ul>
</div>
<div class="col" style="flex: 3;">
  <div id="chart-main" class="placeholder" style="flex: 1;"></div>
</div>
```

Registreer `chart-main` in `deck.json` → `slides[].charts[]` (zie authoring guide).

## Swimlane-kolommen (categorie per kleur — multi-accent decks)

```html
<div class="col">
  <div style="background: var(--sfnl-grapefruit); border-radius: 4pt; padding: 6pt 10pt;"><p class="label" style="color: #FFFFFF;">VRAAGSTUK</p></div>
  <div class="card" style="background: var(--sfnl-grapefruit-tint80);"><p>Inhoud…</p></div>
</div>
<div class="col">
  <div style="background: var(--sfnl-emerald); border-radius: 4pt; padding: 6pt 10pt;"><p class="label" style="color: #FFFFFF;">ACTIVITEITEN</p></div>
  <div class="card" style="background: var(--sfnl-emerald-tint80);"><p>Inhoud…</p></div>
</div>
<div class="col">
  <div style="background: var(--sfnl-orange); border-radius: 4pt; padding: 6pt 10pt;"><p class="label" style="color: #FFFFFF;">IMPACT</p></div>
  <div class="card" style="background: var(--sfnl-orange-tint80);"><p>Inhoud…</p></div>
</div>
```

## Proces-chevrons

```html
<div class="col" style="flex-direction: row; gap: 8pt; align-items: stretch;">
  <div class="card card-accent" style="flex: 1;"><p class="kicker">STAP 1</p><p style="margin-top: 6pt;"><b>Verkennen</b></p><p>Korte omschrijving.</p></div>
  <div class="card" style="flex: 1;"><p class="kicker">STAP 2</p><p style="margin-top: 6pt;"><b>Ontwerpen</b></p><p>Korte omschrijving.</p></div>
  <div class="card" style="flex: 1;"><p class="kicker">STAP 3</p><p style="margin-top: 6pt;"><b>Uitvoeren</b></p><p>Korte omschrijving.</p></div>
</div>
```

(Voor echte pijlpunten: rasterize een chevron-PNG via Sharp in `assets/` en gebruik `<img>`.)

## 2×2-matrix

```html
<div class="col" style="display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 10pt;">
  <div class="card card-accent"><p class="kicker">HOOG / LAAG</p><p>Kwadrant.</p></div>
  <div class="card"><p class="kicker">HOOG / HOOG</p><p>Kwadrant.</p></div>
  <div class="card"><p class="kicker">LAAG / LAAG</p><p>Kwadrant.</p></div>
  <div class="card"><p class="kicker">LAAG / HOOG</p><p>Kwadrant.</p></div>
</div>
```

## Scenario-kaarten

```html
<div class="col" style="flex-direction: row;">
  <div class="card" style="border-top: 3pt solid var(--sfnl-orange);"><p class="kicker">SCENARIO A</p><p class="big-number" style="font-size: 20pt; margin-top: 6pt;">€ 1,2M</p><p style="margin-top: 6pt;">Aannames in één regel.</p></div>
  <div class="card" style="border-top: 3pt solid var(--sfnl-orange);"><p class="kicker">SCENARIO B</p><p class="big-number" style="font-size: 20pt; margin-top: 6pt;">€ 2,1M</p><p style="margin-top: 6pt;">Aannames in één regel.</p></div>
</div>
```

## Evidence stack / lagenmodel

```html
<div class="col" style="justify-content: center; gap: 6pt;">
  <div style="background: var(--sfnl-navy); border-radius: 4pt; padding: 8pt 14pt;"><p style="color: #FFFFFF;"><b>Impact</b> — maatschappelijk resultaat</p></div>
  <div style="background: var(--sfnl-royal); border-radius: 4pt; padding: 8pt 14pt; margin: 0 24pt;"><p style="color: #FFFFFF;"><b>Outcomes</b> — gedragsverandering</p></div>
  <div style="background: var(--sfnl-sky); border-radius: 4pt; padding: 8pt 14pt; margin: 0 48pt;"><p style="color: #FFFFFF;"><b>Output</b> — geleverde trajecten</p></div>
</div>
```

## Cyclus / mechanisme

Posities absoluut binnen een relatief gepositioneerde container; verbindingslijnen als dunne
`<div>`s (bv. `height: 1.5pt; background: var(--sfnl-grey-70);`), knopen als cirkels
(`border-radius: 50%`). Pijlpunten: PNG via Sharp.

## Assessment-tabel

Gebruik geen HTML `<table>` (niet ondersteund) — bouw rijen als flex-divs:

```html
<div class="col" style="gap: 4pt;">
  <div style="display: flex; gap: 4pt;">
    <div style="flex: 2; background: var(--sfnl-navy); padding: 5pt 8pt;"><p class="label" style="color: #FFFFFF;">CRITERIUM</p></div>
    <div style="flex: 1; background: var(--sfnl-navy); padding: 5pt 8pt;"><p class="label" style="color: #FFFFFF;">OORDEEL</p></div>
  </div>
  <div style="display: flex; gap: 4pt;">
    <div style="flex: 2; background: var(--sfnl-grey-95); padding: 5pt 8pt;"><p>Haalbaarheid</p></div>
    <div style="flex: 1; background: var(--sfnl-emerald-tint60); padding: 5pt 8pt;"><p><b>Sterk</b></p></div>
  </div>
</div>
```

Complexe tabellen kunnen ook native: via de per-deck hook (`slide.addTable`, zie authoring guide).

## Iconen

Rasterize react-icons naar merkkleur-PNGs in de workspace `assets/` (zie authoring guide,
`build/raster.js`) en plaats met `<img style="width: 22pt; height: 22pt;">`. Iconen zijn inhoud,
geen decoratie: kies op betekenis.
````

- [ ] **Step 4: Run tests** — `npm test` → archetypes test PASS.
- [ ] **Step 5: Commit**

```powershell
git add -A "sfnl-pptx/engine/web"
git commit -m "feat(sfnl-pptx): slide archetypes and layout pattern cookbook"
```

---

### Task 6: Icon/gradient rasterizer (raster.js)

**Files:**
- Create: `sfnl-pptx/engine/web/build/raster.js`
- Create: `sfnl-pptx/engine/web/build/test/raster.test.js`

**Interfaces:**
- Produces: `rasterizeIcon({ pack, name, colorHex, sizePx, outFile })` and `rasterizeGradient({ from, to, widthPx, heightPx, outFile })`; CLI `node raster.js icon <pack> <IconName> <hex> <size> <out.png>` and `node raster.js gradient <hexFrom> <hexTo> <w> <h> <out.png>`.

- [ ] **Step 1: Write the failing test** — `test/raster.test.js`:

```javascript
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const sharp = require('sharp');
const { rasterizeIcon, rasterizeGradient } = require('../raster');

test('rasterizes a react-icon to a sized PNG', async () => {
  const out = path.join(os.tmpdir(), `sfnl-icon-${process.pid}.png`);
  await rasterizeIcon({ pack: 'fa', name: 'FaUsers', colorHex: 'F87F4F', sizePx: 256, outFile: out });
  const meta = await sharp(out).metadata();
  assert.equal(meta.format, 'png');
  assert.equal(meta.width, 256);
  fs.unlinkSync(out);
});

test('unknown icon throws a clear error', async () => {
  await assert.rejects(() => rasterizeIcon({ pack: 'fa', name: 'FaDoesNotExist', colorHex: 'F87F4F', sizePx: 64, outFile: 'x.png' }), /not found/);
});

test('rasterizes a two-stop gradient PNG', async () => {
  const out = path.join(os.tmpdir(), `sfnl-grad-${process.pid}.png`);
  await rasterizeGradient({ from: '201B5C', to: '3B62C1', widthPx: 400, heightPx: 225, outFile: out });
  const meta = await sharp(out).metadata();
  assert.equal(meta.width, 400);
  fs.unlinkSync(out);
});
```

Run `npm test` → FAIL.

- [ ] **Step 2: Implement `raster.js`**

```javascript
#!/usr/bin/env node
/* Pre-render icons (react-icons) and gradients to PNG — CSS gradients and inline
   SVG never survive the pptx conversion, so all such assets are rasterized first. */
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');

async function rasterizeIcon({ pack, name, colorHex, sizePx = 256, outFile }) {
  const icons = require(`react-icons/${pack}`);
  const Icon = icons[name];
  if (!Icon) throw new Error(`icon ${name} not found in react-icons/${pack}`);
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Icon, { color: `#${colorHex}`, size: String(sizePx) })
  );
  await sharp(Buffer.from(svg)).resize(sizePx, sizePx, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } }).png().toFile(outFile);
  return outFile;
}

async function rasterizeGradient({ from, to, widthPx, heightPx, outFile }) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${widthPx}" height="${heightPx}">
  <defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#${from}"/><stop offset="100%" stop-color="#${to}"/>
  </linearGradient></defs>
  <rect width="100%" height="100%" fill="url(#g)"/></svg>`;
  await sharp(Buffer.from(svg)).png().toFile(outFile);
  return outFile;
}

if (require.main === module) {
  const [mode, ...a] = process.argv.slice(2);
  const run = mode === 'icon'
    ? rasterizeIcon({ pack: a[0], name: a[1], colorHex: a[2], sizePx: Number(a[3]) || 256, outFile: a[4] })
    : mode === 'gradient'
      ? rasterizeGradient({ from: a[0], to: a[1], widthPx: Number(a[2]), heightPx: Number(a[3]), outFile: a[4] })
      : Promise.reject(new Error('usage: node raster.js icon <pack> <Name> <hex> <size> <out> | gradient <from> <to> <w> <h> <out>'));
  run.then((f) => console.log('wrote', f)).catch((e) => { console.error(e.message); process.exit(1); });
}
module.exports = { rasterizeIcon, rasterizeGradient };
```

- [ ] **Step 3: Run tests** — `npm test` → PASS.
- [ ] **Step 4: Commit**

```powershell
git add -A "sfnl-pptx/engine/web/build"
git commit -m "feat(sfnl-pptx): icon and gradient rasterizer (react-icons + sharp)"
```

---

### Task 7: Chart spec module (chart_spec.js)

**Files:**
- Create: `sfnl-pptx/engine/web/build/chart_spec.js`
- Create: `sfnl-pptx/engine/web/build/test/chart_spec.test.js`

**Interfaces:**
- Consumes: `palette.json` object (passed in).
- Produces: `chartArgs(spec, palette, deckAccent)` → `{ chartKey, data, options }` where `chartKey` ∈ `BAR|LINE|AREA|PIE|DOUGHNUT|SCATTER` (index into `pptx.charts`), `options.chartColors` hex **without** `#`. Chart spec JSON schema (documented in Task 12's authoring guide):

```json
{
  "placeholder": "chart-main",
  "type": "column | stackedColumn | bar | line | area | pie | donut | scatter",
  "title": "optional",
  "series": [{ "name": "…", "labels": ["…"], "values": [1, 2] }],
  "axis": { "catTitle": "…", "valTitle": "…", "valMin": 0, "valMax": 100, "majorUnit": 25 },
  "colors": ["orange", "emerald"]
}
```

- [ ] **Step 1: Write the failing test** — `test/chart_spec.test.js`:

```javascript
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { chartArgs } = require('../chart_spec');

const palette = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', '..', 'assets', 'palette.json'), 'utf-8'));
const spec = (over = {}) => ({
  placeholder: 'c1', type: 'column',
  series: [{ name: 'Deelnemers', labels: ['2024', '2025'], values: [120, 180] }],
  ...over,
});

test('column maps to BAR/col with deck accent, no # in colors', () => {
  const { chartKey, data, options } = chartArgs(spec(), palette, 'orange');
  assert.equal(chartKey, 'BAR');
  assert.equal(options.barDir, 'col');
  assert.deepEqual(options.chartColors, ['F87F4F']);
  assert.equal(options.showLegend, false);
  assert.equal(data[0].name, 'Deelnemers');
});

test('explicit color names resolve via palette; multi-series shows legend', () => {
  const s = spec({ colors: ['emerald', 'royal'], series: [
    { name: 'A', labels: ['x'], values: [1] }, { name: 'B', labels: ['x'], values: [2] }] });
  const { options } = chartArgs(s, palette, 'orange');
  assert.deepEqual(options.chartColors, ['6AC6BA', '3B62C1']);
  assert.equal(options.showLegend, true);
});

test('axis fields become pptxgenjs options', () => {
  const { options } = chartArgs(spec({ axis: { catTitle: 'Jaar', valTitle: 'Aantal', valMin: 0, valMax: 200, majorUnit: 50 } }), palette, 'orange');
  assert.equal(options.showCatAxisTitle, true);
  assert.equal(options.catAxisTitle, 'Jaar');
  assert.equal(options.valAxisMaxVal, 200);
  assert.equal(options.valAxisMajorUnit, 50);
});

test('every documented type maps; unknown type and color throw clearly', () => {
  for (const [t, key] of [['column', 'BAR'], ['stackedColumn', 'BAR'], ['bar', 'BAR'], ['line', 'LINE'], ['area', 'AREA'], ['pie', 'PIE'], ['donut', 'DOUGHNUT'], ['scatter', 'SCATTER']]) {
    assert.equal(chartArgs(spec({ type: t }), palette, 'orange').chartKey, key);
  }
  assert.throws(() => chartArgs(spec({ type: 'radar' }), palette, 'orange'), /unknown chart type/);
  assert.throws(() => chartArgs(spec({ colors: ['pink'] }), palette, 'orange'), /unknown color name/);
});
```

Run `npm test` → FAIL.

- [ ] **Step 2: Implement `chart_spec.js`**

```javascript
/* Map SFNL chart-spec JSON (deck.json slides[].charts[]) to PptxGenJS addChart args.
   Colors are always brand hex WITHOUT '#' (with '#' the file corrupts). */
const TYPE_MAP = {
  column: ['BAR', { barDir: 'col' }],
  stackedColumn: ['BAR', { barDir: 'col', barGrouping: 'stacked' }],
  bar: ['BAR', { barDir: 'bar' }],
  line: ['LINE', { lineSize: 3 }],
  area: ['AREA', {}],
  pie: ['PIE', { showPercent: true }],
  donut: ['DOUGHNUT', { showPercent: true, holeSize: 60 }],
  scatter: ['SCATTER', { lineSize: 0, lineDataSymbol: 'circle', lineDataSymbolSize: 6 }],
};

function colorHex(palette, name) {
  const slot = palette.by_name[name];
  if (!slot) throw new Error(`unknown color name "${name}" (allowed: ${Object.keys(palette.by_name).join(', ')})`);
  return palette.by_slot[slot].hex.toUpperCase();
}

function chartArgs(spec, palette, deckAccent) {
  if (!TYPE_MAP[spec.type]) {
    throw new Error(`unknown chart type "${spec.type}" (allowed: ${Object.keys(TYPE_MAP).join(', ')})`);
  }
  const [chartKey, typeOpts] = TYPE_MAP[spec.type];
  const colors = (spec.colors && spec.colors.length ? spec.colors : [deckAccent]).map((n) => colorHex(palette, n));
  const data = spec.series.map((s) => ({ name: s.name, labels: s.labels, values: s.values }));
  const options = {
    ...typeOpts,
    chartColors: colors,
    showLegend: data.length > 1 && !['pie', 'donut'].includes(spec.type) ? true : ['pie', 'donut'].includes(spec.type),
    dataLabelFontFace: 'Lato Light',
    catAxisLabelFontFace: 'Lato Light',
    valAxisLabelFontFace: 'Lato Light',
  };
  options.showLegend = ['pie', 'donut'].includes(spec.type) || data.length > 1;
  if (spec.title) {
    options.showTitle = true;
    options.title = spec.title;
    options.titleFontFace = 'Gotham Bold';
    options.titleColor = '201B5C';
    options.titleFontSize = 12;
  }
  const ax = spec.axis || {};
  if (ax.catTitle) { options.showCatAxisTitle = true; options.catAxisTitle = ax.catTitle; }
  if (ax.valTitle) { options.showValAxisTitle = true; options.valAxisTitle = ax.valTitle; }
  if (ax.valMin != null) options.valAxisMinVal = ax.valMin;
  if (ax.valMax != null) options.valAxisMaxVal = ax.valMax;
  if (ax.majorUnit != null) options.valAxisMajorUnit = ax.majorUnit;
  return { chartKey, data, options };
}

module.exports = { chartArgs, TYPE_MAP };
```

(Note the duplicated `showLegend` assignment: keep only the second, single line — `options.showLegend = ['pie', 'donut'].includes(spec.type) || data.length > 1;` — and omit it from the object literal.)

- [ ] **Step 3: Run tests** — `npm test` → PASS.
- [ ] **Step 4: Commit**

```powershell
git add -A "sfnl-pptx/engine/web/build"
git commit -m "feat(sfnl-pptx): chart spec to native PptxGenJS chart mapping"
```

---

### Task 8: build_deck.js — the generic deck runner + fixture deck

**Files:**
- Create: `sfnl-pptx/engine/web/build/build_deck.js`
- Create: `sfnl-pptx/tests/fixtures/webdeck/deck.json`
- Create: `sfnl-pptx/tests/fixtures/webdeck/slides/01-cover.html`
- Create: `sfnl-pptx/tests/fixtures/webdeck/slides/02-kpi.html`
- Create: `sfnl-pptx/tests/fixtures/webdeck/slides/03-chart.html`
- Create: `sfnl-pptx/tests/fixtures/webdeck-overflow/deck.json`
- Create: `sfnl-pptx/tests/fixtures/webdeck-overflow/slides/01-overflow.html`
- Create: `sfnl-pptx/tests/test_web_build.py`

**Interfaces:**
- Consumes: `html2pptx` (Task 1), `chartArgs` (Task 7), `engine/web/assets/sfnl-logo.png` (Task 4), `engine/assets/palette.json`.
- Produces: CLI `node build_deck.js <workspace-dir>` → writes `<workspace>/<slug>.pptx`; exports `buildDeck(workspace)`. deck.json schema:

```json
{
  "title": "DECK TITLE",
  "slug": "webdeck",
  "language": "nl",
  "author": "Social Finance NL",
  "accent": "orange",
  "hooks": null,
  "slides": [
    { "file": "slides/01-cover.html", "chrome": "none", "notes": "…" },
    { "file": "slides/02-kpi.html", "notes": "Bron: R1, R4" },
    { "file": "slides/03-chart.html", "notes": "Bron: R2",
      "charts": [{ "placeholder": "chart-main", "type": "column",
        "series": [{ "name": "Deelnemers", "labels": ["2024", "2025", "2026"], "values": [120, 180, 260] }],
        "axis": { "catTitle": "Jaar", "valTitle": "Aantal" } }] }
  ]
}
```

`chrome`: `"light"` (default: logo + orange page number), `"dark"` (white page number, no logo), `"none"`. `hooks`: optional path (relative to workspace) to a JS module exporting `{ afterSlide: async ({ pptx, slide, entry, index, placeholders }) => {} }` for exotic direct-PptxGenJS slides.

- [ ] **Step 1: Implement `build_deck.js`** (build first — the pytest below is the failing test for the whole unit):

```javascript
#!/usr/bin/env node
/* build_deck.js — deck.json + slides/*.html -> <workspace>/<slug>.pptx
   Usage: node build_deck.js <workspace-dir>   (workspace contains deck.json) */
const fs = require('fs');
const os = require('os');
const path = require('path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx');
const { chartArgs } = require('./chart_spec');

const palette = require(path.join(__dirname, '..', '..', 'assets', 'palette.json'));
const LOGO = path.join(__dirname, '..', 'assets', 'sfnl-logo.png');
// Geometry from the sjabloon master, scaled 0.75 to the 10in x 5.625in canvas.
const LOGO_POS = { x: 0.27, y: 5.3025, w: 0.825, h: 0.225 };
const PAGE_POS = { x: 9.45, y: 5.34, w: 0.465, h: 0.18 };

function addChrome(slide, pageNo, mode) {
  if (mode === 'none') return;
  if (mode !== 'dark') slide.addImage({ path: LOGO, ...LOGO_POS });
  slide.addText(String(pageNo), {
    ...PAGE_POS, fontFace: 'Montserrat Light', fontSize: 9, align: 'right',
    color: mode === 'dark' ? 'FFFFFF' : 'F87F4F',
  });
}

async function buildDeck(workspace) {
  workspace = path.resolve(workspace);
  const deck = JSON.parse(fs.readFileSync(path.join(workspace, 'deck.json'), 'utf-8'));
  if (!deck.slug) throw new Error('deck.json: "slug" is required');
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = deck.title || deck.slug;
  pptx.author = deck.author || 'Social Finance NL';
  const hooks = deck.hooks ? require(path.resolve(workspace, deck.hooks)) : {};
  const errors = [];
  for (const [i, entry] of deck.slides.entries()) {
    let result;
    try {
      result = await html2pptx(path.resolve(workspace, entry.file), pptx, { tmpDir: os.tmpdir() });
    } catch (e) {
      errors.push(e.message);
      continue;
    }
    const { slide, placeholders } = result;
    for (const c of entry.charts || []) {
      const ph = placeholders.find((p) => p.id === c.placeholder);
      if (!ph) { errors.push(`${entry.file}: placeholder "${c.placeholder}" not found in HTML`); continue; }
      try {
        const { chartKey, data, options } = chartArgs(c, palette, deck.accent || 'orange');
        slide.addChart(pptx.charts[chartKey], data, { x: ph.x, y: ph.y, w: ph.w, h: ph.h, ...options });
      } catch (e) {
        errors.push(`${entry.file}: ${e.message}`);
      }
    }
    if (entry.notes) slide.addNotes(entry.notes);
    addChrome(slide, i + 1, entry.chrome || 'light');
    if (typeof hooks.afterSlide === 'function') {
      await hooks.afterSlide({ pptx, slide, entry, index: i, placeholders });
    }
  }
  if (errors.length) {
    throw new Error(`deck build failed with ${errors.length} error(s):\n`
      + errors.map((e, n) => `  ${n + 1}. ${e}`).join('\n'));
  }
  const out = path.join(workspace, `${deck.slug}.pptx`);
  await pptx.writeFile({ fileName: out });
  return out;
}

if (require.main === module) {
  buildDeck(process.argv[2]).then((out) => console.log('wrote', out))
    .catch((e) => { console.error(e.message); process.exit(1); });
}
module.exports = { buildDeck };
```

- [ ] **Step 2: Create the fixture deck**

`tests/fixtures/webdeck/deck.json`: exactly the schema example above (slug `webdeck`).

`slides/01-cover.html`: copy of `engine/web/archetypes/cover.html` (unchanged).

`slides/02-kpi.html`:

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><link rel="stylesheet" href="sfnl.css"></head>
<body>
  <header class="chrome-header">
    <h1 class="slide-title">DRIE CIJFERS DRAGEN HET RESULTAAT</h1>
    <p class="slide-subtitle">FIXTURE VOOR DE BUILDTESTS</p>
    <div class="dash"></div>
  </header>
  <main class="content">
    <div class="card"><p class="big-number">31%</p><p class="label" style="margin-top: 6pt;">MINDER UITVAL</p><p style="margin-top: 8pt;">Eén regel duiding.</p></div>
    <div class="card card-accent"><p class="big-number">124</p><p class="label" style="margin-top: 6pt;">TRAJECTEN</p><p style="margin-top: 8pt;">Eén regel duiding.</p></div>
    <div class="card"><p class="big-number">€ 0,9M</p><p class="label" style="margin-top: 6pt;">BESPARING</p><p style="margin-top: 8pt;">Eén regel duiding.</p></div>
  </main>
</body>
</html>
```

`slides/03-chart.html`:

```html
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><link rel="stylesheet" href="sfnl.css"></head>
<body>
  <header class="chrome-header">
    <h1 class="slide-title">DEELNAME GROEIT DOOR</h1>
    <div class="dash"></div>
  </header>
  <main class="content">
    <div class="col" style="flex: 2;">
      <p class="kicker">WAT WE ZIEN</p>
      <ul style="margin-top: 6pt;"><li>Instroom groeit jaar op jaar.</li><li>2026 is een prognose.</li></ul>
    </div>
    <div class="col" style="flex: 3;">
      <div id="chart-main" class="placeholder" style="flex: 1;"></div>
    </div>
  </main>
</body>
</html>
```

`tests/fixtures/webdeck-overflow/deck.json`:

```json
{
  "title": "OVERFLOW", "slug": "overflow", "language": "nl", "accent": "orange",
  "slides": [{ "file": "slides/01-overflow.html" }]
}
```

`slides/01-overflow.html`: copy of `engine/web/build/test/fixtures/overflow.html` (Task 1).

- [ ] **Step 3: Write the failing pytest** — `tests/test_web_build.py`:

```python
"""Build-layer integration: fixture deck -> valid .pptx via node build_deck.js."""
import shutil
import subprocess
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
BUILD = ENGINE / "web" / "build"
FIXTURES = Path(__file__).parent / "fixtures"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(
    NODE is None or not (BUILD / "node_modules").exists(),
    reason="node or web build deps unavailable",
)


def _workspace(dst_dir, name):
    ws = dst_dir / name
    shutil.copytree(FIXTURES / name, ws)
    shutil.copy(ENGINE / "web" / "sfnl.css", ws / "slides" / "sfnl.css")
    return ws


def _build(ws):
    return subprocess.run([NODE, str(BUILD / "build_deck.js"), str(ws)],
                          capture_output=True, text=True, timeout=300)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    ws = _workspace(tmp_path_factory.mktemp("webdeck"), "webdeck")
    res = _build(ws)
    assert res.returncode == 0, res.stderr + res.stdout
    out = ws / "webdeck.pptx"
    assert out.exists()
    return Presentation(str(out))


def test_all_slides_present(built):
    assert len(built.slides.__iter__.__self__._sldIdLst) == 3 or len(list(built.slides)) == 3


def test_title_chrome_lands_on_content_slide(built):
    slide = list(built.slides)[1]
    titles = [s for s in slide.shapes if s.has_text_frame and "DRIE CIJFERS" in s.text_frame.text]
    assert titles, "title text missing"
    assert titles[0].top < Inches(0.9)
    fonts = {r.font.name for p in titles[0].text_frame.paragraphs for r in p.runs}
    assert "Gotham Bold" in fonts


def test_orange_dash_shape_present(built):
    slide = list(built.slides)[1]
    assert "F87F4F" in slide._element.xml


def test_notes_carry_dossier_refs(built):
    slide = list(built.slides)[1]
    assert slide.has_notes_slide
    assert "R1" in slide.notes_slide.notes_text_frame.text


def test_chart_injected_with_brand_colors(built):
    slide = list(built.slides)[2]
    frames = [s for s in slide.shapes if s.has_chart]
    assert frames, "native chart missing"
    assert "F87F4F" in frames[0].chart._chartSpace.xml


def test_page_number_and_logo_chrome(built):
    slides = list(built.slides)
    # cover has chrome none -> no page number '1' textbox bottom-right
    assert not any(s.has_text_frame and s.text_frame.text.strip() == "1" for s in slides[0].shapes)
    two = [s for s in slides[1].shapes if s.has_text_frame and s.text_frame.text.strip() == "2"]
    assert two and two[0].top > Inches(5.0)
    assert any(s.shape_type == 13 for s in slides[1].shapes)  # PICTURE = logo


def test_overflow_deck_fails_loudly(tmp_path):
    ws = _workspace(tmp_path, "webdeck-overflow")
    res = _build(ws)
    assert res.returncode != 0
    assert "overflows body" in (res.stderr + res.stdout)
```

(In `test_all_slides_present` use simply `assert len(list(built.slides)) == 3` — drop the first clause.)

- [ ] **Step 4: Run** — from `sfnl-pptx/`: `python -m pytest tests/test_web_build.py -v`
Expected: initially failures reveal real integration defects; fix `build_deck.js`/fixtures until all PASS.

- [ ] **Step 5: Commit**

```powershell
git add -A "sfnl-pptx/engine/web/build" "sfnl-pptx/tests"
git commit -m "feat(sfnl-pptx): build_deck.js runner with charts, notes, chrome injection, and fixture deck"
```

---

### Task 9: Adapt qa_text.py to the html2pptx pipeline

**Files:**
- Rewrite: `sfnl-pptx/engine/scripts/qa_text.py`
- Rewrite: `sfnl-pptx/tests/test_qa_text.py`

**Interfaces:**
- Consumes: `engine/web/tokens.json` (Task 3).
- Produces: `qa_deck(pptx_path) -> {"findings": [...], "critical": int}` — same output shape as v1 so skills keep calling `python -m scripts.qa_text <deck.pptx>`. Keeps: three-fonts rule, ALL-CAPS titles rule, leftover-text/language markers. Drops: schemeClr/placeholder-idx logic. Off-brand color check now allows token hexes.

- [ ] **Step 1: Rewrite the tests first** — `tests/test_qa_text.py`:

```python
"""qa_text v2: rules over html2pptx-built decks (plain text boxes, brand hex by design)."""
from pathlib import Path

import pytest
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

from scripts.qa_text import qa_deck


def _deck(tmp_path, build):
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    build(slide)
    p = tmp_path / "deck.pptx"
    prs.save(p)
    return p


def _textbox(slide, text, font, size, top=Inches(0.4), color=None):
    box = slide.shapes.add_textbox(Inches(0.4), top, Inches(6), Inches(0.5))
    run = box.text_frame.paragraphs[0].add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    return box


def test_lowercase_gotham_title_is_critical(tmp_path):
    p = _deck(tmp_path, lambda s: _textbox(s, "geen caps titel", "Gotham Bold", 18))
    r = qa_deck(p)
    assert any("ALL CAPS" in f["message"] for f in r["findings"])
    assert r["critical"] >= 1


def test_caps_title_and_brand_colors_pass(tmp_path):
    def build(s):
        _textbox(s, "NETTE TITEL", "Gotham Bold", 18, color="201B5C")
        _textbox(s, "Body in Lato.", "Lato Light", 10, top=Inches(2))
    r = qa_deck(_deck(tmp_path, build))
    assert r["critical"] == 0


def test_big_number_lower_on_canvas_is_not_a_title(tmp_path):
    p = _deck(tmp_path, lambda s: _textbox(s, "31% minder", "Gotham Bold", 30, top=Inches(2.5)))
    assert qa_deck(p)["critical"] == 0


def test_non_brand_font_warns(tmp_path):
    p = _deck(tmp_path, lambda s: _textbox(s, "TEKST", "Comic Sans MS", 12))
    assert any("non-brand font" in f["message"] for f in qa_deck(p)["findings"])


def test_off_token_color_warns_but_tint_passes(tmp_path):
    import json
    tokens = json.loads((Path(__file__).resolve().parents[1] / "engine" / "web" / "tokens.json").read_text())
    a_tint = next(h for h in tokens["allowed_hex"] if h not in {"201B5C", "233348", "F87F4F"})
    def build(s):
        _textbox(s, "PAARS", "Lato Light", 10, color="8B00FF")
        _textbox(s, "TINT", "Lato Light", 10, top=Inches(2), color=a_tint)
    findings = qa_deck(_deck(tmp_path, build))["findings"]
    assert any("8B00FF" in f["message"] for f in findings)
    assert not any(a_tint in f["message"] for f in findings)


def test_leftover_scaffold_text_is_critical(tmp_path):
    p = _deck(tmp_path, lambda s: _textbox(s, "Vervang deze inhoud.", "Lato Light", 10, top=Inches(2)))
    r = qa_deck(p)
    assert any("leftover" in f["message"] for f in r["findings"])
    assert r["critical"] >= 1
```

Run: `python -m pytest tests/test_qa_text.py -q` → FAIL (old qa_text imports `scripts.colors`, old rules).

- [ ] **Step 2: Rewrite `qa_text.py`**

```python
"""Cheap brand/text QA over a built deck (no rendering). v2 for the html2pptx
pipeline: slides are plain text boxes/shapes; brand hex is by design and the
allowed set comes from engine/web/tokens.json (palette + precomputed tints)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches

ENGINE = Path(__file__).resolve().parents[1]

ALLOWED_FONTS = {"Montserrat Light", "Lato Light", "Gotham Bold"}
LEFTOVER_MARKERS = (
    "click to edit", "tijdelijke aanduiding", "text placeholder", "lorem ipsum",
    "vervang deze", "action title in all caps", "optionele subtitel",
)
NEUTRAL_HEX = {"FFFFFF", "FEFFFF", "000000"}
TITLE_TOP_MAX = Inches(0.9)
TITLE_MIN_PT = 14


def _allowed_hexes() -> set[str]:
    tokens = json.loads((ENGINE / "web" / "tokens.json").read_text(encoding="utf-8"))
    return {h.upper() for h in tokens["allowed_hex"]} | NEUTRAL_HEX


def qa_deck(pptx_path) -> dict:
    prs = Presentation(str(pptx_path))
    allowed = _allowed_hexes()
    findings = []
    for si, slide in enumerate(prs.slides):
        texts = []
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            t = shape.text_frame.text
            texts.append(t)
            fonts, sizes = set(), []
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if run.font.name:
                        fonts.add(run.font.name)
                    if run.font.size is not None:
                        sizes.append(run.font.size.pt)
            for fn in sorted(fonts - ALLOWED_FONTS):
                findings.append({"slide": si, "axis": "Design", "severity": "warn",
                                 "message": f"non-brand font {fn!r}"})
            is_title = ("Gotham Bold" in fonts and shape.top is not None
                        and shape.top < TITLE_TOP_MAX
                        and any(s >= TITLE_MIN_PT for s in sizes))
            if is_title and t.strip() and t != t.upper():
                findings.append({"slide": si, "axis": "Design", "severity": "critical",
                                 "message": f"titel niet in ALL CAPS: {t!r}"})
            low = t.lower()
            for marker in LEFTOVER_MARKERS:
                if marker in low:
                    findings.append({"slide": si, "axis": "Content", "severity": "critical",
                                     "message": f"leftover scaffold/placeholder text: {t!r}"})
        if not any(t.strip() for t in texts):
            findings.append({"slide": si, "axis": "Content", "severity": "warn",
                             "message": "slide has no text"})
        xml = slide._element.xml
        for hexv in set(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', xml)):
            if hexv.upper() not in allowed:
                findings.append({"slide": si, "axis": "Design", "severity": "warn",
                                 "message": f"off-brand color #{hexv.upper()}"})
    critical = sum(1 for f in findings if f["severity"] == "critical")
    return {"findings": findings, "critical": critical}


if __name__ == "__main__":
    import sys
    print(json.dumps(qa_deck(sys.argv[1]), indent=2, ensure_ascii=False))
```

- [ ] **Step 3: Run** — `python -m pytest tests/test_qa_text.py -q` → PASS. Also run `python -m scripts.qa_text` over the Task 8 fixture output once (build it into a temp dir) and confirm `critical == 0`.

- [ ] **Step 4: Commit**

```powershell
git add "sfnl-pptx/engine/scripts/qa_text.py" "sfnl-pptx/tests/test_qa_text.py"
git commit -m "feat(sfnl-pptx): qa_text v2 for html2pptx decks (tokens.json colors, title heuristic)"
```

---

### Task 10: Retire the deck-spec engine

**Files:**
- Delete: `sfnl-pptx/engine/scripts/build_from_spec.py`, `spec.py`, `components.py`, `icons.py`, `extract_layouts.py`, `colors.py`
- Delete: `sfnl-pptx/engine/assets/layouts.json`, `sfnl-pptx/engine/assets/components/index.json` (and the `components/` dir)
- Delete tests: `tests/test_build.py`, `test_spec.py`, `test_components.py`, `test_colors.py`, `test_layouts.py`, `test_icons.py`, `test_acceptance.py`, `test_visual_components.py`, `test_html_template_components.py`, `test_reference_style_components.py`, `test_extended_freeform_and_chart.py`, `test_deck_spec_reference.py`, `test_scaffold.py`
- Delete fixtures: `tests/fixtures/sample_spec.json`, `sample_visual_spec.json`, `sample_html_components_spec.json`, `sample_reference_style_spec.json`
- Keep: `extract_palette.py`, `render.py`, `qa_text.py`, `office/template.py`, `office/__init__.py`, `scripts/__init__.py`, `assets/palette.json`, `assets/sfnl-template.pptx`; tests `test_palette.py`, `test_render.py`, `test_template.py`, `test_tokens.py`, `test_web_build.py`, `test_qa_text.py`, `test_voice_reference.py`, `test_skills.py` (rewritten in Task 13), `conftest.py`.

- [ ] **Step 1: Delete the retired files**

```powershell
cd "sfnl-pptx"
git rm engine/scripts/build_from_spec.py engine/scripts/spec.py engine/scripts/components.py engine/scripts/icons.py engine/scripts/extract_layouts.py engine/scripts/colors.py
git rm engine/assets/layouts.json
git rm -r engine/assets/components
git rm tests/test_build.py tests/test_spec.py tests/test_components.py tests/test_colors.py tests/test_layouts.py tests/test_icons.py tests/test_acceptance.py tests/test_visual_components.py tests/test_html_template_components.py tests/test_reference_style_components.py tests/test_extended_freeform_and_chart.py tests/test_deck_spec_reference.py tests/test_scaffold.py
git rm tests/fixtures/sample_spec.json tests/fixtures/sample_visual_spec.json tests/fixtures/sample_html_components_spec.json tests/fixtures/sample_reference_style_spec.json
```

- [ ] **Step 2: Sweep for dangling imports**

Run: `grep -rn "build_from_spec\|scripts.spec\|scripts.components\|scripts.colors\|scripts.icons\|extract_layouts\|layouts.json\|components/index.json" sfnl-pptx --include="*.py" --include="*.md" --include="*.json"`
Expected: hits only in `skills/`, `agents/`, `engine/reference/`, `README.md` (fixed in Tasks 12–13). Zero hits in `engine/scripts/` and `tests/`. If `test_skills.py`/`test_voice_reference.py` reference retired modules, stub-adjust minimally now (full rewrite in Task 13).

- [ ] **Step 3: Full remaining suite green**

Run: `python -m pytest tests/ -q` → all pass (skips allowed for COM/node). Run `npm test` in `engine/web/build` → all pass.

- [ ] **Step 4: Commit**

```powershell
git add -A
git commit -m "chore(sfnl-pptx): retire deck-spec python-pptx engine, tests, and fixtures"
```

---

### Task 11: End-to-end smoke — build + COM render of the fixture deck

**Files:**
- Create: `sfnl-pptx/tests/test_e2e_render.py`

**Interfaces:**
- Consumes: `buildDeck` fixture flow from `tests/test_web_build.py` (reuse `_workspace`/`_build` by import), `scripts.render.com_available`/`render_deck`.

- [ ] **Step 1: Write the failing test**

```python
"""E2E smoke: fixture deck -> build_deck.js -> PowerPoint COM render (spec §6)."""
import shutil
from pathlib import Path

import pytest

from scripts.render import com_available, render_deck
from tests.test_web_build import BUILD, NODE, _build, _workspace

pytestmark = pytest.mark.skipif(
    NODE is None or not (BUILD / "node_modules").exists() or not com_available(),
    reason="node deps or PowerPoint COM unavailable",
)


def test_build_and_render_full_fixture_deck(tmp_path):
    ws = _workspace(tmp_path, "webdeck")
    res = _build(ws)
    assert res.returncode == 0, res.stderr + res.stdout
    images = render_deck(ws / "webdeck.pptx", ws / "renders")
    assert len(images) == 3
    assert all(p.exists() and p.stat().st_size > 10_000 for p in images)
```

Note: `from tests.test_web_build import ...` requires running pytest from `sfnl-pptx/` with rootdir discovery; if the import fails, add an empty `tests/__init__.py`.

- [ ] **Step 2: Run** — `python -m pytest tests/test_e2e_render.py -v` → PASS (or SKIP where COM absent — verify it passes on this machine, PowerPoint is installed).

- [ ] **Step 3: Inspect the renders once (visual loop bootstrap)** — Read the three PNGs under the tmp `renders/`; confirm: chrome present (title/dash on slides 2–3, logo + orange page number, none on cover), content fills the canvas, chart uses orange. Fix CSS/archetypes if not, rebuild, re-run.

- [ ] **Step 4: Commit**

```powershell
git add "sfnl-pptx/tests/test_e2e_render.py" "sfnl-pptx/tests/__init__.py"
git commit -m "test(sfnl-pptx): end-to-end build+render smoke for the html2pptx pipeline"
```

---

### Task 12: Reference docs — authoring guide, brand.md, README, plugin version

**Files:**
- Create: `sfnl-pptx/engine/reference/authoring-guide.md`
- Delete: `sfnl-pptx/engine/reference/deck-spec.md`
- Rewrite: `sfnl-pptx/engine/reference/brand.md`
- Modify: `sfnl-pptx/README.md` (pipeline description; keep tone/structure, swap build layer)
- Modify: `sfnl-pptx/.claude-plugin/plugin.json` + `sfnl-pptx/.codex-plugin/plugin.json` (version `0.4.0`, description mentions html2pptx pipeline)

- [ ] **Step 1: Write `authoring-guide.md`** (replaces deck-spec.md):

````markdown
# SFNL deck authoring guide (html2pptx pipeline)

Eén HTML-bestand per slide + één `deck.json` per deck. De build converteert naar een `.pptx`
met bewerkbare tekstvakken, echte shapes en native charts.

## Workspace

```
output/<YYYY-MM-DD>-<slug>/
  deck.json
  slides/01-cover.html … NN-closing.html
  slides/sfnl.css        # kopie van engine/web/sfnl.css
  assets/                # gerasterde iconen/gradients (Sharp)
  renders/               # PNG-renders van de visuele loop
  <slug>.pptx
```

Aanmaken: map maken, `engine/web/sfnl.css` naar `slides/` kopiëren, per slide starten vanaf
`engine/web/scaffold.html` of een archetype uit `engine/web/archetypes/`
(cover, divider, quote, closing, stat-banner). Layoutpatronen: `engine/web/patterns.md`.

## HTML-regels (hard — de build faalt of verliest tekst bij overtreding)

- Canvas exact `width: 720pt; height: 405pt` op `<body>`.
- **Alle tekst in `<p>`, `<h1>`–`<h6>`, `<ul>` of `<ol>`** — tekst los in een `<div>`/`<span>`
  verdwijnt geluidloos.
- Achtergrond/rand/schaduw alleen op `<div>`; `<table>` wordt niet ondersteund (flex-rijen of
  native via hook).
- **Nooit CSS-gradients** — pre-render PNG via `node engine/web/build/raster.js gradient …`.
- Iconen: `node engine/web/build/raster.js icon fa FaUsers F87F4F 256 assets/users.png`, dan `<img>`.
- Tekst > 12pt eindigt ≥ 0.5in boven de onderrand (de `.content`-marges regelen dit).
- Titels/subtitels **in ALL CAPS getypt** (CSS `text-transform` telt niet).
- Logo en paginanummer **niet** in HTML — `build_deck.js` injecteert die native.
- Charts: reserveer ruimte met `<div id="…" class="placeholder" style="…">` en registreer de
  chart in `deck.json`.

## deck.json

```json
{
  "title": "DEKTITEL",
  "slug": "kebab-slug",
  "language": "nl",
  "author": "Social Finance NL",
  "accent": "orange",
  "hooks": null,
  "slides": [
    { "file": "slides/01-cover.html", "chrome": "none", "notes": "Bron: R1" },
    { "file": "slides/02-x.html", "notes": "Bron: R2, R5",
      "charts": [{
        "placeholder": "chart-main",
        "type": "column",
        "title": null,
        "series": [{ "name": "Reeks", "labels": ["2024", "2025"], "values": [120, 180] }],
        "axis": { "catTitle": "Jaar", "valTitle": "Aantal", "valMin": 0, "valMax": 200, "majorUnit": 50 },
        "colors": ["orange"]
      }] }
  ]
}
```

- `accent`: één accent per deck (default `orange`); `colors` per chart alleen bij betekenisvol
  kleurgebruik (categorieën), namen uit `palette.json` (`orange`, `grapefruit`, `royal`, `sky`,
  `emerald`, `navy`, `dark slate`).
- `chrome`: `"light"` (default: logo + oranje paginanummer), `"dark"` (wit paginanummer, geen
  logo — voor navy full-bleed), `"none"` (cover/closing).
- `notes`: speaker notes; verwijs elke claim naar bronnendossier-regels (R-id's).
- `type`: `column | stackedColumn | bar | line | area | pie | donut | scatter`. Scatter volgt de
  PptxGenJS-conventie: eerste serie = X-waarden, volgende series = Y-waarden.
- `hooks` (escape hatch): pad naar JS-module met
  `module.exports = { afterSlide: async ({ pptx, slide, entry, index, placeholders }) => {…} }`
  voor exotische slides met directe PptxGenJS-calls (bv. `slide.addTable`).

## Bouwen en de verplichte visuele loop

```powershell
node engine/web/build/build_deck.js output/<datum>-<slug>       # bouwt <slug>.pptx
python -m scripts.render output/<datum>-<slug>/<slug>.pptx output/<datum>-<slug>/renders  # vanuit engine/
python -m scripts.qa_text output/<datum>-<slug>/<slug>.pptx     # tekst-QA
```

Elke build eindigt pas na de visuele loop: render → elke PNG bekijken (cutoff, overlap,
onbalans, dode witruimte, contrast, chrome-integriteit) → HTML fixen → rebuild → re-render,
tot schoon. De buildvalidatie (overflow, gradients, tekst-buiten-tags, maatafwijking) is de
eerste QA-poort en faalt luid met alle fouten tegelijk.
````

- [ ] **Step 2: Rewrite `brand.md`** — keep the palette table and rules, replace schemeClr guidance:

````markdown
# SFNL Brand Reference (hex tokens + design rules)

> Bron: `engine/assets/palette.json` (gegenereerd uit de sjabloon-theme). CSS-tokens en de
> toegestane hex-set worden daarvan afgeleid door `engine/web/build/generate_tokens.js`
> (`engine/web/sfnl.css`, `engine/web/tokens.json`).

## Palette

| Naam | Hex | CSS-token |
|------|-----|-----------|
| Navy | #201B5C | `--sfnl-navy` |
| Dark slate | #233348 | `--sfnl-dark-slate` |
| Orange | #F87F4F | `--sfnl-orange` |
| Grapefruit | #F95D63 | `--sfnl-grapefruit` |
| Royal | #3B62C1 | `--sfnl-royal` |
| Sky | #45B6E2 | `--sfnl-sky` |
| Emerald | #6AC6BA | `--sfnl-emerald` |
| White | #FEFFFF | `--sfnl-white` |

**Accentregel:** één accent per deck (`deck.json.accent`, default orange) draagt de rode draad;
kleur codeert betekenis. Meerdere accenten alleen wanneer categorieën over veel slides terugkeren
(één vaste kleur per categorie, overal consequent).

**Tinten en schaduwen:** per kleur precomputed (`-tint80/-tint60/-tint40/-shade25`, plus greys
uit dark slate) — zelfde luminantie-wiskunde als PowerPoints lumMod/lumOff, deterministisch.
Gebruik tinten voor pastel-kaarten, shades voor donkere banden. Geen andere hex introduceren:
`qa_text` markeert alles buiten `tokens.json` als off-brand.

## Typografie

- **Alleen drie fonts:** Gotham Bold (display/koppen), Lato Light (body/labels), Montserrat
  Light (secundair/rustig). QA wijst andere fonts af.
- **Titels en subtitels altijd in ALL CAPS — in de HTML getypt.** Uitzondering: quote-slides.
- Fonts zijn lokaal geïnstalleerd, nooit embedded. Fallback-stacks in `sfnl.css` zijn alleen
  vangnet voor rendering.

## Chrome (vast op elke contentslide)

Titelblok linksboven (Gotham Bold 18pt navy, ALL CAPS) met oranje dash eronder; SFNL-logo
linksonder en oranje paginanummer rechtsonder (native geïnjecteerd door `build_deck.js`).
Full-bleed archetypes (cover, divider, closing) hebben eigen chrome-regels — zie
`engine/web/archetypes/`.

## Compositie

- 16:9, canvas 720×405pt. Eén exhibit per slide.
- **Volledige hoogte**: content vult het canvas; half-lege slides zijn een defect.
- Royale, gelijke marges (26pt zijkanten). Big-numbers-patroon voor KPI's.
- Iconen zijn inhoud, geen decoratie: gerasterde react-icons in merkkleur (`raster.js`).
````

- [ ] **Step 3: Update README.md** — replace pipeline/build sections: spec-first JSON → HTML-per-slide + deck.json; commands from the authoring guide; test commands (`python -m pytest tests/`, `npm test`); dependency setup (`npm install` + `npx playwright install chromium` in `engine/web/build`). Keep research/review/proof descriptions.

- [ ] **Step 4: Bump plugin manifests** — in both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`: `"version": "0.4.0"`, description → "Idea-to-proof pipeline for Social Finance NL branded PowerPoint decks: research (bronnendossier), storyboard, free-form HTML slide composition built via html2pptx + PptxGenJS with native editable charts, a mandatory visual render loop, adaptive review, and a full render proof." Also `grep -n "deck-spec\|build_from_spec" .claude-plugin/marketplace.json sfnl-pptx/README.md` and fix any hits.

- [ ] **Step 5: Delete deck-spec.md and commit**

```powershell
git rm "sfnl-pptx/engine/reference/deck-spec.md"
git add -A "sfnl-pptx/engine/reference" "sfnl-pptx/README.md" "sfnl-pptx/.claude-plugin" "sfnl-pptx/.codex-plugin"
git commit -m "docs(sfnl-pptx): HTML authoring guide replaces deck-spec; brand.md on hex tokens; v0.4.0"
```

---

### Task 13: Skills & agent rewrite

**Files:**
- Rewrite: `sfnl-pptx/skills/sfnl-deck/SKILL.md`
- Rewrite: `sfnl-pptx/skills/sfnl-deck-design/SKILL.md`
- Rewrite: `sfnl-pptx/skills/sfnl-deck-review/SKILL.md`
- Modify: `sfnl-pptx/skills/sfnl-deck-proof/SKILL.md` (only pipeline-path updates)
- Modify: `sfnl-pptx/agents/deck-visual-reviewer.md` (paths + fix-loop wording)
- Rewrite: `sfnl-pptx/tests/test_skills.py`
- Keep unchanged: `skills/sfnl-deck-research/SKILL.md`, `engine/reference/voice.md`.

- [ ] **Step 1: Rewrite `skills/sfnl-deck/SKILL.md`** (keep frontmatter `name`/`description` as-is):

````markdown
---
name: sfnl-deck
description: Generate a Social Finance NL branded PowerPoint deck from a brief, outline, or source documents. Use when the user wants a new SFNL/Social Finance NL presentation, slide deck, or pitch deck built from the official sjabloon. Triggers on "SFNL deck", "maak een presentatie", "nieuwe slides in huisstijl", or any request to create, not edit, an SFNL .pptx.
---

# sfnl-deck: generate an SFNL deck

Bouw consultant-kwaliteit decks door **vrije HTML-compositie per slide**, geconverteerd naar
een bewerkbare .pptx via html2pptx + PptxGenJS. Lees vóór het bouwen altijd
`engine/reference/authoring-guide.md` en `engine/web/patterns.md`.

## Pipeline

Idee → research → narrative → storyboard → HTML+deck.json → build → visuele loop → review → proof:

1. **Intake.** Brief, outline of brondocumenten. Detecteer taal (NL/EN).
2. **Research.** Hand off naar `sfnl-deck-research`: bronnendossier (feiten, cijfers, bronnen,
   viz-kandidaten) vóór er een slide bestaat. Elk cijfer op een slide traceert naar een dossierregel.
3. **Narrative en titels.** Lees `engine/reference/voice.md`. SCQA-narrative, action title per
   slide, ghost-deck-test.
4. **Storyboard.** Hand off naar `sfnl-deck-design`: per slide de layoutcompositie (regio's,
   hiërarchie, patroon uit `patterns.md` of archetype, accentgebruik, chart-kandidaten) als
   tekst-storyboard, goedgekeurd vóór er HTML wordt geschreven.
5. **Auteur HTML + deck.json.** Maak de workspace `output/<YYYY-MM-DD>-<slug>/` (kopieer
   `engine/web/sfnl.css` naar `slides/`). Eén HTML-bestand per slide vanaf `engine/web/scaffold.html`
   of een archetype; charts als `class="placeholder"` + chartspec in `deck.json`; speaker notes
   met dossier-verwijzingen in `deck.json`. Volg de harde HTML-regels uit de authoring guide
   (alle tekst in tekst-tags, geen gradients, ALL CAPS-titels getypt, geen logo/paginanummer
   in HTML).
6. **Build + visuele loop (verplicht, elke build).** `node engine/web/build/build_deck.js
   output/<datum>-<slug>`. Faalt de validatie: alle fouten in één keer fixen. Daarna renderen
   (`python -m scripts.render … renders/` vanuit `engine/`), elke PNG inspecteren of de
   `deck-visual-reviewer` dispatchen, HTML fixen, rebuilden — tot schoon. Draai ook
   `python -m scripts.qa_text` en los criticals op.
7. **Review + proof.** Hand off naar `sfnl-deck-review` (adaptieve QA) en vóór klantoplevering
   naar `sfnl-deck-proof` (volledige eindproef). Pas opleveren bij "klaar voor oplevering".

## Regels

- Chrome is heilig: titelblok + oranje dash in de HTML (scaffold), logo + paginanummer komen
  native uit de build. Full-bleed archetypes regelen hun eigen chrome (`chrome: "dark"|"none"`).
- Eén accent per deck (`deck.json.accent`); kleur codeert betekenis (`engine/reference/brand.md`).
- **Volledige hoogte**: elke contentslide vult het canvas met een echte exhibit; half-leeg of
  tekst-zonder-exhibit is een defect. Gebruik `patterns.md` als kookboek, niet als keurslijf —
  pas patronen vrij aan op de boodschap.
- Data die een grafiek verdient wordt een **native chart** (chartspec in deck.json), gevoed
  door de viz-kandidaten uit het dossier.
- Iconen zijn inhoud: rasterize react-icons in merkkleur naar `assets/` (`raster.js`).
- Node-dependencies staan in `engine/web/build/` (`npm install` + `npx playwright install
  chromium` eenmalig). Python-scripts draaien vanuit `sfnl-pptx/engine`.
````

- [ ] **Step 2: Rewrite `skills/sfnl-deck-design/SKILL.md`**:

````markdown
---
name: sfnl-deck-design
description: Work out the visual layout of every slide in an SFNL deck before writing any HTML. Use after the narrative and action titles are drafted and before authoring slides/*.html — produces a per-slide storyboard (composition, regions, pattern/archetype, accent use, chart candidates, rationale) that gets reviewed and adjusted cheaply as text before any building happens. Triggers on "werk de layout per slide uit", "storyboard", "design plan", or as step 4 of the sfnl-deck pipeline.
---

# sfnl-deck-design: componeer de slide vóór je haar bouwt

HTML schrijven zonder plan betekent designfouten ontdekken na een build+render-cyclus. Dit
skill front-loadt de compositiebeslissing in een tekst-storyboard. Denk in **layoutcompositie**
— regio's, hiërarchie, vulling van het canvas — niet in catalogus-componenten.

## Wanneer

Tussen narrative/titels en het schrijven van `slides/*.html`. Nooit rechtstreeks van titels
naar HTML. Lees eerst `engine/web/patterns.md` en bekijk `engine/web/archetypes/`.

## Stap 1: kleurmodel

- **Single-accent** (default): één `deck.json.accent` draagt de rode draad.
- **Multi-accent**: alleen bij 3+ terugkerende categorieën over veel slides (één vaste kleur
  per categorie, overal consequent; leg de mapping vast in het storyboard).

## Stap 2: storyboard per slide

| Veld | Beslissing |
|---|---|
| `file` | wordt de bestandsnaam `slides/NN-….html` |
| `action_title` | verbatim uit stap narrative |
| `archetype/patroon` | archetype (cover/divider/quote/closing/stat-banner) of patroon uit `patterns.md`, of "bespoke" |
| `compositie` | regio-indeling in woorden: kolommen/rijen, wat waar, verhouding (bv. "links 2/5 tekst, rechts 3/5 chart-placeholder") |
| `accent` | waar het accent valt (één plek per slide die de boodschap draagt) |
| `chart` | dossier-viz-kandidaat → charttype (column/line/…): wordt een chartspec in deck.json |
| `iconen/assets` | welke gerasterde iconen of pre-rendered PNGs nodig zijn |
| `chrome` | light / dark / none |
| `rationale` | één regel: waarom deze compositie de boodschap draagt |

Bespoke composities (funnel, geldstroom, stakeholderkaart, parallelle tijdlijnen) zijn welkom:
schets regio's en elementen in het storyboard zodat de HTML-stap mechanisch wordt. Complexe
native elementen (tabellen e.d.) kunnen via de per-deck hook — noteer dat expliciet.

## Stap 3: self-review van het hele storyboard

- Vult elke contentslide het canvas? Een slide die "een kaartje linksboven" is, is een defect.
- Geen twee aangrenzende slides met identieke compositie, tenzij bewust ritme (bv. KPI-reeks).
- Elke dossier-viz-kandidaat (`chart`/`kpi`) landt als native chart, big-number of stat-banner.
- Multi-accent: elke categorie overal dezelfde kleur; dividers onderling verschillend.
- Ritme over de hele deck: wissel kaarten, banners, charts, dividers — monotonie is een defect.

## Stap 4: vertaal naar HTML + deck.json

Elke storyboard-rij wordt één HTML-bestand + één `deck.json`-entry, per
`engine/reference/authoring-guide.md`. Vereist deze stap nieuw designoordeel, dan was het
storyboard onvolledig: terug naar stap 2 voor die slide.

## Handoff

Na het bouwen: `sfnl-deck-review`. Bewaar het storyboard naast de workspace — het is de snelste
uitleg waarom een slide eruitziet zoals ze eruitziet.
````

- [ ] **Step 3: Rewrite `skills/sfnl-deck-review/SKILL.md`** (render-inspect loop as its core):

````markdown
---
name: sfnl-deck-review
description: "QA-review an SFNL PowerPoint deck against the Content/Design/Coherence rubric before delivery. Use after generating or editing an SFNL deck, or when the user asks to check, review, or validate an SFNL .pptx. Core: the mandatory render-inspect-fix loop over every slide, plus cheap text QA."
---

# sfnl-deck-review: QA an SFNL deck

Score op drie assen: **Content**, **Design**, **Coherence**. Nooit succes rapporteren zonder
één afgeronde QA-pass. De kern is de **visuele loop — verplicht voor elke build en over álle
slides**, niet alleen "sensitive" slides.

## Procedure

1. **Tekst-QA, alle slides.** `python -m scripts.qa_text <deck.pptx>` (vanuit `engine/`):
   leftover scaffold-tekst, niet-ALL-CAPS-titels, off-brand fonts/kleuren (buiten
   `engine/web/tokens.json`), lege slides. Elke `critical` blokkeert: HTML fixen, rebuilden.
2. **Visuele loop, alle slides.** Render alles:
   `python -m scripts.render <deck.pptx> <workspace>/renders`. Dispatch de
   `deck-visual-reviewer` (hele-deck-pass) of inspecteer elke PNG zelf op: tekst-cutoff,
   overlap, onbalans, dode witruimte, contrast, **chrome-integriteit** (titel + dash, logo,
   paginanummer aanwezig en op hun plek), half-lege slides, monotonie. Elke bevinding: fix de
   HTML (of deck.json/chartspec) → `node engine/web/build/build_deck.js <workspace>` →
   re-render → opnieuw beoordelen. **Herhaal tot schoon.**
3. **Exhibit-check.** Elke contentslide draagt een echte exhibit die het canvas vult (kaarten,
   big numbers, chart, swimlanes, matrix, diagram). Tekst-zonder-exhibit blokkeert tenzij de
   notes uitleggen waarom dat bewust is. Check de build tegen het storyboard van
   `sfnl-deck-design`.
4. **Coherence.** Action titles in volgorde (ghost-deck-test); accentgebruik consistent met het
   gekozen kleurmodel.

## Output

Bevindingen per as met slide-nummers en severity, plus het aantal loop-rondes. Eindig met:
clear to deliver / geblokkeerd op N criticals.

## Handoff naar de eindproef

Deze review is de adaptieve QA tijdens het bouwen. Vóór klantoplevering volgt altijd
`sfnl-deck-proof`. "Review passed" betekent "klaar voor de eindproef", niet "klaar voor de klant".
````

- [ ] **Step 4: Update `skills/sfnl-deck-proof/SKILL.md`** — three surgical edits, rest unchanged:
  - Step 6 (Herstellen): replace "fix de deck-spec, rebuild" with "fix de HTML/deck.json, rebuild met `node engine/web/build/build_deck.js <workspace>`".
  - Rule "De proef beoordeelt de gebouwde .pptx, niet de spec" → "…, niet de HTML-bron".
  - Render paths: renders naar `<workspace>/renders/` (workspace = `output/<datum>-<slug>/`).

- [ ] **Step 5: Update `agents/deck-visual-reviewer.md`**:
  - Frontmatter description: replace "flagged `sensitive` in the deck-spec" phrasing with "built by the sfnl-pptx html2pptx engine; inspect all slides by default (the visual loop is mandatory for every build)".
  - Body: review mode default = **all slides**; replace "cross-check that each built slide matches its planned component and category accent" with "cross-check each built slide against its storyboard composition and accent"; add chrome-integrity to the checklist (title + dash, logo bottom-left, orange page number bottom-right — except full-bleed archetypes); replace "Do not fix the deck-spec" with "Do not fix the HTML or rebuild the deck yourself unless explicitly asked"; keep the render commands (`python -m scripts.render`) — they are unchanged.

- [ ] **Step 6: Rewrite `tests/test_skills.py`**:

```python
"""Skills/docs must reference the html2pptx pipeline and nothing retired."""
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"

RETIRED = ("build_from_spec", "deck-spec.md", "scripts.spec", "components.py",
           "find_components", "custom-freeform", "chart-native", "scripts/icons.py")


def _all_docs():
    return list(SKILLS.rglob("SKILL.md")) + [PLUGIN / "agents" / "deck-visual-reviewer.md",
                                             PLUGIN / "README.md"]


def test_all_skills_exist():
    for name in ("sfnl-deck", "sfnl-deck-research", "sfnl-deck-design",
                 "sfnl-deck-review", "sfnl-deck-proof"):
        assert (SKILLS / name / "SKILL.md").exists(), name


def test_no_doc_references_retired_engine():
    for doc in _all_docs():
        text = doc.read_text(encoding="utf-8")
        for marker in RETIRED:
            assert marker not in text, f"{doc.name} still references {marker}"


def test_deck_skill_mandates_new_pipeline():
    text = (SKILLS / "sfnl-deck" / "SKILL.md").read_text(encoding="utf-8")
    for needle in ("authoring-guide.md", "patterns.md", "build_deck.js", "visuele loop"):
        assert needle in text


def test_review_skill_mandates_full_render_loop():
    text = (SKILLS / "sfnl-deck-review" / "SKILL.md").read_text(encoding="utf-8")
    assert "scripts.render" in text and "alle slides" in text.lower()


def test_reference_docs():
    ref = PLUGIN / "engine" / "reference"
    assert (ref / "authoring-guide.md").exists()
    assert not (ref / "deck-spec.md").exists()
    assert "schemeClr" not in (ref / "brand.md").read_text(encoding="utf-8")
```

- [ ] **Step 7: Run** — `python -m pytest tests/test_skills.py -q` → PASS (fix any lingering retired references it finds, including in `sfnl-deck-research` if any). Then full suite: `python -m pytest tests/ -q` → green.

- [ ] **Step 8: Commit**

```powershell
git add -A "sfnl-pptx/skills" "sfnl-pptx/agents" "sfnl-pptx/tests/test_skills.py"
git commit -m "docs(sfnl-pptx): skills and visual-reviewer agent rewritten for the html2pptx pipeline"
```

---

### Task 14: Acceptance — demo deck through the full pipeline

**Files:**
- Create: `output/2026-07-02-sfnl-v2-demo/` (workspace; gitignored — deliverable evidence, not source)

- [ ] **Step 1: Author a 6-slide demo deck** following `sfnl-deck` end-to-end (research step may be stubbed with 3 invented dossier rows): cover (archetype), KPI row (pattern), two-column + native column chart, swimlane columns (multi-color pattern used single-accent), stat-banner, closing. Author `deck.json` with notes referencing the stub dossier rows and one slide using `chrome: "dark"` (add a divider if preferred).

- [ ] **Step 2: Build + visual loop until clean** — `node engine/web/build/build_deck.js output/2026-07-02-sfnl-v2-demo`; render all slides; inspect every PNG (or dispatch `deck-visual-reviewer`); fix HTML; rebuild; repeat. Then `python -m scripts.qa_text` → 0 critical.

- [ ] **Step 3: Acceptance checklist against the spec's pain points** — confirm on the renders: (1) layout & composition: content fills the canvas, no half-empty slides; (2) visual richness: color surfaces, big numbers, native chart present; (3) typography: Gotham/Lato/Montserrat hierarchy visible; (4) no rigid-component look. Chrome integrity on every content slide. Open the .pptx in PowerPoint once and verify text boxes/shapes/chart are editable.

- [ ] **Step 4: Report** — summarize loop rounds + findings to the user with the deck path. No commit needed (output/ is gitignored); if any engine/css fixes were made during the loop, commit those:

```powershell
git add -A "sfnl-pptx"
git commit -m "fix(sfnl-pptx): visual-loop refinements from acceptance demo deck"
```

---

## Self-Review (performed while writing)

- **Spec coverage:** §1 pipeline/workspace → Tasks 8, 12, 13; §2 design system (tokens/typography/chrome/scaffold/archetypes/patterns/icons) → Tasks 3–6; §3 build layer (vendored html2pptx Windows-adapted, build_deck.js, charts, notes, hooks, loud validation) → Tasks 1, 7, 8; §4 visual loop + qa_text → Tasks 9, 11, 13 (review skill); §5 skills/docs table → Tasks 12–13 (research/voice/proof kept per spec); §6 retirements → Task 10, tests → Tasks 3 (tokens), 8 (build + validation gate), 9 (qa rules), 11 (E2E COM smoke); Risk section → Task 2 spike. `colors.py` is retired beyond the spec's explicit list because its only consumer (qa_text) now inlines `ALLOWED_FONTS` — recorded in Global Constraints.
- **Placeholder scan:** none — all steps carry full code/content; two intentional "copy of X" fixture steps name their exact source file.
- **Type consistency:** `html2pptx(htmlFile, pres, options)` (Tasks 1→2,4,5,8); `chartArgs(spec, palette, deckAccent) → {chartKey, data, options}` (Tasks 7→8); `buildDeck(workspace)`/CLI (Tasks 8→11,12,13); tokens vars `--sfnl-<name>[-tint80|-tint60|-tint40|-shade25]`, greys `--sfnl-grey-95/85/70` (Tasks 3→4,5); `tokens.json.allowed_hex` (Tasks 3→9); chrome modes `light|dark|none` (Tasks 5→8→12); fixture slug `webdeck` (Tasks 8→11).
