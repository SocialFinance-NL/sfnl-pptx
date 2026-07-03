---
name: sfnl-deck-proof
description: Volledige eindproef van een SFNL-deck vóór oplevering aan de klant. Rendert álle slides naar PNG, laat de deck-visual-reviewer de hele deck visueel beoordelen, controleert alle cijfers tegen het bronnendossier en levert een proefrapport plus definitieve .pptx. Gebruik als laatste stap van de sfnl-deck pipeline, of wanneer de gebruiker zegt "final proof", "klaar voor de klant", "maak het af", "eindcheck", of "kan dit de deur uit".
---

# sfnl-deck-proof: de eindproef

`sfnl-deck-review` is de adaptieve QA tijdens het bouwen. Deze skill is de **eindproef**: de
laatste, volledige controle voordat een deck naar een klant gaat. Geen sampling, geen "alleen
sensitive slides" — alles wordt gerenderd en bekeken.

## Procedure

1. **Voorwaarden.** De deck is gebouwd en heeft `sfnl-deck-review` doorlopen zonder critical
   findings. Zo niet: eerst terug naar review.
2. **PowerPoint-validatie + volledige render.** Run `python -m scripts.render --check`; bij
   beschikbare PowerPoint COM eerst
   `python -m scripts.render --assert-layouts <deck.pptx> 31` om de ingebedde SFNL-layoutgalerij
   in echte PowerPoint te valideren. Daarna
   render álle slides: `python -m scripts.render <deck.pptx> <workspace>/renders` (workspace =
   `output/<datum>-<slug>/`). Is COM niet beschikbaar
   (geen Windows/PowerPoint), meld dan expliciet dat de visuele eindproef niet kon draaien.
   Lever niet op: geen PowerPoint-render = verdict `GEBLOKKEERD`. A fallback based on Codex artifact-tool PPTX
   screenshots, HTML screenshots, or text QA must be listed under `Niet uitgevoerd` and cannot be
   called ready for delivery; note this as `render niet beschikbaar`.
3. **Visuele proef, hele deck.** Dispatch de `deck-visual-reviewer` subagent met het .pptx-pad
   en expliciet **alle** slide-indices (proof-modus). De agent beoordeelt elke slide op overflow,
   overlap, uitlijning, merkregels, kale slides, monotonie en accent-consistentie, en rapporteert
   per slide — ook de schone slides.
4. **Feitenproef.** Is er een bronnendossier (`output/research/<slug>-dossier.md`)? Loop dan elk
   cijfer en elke feitelijke claim op de slides na tegen het dossier. Een cijfer zonder
   dossierregel is een critical finding. Controleer ook of speaker notes de bronverwijzingen
   dragen. Geen dossier? Noteer in het rapport dat de feitenproef niet uitgevoerd kon worden.
5. **Taalproef.** Loop alle slide-teksten na op taalfouten, inconsistente spelling (NL/EN mix),
   dubbele spaties en afgebroken zinnen. Controleer of alle action titles nog kloppen met wat de
   slide daadwerkelijk toont.
6. **Herstellen en herhalen.** Elke critical finding: fix de HTML/deck.json, rebuild met
   `node engine/web/build/build_deck.js <workspace>`, re-render de
   betrokken slides en laat ze opnieuw beoordelen. Herhaal tot nul critical findings.
7. **Proefrapport.** Schrijf `output/<slug>-proefrapport.md`:

```markdown
# Proefrapport: <dektitel>
Datum: <datum> · Deck: <pad> · Slides: <N> · Rondes: <n>

## Verdict: KLAAR VOOR OPLEVERING | GEBLOKKEERD

## Visuele proef (per slide)
| Slide | Status | Bevinding |
|-------|--------|-----------|

## Feitenproef
| Slide | Cijfer/claim | Dossierregel | Status |

## Taalproef
<bevindingen of "geen">

## Niet uitgevoerd
<bijv. render niet beschikbaar — expliciet benoemen>
```

## Regels

- Nooit "klaar voor oplevering" rapporteren met openstaande critical findings of een
  overgeslagen proef die niet in het rapport staat.
- De proef beoordeelt de gebouwde .pptx, niet de HTML-bron: wat de klant ziet is leidend.
- Maximaal drie herstelrondes; daarna de resterende bevindingen expliciet aan de gebruiker
  voorleggen in plaats van eindeloos itereren.
