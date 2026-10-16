"""Websiteteksten exporteren naar Word en aangepaste teksten weer inlezen.

  python3 copy/copytool.py export                 -> copy/Triple-R-websiteteksten.docx
  python3 copy/copytool.py import <bestand.docx>  -> past de kolom 'Nieuwe tekst' toe in de *.src.html-bestanden
                                                     en draait daarna build.py (gebruik --dry-run om eerst te bekijken)

Alleen de standaardbibliotheek, geen extra pakketten. Uit te voeren vanuit de map design/.
Elke tekst krijgt een ID (bv. HOME-012). Bij het inlezen controleert het script dat de 'Huidige tekst'
nog klopt met de pagina; is de pagina intussen gewijzigd, dan zoekt het de tekst op inhoud terug.
Teksten die door JavaScript worden opgebouwd (productdata, Systembuilder, voorbeeldantwoorden) staan niet in
het document; die komen in de Astro-bouw uit content collections.
"""
import html, os, re, sys, zipfile, subprocess
from html.parser import HTMLParser
from xml.sax.saxutils import escape as xesc

PAGES = [('homepage', 'HOME', 'Homepage'), ('oplossingen', 'OPL', 'Oplossingen'), ('producten', 'PROD', 'Producten'),
         ('filtration-systembuilder', 'SYS', 'Filtration Systembuilder'), ('sectoren', 'SECT', 'Sectoren'),
         ('olieanalyse', 'OA', 'Gratis olieanalyse'), ('verhuur', 'HUUR', 'Verhuur'), ('offerte', 'OFF', 'Offerte aanvragen'),
         ('netwerk', 'NET', 'Netwerk van distributeurs'), ('faq', 'FAQ', 'Veelgestelde vragen'),
         ('besparingscalculator', 'CALC', 'Besparingscalculator')]
PARTIALS = [('partials/header', 'HDR', 'Header en menu (op elke pagina)'), ('partials/footer', 'FTR', 'Footer, contactknop en zoekvenster (op elke pagina)')]
SKIP_TAGS = {'script', 'style', 'svg', 'code'}
KIND = {'title': 'Titel in Google', 'h1': 'Paginatitel (H1)', 'h2': 'Titel', 'h3': 'Tussentitel', 'h4': 'Tussentitel',
        'p': 'Tekst', 'li': 'Opsomming', 'a': 'Link', 'button': 'Knop', 'label': 'Veldlabel', 'summary': 'Vraag (FAQ)',
        'b': 'Tekst (vet)', 'small': 'Kleine tekst', 'span': 'Tekst', 'dt': 'Label', 'dd': 'Waarde', 'th': 'Tabelkop', 'td': 'Tabelcel',
        'option': 'Keuze in lijst', 'figcaption': 'Bijschrift', 'em': 'Tekst', 'strong': 'Tekst (vet)', 'address': 'Adres'}
ATTR = {'placeholder': 'Voorbeeldtekst in veld', 'alt': 'Beschrijving afbeelding', 'aria-label': 'Label voor schermlezers',
        'meta': 'Omschrijving in Google'}
FILL = re.compile(r'\{\{|\$\{')


class Extract(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=True)
        self.src, self.out, self.stack, self.skip = src, [], [], 0
        self.lines = [0]
        for m in re.finditer('\n', src):
            self.lines.append(m.end())
        self.section = ''
        self.want_head = False

    def off(self):
        ln, col = self.getpos()
        return self.lines[ln - 1] + col

    def add(self, kind, start, raw, attr=False):
        txt = re.sub(r'\s+', ' ', html.unescape(raw)).strip()
        if not txt or FILL.search(raw) or not re.search(r'[A-Za-zÀ-ÿ0-9]', txt):
            return
        self.out.append({'kind': kind, 'start': start, 'end': start + len(raw), 'raw': raw, 'text': txt, 'attr': attr, 'section': self.section})

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in SKIP_TAGS or 'tb' in (a.get('class') or '').split():
            if tag not in ('br', 'img', 'input', 'meta', 'link'):
                self.skip += 1
            self.stack.append((tag, True))
            return
        if tag in ('section', 'header', 'footer', 'nav', 'aside', 'dialog') or (tag == 'div' and a.get('class', '').startswith(('ask ', 'fab', 'drawer', 'mega'))):
            self.want_head = True
        if not self.skip:
            st, raw_tag = self.off(), self.get_starttag_text()
            for name in ('placeholder', 'alt'):
                if a.get(name):
                    m = re.search(r'\s' + name + r'\s*=\s*"([^"]*)"', raw_tag)
                    if m:
                        self.add(ATTR[name], st + m.start(1), m.group(1), attr=True)
            if tag == 'meta' and a.get('name') == 'description':
                m = re.search(r'content="([^"]*)"', raw_tag)
                if m:
                    self.add(ATTR['meta'], st + m.start(1), m.group(1), attr=True)
        if tag not in ('br', 'img', 'input', 'meta', 'link', 'source', 'hr', 'col', 'path', 'circle', 'rect', 'use'):
            self.stack.append((tag, False))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        while self.stack:
            t, sk = self.stack.pop()
            if sk and t not in ('br', 'img', 'input', 'meta', 'link'):
                self.skip -= 1
            if t == tag:
                break

    def handle_data(self, data):
        if self.skip or not data.strip():
            return
        tags = [t for t, _ in self.stack]
        strong = [t for t in tags if t in ('title', 'h1', 'h2', 'h3', 'h4', 'summary', 'button', 'a', 'label', 'li', 'th', 'td', 'option', 'figcaption', 'dt', 'dd')]
        tag = strong[-1] if strong else next((t for t in reversed(tags) if t in KIND), 'p')
        if self.want_head and tag in ('h1', 'h2', 'h3'):
            self.section = re.sub(r'\s+', ' ', data).strip()
            self.want_head = False
        st = self.off()
        end = self.src.find('<', st)
        self.add(KIND.get(tag, 'Tekst'), st, self.src[st:end if end >= 0 else len(self.src)])


def entries():
    res = []
    for base, code, label in PAGES + PARTIALS:
        path = base + ('.html' if base.startswith('partials') else '.src.html')
        if not os.path.exists(path):
            continue
        src = open(path, encoding='utf-8').read()
        p = Extract(src)
        p.feed(src)
        for i, e in enumerate(p.out, 1):
            e.update(id=f'{code}-{i:03d}', file=path, page=label)
            res.append(e)
    return res


# ---------------------------------------------------------------- Word schrijven
def para(text, bold=False, size=None, color=None, shade=None):
    rpr = ''.join([('<w:b/>' if bold else ''), (f'<w:color w:val="{color}"/>' if color else ''), (f'<w:sz w:val="{size}"/>' if size else '')])
    runs = '<w:r><w:br/></w:r>'.join(f'<w:r>{"<w:rPr>" + rpr + "</w:rPr>" if rpr else ""}<w:t xml:space="preserve">{xesc(t)}</w:t></w:r>' for t in text.split('\n'))
    return f'<w:p><w:pPr><w:spacing w:after="60"/></w:pPr>{runs}</w:p>'


def cell(w, content, shade=None, span=1):
    tcpr = f'<w:tcW w:w="{w}" w:type="dxa"/>' + (f'<w:gridSpan w:val="{span}"/>' if span > 1 else '') + (f'<w:shd w:val="clear" w:color="auto" w:fill="{shade}"/>' if shade else '')
    return f'<w:tc><w:tcPr>{tcpr}</w:tcPr>{content}</w:tc>'


COLS = [1250, 1800, 5900, 5900]


def export(out='copy/Triple-R-websiteteksten.docx'):
    es = entries()
    body = [para('Triple R Europe: websiteteksten', bold=True, size=40),
            para('Zo werkt het: pas alleen de kolom "Nieuwe tekst" aan. Laat een cel leeg als de tekst goed is. '
                 'Laat de kolommen ID en "Huidige tekst" ongewijzigd, zodat de aanpassingen automatisch op de juiste plaats komen. '
                 'Wijzigingen bijhouden (track changes) en opmerkingen mogen.', color='444444'),
            para('Niet in dit document: productgegevens in lijsten en tabellen, de Filtration Systembuilder en de voorbeeldantwoorden '
                 'van "Vraag het aan Triple R". Die beheren we apart.', color='444444')]
    by_page = {}
    for e in es:
        by_page.setdefault(e['page'], []).append(e)
    for page, rows in by_page.items():
        body.append(f'<w:p><w:pPr><w:pageBreakBefore/><w:spacing w:after="120"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="32"/><w:color w:val="0086CD"/></w:rPr><w:t>{xesc(page)}</w:t></w:r></w:p>')
        trs = ['<w:tr><w:trPr><w:tblHeader/></w:trPr>' + ''.join(cell(w, para(h, bold=True, color='FFFFFF'), shade='0E0B24') for w, h in zip(COLS, ['ID', 'Soort', 'Huidige tekst', 'Nieuwe tekst'])) + '</w:tr>']
        sec = None
        for e in rows:
            if e['section'] != sec and e['section']:
                sec = e['section']
                trs.append('<w:tr>' + cell(sum(COLS), para('Blok: ' + sec, bold=True, color='0E0B24'), shade='E6F3FB', span=4) + '</w:tr>')
            trs.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + cell(COLS[0], para(e['id'], size=16, color='666666')) + cell(COLS[1], para(e['kind'], size=18, color='444444'))
                       + cell(COLS[2], para(e['text'])) + cell(COLS[3], para(''), shade='FFFBEA') + '</w:tr>')
        grid = ''.join(f'<w:gridCol w:w="{w}"/>' for w in COLS)
        body.append('<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblLayout w:type="fixed"/><w:tblBorders>'
                    + ''.join(f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="DADFE6"/>' for b in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
                    + f'</w:tblBorders><w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:bottom w:w="40" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>{grid}</w:tblGrid>'
                    + ''.join(trs) + '</w:tbl>')
    sect = '<w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="900" w:right="1000" w:bottom="900" w:left="1000" w:header="500" w:footer="500" w:gutter="0"/></w:sectPr>'
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
           + ''.join(body) + sect + '</w:body></w:document>')
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/><w:sz w:val="20"/><w:lang w:val="nl-BE"/></w:rPr></w:rPrDefault></w:docDefaults></w:styles>')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/_rels/document.xml.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        z.writestr('word/document.xml', doc)
        z.writestr('word/styles.xml', styles)
    print(f'{out}: {len(es)} teksten op {len(by_page)} pagina\'s')


# ---------------------------------------------------------------- Word lezen
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def cell_text(tc):
    ps = []
    for p in tc.iter(W + 'p'):
        t = ''
        for el in p.iter():
            if el.tag == W + 't':
                t += el.text or ''
            elif el.tag in (W + 'br', W + 'cr'):
                t += '\n'
            elif el.tag == W + 'tab':
                t += ' '
        ps.append(t)
    return '\n'.join(ps).strip()


def read_docx(path):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(zipfile.ZipFile(path).read('word/document.xml'))
    for d in root.iter(W + 'del'):  # verwijderde tekst (track changes) negeren
        for t in list(d):
            d.remove(t)
    rows = []
    for tr in root.iter(W + 'tr'):
        cs = [cell_text(tc) for tc in tr.findall(W + 'tc')]
        if len(cs) == 4 and re.fullmatch(r'[A-Z]+-\d{3}', cs[0]):
            rows.append({'id': cs[0], 'old': cs[2], 'new': cs[3]})
    return rows


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def do_import(path, dry=False):
    cur = {e['id']: e for e in entries()}
    changes, problems = [], []
    for r in read_docx(path):
        if not r['new'] or norm(r['new']) == norm(r['old']):
            continue
        e = cur.get(r['id'])
        if not e or norm(e['text']) != norm(r['old']):
            same = [x for x in cur.values() if x['id'].split('-')[0] == r['id'].split('-')[0] and norm(x['text']) == norm(r['old'])]
            e = same[0] if len(same) == 1 else None
        if not e:
            problems.append(f"{r['id']}: tekst niet meer gevonden op de pagina ({r['old'][:60]}…)")
            continue
        changes.append((e, r['new']))
    by_file = {}
    for e, new in changes:
        by_file.setdefault(e['file'], []).append((e, new))
    for f, lst in by_file.items():
        src = open(f, encoding='utf-8').read()
        for e, new in sorted(lst, key=lambda x: -x[0]['start']):
            raw = src[e['start']:e['end']]
            if raw != e['raw']:
                problems.append(f"{e['id']}: bron gewijzigd, overgeslagen"); continue
            lead, trail = re.match(r'\s*', raw).group(0), re.search(r'\s*$', raw).group(0)
            val = html.escape(norm(new), quote=e['attr'])
            src = src[:e['start']] + lead + val + trail + src[e['end']:]
            print(f"{e['id']} ({e['kind']}): {e['text'][:50]!r} -> {norm(new)[:50]!r}")
        if not dry:
            open(f, 'w', encoding='utf-8').write(src)
    print(f'{len(changes)} wijziging(en){" (dry run, niets opgeslagen)" if dry else ""}.')
    for p in problems:
        print('LET OP', p)
    if changes and not dry:
        subprocess.run([sys.executable, 'build.py'], check=True)


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'export':
        export(*sys.argv[2:3])
    elif len(sys.argv) >= 3 and sys.argv[1] == 'import':
        do_import(sys.argv[2], dry='--dry-run' in sys.argv)
    else:
        print(__doc__)
