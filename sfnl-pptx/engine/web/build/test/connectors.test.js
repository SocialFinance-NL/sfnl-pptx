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
  assert.deepEqual(segments[2], { x1: midX, y1: 3.25, x2: 4, y2: 3.25 });
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

test('invalid JSON in data-connectors fails loudly', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  await assert.rejects(
    () => html2pptx(fixture('connectors-invalid-json.html'), pptx),
    /not valid JSON/i
  );
});

test('connector overrides (arrow, color, width) are honored', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  const { slide } = await html2pptx(fixture('connectors-overrides.html'), pptx);
  const lines = slide._slideObjects.filter((o) => (o.shape || (o.options && o.options.shape)) === 'line');
  assert.equal(lines.length, 1, 'one connector segment expected');
  const { line } = lines[0].options;
  assert.equal(line.endArrowType, null, 'arrow: false should suppress the arrowhead');
  assert.equal(line.color.toUpperCase(), 'F87F4F');
  assert.equal(line.width, 3);
});
