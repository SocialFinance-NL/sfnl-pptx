# Editing existing SFNL PowerPoints

This guide is for `.pptx` files that do not have an HTML/`deck.json` source workspace. If the
deck was built by `sfnl-deck` and the workspace still exists, edit the HTML and rebuild instead.

## Workspace discipline

Create an edit workspace such as `output/2026-07-03-klantdeck-edit/` and copy the user's file to
`original.pptx`. Every script writes a new file:

```bash
cd sfnl-pptx/engine
python -m scripts.inventory ../../output/.../original.pptx ../../output/.../text-inventory.json
python -m scripts.rearrange ../../output/.../original.pptx ../../output/.../reordered.pptx 0,2,2,1
python -m scripts.replace ../../output/.../reordered.pptx ../../output/.../replacements.json ../../output/.../edited.pptx
python -m scripts.qa_text ../../output/.../edited.pptx
python -m scripts.render ../../output/.../edited.pptx ../../output/.../renders
```

Never overwrite `original.pptx` unless the user explicitly asks for that final copy step.

## Inventory and replacements

`scripts.inventory` emits slide entries with stable `id` values for text-bearing content shapes:

```json
{
  "slides": [
    {
      "index": 0,
      "shapes": [
        {
          "id": 0,
          "left_pt": 36,
          "top_pt": 48,
          "width_pt": 360,
          "height_pt": 42,
          "paragraphs": [
            {"text": "OUDE TITEL", "font_name": "Gotham Bold", "font_size_pt": 18}
          ]
        }
      ]
    }
  ]
}
```

Use those same slide/shape ids in a replacement plan. Include every content shape whose text must
remain; omitted shapes are cleared deliberately so stale text cannot survive an edit unnoticed.

```json
{
  "slides": [
    {
      "index": 0,
      "shapes": [
        {
          "id": 0,
          "paragraphs": [
            {
              "text": "NIEUWE ACTIETITEL",
              "font_name": "Gotham Bold",
              "font_size_pt": 18,
              "bold": true,
              "color": "201B5C"
            }
          ]
        }
      ]
    }
  ]
}
```

`replace.py` does not silently fix brand issues. Keep fonts/colors intentional and let
`scripts.qa_text` catch off-brand leftovers.

## Slide operations

`scripts.rearrange` takes a 0-based sequence into the original deck. Repeating an index duplicates
that slide; leaving an index out deletes it.

```bash
python -m scripts.rearrange original.pptx reordered.pptx 0,3,3,1
```

This writes four slides: original slide 0, original slide 3, a duplicate of original slide 3, and
original slide 1.

## Official chrome slides

Use `scripts.insert_chrome_slide` for official covers, dividers and quote slides. It reads
`engine/web/assets/chrome/manifest.json` and the matching PNG assets, then adds editable text boxes
for manifest slots.

```bash
python -m scripts.insert_chrome_slide original.pptx with-divider.pptx divider-01 2 \
  --title "NIEUWE FASE" --body "Korte introductie"
```

The target deck must match the manifest canvas size. A mismatch fails loudly instead of stretching
the artwork.

## OOXML escape hatch

Use this only for edits the python-pptx scripts cannot reach: tables, charts, grouped shapes,
image swaps, or specific XML attributes.

```bash
python -m ooxml.scripts.unpack edited.pptx ooxml-work
# make one targeted XML edit
python -m ooxml.scripts.validate ooxml-work
python -m ooxml.scripts.pack ooxml-work edited-ooxml.pptx
```

`validate.py` checks XML well-formedness, relationship targets and duplicate slide/master/layout
ids. It is not full XSD schema validation. After packing, still run `scripts.qa_text` and
`scripts.render`; PowerPoint rendering is the real end-to-end check.
