"""Inhoudsexport voor de AI-assistent Marc: dist/ask-content.json.

Wordt bij elke build aangeroepen vanuit site.py, na het schrijven van alle pagina's.
Bevat de enige bronnen waarop Marc mag antwoorden:
  - alle geïndexeerde webpagina's (NL, EN, FR), opgeknipt per H2-sectie;
  - alle PDF-datasheets per pagina (tekst uit content/pdf-pages.json, zie build/pdf_text.py);
  - de productlijst met vaste product-id's.
Formaat: zie docs/marc-ai-backend-brief.md §4.
"""
import hashlib
import html as H
import json
import os
import re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = 'triple-r-ask-content/1'
from pages import LANGS, PRODUCTS_SLUG as PROD_DIR  # talen en productmap per taal: één centrale plek
# eerste URL-segment -> type
TYPES = {
    'producten': 'product', 'products': 'product', 'produits': 'product',
    'oplossingen': 'solution', 'solutions': 'solution',
    'sectoren': 'sector', 'industries': 'sector', 'secteurs': 'sector',
    'diensten': 'service', 'services': 'service', 'verhuur': 'service', 'rental': 'service', 'location': 'service',
    'gratis-olieanalyse': 'service', 'free-oil-analysis': 'service', 'analyse-huile-gratuite': 'service',
    'filtration-systembuilder': 'tool', 'besparingscalculator': 'tool', 'savings-calculator': 'tool', 'calculateur-economies': 'tool',
    'veelgestelde-vragen': 'faq', 'faq': 'faq', 'questions-frequentes': 'faq',
    'vacatures': 'job', 'careers': 'job', 'emplois': 'job',
}
# niet indexeren: juridisch en formulieren zonder inhoud
SKIP_SEG = {'privacybeleid', 'privacy-policy', 'politique-de-confidentialite', 'cookiebeleid', 'cookie-policy', 'politique-cookies'}
MAX_CHARS = 2400  # ca. 400-600 tokens per stuk


def _h(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:16]


def _text(fragment):
    s = re.sub(r'<(script|style|svg|noscript|form|template|button|select|nav)\b.*?</\1>', ' ', fragment, flags=re.S | re.I)
    s = re.sub(r'<ol class="crumbs".*?</ol>', ' ', s, flags=re.S)  # broodkruimel
    s = re.sub(r'<div class="heroask__lbl">.*?</div></div>', ' ', s, flags=re.S)  # ingebouwd Marc-vak
    s = re.sub(r'<(br|/p|/li|/h[1-6]|/tr|/div|/dt|/dd|/figcaption)\b[^>]*>', '\n', s, flags=re.I)
    s = re.sub(r'<(td|th)\b[^>]*>', ' | ', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = H.unescape(s).replace(' ', ' ').replace('­', '')
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r' *\n[ \n]*', '\n', s)
    return s.strip()


def _split(text):
    if len(text) <= MAX_CHARS:
        return [text]
    out, cur = [], ''
    for para in text.split('\n'):
        if cur and len(cur) + len(para) + 1 > MAX_CHARS:
            out.append(cur)
            cur = ''
        cur = (cur + '\n' + para).strip()
    if cur:
        out.append(cur)
    return out


def _pages(out_dir, product_ids):
    chunks = []
    for lang in LANGS:
        base = os.path.join(out_dir, lang)
        for dirpath, _, files in os.walk(base):
            if 'index.html' not in files:
                continue
            rel = os.path.relpath(dirpath, out_dir).replace(os.sep, '/')
            url = '/' + rel + '/'
            segs = rel.split('/')[1:]
            if segs and segs[0] in SKIP_SEG:
                continue
            if segs and TYPES.get(segs[0]) == 'tool':
                continue  # configurator/calculator: voorbeeldwaarden zouden de AI misleiden
            s = open(os.path.join(dirpath, 'index.html'), encoding='utf-8').read()
            if re.search(r'<meta name="robots" content="[^"]*noindex', s):
                continue
            m = re.search(r'<main\b[^>]*>(.*)</main>', s, re.S)
            if not m:
                continue
            main = m.group(1)
            title = H.unescape(re.sub(r'\s*[–|·-]\s*Triple R.*$', '', re.search(r'<title>(.*?)</title>', s, re.S).group(1))).strip()
            ptype = 'home' if not segs else TYPES.get(segs[0], 'page')
            product = segs[1] if ptype == 'product' and len(segs) > 1 and segs[1] in product_ids else None
            if ptype == 'product' and len(segs) > 1 and not product:
                ptype = 'series'
            # opknippen per H2; de tekst vóór de eerste H2 is de intro
            parts = re.split(r'(?=<h2\b)', main)
            for part in parts:
                hm = re.match(r'<h2\b([^>]*)>(.*?)</h2>', part, re.S)
                anchor, section = '', ''
                if hm:
                    idm = re.search(r'\bid="([^"]+)"', hm.group(1))
                    anchor = '#' + idm.group(1) if idm else ''
                    section = _text(hm.group(2))
                text = _text(part)
                if len(text) < 60:
                    continue
                for i, piece in enumerate(_split(text)):
                    cid = f'{lang}:{rel}:{_h(section or "intro")}' + (f':{i}' if i else '')
                    chunks.append({
                        'id': cid, 'type': ptype, 'lang': lang, 'title': title, 'section': section or None,
                        'url': url, 'anchor': anchor or None, 'page': None, 'product': product,
                        'text': piece, 'hash': _h(piece),
                    })
    return chunks


def _pdfs(products, js_titles):
    import pdf_text
    data = pdf_text.refresh()  # leest nieuwe of gewijzigde PDF's automatisch uit
    by_pdf = {}
    for p in products:
        if p.get('pdf'):
            by_pdf.setdefault(p['pdf'], []).append(p['id'])
    chunks = []
    for f, d in data.items():
        if not os.path.exists(os.path.join(ROOT, 'design', 'pdf', f)):
            continue
        title = js_titles.get(f) or re.sub(r'[-_]+', ' ', f[:-4]).strip()
        for n, txt in enumerate(d['pages'], 1):
            if len(txt) < 40:
                continue
            for i, piece in enumerate(_split(txt)):
                chunks.append({
                    'id': f'pdf:{f}:p{n}' + (f':{i}' if i else ''), 'type': 'pdf', 'lang': 'en', 'title': title, 'section': None,
                    'url': f'/assets/pdf/{f}', 'anchor': f'#page={n}', 'page': n, 'product': None,
                    'products': by_pdf.get(f, []), 'text': piece, 'hash': _h(piece),
                })
    return chunks


def run(out_dir, tr):
    """tr(tekst, taal): de catalogusvertaler van site.py (cat_str)."""
    data = json.load(open(os.path.join(ROOT, 'design', 'data', 'products.json'), encoding='utf-8'))
    cats = {c['id']: c for c in data['cats']}
    series = data['series']
    live = [p for p in data['products'] if not p.get('hidden')]
    ids = {p['id'] for p in live}
    js = open(os.path.join(ROOT, 'design', 'site.js'), encoding='utf-8').read()
    js_titles = dict(re.findall(r"\{ f: '([^']+)', t: '([^']+)'", js))

    def t(s, lang):
        return s if lang == 'nl' or not s else tr(s, lang)

    products = []
    for p in live:
        ser = series.get(p['series'], {})
        cat = cats.get(p.get('cat'), {})
        products.append({
            'id': p['id'],
            'name': p['n'],
            'article_no': p.get('art'),
            'series': p['series'],
            'series_name': {l: t(ser.get('n', ''), l) for l in LANGS},
            'category': p.get('cat'),
            'category_name': {l: t(cat.get('n', ''), l) for l in LANGS},
            'summary': {l: t(p.get('s', ''), l) for l in LANGS},
            'specs': {l: [[t(k, l), t(v, l)] for k, v in p.get('specs', [])] for l in LANGS},
            'url': {l: f'/{l}/{PROD_DIR[l]}/{p["id"]}/' for l in LANGS},
            'image': ('/assets/img/' + re.sub(r'\.(png|jpe?g)$', '.webp', p['img'])) if p.get('img') else None,
            'datasheet': {'url': f'/assets/pdf/{p["pdf"]}', 'page': p.get('page')} if p.get('pdf') else None,
            'fits_elements': p.get('elements') or [],
        })
    chunks = _pages(out_dir, ids) + _pdfs(live, js_titles)
    counts = {'products': len(products), 'chunks': len(chunks)}
    for c in chunks:
        k = c['type'] if c['type'] == 'pdf' else c['lang']
        counts[k] = counts.get(k, 0) + 1
    doc = {
        'schema': SCHEMA,
        'generated': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'site': 'https://www.triple-r-europe.com',
        'note': 'URLs zijn relatief ten opzichte van de site. Antwoord alleen op basis van deze inhoud; beveel alleen producten uit "products" aan (sommige datasheets noemen oudere modellen die niet meer aangeboden worden).',
        'counts': counts,
        'products': products,
        'chunks': chunks,
    }
    path = os.path.join(out_dir, 'ask-content.json')  # buiten /assets: geen cache van een jaar
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(',', ':'))
    return counts, os.path.getsize(path)
