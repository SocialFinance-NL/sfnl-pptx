"""Load the bundled SFNL template as a clean, editable python-pptx Presentation.

The bundled `sfnl-template.pptx` is a one-slide-per-layout sampler exported from
the official sjabloon. It opens directly in python-pptx (unlike a .potx) and
carries the brand theme, both masters, and all 30 layouts. We strip its sampler
slides and their relationships so the build starts from an empty deck; the masters
and layouts remain. The relationships are dropped to ensure orphan slide parts are
not re-serialized on save. The bundled file on disk is never modified — stripping
happens on the in-memory Presentation copy.
"""
from __future__ import annotations

from pathlib import Path

from pptx import Presentation

TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "assets" / "sfnl-template.pptx"


def load_template_presentation() -> Presentation:
    """Open the bundled template and remove all sampler slides (layouts kept)."""
    prs = Presentation(str(TEMPLATE_PATH))
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        prs.part.drop_rel(sldId.rId)   # drop the rel so the orphan slide part is not serialized
        sldIdLst.remove(sldId)
    return prs
