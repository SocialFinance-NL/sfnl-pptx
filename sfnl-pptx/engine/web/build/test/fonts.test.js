const test = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const os = require('node:os');
const { spawnSync } = require('node:child_process');
const pptxgen = require('pptxgenjs');
const html2pptx = require('../html2pptx');

test('brand fonts land as fontFace in the pptx XML', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  await html2pptx(path.join(__dirname, 'fixtures', 'spike-fonts.html'), pptx);
  const out = path.join(os.tmpdir(), `sfnl-spike-${process.pid}.pptx`);
  await pptx.writeFile({ fileName: out });
  const py = spawnSync('python', ['-c', `
import zipfile, sys
x = zipfile.ZipFile(sys.argv[1]).read('ppt/slides/slide1.xml').decode('utf-8')
for f in ("Gotham Bold", "Lato Light", "Montserrat Light"):
    assert f in x, f
print("ok")
`, out], { encoding: 'utf-8' });
  assert.match(py.stdout, /ok/, new Error(py.stderr));
});
