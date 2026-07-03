const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('../html2pptx');

const WEB = path.join(__dirname, '..', '..');

test('every archetype converts without validation errors', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sfnl-arch-'));
  fs.copyFileSync(path.join(WEB, 'sfnl.css'), path.join(dir, 'sfnl.css'));
  // Chrome-archetypes verwijzen naar chrome/<key>.png — kopieer de assets mee,
  // net als een workspace dat doet.
  fs.cpSync(path.join(WEB, 'assets', 'chrome'), path.join(dir, 'chrome'), { recursive: true });
  const names = fs.readdirSync(path.join(WEB, 'archetypes'))
    .filter((f) => f.endsWith('.html'))
    .map((f) => f.replace(/\.html$/, ''));
  assert.ok(names.length >= 16, `expected the official archetype set, got ${names.length}`);
  for (const name of names) {
    fs.copyFileSync(path.join(WEB, 'archetypes', `${name}.html`), path.join(dir, `${name}.html`));
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    await assert.doesNotReject(() => html2pptx(path.join(dir, `${name}.html`), pptx), `${name} failed`);
  }
});
