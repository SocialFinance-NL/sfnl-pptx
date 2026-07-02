const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { tint, shade, buildTokens } = require('../generate_tokens');

test('tint/shade boundary behaviour', () => {
  assert.equal(tint('F87F4F', 100), 'FFFFFF');
  assert.equal(tint('F87F4F', 0), 'F87F4F');
  assert.equal(shade('F87F4F', 100), '000000');
  assert.equal(shade('F87F4F', 0), 'F87F4F');
});

test('tint lightens monotonically, shade darkens, deterministic', () => {
  const lum = (hex) => [hex.slice(0, 2), hex.slice(2, 4), hex.slice(4, 6)]
    .map((c) => parseInt(c, 16)).reduce((a, b) => a + b, 0);
  assert.ok(lum(tint('3B62C1', 80)) > lum(tint('3B62C1', 40)));
  assert.ok(lum(tint('3B62C1', 40)) > lum('3B62C1'));
  assert.ok(lum(shade('3B62C1', 25)) < lum('3B62C1'));
  assert.equal(tint('6AC6BA', 60), tint('6AC6BA', 60));
});

test('buildTokens covers every brand color with tints and greys', () => {
  const palette = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', '..', 'assets', 'palette.json'), 'utf-8'));
  const tokens = buildTokens(palette);
  for (const name of ['navy', 'dark-slate', 'orange', 'grapefruit', 'royal', 'sky', 'emerald', 'white']) {
    assert.ok(tokens[`--sfnl-${name}`], `missing --sfnl-${name}`);
  }
  assert.ok(tokens['--sfnl-orange-tint80']);
  assert.ok(tokens['--sfnl-navy-shade25']);
  assert.ok(tokens['--sfnl-grey-95']);
  assert.ok(!tokens['--sfnl-white-tint80'], 'white gets no tints');
});
