# SFNL layout patterns — editorial kadergrid

Default style: every content slide has a deliberate frame structure. Avoid loose pale cards floating in whitespace. Use one full-canvas exhibit with colored kaders, bands, sidebars, evidence boxes, and clear hierarchy.

- Body text is normally 16pt Lato Light; use 18pt for sparse explanatory slides and 14pt only for dense matrices.
- Titles and subtitles remain ALL CAPS because this is a company requirement; keep them short and spacious so the caps read as brand voice.
- Gotham Bold is reserved for big numbers, official archetype slots, and short display emphasis. Do not use it as the default body/title voice.
- The orange dash is a brand marker, not the composition. The slide should still work if the dash is removed.
- Use 2pt square-ish frames and colored bands more often than soft cards.
- Semantic color mapping: orange = result/recommendation, royal/sky = process/system, emerald = managed/positive, grapefruit = risk/leak.
- Run the squint test: blurred or viewed small, the primary takeaway should still be the strongest element, followed by support and metadata.
- Every frame has a role: evidence, mechanism, risk, decision, result, or ask. Decoration-only frames fail review.

Fragmenten hieronder horen binnen het scaffold's `<main class="content">` en gelden alleen voor contentslides. Covers, sectiedividers en quotes zijn geen patroon maar een gegeven: gebruik de officiële archetypes (`archetypes/cover-*`, `divider-*`, `quote-*`; catalogus in `assets/chrome/manifest.json`) en vervang alleen de slotteksten.

Gebruik geen HTML `<table>`; bouw matrices als flex-rijen of gebruik de native per-deck hook (`slide.addTable`, zie authoring guide). Registreer chart-placeholders altijd in `deck.json` → `slides[].charts[]`. Iconen zijn inhoud, geen decoratie: rasterize betekenisvolle react-icons naar merkkleur-PNGs in de workspace `assets/` en plaats ze met `<img>`.

`.card` is alleen een lower-emphasis fallback voor kleine metadata of restinformatie. De default voor herhaalde of dragende elementen is een kader, band, sidebar, evidence box, matrixrij of verdict box.

## Framed KPI band

```html
<div class="col" style="gap: 10pt;">
  <div class="frame-band"><p class="body-large">De businesscase draait op één hard criterium: vermeden escalatie.</p></div>
  <div class="col" style="flex-direction: row; gap: 10pt;">
    <div class="frame-panel royal" style="flex: 1;"><p class="big-number">8.400</p><p class="label">JONGEREN</p><p>Beginnende betalingsachterstand.</p></div>
    <div class="frame-panel" style="flex: 1;"><p class="big-number" style="color: var(--sfnl-navy);">€ 4.700</p><p class="label">SCHULD</p><p>Gemiddeld bij 21 jaar.</p></div>
    <div class="verdict-box" style="flex: 1;"><p class="big-number" style="color: #FEFFFF;">€ 12.000</p><p class="label" style="color: #FEFFFF;">VERMEDEN KOSTEN</p><p>Per voorkomen wettelijk traject.</p></div>
  </div>
</div>
```

## Sidebar + exhibit

Gebruik de sidebar als lens, vraag of conclusie; het hoofdvlak draagt de exhibit. De slide moet ook zonder dash leesbaar en gebalanceerd blijven.

```html
<div class="frame-sidebar">
  <p class="label" style="color: #FEFFFF;">BESLISLENS</p>
  <p class="body-large">Waar lekt waarde uit de keten?</p>
</div>
<div class="col" style="gap: 10pt;">
  <div class="frame-band"><p>Drie momenten bepalen of preventie omzet in vermeden escalatie.</p></div>
  <div class="col" style="flex-direction: row; gap: 10pt; flex: 1;">
    <div class="frame-panel royal" style="flex: 1;"><p class="kicker">1. SIGNALEREN</p><p>Vroege betalingsachterstand wordt zichtbaar voordat formele schuld ontstaat.</p></div>
    <div class="frame-panel royal" style="flex: 1;"><p class="kicker">2. ACTIVEREN</p><p>Jongere accepteert hulp binnen het eerste contactvenster.</p></div>
    <div class="frame-panel orange" style="flex: 1;"><p class="kicker">3. VOORKOMEN</p><p>Wettelijk traject blijft uit; besparing is meetbaar per cohort.</p></div>
  </div>
</div>
```

## Evidence stack met gekleurde kaders

Gebruik de stack om bewijsgewicht te ordenen: brondata, mechanisme, resultaat. Kleur ondersteunt de rol; tekst en positie blijven leidend.

```html
<div class="col" style="gap: 8pt;">
  <div class="evidence-box" style="border-left-color: var(--sfnl-royal);">
    <p class="label" style="color: var(--sfnl-dark-slate);">EVIDENCE</p>
    <p style="color: var(--sfnl-dark-slate);">Gemeentedata tonen dat eerste achterstanden geconcentreerd zijn in de overgang 18-21 jaar.</p>
  </div>
  <div class="evidence-box" style="border-left-color: var(--sfnl-sky);">
    <p class="label" style="color: var(--sfnl-dark-slate);">MECHANISME</p>
    <p style="color: var(--sfnl-dark-slate);">Snelle begeleiding voorkomt stapeling van incasso, afsluitkosten en formele schuldhulp.</p>
  </div>
  <div class="evidence-box" style="border-left-color: var(--sfnl-orange);">
    <p class="label" style="color: var(--sfnl-dark-slate);">RESULTAAT</p>
    <p style="color: var(--sfnl-dark-slate);">De businesscase telt alleen vermeden escalatie mee, niet generieke contactmomenten.</p>
  </div>
</div>
<div class="frame-panel orange" style="width: 170pt;">
  <p class="big-number">72%</p>
  <p class="label">VROEG BEREIKT</p>
  <p>Bereikt voor formele aanmelding schuldhulp.</p>
</div>
```

## Verdict met ask-blok

Gebruik een verdict-box voor de uitkomst en een apart ask-kader voor het besluit dat nodig is. Vermijd een gecentreerde losse conclusiekaart.

```html
<div class="col" style="flex: 2; gap: 10pt;">
  <div class="verdict-box" style="flex: 1;">
    <p class="label" style="color: #FEFFFF;">VERDICT</p>
    <p class="body-large">Opschalen is verdedigbaar als instroomkwaliteit en escalatiemeting maandelijks worden bewaakt.</p>
  </div>
  <div class="frame-panel emerald">
    <p class="kicker">BEHEERSING</p>
    <p>Stop/go per kwartaal op bereik, conversie en vermeden wettelijke trajecten.</p>
  </div>
</div>
<div class="frame-panel orange" style="flex: 1;">
  <p class="label">ASK</p>
  <p class="body-large">Besluit vandaag over fase 2: drie gemeenten, één meetprotocol, vaste escalatie-definitie.</p>
</div>
```

## Risicomatrix met functionele kleur

Gebruik grapefruit voor risico/lekkage en emerald voor beheersing/positieve status. Bouw de matrix met flex-rijen; gebruik geen HTML table.

```html
<div class="col" style="gap: 5pt;">
  <div style="display: flex; gap: 5pt;">
    <div class="frame-band" style="flex: 2;"><p class="label" style="color: #FEFFFF;">RISICO</p></div>
    <div class="frame-band" style="flex: 1;"><p class="label" style="color: #FEFFFF;">STATUS</p></div>
    <div class="frame-band" style="flex: 2;"><p class="label" style="color: #FEFFFF;">MAATREGEL</p></div>
  </div>
  <div style="display: flex; gap: 5pt;">
    <div class="frame-panel grapefruit" style="flex: 2;"><p class="body-dense">Bereik blijft onder kritieke massa.</p></div>
    <div class="frame-panel grapefruit" style="flex: 1;"><p class="body-dense"><b>LEK</b></p></div>
    <div class="frame-panel emerald" style="flex: 2;"><p class="body-dense">Referral-afspraak met vaste terugkoppeling per wijkteam.</p></div>
  </div>
  <div style="display: flex; gap: 5pt;">
    <div class="frame-panel royal" style="flex: 2;"><p class="body-dense">Kosten per traject verschuiven door casemix.</p></div>
    <div class="frame-panel emerald" style="flex: 1;"><p class="body-dense"><b>BEHEERST</b></p></div>
    <div class="frame-panel emerald" style="flex: 2;"><p class="body-dense">Maandelijkse cohortcontrole op zwaarte en doorlooptijd.</p></div>
  </div>
</div>
```

## Chart + conclusieband

Plaats de chart als exhibit, niet als decoratie. Registreer `chart-main` in `deck.json` → `slides[].charts[]`; de conclusieband maakt de interpretatie expliciet.

```html
<div class="col" style="flex: 3; gap: 10pt;">
  <div id="chart-main" class="placeholder" style="flex: 1;"></div>
  <div class="frame-band"><p>Conclusie: uitstroom stijgt pas wanneer signalering en activatie in dezelfde maand plaatsvinden.</p></div>
</div>
<div class="col" style="flex: 1; gap: 10pt;">
  <div class="evidence-box"><p class="label" style="color: var(--sfnl-dark-slate);">BRON</p><p class="body-dense" style="color: var(--sfnl-dark-slate);">Cohortmonitor M1-M6, n=312.</p></div>
  <div class="frame-panel orange"><p class="label">BESLUIT</p><p class="body-dense">Stuur op maandelijkse activatie, niet op jaargemiddelde instroom.</p></div>
</div>
```

## Procesband met mechanismen

Voor proces en systeemlogica zijn royal/sky de dragende kleuren. Gebruik frames per mechanisme, niet een rij pale kaarten.

```html
<div class="col" style="gap: 10pt;">
  <div class="frame-band"><p>Mechanisme: eerder contact verkort de escalatieketen met drie beslismomenten.</p></div>
  <div class="col" style="flex-direction: row; gap: 10pt;">
    <div class="frame-panel royal" style="flex: 1;"><p class="kicker">1. DATA</p><p>Signaal uit achterstand, school of inkomensloket.</p></div>
    <div class="frame-panel royal" style="flex: 1;"><p class="kicker">2. CONTACT</p><p>Warme overdracht naar begeleiding binnen tien werkdagen.</p></div>
    <div class="frame-panel" style="flex: 1; border-color: var(--sfnl-sky);"><p class="kicker">3. ACTIE</p><p>Budgetafspraak voorkomt extra incassokosten.</p></div>
    <div class="frame-panel orange" style="flex: 1;"><p class="kicker">4. RESULTAAT</p><p>Wettelijk traject blijft uit.</p></div>
  </div>
</div>
```

## Scenario-kaders

Scenario's zijn besliskaders. Gebruik Gotham Bold alleen voor de korte bedragen of indexen, niet voor de volledige tekst.

```html
<div class="col" style="flex-direction: row; gap: 10pt;">
  <div class="frame-panel royal" style="flex: 1;">
    <p class="kicker">VOORZICHTIG</p>
    <p class="big-number" style="font-size: 24pt; color: var(--sfnl-navy);">€ 0,8M</p>
    <p class="body-dense">Alleen harde wettelijke trajectkosten meegeteld.</p>
  </div>
  <div class="frame-panel orange" style="flex: 1;">
    <p class="kicker">BASIS</p>
    <p class="big-number" style="font-size: 24pt;">€ 1,2M</p>
    <p class="body-dense">Wettelijke trajectkosten plus aantoonbare uitvoeringsbesparing.</p>
  </div>
  <div class="frame-panel emerald" style="flex: 1;">
    <p class="kicker">OPSCHALING</p>
    <p class="big-number" style="font-size: 24pt; color: var(--sfnl-emerald);">€ 1,7M</p>
    <p class="body-dense">Effect blijft stabiel bij drie extra gemeenten.</p>
  </div>
</div>
```

## Native hook en iconen

Complexe tabellen kunnen native via de per-deck hook (`slide.addTable`, zie authoring guide). Iconen horen alleen in een slide als ze inhoud dragen, bijvoorbeeld een bronsoort, doelgroep of beslisstatus.

```html
<div class="frame-panel royal" style="flex: 2;">
  <p class="label">NATIVE HOOK</p>
  <p>Gebruik de hook voor echte tabellen, speciale vormen of PowerPoint-native elementen die HTML niet betrouwbaar bouwt.</p>
</div>
<div class="evidence-box" style="flex: 1;">
  <p class="label" style="color: var(--sfnl-dark-slate);">ICOON</p>
  <p style="color: var(--sfnl-dark-slate);">Alleen gebruiken wanneer het icoon een betekenislabel ondersteunt; geen decoratieve iconenrijen.</p>
</div>
```
