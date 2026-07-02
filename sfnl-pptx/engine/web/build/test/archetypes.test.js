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
