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
