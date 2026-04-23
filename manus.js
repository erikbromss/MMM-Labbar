const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, BorderStyle, LevelFormat
} = require('docx');
const fs = require('fs');

// ── helpers ────────────────────────────────────────────────────────────────
const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new TextRun({ text, bold: true, size: 32, font: "Arial" })]
});

const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun({ text, bold: true, size: 26, font: "Arial" })]
});

const body = (text) => new Paragraph({
  spacing: { after: 160 },
  children: [new TextRun({ text, size: 22, font: "Arial" })]
});

const italic = (text) => new Paragraph({
  spacing: { after: 120 },
  children: [new TextRun({ text, size: 20, font: "Arial", italics: true, color: "555555" })]
});

const imgPlaceholder = (label) => new Paragraph({
  spacing: { before: 120, after: 240 },
  border: {
    top:    { style: BorderStyle.SINGLE, size: 4, color: "2E75B6" },
    bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E75B6" },
    left:   { style: BorderStyle.SINGLE, size: 4, color: "2E75B6" },
    right:  { style: BorderStyle.SINGLE, size: 4, color: "2E75B6" },
  },
  children: [new TextRun({ text: `📊 ${label}`, size: 20, font: "Arial", color: "2E75B6", italics: true })]
});

const spacer = () => new Paragraph({ children: [new TextRun("")] });

// ── document ───────────────────────────────────────────────────────────────
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1F3864" },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 1 }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [

      // ── TITELBLAD ───────────────────────────────────────────────────────
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 2000, after: 400 },
        children: [new TextRun({ text: "Klimatmodelleringsprojektet", bold: true, size: 48, font: "Arial", color: "1F3864" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: "MVE347 — Presentationsmanus", size: 26, font: "Arial", color: "444444" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 2000 },
        children: [new TextRun({ text: "Del 1: Kolcykelmodell  |  Del 2: Energibalans  |  Del 3: Analys", size: 22, font: "Arial", italics: true, color: "666666" })]
      }),
      spacer(),

      // ═══════════════════════════════════════════════════════════════════
      // DEL 1
      // ═══════════════════════════════════════════════════════════════════
      h1("Del 1 — Modellering av kolcykeln"),
      spacer(),

      // ── TASK 1 ─────────────────────────────────────────────────────────
      h2("Task 1 – Biosfärens boxmodell"),

      body("Vi modellerar kolets rörelse mellan tre reservoarer med hjälp av en boxmodell och differentialekvationerna 2–4 i projektet, losta numeriskt med forward Euler (tidssteg 1 år):"),
      body("Box 1 (atmosfär, 600 GtC), Box 2 (biomassa ovan mark, 600 GtC) och Box 3 (mark och rötter, 1 500 GtC). Flödeskoefficienterna α beräknas som det pre-industriella flödet dividerat med boxens storlek och hålls konstanta."),
      body("Fotosyntes — flödet från atmosfären in i biomassan — är inte linjärt utan ökar logaritmiskt med atmosfärens kolinnehåll, ett fenomen kallat CO₂-gödsling (ekvation 1): NPP = NPP₀ · (1 + β · ln(B₁/B₁,₀)). Parametern β kallas CO₂-gödslingsparametern och har referensvärdet 0.35."),
      body("Med RCP4.5-utsläppsdata som indata beräknar vi atmosfärens CO₂-koncentration via omvandlingsfaktorn 0.469 ppm/GtC."),

      imgPlaceholder("Plot 1 (task1_2.py) – Atmosfärisk CO₂: biosfärmodell vs RCP4.5-referensdata"),

      body("Modellen överskatter koncentrationerna jämfört med RCP4.5-datan. Anledningen är att vi ännu inte inkluderat havsupptaget — havet absorberar en stor andel av de antropogena utsläppen, och när det saknas stannar mer kol i atmosfären."),
      spacer(),

      // ── TASK 2 ─────────────────────────────────────────────────────────
      h2("Task 2 – Känslighetsanalys: gödslingsparametern β"),

      body("Vi testar β = 0.1, 0.35 och 0.8 och studerar hur atmosfären (B1), biomassa (B2) och mark (B3) svarar."),

      imgPlaceholder("Plot 2 (task1_2.py) – Effekt av β på B1 (ppm), B2 (GtC) och B3 (GtC)"),

      body("Högt β innebär att växtligheten svarar kraftigare på ökad CO₂ i atmosfären. Mer kol binds in i biomassa och mark, vilket bromsar ökningen i atmosfären. Lågt β ger tvärtom — biosfären reagerar svagt och mer kol stannar i luften."),
      body("Mekanismen: NPP ökar med ln(B1/B1,₀) skalad med β. Mer NPP → snabbare påfyllning av B2 → B2 drar mer kol ur B1 → B1 hålls nere. Biosfärens återkoppling är relativt snabb och syns tydligt redan på decennieskalan."),
      spacer(),

      // ── TASK 3 ─────────────────────────────────────────────────────────
      h2("Task 3 – Impulsrespons för havsupptag"),

      body("Havet modelleras inte med en boxmodell utan med en impulsresponsfunktion — summan av exponentiellt avklingande termer med olika tidskonstanter τᵢ (ekvation 6a). Varje term representerar en fysikalisk process: ytblandning (snabb, år), termoklintransport (decennier) och djuphavsomblandning (sekler)."),
      body("Tidskonstanterna beror på tidigare kumulativa utsläpp: τᵢ(t) = τ₀,ᵢ · (1 + k · Σ U). Parametern k = 3.06·10⁻³ GtC⁻¹ styr hur snabbt havet mättas — ett högt k innebär att havet snabbt tappar förmåga att absorbera mer CO₂."),

      imgPlaceholder("Plot 3 (task3_4.py) – Impulsrespons för 0, 140, 560 och 1 680 GtC kumulativa utsläpp"),

      body("Med ökande kumulativa utsläpp sjunker impulsresponsen snabbare — havet mättas och en större andel av en ny utsläppspuls stannar kvar i atmosfären. Detta är en viktig positiv återkoppling i systemet."),
      spacer(),

      // ── TASK 4 ─────────────────────────────────────────────────────────
      h2("Task 4 – Havsmodell: atmosfärisk CO₂"),

      body("Genom att falta (konvolvera) impulsresponsen med utsläppen beräknar vi atmosfärens kolinnehåll M(t) enligt ekvation 8. Modellen tar alltså hänsyn till hur mycket av varje historisk utsläppspuls som fortfarande befinner sig i atmosfären."),

      imgPlaceholder("Plot 4 (task3_4.py) – Havsmodell vs RCP4.5-referensdata"),

      body("Havsmodellen ensam ger en bättre anpassning till referensdata än biosfärmodellen ensam (Task 1), men koncentrationerna är fortfarande lite höga — biosfärens uptag saknas fortfarande."),
      spacer(),

      // ── TASK 5 ─────────────────────────────────────────────────────────
      h2("Task 5 – Integrerad boxmodell (konceptuell)"),
      body("Vi ritar en utökad boxmodell (se hand- eller digitalteckning) där de tre biosfärboxarna kombineras med ett havsblock som representeras av impulsresponsen. Antropogena utsläpp U(t) tillförs atmosfärboxen (B1). Havsupptaget är inte ett flöde till en separat box utan modelleras som ett nettoupptag som reducerar de 'effektiva utsläpp' U_eff som når atmosfär–hav-systemet."),
      spacer(),

      // ── TASK 6 ─────────────────────────────────────────────────────────
      h2("Task 6 – Kombinerad biosfär + havsmodell"),

      body("Nu kopplas biosfärmodellen och havsmodellen ihop. Biosfärens nettoupptag beräknas varje tidssteg som: Netto_bio = NPP − (α₂₁·B2 + α₃₁·B3). De effektiva utsläpp som når havet är: U_eff = U_antro − Netto_bio. Havsmodellen (ekvation 8) körs sedan på U_eff istället för U."),

      imgPlaceholder("Plot 5 (task6.py) – Kombinerad modell vs RCP4.5-referensdata"),

      body("Med β = 0.35 och k = 3.06·10⁻³ stämmer den kombinerade modellen väl med RCP4.5-referensdatan. Det visar att vår enkla modell fångar de dominerande processerna i kolcykeln på ett rimligt sätt."),
      spacer(),

      // ── TASK 7 ─────────────────────────────────────────────────────────
      h2("Task 7 – Kolreservoarernas utveckling fram till 2100"),

      body("Vi analyserar hur de fyra reservoarerna — atmosfär, biomassa, mark och hav — förändras till 2100, och hur de beror på β och k."),

      imgPlaceholder("Plot 6 (task7.py) – Basfall: absoluta kolmängder i alla fyra reservoarer"),
      imgPlaceholder("Plot 7 (task7.py) – Känslighetsanalys β: ΔGtC relativt pre-industriellt för alla reservoarer"),
      imgPlaceholder("Plot 8 (task7.py) – Känslighetsanalys k: ΔGtC relativt pre-industriellt för alla reservoarer"),

      body("β styr hur mycket kol biosfären binder. Högt β → biomassa och mark växer snabbare → atmosfären hålls nere → havet behöver absorbera mindre. Biosfärens återkoppling är snabb och divergensen mellan β-scenarierna syns tidigt."),
      body("k styr havets mättnadshastighet. Högt k → havet mättas tidigare → mer kol stannar i atmosfären. Effekten är kumulativ och långsam — kurvorna för olika k divergerar sent men konsekvenserna är svåra att reversera."),
      body("Basfallet (β = 0.35, k = 3.06·10⁻³) ligger nära referensdata och utgör vår bästa approximation av verkligheten."),
      spacer(),

      // ═══════════════════════════════════════════════════════════════════
      // DEL 2
      // ═══════════════════════════════════════════════════════════════════
      h1("Del 2 — Energibalansmodellering"),
      spacer(),

      // ── TASK 8 ─────────────────────────────────────────────────────────
      h2("Task 8 – Radiativ forcing från CO₂"),

      body("CO₂:s bidrag till radiativ forcing (RF) beräknas med den empiriska relationen: RF_CO₂ = 5.35 · ln(pCO₂ / pCO₂,₀). Beroendet är logaritmiskt eftersom absorptionsbanden i infraröd strålning gradvis mättas — varje ny CO₂-molekyl i en redan mättad vågläng bidrar allt mindre."),
      body("Vi beräknar RF från modellens koncentrationer och jämför med RCP4.5-referensdatan för RF."),

      imgPlaceholder("Plot 9 (task8.py) – Modellerad RF (CO₂) vs RCP4.5-referens"),

      body("God överensstämmelse med referensdatan bekräftar att vår kolcykelmodell producerar rimliga CO₂-koncentrationer."),
      spacer(),

      // ── TASK 9 ─────────────────────────────────────────────────────────
      h2("Task 9 – Total radiativ forcing"),

      body("Utöver CO₂ bidrar aerosoler (kylande, negativ RF) och övriga växthusgaser (CH₄, N₂O, halogener etc., värmande) till den totala forcingen. Dessa hämtas direkt från radiativeForcingRCP45.csv."),
      body("Aerosolernas bidrag skalas med faktorn s (standardvärde 1.0). Parametern s representerar den stora osäkerhet som finns kring aerosolernas kylande effekt. Hög s (t.ex. s = 2) innebär kraftigare kylning och lägre netto-RF; låg s (t.ex. s = 0.5) innebär svagare kylning."),
      body("Totala RF = RF_CO₂ + s · RF_aerosol + RF_övriga."),
      spacer(),

      // ── TASK 10 ────────────────────────────────────────────────────────
      h2("Task 10 – Tvåboxars energibalansmodell"),

      body("Temperaturresponsen beräknas med en tvåboxsmodell (ekvationerna 10–11). Den övre boxen representerar atmosfär, landyta och det ytliga havet med värmekapacitet C₁. Den nedre boxen är djuphavet med värmekapacitet C₂. Boxarna utbyter energi med koefficienten κ."),
      body("Tre centrala parametrar:"),
      body("λ (klimatkänslighetsparameter, K·W⁻¹·m²): Styr jämviktstemperaturen ΔT₁ = RF · λ. Högt λ → planeten värms upp mer per enhet forcing. Referensvärde 0.8, span 0.5–1.3."),
      body("κ (värmeväxlingskoefficient, W·K⁻¹·m⁻²): Styr hur snabbt värme pumpas från den övre boxen till djuphavet. Högt κ → djuphavet absorberar snabbt → yttemperaturen stiger långsammare initialt (längre transienstid). Referensvärde 0.5, span 0.2–1.0."),
      body("C₁ och C₂: Effektiva värmekapaciteter för respektive box. C₂ är enormt (djuphav ~270 W·yr·K⁻¹·m⁻²) vilket förklarar varför systemet tar hundratals till tusentals år att nå jämvikt."),

      imgPlaceholder("Plot 10 (task10.py) – 10a: Stegrespons 1 W/m² — ΔT1 och ΔT2 mot jämvikt 0.8°C"),
      imgPlaceholder("Plot 11 (task10.py) – 10b: E-foldingtider τ₁ och τ₂ som funktion av κ för olika λ"),
      imgPlaceholder("Plot 12 (task10.py) – 10b: E-foldingtider för djuphavstemperatur τ₂"),
      imgPlaceholder("Plot 13 (task10.py) – 10c: Energiflöden (RF, rymdstrålning, havsupptag) över 200 år"),
      imgPlaceholder("Plot 14 (task10.py) – 10c: Energikonservation (kumulativt nettoinflöde vs lagrad energi)"),

      body("10a: Jämviktstemperaturen är ΔT₁ = ΔT₂ = RF · λ = 0.8°C, i enlighet med teorin. Det tar dock tusentals år att nå full jämvikt, eftersom djuphavet med sin enorma värmekapacitet absorberar energi mycket länge."),
      body("10b: Högt κ ökar τ₁ (ytan värms långsammare) men minskar τ₂ (djuphav värms snabbare). Högt λ ökar jämviktstemperaturen och därmed också e-foldingtiderna något. Effekten av κ dominerar över λ för transiensens hastighet."),
      body("10c: I stegresponsexperimentet stiger rymdstrålningen (ΔT₁/λ) gradvis från noll mot 1 W/m². Havsupptaget (κ·(ΔT₁−ΔT₂)) toppar tidigt och avtar sedan när T₂ hinner ikapp T₁. Energikonservation gäller: kumulativt nettoinflöde = lagrad energi i systemet."),
      spacer(),

      // ═══════════════════════════════════════════════════════════════════
      // DEL 3
      // ═══════════════════════════════════════════════════════════════════
      h1("Del 3 — Analys med den fullständiga klimatmodellen"),
      spacer(),

      // ── TASK 11 ────────────────────────────────────────────────────────
      h2("Task 11 – Historisk temperaturvalidering (1765–2024)"),

      body("Den fullständiga modellen (kolcykel → RF → energibalans) körs med historiska utsläpp. Resultatet jämförs med NASA GISS-temperaturanomalier (1880–2019)."),

      imgPlaceholder("Plot 15 (task11.py) – 11a/b: Modelltemperatur 1765–2024, och jämförelse med NASA GISS 1880–2019"),
      imgPlaceholder("Plot 16 (task11.py) – 11b: Alla kombinationer av λ, κ och s mot NASA-datan"),

      body("11a — Referensperioden: Val av referensperiod förskjuter hela temperaturkurvan vertikalt utan att ändra trend eller form. En varm referensperiod (t.ex. 1981–2010) gör historisk uppvärmning 'osynlig'. För att beskriva förändringen sedan pre-industriell tid bör referensperioden vara 1765–1800 (eller liknande tidigt 1800-tal)."),
      body("11b — Parametrarnas roll: λ bestämmer amplituden på uppvärmningen. Högt λ ger för hög temperatur relativt NASA-datan, vilket kan kompenseras med högt s (starkare aerosolkylning) eller högt κ (mer värme till djuphavet). Parametrarna är sammanflätade — flera kombinationer av (λ, κ, s) ger liknande anpassning till NASA-datan."),
      body("11c — Statistisk skattning: Det är principiellt möjligt men svårt i praktiken, eftersom parametrarna kompenserar varandra. Att separera λ, κ och s ur enbart 140 år av temperaturdata (med naturlig variabilitet som brus) är problematiskt. En bayesiansk ansats med flera observationstyper simultant — yttemperatur, havsvärmeinnehåll och strålningsdata — kan ge smalare osäkerhetsintervall men inte eliminera osäkerheten."),
      spacer(),

      // ── TASK 12 ────────────────────────────────────────────────────────
      h2("Task 12 – Framtida utsläppsscenarier och temperaturprojektioner"),

      body("Vi definierar tre utsläppsscenarier från dagens nivå (~10.6 GtC/år) för perioden 2025–2200:"),
      body("Scenario i (lågt): Linjär minskning till noll 2070, fortsätter negativt till 2100, konstant därefter."),
      body("Scenario ii (medel): Konstant på dagens nivå hela perioden."),
      body("Scenario iii (högt): Linjär ökning till 200 % av dagens nivå 2100, konstant därefter."),

      imgPlaceholder("Plot 17 (task12_13.py) – 12a: Utsläppsscenarier och temperaturprojektioner 1765–2200 (λ=0.8, ref 1951–1980)"),
      imgPlaceholder("Plot 18 (task12_13.py) – 12b: Temperaturökning relativt pre-industriellt — alla tre scenarier med 2100-markering"),
      imgPlaceholder("Plot 19 (task12_13.py) – 12c: Temperaturspridning år 2100 givet osäkerhet i λ (osäkerhetsband per scenario)"),

      body("12a/b: Temperaturökning år 2100 relativt pre-industriellt: Scenario i ≈ 1.4°C, Scenario ii ≈ 2.5°C, Scenario iii ≈ 4°C (för λ = 0.8). Enbart scenario i klarar Parisavtalets 1.5°C-mål."),
      body("12c: Osäkerhetsband: λ-osäkerheten (0.5–1.3) skapar ett brett band i temperaturprojektionerna. För scenario ii och iii finns överlapp med 2°C-målet enbart för de lägsta λ-värdena. Scenariovalet har dock generellt större påverkan på temperaturen än λ-osäkerheten — klimatpolitiken vi väljer dominerar över vår okunnighet om klimatkänsligheten."),
      body("12d — Implikationer för klimatpolitik: Osäkerheten i λ, κ och s bör enligt försiktighetsprincipen (Lundqvist) leda till mer ambitiös utsläppspolitik, inte mindre. Om λ visar sig vara i det övre spannet och vi inte minskat utsläppen tillräckligt, saknar vi handlingsutrymme. Konjunkturrådet argumenterar för att fokus bör ligga på global klimatnytta — teknikutveckling som sänker kostnaden för omställning i alla länder, inte bara i Sverige."),

      imgPlaceholder("Plot 20 (task12_13.py) – 12e: Scenario i med negativa utsläpp och temperaturpeak-and-decline"),

      body("12e — Negativa utsläpp och peak-and-decline: I scenario i når utsläppen noll 2070 och blir sedan negativa. Det leder till att CO₂-koncentrationen börjar sjunka, RF minskar och temperaturen når en topp och börjar sedan falla — ett 'peak-and-decline'-förlopp. Denna typ av bana är central för 1.5°C-målet: om vi tillfälligt överskrider målet kan negativa utsläpp ta oss tillbaka under det."),
      body("Negativa utsläpp kan realiseras genom: (1) naturbaserade metoder — återbeskogning, restaurering av myrar och mangrove; (2) tekniska metoder — BECCS (bioenergi med koldioxidinfångning) eller direktinfångning ur luft (DAC). Alla är antingen marknadsbegränsade eller energi- och kostnadskrävande i stor skala."),
      spacer(),

      // ── TASK 13 ────────────────────────────────────────────────────────
      h2("Task 13 – Geoengineerering: stratosfärisk aerosolinjektion"),

      body("Vi analyserar vad som händer om geoengineering implementeras under scenario iii (höga utsläpp), med en minskning av inkommande solstrålning med 4 W/m² under 2050–2100, och sedan abrupt avbryts."),

      imgPlaceholder("Plot 21 (task12_13.py) – 13a: Termination shock — Scenario iii med och utan geoengineering (1765–2200)"),

      body("13a — Termination shock: Under geoengineeringens aktiva period (2050–2100) hålls temperaturen nere. Men CO₂ fortsätter att ackumuleras. När geoengineeringen abrupt avbryts 2100 stiger temperaturen brant — uppvärmningstakten efter avbrottet är ca 10 gånger högre än den naturliga takten under perioden 2000–2012. Ekosystem och samhällen ges extremt lite tid att anpassa sig."),
      body("13b — Hållbarhetsperspektiv: Geoengineering adresserar symptomet (temperaturen) men inte orsaken (CO₂-ackumulationen). Det skapar ett kritiskt beroende: ett enda politiskt beslut, ekonomisk kris eller konflikt kan utlösa termination shock."),
      body("Tre hållbarhetsdimensioner: (1) Intergenerationell rättvisa — vi skjuter ett ännu svårare problem till framtida generationer. (2) Global rättvisa — förändringar i monsunmönster och nederbördsfördelning drabbar regioner som inte beslutat om eller gynnas av interventionen. (3) Systemisk robusthet — det är svårt att tänka sig en mindre robust lösning än en som kollapsar om den avbryts."),
      body("Jämfört med utsläppsminskningar och negativa utsläpp — som angriper problemet vid källan och är förenliga med Parisavtalet — är geoengineering som substitut fundamentalt oförenligt med hållbar utvecklings principer. Möjligen kan det diskuteras som ett nödåtgärdsverktyg i extrema scenarier, men aldrig som ersättning för strukturell omställning av energisystemet."),
      spacer(),

      // ── AVSLUTNING ─────────────────────────────────────────────────────
      h1("Sammanfattning"),
      body("Del 1 visar att en kombination av biosfärens boxmodell (β = 0.35) och havets impulsrespons (k = 3.06·10⁻³) reproducerar historiska CO₂-koncentrationer väl. Parametrarna β och k kontrollerar hur snabbt biosfären respektive havet mättas och har tydliga konsekvenser för kolreservoarernas långsiktiga utveckling."),
      body("Del 2 kvantifierar temperaturresponsen via radiativ forcing och tvåboxsenergibalansen. Klimatkänsligheten λ bestämmer jämviktstemperaturen; κ styr transiensens hastighet; s skalerar aerosolernas kylande effekt. Parametrarna är sammanflätade men kan begränsas med flertypsobservationer."),
      body("Del 3 visar att valet av utsläppsscenario dominerar över λ-osäkerheten för temperaturprojektioner 2100. Enbart kraftiga utsläppsminskningar kombinerade med negativa utsläpp håller oss nära 1.5°C. Geoengineering köper tid men skapar ett farligt beroende och är inte förenligt med hållbar utveckling på lång sikt."),
      spacer(),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/mnt/user-data/outputs/presentationsmanus.docx", buf);
  console.log("Done");
});
