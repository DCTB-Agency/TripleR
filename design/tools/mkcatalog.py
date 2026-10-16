"""Productcatalogus per model, uit de datasheets in design/pdf (stand oktober 2026).

Gebruik (vanuit design/):  python3 tools/mkcatalog.py
Schrijft: data/products.json (bron voor Astro content collections) en catalog.js (window.RRR_CATALOG voor de prototypes).

Regels: alleen waarden die letterlijk in een datasheet staan. Tegenstrijdigheden en ontbrekende waarden krijgen
een 'confirm'-notitie; die verschijnen op de site als [CONFIRM]-marker.
"""
import json

CATS = [
    ('druk', 'Op de drukleiding', 'Bypassfilters die u aansluit op een bestaande drukleiding. Geen pomp of motor nodig.'),
    ('lagedruk', 'Bypass bij lage druk', 'Filterhuizen voor motorolie, smeersystemen en filterinstallaties tot enkele bar.'),
    ('offline', 'Offline met eigen pomp', 'Zelfaanzuigende units met motor-pompgroep: stationair, aan de wand of mobiel.'),
    ('vullen', 'Vulpompen', 'Olie gefilterd overpompen en machines vullen.'),
    ('water', 'Water verwijderen', 'Vacuümdrogers en olie-waterafscheiders.'),
    ('lucht', 'Lucht en schuim', 'Ontluchters op basis van het cycloonprincipe.'),
    ('proces', 'Koelvloeistof en proceswater', 'Centrifuges zonder verbruiksmateriaal.'),
    ('elementen', 'Filterelementen', 'Vervangelementen en voorfilters voor alle Triple R-systemen.'),
]
FLUIDS = {'hyd': 'Hydraulische olie', 'lube': 'Smeer- en tandwielolie', 'eng': 'Motorolie', 'wg': 'Water-glycol',
          'comp': 'Compressorolie', 'fuel': 'Diesel', 'cool': 'Koelvloeistof en proceswater'}
VERSIONS = {'stationair': 'Stationair', 'mobiel': 'Mobiel', 'wand': 'Wandmontage', 'inline': 'In de leiding'}

SERIES = {
    'bu': dict(n='BU-serie', cat='druk', img='BU-Series.png', pdf='BU-2023-UK-.pdf', s='Bypassfilters voor hydraulische systemen, direct op de drukleiding.'),
    'bu-wind': dict(n='BU-100E-Wind', cat='druk', img='BU-Series.png', pdf='BU-100E-Wind-S.pdf', s='BU-filter voor tandwielkasten van windturbines.'),
    'hp': dict(n='Stalen huizen HP', cat='druk', img=None, pdf='STEEL-housing-HP.pdf', s='Stalen bypasshuizen voor (koel)compressoren.'),
    'tr': dict(n='TR-serie', cat='lagedruk', img=None, pdf='TR-2019-ENGLISH.pdf', s='Motorolie-reinigers voor dieselmotoren en generatoren, systemen onder 6 bar.'),
    'ss': dict(n='SS-serie', cat='lagedruk', img='ss.png', pdf='SS-2019-ENGLISH-.pdf', s='Stalen filterhuizen voor 2 tot 12 elementen, voor hoge debieten.'),
    'se': dict(n='SE-serie', cat='offline', img='se.png', pdf='SE-2019-ENGLISH.pdf', s='Offline oliereinigers met eigen motor-pompgroep.'),
    'se-mobile': dict(n='SE Mobile', cat='offline', img='se.png', pdf='SE-Mobile-2023-ENGLISH.pdf', s='Mobiele SE-units op wielen, voor service en onderhoud.'),
    'osca': dict(n='OSCA-serie', cat='offline', img='osca.png', pdf='OSCA-2019-ENGLISH.pdf', s='Offline reinigers met hoog debiet voor grote volumes.'),
    'vp': dict(n='Vulpompen', cat='vullen', img=None, pdf=None, s='Pompen om olie gefilterd over te pompen en machines te vullen.'),
    'vacuum': dict(n='Vacuümdroger', cat='water', img='vacuum.png', pdf='VacuumDehydrator-TRVS-N30E-ENG.pdf', s='Volautomatische waterverwijdering onder vacuüm.'),
    'ws': dict(n='WS-serie', cat='water', img='ws.png', pdf='WS-2019-ENGLISH.pdf', s='Olie-waterafscheiders op basis van coalescentie.'),
    'quicktoron': dict(n='Quicktoron', cat='lucht', img='quicktoron.png', pdf='QUICKTORON-2023-ENGLISH.pdf', s='Cycloon-ontluchter in roestvast staal.'),
    'centrifuges': dict(n='Centrifuges', cat='proces', img='centrifuge.png', pdf='Centrifuges_2014_UK-1.pdf', s='Deeltjes en slib uit koelvloeistof en proceswater.'),
    'el-m': dict(n='M-elementen', cat='elementen', img='elements.png', pdf='Element-data-sheet-2023.pdf', s='Fijnste deeltjesfiltratie, 2 en 3 µm absoluut.'),
    'el-e': dict(n='E-elementen', cat='elementen', img='elements.png', pdf='Element-data-sheet-2023.pdf', s='5 µm absoluut, voor motor- en smeerolie.'),
    'el-x': dict(n='X-elementen', cat='elementen', img='elements.png', pdf='Element-data-sheet-2023.pdf', s='10 µm absoluut, lange levensduur, hoge viscositeit.'),
    'el-d': dict(n='D-elementen', cat='elementen', img='elements.png', pdf='Element-data-sheet-2023.pdf', s='Tweetraps element met extra vuilcapaciteit.'),
    'el-v': dict(n='V100-elementen', cat='elementen', img='elements.png', pdf='V100-ENGLISH.pdf', s='Varnish-verwijderaar met absorberende pouch.'),
    'el-w': dict(n='Water- en water-glycolelementen', cat='elementen', img='elements.png', pdf='Element-data-sheet-2023.pdf', s='Waterabsorptie en elementen voor water-glycol.'),
    'el-pre': dict(n='Voorfilters', cat='elementen', img=None, pdf='Elements-ENGLISH.pdf', s='Wasbare metalen aanzuigfilters, 80/100 µm.'),
}

P = []


def add(id, series, name, art, s, specs, fluid=(), version=(), vol=None, vol_grey=None, flow=None, elements=(), fits=(), page=2, confirm=(), img=None, old=None):
    P.append(dict(id=id, series=series, n=name, art=art, old=old, s=s, specs=specs, fluid=list(fluid), version=list(version),
                  vol=vol, volGrey=vol_grey, flow=flow, elements=list(elements), fits=list(fits), page=page, confirm=list(confirm), img=img))


M100_SET = ['m100', 'e100', 'x100', 'd100', 'v100-m', 'v100-e', 'v100-x', 'we100']

# ---------------- BU-serie (BU-2023-UK-.pdf p.2) ----------------
BU_P = ('Werkdruk', '10 tot 245 bar (gegarandeerd debiet)')
BU_V = ('Viscositeit', '9 tot 180 cSt')
BU_R = ('Overdrukventiel', 'opent bij 4,5 bar ΔP')
BU_CONF = ['Datasheet: debiet gegarandeerd van 10 tot 245 bar; elders op de site staat "tot 450 bar"']
for id, name, art, flow, thr, n, kg, dim, mat, vol, grey, els in [
    ('bu30e', 'BU30E', 'TR-19450', 1.0, '1/4" x 1/4" BSPT', 1, 2.5, '14 x 12 x 29 cm', 'aluminium spuitgietwerk', (0, 300), None, ['m30', 'e30', 'x30']),
    ('bu100e', 'BU100E', 'TR-19530', 2.0, '1/4" x 3/8" BSPT', 1, 6.5, '23 x 17 x 32 cm', 'aluminium spuitgietwerk', (300, 600), 800, ['m100', 'e100', 'x100', 'd100', 'we100', 'v100-m', 'v100-e', 'v100-x']),
    ('bu200e', 'BU200E', 'TR-19200', 4.0, '1/4" x 1/4" BSPT', 2, 8.0, '24 x 24 x 41 cm', 'roestvast staal', (600, 1200), 1800, ['m100', 'e100', 'x100', 'd100', 'we100']),
    ('bu300e', 'BU300E', 'TR-19320', 6.0, '1/2" x 1/2" BSPT', 3, 12.0, '24 x 24 x 77 cm', 'roestvast staal', (1200, 1800), None, ['m100', 'e100', 'x100', 'd100', 'we100']),
]:
    add(id, 'bu', name, art, f'Bypassfilter op de drukleiding met {n} element{"en" if n > 1 else ""}, voor hydraulische olie.',
        [('Debiet', f'{flow:.1f} l/min'.replace('.', ',')), BU_P, BU_V, ('Aansluiting in/uit', thr), ('Elementen', f'{n} × {"30" if id == "bu30e" else "100"}-formaat'),
         BU_R, ('Gewicht', f'{kg:.1f} kg'.replace('.', ',')), ('Afmetingen', dim), ('Materiaal', mat)],
        fluid=['hyd'], version=['stationair'], vol=list(vol), vol_grey=grey, flow=flow, elements=els, confirm=BU_CONF)
for id, name, art, flow, thr, n, kg, dim, mat, vol, grey in [
    ('bu100ew', 'BU100EW', 'TR-19550', 1.5, '1/4" x 3/8" BSPT', 1, 6.5, '23 x 17 x 32 cm', 'gecoat', (0, 300), 600),
    ('bu200ew', 'BU200EW', 'TR-19100', 3.0, '1/4" x 1/4" BSPT', 2, 8.0, '24 x 24 x 41 cm', 'roestvast staal', (300, 600), 800),
    ('bu300ew', 'BU300EW', 'TR-19700', 4.0, '1/2" x 1/2" BSPT', 3, 12.0, '24 x 24 x 77 cm', 'roestvast staal', (600, 800), None),
]:
    add(id, 'bu', name, art, f'BU-bypassfilter voor water-glycol met {n} WG/DWG-element{"en" if n > 1 else ""}.',
        [('Debiet', f'{flow:.1f} l/min'.replace('.', ',')), BU_P, ('Vloeistof', 'water-glycol'), ('Aansluiting in/uit', thr), ('Elementen', f'{n} × WG100 of DWG100'),
         BU_R, ('Gewicht', f'{kg:.1f} kg'.replace('.', ',')), ('Afmetingen', dim), ('Materiaal', mat)],
        fluid=['wg'], version=['stationair'], vol=list(vol), vol_grey=grey, flow=flow, elements=['wg100', 'dwg100'], confirm=BU_CONF)
add('bu100e-wind', 'bu-wind', 'BU-100E-Wind', 'TR-19580', 'BU100E-uitvoering voor windturbines, met X100-element, manometer en montagebeugel.',
    [('Debiet', '1,5 tot 2,0 l/min'), ('Max. druk met debiet', '12 MPa (120 bar)'), ('Terugslag- en overdrukventiel', '0,45 MPa'), ('Aansluiting in/uit', 'Rc 1/4" x Rc 3/8"'),
     ('Element', '1 × X100 (standaard)'), ('Manometer', 'Ø40, 0 tot 1 MPa'), ('Afmetingen', 'Ø206 mm, hoogte ca. 255 mm')],
    fluid=['lube'], version=['stationair'], vol=[0, 300], flow=1.75, elements=['x100'], page=1,
    confirm=['Bron is een technische tekening (MVU-TRE-2022). Volume "1 huis tot 300 l" komt uit de brochure windturbines.'])

# ---------------- Stalen huizen HP (STEEL-housing-HP.pdf p.2) ----------------
HP_CONF = ['Datasheet: pagina 1 vermeldt 25 bar, de specificatietabel 40 bar']
for id, name, art, flow, thr, el, kg, dim, vol, grey in [
    ('bf-15', 'BF-15', 'TR-18100', 1.5, '1/4" x 1/4" BSPT', 'm30', 8, '168 x 154 mm', (0, 300), None),
    ('bf-20', 'BF-20', 'TR-18120', 2.0, '1/4" x 3/8" BSPT', 'm50', 12, '189 x 250 mm', (300, 450), 300),
    ('al100-hp', 'AL100-HP', 'TR-10460', 3.0, '1/4" x 1/4" BSP', 'm100', 16, '260 x 330 mm', (450, 750), 450),
]:
    add(id, 'hp', name, art, 'Stalen bypasshuis voor (koel)compressoren, direct op de drukleiding, met M-element dat ammoniak verdraagt.',
        [('Debiet', f'ca. {flow:.1f} l/min'.replace('.', ',')), ('Max. druk', '40 bar'), ('Aansluiting in/uit', thr), ('Element', el.upper()),
         ('Gewicht', f'{kg} kg'), ('Afmetingen', dim), ('Materiaal', 'staal 52/3'), ('Certificaat', 'drukproefcertificaat per huis')],
        fluid=['comp'], version=['stationair'], vol=list(vol), vol_grey=grey, flow=flow, elements=[el], confirm=HP_CONF)

# ---------------- TR-serie (TR-2019-ENGLISH.pdf p.2) ----------------
for id, art, vol, flow, kg in [('al100', 'TR-10450', 45, 0.5, 5.5), ('al200', 'TR-121048', 100, 1.0, 12), ('al300', 'TR-121049', 150, 1.5, 18), ('al400', 'TR-121051', 200, 2.0, 25)]:
    add(id, 'tr', id.upper(), art, f'Bypassfilter voor motorolie, voor motoren met minder dan {vol} l olie.',
        [('Motorolievolume', f'< {vol} l'), ('Max. debiet', f'< {flow:.1f} l/min'.replace('.', ',')), ('Max. druk', '6 bar'), ('Aansluiting in/uit', '1/4" x 3/8" BSPT'),
         ('Elementen', 'E100, X100 of D100'), ('Gewicht', f'{kg} kg'.replace('.', ','))],
        fluid=['eng', 'lube'], version=['stationair'], vol=[0, vol], flow=flow, elements=['e100', 'x100', 'd100'])

# ---------------- SS-serie (SS-2019-ENGLISH-.pdf p.2) ----------------
SS_P = ('Druk', 'max. 4,5 bar werkdruk, barstdruk 15 bar')
for id, art, flow, thr, els, n, kg, dim, eltxt in [
    ('ss102', 'TR-11400', '~6 l/min', '3/8"', ['m100', 'e100', 'x100', 'd100', 'we100'], 2, 18, '300 x 300 x 600 mm', 'M/E/X/D/WE100, hoogte 114 mm'),
    ('ss103', 'TR-11410', '~9 l/min', '3/8"', ['m100', 'e100', 'x100', 'd100', 'we100'], 3, 22, '300 x 300 x 743 mm', 'M/E/X/D/WE100, hoogte 114 mm'),
    ('ss104', 'TR-11420', '~15 l/min', '3/8"', [], 4, 22, '300 x 300 x 743 mm', 'M/E/X100, hoogte 80 mm'),
    ('ss305', 'TR-10515', '35 tot 45 l/min', '1"', ['m300-h114', 'e300-h114', 'x300-h114', 'd300'], 5, 89, '480 x 480 x 1250 mm', 'M/E/X/D300, hoogte 114 mm'),
    ('ss306', 'TR-10520', '50 tot 60 l/min', '1"', ['m300-h80', 'e300-h80', 'x300-h80'], 6, 87, '480 x 480 x 1250 mm', 'M/E/X300, hoogte 80 mm'),
    ('ss12pf20', 'TR-12660', '30 tot 60 l/min', '1"', [], 12, 78, '480 x 480 x 1250 mm', 'PF20, verschillende fijnheden'),
]:
    add(id, 'ss', id.upper(), art, f'Stalen filterhuis met {n} elementen, voor filterinstallaties met hoog debiet en hoge viscositeit.',
        [('Debiet (olie 32 cSt)', flow), SS_P, ('Aansluiting in/uit', thr), ('Elementen', f'{n} × {eltxt}'), ('Gewicht', f'{kg} kg'), ('Afmetingen', dim), ('Materiaal', 'koolstofstaal')],
        fluid=['hyd', 'lube'], version=['stationair'], elements=els,
        confirm=['H80-elementen 100-formaat (M/E/X100-H80) zijn volgens de elementenbrochure uit productie'] if id == 'ss104' else [])

# ---------------- SE-serie (SE-2019-ENGLISH.pdf p.2) ----------------
SE_M = ('Motor', '230 V x 1 of 400 V x 3, 50/60 Hz')
SE_R = ('Overdrukventiel', '6,0 bar')
for id, name, flow, pw, thr, size, n, kg, dim, vol, grey in [
    ('se50e-bh', 'SE50E-BH', 1.6, '0,12 kW (230 V) / 0,18 kW (400 V)', '1/2" in en uit', '50', 1, 17.0, '363 x 230 x 460 mm', (0, 500), None),
    ('se100e-bh', 'SE100E-BH', 2.5, '0,12 kW (230 V) / 0,18 kW (400 V)', '1/2" in en uit', '100', 1, 17.4, '385 x 230 x 460 mm', (500, 750), 1000),
    ('se200e-bh', 'SE200E-BH', 5.0, '0,12 kW (230 V) / 0,18 kW (400 V)', '1/2" in en uit', '100', 2, 23.0, '470 x 400 x 370 mm', (1000, 1500), 2000),
    ('se400e-bh', 'SE400E-BH', 9.0, '0,37 kW', '1/2" in en uit', '100', 4, 40.0, '610 x 470 x 370 mm', (2000, 4000), None),
    ('se600e-bh', 'SE600E-BH', 12.0, '0,37 kW', '3/4" in, 1/2" uit', '100', 6, 50.0, '1080 x 470 x 370 mm', (4000, 6000), None),
]:
    els = ['m50', 'e50', 'x50'] if size == '50' else ['m100', 'e100', 'x100', 'd100', 'we100', 'v100-m', 'v100-e', 'v100-x']
    add(id, 'se', name, name.replace('E-', ''), f'Offline oliereiniger met eigen motor-pompgroep en {n} element{"en" if n > 1 else ""}, CE-gecertificeerd.',
        [('Debiet', f'{flow:.1f} l/min'.replace('.', ',')), SE_M, ('Vermogen', pw), ('Aansluiting', thr), ('Elementen', f'{n} × {size}-formaat'), SE_R,
         ('Gewicht', f'{kg:.1f} kg'.replace('.', ',')), ('Afmetingen', dim)],
        fluid=['hyd'], version=['stationair'], vol=list(vol), vol_grey=grey, flow=flow, elements=els)
add('se100e-wh', 'se', 'SE100E-WH', None, 'Wandmodel van de SE100E: offline oliereiniger met eigen motor-pompgroep, aan de wand gemonteerd.',
    [('Uitvoering', 'wandmontage, 400 V'), ('Elementen', '1 × 100-formaat')], fluid=['hyd'], version=['wand'], vol=[500, 750], vol_grey=1000,
    elements=['m100', 'e100', 'x100', 'd100', 'we100'], page=1, img='se100e-wh.jpg',
    confirm=['Alleen een 3D-weergave beschikbaar (se100e-wh.pdf); technische gegevens en artikelnummer volgen'])

# ---------------- SE Mobile (SE-Mobile-2023-ENGLISH.pdf p.2, SE-Mobile-HF-ENGLISH.pdf p.2) ----------------
MOB_OPT = ('Op aanvraag', 'smeerolie (L), diesel (D), water-glycol (W), 24 V, 100 V x 1 of 200 V x 3 60 Hz, ATEX')
add('se200e-mh', 'se-mobile', 'SE200E-MH', 'SE200 MH-1OS', 'Mobiele oliereiniger op wielen met 2 AL100-huizen, voor hydraulische olie.',
    [('Debiet', '5,0 l/min'), SE_M, ('Vermogen', '0,12 kW'), ('Aansluiting', '1/2" in x 10L uit'), ('Elementen', '2 × 100-formaat (M, E, X, D, WE, WG)'), SE_R,
     ('Gewicht', 'ca. 40 kg'), ('Afmetingen', '1200 x 610 x 585 mm')],
    fluid=['hyd'], version=['mobiel'], flow=5.0, elements=['m100', 'e100', 'x100', 'd100', 'we100', 'wg100'])
add('se400e-mh', 'se-mobile', 'SE400E-MH', 'SE400 MH-1OS', 'Mobiele oliereiniger op wielen met 4 elementen, voor grotere systemen.',
    [('Debiet', '9,0 l/min'), SE_M, ('Vermogen', '0,37 kW'), ('Aansluiting', '3/4" in x 1/2" uit'), ('Elementen', '4 × 100-formaat (M, E, X, D, WE, WG)'), SE_R,
     ('Gewicht', 'ca. 55 kg'), ('Afmetingen', '1200 x 610 x 585 mm')],
    fluid=['hyd'], version=['mobiel'], flow=9.0, elements=['m100', 'e100', 'x100', 'd100', 'we100', 'wg100'])
add('se200e-hf', 'se-mobile', 'SE200E Mobile High Flow', 'SE200E-HF', 'Mobiele vul-, overpomp- en reinigingsunit: snel vullen aan 25 l/min en tegelijk dieptefiltratie.',
    [('Debiet vullen/overpompen', '25 l/min (1500 l/u)'), ('Debiet dieptefiltratie', '300 l/u'), SE_M, ('Vermogen', '0,37 kW'), ('Aansluiting', '1" in x 3/4" uit'),
     ('Aanzuigfilter', 'spin-on, 60 µm'), ('Hoofdfilter high flow', 'spin-on, 3 µm glasvezel'), ('Triple R-elementen', 'V100 (1 µm), M100 (3 µm), D100 (4 µm) of X100 (10 µm)'),
     ('Aantal filters', '2 spin-on + 2 Triple R'), SE_R, ('Gewicht', 'ca. 85 kg'), ('Afmetingen', '1200 x 610 x 585 mm')],
    fluid=['hyd'], version=['mobiel'], flow=25.0, elements=['v100-m', 'm100', 'd100', 'x100'],
    confirm=['Nieuw model (datasheet SE-Mobile-HF). Productfoto volgt'])

# ---------------- OSCA (OSCA-2019-ENGLISH.pdf p.2) ----------------
OS_M = ('Motor', '230 V x 1 of 400 V x 3, 50 Hz')
for id, name, pw, flow, io, dim, kg, els in [
    ('cs-su102-h114-2r', 'CS-SU102-H114-2R', '0,38 kW', 12, '1" x 1"', '406 x 1042 x 1007 mm', 115, ['m100', 'e100', 'x100', 'd100', 'we100']),
    ('cs-su103-h114-2r', 'CS-SU103-H114-2R', '0,75 kW', 20, '1" x 1"', '406 x 1042 x 1007 mm', 115, ['m100', 'e100', 'x100', 'd100', 'we100']),
    ('cs-su103-h114-3r', 'CS-SU103-H114-3R', '0,75 kW', 30, '1" x 1"', '406 x 1360 x 1007 mm', 140, ['m100', 'e100', 'x100', 'd100', 'we100']),
    ('cs-ss305-h114-1r', 'CS-SS305-H114-1R', '1,1 kW', 40, '2 x 1 1/4"', '700 x 1100 x 1520 mm', 200, ['m300-h114', 'e300-h114', 'x300-h114', 'd300']),
    ('cs-ss305-h114-2r', 'CS-SS305-H114-2R', '2,2 kW', 70, '2 x 1 1/4"', '700 x 1650 x 1520 mm', 280, ['m300-h114', 'e300-h114', 'x300-h114', 'd300']),
    ('cs-ss306-h80-2r', 'CS-SS306-H80-2R', '2,2 kW', 100, '2 x 1 1/4"', '700 x 1650 x 1520 mm', 280, ['m300-h80', 'e300-h80', 'x300-h80']),
]:
    hs = name.split('-')[1]
    add(id, 'osca', name, None, f'Offline reiniger met hoog debiet ({flow} l/min) op frame, met {name[-2]} {hs}-filterhuis{"" if name[-2] == "1" else "en"}.',
        [('Debiet', f'{flow} l/min'), OS_M, ('Vermogen', pw), ('Aansluiting in/uit', io), ('Afmetingen (L x B x H)', dim), ('Gewicht', f'{kg} kg'),
         ('Modelcode', f'CS = frame, {hs} = huis, {name.split("-")[2]} = elementhoogte, {name[-2:]} = aantal huizen'),
         ('Standaard', 'wasbaar metalen aanzuigfilter, manometers, bedieningspaneel, aftapkraan')],
        fluid=['hyd', 'lube'], version=['stationair'], vol=[1000, 50000], flow=flow, elements=els,
        confirm=['Artikelnummer niet vermeld in de datasheet'])

# ---------------- Water, lucht, proces ----------------
add('trvs-n30e', 'vacuum', 'TRVS-N30E', 'TRVS-N30E', 'Volautomatische vacuümdroger: 80% van het opgeloste en 100% van het vrije water, plus luchtbellen.',
    [('Debiet', '30 l/min'), ('Motor', '415 V x 3, 50 Hz'), ('Vermogen', '0,75 kW'), ('Aansluiting', 'in 1 1/4", uit 1"'), ('Viscositeit', '10 tot 600 cSt'),
     ('Olietemperatuur', '15 tot 60 °C'), ('Afmetingen', 'L 1350 x B 670 x H 1765 mm'), ('Gewicht', '410 kg')],
    fluid=['hyd', 'lube'], version=['stationair'], flow=30, page=2)
for id, art, flow, el, kg, dim in [('ws-wd', 'TR-16000', 1.8, '1 × WG100 + 1 × WS10', 25.0, '505 x 300 x 500 mm'),
                                   ('ws-wd-1pf', 'TR-16100', 1.8, '1 × WS10 + 1 × PF10', 27.4, '570 x 300 x 500 mm'),
                                   ('ws-su103-1r-ws20', 'TR-16300', 6.0, '3 × WG100 + 3 × WS20', 95.0, '440 x 955 x 1045 mm')]:
    add(id, 'ws', id.upper(), art, 'Olie-waterafscheider op basis van coalescentie, met kijkglas en snelle waterafvoer.',
        [('Debiet', f'{flow:.1f} l/min'.replace('.', ',')), ('Motor', '230 V x 1 of 400 V x 3, 50 Hz'), ('Vermogen', '0,12 kW (230 V) / 0,37 kW (400 V)'),
         ('Elementen', el), ('Overdrukventiel', '4,5 bar'), ('Gewicht', f'{kg:.1f} kg'.replace('.', ',')), ('Afmetingen', dim)],
        fluid=['hyd', 'lube'], version=['stationair'], flow=flow, elements=['ws10', 'wg100'] if id == 'ws-wd' else ['ws10'] if id == 'ws-wd-1pf' else ['wg100'])
for id, name, art, fl, ln, dia, kg in [('trqt-50-sus', 'TRQT-50-SUS', 'TR010390', '9 tot 50 l/min', '212 mm', '98 mm', 2.4),
                                        ('trqt-100-sus', 'TRQT-100-SUS', 'TR010500', '50 tot 100 l/min', '303 mm', '118 mm', 7.0)]:
    add(id, 'quicktoron', f'Quicktoron {name}', art, 'Ontluchter op basis van het cycloonprincipe; haalt fijne luchtbellen uit de olie.',
        [('Debiet', fl), ('Max. druk', '10 bar'), ('Max. viscositeit', '250 cSt'), ('Max. temperatuur', '120 °C'), ('Lengte', ln), ('Diameter', dia),
         ('Gewicht', f'{kg:.1f} kg'.replace('.', ',')), ('Materiaal', 'roestvast staal SCS13')],
        fluid=['hyd', 'lube'], version=['inline'])
for id, name, kw, fl, rpm, dim, kg, kind in [('trs30-m', 'TRS30-M', '0,75 kW', 30, '2.810', '300 x 500 x 377 mm', 55, 'manueel'),
                                              ('trs50-m', 'TRS50-M', '1,5 kW', 50, '1.881', '380 x 650 x 422 mm', 100, 'manueel'),
                                              ('trs100-a', 'TRS100-A', '3,7 kW', 100, '3.000', '630 x 1100 x 1768 mm', 650, 'automatisch'),
                                              ('trs200-a', 'TRS200-A', '5,5 kW', 200, '2.500', '730 x 1200 x 1768 mm', 750, 'automatisch')]:
    add(id, 'centrifuges', f'Centrifuge {name}', name, f'{kind.capitalize()}e centrifuge voor koelvloeistof, emulsies en proceswater, zonder verbruiksmateriaal.',
        [('Max. debiet', f'{fl} l/min (waterbasis; bij olie 50%)'), ('Motor', '400 V x 3, 50 Hz'), ('Vermogen', kw), ('Toerental', f'{rpm} tpm'),
         ('Bediening', kind), ('Afmetingen', dim), ('Gewicht', f'{kg} kg'), ('Olie', 'max. 20 cSt bij werktemperatuur')],
        fluid=['cool'], version=['stationair'], flow=fl)

# ---------------- Filterelementen (Element-data-sheet-2023.pdf + Elements-ENGLISH.pdf) ----------------
FIT = {'30': 'BU30E, SE30-YT, BF-15', '50': 'BU50E, SE50-YT, SE50E-BH, BF-20',
       '100': 'BU100E/BU200E/BU300E, SE100 tot SE600, AL100 en TR-serie, OSCA AL-serie, SU/SS102, SU/SS103, AL100-HP',
       '300-H114': 'SS305 en OSCA SS305', '300-H80': 'SS306 en OSCA SS306'}
FITS = {'30': ['bu30e', 'bf-15'], '50': ['se50e-bh', 'bf-20'], '100': ['bu100e', 'bu200e', 'bu300e', 'se100e-bh', 'se200e-bh', 'se400e-bh', 'se600e-bh', 'se200e-mh', 'se400e-mh', 'al100', 'al200', 'al300', 'al400', 'al100-hp', 'ss102', 'ss103', 'cs-su102-h114-2r', 'cs-su103-h114-2r', 'cs-su103-h114-3r'],
        '300-H114': ['ss305', 'cs-ss305-h114-1r', 'cs-ss305-h114-2r'], '300-H80': ['ss306', 'cs-ss306-h80-2r']}
ELS = [  # id, series, model, new, old, beta, water, dirt, dim, weight g, flow, size
    ('m30', 'el-m', 'M30-H114', 'EL03003', 'TR-20230', 'β2 > 75, β3 > 600', '~60 ml', '~35 g', 'Ø103 x 114 mm', 250, '1,0 l/min', '30'),
    ('m50', 'el-m', 'M50-H114', 'EL05004', 'TR-20330', 'β2 > 75, β3 > 600', '~130 ml', '~50 g', 'Ø142 x 114 mm', 490, '1,5 l/min', '50'),
    ('m100', 'el-m', 'M100-H114', 'EL10006', 'TR-20430', 'β2 > 200, β3 > 900', '~200 ml', '~95 g', 'Ø178 x 114 mm', 770, '2,0 tot 3,0 l/min', '100'),
    ('m300-h114', 'el-m', 'M300-H114', 'EL30004', 'TR-20520', 'β2 > 200, β3 > 900', '~560 ml', '~260 g', 'Ø303 x 114 mm', 2150, '5,5 tot 8,5 l/min', '300-H114'),
    ('m300-h80', 'el-m', 'M300-H80', 'EL30025', 'TR-20530', 'β2 > 200, β3 > 900', '~560 ml', '~260 g', 'Ø303 x 80 mm', 1510, '7,0 tot 11,0 l/min', '300-H80'),
    ('e30', 'el-e', 'E30-H114', 'EL03002', 'TR-20270', 'β3 > 75, β5 > 500', '~50 ml', '~40 g', 'Ø103 x 114 mm', 230, '1,0 l/min', '30'),
    ('e50', 'el-e', 'E50-H114', 'EL05002', 'TR-20370', 'β3 > 75, β5 > 500', '~100 ml', '~60 g', 'Ø142 x 114 mm', 420, '1,5 l/min', '50'),
    ('e100', 'el-e', 'E100-H114', 'EL10003', 'TR-20470', 'β3 > 75, β5 > 500', '~180 ml', '~110 g', 'Ø178 x 114 mm', 700, '2,0 tot 3,0 l/min', '100'),
    ('e300-h114', 'el-e', 'E300-H114', 'EL30003', 'TR-20510', 'β3 > 75, β5 > 500', '~500 ml', '~300 g', 'Ø303 x 114 mm', 1960, '5,5 tot 8,5 l/min', '300-H114'),
    ('e300-h80', 'el-e', 'E300-H80', 'EL30007', 'TR-20540', 'β3 > 75, β5 > 500', '~500 ml', '~300 g', 'Ø303 x 80 mm', 1375, '7,0 tot 11,0 l/min', '300-H80'),
    ('x30', 'el-x', 'X30-H114', 'EL03004', 'TR-25250', 'β5 > 75, β10 > 140', '~60 ml', '~55 g', 'Ø103 x 114 mm', 210, '1,0 l/min', '30'),
    ('x50', 'el-x', 'X50-H114', 'EL05007', 'TR-25350', 'β5 > 75, β10 > 140', '~130 ml', '~75 g', 'Ø142 x 114 mm', 400, '1,5 l/min', '50'),
    ('x100', 'el-x', 'X100-H114', 'EL10010', 'TR-25450', 'β5 > 75, β10 > 140', '~200 ml', '~130 g', 'Ø178 x 114 mm', 630, '2,0 tot 3,0 l/min', '100'),
    ('x300-h114', 'el-x', 'X300-H114', 'EL30006', 'TR-20512', 'β5 > 75, β10 > 140', '~560 ml', '~360 g', 'Ø303 x 114 mm', 1760, '5,5 tot 8,5 l/min', '300-H114'),
    ('x300-h80', 'el-x', 'X300-H80', 'EL30019', 'TR-20550', 'β5 > 75, β10 > 140', '~560 ml', '~360 g', 'Ø303 x 80 mm', 1230, '7,0 tot 11,0 l/min', '300-H80'),
    ('d100', 'el-d', 'D100-H114', 'EL10002', 'TR-20000', 'β2 > 75, β3 > 400', '~400 ml', '~170 g', 'Ø178 x 114 mm', 700, '2,0 l/min', '100'),
    ('d300', 'el-d', 'D300-H114', 'EL30001', 'TR-20515', 'β2 > 75, β3 > 400', '~1.100 ml', '~470 g', 'Ø303 x 114 mm', 1960, '5,5 tot 8,5 l/min', '300-H114'),
]
TXT = {'el-m': 'Hoogwaardig element voor hydraulische olie en diesel; verwachte reinheid NAS 6, ISO 16/14/12 of beter.',
       'el-e': 'Element voor motor- en smeerolie, en als eerste trap bij hydraulische olie met veel vuil.',
       'el-x': 'Long-life element met hoge vuilopname, ideaal voor hoge viscositeit (220 tot 460 cSt).',
       'el-d': 'Tweetraps element: X-medium bovenaan, M-medium onderaan, gescheiden door een vlies dat het onderste deel beschermt tegen water.'}
CONF_EL = {'m300-h114': ['Artikelnummer: datasheet 2023 EL30004, elementenbrochure EL30008'],
           'm300-h80': ['Artikelnummer: datasheet 2023 EL30025, elementenbrochure EL30008']}
for id, ser, name, new, old, beta, water, dirt, dim, g, flow, size in ELS:
    add(id, ser, name, new, TXT[ser],
        [('Filtergraad', beta), ('Waterabsorptie', water), ('Vuilcapaciteit (ISO 16889)', dirt), ('Filtermedium', 'cellulose'), ('Afmetingen', dim),
         ('Gewicht', f'{g} g'), ('Debiet (afh. van viscositeit)', flow), ('Past in', FIT[size])],
        fits=FITS[size], page=1, old=old, confirm=CONF_EL.get(id, []))
for id, name, art, visc, kg in [('v100-m', 'V100-M', 'EL999201', '2 tot 100 cSt', '0,75 kg'), ('v100-e', 'V100-E', 'EL999202', '32 tot 180 cSt', '0,68 kg'), ('v100-x', 'V100-X', 'EL999203', '46 tot 320 cSt', '0,61 kg')]:
    add(id, 'el-v', name, art, f'Varnish-verwijderaar: absorberende pouch boven een {name[-1]}100-element. Haalt varnish en oxidatieproducten uit turbine- en hydraulische olie.',
        [('Viscositeitsbereik', visc), ('Fijnheid', 'tot 1 µm'), ('Afmetingen', 'Ø179 x 114 mm'), ('Gewicht', kg), ('Max. druk', '5 bar'),
         ('Past in', 'AL100, BU100E, SE100E tot SE600, grotere SE- en OSCA-systemen')],
        fits=['bu100e', 'al100', 'se100e-bh', 'se200e-bh', 'se400e-bh', 'se600e-bh'], page=2,
        confirm=['Datasheet V100: past in alle huizen van 100-formaat; elementenbrochure: niet in SU- en SS-huizen'])
add('we100', 'el-w', 'WE100', 'EL10013', 'Waterabsorberend element: neemt tot 900 ml water op.',
    [('Filtergraad', 'β40 > 50'), ('Waterabsorptie', '900 ml'), ('Filtermedium', 'laag synthetisch vezel'), ('Afmetingen', 'Ø178 x 114 mm'), ('Gewicht', '630 g'),
     ('Debiet', '2,0 l/min'), ('Past in', 'AL100, BU100, SE100')], fits=['al100', 'bu100e', 'se100e-bh'], page=1, old='TR-20450')
add('wg100', 'el-w', 'WG100', 'EL10012', 'Polyester element voor het reinigen van water-glycol, 10 µm.',
    [('Filtergraad', 'β10 > 75'), ('Filtermedium', 'polyester'), ('Afmetingen', 'Ø178 x 114 mm'), ('Gewicht', '680 g'), ('Debiet', '1,0 tot 1,4 l/min'),
     ('Past in', 'alle water-glycolhuizen')], fits=['bu100ew', 'bu200ew', 'bu300ew'], page=1, old='TR-25470')
add('dwg100', 'el-w', 'DWG100', 'EL10017', 'Polyester element voor het reinigen van water-glycol, 5 µm.',
    [('Filtergraad', 'β5 > 75'), ('Filtermedium', 'polyester'), ('Afmetingen', 'Ø178 x 114 mm'), ('Gewicht', '680 g'), ('Debiet', '1,0 tot 1,4 l/min'),
     ('Past in', 'alle water-glycolhuizen')], fits=['bu100ew', 'bu200ew', 'bu300ew'], page=1, old='TR-25480')
add('ws10', 'el-w', 'WS10 waterafscheider', 'EL0410010', 'Coalescentie-element van 1 µm dat water van olie scheidt.',
    [('Fijnheid', '1 µm'), ('Afmetingen', 'Ø68 x 250 mm'), ('Past in', 'WS-WD')], fits=['ws-wd', 'ws-wd-1pf'], page=4, old='TR-20101')
for id, name, art, dim, fit in [('pre-se', 'Aanzuigfilter SE-serie', 'TR-21461', 'Ø35 x 50 mm', 'SE-serie'), ('pre-osca', 'Aanzuigfilter OSCA-serie', 'TR-21200', 'Ø112 x 151 mm', 'OSCA-serie')]:
    add(id, 'el-pre', name, art, 'Wasbaar metalen aanzuigfilter (80/100 µm) dat de pomp beschermt.', [('Fijnheid', '80/100 µm'), ('Afmetingen', dim), ('Past in', fit)], page=4)

add('vulpomp', 'vp', 'Vulpompen', None, 'Vulpompen om olie gefilterd over te pompen en machines te vullen. Modellen en specificaties volgen.',
    [('Toepassing', 'olie overpompen en machines vullen')], fluid=['hyd', 'lube'], version=['mobiel'],
    confirm=['Modellen, artikelnummers, foto en datasheet van de vulpompen aanleveren'])

# ---------------- uitvoer ----------------
ids = {p['id'] for p in P}
for p in P:  # alleen bestaande verwijzingen
    p['elements'] = [e for e in p['elements'] if e in ids]
    p['fits'] = [f for f in p['fits'] if f in ids]
    p['cat'] = SERIES[p['series']]['cat']
    p['pdf'] = SERIES[p['series']]['pdf']
    p['also'] = ['vullen'] if p['id'] == 'se200e-hf' else []
    p['img'] = p['img'] or SERIES[p['series']]['img']
out = dict(cats=[dict(id=c, n=n, s=s) for c, n, s in CATS], fluids=FLUIDS, versions=VERSIONS, series=SERIES, products=P)
json.dump(out, open('data/products.json', 'w'), ensure_ascii=False, indent=1)
open('catalog.js', 'w').write('/* gegenereerd door tools/mkcatalog.py; niet met de hand aanpassen */\nwindow.RRR_CATALOG=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(f'{len(P)} producten in {len(SERIES)} series; catalog.js {len(open("catalog.js").read()) // 1024} KB')
