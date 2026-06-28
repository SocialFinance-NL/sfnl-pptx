from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from scripts.colors import set_scheme_fill, set_run_scheme_color, set_run_font, ACCENT_TO_SLOT

def _blank_slide():
    prs = Presentation()
    return prs.slides.add_slide(prs.slide_layouts[6])

def test_accent_map_covers_brand_accents():
    assert ACCENT_TO_SLOT["orange"] == "accent1"
    assert ACCENT_TO_SLOT["emerald"] == "accent5"
    assert ACCENT_TO_SLOT["navy"] == "dk2"

def test_scheme_fill_uses_schemeclr_not_hex():
    slide = _blank_slide()
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(1), Inches(2), Inches(1))
    set_scheme_fill(shp, "emerald")
    xml = shp.fill._xPr.xml
    assert "schemeClr" in xml and 'val="accent5"' in xml
    assert "srgbClr" not in xml

def test_run_font_applies_name_and_size():
    slide = _blank_slide()
    tb = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(3), Inches(1))
    run = tb.text_frame.paragraphs[0].add_run()
    run.text = "Hi"
    set_run_font(run, "Gotham Bold", size_pt=28, bold=True)
    assert run.font.name == "Gotham Bold"
    assert run.font.size == Pt(28)
    assert run.font.bold is True
