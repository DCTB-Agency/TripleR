#!/usr/bin/env python3
"""Controleert dist/: SEO-basis, links, redirects, taal, derden. Exit 1 bij fouten."""
import glob, json, os, re, sys, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dist')
errs, warns = [], []
files = [f for f in glob.glob(OUT + '/**/*.html', recursive=True)]
paths = set()
for f in files:
    rel = f[len(OUT):]
    paths.add(rel[:-len('index.html')] if rel.endswith('index.html') else rel)
NLW = re.compile(r'\b(uw|voor de|het|een|niet|olie|wordt|bij|deze|zijn|naar|onze|hoe|wij)\b', re.I)
strip = lambda s: re.sub(r'<(script|style|svg)\b.*?</\1>', ' ', s, flags=re.S)
seen_t = {}
for f in files:
    rel = f[len(OUT):]
    s = open(f, encoding='utf-8').read()
    is404 = rel.endswith('404.html')
    h = strip(s)
    n = len(re.findall(r'<h1\b', h))
    if n != 1: errs.append(f'{rel}: {n} H1')
    t = re.search(r'<title>(.*?)</title>', s, re.S).group(1).replace('&amp;', '&')
    d = re.search(r'<meta name="description" content="([^"]*)"', s).group(1).replace('&#x27;', "'").replace('&amp;', '&').replace('&quot;', '"')
    if len(t) > 60: errs.append(f'{rel}: titel {len(t)} tekens: {t}')
    if len(d) > 155: errs.append(f'{rel}: description {len(d)} tekens')
    if not is404:
        seen_t.setdefault(t, []).append(rel)
        if '<link rel="canonical"' not in s: errs.append(f'{rel}: geen canonical')
        if len(re.findall(r'hreflang="(nl|en|fr|x-default)" href', s)) != 4: errs.append(f'{rel}: hreflang onvolledig')
        if 'application/ld+json' not in s: errs.append(f'{rel}: geen JSON-LD')
        if 'noindex' in s: errs.append(f'{rel}: noindex in HTML')
        if 'class="crumbs"' not in s and rel.count('/') > 2: warns.append(f'{rel}: geen broodkruimel')
    for b in ('fonts.googleapis', 'fonts.gstatic', 'cdnjs.cloudflare', '[X]', 'Prototype', 'Designvoorstel', '[CONFIRM]', 'data-annot', '{{'):
        if b in s: errs.append(f'{rel}: bevat {b}')
    m = re.match(r'/(nl|en|fr)/', rel)
    if m and m.group(1) != 'nl':
        txt = re.sub(r'<[^>]+>', ' ', h)
        txt = re.sub(r'\s+', ' ', txt)
        hits = [x for x in re.findall(r'[^.!?]{0,40}\b(?:uw|voor de|wordt|niet|onze|deze)\b[^.!?]{0,40}', txt) if not re.search(r'[éèàç]', x)]
        if hits: errs.append(f'{rel}: NL-tekst? {hits[0].strip()[:70]}')
        for w in ('Verenigd Koninkrijk', 'Oostenrijk', 'Zwitserland', 'nl-BE'):
            if w in s: errs.append(f'{rel}: bevat {w}')
    for href in re.findall(r'href="([^"]*)"', h):
        if href == '#' and 'data-cookie-settings' not in h: errs.append(f'{rel}: href=#')
        if href.startswith('/') and not href.startswith('//'):
            p = urllib.parse.unquote(href.split('#')[0].split('?')[0])
            if p.startswith('/assets/'):
                if not os.path.exists(OUT + p): errs.append(f'{rel}: ontbrekend {p}')
            elif p not in paths and p + '/' not in paths and p != '/': errs.append(f'{rel}: dode link {p}')
        elif re.search(r'\.html($|[?#])', href) and not href.startswith('http'): errs.append(f'{rel}: oude link {href}')
for t, r in seen_t.items():
    if len(r) > 3: warns.append(f'dubbele titel ({len(r)}×): {t}')
# redirects
rd = [l.split() for l in open(OUT + '/_redirects') if l.strip() and not l.startswith('#')]
for parts in rd:
    o, t = parts[0], parts[1]
    if o.startswith('/wp-content/uploads/*') or t.startswith('/.netlify') or t.endswith('404.html'): continue
    p = urllib.parse.unquote(t.split('?')[0].split('#')[0])
    if p.startswith('/assets/'):
        if not os.path.exists(OUT + p): errs.append(f'redirect {o} -> {t}: bestaat niet')
    elif p not in paths: errs.append(f'redirect {o} -> {t}: bestaat niet')
oldc = [u.strip() for u in open(os.path.join(ROOT, 'docs/migratie/oude-urls.txt'))]
have = {urllib.parse.unquote(l[0]) for l in rd}
miss = [u for u in oldc if urllib.parse.urlparse(u).path not in have and urllib.parse.urlparse(u).path != '/']
if miss: errs.append(f'{len(miss)} oude URL\'s zonder redirect, bv. {miss[0]}')
# JS: geen derden behalve GTM ná toestemming
for j in glob.glob(OUT + '/assets/site.*.js'):
    s = open(j, encoding='utf-8').read()
    ext = set(re.findall(r'https?://[a-z0-9.-]+', s)) - {'https://www.googletagmanager.com', 'http://www.w3.org'}
    if ext: warns.append(f'{os.path.basename(j)}: externe adressen {ext}')
for j in ('en', 'fr'):
    s = open(f'{OUT}/assets/site.{j}.js', encoding='utf-8').read()
    for w in ('Bedankt', 'Vul uw', 'Offerteaanvraag', 'Verzenden is niet'):
        if w in s: errs.append(f'site.{j}.js bevat "{w}"')
# alle JavaScript moet parsen
import subprocess, tempfile
for j in glob.glob(OUT + '/assets/*.js'):
    r = subprocess.run(['node', '--check', j], capture_output=True, text=True)
    if r.returncode: errs.append(f'{os.path.basename(j)}: syntaxfout {r.stderr[:200]}')
done = set()
for f in files:
    for m in re.findall(r'<script(?![^>]*src=)(?![^>]*ld\+json)[^>]*>(.*?)</script>', open(f, encoding='utf-8').read(), re.S):
        h_ = hash(m)
        if h_ in done or 'RRR_PID' in m: continue
        done.add(h_)
        with tempfile.NamedTemporaryFile('w', suffix='.mjs', delete=False) as t: t.write(m)
        r = subprocess.run(['node', '--check', t.name], capture_output=True, text=True)
        os.unlink(t.name)
        if r.returncode: errs.append(f'{f[len(OUT):]}: script-syntaxfout {r.stderr[:160]}')
print(f'{len(files)} pagina\'s, {len(rd)} redirects')
for w in sorted(set(warns))[:12]: print('LET OP', w)
for e in errs[:60]: print('FOUT', e)
print(f'{len(errs)} fouten, {len(warns)} waarschuwingen')
sys.exit(1 if errs else 0)
