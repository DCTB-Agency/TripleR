/* Triple R — gedeelde scripts: header, megamenu, drawer, "Vraag het Triple R" (incl. PDF-index), beweging, review */
(() => {
  const root = document.documentElement, params = new URLSearchParams(location.search);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce) root.classList.add('motion');

  /* ---------- review-balk ---------- */
  const tTb = document.getElementById('t-tb'), tAn = document.getElementById('t-annot');
  const setTb = on => { root.classList.toggle('no-tb', !on); tTb.setAttribute('aria-pressed', on); };
  const setAn = on => { root.classList.toggle('annot', on); tAn.setAttribute('aria-pressed', on); };
  tTb.addEventListener('click', () => setTb(tTb.getAttribute('aria-pressed') !== 'true'));
  tAn.addEventListener('click', () => setAn(tAn.getAttribute('aria-pressed') !== 'true'));
  if (params.has('annot')) setAn(true);
  if (params.has('clean')) setTb(false);

  /* ---------- megamenu + drawer ---------- */
  const mmBtn = document.getElementById('mm-btn'), mm = document.getElementById('mm');
  const closeMm = () => { mm.hidden = true; mmBtn.setAttribute('aria-expanded', 'false'); };
  mmBtn.addEventListener('click', () => { const o = mm.hidden; mm.hidden = !o; mmBtn.setAttribute('aria-expanded', o); });
  document.addEventListener('click', e => { if (!mm.hidden && !mm.contains(e.target) && !mmBtn.contains(e.target)) closeMm(); });
  mm.addEventListener('click', e => { if (e.target.closest('a')) closeMm(); });
  const drawer = document.getElementById('drawer'), mOpen = document.getElementById('m-open');
  const openDrawer = (v, f) => { drawer.hidden = !v; mOpen.setAttribute('aria-expanded', v); document.body.style.overflow = v ? 'hidden' : ''; (v ? document.getElementById(f || 'm-close') : mOpen).focus(); };
  mOpen.addEventListener('click', () => openDrawer(true));
  document.getElementById('m-close').addEventListener('click', () => openDrawer(false));
  drawer.addEventListener('click', e => { if (e.target.closest('.list a, .btn')) openDrawer(false); });

  /* =====================================================================
     VRAAG HET TRIPLE R — conversational search (designprototype, BRIEF §17)
     • Webpagina's: vaste index (in productie: Pagefind op de gebouwde site).
     • PDF's: de échte datasheets uit /pdf/ worden per pagina uitgelezen met pdf.js
       (in productie gebeurt dit bij elke build → Pagefind + vectorindex).
     • Antwoorden: 3 voorbeeldantwoorden (feiten uit de brief) met bronnen die naar
       de gevonden PDF-pagina linken; anders letterlijke passages uit de PDF's;
       anders "geen betrouwbaar antwoord". In productie schrijft Claude het antwoord.
     ===================================================================== */
  const ask = document.getElementById('ask'), askQ = document.getElementById('ask-q'), askBody = document.getElementById('ask-body'), askGo = document.getElementById('ask-go'), askStatus = document.getElementById('ask-status');
  let lastFocus = null, sel = -1, streamTimer = 0;
  const I = {
    spark: '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 1l1.6 4.1L13.7 6.7 9.6 8.3 8 12.4 6.4 8.3 2.3 6.7l4.1-1.6z"/><path d="M13 10.5l.6 1.5 1.5.6-1.5.6-.6 1.5-.6-1.5-1.5-.6 1.5-.6z" opacity=".75"/></svg>',
    q: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 3.5h10v7H7l-3 2.5v-2.5H3z"/></svg>',
    back: '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M13 8H3M7 4L3 8l4 4"/></svg>',
    up: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 7v7H2.5V7zM5 7l3-5c1.2 0 1.8.8 1.6 2L9 6.5h3.6c.9 0 1.5.8 1.3 1.7l-1 4.6c-.2.7-.8 1.2-1.5 1.2H5"/></svg>',
    down: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true" style="transform:rotate(180deg)"><path d="M5 7v7H2.5V7zM5 7l3-5c1.2 0 1.8.8 1.6 2L9 6.5h3.6c.9 0 1.5.8 1.3 1.7l-1 4.6c-.2.7-.8 1.2-1.5 1.2H5"/></svg>'
  };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

  /* ---------- bronnen ---------- */
  const PDFS = [
    { f: 'BU-2023-UK-.pdf', t: 'BU-serie datasheet', p: 'bu' },
    { f: 'SE-2019-ENGLISH.pdf', t: 'SE-serie datasheet', p: 'se' },
    { f: 'SE-Mobile-2023-ENGLISH.pdf', t: 'SE-Mobile datasheet', p: 'se' },
    { f: 'se100e-bh.pdf', t: 'SE100E-BH datasheet', p: 'se' },
    { f: 'se100e-wh.pdf', t: 'SE100E-WH datasheet', p: 'se' },
    { f: 'TR-2019-ENGLISH.pdf', t: 'TR-serie datasheet', p: 'tr' },
    { f: 'OSCA-2019-ENGLISH.pdf', t: 'OSCA-serie datasheet', p: 'osca' },
    { f: 'SS-2019-ENGLISH-.pdf', t: 'SS-serie datasheet', p: 'ss' },
    { f: 'WS-2019-ENGLISH.pdf', t: 'WS-serie datasheet', p: 'ws' },
    { f: 'QUICKTORON-2023-ENGLISH.pdf', t: 'Quicktoron datasheet', p: 'quicktoron' },
    { f: 'VacuumDehydrator-TRVS-N30E-ENG.pdf', t: 'Vacuümontwateraar TRVS-N30E', p: 'vacuum' },
    { f: 'vacuum_system_test.pdf', t: 'Vacuümontwateraar testrapport', p: 'vacuum' },
    { f: 'Centrifuges_2014_UK-1.pdf', t: 'Centrifuges brochure', p: 'centrifuges' },
    { f: 'windmill.pdf', t: 'Toepassing windturbines' },
    { f: 'Recommended-cleanliness4.pdf', t: 'Recommended cleanliness' },
    { f: 'iso440637534.pdf', t: 'ISO 4406-tabel' },
    { f: 'nas1638-kopie.pdf', t: 'NAS 1638-tabel' }
  ];
  const PAGES = [
    { g: 'Producten', t: 'BU-serie', s: 'Bypassfilter direct op de hogedrukleiding tot 450 bar, zonder pomp of motor.', k: 'bu serie bypass 450 bar druk spuitgiet servo pressure', u: 'producten.html#p-bu' },
    { g: 'Producten', t: 'SE-serie', s: 'Offline oliereiniger met motor-pompgroep, ook mobiel met deeltjesteller.', k: 'se serie offline mobiel pomp pump', u: 'producten.html#p-se' },
    { g: 'Producten', t: 'OSCA-serie', s: 'Oliereiniger van 6 tot > 60 l/min voor volumes boven 50.000 l.', k: 'osca oscareeks debiet grote tank flushing flow', u: 'producten.html#p-osca' },
    { g: 'Producten', t: 'TR-serie', s: 'Bypassfilter voor motorolie en systemen onder 6 bar.', k: 'tr serie motorolie tandwiel 6 bar engine', u: 'producten.html#p-tr' },
    { g: 'Producten', t: 'SS-serie', s: 'Stalen filterhuizen voor 2 tot 6 elementen, tot 60 l/min en 15 bar.', k: 'ss serie staal huis housing', u: 'producten.html#p-ss' },
    { g: 'Producten', t: 'Filterelementen', s: '3-in-1 dieptefilter, 1 tot 10 µm absoluut; WE100 absorbeert tot 900 ml water.', k: 'filterelement element v100 m100 we100 water varnish cartridge', u: 'producten.html#p-elementen' },
    { g: 'Producten', t: 'Vacuümontwateraar', s: 'Verwijdert 80% opgelost en 100% vrij water, 10–600 cSt, optioneel ATEX.', k: 'vacuum vacuumontwateraar water ontwateren atex dehydrator', u: 'producten.html#p-vacuum' },
    { g: 'Producten', t: 'WS-serie', s: 'Coalescer olie-waterafscheider voor continue waterinloop.', k: 'ws coalescer water afscheider separator', u: 'producten.html#p-ws' },
    { g: 'Producten', t: 'Quicktoron', s: 'Cycloon-ontluchter die tot 95% van de luchtbellen verwijdert.', k: 'quicktoron quiktoron lucht schuim cavitatie air', u: 'producten.html#p-quicktoron' },
    { g: 'Producten', t: 'Centrifuges', s: 'Deeltjes tot 3 µm uit koelvloeistof en proceswater, 15–200 l/min.', k: 'centrifuge koelvloeistof emulsie proceswater coolant', u: 'producten.html#p-centrifuges' },
    { g: 'Oplossingen', t: 'Varnish verwijderen', s: 'Oxidatieresten die kleppen doen haperen, verwijderd met een 114 mm dieptefilter.', k: 'varnish sludge oxidatie klep', u: 'homepage.html#contaminanten' },
    { g: 'Oplossingen', t: 'Water in olie verwijderen', s: 'Oorzaken, gevolgen en ontwateren tot onder 100 ppm.', k: 'water ppm vocht ontwateren tandwiel', u: 'homepage.html#contaminanten' },
    { g: 'Oplossingen', t: 'Vuile olie filtreren (ISO 4406)', s: 'Breng uw olie naar de juiste reinheidsklasse.', k: 'deeltjes iso 4406 nas 1638 reinheid vuil', u: 'homepage.html#contaminanten' },
    { g: 'Oplossingen', t: 'Besparingscalculator', s: 'Bereken wat schone olie u oplevert aan olie, stilstand en CO₂.', k: 'besparing calculator kosten roi co2 rendement', u: 'besparingscalculator.html' },
    { g: 'Kennisbank', t: 'ISO 4406-reinheidscode uitgelegd', s: 'Wat de drie getallen betekenen, met tabel en voorbeelden.', k: 'iso 4406 21/18/16 code reinheid tabel', u: 'homepage.html#kennis' },
    { g: 'Kennisbank', t: 'Bypass- of full-flowfiltratie: het verschil', s: 'Vergelijking met rekenvoorbeeld.', k: 'bypass full flow verschil nevenstroom', u: 'homepage.html#kennis' },
    { g: 'Sectoren', t: 'Hydraulische systemen', s: 'Spuitgietmachines, persen en testbanken.', k: 'hydrauliek hydraulisch spuitgiet spuitgietmachine pers', u: 'homepage.html#sectoren' },
    { g: 'Sectoren', t: 'Scheepvaart', s: 'Motoren, thrusters, kranen en lieren; ook ATEX.', k: 'scheepvaart schip marine thruster kraan', u: 'homepage.html#sectoren' },
    { g: 'Sectoren', t: 'Windenergie', s: 'Tandwielkastolie schoon en droog houden.', k: 'wind windturbine tandwiel gearbox', u: 'homepage.html#sectoren' }
  ];
  /* NL → EN-uitbreiding: de datasheets zijn Engelstalig */
  const SYN = {
    water: 'water moisture', vocht: 'moisture water humidity', deeltjes: 'particles particle contamination', deeltje: 'particle', vuil: 'dirt contamination', varnish: 'varnish sludge oxidation', sludge: 'sludge varnish',
    druk: 'pressure bar', werkdruk: 'pressure working', debiet: 'flow capacity', viscositeit: 'viscosity cst', temperatuur: 'temperature', olie: 'oil', filter: 'filter element', filterelement: 'element cartridge', element: 'element cartridge', elementen: 'elements cartridges',
    hydrauliek: 'hydraulic', hydraulisch: 'hydraulic', hydraulische: 'hydraulic', tandwiel: 'gear gearbox', tandwielolie: 'gear oil gearbox', tandwielkast: 'gearbox gear', motorolie: 'engine oil', motor: 'engine motor',
    windturbine: 'wind turbine windmill', windmolen: 'windmill wind turbine', wind: 'wind windmill', schip: 'marine ship vessel', scheepvaart: 'marine ship vessel', lucht: 'air', luchtbellen: 'air bubbles', schuim: 'foam foaming',
    ontwateraar: 'dehydrator dewatering', ontwateren: 'dewatering dehydration water removal', vacuum: 'vacuum', afmetingen: 'dimensions dimension', gewicht: 'weight kg', aansluiting: 'connection inlet outlet', pomp: 'pump',
    reinheid: 'cleanliness', reinheidsklasse: 'cleanliness class', servoklep: 'servo valve', servo: 'servo', klep: 'valve', kleppen: 'valves', vermogen: 'power kw', spanning: 'voltage', capaciteit: 'capacity',
    koelvloeistof: 'coolant', emulsie: 'emulsion', installatie: 'installation', onderhoud: 'maintenance', vervangen: 'replace change replacement', deeltjesteller: 'particle counter', spuitgiet: 'injection moulding', spuitgietmachine: 'injection moulding machine', pers: 'press', staal: 'sample', analyse: 'analysis', test: 'test', testrapport: 'test report result'
  };
  const STOP = new Set('de het een en of in op voor van met tot uit bij hoe wat welke welk is zijn wordt worden ik mijn u uw kan kun je we wij er dat die dit om te aan als ook niet geen heb heeft hebben nodig moet the a an and or of in on for to with is are be by at from what how which'.split(' '));
  const tok = s => norm(s).replace(/[^a-z0-9µ./-]+/g, ' ').split(' ').filter(w => w.length > 1 && !STOP.has(w));
  const expand = q => { const out = new Set(); tok(q).forEach(w => { out.add(w); if (SYN[w]) SYN[w].split(' ').forEach(x => out.add(x)); Object.keys(SYN).forEach(k => { if (w.length > 4 && w !== k && w.startsWith(k)) SYN[k].split(' ').forEach(x => out.add(x)); }); }); return [...out]; };

  /* ---------- PDF-index (pdf.js, lazy) ---------- */
  const CACHE = 'rrr-pdf-index-v1';
  let pdfChunks = null, pdfLoading = null, df = new Map();
  try { const c = JSON.parse(localStorage.getItem(CACHE) || 'null'); if (c && c.length) { pdfChunks = c; buildDf(); } } catch (e) {}
  function buildDf() { df = new Map(); pdfChunks.forEach(ch => { ch.tf = ch.tf || termFreq(ch.text); Object.keys(ch.tf).forEach(t => df.set(t, (df.get(t) || 0) + 1)); }); }
  function termFreq(text) { const m = {}; tok(text).forEach(w => { m[w] = (m[w] || 0) + 1; }); return m; }
  function setStatus(txt, busy) { if (!askStatus) return; askStatus.classList.toggle('busy', !!busy); askStatus.querySelector('span').textContent = txt; }
  function statusReady() { const docs = new Set(pdfChunks.map(c => c.f)).size; setStatus(`Doorzoekt ${PAGES.length} webpagina’s en ${docs} PDF’s (${pdfChunks.length} pagina’s)`); }
  function loadScript(src) { return new Promise((res, rej) => { const s = document.createElement('script'); s.src = src; s.onload = res; s.onerror = rej; document.head.appendChild(s); }); }
  function ensurePdfIndex() {
    if (pdfChunks) { statusReady(); return Promise.resolve(); }
    if (pdfLoading) return pdfLoading;
    const V = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/';
    pdfLoading = (async () => {
      try {
        setStatus('PDF’s worden geïndexeerd…', true);
        await loadScript(V + 'pdf.min.js');
        const lib = window['pdfjs-dist/build/pdf'];
        try { const w = await fetch(V + 'pdf.worker.min.js').then(r => r.text()); lib.GlobalWorkerOptions.workerSrc = URL.createObjectURL(new Blob([w], { type: 'text/javascript' })); } catch (e) { lib.GlobalWorkerOptions.workerSrc = V + 'pdf.worker.min.js'; }
        const out = []; let done = 0;
        await Promise.all(PDFS.map(async d => {
          try {
            const doc = await lib.getDocument({ url: 'pdf/' + d.f }).promise;
            for (let p = 1; p <= doc.numPages; p++) {
              const tc = await (await doc.getPage(p)).getTextContent();
              const text = tc.items.map(i => i.str + (i.hasEOL ? '\n' : ' ')).join('').replace(/[ \t]+/g, ' ').replace(/\s*\n\s*/g, '\n').trim();
              if (text.length > 20) out.push({ f: d.f, t: d.t, p: d.p || null, page: p, pages: doc.numPages, text });
            }
          } catch (e) { /* PDF niet leesbaar: overslaan */ }
          setStatus(`PDF’s worden geïndexeerd… ${++done}/${PDFS.length}`, true);
        }));
        pdfChunks = out; buildDf();
        try { localStorage.setItem(CACHE, JSON.stringify(out.map(({ tf, ...r }) => r))); } catch (e) {}
        statusReady();
        if (!ask.hidden && askQ.value.trim() && !askBody.querySelector('#ans')) render();
      } catch (e) { setStatus('PDF-index niet beschikbaar (offline?) — webpagina’s blijven doorzoekbaar'); }
    })();
    return pdfLoading;
  }
  const PKEYS = [['osca', /osca/], ['bu', /\bbu\b|bu-serie/], ['se', /\bse\b|se-serie|se-mobile|se100/], ['tr', /\btr\b|tr-serie/], ['ss', /\bss\b|ss-serie/], ['ws', /\bws\b|ws-serie|coalescer/], ['quicktoron', /quick?t?oron/], ['vacuum', /vacu|ontwateraar|dehydrator/], ['centrifuges', /centrifug/]];
  const detectProduct = q => { const n = norm(q); const hit = PKEYS.find(([, re]) => re.test(n)); return hit ? hit[0] : null; };
  function scorePdf(terms, pk) {
    if (!pdfChunks) return [];
    const N = pdfChunks.length;
    return pdfChunks.map(ch => {
      let sc = 0, hit = 0; terms.forEach(t => { const f = ch.tf[t]; if (f) { hit++; sc += (1 + Math.log(f)) * Math.log(1 + N / (df.get(t) || 1)); } });
      if (norm(ch.t).split(/\s+/).some(w => terms.includes(w))) sc += 2;
      if (pk && ch.p === pk) sc += 6;
      return { ch, sc: hit ? sc * (0.6 + hit / terms.length) : 0, hit };
    }).filter(x => x.sc > 0).sort((a, b) => b.sc - a.sc);
  }
  function snippet(text, terms, len = 170) {
    const low = norm(text); let at = -1;
    for (const t of terms) { const i = low.indexOf(t); if (i >= 0 && (at < 0 || i < at)) at = i; }
    if (at < 0) at = 0;
    let s = Math.max(0, at - 60), e = Math.min(text.length, s + len);
    let out = text.slice(s, e).replace(/\n/g, ' · ');
    return (s > 0 ? '… ' : '') + out.trim() + (e < text.length ? ' …' : '');
  }
  function bestSentence(text, terms) {
    const parts = text.replace(/\n/g, ' ').split(/(?<=[.!?])\s+(?=[A-Z0-9])/).flatMap(p => p.length > 260 ? p.match(/.{1,220}(\s|$)/g) : [p]).map(p => p.trim()).filter(p => p.length > 25);
    let best = parts[0] || text.slice(0, 200), bs = -1;
    parts.forEach(p => { const l = norm(p); const s = terms.reduce((a, t) => a + (l.includes(t) ? 1 : 0), 0); if (s > bs) { bs = s; best = p; } });
    return best.length > 240 ? best.slice(0, 237) + '…' : best;
  }
  const pdfHref = (f, page) => `pdf/${encodeURIComponent(f)}#page=${page}`;
  function resolvePdf(f, q) { const terms = expand(q); const hits = scorePdf(terms).filter(x => x.ch.f === f); const c = hits[0]?.ch || (pdfChunks || []).find(x => x.f === f); return { f, page: c ? c.page : 1, t: (PDFS.find(d => d.f === f) || {}).t || f, text: c ? c.text : '' }; }

  /* ---------- producten & voorbeeldantwoorden ---------- */
  const PROD = {
    bu: { n: 'BU-serie', img: 'img/BU-Series.png', c: ['tot 450 bar', '2 µm absoluut (M)', 'geen pomp of motor'], pdf: 'BU-2023-UK-.pdf', u: 'producten.html#p-bu' },
    vac: { n: 'Vacuümontwateraar', img: 'img/vacuum.png', c: ['80% opgelost water', '100% vrij water', 'optioneel ATEX'], pdf: 'VacuumDehydrator-TRVS-N30E-ENG.pdf', u: 'producten.html#p-vacuum' },
    el: { n: 'Filterelementen', img: 'img/elements.png', c: ['1–10 µm absoluut', 'WE100: < 80 ppm', '3–320 cSt'], pdf: null, u: 'producten.html#p-elementen' }
  };
  const ANSWERS = [
    { m: /spuitgiet|injectie|400 ?l/, prod: 'bu', lead: 'Advies over de BU-serie',
      blocks: [['p', 'Voor een spuitgietmachine wordt meestal de BU-serie ingezet: een bypassfilter die rechtstreeks op de hogedrukleiding komt, zonder eigen pomp of motor [1].'],
        ['ul', ['Werkdruk tot 450 bar; het M-element filtert 2 µm absoluut [2].', 'Geschikt voor servo- en proportionele hydrauliek, typisch in kunststofinjectie [1][3].', 'Wilt u los van de machine filtreren, dan is de SE-serie met eigen motor-pompgroep een alternatief [4].']],
        ['p', 'Het aantal en type elementen voor 400 l olie hangt af van uw olie en vervuiling. Laat dat bevestigen door een specialist of via een gratis olieanalyse.']],
      src: [{ page: 'BU-serie · Voor welke toepassingen?', u: 'producten.html#p-bu' }, { pdf: 'BU-2023-UK-.pdf', q: 'pressure bar micron' }, { page: 'Hydraulische systemen', u: 'homepage.html#sectoren' }, { pdf: 'SE-2019-ENGLISH.pdf', q: 'pump motor offline' }],
      follow: ['Hoeveel elementen heb ik nodig voor 400 l?', 'Wat is het verschil tussen BU en SE?', 'Welke reinheid hebben servokleppen nodig?'] },
    { m: /water|vocht|tandwiel/, prod: 'vac', lead: 'Advies over water in olie',
      blocks: [['p', 'Water uit tandwielolie haalt u, afhankelijk van de hoeveelheid, op drie manieren:'],
        ['ul', ['Beperkte hoeveelheden: de cellulose van een Triple R-element absorbeert water tot onder 100 ppm; het WE100-element neemt tot 900 ml op en haalt < 80 ppm [1].', 'Continue waterinloop: een WS-coalescer scheidt het water af [2].', 'Veel of opgelost water: een vacuümontwateraar verwijdert 80% van het opgeloste en 100% van het vrije water, zonder verbruiksmateriaal [3].']],
        ['p', 'Welke oplossing past, hangt af van het watergehalte in uw olie. Een olieanalyse meet dat in ppm.']],
      src: [{ page: 'Filterelementen · WE100', u: 'producten.html#p-elementen' }, { pdf: 'WS-2019-ENGLISH.pdf', q: 'water coalescing separator' }, { pdf: 'VacuumDehydrator-TRVS-N30E-ENG.pdf', q: 'water dissolved free removal' }],
      follow: ['Hoe neem ik een oliestaal uit een tandwielkast?', 'Is de vacuümontwateraar ook ATEX?', 'Wat staat er in het testrapport van de vacuümontwateraar?'] },
    { m: /iso|4406|21\/18|reinheid|nas/, prod: 'el', lead: 'Laat uw reinheid meten',
      blocks: [['p', 'Een ISO 4406-code telt de deeltjes per ml olie in drie groottes: groter dan 4, 6 en 14 µm [1].'],
        ['ul', ['21 = 10.000 tot 20.000 deeltjes > 4 µm per ml.', '18 = 1.300 tot 2.500 deeltjes > 6 µm per ml.', '16 = 320 tot 640 deeltjes > 14 µm per ml.']],
        ['p', 'Elke stap lager halveert ongeveer het aantal deeltjes. Welke code uw componenten nodig hebben, staat in de tabel “Recommended cleanliness” [2].']],
      src: [{ pdf: 'iso440637534.pdf', q: '4406 particles ml code' }, { pdf: 'Recommended-cleanliness4.pdf', q: 'cleanliness servo valve' }],
      follow: ['Welke reinheid hebben servokleppen nodig?', 'Wat is het verschil met NAS 1638?', 'Hoe verlaag ik mijn ISO-code?'] }
  ];
  const SUGGEST = ['Welke filter heb ik nodig voor een spuitgietmachine met 400 liter olie?', 'Hoe verwijder ik water uit tandwielolie?', 'Wat betekent ISO 4406 21/18/16?', 'Welke viscositeit kan de OSCA-serie aan?', 'Wat is het maximale debiet van de SS-serie?', 'Hoe werkt de Quicktoron?'];

  function openAsk(prefill) {
    lastFocus = document.activeElement; ask.hidden = false; document.body.style.overflow = 'hidden';
    if (!drawer.hidden) { drawer.hidden = true; mOpen.setAttribute('aria-expanded', 'false'); }
    askQ.value = prefill || ''; render(); askQ.focus(); ensurePdfIndex();
  }
  function closeAsk() { clearInterval(streamTimer); ask.hidden = true; document.body.style.overflow = ''; (lastFocus || document.getElementById('ask-open')).focus(); }
  function render() { const v = askQ.value.trim(); askGo.disabled = !v; askQ.setAttribute('aria-expanded', 'true'); sel = -1; v ? renderResults(v) : renderEmpty(); }
  function hl(text, terms) { let h = esc(text); terms.filter(t => t.length > 2).forEach(t => { h = h.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); }); return h; }

  function renderEmpty() {
    askBody.innerHTML = `<div class="cols"><div><h3 class="lbl">Voorbeeldvragen</h3><ul class="qlist" role="listbox" aria-label="Voorbeeldvragen">${SUGGEST.map(s => `<li><button type="button" role="option" data-ask="${esc(s)}">${I.q}${esc(s)}</button></li>`).join('')}</ul></div>
      <div><h3 class="lbl">Populaire producten</h3>${['bu', 'el', 'vac'].map(k => `<a class="pmini" href="${PROD[k].u}" data-close-go><img src="${PROD[k].img}" alt=""><span><b>${PROD[k].n}</b><span>${PROD[k].c.slice(0, 2).join(' · ')}</span></span></a>`).join('')}
      <h3 class="lbl" style="margin-top:var(--s-4)">Datasheets</h3>${PDFS.slice(0, 3).map(d => `<a class="pmini" href="${pdfHref(d.f, 1)}" target="_blank" rel="noopener"><span class="ty pdf" style="font-size:11px;padding:2px 8px;border-radius:999px;background:#FDECEA;color:#9B2C1F">PDF</span><span><b>${esc(d.t)}</b><span>Engelstalig</span></span></a>`).join('')}</div></div>`;
  }
  function renderResults(v) {
    const terms = expand(v);
    const pageHits = PAGES.map(it => { const hay = norm(it.t + ' ' + it.s + ' ' + it.k); const sc = terms.reduce((a, t) => a + (hay.includes(t) ? (norm(it.t).includes(t) ? 3 : 1) : 0), 0); return { it, sc }; }).filter(x => x.sc > 0).sort((a, b) => b.sc - a.sc);
    const pdfHits = scorePdf(terms, detectProduct(v)).slice(0, 4);
    let html = `<button type="button" class="askrow" role="option" data-ask="${esc(v)}"><span class="spark">${I.spark}</span><span>Stel deze vraag: <b>“${esc(v)}”</b></span><span class="kbd" aria-hidden="true">↵</span></button>`;
    let any = false;
    ['Producten', 'Oplossingen', 'Kennisbank', 'Sectoren'].forEach(g => { const list = pageHits.filter(h => h.it.g === g).slice(0, 3); if (!list.length) return; any = true;
      html += `<div class="grp"><h3 class="lbl">${g}</h3>${list.map(({ it }) => `<a class="res" role="option" href="${it.u}" data-close-go><span class="ty">${{ Producten: 'Product', Oplossingen: 'Oplossing', Kennisbank: 'Artikel', Sectoren: 'Sector' }[g]}</span><b>${hl(it.t, terms)}</b><span class="sn">${hl(it.s, terms)}</span></a>`).join('')}</div>`; });
    if (pdfHits.length) { any = true;
      html += `<div class="grp"><h3 class="lbl">Downloads · in de PDF’s gevonden</h3>${pdfHits.map(({ ch }) => `<a class="res" role="option" href="${pdfHref(ch.f, ch.page)}" target="_blank" rel="noopener"><span class="ty pdf">PDF</span><b>${esc(ch.t)} <span class="srcpg">· p. ${ch.page}</span></b><span class="sn">${hl(snippet(ch.text, terms), terms)}</span></a>`).join('')}</div>`; }
    else if (!pdfChunks) html += `<p class="none">De PDF’s worden nog geïndexeerd; resultaten uit datasheets verschijnen zo meteen.</p>`;
    if (!any && pdfChunks) html += `<p class="none">Geen directe resultaten. Stel de vraag hierboven, dan zoekt de assistent verder in alle pagina’s en datasheets.</p>`;
    askBody.innerHTML = html;
  }

  function tokens(blocks) { const out = []; blocks.forEach(([t, x]) => { if (t === 'p') out.push({ open: 'p', words: x }); else x.forEach(li => out.push({ open: 'li', words: li })); }); return out; }
  function wordsHtml(s) { return s.split(/(\[\d\])/).filter(Boolean).flatMap(part => /^\[\d\]$/.test(part) ? [`<sup><a href="#src-${part[1]}" aria-label="bron ${part[1]}">${part[1]}</a></sup>`] : part.split(/(\s+)/).map(esc)); }
  function srcCard(s, i) {
    if (s.pdf) return `<a class="src pdf" id="src-${i + 1}" href="${pdfHref(s.pdf, s.pageNo)}" target="_blank" rel="noopener"><span class="n">${i + 1}</span><b>${esc(s.title)}</b><span>PDF · p. ${s.pageNo} ↗</span></a>`;
    return `<a class="src" id="src-${i + 1}" href="${s.u}" data-close-go><span class="n">${i + 1}</span><b>${esc(s.page)}</b><span>Webpagina</span></a>`;
  }
  async function answer(q) {
    clearInterval(streamTimer);
    askQ.value = q; askGo.disabled = false;
    const nq = norm(q), terms = expand(q);
    const offtopic = /prijs|kost|kosten|concurrent|cjc|hydac|pall|weer|voetbal|recept/.test(nq);
    const a = !offtopic && ANSWERS.find(x => x.m.test(nq));
    askBody.innerHTML = `<button type="button" class="back" data-back>${I.back}Terug naar resultaten</button><p class="qhead">${esc(q)}</p><p class="ai busy"><span class="dot"></span><span>Zoekt in webpagina’s en PDF’s…</span></p>`;
    if (!pdfChunks) { try { await ensurePdfIndex(); } catch (e) {} }
    if (askQ.value !== q) return;
    const pk = detectProduct(q);
    let hits = offtopic ? [] : scorePdf(terms, pk);
    if (pk && hits.some(h => h.ch.p === pk)) hits = hits.filter(h => h.ch.p === pk);
    const strong = hits.filter(h => h.hit >= (pk ? 1 : Math.min(2, terms.length)) && h.sc > 3).slice(0, 3);
    if (!a && !strong.length) return noAnswer(q);
    let blocks, src, prod, lead, follow, mode;
    if (a) {
      mode = 'gen'; blocks = a.blocks; lead = a.lead; follow = a.follow; prod = PROD[a.prod];
      src = a.src.map(s => s.pdf ? (r => ({ pdf: s.pdf, pageNo: r.page, title: r.t }))(resolvePdf(s.pdf, s.q)) : s);
    } else {
      mode = 'ext'; lead = 'Stel uw vraag aan een specialist'; prod = null;
      src = strong.map(h => ({ pdf: h.ch.f, pageNo: h.ch.page, title: h.ch.t, quote: bestSentence(h.ch.text, terms) }));
      blocks = [['p', `Ik vond ${src.length === 1 ? 'één relevante passage' : src.length + ' relevante passages'} in de datasheets van Triple R. Hieronder letterlijk, met de pagina waar ze staan.`]];
      const pk2 = pk || strong.map(h => h.ch.p).find(Boolean); if (pk2) { const m = { bu: 'bu', vacuum: 'vac' }[pk2]; if (m) prod = PROD[m]; }
      follow = SUGGEST.slice(0, 3);
    }
    const docs = new Set((pdfChunks || []).map(c => c.f)).size;
    askBody.innerHTML = `<button type="button" class="back" data-back>${I.back}Terug naar resultaten</button><p class="qhead">${esc(q)}</p>
      <p class="ai busy" id="ai-l"><span class="dot"></span><span id="ai-t">AI-antwoord wordt opgesteld…</span></p>
      <div class="ans" id="ans" aria-live="polite" aria-busy="true"></div>
      <div id="after" hidden>
        ${mode === 'ext' ? src.map((s, i) => `<blockquote class="quote">“${hl(s.quote, terms)}”<cite>${esc(s.title)} · p. ${s.pageNo} <sup><a href="#src-${i + 1}">${i + 1}</a></sup> · Engelstalige datasheet</cite></blockquote>`).join('') : ''}
        <h3 class="lbl" style="margin-top:var(--s-5)">Bronnen <span style="text-transform:none;letter-spacing:0">· gezocht in ${PAGES.length} webpagina’s en ${docs} PDF’s</span></h3><div class="srcs">${src.map(srcCard).join('')}</div>
        ${prod ? `<div class="pcard"><img src="${prod.img}" alt=""><div><b>${prod.n}</b><div class="chips">${prod.c.map(c => `<span>${c}</span>`).join('')}</div><div class="links"><a href="${prod.u}" data-close-go>Bekijk product</a>${prod.pdf ? `<a href="${pdfHref(prod.pdf, 1)}" target="_blank" rel="noopener">Datasheet (PDF)</a>` : ''}</div></div></div>` : ''}
        ${handoff(lead, q)}
        <div class="follow" aria-label="Vervolgvragen">${follow.map(f => `<button type="button" data-ask="${esc(f)}">${esc(f)}</button>`).join('')}</div>
        <div class="fb"><span>Was dit antwoord nuttig?</span><button type="button" aria-pressed="false" aria-label="Nuttig" data-fb>${I.up}</button><button type="button" aria-pressed="false" aria-label="Niet nuttig" data-fb>${I.down}</button><span id="fb-t" role="status"></span></div>
      </div>`;
    const ans = document.getElementById('ans'), toks = tokens(blocks);
    const finish = () => { ans.querySelector('.caret')?.remove(); ans.setAttribute('aria-busy', 'false'); document.getElementById('ai-l').classList.remove('busy'); document.getElementById('ai-t').textContent = mode === 'gen' ? 'AI-antwoord op basis van Triple R-documentatie' : 'Gevonden in de documentatie (letterlijke passages)'; document.getElementById('after').hidden = false; };
    if (reduce) { toks.forEach(t => appendBlock(ans, t, wordsHtml(t.words).join(''))); finish(); return; }
    let bi = 0, wi = 0, words = null, el = null;
    streamTimer = setInterval(() => {
      if (!words) { if (bi >= toks.length) { clearInterval(streamTimer); finish(); return; } words = wordsHtml(toks[bi].words); el = appendBlock(ans, toks[bi], ''); wi = 0; }
      ans.querySelector('.caret')?.remove();
      for (let n = 0; n < 3 && wi < words.length; n++) el.insertAdjacentHTML('beforeend', words[wi++]);
      el.insertAdjacentHTML('beforeend', '<span class="caret" aria-hidden="true"></span>');
      if (wi >= words.length) { words = null; bi++; }
    }, 40);
  }
  function noAnswer(q) {
    askBody.innerHTML = `<button type="button" class="back" data-back>${I.back}Terug naar resultaten</button><p class="qhead">${esc(q)}</p>
      <div class="noans" role="status"><p class="ai"><span class="dot"></span>AI-antwoord</p><p><b>Daar vind ik geen betrouwbaar antwoord op in de documentatie van Triple R.</b></p><p class="small muted">Ik heb gezocht in de webpagina’s en alle datasheets, maar geef liever geen gok. Een specialist beantwoordt uw vraag persoonlijk.<i class="tb" title="Te bevestigen: responstijd"></i></p></div>
      ${handoff('Stel uw vraag aan een specialist', q)}`;
  }
  function appendBlock(ans, t, html) {
    if (t.open === 'li') { let ul = ans.lastElementChild; if (!ul || ul.tagName !== 'UL') { ul = document.createElement('ul'); ans.appendChild(ul); } const li = document.createElement('li'); li.innerHTML = html; ul.appendChild(li); return li; }
    const p = document.createElement('p'); p.innerHTML = html; ans.appendChild(p); return p;
  }
  function handoff(lead, q) {
    return `<div class="handoff"><p>Volgende stap. Het adviesformulier opent vooraf ingevuld met uw vraag; u kunt alles nog aanpassen.</p>
      <div class="btns"><a class="btn btn--primary" href="#?advies&vraag=${encodeURIComponent(q)}">${esc(lead)}</a><a class="btn btn--secondary" href="homepage.html#olieanalyse" data-close-go>Gratis olieanalyse</a><a class="btn btn--secondary" href="tel:+3238254647">Bel +32 3 825 46 47</a></div></div>`;
  }

  document.querySelectorAll('[data-ask-open]').forEach(b => {
    b.addEventListener('click', () => openAsk());
    b.addEventListener('pointerenter', () => ensurePdfIndex(), { once: true }); /* index opwarmen bij hover */
  });
  document.querySelectorAll('[data-ask-embed]').forEach(f => f.addEventListener('submit', e => { e.preventDefault(); const v = f.querySelector('input').value.trim(); openAsk(v); if (v) answer(v); }));
  askQ.addEventListener('input', render);
  askGo.addEventListener('click', () => askQ.value.trim() && answer(askQ.value.trim()));
  ask.addEventListener('click', e => {
    const t = e.target.closest('[data-ask],[data-back],[data-close],[data-close-go],[data-fb]');
    if (!t) return;
    if (t.hasAttribute('data-ask')) answer(t.dataset.ask);
    else if (t.hasAttribute('data-back')) { clearInterval(streamTimer); render(); askQ.focus(); }
    else if (t.hasAttribute('data-close') || t.hasAttribute('data-close-go')) closeAsk();
    else if (t.hasAttribute('data-fb')) { t.parentElement.querySelectorAll('[data-fb]').forEach(b => b.setAttribute('aria-pressed', b === t)); document.getElementById('fb-t').textContent = 'Bedankt voor uw feedback.'; }
  });
  ask.addEventListener('keydown', e => {
    if (e.key === 'Escape') { e.preventDefault(); closeAsk(); return; }
    const opts = [...askBody.querySelectorAll('[role="option"]')];
    if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && opts.length && document.activeElement === askQ) {
      e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + opts.length) % opts.length;
      opts.forEach((o, i) => o.setAttribute('aria-selected', i === sel)); opts[sel].scrollIntoView({ block: 'nearest' });
    }
    if (e.key === 'Enter' && document.activeElement === askQ) { e.preventDefault(); if (sel >= 0 && opts[sel]) opts[sel].click(); else if (askQ.value.trim()) answer(askQ.value.trim()); }
    if (e.key === 'Tab') { const f = [...ask.querySelectorAll('a[href],button:not([disabled]),input')].filter(x => x.offsetParent !== null); if (!f.length) return; const first = f[0], last = f[f.length - 1]; if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); } else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); } }
  });
  const ph = document.getElementById('ask-ph'), PH = ['Zoek een product of stel een vraag', 'Bv. varnish in hydraulische olie', 'Bv. filter voor 450 bar', 'Bv. viscositeit OSCA-serie'];
  let phi = 0; if (!reduce && ph) setInterval(() => { ph.style.opacity = 0; setTimeout(() => { phi = (phi + 1) % PH.length; ph.textContent = PH[phi]; ph.style.opacity = 1; }, 300); }, 3600);
  if (params.has('ask')) { openAsk(params.get('ask') || ''); if (params.get('ask')) answer(params.get('ask')); }

  document.addEventListener('keydown', e => {
    const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName);
    if (((e.key === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !typing)) && ask.hidden) { e.preventDefault(); openAsk(); }
    if (e.key === 'Escape' && ask.hidden) { closeMm(); if (!drawer.hidden) openDrawer(false); }
  });

  /* =====================================================================
     BEWEGING — reveals, tellers, header, scroll-voortgang, parallax, spotlight
     ===================================================================== */
  const hdr = document.querySelector('.hdr'), bar = document.querySelector('.progress-line');
  let ticking = false;
  const onScroll = () => { if (ticking) return; ticking = true; requestAnimationFrame(() => { ticking = false; hdr.classList.toggle('scrolled', scrollY > 60); if (bar) bar.style.setProperty('--p', Math.min(1, scrollY / Math.max(1, document.documentElement.scrollHeight - innerHeight)).toFixed(4)); }); };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  const fmt = new Intl.NumberFormat('nl-BE');
  const countUp = el => { const to = +el.dataset.count, t0 = performance.now(), D = 1400; const step = now => { const k = Math.min(1, (now - t0) / D), v = Math.round(to * (1 - Math.pow(1 - k, 3))); el.textContent = fmt.format(v); if (k < 1) requestAnimationFrame(step); }; requestAnimationFrame(step); };
  if (!reduce && 'IntersectionObserver' in window) {
    const SEL = '.ccard,.prod,.case,.sectors li,.oa ol li,.results>div,.facts>div,.rrr li,.arts li,.faq details,.steps li,.how figure,.head,.sect__img,.oa__img,.sus figure,.co2,.finder,.cta,[data-reveal]';
    const io = new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting) return; e.target.classList.add('in'); e.target.classList.remove('pre'); io.unobserve(e.target); }), { threshold: .12, rootMargin: '0px 0px -6% 0px' });
    document.querySelectorAll(SEL).forEach(el => {
      if (el.closest('.hero') || el.closest('.ask')) return;
      const sibs = [...el.parentElement.children].filter(c => c.matches(SEL));
      el.style.setProperty('--i', Math.min(6, sibs.indexOf(el)));
      el.classList.add('rv');
      if (el.getBoundingClientRect().top > innerHeight * .9) { el.classList.add('pre'); io.observe(el); } else el.classList.add('in');
    });
    const io2 = new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting) return; e.target.classList.add('in'); io2.unobserve(e.target); }), { threshold: .3 });
    document.querySelectorAll('.chart,.photo-band,[data-in]').forEach(el => io2.observe(el));
    const io3 = new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting) return; countUp(e.target); io3.unobserve(e.target); }), { threshold: .6 });
    document.querySelectorAll('[data-count]').forEach(el => io3.observe(el));
  } else document.querySelectorAll('.chart,.photo-band,[data-in]').forEach(el => el.classList.add('in'));

  if (!reduce && matchMedia('(pointer:fine)').matches) {
    document.querySelectorAll('.hero').forEach(h => {
      const st = h.querySelector('.stage'); if (!st) return;
      h.addEventListener('pointermove', e => { const r = h.getBoundingClientRect(); st.style.setProperty('--px', ((e.clientX - r.left) / r.width - .5).toFixed(3) * 2); st.style.setProperty('--py', ((e.clientY - r.top) / r.height - .5).toFixed(3) * 2); });
      h.addEventListener('pointerleave', () => { st.style.setProperty('--px', 0); st.style.setProperty('--py', 0); });
    });
    document.addEventListener('pointermove', e => { const c = e.target.closest?.('.ccard,.prod,.case'); if (!c) return; const r = c.getBoundingClientRect(); c.style.setProperty('--mx', (e.clientX - r.left) + 'px'); c.style.setProperty('--my', (e.clientY - r.top) + 'px'); }, { passive: true });
  }
})();
