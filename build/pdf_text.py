"""Tekst per pagina uit de PDF's in design/pdf, met cache in content/pdf-pages.json.

De build (ask_export.py) roept refresh() automatisch aan: nieuwe of gewijzigde PDF's worden
uitgelezen als pypdf beschikbaar is (Netlify installeert het via requirements.txt).
Zonder pypdf wordt de bestaande cache gebruikt. Handmatig: python3 build/pdf_text.py
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'design', 'pdf')
CACHE = os.path.join(ROOT, 'content', 'pdf-pages.json')

# PDF's van producten die niet meer aangeboden worden: niet indexeren
SKIP = {'Centrifuges_2014_UK-1.pdf', 'TR-2019-ENGLISH.pdf'}


def clean(t):
    t = t.replace('­', '').replace('\r', '\n')
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return t.strip()


def extract(path):
    import logging
    from pypdf import PdfReader
    logging.getLogger('pypdf').setLevel(logging.ERROR)
    pages = []
    for i, p in enumerate(PdfReader(path).pages, 1):
        try:
            pages.append(clean(p.extract_text() or ''))
        except Exception as e:  # beschadigde pagina: overslaan, niet de hele build stoppen
            print(f'  waarschuwing: {os.path.basename(path)} p.{i}: {e}', file=sys.stderr)
            pages.append('')
    return pages


def refresh(verbose=False):
    """Geeft {bestand: {sha1, pages}} terug; leest alleen nieuwe of gewijzigde PDF's opnieuw uit."""
    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    try:
        import pypdf  # noqa: F401
        can = True
    except ImportError:
        can = False
    out, changed, missing = {}, [], []
    for f in sorted(os.listdir(SRC)):
        if not f.lower().endswith('.pdf') or f in SKIP:
            continue
        sha = hashlib.sha1(open(os.path.join(SRC, f), 'rb').read()).hexdigest()
        if f in cache and cache[f].get('sha1') == sha:
            out[f] = cache[f]
        elif can:
            out[f] = {'sha1': sha, 'pages': extract(os.path.join(SRC, f))}
            changed.append(f)
        elif f in cache:
            out[f] = cache[f]  # verouderde tekst is beter dan geen tekst
            missing.append(f)
        else:
            missing.append(f)
    if changed:
        try:
            with open(CACHE, 'w', encoding='utf-8') as fh:
                json.dump(out, fh, ensure_ascii=False, indent=1)
        except OSError:
            pass
    if verbose or changed or missing:
        print(f'pdf-tekst: {len(out)} PDF\'s' + (f', opnieuw uitgelezen: {", ".join(changed)}' if changed else '')
              + (f'; LET OP zonder pypdf niet (opnieuw) uitgelezen: {", ".join(missing)}' if missing else ''))
    return out


if __name__ == '__main__':
    refresh(verbose=True)
