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
  // 'number': alleen oranje paginanummer — voor sjabloonslides die hun eigen
  // logo al in het ontwerp dragen (zie assets/chrome/manifest.json).
  if (mode !== 'dark' && mode !== 'number') slide.addImage({ path: LOGO, ...LOGO_POS });
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
