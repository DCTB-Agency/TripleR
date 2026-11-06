#!/usr/bin/env python3
"""Productiebuild: design/ (NL-bron) + i18n/{en,fr}.json -> dist/ met /nl/, /en/, /fr/.

  python3 build/site.py            staging: X-Robots-Tag noindex via _headers
  SITE_ENV=production ... site.py  productie: geen noindex
"""
import hashlib, html, json, os, re, shutil, sys, urllib.parse
from datetime import date
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'build'))
from pages import LANGS, PAGES, PRODUCTS_SLUG
from kb_meta import KB, SECTION, PARENT
import kb_render as R
D, OUT, I18N = os.path.join(ROOT, 'design'), os.path.join(ROOT, 'dist'), os.path.join(ROOT, 'i18n')
SITE = 'https://www.triple-r-europe.com'
ENV = os.environ.get('SITE_ENV', 'staging')
os.chdir(D)
_g = {'__name__': 'copytool'}
exec(open('copy/copytool.py', encoding='utf-8').read().split('if __name__')[0], _g)
Extract = _g['Extract']
DICT = {l: json.load(open(os.path.join(I18N, l + '.json'), encoding='utf-8')) for l in ('en', 'fr')}
MISSING = {'en': {}, 'fr': {}}
LANG_NAME = {'nl': 'Nederlands', 'en': 'English', 'fr': 'Français'}
TAAL = {'nl': 'Taal', 'en': 'Language', 'fr': 'Langue'}


def tr(text, lang, where='', report=True):
    if lang == 'nl':
        return text
    key = text.strip()
    if not key:
        return text
    v = DICT[lang].get(key)
    if v is None:
        v = DICT[lang].get(re.sub(r'\s+', ' ', key))
    if v is None:
        if report and re.search(r'[a-zà-ÿ]{3}', key):
            MISSING[lang].setdefault(key, where)
        return text
    lead = '' if v[:1].isspace() else text[:len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()):]
    return lead + v + trail


ATTR = re.compile(r'\b(aria-label|placeholder|title|alt|data-on)="([^"$]*)"')
JS_MISS = {'en': {}, 'fr': {}}


def tr_piece(text, lang, where, q):
    """Vertaalt één tekststuk uit een JS-string; code-achtige strings blijven ongemoeid."""
    v = tr(text, lang, where, report=False)
    if v != text:
        return esc_lit(v, q)
    k = text.strip()
    if ' ' in k and re.search(r'[a-zà-ÿ]{3}', k) and not re.search(r'[={};]|=>|\.html|\.pdf|^[.#\[]', k) and lang in JS_MISS:
        JS_MISS[lang].setdefault(k, where)
    return text


def esc_lit(s, q):
    if q == '`':
        return s.replace('\\n', '\x00').replace('`', '\\`').replace('\x00', '\\n')
    return re.sub(r'(?<!\\)' + re.escape(q), lambda m: '\\' + q, s)


def tr_html_text(seg, lang, where, st):
    """Tekst in een template: tags blijven staan (attributen wel vertaald), tekst ertussen wordt vertaald."""
    out, buf, i = [], '', 0
    while i < len(seg):
        c = seg[i]
        if not st['tag'] and c == '<' and i + 1 < len(seg) and (seg[i + 1].isalpha() or seg[i + 1] == '/'):
            out.append(tr_piece(buf, lang, where, '`'))
            buf, st['tag'] = c, True
        elif st['tag'] and c == '>':
            out.append(ATTR.sub(lambda m: f'{m.group(1)}="{tr(m.group(2), lang, where)}"', buf + c))
            buf, st['tag'] = '', False
        else:
            buf += c
        i += 1
    if st['tag']:
        out.append(ATTR.sub(lambda m: f'{m.group(1)}="{tr(m.group(2), lang, where)}"', buf))
    else:
        out.append(tr_piece(buf, lang, where, '`'))
    return ''.join(out)


def scan_template(s, i, lang, where):
    """s[i] is het teken na de openings-backtick. Geeft (vertaald, index na sluit-backtick)."""
    out, seg, st = [], '', {'tag': False}
    while i < len(s):
        c = s[i]
        if c == '\\':
            seg += s[i:i + 2]
            i += 2
        elif c == '`':
            out.append(tr_html_text(seg, lang, where, st))
            return ''.join(out), i + 1
        elif c == '$' and s[i + 1:i + 2] == '{':
            out.append(tr_html_text(seg, lang, where, st))
            seg = ''
            inner, i = scan_code(s, i + 2, lang, where, in_expr=True)
            out.append('${' + inner + '}')
        else:
            seg += c
            i += 1
    raise ValueError('open template in ' + where)


def scan_code(s, i, lang, where, in_expr=False):
    out, depth, prev = [], 0, ''
    n = len(s)
    while i < n:
        c = s[i]
        if c in '\'"':
            j = i + 1
            while s[j] != c:
                if s[j] == '\\':
                    j += 1
                j += 1
            body = s[i + 1:j]
            if '<' in body and '>' in body:
                st = {'tag': False}
                saved = tr_piece
                body = tr_html_text(body, lang, where, st)
                out.append(c + re.sub(r"(?<!\\)" + c, lambda m: '\\' + c, body) if c == "'" else c + body)
                out.append(c)
            else:
                out.append(c + tr_piece(body, lang, where, c) + c)
            i, prev = j + 1, c
        elif c == '`':
            t, i = scan_template(s, i + 1, lang, where)
            out.append('`' + t + '`')
            prev = '`'
        elif s.startswith('//', i):
            j = s.find('\n', i)
            j = n if j < 0 else j
            out.append(s[i:j])
            i = j
        elif s.startswith('/*', i):
            j = s.index('*/', i) + 2
            out.append(s[i:j])
            i = j
        elif c == '/' and (prev in '(,=:[!&|?{};\n' or prev == '' or s[max(0, i - 7):i].rstrip().endswith('return')):
            j, cls = i + 1, False
            while s[j] != '/' or cls:
                if s[j] == '\\':
                    j += 1
                elif s[j] == '[':
                    cls = True
                elif s[j] == ']':
                    cls = False
                j += 1
            out.append(s[i:j + 1])
            i, prev = j + 1, 'r'
        else:
            if in_expr:
                if c == '{':
                    depth += 1
                elif c == '}':
                    if depth == 0:
                        return ''.join(out), i + 1
                    depth -= 1
            out.append(c)
            if not c.isspace():
                prev = c
            i += 1
    return ''.join(out), i


def tr_js(src, lang, where):
    if lang == 'nl':
        return src
    return scan_code(src, 0, lang, where)[0]


def strip_js_comments(src):
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.S)
    return re.sub(r'^\s*//.*$', '', src, flags=re.M)


def tr_file(path, lang):
    s = open(path, encoding='utf-8').read()
    if lang != 'nl':
        p = Extract(s)
        p.feed(s)
        for e in sorted(p.out, key=lambda x: -x['start']):
            if s[e['start']:e['end']] != e['raw']:
                continue
            s = s[:e['start']] + tr(e['raw'], lang, path) + s[e['end']:]
    return re.sub(r'(<script\b[^>]*>)(.*?)(</script>)', lambda m: m.group(1) + tr_js(strip_js_comments(m.group(2)), lang, path) + m.group(3), s, flags=re.S)


def route(page, lang):
    if page in KB:
        i = LANGS.index(lang)
        return f"/{lang}/{SECTION[KB[page]['sec']][i]}/{KB[page]['slug'][i]}/"
    slug = PAGES[page]['slug'][LANGS.index(lang)]
    return f'/{lang}/{slug}/' if slug else f'/{lang}/'


def rewrite_links(s, lang):
    s = re.sub(r'product\.html\?id=\$\{([^}]*)\}', lambda m: f'/{lang}/{PRODUCTS_SLUG[lang]}/${{{m.group(1)}}}/', s)
    s = re.sub(r"'product\.html\?id=' \+ ([\w.]+)", lambda m: f"'/{lang}/{PRODUCTS_SLUG[lang]}/' + {m.group(1)} + '/'", s)
    SER = {'bu': 'p-bu', 'se': 'p-se', 'osca': 'p-osca', 'tr': 'p-tr', 'ss': 'p-ss', 'ws': 'p-ws', 'quicktoron': 'p-qt', 'vacuum': 'p-vac', 'centrifuges': 'p-cen'}
    s = re.sub(r'(?<![\w/.-])producten\.html\?serie=(\w+)(?=["\'`])', lambda m: route(SER[m.group(1)], lang) if m.group(1) in SER else m.group(0), s)
    s = re.sub(r'(?<![\w/.-])producten\.html\?cat=elementen(?=["\'`])', lambda m: route('p-el', lang), s)
    names = '|'.join(re.escape(p) for p in list(PAGES) + list(KB))
    s = re.sub(rf'(?<![\w/.-])({names})\.html', lambda m: route(m.group(1), lang), s)
    s = re.sub(r'(?<![\w/.-])product\.html', f'/{lang}/{PRODUCTS_SLUG[lang]}/', s)
    return s


def assets(s, lang, ver):
    s = re.sub(r'''(["'`(])(img|media|pdf|vendor|fonts)/''', r'\1/assets/\2/', s)
    s = re.sub(r'"(tokens\.css|site\.css)"', lambda m: f'"/assets/{m.group(1)}?v={ver[m.group(1)]}"', s)
    if 'site.' + lang in ver:
        s = s.replace('"site.js"', f'"/assets/site.{lang}.js?v={ver["site." + lang]}"').replace('"catalog.js"', f'"/assets/catalog.{lang}.js?v={ver["catalog." + lang]}"')
    return s


def optimise(s):
    """WebP overal behalve in OG-tags; afbeeldingen lazy behalve de eerste; video start pas na het laden."""
    s = re.sub(r'(?<!\.com)(/assets/img/[\w/.-]+?)\.(png|jpe?g)', r'\1.webp', s)
    n = [0]

    def lazy(m):
        tag = m.group(0)
        n[0] += 1
        if 'loading=' in tag or 'width="0"' in tag:
            return tag
        if n[0] <= 2 or 'marc-pose' in tag:
            return tag.replace('<img ', '<img fetchpriority="high" decoding="async" ', 1) if 'marc-pose' in tag else tag
        return tag.replace('<img ', '<img loading="lazy" decoding="async" ', 1)
    return re.sub(r'<img\b[^>]*>', lazy, s)


def clean(s):
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s = re.sub(r'\sdata-annot="[^"]*"', '', s, flags=re.S)
    return re.sub(r'<i class="tb"[^>]*>\s*</i>', '', s)


def lang_links(alts, lang):
    hdr = ''.join(f'<a href="{alts[l]}" lang="{l}" hreflang="{l}">{LANG_NAME[l]}</a>' for l in LANGS if l != lang)
    header = f'<details class="langsw"><summary aria-label="{TAAL[lang]}: {LANG_NAME[lang]}">{lang.upper()}</summary><nav aria-label="{TAAL[lang]}">{hdr}</nav></details>'
    footer = ''.join(f'<a href="{alts[l]}" lang="{l}" hreflang="{l}"' + (' aria-current="true"' if l == lang else '') + f'>{l.upper()}</a>' for l in LANGS)
    return header, footer


ORG = {'@type': 'Corporation', '@id': SITE + '/#organization', 'name': 'Triple R Europe', 'legalName': 'Triple R Europe nv', 'url': SITE + '/', 'logo': SITE + '/assets/logo-color.svg',
       'vatID': 'BE0448276293', 'telephone': '+3238254647', 'email': 'info@triple-r-europe.com', 'areaServed': 'Europe', 'sameAs': ['https://www.linkedin.com/company/10456623/'],
       'address': {'@type': 'PostalAddress', 'streetAddress': 'Cleydaellaan 16, unit 8', 'postalCode': '2630', 'addressLocality': 'Aartselaar', 'addressCountry': 'BE'},
       'contactPoint': {'@type': 'ContactPoint', 'telephone': '+3238254647', 'contactType': 'sales', 'availableLanguage': ['nl', 'en', 'fr']}}


def jsonld(lang, url, crumbs, extra=None):
    g = [ORG, {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Triple R Europe', 'inLanguage': lang, 'publisher': {'@id': ORG['@id']}}]
    if crumbs:
        g.append({'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate(crumbs)]})
    if extra:
        g.append(extra)
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': g}, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def head(lang, title, desc, alts, ld, noindex=False, img='/assets/img/industry.jpg'):
    e = html.escape
    url = SITE + alts[lang]
    links = ''.join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{alts[l]}">\n' for l in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{alts["en"]}">\n'
    r = '<meta name="robots" content="noindex">\n' if noindex else ''
    return (f'<!doctype html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<title>{e(title, False)}</title>\n<meta name="description" content="{e(desc)}">\n{r}<link rel="canonical" href="{url}">\n{links}'
            f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="Triple R Europe">\n<meta property="og:title" content="{e(title)}">\n<meta property="og:description" content="{e(desc)}">\n'
            f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{SITE}{img}">\n<meta property="og:locale" content="{ {"nl": "nl_BE", "en": "en_GB", "fr": "fr_BE"}[lang]}">\n<meta name="twitter:card" content="summary_large_image">\n'
            f'<link rel="icon" href="/assets/logo-color.svg" type="image/svg+xml">\n{ld}\n')


def dealers(lang):
    """Distributeursdata per taal, zonder interne bronnotities."""
    d = json.load(open('partials/dealers.json', encoding='utf-8'))
    d.pop('_bron', None)
    for r in d['europe']:
        r.pop('bron', None)
        r['country'] = tr(r['country'], lang, 'dealers')
    d['world'] = {tr(k, lang, 'dealers'): [tr(x, lang, 'dealers') for x in v] for k, v in d['world'].items()}
    return json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def faq_ld(body):
    qs = re.findall(r'<details>\s*<summary>(.*?)</summary>(.*?)</details>', body, re.S)
    strip = lambda x: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x)).strip()
    return {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': strip(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in qs]} if qs else None


def build_page(name, lang, ver, parts, alts, title, desc, crumbs, noindex=False, inject='', extra_ld=None, img='/assets/img/industry.jpg', out=None, blocks=None, h1=None):
    src = tr_file(f'{name}.src.html', lang)
    src = src.replace('{{HEADER}}', parts[lang]['header']).replace('{{FOOTER}}', parts[lang]['footer'])
    if '{{EUROPE_MAP}}' in src:
        src = src.replace('{{EUROPE_MAP}}', open('partials/europe-map.svg', encoding='utf-8').read()).replace('{{DEALERS}}', dealers(lang))
    for k, v in LOGOS.items():
        src = src.replace(k, v)
    for k, v in (blocks or {}).items():
        src = src.replace(k, v)
    hl, fl = lang_links(alts, lang)
    src = src.replace('{{LANGS_HEADER}}', hl).replace('{{LANGS_FOOTER}}', fl)
    src = re.sub(r'<title>.*?</title>\n', '', src, count=1, flags=re.S)
    src = re.sub(r'<meta name="description"[^>]*>\n', '', src, count=1)
    i = src.index('</style>') + len('</style>') if '</style>' in src else 0
    headpart, body = src[:i], src[i:]
    ld = jsonld(lang, alts[lang], crumbs, extra_ld or (faq_ld(body) if name == 'faq' else None))
    page = head(lang, title, desc, alts, ld, noindex, img) + headpart + '\n' + inject + '</head>\n<body>\n' + body + '\n</body>\n</html>\n'
    if h1:  # model: naam, omschrijving en specificaties staan in de HTML, JS verrijkt ze daarna
        page = page.replace('<h1 id="h1">Product</h1>', f'<h1 id="h1">{R.e(h1[0])}</h1>').replace('<p class="lead" id="lead"></p>', f'<p class="lead" id="lead">{R.e(h1[1])}</p>').replace('<div class="wrap" id="spec"></div>', f'<div class="wrap prose" id="spec">{h1[2]}</div>')
    if lang != 'nl':
        page = ATTR.sub(lambda m: f'{m.group(1)}="{tr(m.group(2), lang, name, report=False)}"', page)
    page = clean(rewrite_links(page, lang))
    page = re.sub(r',?\s*"note":\s*"[^"]*geen marker[^"]*"', '', page)
    page = assets(page, lang, ver)
    page = optimise(page)
    path = out or os.path.join(OUT, alts[lang].strip('/'), 'index.html')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(page)


# ---- catalogus per taal
NUM = {
    'en': [(r'(\d),(\d)', r'\1.\2'), (r'(\d)\.(\d{3})\b', r'\1,\2'), (r' tot ', ' to '), (r'\btpm\b', 'rpm'), (r'-formaat', ' size'), (r'\bhoogte\b', 'height'), (r'\(gegarandeerd debiet\)', '(guaranteed flow)'), (r'\(standaard\)', '(standard)'), (r'\(waterbasis; bij olie 50%\)', '(water-based; 50% with oil)'), (r'verschillende fijnheden', 'various grades'), (r'" in en uit', '" in and out'), (r'\buit\b', 'out'), (r'\bca,', 'approx.')],
    'fr': [(r'(\d)\.(\d{3})\b', '\\1\u00a0\\2'), (r' tot ', ' à '), (r'\btpm\b', 'tr/min'), (r'(\d+)-formaat', r'format \1'), (r'\bhoogte\b', 'hauteur'), (r'\(gegarandeerd debiet\)', '(débit garanti)'), (r'\(standaard\)', '(standard)'), (r'\(waterbasis; bij olie 50%\)', '(base eau ; 50 % avec huile)'), (r'verschillende fijnheden', 'diverses finesses'), (r'" in en uit', '" entrée et sortie'), (r'" in\b', '" entrée'), (r'\buit\b', 'sortie'), (r'\bca,', 'env.')],
}


def cat_str(s, lang):
    if lang == 'nl':
        return s
    v = DICT[lang].get(s.strip())
    if v is not None:
        return v
    r = s
    for a, b in NUM[lang]:
        r = re.sub(a, b, r)
    if r == s and re.search(r'[a-zà-ÿ]{4}', s) and not re.match(r'^[A-Z0-9/ .-]+$', s):
        MISSING[lang].setdefault(s, 'catalog')
    return r


SKIP_KEYS = {'id', 'img', 'pdf', 'series', 'art', 'old', 'cat', 'fluid', 'version', 'elements', 'fits', 'also', 'vol', 'volGrey', 'flow', 'page', 'hidden'}


def walk(x, lang, key=None):
    if isinstance(x, str):
        return cat_str(x, lang)
    if isinstance(x, list):
        return [walk(i, lang, key) for i in x]
    if isinstance(x, dict):
        return {k: ([] if k == 'confirm' else walk(v, lang, k) if isinstance(v, dict) and k == 'series' else v if k in SKIP_KEYS else walk(v, lang, k)) for k, v in x.items()}
    return x


def catalog(lang):
    d = json.load(open('data/products.json', encoding='utf-8'))
    t = walk(d, lang)
    return t, '/* gegenereerd door build/site.py */\nwindow.RRR_CATALOG=' + json.dumps(t, ensure_ascii=False, separators=(',', ':')) + ';\n'


CRUMB = {'oplossingen': {'nl': 'Oplossingen', 'en': 'Solutions', 'fr': 'Solutions'}, 'sectoren': {'nl': 'Sectoren', 'en': 'Industries', 'fr': 'Secteurs'}, 'producten': {'nl': 'Producten', 'en': 'Products', 'fr': 'Produits'}}


def kb_links(l):
    t = R.T[l]
    items = ''.join(f'<li><a href="{route(k, l)}">{R.e(m[l][0])}</a></li>' for k, m in KB.items() if m['sec'] == 'opl')
    return f'<section class="sec"><div class="wrap prose"><h2>{t["topics"]}</h2><p>{t["topics_s"]}</p><ul>{items}</ul></div></section>'


def all_models(cat, l):
    t = R.T[l]
    out = []
    for sid, s in cat['series'].items():
        ps = [p for p in cat['products'] if p.get('series') == sid and not p.get('hidden')]
        if ps:
            out.append(f'<h3>{R.e(s["n"])}</h3><ul>' + ''.join(f'<li><a href="/{l}/{PRODUCTS_SLUG[l]}/{p["id"]}/">{R.e(p["n"])}</a></li>' for p in ps) + '</ul>')
    return f'<section class="sec" id="alle-modellen"><div class="wrap prose"><h2>{t["all"]}</h2><p>{t["all_s"]}</p>{"".join(out)}</div></section>'


def llms(kb, cats):
    head = {'nl': '## Nederlands', 'en': '## English', 'fr': '## Français'}
    intro = {'nl': 'Triple R Europe nv (Aartselaar, België) levert bypass-oliefiltratie voor de industrie: filterelementen van 114 mm die vaste deeltjes, varnish en water uit hydraulische olie en smeerolie verwijderen, in systemen van compacte bypassfilters tot mobiele oliereinigers, vacuümdrogers en centrifuges.',
             'en': 'Triple R Europe nv (Aartselaar, Belgium) supplies bypass oil filtration for industry: 114 mm filter elements that remove solid particles, varnish and water from hydraulic and lubricating oil, in systems ranging from compact bypass filters to mobile oil cleaners, vacuum dehydrators and centrifuges.',
             'fr': 'Triple R Europe nv (Aartselaar, Belgique) fournit la filtration d\'huile en dérivation pour l\'industrie : éléments filtrants de 114 mm qui éliminent particules solides, vernis et eau des huiles hydrauliques et de lubrification, dans des systèmes allant du filtre compact à l\'épurateur mobile, au déshydrateur sous vide et à la centrifugeuse.'}
    a = ['# Triple R Europe', '', '> Industrial bypass oil filtration. Head office: Cleydaellaan 16, unit 8, 2630 Aartselaar, Belgium. +32 3 825 46 47, info@triple-r-europe.com.', '']
    f = list(a)
    for l in LANGS:
        a += [head[l], '', intro[l], '']
        f += [head[l], '', intro[l], '']
        for k in ('homepage', 'producten', 'oplossingen', 'sectoren', 'olieanalyse', 'faq', 'contact'):
            a.append(f'- [{PAGES[k][l][0]}]({SITE}{route(k, l)})')
        for k, m in KB.items():
            a.append(f'- [{m[l][0]}]({SITE}{route(k, l)}): {m[l][2]}')
            if m['sec'] == 'opl':
                f += [f'### {m[l][0]}', '', f'URL: {SITE}{route(k, l)}', '', m[l][3], '']
                for t, x in kb[k][l]:
                    f.append(('#### ' if t in ('h2', 'h3', 'h4') else '- ' if t == 'li' else '') + x)
                f.append('')
        a.append('')
    open(os.path.join(OUT, 'llms.txt'), 'w', encoding='utf-8').write('\n'.join(a))
    open(os.path.join(OUT, 'llms-full.txt'), 'w', encoding='utf-8').write('\n'.join(f))


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    A = os.path.join(OUT, 'assets')
    os.makedirs(A)
    for d in ('img', 'media', 'pdf', 'fonts', 'vendor'):
        shutil.copytree(d, os.path.join(A, d))
    for f in ('tokens.css', 'site.css', 'logo-color.svg', 'logo-white.svg'):
        shutil.copy(f, A)
    css = open(os.path.join(A, 'site.css'), encoding='utf-8').read()
    open(os.path.join(A, 'site.css'), 'w', encoding='utf-8').write(re.sub(r'(img/[\w/.-]+?)\.(png|jpe?g)', r'\1.webp', css))
    ver = {f: hashlib.md5(open(f, 'rb').read()).hexdigest()[:8] for f in ('tokens.css', 'site.css')}
    cats = {}
    for l in LANGS:
        js = open('site.js', encoding='utf-8').read()
        js = assets(rewrite_links(tr_js(strip_js_comments(js), l, 'site.js'), l), l, ver)
        js = re.sub(r'(/assets/img/[\w/.-]+?)\.(png|jpe?g)', r'\1.webp', js)
        open(os.path.join(A, f'site.{l}.js'), 'w', encoding='utf-8').write(js)
        ver['site.' + l] = hashlib.md5(js.encode()).hexdigest()[:8]
        cats[l], c = catalog(l)
        c = re.sub(r'"img":"([\w.-]+?)\.(png|jpe?g)"', r'"img":"\1.webp"', c)
        open(os.path.join(A, f'catalog.{l}.js'), 'w', encoding='utf-8').write(c)
        ver['catalog.' + l] = hashlib.md5(c.encode()).hexdigest()[:8]
    global LOGOS
    color, white = open('logo-color.clean.svg').read(), open('logo-white.clean.svg').read()
    reid = lambda s, o, n: re.sub(r'(id="|url\(#)' + o, lambda m: m.group(1) + n, s)
    LOGOS = {'{{LOGO_REV}}': reid(color.replace('fill: #1d1d1b', 'fill: #fff'), 'lc', 'lr'), '{{LOGO_WHITE_D}}': reid(white, 'lw', 'wd').replace('aria-label="Triple R"', 'aria-hidden="true"'),
             '{{LOGO_WHITE_F}}': reid(white, 'lw', 'wf'), '{{LOGO_WHITE_H}}': reid(white, 'lw', 'wh'), '{{LOGO_COLOR_D}}': reid(color, 'lc', 'ld').replace('aria-label="Triple R"', 'aria-hidden="true"'), '{{LOGO_COLOR}}': color}
    parts = {l: {'header': tr_file('partials/header.html', l), 'footer': tr_file('partials/footer.html', l)} for l in LANGS}
    urls = []
    HOME = {'nl': 'Home', 'en': 'Home', 'fr': 'Accueil'}
    for name, p in PAGES.items():
        alts = {l: route(name, l) for l in LANGS}
        for l in LANGS:
            title, desc = p[l]
            crumbs = [(HOME[l], f'/{l}/')] + ([] if name == 'homepage' else [(title.split(' – ')[0].split(':')[0], alts[l])])
            prod_url = lambda x: f"/{l}/{PRODUCTS_SLUG[l]}/{x['id']}/"
            blocks = {'{{KB_LINKS}}': kb_links(l), '{{ALL_MODELS}}': all_models(cats[l], l)}
            build_page(name, l, ver, parts, alts, title, desc, crumbs, blocks=blocks)
        urls.append((alts, p['prio']))
    # inhoudspagina's
    kb_data = json.load(open(os.path.join(ROOT, 'content', 'kb.json'), encoding='utf-8'))
    for key, m in KB.items():
        alts = {l: route(key, l) for l in LANGS}
        for l in LANGS:
            data = m[l]
            h1, title, desc = data[:3]
            blocks_ = kb_data[key][l]
            if len(data) > 3:
                lead, skip = data[3], 0
            else:
                lead, skip = R.lead_from(blocks_)
                rest = []
                n = skip
                for b in blocks_:
                    if n and b[0] == 'p':
                        n -= 1
                        continue
                    rest.append(b)
                blocks_ = rest
            parent = PARENT[m['sec']]
            ptitle = PAGES[parent][l][0].split(' – ')[0].split(':')[0]
            crumbs = [(HOME[l], f'/{l}/'), (CRUMB[parent][l], route(parent, l)), (h1, alts[l])]
            t = R.T[l]
            prods = [p for p in cats[l]['products'] if p.get('series') in m.get('serie', []) and not p.get('hidden')]
            models = R.models_table(prods, l, lambda x: f"/{l}/{PRODUCTS_SLUG[l]}/{x['id']}/") if prods else ''
            sib = [k for k, v in KB.items() if v['sec'] == m['sec'] and k != key]
            i = list(KB).index(key)
            sib = sorted(sib, key=lambda k: (list(KB).index(k) - i) % len(KB))[:4]
            rel = ''.join(f'<li><a href="{route(k, l)}">{R.e(KB[k][l][0])}</a></li>' for k in sib)
            html_body = f'''<section class="hero hero--page" aria-labelledby="h1"><div class="hero__bg" aria-hidden="true"></div><div class="wrap"><div class="hero__copy" style="gap:0">
<ol class="crumbs" aria-label="Kruimelpad"><li><a href="{route('homepage', l)}">{HOME[l]}</a></li><li><a href="{route(parent, l)}">{CRUMB[parent][l]}</a></li><li aria-current="page">{R.e(h1)}</li></ol>
<h1 id="h1">{R.e(h1)}</h1><p class="lead">{R.e(lead)}</p></div></div></section>
<section class="sec"><div class="wrap prose">{models if m['sec'] == 'pro' else ''}{R.body(blocks_)}
<p style="margin-top:var(--s-6);font-size:13px;color:var(--grey-600)">{t['upd']}: <time datetime="{date.today().isoformat()}">{t['date']}</time> · {R.e(t['by'])}</p>
<h2>{t['rel']}</h2><ul>{rel}</ul></div></section>''' + R.cta(l)
            ld = {'@type': 'TechArticle' if m['sec'] == 'opl' else 'WebPage', 'headline': h1, 'name': h1, 'description': desc, 'inLanguage': l, 'url': SITE + alts[l], 'dateModified': date.today().isoformat(), 'publisher': {'@id': ORG['@id']}, 'author': {'@id': ORG['@id']}}
            build_page('kb', l, ver, parts, alts, title, desc, crumbs, extra_ld=ld, blocks={'{{KB}}': html_body})
        urls.append((alts, '0.8'))
    llms(kb_data, cats)
    # productpagina's per model
    base = CRUMB['producten']
    for prod in cats['nl']['products']:
        if prod.get('hidden'):
            continue
        pid = prod['id']
        alts = {l: f'/{l}/{PRODUCTS_SLUG[l]}/{pid}/' for l in LANGS}
        for l in LANGS:
            pr = next(x for x in cats[l]['products'] if x['id'] == pid)
            title = f"{pr['n']} – Triple R"
            desc = pr['s'][:152]
            crumbs = [(HOME[l], f'/{l}/'), (base[l], route('producten', l)), (pr['n'], alts[l])]
            img = '/assets/img/' + pr['img'] if pr.get('img') and os.path.exists('img/' + pr['img']) else '/assets/img/industry.jpg'
            ld = {'@type': 'Product', 'name': pr['n'], 'description': pr['s'], 'brand': {'@type': 'Brand', 'name': 'Triple R'}, 'image': SITE + img}
            if pr.get('art'):
                ld['sku'] = pr['art']
            build_page('product', l, ver, parts, alts, title, desc, crumbs, inject=f'<script>window.RRR_PID={json.dumps(pid)};</script>\n', extra_ld=ld, img=img, h1=(pr['n'], pr['s'], R.spec_table(pr, l)))
        urls.append((alts, '0.6'))
    # 404 per taal
    T404 = {'nl': ('Pagina niet gevonden – Triple R', 'Deze pagina bestaat niet meer. Bekijk onze producten of neem contact op.'), 'en': ('Page not found – Triple R', 'This page no longer exists. Browse our products or get in touch.'), 'fr': ('Page introuvable – Triple R', 'Cette page n\'existe plus. Consultez nos produits ou contactez-nous.')}
    alts = {l: f'/{l}/' for l in LANGS}
    for l in LANGS:
        build_page('404', l, ver, parts, alts, *T404[l], [], noindex=True, out=os.path.join(OUT, f'{l}/404.html'))
    shutil.copy(os.path.join(OUT, 'nl/404.html'), os.path.join(OUT, '404.html'))
    # sitemap, robots, llms
    today = date.today().isoformat()
    x = ['<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for alts, prio in urls:
        links = ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{alts[l]}"/>' for l in LANGS) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{alts["en"]}"/>'
        for l in LANGS:
            x.append(f'<url><loc>{SITE}{alts[l]}</loc>{links}<lastmod>{today}</lastmod><priority>{prio}</priority></url>')
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(x) + '\n</urlset>\n')
    bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'PerplexityBot', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'Google-Extended', 'Googlebot', 'Bingbot', 'Applebot', 'Applebot-Extended', 'DuckAssistBot', 'meta-externalagent']
    open(os.path.join(OUT, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n\n' + ''.join(f'User-agent: {b}\nAllow: /\n\n' for b in bots) + f'Sitemap: {SITE}/sitemap.xml\n')
    # headers en redirects
    csp = "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com https://www.googletagmanager.com; font-src 'self'; connect-src 'self' https://www.google-analytics.com https://*.analytics.google.com https://*.google-analytics.com; worker-src 'self' blob:; frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
    h = ['/*', '  X-Content-Type-Options: nosniff', '  Referrer-Policy: strict-origin-when-cross-origin', '  Permissions-Policy: camera=(), microphone=(), geolocation=()', '  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload', f'  Content-Security-Policy: {csp}']
    if ENV != 'production':
        h.append('  X-Robots-Tag: noindex, nofollow')
    h += ['/assets/*', '  Cache-Control: public, max-age=31536000, immutable']
    open(os.path.join(OUT, '_headers'), 'w').write('\n'.join(h) + '\n')
    shutil.copy(os.path.join(ROOT, 'build', '_redirects'), os.path.join(OUT, '_redirects'))
    json.dump({'html': MISSING, 'js': JS_MISS}, open(os.path.join(ROOT, 'build', '.missing.json'), 'w'), ensure_ascii=False, indent=0)
    print('pagina\'s:', sum(1 for _ in os.walk(OUT) for f in _[2] if f.endswith('.html')), '| niet vertaald EN', len(MISSING['en']), 'FR', len(MISSING['fr']))


if __name__ == '__main__':
    main()
