const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('../html2pptx');

// scaffold links sfnl.css relatively; copy both to a temp dir like a real workspace
function stageScaffold() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sfnl-scaffold-'));
  const web = path.join(__dirname, '..', '..');
  fs.copyFileSync(path.join(web, 'scaffold.html'), path.join(dir, 'slide.html'));
  fs.copyFileSync(path.join(web, 'sfnl.css'), path.join(dir, 'sfnl.css'));
  return path.join(dir, 'slide.html');
}

test('scaffold converts cleanly with title chrome', async () => {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  const { slide } = await html2pptx(stageScaffold(), pptx);
  assert.ok(slide);
  const out = path.join(os.tmpdir(), `sfnl-scaffold-${process.pid}.pptx`);
  await pptx.writeFile({ fileName: out });
  const { spawnSync } = require('node:child_process');
  const py = spawnSync('python', ['-c', `
import zipfile, sys
x = zipfile.ZipFile(sys.argv[1]).read('ppt/slides/slide1.xml').decode('utf-8')
assert "Gotham Bold" in x
assert "ACTION TITLE" in x
assert "F87F4F" in x  # orange dash shape
print("ok")
`, out], { encoding: 'utf-8' });
  assert.match(py.stdout, /ok/, new Error(py.stderr));
  fs.unlinkSync(out);
});
