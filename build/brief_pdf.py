"""Maakt de PDF van de briefing voor Kigumi uit docs/marc-ai-backend-brief.md, in de huisstijl van Triple R.

Vereist: pip install markdown, en Google Chrome (headless).
    python3 build/brief_pdf.py   -> docs/Triple-R-Marc-AI-briefing-Kigumi-v<versie>.pdf
"""
import glob
import os
import re
import subprocess
import sys
import tempfile

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
FONTS = os.path.join(ROOT, 'design', 'fonts') + '/'
CSS = f'''
@font-face{{font-family:Geist;src:url("file://{FONTS}geist-latin-wght-normal.woff2") format("woff2");font-weight:100 900}}
@font-face{{font-family:Geist;src:url("file://{FONTS}geist-latin-ext-wght-normal.woff2") format("woff2");font-weight:100 900;unicode-range:U+0100-024F,U+2000-206F,U+20AC}}
@font-face{{font-family:"Geist Mono";src:url("file://{FONTS}geist-mono-latin-wght-normal.woff2") format("woff2");font-weight:100 900}}
@page{{size:A4;margin:18mm 17mm 20mm}}
html{{font-family:Geist,"Helvetica Neue",Arial,sans-serif;color:#1D1D1B;font-size:10pt;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.cover{{border-bottom:3px solid #0086CD;padding-bottom:12mm;margin-bottom:8mm}}
.cover svg{{height:15mm;width:auto;display:block;margin-bottom:12mm}}
.kick{{text-transform:uppercase;letter-spacing:.12em;font-size:8pt;color:#006BA6;font-weight:600;margin:0 0 3mm}}
h1{{font-size:24pt;line-height:1.12;letter-spacing:-.02em;margin:0 0 6mm;font-weight:700}}
.meta p{{margin:1mm 0;color:#5B6178}} .meta strong{{color:#1D1D1B}}
h2{{font-size:15pt;letter-spacing:-.01em;margin:9mm 0 3mm;padding-top:3mm;border-top:1px solid #D9DEE6;break-after:avoid}}
.cover + h2{{border-top:0;margin-top:0;padding-top:0}}
h3{{font-size:11.5pt;color:#006BA6;margin:6mm 0 2mm;break-after:avoid}}
p,li{{orphans:3;widows:3}} ul,ol{{padding-left:6mm}} li{{margin:1mm 0}} a{{color:#006BA6}}
code{{font-family:"Geist Mono",Menlo,monospace;font-size:8.6pt;background:#EAF4FA;padding:.3mm 1.2mm;border-radius:1mm}}
pre{{background:#0E1430;color:#E8ECF5;padding:4mm 5mm;border-radius:2mm;font-size:8pt;line-height:1.45;white-space:pre-wrap;word-break:break-word;break-inside:avoid}}
pre code{{background:none;padding:0;color:inherit;font-size:inherit}}
table{{border-collapse:collapse;width:100%;margin:3mm 0 4mm;font-size:9pt}}
th{{background:#EAF4FA;text-align:left;font-weight:600}} th,td{{border:1px solid #D9DEE6;padding:1.6mm 2.4mm;vertical-align:top}} tr{{break-inside:avoid}}
table.ts{{font-size:7.4pt;line-height:1.35}} table.ts th,table.ts td{{padding:1.2mm 1.6mm}} table.ts td:first-child{{white-space:nowrap;font-weight:600}} table.ts code{{font-size:6.8pt;padding:0 .6mm}}
h2.app{{break-before:page}}
'''


def main():
    md = open(os.path.join(ROOT, 'docs', 'marc-ai-backend-brief.md'), encoding='utf-8').read()
    ver = re.search(r'\*\*Versie:\*\*\s*([\d.]+)', md).group(1)
    lines = md.split('\n')
    title = lines[0].lstrip('# ').strip()
    meta, i = [], 1
    while i < len(lines) and not lines[i].startswith('---'):
        if lines[i].strip():
            meta.append(markdown.markdown(lines[i]))
        i += 1
    body = re.sub(r'<hr\s*/?>', '', markdown.markdown('\n'.join(lines[i + 1:]), extensions=['tables', 'fenced_code', 'sane_lists']))
    k = body.find('<h2>Bijlage A')
    if k > 0:
        body = body[:k] + body[k:].replace('<h2>', '<h2 class="app">', 1).replace('<table>', '<table class="ts">')
    logo = open(os.path.join(ROOT, 'design', 'logo-color.svg') if os.path.exists(os.path.join(ROOT, 'design', 'logo-color.svg')) else os.path.join(ROOT, 'dist', 'assets', 'logo-color.svg'), encoding='utf-8').read()
    html = (f'<!doctype html><html lang="nl"><head><meta charset="utf-8"><title>{title}</title><style>{CSS}</style></head><body>'
            f'<div class="cover">{logo}<p class="kick">Briefing Kigumi · AI-assistent</p><h1>{title}</h1><div class="meta">{"".join(meta)}</div></div>{body}</body></html>')
    out = os.path.join(ROOT, 'docs', f'Triple-R-Marc-AI-briefing-Kigumi-v{ver}.pdf')
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'brief.html')
        open(src, 'w', encoding='utf-8').write(html)
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--allow-file-access-from-files',
                        f'--print-to-pdf={out}', f'file://{src}'], check=True, capture_output=True)
    for old in glob.glob(os.path.join(ROOT, 'docs', 'Triple-R-Marc-AI-briefing-Kigumi-v*.pdf')):
        if old != out:
            os.remove(old)  # alleen de laatste versie bewaren
    print('->', os.path.relpath(out, ROOT))


if __name__ == '__main__':
    sys.exit(main())
