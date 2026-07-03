---
name: sfnl-deck-edit
description: "Edit an existing SFNL PowerPoint that has no HTML/deck.json source. Use when the user wants changes to a hand-built or older SFNL .pptx: text edits, slide reorder/duplicate/delete, official cover/divider/quote insertion, or targeted OOXML edits. Always backup original.pptx, then run qa_text and render."
---

# sfnl-deck-edit: bestaande SFNL PowerPoint aanpassen

Gebruik deze skill voor een bestaande SFNL `.pptx` **zonder HTML-bron**. Denk aan een handmatig
gemaakte deck, een oud bestand, of een PowerPoint die buiten de `sfnl-deck` pipeline is aangepast.

Niet gebruiken wanneer er nog een bijbehorende `output/<datum>-<slug>/slides/*.html` workspace is.
Dan blijft HTML de source of truth: gebruik `sfnl-deck-review` of `sfnl-deck-design`, pas de HTML
aan en rebuild.

## Workflow

1. **Applicability check.** Vraag of zoek of er een HTML/`deck.json` workspace bij de deck hoort.
   Als die bestaat: stop deze workflow en ga terug naar de HTML-pipeline.
2. **Snapshot.** Maak `output/<datum>-<slug>-edit/` en kopieer de doeldeck daarheen als
   `original.pptx`. Overschrijf de originele user-file nooit in-place.
3. **Inventory.** Draai vanuit `sfnl-pptx/engine`:
   `python -m scripts.inventory <workspace>/original.pptx <workspace>/text-inventory.json`.
   Lees de JSON volledig. Noteer bestaande off-slide/overlap issues en duidelijk off-brand
   fonts/kleuren voordat je edits doet.
4. **Editplan afspreken.** Leg vast welke slides/shapes tekst krijgen, welke slides worden
   verplaatst/gedupliceerd/verwijderd, of er een officiele cover/divider/quote bij moet, en of
   een OOXML escape hatch nodig is.
5. **Apply in stabiele volgorde.**
   - Nieuwe officiele chrome-slide: `python -m scripts.insert_chrome_slide`.
   - Slidevolgorde/duplicatie/deletie: `python -m scripts.rearrange`.
   - Nieuwe inventory op het tussenresultaat.
   - Tekstedits: `python -m scripts.replace`, met een replacement JSON op basis van de verse
     inventory.
   - Tabellen, charts, grouped shapes, images of andere XML-only edits: `python -m
     ooxml.scripts.unpack` -> gerichte XML-edit -> `python -m ooxml.scripts.validate` -> `python
     -m ooxml.scripts.pack`. Valideer na elke losse XML-ingreep.
6. **QA verplicht.** Draai altijd `python -m scripts.qa_text <edited.pptx>`. Los alle `critical`
   findings op. Render daarna alle aangeraakte deckversies met
   `python -m scripts.render <edited.pptx> <workspace>/renders` en inspecteer de geraakte slides
   visueel, of dispatch `deck-visual-reviewer` voor een hele-deck-pass.
7. **Rapportage.** Geef het pad naar de edited `.pptx`, vat per slide samen wat is aangepast en
   vermeld openstaande waarschuwingen. Alleen op expliciet verzoek van de user mag de originele
   file worden overschreven.

## Tools

- `scripts.inventory`: tekst, positie, formatting, off-slide en overlap inventariseren.
- `scripts.replace`: tekst volgens inventory shape-id's vervangen; niet genoemde content-shapes
  worden leeg gemaakt.
- `scripts.rearrange`: slides herordenen, dupliceren of verwijderen via een index-sequence.
- `scripts.insert_chrome_slide`: officiele cover/divider/quote uit
  `engine/web/assets/chrome/manifest.json` invoegen.
- `ooxml.scripts.unpack`, `validate`, `pack`: escape hatch voor edits die python-pptx niet kan
  bereiken.
- `scripts.qa_text` en `scripts.render`: verplicht na elke editronde.

Zie `engine/reference/editing-guide.md` voor concrete JSON-vormen, commandovoorbeelden en
OOXML-regels.
