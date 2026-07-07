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
  // asymmetric padding maps to pptxgenjs margin order [top, right, bottom, left]
  // fixture: padding: 4px 10px 6px 2px → pt = px * 0.75
  assert.deepEqual(rows[1][0].options.margin, [3, 7.5, 4.5, 1.5]);
});

test('table ending too close to the bottom edge fails loudly', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  await assert.rejects(
    () => html2pptx(fixture('table-bottom-overflow.html'), pptx),
    /too close to bottom edge/i
  );
});

test('nested tables and sub-10pt cell text fail loudly', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  await assert.rejects(
    () => html2pptx(fixture('table-invalid.html'), pptx),
    /(nested table|10pt)/i
  );
});

test('sfnl-table presets style header, section, total and value cells', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  const { slide } = await html2pptx(fixture('table-styled.html'), pptx);
  const rows = slide._slideObjects.find((o) => o._type === 'table').arrTabRows;
  assert.equal(rows[0][0].options.fill.color.toUpperCase(), '201B5C');   // navy header
  assert.equal(rows[0][0].options.color.toUpperCase(), 'FEFFFF');
  assert.equal(rows[1][0].options.colspan, 3);                            // section row spans
  assert.equal(rows[1][0].options.fill.color.toUpperCase(), 'C6C3ED');    // section row --sfnl-navy-tint80
  assert.equal(rows[2][1].options.align, 'right');                        // col-num
  assert.equal(rows[2][1].options.color.toUpperCase(), 'F95D63');         // val-cost grapefruit
  assert.equal(rows[3][1].options.color.toUpperCase(), '6AC6BA');         // val-benefit emerald
  assert.equal(rows[4][0].options.fill.color.toUpperCase(), '201B5C');    // navy total band
  assert.ok(rows[4][0].options.bold, 'total row bold');
  assert.ok(rows[2][2].options.fontSize <= 10.5, 'source column smaller');
});
