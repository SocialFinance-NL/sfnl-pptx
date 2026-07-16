# Content-slides erven de echte `[Titel, subtitel]`-layout

## Probleem

Covers, dividers en quotes zijn *waarheidsgetrouw* aan het officiële SFNL-sjabloon: `extract_chrome.py`
rendert de echte sjabloonslide naar een PNG-achtergrond en legt titel/subtitel in de exacte
placeholder-posities van de master. **Content-slides niet.** Die krijgen hun chrome uit een met de
hand geschreven CSS-nabootsing in `sfnl.css`:

- `.chrome-header` met een vaste marge van 26pt, `.slide-title`, `.slide-subtitle`;
- `.dash` — een oranje rechthoek van `18pt × 2pt`.

`merge_template.py` bedt de echte sjabloon-masters/-layouts wél in de output in, maar puur zodat ze
in PowerPoint's *Nieuwe dia*-galerij verschijnen. De gegenereerde content-slides **gebruiken die
layouts nooit**. Elke oranje lijn, titelpositie en logo op een content-slide wordt dus door de engine
opnieuw uitgevonden en dryft weg van het sjabloon. Dat is de verloren "truthfulness to the template".

De echte structuur in Master 1, layout **`[Titel, subtitel]`** (bron-inches):

| Element | Geometrie (bron in) | Wat het is |
|---|---|---|
| `Title 1` (ph) | 0.479, 0.60, 12.52 × 0.367 | titel-placeholder |
| `Text Placeholder 2` (ph) | 0.479, 1.037, 12.52 × 0.626 | subtitel-placeholder |
| `Rectangle 11` | 0.56, **1.718**, 0.276 × 0.058 | **de oranje lijn** (kleine dash) |
| logo `Picture 4` (master) | 0.361, 7.069, 1.102 × 0.295 | logo linksonder |
| slidenummer (master) | 12.6, 7.125 | paginanummer rechtsonder |

De template-structuur is precies het mentale model van de gebruiker: titel, subtitel, een kleine
oranje dash op ~1.72″ vanaf boven, en **daaronder leeg wit canvas** tot de footer.

## Doel

Content-slides stoppen met het uitvinden van chrome en **erven** de echte `[Titel, subtitel]`-layout
(al ingebed door `merge_template.py`). De oranje dash, het logo en het paginanummer komen dan
rechtstreeks uit layout/master — de engine tekent ze niet meer. Titel en subtitel worden placeholders
die geometrie en typografie van de master erven. Alles onder de dash is een gedefinieerd wit
**canvas** dat zowel de bestaande exhibit-grammatica als vrije, bespoke illustraties draagt.

Dit is expliciet het stuk dat in `2026-07-03-sfnl-template-layout-embed-design.md` buiten scope was
gezet ("het daadwerkelijk gebruiken van de geïmporteerde layouts door de generatie-pipeline zelf").

## Scope

- Alleen `chrome: light` content-slides. Covers/dividers/quotes (`none`/`dark`/`number`) blijven
  ongewijzigd via de bestaande chrome-archetypes.
- Chrome (dash/logo/paginanummer) komt via **layout-rebind** — dat is de kern.
- Titel/subtitel worden bij voorkeur echte placeholders; met een geautomatiseerde fallback naar
  vaste tekstvakken op master-geometrie als PowerPoint een reparatieprompt geeft.
- Canvas onder de dash draagt exhibit-grammatica **én** bespoke illustraties.
- Buiten scope: covers/dividers/quotes; herbouw op python-pptx; het cureren van de layoutset
  (blijft de volledige set uit de vorige iteratie).

## Architectuur

### 1. Chrome via overerving (de rebind)

Een post-build stap, ingebouwd in / naast `merge_template.py` (daar zijn de ingebedde layout-partnamen
al bekend via `layout_map`):

1. Identificeer content-slides. `build_deck.js` markeert ze — praktisch: elke slide met
   `chrome === 'light'` (de default). De markering wordt doorgegeven aan de merge-stap via een
   zijkanaal (een lijst 1-based slide-indexen, geschreven naast de deck of meegegeven als argument).
2. Herricht de `slideLayout`-relatie van elke content-slide → de ingebedde
   `[Titel, subtitel]`-layoutpart. De layout hangt onder de ingebedde sjabloon-master; de
   rel-keten slide → layout → master → theme wordt volledig consistent gemaakt.
3. Converteer de titel/subtitel-shapes naar placeholders (`<p:ph type="title"/>`,
   `<p:ph type="body" idx="1"/>`), tekst behouden, harde CSS-geometrie en run-typografie strippen
   zodat ze layoutgeometrie en -stijl erven.

De engine **tekent niet meer**: de `.dash`, en in `addChrome` het logo + paginanummer voor
`light`-slides (die erven nu).

**Kleurveiligheid:** `html2pptx.js` emit overal expliciete hex (`rgbToHex(...)`), geen `schemeClr`.
Het overzetten van content-slides naar het sjabloon-theme verschuift dus geen enkele
content-kleur. (Geverifieerd in de codebase.)

**Fallback (automatisch, gestuurd door de render-check):** als placeholder-conversie een
PowerPoint-reparatieprompt oplevert, val terug op titel/subtitel als vrije tekstvakken op de exacte
master-geometrie (0.479/0.60 en 0.479/1.037) met master-typografie. De layout-rebind (en dus
dash/logo/paginanummer) blijft in beide gevallen intact. Visueel identiek, semantisch iets minder.

### 2. Het canvas-contract

Een canvas-box afgeleid van de master-geometrie: bovenkant net onder de dash (~96pt in de
720×405pt HTML-canvas), zijmarges ~26pt, onderkant bij de footer (~370pt). `<main class="content">`
verankert aan deze box. Twee modi bestaan naast elkaar binnen het canvas:

- **Exhibit-grammatica** (ongewijzigd): cards / tiles / chips / stat-cards / charts stromen binnen
  het canvas.
- **Bespoke illustratielaag**: absoluut gepositioneerde custom shapes / lijnen / connectors (de
  engine converteert die al) binnen de canvas-grenzen — een gedocumenteerd affordance met expliciete
  bounds zodat illustraties nooit botsen met de geërfde chrome.

### 3. Eén bron van waarheid voor de geometrie

`extract_chrome.py` voegt `[Titel, subtitel]` (en `[Leeg]`) toe als `kind: "content"`-varianten in
`manifest.json`, met de titel/subtitel-slots, dash-geometrie, canvas-box en logo/paginanummer.
De engine en de skills lezen die getallen uit het manifest in plaats van hardgecodeerde CSS/JS.

## Wijzigingen per bestand

- `engine/scripts/extract_chrome.py` — `[Titel, subtitel]` + `[Leeg]` als `content`-varianten;
  canvas-box in het manifest.
- `engine/web/build/build_deck.js` — `addChrome` slaat logo/paginanummer over voor content-slides;
  content-slides worden gemarkeerd en de markering gaat naar de merge-stap.
- `engine/scripts/merge_template.py` (of een broer-module die het aanroept) — de rebind- en
  placeholder-conversie-logica; assertie dat elke content-slide de `[Titel, subtitel]`-layout
  resolvet.
- `engine/web/sfnl.css` — `.chrome-header`/`.dash` verwijderen; `.canvas`-regio en
  illustratie-affordances toevoegen.
- `engine/web/archetypes/` — n.v.t. (content heeft geen PNG-archetype), maar een korte content-notitie.
- `skills/sfnl-deck-design` (authoring notes) — het nieuwe content-contract en de
  canvas/illustratie-vocabulaire documenteren.
- Fixtures — bestaande `webdeck`-fixtures aanpassen aan het nieuwe content-contract; een fixture
  met één exhibit-grammatica-slide en één bespoke-illustratie-slide toevoegen.

## Verificatie

- `merge_template` round-trip: assert dat elke content-slide-rel `[Titel, subtitel]` resolvet;
  echte-PowerPoint-render-check (geen reparatieprompt) — dit stuurt ook de fallback-keuze.
- `deck-visual-reviewer`-loop over álle slides: dash/logo/paginanummer verschijnen exact één keer
  (niet dubbel), titel/subtitel op master-positie, canvas-content binnen bounds, geen ghost-prompt
  ("Klik om titel toe te voegen").
- Bestaande pytest-suite blijft groen; nieuwe assertions voor de rebind.

## Risico's

- **Rel-keten-consistentie**: de slide-layout hangt nu onder de sjabloon-master; de
  PptxGenJS-gegenereerde master/layout mag niet dangling achterblijven op een manier die PowerPoint
  afkeurt. Afgedekt door round-trip + echte-PowerPoint-render.
- **Ghost-prompttekst**: geërfde lege placeholders kunnen prompttekst tonen. We vullen ze, maar
  verifieer geen ghosts op deels gevulde slides.
- **Dubbele chrome**: als het strippen van de engine-getekende `.dash`/logo onvolledig is, verschijnt
  chrome dubbel. De visuele review vangt dit.
