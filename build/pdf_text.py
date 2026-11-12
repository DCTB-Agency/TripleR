"""Haalt de tekst per pagina uit de PDF's in design/pdf en bewaart die in content/pdf-pages.json.

Lokaal draaien wanneer er een PDF bijkomt of wijzigt (Netlify heeft geen pypdf):
    pip install pypdf && python3 build/pdf_text.py
De build (build/ask_export.py) leest daarna alleen het JSON-bestand.
"""
import hashlib
import json
import os
import re
import sys

from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'design', 'pdf')
OUT = os.path.join(ROOT, 'content', 'pdf-pages.json')

# PDF's van producten die niet meer aangeboden worden: niet indexeren
SKIP = {'Centrifuges_2014_UK-1.pdf', 'TR-2019-ENGLISH.pdf'}


def clean(t):
    t = t.replace('­', '').replace('\r', '\n')
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return t.strip()


def main():
    out = {}
    for f in sorted(os.listdir(SRC)):
        if not f.lower().endswith('.pdf') or f in SKIP:
            continue
        path = os.path.join(SRC, f)
        data = open(path, 'rb').read()
        r = PdfReader(path)
        pages = []
        for i, p in enumerate(r.pages, 1):
            try:
                txt = clean(p.extract_text() or '')
            except Exception as e:  # beschadigde pagina: overslaan, niet de hele build stoppen
                print(f'  waarschuwing: {f} p.{i}: {e}', file=sys.stderr)
                txt = ''
            pages.append(txt)
        out[f] = {'sha1': hashlib.sha1(data).hexdigest(), 'pages': pages}
        empty = sum(1 for t in pages if len(t) < 20)
        print(f'{f}: {len(pages)} pagina\'s' + (f' ({empty} zonder tekst, mogelijk scan)' if empty else ''))
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f'-> {os.path.relpath(OUT, ROOT)}')


if __name__ == '__main__':
    main()
