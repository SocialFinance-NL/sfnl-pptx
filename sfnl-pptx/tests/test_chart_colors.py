import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "engine" / "web" / "build"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node unavailable")


def test_chart_spec_accepts_neutral_alias():
    script = """
    const { chartArgs } = require('./chart_spec');
    const palette = require('../../assets/palette.json');
    const spec = { type: 'column', colors: ['neutral', 'orange'], series: [
      { name: 'A', labels: ['M1'], values: [1] },
      { name: 'B', labels: ['M1'], values: [2] }
    ]};
    const out = chartArgs(spec, palette, 'orange');
    console.log(JSON.stringify(out.options.chartColors));
    """
    res = subprocess.run([NODE, "-e", script], cwd=BUILD, capture_output=True, text=True, timeout=30)
    assert res.returncode == 0, res.stderr
    colors = json.loads(res.stdout)
    assert colors[0] == "233348"
    assert colors[1] == "F87F4F"
