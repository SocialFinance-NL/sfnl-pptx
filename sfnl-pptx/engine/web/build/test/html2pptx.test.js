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
