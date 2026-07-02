/* Map SFNL chart-spec JSON (deck.json slides[].charts[]) to PptxGenJS addChart args.
   Colors are always brand hex WITHOUT '#' (with '#' the file corrupts). */
const TYPE_MAP = {
  column: ['BAR', { barDir: 'col' }],
  stackedColumn: ['BAR', { barDir: 'col', barGrouping: 'stacked' }],
  bar: ['BAR', { barDir: 'bar' }],
  line: ['LINE', { lineSize: 3 }],
  area: ['AREA', {}],
  pie: ['PIE', { showPercent: true }],
  donut: ['DOUGHNUT', { showPercent: true, holeSize: 60 }],
  scatter: ['SCATTER', { lineSize: 0, lineDataSymbol: 'circle', lineDataSymbolSize: 6 }],
};

function colorHex(palette, name) {
  const slot = palette.by_name[name];
  if (!slot) throw new Error(`unknown color name "${name}" (allowed: ${Object.keys(palette.by_name).join(', ')})`);
  return palette.by_slot[slot].hex.toUpperCase();
}

function chartArgs(spec, palette, deckAccent) {
  if (!TYPE_MAP[spec.type]) {
    throw new Error(`unknown chart type "${spec.type}" (allowed: ${Object.keys(TYPE_MAP).join(', ')})`);
  }
  const [chartKey, typeOpts] = TYPE_MAP[spec.type];
  const colors = (spec.colors && spec.colors.length ? spec.colors : [deckAccent]).map((n) => colorHex(palette, n));
  const data = spec.series.map((s) => ({ name: s.name, labels: s.labels, values: s.values }));
  const options = {
    ...typeOpts,
    chartColors: colors,
    dataLabelFontFace: 'Lato Light',
    catAxisLabelFontFace: 'Lato Light',
    valAxisLabelFontFace: 'Lato Light',
  };
  options.showLegend = ['pie', 'donut'].includes(spec.type) || data.length > 1;
  if (spec.title) {
    options.showTitle = true;
    options.title = spec.title;
    options.titleFontFace = 'Gotham Bold';
    options.titleColor = '201B5C';
    options.titleFontSize = 12;
  }
  const ax = spec.axis || {};
  if (ax.catTitle) { options.showCatAxisTitle = true; options.catAxisTitle = ax.catTitle; }
  if (ax.valTitle) { options.showValAxisTitle = true; options.valAxisTitle = ax.valTitle; }
  if (ax.valMin != null) options.valAxisMinVal = ax.valMin;
  if (ax.valMax != null) options.valAxisMaxVal = ax.valMax;
  if (ax.majorUnit != null) options.valAxisMajorUnit = ax.majorUnit;
  return { chartKey, data, options };
}

module.exports = { chartArgs, TYPE_MAP };
