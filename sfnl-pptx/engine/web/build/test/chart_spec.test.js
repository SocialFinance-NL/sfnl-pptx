const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { chartArgs } = require('../chart_spec');

const palette = JSON.parse(fs.readFileSync(path.join(__dirname, '..', '..', '..', 'assets', 'palette.json'), 'utf-8'));
const spec = (over = {}) => ({
  placeholder: 'c1', type: 'column',
  series: [{ name: 'Deelnemers', labels: ['2024', '2025'], values: [120, 180] }],
  ...over,
});

test('column maps to BAR/col with deck accent, no # in colors', () => {
  const { chartKey, data, options } = chartArgs(spec(), palette, 'orange');
  assert.equal(chartKey, 'BAR');
  assert.equal(options.barDir, 'col');
  assert.deepEqual(options.chartColors, ['F87F4F']);
  assert.equal(options.showLegend, false);
  assert.equal(data[0].name, 'Deelnemers');
});

test('explicit color names resolve via palette; multi-series shows legend', () => {
  const s = spec({ colors: ['emerald', 'royal'], series: [
    { name: 'A', labels: ['x'], values: [1] }, { name: 'B', labels: ['x'], values: [2] }] });
  const { options } = chartArgs(s, palette, 'orange');
  assert.deepEqual(options.chartColors, ['6AC6BA', '3B62C1']);
  assert.equal(options.showLegend, true);
});

test('axis fields become pptxgenjs options', () => {
  const { options } = chartArgs(spec({ axis: { catTitle: 'Jaar', valTitle: 'Aantal', valMin: 0, valMax: 200, majorUnit: 50 } }), palette, 'orange');
  assert.equal(options.showCatAxisTitle, true);
  assert.equal(options.catAxisTitle, 'Jaar');
  assert.equal(options.valAxisMaxVal, 200);
  assert.equal(options.valAxisMajorUnit, 50);
});

test('every documented type maps; unknown type and color throw clearly', () => {
  for (const [t, key] of [['column', 'BAR'], ['stackedColumn', 'BAR'], ['bar', 'BAR'], ['line', 'LINE'], ['area', 'AREA'], ['pie', 'PIE'], ['donut', 'DOUGHNUT'], ['scatter', 'SCATTER']]) {
    assert.equal(chartArgs(spec({ type: t }), palette, 'orange').chartKey, key);
  }
  assert.throws(() => chartArgs(spec({ type: 'radar' }), palette, 'orange'), /unknown chart type/);
  assert.throws(() => chartArgs(spec({ colors: ['pink'] }), palette, 'orange'), /unknown color name/);
});
