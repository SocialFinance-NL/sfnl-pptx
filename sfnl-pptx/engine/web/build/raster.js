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
  await sharp(Buffer.from(svg))
    .resize(sizePx, sizePx, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png().toFile(outFile);
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
