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
