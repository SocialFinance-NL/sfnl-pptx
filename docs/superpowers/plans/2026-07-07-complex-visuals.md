# Consultant-grade visuals (tabellen, shapes, connectors) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** De sfnl-pptx html2pptx-engine leert native PowerPoint-tabellen, een shape-vocabulaire (chevron/pill/circle/blokpijlen) en connectors met labels; de designtaal wordt herijkt op de exhibit-galerij.

**Architecture:** Alle nieuwe visuals blijven bewerkbare native shapes. HTML blijft het enige authoring-oppervlak: de Playwright-extractie in `html2pptx.js` leest computed styles (dus SFNL-tabelpresets zijn pure CSS), connectorrouting is een pure-Node module (`connectors.js`) die uit gerenderde elementposities lijnsegmenten plant. Patterns/skills verwijzen naar de exhibit-galerij (`engine/reference/exhibits/`).

**Tech Stack:** Node (playwright, pptxgenjs 4.x, `node --test`), Python (pytest + python-pptx) voor e2e, CSS custom properties.

**Spec:** `docs/superpowers/specs/2026-07-07-complex-visuals-design.md`

## Global Constraints

- Repo-root: `C:\Users\XavierFriesen\.projects SFNL\Powerpoints design`; alle paden hieronder relatief daaraan.
- Node-tests draaien vanuit `sfnl-pptx/engine/web/build` met `node --test` (of `node --test test/<file>.test.js` voor één bestand).
- Python-tests vanuit `sfnl-pptx` met `python -m pytest tests/<file> -v`.
- Buildvalidatie faalt **luid en verzameld** (errors-array, alles tegelijk), zoals bestaande validaties in `html2pptx.js`.
- Kleuren altijd via `sfnl.css` custom properties / `palette.json`-namen; nooit nieuwe hexwaarden verzinnen.
- Canvas is 720pt × 405pt (`LAYOUT_16x9`, 10in × 5.625in); tekst >12pt eindigt ≥0.5in boven de onderrand (bestaande check; geldt niet voor tabelcellen — tabellen hebben een eigen 0.3in-marge-check).
- Covers/dividers/quotes blijven ongewijzigd uit de officiële chrome-archetypes.
- Commit na elke taak; commitprefix `feat(sfnl-pptx):` / `docs(sfnl-pptx):` / `test(sfnl-pptx):`.

---

### Task 1: `<table>` → native PptxGenJS-tabel (extractie + rendering + validatie)

**Files:**
- Modify: `sfnl-pptx/engine/web/build/html2pptx.js` (extractSlideData ± regel 604, addElements ± regel 141)
- Test: `sfnl-pptx/engine/web/build/test/tables.test.js` (nieuw)
- Create: `sfnl-pptx/engine/web/build/test/fixtures/table-basic.html`
- Create: `sfnl-pptx/engine/web/build/test/fixtures/table-invalid.html`

**Interfaces:**
- Consumes: bestaande `extractSlideData`-helpers (`pxToInch`, `pxToPoints`, `rgbToHex`, `parseInlineFormatting`, `errors`-array).
- Produces: elementtype `{ type: 'table', position: {x,y,w,h}, colW: number[] (inches), rowH: number[] (inches), rows: Cell[][] }` met `Cell = { text: TextRun[], options: { fill?, color, bold, fontSize, fontFace, align, valign, colspan?, border? } }`. Rendering via `targetSlide.addTable(rows, {...})`. Latere taken (2, 5) bouwen hierop met pure CSS.

- [ ] **Step 1: Schrijf de failing tests**

`sfnl-pptx/engine/web/build/test/fixtures/table-basic.html`:

```html
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../../../sfnl.css">
<style>
  body { width: 720pt; height: 405pt; margin: 0; position: relative; }
  table { position: absolute; left: 40pt; top: 40pt; width: 640pt; border-collapse: collapse; }
  th { background: var(--sfnl-orange); color: #FEFFFF; font-family: 'Montserrat Light'; font-size: 11pt; text-align: left; padding: 6pt; }
  td { font-family: 'Lato Light'; font-size: 11pt; color: var(--sfnl-dark-slate); padding: 6pt; border-bottom: 1pt solid var(--sfnl-orange-tint80); }
  td.num { text-align: right; }
</style></head>
<body>
  <table>
    <tr><th>Indicator</th><th>Doel</th><th>Waarde</th></tr>
    <tr><td>Bereik</td><td>Instroom per cohort</td><td class="num">686</td></tr>
    <tr><td>Kosten</td><td><b>Totale kosten</b> per jaar</td><td class="num">€ 84.000</td></tr>
  </table>
</body></html>
```

`sfnl-pptx/engine/web/build/test/fixtures/table-invalid.html` (geneste tabel + te kleine celtekst):

```html
<!DOCTYPE html>
<html><head><style>
  body { width: 720pt; height: 405pt; margin: 0; position: relative; }
  table { position: absolute; left: 40pt; top: 40pt; width: 400pt; border-collapse: collapse; }
  td { font-size: 8pt; padding: 4pt; }
</style></head>
<body>
  <table>
    <tr><td>Buitencel<table><tr><td>binnen</td></tr></table></td></tr>
  </table>
</body></html>
```

`sfnl-pptx/engine/web/build/test/tables.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('../html2pptx');

const fixture = (name) => path.join(__dirname, 'fixtures', name);

test('converts <table> to a native pptx table with styled cells', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  const { slide } = await html2pptx(fixture('table-basic.html'), pptx);
  const tables = slide._slideObjects.filter((o) => o._type === 'table');
  assert.equal(tables.length, 1, 'one native table expected');
  const rows = tables[0].arrTabRows;
  assert.equal(rows.length, 3);
  assert.equal(rows[0].length, 3);
  // header cell: orange fill, white text
  assert.equal(rows[0][0].options.fill.color.toUpperCase(), 'F87F4F');
  assert.equal(rows[0][0].options.color.toUpperCase(), 'FEFFFF');
  // numeric cell right-aligned
  assert.equal(rows[1][2].options.align, 'right');
  // inline bold survives as run
  const boldCell = rows[2][1];
  assert.ok(boldCell.text.some((r) => r.options && r.options.bold), 'bold run expected');
});

test('nested tables and sub-10pt cell text fail loudly', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  await assert.rejects(
    () => html2pptx(fixture('table-invalid.html'), pptx),
    /(nested table|10pt)/i
  );
});
```

- [ ] **Step 2: Run tests, verifieer dat ze falen**

Run (vanuit `sfnl-pptx/engine/web/build`): `node --test test/tables.test.js`
Expected: FAIL — eerste test vindt 0 tabellen (huidige code negeert `<table>` of struikelt over unwrapped text), tweede test rejects niet op het juiste patroon.

- [ ] **Step 3: Implementeer tabel-extractie in `extractSlideData`**

In `html2pptx.js`, in de `document.querySelectorAll('*').forEach`-loop, **vóór** het DIV-shape-blok (`// Extract DIVs with backgrounds/borders as shapes`, ± regel 604), voeg toe:

```js
      // Extract <table> as native pptx table
      if (el.tagName === 'TABLE') {
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) { processed.add(el); return; }

        if (el.querySelector('table')) {
          errors.push('Nested tables are not supported. Flatten the inner table.');
          processed.add(el);
          el.querySelectorAll('*').forEach((child) => processed.add(child));
          return;
        }

        const bottomEdgeIn = pxToInch(rect.top + rect.height);
        const slideHeightIn = document.body.getBoundingClientRect().height / PX_PER_IN;
        if (slideHeightIn - bottomEdgeIn < 0.3) {
          errors.push(`Table ends too close to bottom edge (${(slideHeightIn - bottomEdgeIn).toFixed(2)}" from bottom, minimum 0.3" required)`);
        }

        const trs = Array.from(el.querySelectorAll('tr'));
        const rows = [];
        const rowH = [];
        let colW = null;

        trs.forEach((tr) => {
          const cells = Array.from(tr.children).filter((c) => c.tagName === 'TD' || c.tagName === 'TH');
          if (!cells.length) return;
          rowH.push(pxToInch(tr.getBoundingClientRect().height));
          if (!colW && !cells.some((c) => c.colSpan > 1)) {
            colW = cells.map((c) => pxToInch(c.getBoundingClientRect().width));
          }
          const row = cells.map((cell) => {
            const cs = window.getComputedStyle(cell);
            const fontSize = pxToPoints(cs.fontSize);
            if (fontSize < 10) {
              errors.push(`Table cell "${cell.textContent.trim().substring(0, 30)}" uses ${fontSize.toFixed(1)}pt; minimum 10pt in tables.`);
            }
            const cellTransform = cs.textTransform;
            const runs = parseInlineFormatting(cell, {}, [], (s) => applyTextTransform(s, cellTransform));
            const border = ['Top', 'Right', 'Bottom', 'Left'].map((side) => {
              const w = parseFloat(cs[`border${side}Width`]) || 0;
              return w > 0
                ? { type: 'solid', color: rgbToHex(cs[`border${side}Color`]), pt: w * PT_PER_PX }
                : { type: 'none' };
            });
            const isBold = cs.fontWeight === 'bold' || parseInt(cs.fontWeight) >= 600;
            const hasBg = cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)';
            const options = {
              color: rgbToHex(cs.color),
              bold: isBold,
              fontSize,
              fontFace: cs.fontFamily.split(',')[0].replace(/['"]/g, '').trim(),
              align: cs.textAlign === 'start' ? 'left' : cs.textAlign,
              valign: 'middle',
              border,
              margin: [pxToPoints(cs.paddingLeft), pxToPoints(cs.paddingRight), pxToPoints(cs.paddingBottom), pxToPoints(cs.paddingTop)]
            };
            if (hasBg) options.fill = { color: rgbToHex(cs.backgroundColor) };
            if (cell.colSpan > 1) options.colspan = cell.colSpan;
            return { text: runs.length ? runs : [{ text: '', options: {} }], options };
          });
          rows.push(row);
        });

        elements.push({
          type: 'table',
          position: { x: pxToInch(rect.left), y: pxToInch(rect.top), w: pxToInch(rect.width), h: pxToInch(rect.height) },
          colW, rowH, rows
        });
        el.querySelectorAll('*').forEach((child) => processed.add(child));
        processed.add(el);
        return;
      }
```

Belangrijk: het tekst-validatieblok bovenaan de loop (`textTags.includes(el.tagName)` → "has background/border") slaat cellen nu automatisch over omdat alle table-descendants via `processed` gemarkeerd worden — maar dat blok draait **vóór** de processed-check niet: de `if (processed.has(el)) return;` staat al als eerste regel, en tabellen worden eerder bezocht dan hun kinderen (document order), dus dit werkt. `TD`/`TH` staan bovendien niet in `textTags`.

- [ ] **Step 4: Implementeer tabel-rendering in `addElements`**

In `html2pptx.js` in `addElements` (± regel 142), voeg vóór `} else if (el.type === 'line')` een branch toe:

```js
    } else if (el.type === 'table') {
      const tableOptions = {
        x: el.position.x,
        y: el.position.y,
        w: el.position.w,
        rowH: el.rowH,
        autoPage: false
      };
      if (el.colW) tableOptions.colW = el.colW;
      targetSlide.addTable(el.rows, tableOptions);
    } else if (el.type === 'line') {
```

(pas de bestaande `if (el.type === 'image')`-keten hierop aan; `addTable` krijgt per cel de `options.border`/`fill`/`margin` uit de extractie.)

- [ ] **Step 5: Run tests, verifieer dat ze slagen**

Run: `node --test test/tables.test.js`
Expected: PASS (2 tests). Run ook `node --test` volledig — bestaande tests blijven groen.

- [ ] **Step 6: Commit**

```bash
git add sfnl-pptx/engine/web/build/html2pptx.js sfnl-pptx/engine/web/build/test/tables.test.js sfnl-pptx/engine/web/build/test/fixtures/table-basic.html sfnl-pptx/engine/web/build/test/fixtures/table-invalid.html
git commit -m "feat(sfnl-pptx): convert <table> to native editable pptx tables"
```

---

### Task 2: SFNL-tabelpresets in sfnl.css (pure CSS, geleerd uit de exhibits)

**Files:**
- Modify: `sfnl-pptx/engine/web/sfnl.css` (append na bestaande frame-klassen)
- Test: `sfnl-pptx/engine/web/build/test/tables.test.js` (test toevoegen)
- Create: `sfnl-pptx/engine/web/build/test/fixtures/table-styled.html`

**Interfaces:**
- Consumes: Task 1-tabelconversie; bestaande tint-tokens (`--sfnl-*-tint80`).
- Produces: CSS-klassen `sfnl-table` (+ accent `orange|royal|teal|navy`), rijklassen `section-row`, `total-row`, celklassen `col-num`, `val-cost`, `val-benefit`, `col-source`. Taken 5-7 gebruiken exact deze namen.

- [ ] **Step 1: Schrijf de failing test**

`sfnl-pptx/engine/web/build/test/fixtures/table-styled.html`:

```html
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="../../../sfnl.css">
<style>body { width: 720pt; height: 405pt; margin: 0; position: relative; }
  table { position: absolute; left: 40pt; top: 40pt; width: 640pt; }</style></head>
<body>
  <table class="sfnl-table navy">
    <tr><th>Variabele</th><th class="col-num">Waarde</th><th class="col-source">Bron</th></tr>
    <tr class="section-row"><td colspan="3">Kosten</td></tr>
    <tr><td>Zorgkosten diagnostiek</td><td class="col-num val-cost">€ 679.745</td><td class="col-source">NZa 2025</td></tr>
    <tr><td>Vermeden zorgkosten</td><td class="col-num val-benefit">€ 260.590</td><td class="col-source">NZa 2025</td></tr>
    <tr class="total-row"><td>Netto resultaat</td><td class="col-num">€ 4,0 mln</td><td></td></tr>
  </table>
</body></html>
```

Append aan `test/tables.test.js`:

```js
test('sfnl-table presets style header, section, total and value cells', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  const { slide } = await html2pptx(fixture('table-styled.html'), pptx);
  const rows = slide._slideObjects.find((o) => o._type === 'table').arrTabRows;
  assert.equal(rows[0][0].options.fill.color.toUpperCase(), '201B5C');   // navy header
  assert.equal(rows[0][0].options.color.toUpperCase(), 'FEFFFF');
  assert.equal(rows[1][0].options.colspan, 3);                            // section row spans
  assert.ok(rows[1][0].options.fill, 'section row is tinted');
  assert.equal(rows[2][1].options.align, 'right');                        // col-num
  assert.equal(rows[2][1].options.color.toUpperCase(), 'F95D63');         // val-cost grapefruit
  assert.equal(rows[3][1].options.color.toUpperCase(), '6AC6BA');         // val-benefit emerald
  assert.equal(rows[4][0].options.fill.color.toUpperCase(), '201B5C');    // navy total band
  assert.ok(rows[4][0].options.bold, 'total row bold');
  assert.ok(rows[2][2].options.fontSize <= 10.5, 'source column smaller');
});
```

- [ ] **Step 2: Run test, verifieer dat hij faalt**

Run: `node --test test/tables.test.js`
Expected: FAIL — klassen bestaan nog niet, header heeft geen fill.

- [ ] **Step 3: Voeg de presets toe aan sfnl.css**

Append aan `sfnl-pptx/engine/web/sfnl.css`:

```css
/* ── SFNL tabellen (grammatica uit engine/reference/exhibits/) ─────────── */
.sfnl-table { border-collapse: collapse; }
.sfnl-table th, .sfnl-table td {
  font-family: 'Lato Light', sans-serif; font-size: 11pt;
  color: var(--sfnl-dark-slate); text-align: left; padding: 5pt 7pt;
}
.sfnl-table th {
  font-family: 'Montserrat Light', sans-serif; color: #FEFFFF;
  text-transform: uppercase; letter-spacing: 0.06em;
}
.sfnl-table.orange th { background: var(--sfnl-orange); }
.sfnl-table.royal  th { background: var(--sfnl-royal); }
.sfnl-table.teal   th { background: var(--sfnl-emerald); }
.sfnl-table.navy   th { background: var(--sfnl-navy); }
.sfnl-table td { border-bottom: 1pt solid var(--sfnl-dark-slate-tint80); }
.sfnl-table tr.section-row td {
  font-family: 'Montserrat Light', sans-serif; font-weight: 600; border-bottom: none;
}
.sfnl-table.orange tr.section-row td { background: var(--sfnl-orange-tint80); }
.sfnl-table.royal  tr.section-row td { background: var(--sfnl-royal-tint80); }
.sfnl-table.teal   tr.section-row td { background: var(--sfnl-emerald-tint80); }
.sfnl-table.navy   tr.section-row td { background: var(--sfnl-navy-tint80); }
.sfnl-table tr.total-row td {
  background: var(--sfnl-navy); color: #FEFFFF; font-weight: 700; border-bottom: none;
}
.sfnl-table .col-num { text-align: right; }
.sfnl-table .val-cost { color: var(--sfnl-grapefruit); font-weight: 600; }
.sfnl-table .val-benefit { color: var(--sfnl-emerald); font-weight: 600; }
.sfnl-table .col-source { font-size: 10pt; color: var(--sfnl-dark-slate-tint40); }
```

Controleer eerst met `grep -n "emerald" sfnl-pptx/engine/web/sfnl.css` welke emerald-tokennamen bestaan (`--sfnl-emerald`, `--sfnl-emerald-tint80`); gebruik de bestaande namen exact.

- [ ] **Step 4: Run tests, verifieer dat ze slagen**

Run: `node --test test/tables.test.js`
Expected: PASS (3 tests).

- [ ] **Step 5: Run de Python CSS-designsysteemtest**

Run (vanuit `sfnl-pptx`): `python -m pytest tests/test_design_system_css.py tests/test_tokens.py -v`
Expected: PASS — nieuwe klassen breken geen tokenchecks. Faalt er iets op verwachte klassenlijsten, voeg de nieuwe klassen daar toe.

- [ ] **Step 6: Commit**

```bash
git add sfnl-pptx/engine/web/sfnl.css sfnl-pptx/engine/web/build/test/tables.test.js sfnl-pptx/engine/web/build/test/fixtures/table-styled.html
git commit -m "feat(sfnl-pptx): SFNL table style presets (header/section/total/value cells)"
```

---

### Task 3: shape-vocabulaire via `data-shape`

**Files:**
- Modify: `sfnl-pptx/engine/web/build/html2pptx.js` (DIV-shape-blok in extractSlideData; addElements)
- Test: `sfnl-pptx/engine/web/build/test/shapes.test.js` (nieuw)
- Create: `sfnl-pptx/engine/web/build/test/fixtures/shapes.html`

**Interfaces:**
- Consumes: bestaand DIV-shape-extractiepad (fill/border/shadow/rectRadius).
- Produces: `el.shape.shapeType` (string) op shape-elementen; toegestane waarden `chevron | pill | circle | arrow-right | arrow-left | arrow-up | arrow-down`. Mapping naar PptxGenJS: `chevron→chevron`, `circle→ellipse`, `pill→roundRect (rectRadius = h/2)`, `arrow-*→rightArrow/leftArrow/upArrow/downArrow`. Task 4/5 gebruiken `data-shape` in fixtures.

- [ ] **Step 1: Schrijf de failing tests**

`sfnl-pptx/engine/web/build/test/fixtures/shapes.html`:

```html
<!DOCTYPE html>
<html><head><style>
  body { width: 720pt; height: 405pt; margin: 0; position: relative; }
  div[data-shape] { position: absolute; }
</style></head>
<body>
  <div data-shape="chevron" style="left:40pt;top:60pt;width:180pt;height:40pt;background:#F87F4F;"><p style="color:#FEFFFF;font-size:12pt;">FASE 1</p></div>
  <div data-shape="arrow-right" style="left:240pt;top:60pt;width:80pt;height:40pt;background:#C6C3ED;"></div>
  <div data-shape="pill" style="left:340pt;top:60pt;width:140pt;height:30pt;background:#3B62C1;"><p style="color:#FEFFFF;font-size:11pt;">OUTCOME</p></div>
  <div data-shape="circle" style="left:520pt;top:55pt;width:40pt;height:40pt;background:#6AC6BA;"><p style="color:#FEFFFF;font-size:14pt;text-align:center;">1</p></div>
</body></html>
```

`sfnl-pptx/engine/web/build/test/shapes.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('../html2pptx');

const fixture = (name) => path.join(__dirname, 'fixtures', name);

test('data-shape divs become native chevron/arrow/pill/circle shapes', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  const { slide } = await html2pptx(fixture('shapes.html'), pptx);
  const shapes = slide._slideObjects.filter((o) => o.shape || (o.options && o.options.shape));
  const shapeNames = shapes.map((o) => (o.shape || o.options.shape));
  assert.ok(shapeNames.includes('chevron'), 'chevron present');
  assert.ok(shapeNames.includes('rightArrow'), 'rightArrow present');
  assert.ok(shapeNames.includes('ellipse'), 'ellipse present');
  const pill = shapes.find((o) => (o.shape || o.options.shape) === 'roundRect');
  assert.ok(pill, 'pill as roundRect present');
});

test('unknown data-shape fails loudly', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  const html = fixture('shapes-unknown.html');
  const fs = require('node:fs');
  fs.writeFileSync(html, `<!DOCTYPE html><html><head><style>body{width:720pt;height:405pt;margin:0;}</style></head><body><div data-shape="hexagon" style="position:absolute;left:10pt;top:10pt;width:50pt;height:50pt;background:#F87F4F;"></div></body></html>`);
  await assert.rejects(() => html2pptx(html, pptx), /data-shape "hexagon"/);
  fs.unlinkSync(html);
});
```

Let op: inspecteer bij het draaien hoe pptxgenjs 4.x het shapetype op het slide-object opslaat (`o.shape`, `o.options.shape` of `o._shape`); pas de assert-helper daarop aan — de bedoeling van de test (4 shapetypes aanwezig) blijft gelijk.

- [ ] **Step 2: Run tests, verifieer dat ze falen**

Run: `node --test test/shapes.test.js`
Expected: FAIL — alle shapes komen nu als `rect` uit de conversie; unknown-shape werpt niets.

- [ ] **Step 3: Implementeer in extractSlideData en addElements**

In het DIV-shape-blok van `extractSlideData` (bij `if (hasBg || hasUniformBorder) { elements.push({ type: 'shape', ... })`), voeg vóór de push toe:

```js
            const SHAPE_MAP = {
              'chevron': 'chevron', 'pill': 'pill', 'circle': 'ellipse',
              'arrow-right': 'rightArrow', 'arrow-left': 'leftArrow',
              'arrow-up': 'upArrow', 'arrow-down': 'downArrow'
            };
            let shapeType = null;
            if (el.dataset && el.dataset.shape) {
              shapeType = SHAPE_MAP[el.dataset.shape];
              if (!shapeType) {
                errors.push(`Unknown data-shape "${el.dataset.shape}". Allowed: ${Object.keys(SHAPE_MAP).join(', ')}.`);
              }
            }
```

en neem `shapeType` op in het shape-object: `shape: { shapeType, fill: ..., ... }`.

Zorg ook dat een `data-shape`-div **zonder** background/border toch als shape geëxtraheerd wordt: verruim de conditie `if (hasBg || hasBorder)` naar `if (hasBg || hasBorder || (el.dataset && el.dataset.shape))`.

In `addElements` (shape-branch, ± regel 160), vervang de shape-keuze:

```js
      const st = el.shape.shapeType;
      let pptxShape;
      if (st === 'pill') {
        pptxShape = pres.ShapeType.roundRect;
      } else if (st) {
        pptxShape = pres.ShapeType[st];
      } else {
        pptxShape = el.shape.rectRadius > 0 ? pres.ShapeType.roundRect : pres.ShapeType.rect;
      }
      const shapeOptions = { x: el.position.x, y: el.position.y, w: el.position.w, h: el.position.h, shape: pptxShape };
      if (st === 'pill') shapeOptions.rectRadius = el.position.h / 2;
```

- [ ] **Step 4: Run tests, verifieer dat ze slagen**

Run: `node --test test/shapes.test.js` → PASS. Run `node --test` volledig → alles groen.

- [ ] **Step 5: Commit**

```bash
git add sfnl-pptx/engine/web/build/html2pptx.js sfnl-pptx/engine/web/build/test/shapes.test.js sfnl-pptx/engine/web/build/test/fixtures/shapes.html
git commit -m "feat(sfnl-pptx): data-shape vocabulary (chevron, pill, circle, block arrows)"
```

---

### Task 4: connectors tussen benoemde nodes

**Files:**
- Create: `sfnl-pptx/engine/web/build/connectors.js`
- Modify: `sfnl-pptx/engine/web/build/html2pptx.js` (node-rects verzamelen; connectors renderen)
- Test: `sfnl-pptx/engine/web/build/test/connectors.test.js` (nieuw)
- Create: `sfnl-pptx/engine/web/build/test/fixtures/connectors.html`

**Interfaces:**
- Consumes: elementposities (inches) uit extractSlideData; `data-connectors` JSON op `<body>`.
- Produces: `connectors.js` exporteert `planConnector(fromRect, toRect, opts)` → `{ segments: [{x1,y1,x2,y2}], labelPos: {x,y} }` waarbij rects `{x,y,w,h}` in inches zijn en `opts = { route: 'straight'|'elbow' }`. extractSlideData levert extra veld `slideData.nodes = { [id]: {x,y,w,h} }` en `slideData.connectors = [{from,to,route,color,width,dashed,arrow,label}]`. Task 5 gebruikt de HTML-syntax.

Connector-syntax (op `<body>`):

```html
<body data-connectors='[
  {"from":"n1","to":"n2","route":"elbow","color":"201B5C","arrow":true,"label":"50%"},
  {"from":"n2","to":"n3","dashed":true}
]'>
```

Defaults: `route:"straight"`, `color:"201B5C"` (navy), `width:1.5` (pt), `dashed:false`, `arrow:true`, `label:null`.

- [ ] **Step 1: Schrijf failing unit-tests voor de routeringsgeometrie**

`sfnl-pptx/engine/web/build/test/connectors.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const pptxgen = require('pptxgenjs');
const { planConnector } = require('../connectors');
const html2pptx = require('../html2pptx');

const fixture = (name) => path.join(__dirname, 'fixtures', name);

test('straight connector: box left of box → right edge to left edge', () => {
  const from = { x: 1, y: 1, w: 1, h: 0.5 };
  const to = { x: 3, y: 1, w: 1, h: 0.5 };
  const { segments, labelPos } = planConnector(from, to, { route: 'straight' });
  assert.equal(segments.length, 1);
  assert.deepEqual(segments[0], { x1: 2, y1: 1.25, x2: 3, y2: 1.25 });
  assert.ok(Math.abs(labelPos.x - 2.5) < 1e-9);
});

test('straight connector: box above box → bottom edge to top edge', () => {
  const from = { x: 1, y: 1, w: 1, h: 0.5 };
  const to = { x: 1, y: 3, w: 1, h: 0.5 };
  const { segments } = planConnector(from, to, { route: 'straight' });
  assert.deepEqual(segments[0], { x1: 1.5, y1: 1.5, x2: 1.5, y2: 3 });
});

test('elbow connector: horizontal-vertical-horizontal, 3 segments', () => {
  const from = { x: 1, y: 1, w: 1, h: 0.5 };
  const to = { x: 4, y: 3, w: 1, h: 0.5 };
  const { segments } = planConnector(from, to, { route: 'elbow' });
  assert.equal(segments.length, 3);
  const midX = 3; // halverwege 2 (from right) en 4 (to left)
  assert.deepEqual(segments[0], { x1: 2, y1: 1.25, x2: midX, y2: 1.25 });
  assert.deepEqual(segments[1], { x1: midX, y1: 1.25, x2: midX, y2: 3.25 });
  assert.deepEqual(segments[2], { x1: midX, y1: 3.25, x2: 5, y2: 3.25 });
});

test('connector to unknown id fails the build loudly', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  await assert.rejects(() => html2pptx(fixture('connectors-bad.html'), pptx), /unknown node id "ghost"/i);
});

test('e2e: connectors render as line shapes with arrowheads and label', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  const { slide } = await html2pptx(fixture('connectors.html'), pptx);
  const lines = slide._slideObjects.filter((o) => (o.shape || (o.options && o.options.shape)) === 'line');
  assert.ok(lines.length >= 2, 'expected connector line segments');
  const texts = slide._slideObjects.filter((o) => o._type === 'text');
  assert.ok(texts.some((t) => JSON.stringify(t.text).includes('50%')), 'connector label rendered');
});
```

`test/fixtures/connectors.html`:

```html
<!DOCTYPE html>
<html><head><style>
  body { width: 720pt; height: 405pt; margin: 0; position: relative; }
  .node { position: absolute; width: 140pt; height: 50pt; background: #3B62C1; border-radius: 6pt; }
  .node p { color: #FEFFFF; font-size: 11pt; padding: 6pt; }
</style></head>
<body data-connectors='[{"from":"n1","to":"n2","label":"50%"},{"from":"n1","to":"n3","route":"elbow","dashed":true}]'>
  <div id="n1" class="node" style="left:60pt;top:80pt;"><p>Diagnostiek</p></div>
  <div id="n2" class="node" style="left:320pt;top:80pt;"><p>Familieonderzoek</p></div>
  <div id="n3" class="node" style="left:320pt;top:220pt;"><p>Geen onderzoek</p></div>
</body></html>
```

`test/fixtures/connectors-bad.html`: kopie van bovenstaand maar met `{"from":"n1","to":"ghost"}` en alleen node n1.

- [ ] **Step 2: Run tests, verifieer dat ze falen**

Run: `node --test test/connectors.test.js`
Expected: FAIL — `../connectors` bestaat niet (module not found).

- [ ] **Step 3: Implementeer `connectors.js` (pure geometrie)**

```js
/** connectors.js — plan connector line segments between two rects (inches). */
function centers(r) {
  return {
    left:   { x: r.x,          y: r.y + r.h / 2 },
    right:  { x: r.x + r.w,    y: r.y + r.h / 2 },
    top:    { x: r.x + r.w / 2, y: r.y },
    bottom: { x: r.x + r.w / 2, y: r.y + r.h }
  };
}

function pickAnchors(from, to) {
  const f = centers(from);
  const t = centers(to);
  const dx = (to.x + to.w / 2) - (from.x + from.w / 2);
  const dy = (to.y + to.h / 2) - (from.y + from.h / 2);
  if (Math.abs(dx) >= Math.abs(dy)) {
    return dx >= 0 ? { start: f.right, end: t.left, axis: 'h' } : { start: f.left, end: t.right, axis: 'h' };
  }
  return dy >= 0 ? { start: f.bottom, end: t.top, axis: 'v' } : { start: f.top, end: t.bottom, axis: 'v' };
}

function planConnector(from, to, opts = {}) {
  const { start, end, axis } = pickAnchors(from, to);
  const route = opts.route || 'straight';
  let segments;
  if (route === 'elbow' && (Math.abs(start.x - end.x) > 1e-6 && Math.abs(start.y - end.y) > 1e-6)) {
    if (axis === 'h') {
      const midX = (start.x + end.x) / 2;
      segments = [
        { x1: start.x, y1: start.y, x2: midX, y2: start.y },
        { x1: midX, y1: start.y, x2: midX, y2: end.y },
        { x1: midX, y1: end.y, x2: end.x, y2: end.y }
      ];
    } else {
      const midY = (start.y + end.y) / 2;
      segments = [
        { x1: start.x, y1: start.y, x2: start.x, y2: midY },
        { x1: start.x, y1: midY, x2: end.x, y2: midY },
        { x1: end.x, y1: midY, x2: end.x, y2: end.y }
      ];
    }
  } else {
    segments = [{ x1: start.x, y1: start.y, x2: end.x, y2: end.y }];
  }
  const mid = segments[Math.floor(segments.length / 2)];
  const labelPos = { x: (mid.x1 + mid.x2) / 2, y: (mid.y1 + mid.y2) / 2 };
  return { segments, labelPos };
}

module.exports = { planConnector };
```

- [ ] **Step 4: Run de geometrie-tests**

Run: `node --test test/connectors.test.js`
Expected: eerste 3 tests PASS; de 2 html2pptx-tests falen nog.

- [ ] **Step 5: Integreer in html2pptx.js**

In `extractSlideData`, na de element-loop en vóór `return { background, ... }`:

```js
    // Collect node rects (elements with an id) and connector spec from <body>
    const nodes = {};
    document.querySelectorAll('[id]').forEach((n) => {
      const r = n.getBoundingClientRect();
      if (r.width > 0 && r.height > 0) {
        nodes[n.id] = { x: pxToInch(r.left), y: pxToInch(r.top), w: pxToInch(r.width), h: pxToInch(r.height) };
      }
    });
    let connectors = [];
    if (document.body.dataset.connectors) {
      try {
        connectors = JSON.parse(document.body.dataset.connectors);
      } catch (e) {
        errors.push(`data-connectors is not valid JSON: ${e.message}`);
      }
      for (const c of connectors) {
        if (!nodes[c.from]) errors.push(`data-connectors: unknown node id "${c.from}"`);
        if (!nodes[c.to]) errors.push(`data-connectors: unknown node id "${c.to}"`);
      }
    }
```

en breid de return uit: `return { background, elements, placeholders, errors, nodes, connectors };`

In `html2pptx` (Node-kant), na `addElements(slideData, targetSlide, pres);`:

```js
    const { planConnector } = require('./connectors');
    for (const c of slideData.connectors || []) {
      const { segments, labelPos } = planConnector(slideData.nodes[c.from], slideData.nodes[c.to], { route: c.route });
      segments.forEach((s, idx) => {
        const isLast = idx === segments.length - 1;
        const line = { color: c.color || '201B5C', width: c.width || 1.5 };
        if (c.dashed) line.dashType = 'dash';
        if (isLast && c.arrow !== false) line.endArrowType = 'triangle';
        targetSlide.addShape(pres.ShapeType.line, {
          x: Math.min(s.x1, s.x2), y: Math.min(s.y1, s.y2),
          w: Math.abs(s.x2 - s.x1), h: Math.abs(s.y2 - s.y1),
          flipH: s.x2 < s.x1, flipV: s.y2 < s.y1,
          line
        });
      });
      if (c.label) {
        targetSlide.addText(c.label, {
          x: labelPos.x - 0.35, y: labelPos.y - 0.22, w: 0.7, h: 0.2,
          fontSize: 9, fontFace: 'Montserrat Light', align: 'center',
          color: c.color || '201B5C'
        });
      }
    }
```

(verplaats de `require` naar de top van het bestand naast de andere requires.)

- [ ] **Step 6: Run alle connector-tests**

Run: `node --test test/connectors.test.js` → PASS (5 tests). Run `node --test` volledig → groen.

- [ ] **Step 7: Commit**

```bash
git add sfnl-pptx/engine/web/build/connectors.js sfnl-pptx/engine/web/build/html2pptx.js sfnl-pptx/engine/web/build/test/connectors.test.js sfnl-pptx/engine/web/build/test/fixtures/connectors.html sfnl-pptx/engine/web/build/test/fixtures/connectors-bad.html
git commit -m "feat(sfnl-pptx): named-node connectors with elbow routing, arrowheads and labels"
```

---

### Task 5: e2e fixture-decks (tabelzwaar + diagramzwaar) door de volledige build

**Files:**
- Create: `sfnl-pptx/tests/fixtures/webdeck-visuals/deck.json`
- Create: `sfnl-pptx/tests/fixtures/webdeck-visuals/slides/01-tables.html`
- Create: `sfnl-pptx/tests/fixtures/webdeck-visuals/slides/02-diagram.html`
- Modify: `sfnl-pptx/tests/test_web_build.py`

**Interfaces:**
- Consumes: Task 1-4 (tabellen, presets, shapes, connectors); bestaande `_workspace`/`_build`-helpers in `test_web_build.py`.
- Produces: gevalideerd bewijs dat de hele keten (deck.json → build_deck.js → merge_template → python-pptx) de nieuwe elementen als native objecten oplevert.

- [ ] **Step 1: Maak het fixture-deck**

`deck.json`:

```json
{
  "title": "VISUALS FIXTURE",
  "slug": "webdeck-visuals",
  "language": "nl",
  "author": "Social Finance NL",
  "accent": "orange",
  "hooks": null,
  "slides": [
    { "file": "slides/01-tables.html", "notes": "tabel fixture" },
    { "file": "slides/02-diagram.html", "notes": "diagram fixture" }
  ]
}
```

`slides/01-tables.html`: kopieer de structuur van `engine/web/build/test/fixtures/table-styled.html`, maar met `<link rel="stylesheet" href="sfnl.css">` (workspace-lokaal pad, zoals de bestaande webdeck-fixture doet — check `tests/fixtures/webdeck/slides/` voor het exacte linkpad) en een titel:

```html
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="sfnl.css">
<style>body { width: 720pt; height: 405pt; margin: 0; position: relative; }
  table { position: absolute; left: 40pt; top: 90pt; width: 640pt; }
  h1 { position: absolute; left: 40pt; top: 30pt; font-family: 'Montserrat Light'; font-size: 20pt; color: var(--sfnl-navy); }
</style></head>
<body>
  <h1>RESULTAAT PER OUTCOME</h1>
  <table class="sfnl-table orange">
    <tr><th>Effect</th><th>Stakeholder</th><th class="col-num">Waarde</th><th class="col-source">Bron</th></tr>
    <tr class="section-row"><td colspan="4">Kosten</td></tr>
    <tr><td>Zorgkosten diagnostiek</td><td>Zorgverzekeraar</td><td class="col-num val-cost">€ 679.745</td><td class="col-source">NZa 2025</td></tr>
    <tr class="section-row"><td colspan="4">Baten</td></tr>
    <tr><td>Vermeden zorgkosten</td><td>Zorgverzekeraar</td><td class="col-num val-benefit">€ 260.590</td><td class="col-source">NZa 2025</td></tr>
    <tr class="total-row"><td>Netto maatschappelijk resultaat</td><td></td><td class="col-num">€ 4,0 mln</td><td></td></tr>
  </table>
</body></html>
```

`slides/02-diagram.html`:

```html
<!DOCTYPE html>
<html><head><link rel="stylesheet" href="sfnl.css">
<style>body { width: 720pt; height: 405pt; margin: 0; position: relative; }
  .node { position: absolute; width: 150pt; height: 46pt; border-radius: 6pt; }
  .node p { color: #FEFFFF; font-size: 11pt; padding: 6pt; }
  h1 { position: absolute; left: 40pt; top: 30pt; font-family: 'Montserrat Light'; font-size: 20pt; color: var(--sfnl-navy); }
</style></head>
<body data-connectors='[{"from":"d1","to":"d2","label":"60%"},{"from":"d1","to":"d3","route":"elbow","dashed":true,"label":"40%"}]'>
  <h1>SCENARIO-UITWERKING</h1>
  <div data-shape="chevron" style="position:absolute;left:40pt;top:80pt;width:160pt;height:36pt;background:var(--sfnl-orange);"><p style="color:#FEFFFF;font-size:11pt;">FASE 1</p></div>
  <div id="d1" class="node" style="left:60pt;top:160pt;background:var(--sfnl-royal);"><p>Uitvoering diagnostiek</p></div>
  <div id="d2" class="node" style="left:340pt;top:130pt;background:var(--sfnl-emerald);"><p>Erfelijke oorzaak aantoonbaar</p></div>
  <div id="d3" class="node" style="left:340pt;top:250pt;background:var(--sfnl-sky);"><p>Geen vervolgonderzoek</p></div>
</body></html>
```

Controleer de emerald/sky variabelenamen tegen `sfnl.css` en het stylesheet-linkpad tegen `tests/fixtures/webdeck/slides/*.html`; volg exact dezelfde conventie.

- [ ] **Step 2: Schrijf de failing pytest**

Append aan `sfnl-pptx/tests/test_web_build.py`:

```python
@pytest.fixture(scope="module")
def built_visuals(tmp_path_factory):
    ws = _workspace(tmp_path_factory.mktemp("webdeck-visuals"), "webdeck-visuals")
    res = _build(ws)
    assert res.returncode == 0, res.stderr + res.stdout
    return Presentation(str(ws / "webdeck-visuals.pptx"))


def test_visuals_table_is_native(built_visuals):
    slide = list(built_visuals.slides)[0]
    tables = [s for s in slide.shapes if s.has_table]
    assert len(tables) == 1
    tbl = tables[0].table
    assert len(tbl.rows) == 6
    assert "RESULTAAT" not in tbl.cell(0, 0).text  # titel staat buiten de tabel
    assert "679.745" in tbl.cell(2, 2).text


def test_visuals_diagram_has_shapes_and_connectors(built_visuals):
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    slide = list(built_visuals.slides)[1]
    autos = [s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE]
    names = {s.adjustments and s.name or s.name for s in autos}
    # chevron + 3 nodes + connectorlijnen komen als autoshapes/lines binnen
    assert len(autos) >= 4, f"expected >=4 autoshapes, got {len(autos)}: {names}"
    lines = [s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.LINE]
    assert len(lines) >= 4, "straight (1) + elbow (3) connector segments expected"
```

- [ ] **Step 3: Run de pytest, verifieer dat hij faalt**

Run (vanuit `sfnl-pptx`): `python -m pytest tests/test_web_build.py -v -k visuals`
Expected: FAIL zolang fixture-workspace nog niet bestaat/build faalt; daarna groen zonder verdere codewijziging (taken 1-4 leveren de capaciteit). Faalt de LINE-check omdat pptxgenjs lijnen als AUTO_SHAPE serialiseert: pas de assert aan op werkelijke shape_type (inspecteer met python-pptx) — de bedoeling (≥4 connectorsegmenten aanwezig) blijft.

- [ ] **Step 4: Fix eventuele integratie-issues tot de tests slagen**

Run: `python -m pytest tests/test_web_build.py -v`
Expected: PASS, inclusief de bestaande webdeck-tests.

- [ ] **Step 5: Visuele loop op het fixture-deck (handmatige poort)**

```powershell
# workspace-kopie onder output/ maken en bouwen
cp -r sfnl-pptx/tests/fixtures/webdeck-visuals output/qa-visuals
cp sfnl-pptx/engine/web/sfnl.css output/qa-visuals/slides/sfnl.css
node sfnl-pptx/engine/web/build/build_deck.js output/qa-visuals
cd sfnl-pptx/engine
python -m scripts.render ../../output/qa-visuals/webdeck-visuals.pptx ../../output/qa-visuals/renders
```

Bekijk beide PNG's (Read): tabelbanding, headerkleur, chevronvorm, pijlpunten, labelpositie. Fix afwijkingen in de conversie, niet in de fixture.

- [ ] **Step 6: Commit**

```bash
git add sfnl-pptx/tests/fixtures/webdeck-visuals sfnl-pptx/tests/test_web_build.py
git commit -m "test(sfnl-pptx): e2e fixture decks for native tables and diagram connectors"
```

---

### Task 6: designtaal-herijking — patterns.md herbouwen + component-CSS

**Files:**
- Modify: `sfnl-pptx/engine/web/sfnl.css` (kaart/tile/chip/statcard-klassen)
- Modify: `sfnl-pptx/engine/web/patterns.md` (volledig herschrijven)
- Test: `sfnl-pptx/tests/test_design_system_css.py` (bestaande checks laten slagen; nieuwe klassen toevoegen aan verwachte sets als die test klassenlijsten valideert)

**Interfaces:**
- Consumes: exhibit-galerij `sfnl-pptx/engine/reference/exhibits/manifest.md`; tabelpresets (Task 2), shapes (Task 3), connectors (Task 4).
- Produces: CSS-klassen `.card-soft`, `.icon-tile`, `.chip`, `.stat-card`, `.stat-number`, `.ladder-row`; patroonnamen die Task 7 in de skills gebruikt: `sfnl-table`, `veranderttheorie-map`, `flow-tree`, `effectenkaart`, `chevron-process`, `stat-cards`, `stakeholder-ladder`, `icon-tiles`, `chips`, `definition-box`.

- [ ] **Step 1: Voeg component-CSS toe aan sfnl.css**

Append:

```css
/* ── Componenten (grammatica uit engine/reference/exhibits/) ───────────── */
.card-soft { border-radius: 9pt; padding: 10pt 12pt; }
.icon-tile {
  border-radius: 9pt; width: 72pt; height: 72pt;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.icon-tile p { color: #FEFFFF; font-size: 10pt; margin: 2pt 0 0 0; }
.icon-tile img { width: 36pt; height: 36pt; }
.chip {
  border-radius: 4pt; width: 34pt; height: 34pt;
  display: flex; align-items: center; justify-content: center;
}
.chip p { color: #FEFFFF; font-family: 'Gotham Bold', sans-serif; font-size: 14pt; margin: 0; }
.stat-card { border-radius: 9pt; background: var(--sfnl-navy); padding: 14pt; text-align: center; }
.stat-card .stat-number { font-family: 'Gotham Bold', sans-serif; font-size: 40pt; color: var(--sfnl-orange); margin: 0; }
.stat-card p { color: #FEFFFF; font-size: 11pt; }
.ladder-row { background: var(--sfnl-dark-slate-tint80); border-radius: 4pt; padding: 8pt 12pt; display: flex; align-items: center; }
.ladder-row.total { background: var(--sfnl-navy); }
.definition-box { background: var(--sfnl-navy-tint80); border: 1pt solid var(--sfnl-navy); padding: 6pt 8pt; }
.definition-box p { font-size: 10pt; color: var(--sfnl-dark-slate); }
```

(Controleer variabelen tegen bestaande tokens; gebruik `--sfnl-lilac`-achtige tokens alleen als ze bestaan, anders `navy-tint80`.)

- [ ] **Step 2: Herschrijf patterns.md**

Vervang de inhoud volledig. Structuur (elk patroon: 1 regel doel + verwijzing naar exhibit-PNG + copy-paste HTML-fragment dat de klassen uit Step 1/Task 2-4 gebruikt):

```markdown
# SFNL layout patterns — referentiegrammatica

De maatstaf is de exhibit-galerij: `engine/reference/exhibits/` (zie manifest.md).
Bekijk (Read) het bijpassende exhibit vóór je een tabel, diagram of statcompositie bouwt.
Herbouw de grammatica op de nieuwe inhoud; kopieer nooit tekst of cijfers.

Stijlconstanten: afgeronde hoeken (~9pt) op kaarten/tiles, tabellen strak; pasteltinten
(`--sfnl-*-tint80`) als vlakvulling, volle merkkleur voor headers/chips/accenten;
rood/grapefruit=kosten/risico, teal/emerald=baten/positief, navy=totaal, oranje=resultaat,
royal/sky=proces. Titels in ALL CAPS (getypt). Iconen dragen betekenis (raster.js → PNG).

## Tabellen (`sfnl-table`) — exhibits: outcome-ledger-table, financial-table-sections, …
[fragment: de styled table uit Task 5 slide 01]

## Flow-tree / beslisboom — exhibit: scenario-decision-tree
[fragment: nodes + data-connectors uit Task 5 slide 02]

## Veranderttheorie-map — exhibit: veranderttheorie-map
[fragment: 5 kolommen met pill-headers (data-shape="pill"), gestapelde nodes, verticale
connectors, navy zijpaneel, onderband]

## Effectenkaart — exhibit: effectenkaart-matrix
[fragment: kolommen van pills, dashed scheiders via smalle div met border-left dashed,
geroteerd groepslabel via writing-mode]

## Chevron-procesband — exhibit: chevron-process
[fragment: 3 data-shape="chevron" divs + definition-boxen eronder]

## Statcomposities — exhibits: hero-stat-kpi, stat-cards-arrow, stat-cards-totalband
[fragment: stat-card grid + data-shape="arrow-right" achtergrondpijl + navy totaalband]

## Stakeholder-ladder — exhibit: stakeholder-ladder
[fragment: ladder-row's + .total]

## Icon-tiles & chips — exhibits: icon-tiles-bullets, icon-tile-grid, letter-chips, numbered-card-columns
[fragment: icon-tile + chip + genummerde kaartkolom]

## Native hook
[behoud de bestaande hook-sectie; tabellen hoeven niet meer via de hook]
```

Schrijf elk `[fragment: …]` volledig uit als werkend HTML-fragment binnen het scaffold-`<main class="content">`; hergebruik letterlijk de fixture-HTML uit Taken 2-5 waar mogelijk. Verwijder de oude regels "geen HTML `<table>`" en "2pt square-ish frames".

- [ ] **Step 3: Run de designsysteem-tests**

Run (vanuit `sfnl-pptx`): `python -m pytest tests/test_design_system_css.py tests/test_skills.py -v`
Expected: PASS. Als `test_skills.py`/`test_design_system_css.py` op verdwenen patroonzinnen asserten (bv. "geen HTML table"), werk die verwachtingen bij naar de nieuwe designtaal — de test hoort het nieuwe contract te borgen.

- [ ] **Step 4: Commit**

```bash
git add sfnl-pptx/engine/web/sfnl.css sfnl-pptx/engine/web/patterns.md sfnl-pptx/tests/test_design_system_css.py sfnl-pptx/tests/test_skills.py
git commit -m "feat(sfnl-pptx): rebuild design language on exhibit grammar (cards, tiles, chips, stat cards)"
```

---

### Task 7: skills, authoring guide, reviewer, README, versiebump

**Files:**
- Modify: `sfnl-pptx/engine/reference/authoring-guide.md`
- Modify: `sfnl-pptx/skills/sfnl-deck/SKILL.md`
- Modify: `sfnl-pptx/skills/sfnl-deck-design/SKILL.md`
- Modify: `sfnl-pptx/skills/sfnl-deck-review/SKILL.md`
- Modify: `sfnl-pptx/agents/deck-visual-reviewer.md`
- Modify: `sfnl-pptx/README.md`
- Modify: `sfnl-pptx/.claude-plugin/plugin.json` (version `0.5.1` → `0.6.0`; check ook `.codex-plugin` op een versieveld)

**Interfaces:**
- Consumes: patroonnamen uit Task 6, tabel/shape/connector-syntax uit Taken 1-4, exhibit-manifest.
- Produces: skills die de nieuwe vocabulaire kennen; geen code.

- [ ] **Step 1: Update authoring-guide.md**

In de sectie "HTML-regels": vervang de regel over `<table>` ("wordt niet ondersteund") door:

```markdown
- Tabellen: gebruik HTML `<table class="sfnl-table {orange|royal|teal|navy}">` met
  `section-row`/`total-row`-rijen en `col-num`/`val-cost`/`val-benefit`/`col-source`-cellen;
  de build converteert naar een native, bewerkbare PowerPoint-tabel. Minimaal 10pt celtekst,
  geen geneste tabellen, onderrand ≥0.3in boven de slide-rand.
- Shapes: `<div data-shape="chevron|pill|circle|arrow-right|arrow-left|arrow-up|arrow-down">`
  wordt een native autoshape; styling (fill/border) via CSS zoals bij gewone divs.
- Connectors: geef nodes een `id` en declareer op `<body>`
  `data-connectors='[{"from":"a","to":"b","route":"elbow","dashed":true,"label":"50%"}]'`
  (defaults: straight, navy, 1.5pt, arrow aan). Onbekende id's laten de build falen.
- Exhibit-galerij: bekijk vóór het bouwen van tabellen/diagrammen/statcomposities het
  bijpassende referentiebeeld in `engine/reference/exhibits/` (catalogus: `manifest.md`).
```

- [ ] **Step 2: Update de skills**

- `sfnl-deck/SKILL.md`: zelfde vier bullets (verkort) + verwijzing naar patterns.md-patroonnamen.
- `sfnl-deck-design/SKILL.md`: storyboard mag per slide een patroon uit Task 6 benoemen (`sfnl-table navy`, `flow-tree`, `effectenkaart`, `chevron-process`, `stat-cards`, `stakeholder-ladder`, `icon-tiles`, `veranderttheorie-map`); instructie: "Bekijk (Read) het bijpassende exhibit uit `engine/reference/exhibits/manifest.md` voordat je de compositie van zo'n slide vastlegt; herbouw de grammatica, kopieer nooit inhoud."
- `sfnl-deck-review/SKILL.md` en `agents/deck-visual-reviewer.md`: QA-criteria toevoegen: (a) connectors raken hun nodes (geen zwevende pijlen), (b) tabellen: geen celoverflow, consistente banding, kleurrol klopt (rood=kost, teal=baat), header in caps, (c) chevrons/pijlen wijzen in leesrichting, (d) statgetallen in Gotham Bold met correcte accentkleur, (e) vergelijk twijfelgevallen met het exhibit uit de galerij.

- [ ] **Step 3: README + versiebump**

- README: sectie "Complexe visuals" met de vier capabilities + galerijverwijzing + vertrouwelijkheidsnoot ("exhibits bevatten klantmateriaal; galerij niet publiceren buiten de privé-repo").
- `.claude-plugin/plugin.json`: `"version": "0.6.0"`. Doe hetzelfde in `.codex-plugin` als daar een versie staat (`grep -rn "0.5.1" sfnl-pptx/.claude-plugin sfnl-pptx/.codex-plugin`).

- [ ] **Step 4: Run de skill/docs-tests**

Run (vanuit `sfnl-pptx`): `python -m pytest tests/test_skills.py tests/test_voice_reference.py -v`
Expected: PASS; werk verwachtingen bij als de tests op oude formuleringen asserten.

- [ ] **Step 5: Commit**

```bash
git add sfnl-pptx/engine/reference/authoring-guide.md sfnl-pptx/skills sfnl-pptx/agents/deck-visual-reviewer.md sfnl-pptx/README.md sfnl-pptx/.claude-plugin/plugin.json sfnl-pptx/.codex-plugin
git commit -m "docs(sfnl-pptx): teach skills the complex-visuals vocabulary; bump to 0.6.0"
```

---

### Task 8: eindverificatie — demo-deck door de volledige pipeline + visuele loop

**Files:**
- Create: `output/2026-07-07-visuals-demo/` (workspace; niet committen — `output/` is werkruimte)

**Interfaces:**
- Consumes: alles uit Taken 1-7.
- Produces: gerenderd bewijs dat de nieuwe capaciteiten consultant-grade slides opleveren; go/no-go voor oplevering.

- [ ] **Step 1: Bouw een demo-deck van 5 contentslides**

Workspace aanmaken volgens authoring-guide (sfnl.css + chrome kopiëren). Slides: (1) cover uit archetype, (2) `sfnl-table orange` ledger-tabel, (3) flow-tree met elbow-connectors en percentagelabels, (4) chevron-procesband + definition-boxen, (5) stat-cards met achtergrondpijl + navy totaalband. Inhoud: fictieve maar realistische MBC-cijfers.

- [ ] **Step 2: Bouw en render**

```powershell
node sfnl-pptx/engine/web/build/build_deck.js output/2026-07-07-visuals-demo
cd sfnl-pptx/engine
python -m scripts.render ../../output/2026-07-07-visuals-demo/visuals-demo.pptx ../../output/2026-07-07-visuals-demo/renders
python -m scripts.qa_text ../../output/2026-07-07-visuals-demo/visuals-demo.pptx
python -m scripts.render --assert-layouts ../../output/2026-07-07-visuals-demo/visuals-demo.pptx 31
```

Expected: build zonder errors; 31 layouts embedded; qa_text schoon.

- [ ] **Step 3: Visuele loop via de deck-visual-reviewer agent**

Dispatch `sfnl-pptx:deck-visual-reviewer` op alle renders; vergelijk elke slide mentaal met het bijpassende exhibit. Fix → rebuild → re-render tot schoon.

- [ ] **Step 4: Open het bestand in PowerPoint en verifieer bewerkbaarheid**

Handmatige check (of via COM): dubbelklik tabelcel → tekst bewerkbaar; chevron selecteerbaar als autoshape; connectorlijn versleepbaar. Dit is het kernvereiste "editable native shapes" uit de spec.

- [ ] **Step 5: Rapporteer resultaat aan Xavier met 2-3 render-PNG's als bewijs**

Geen commit (output/ is werkruimte); wel het eindrapport in de sessie.
