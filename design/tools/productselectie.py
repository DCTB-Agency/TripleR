"""Productselectie: alle producten uit de catalogus in een Excel-lijst om aan te duiden wat op de site moet.

  python3 tools/productselectie.py export                -> copy/Triple-R-productselectie.xlsx
  python3 tools/productselectie.py import <bestand.xlsx>  -> data/product-selectie.json (+ catalogus en pagina's opnieuw bouwen)

Alleen de standaardbibliotheek. Uit te voeren vanuit de map design/.
Kolom "Op de site?" (Ja/Nee) bepaalt of een product in de catalogus blijft; "Opmerking" wordt bewaard.
"""
import json, re, subprocess, sys, zipfile
from xml.sax.saxutils import escape as x

OUT = 'copy/Triple-R-productselectie.xlsx'
SEL = 'data/product-selectie.json'
HEAD = ['ID', 'Categorie', 'Serie', 'Model', 'Artikelnr.', 'Omschrijving', 'Kerngegevens', 'Bron (datasheet)', 'Nog te bevestigen', 'Op de site?', 'Opmerking']
WIDTH = [16, 22, 20, 24, 14, 50, 46, 30, 40, 13, 40]


def col(i):
    s = ''
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def cell(r, c, v, style=0):
    ref = f'{col(c)}{r}'
    st = f' s="{style}"' if style else ''
    return f'<c r="{ref}" t="inlineStr"{st}><is><t xml:space="preserve">{x(str(v or ""))}</t></is></c>'


def export():
    d = json.load(open('data/products.json'))
    prev = json.load(open(SEL)) if __import__('os').path.exists(SEL) else {}
    cats = {c['id']: (i, c['n']) for i, c in enumerate(d['cats'])}
    ps = sorted(d['products'], key=lambda p: (cats[p['cat']][0], list(d['series']).index(p['series'])))
    rows = ['<row r="1" ht="30" customHeight="1">' + ''.join(cell(1, i, h, 1) for i, h in enumerate(HEAD)) + '</row>']
    for n, p in enumerate(ps, 2):
        key = ' · '.join(f'{a}: {b}' for a, b in p['specs'][:2])
        src = f"{p['pdf']} (p. {p['page']})" if p.get('pdf') else 'geen datasheet'
        keep = prev.get(p['id'], {}).get('keep', 'Ja')
        note = prev.get(p['id'], {}).get('note', '')
        vals = [p['id'], cats[p['cat']][1], d['series'][p['series']]['n'], p['n'], p.get('art') or '', p['s'], key, src, '; '.join(p['confirm']), keep, note]
        rows.append(f'<row r="{n}">' + ''.join(cell(n, i, v, 3 if i == 9 else 4 if i == 10 else 2) for i, v in enumerate(vals)) + '</row>')
    last = len(ps) + 1
    cols = ''.join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(WIDTH))
    sheet = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
             '<sheetViews><sheetView workbookViewId="0" zoomScale="110"><pane xSplit="4" ySplit="1" topLeftCell="E2" activePane="bottomRight" state="frozen"/></sheetView></sheetViews>'
             f'<sheetFormatPr defaultRowHeight="30"/><cols>{cols}</cols><sheetData>{"".join(rows)}</sheetData>'
             f'<autoFilter ref="A1:K{last}"/>'
             f'<conditionalFormatting sqref="A2:K{last}"><cfRule type="expression" dxfId="0" priority="1"><formula>$J2="Nee"</formula></cfRule></conditionalFormatting>'
             f'<dataValidations count="1"><dataValidation type="list" allowBlank="1" showErrorMessage="1" errorTitle="Ja of Nee" error="Kies Ja of Nee." sqref="J2:J{last}"><formula1>"Ja,Nee"</formula1></dataValidation></dataValidations>'
             '<pageSetup orientation="landscape" fitToWidth="1" fitToHeight="0"/></worksheet>')
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
              '<fonts count="3"><font><sz val="10"/><name val="Calibri"/></font><font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font><font><b/><sz val="10"/><name val="Calibri"/></font></fonts>'
              '<fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
              '<fill><patternFill patternType="solid"><fgColor rgb="FF0E0B24"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFF6D9"/></patternFill></fill></fills>'
              '<borders count="2"><border/><border><left style="thin"><color rgb="FFDADFE6"/></left><right style="thin"><color rgb="FFDADFE6"/></right><top style="thin"><color rgb="FFDADFE6"/></top><bottom style="thin"><color rgb="FFDADFE6"/></bottom></border></borders>'
              '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
              '<cellXfs count="5"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
              '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>'
              '<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
              '<xf numFmtId="0" fontId="2" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1" applyProtection="1"><alignment horizontal="center" vertical="top"/><protection locked="0"/></xf>'
              '<xf numFmtId="0" fontId="0" fillId="3" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1" applyProtection="1"><alignment vertical="top" wrapText="1"/><protection locked="0"/></xf></cellXfs>'
              '<dxfs count="1"><dxf><font><color rgb="FF9B2C1F"/><strike/></font><fill><patternFill patternType="solid"><bgColor rgb="FFFDECEA"/></patternFill></fill></dxf></dxfs>'
              '</styleSheet>')
    readme_rows = ['Zo werkt het', '1. Kies per product in kolom "Op de site?" Ja of Nee (keuzelijst). Standaard staat alles op Ja.', '2. Zet eventueel een opmerking in de kolom "Opmerking" (bv. "andere naam", "foto volgt", "alleen op aanvraag").',
                   '3. Producten op Nee kleuren rood en worden van de site gehaald zodra het bestand weer ingelezen is.', '4. Bewaar het bestand en bezorg het terug. Wijzig de kolom ID niet: daarmee vinden we het product terug.',
                   'Gele kolommen zijn de kolommen die u invult. De gegevens komen uit de datasheets van Triple R Europe (oktober 2026).']
    readme = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><cols><col min="1" max="1" width="120" customWidth="1"/></cols><sheetData>'
              + ''.join(f'<row r="{i}">{cell(i, 0, t, 1 if i == 1 else 0)}</row>' for i, t in enumerate(readme_rows, 1)) + '</sheetData></worksheet>')
    wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
          '<sheets><sheet name="Producten" sheetId="1" r:id="rId1"/><sheet name="Uitleg" sheetId="2" r:id="rId2"/></sheets>'
          f'<definedNames><definedName name="_xlnm._FilterDatabase" localSheetId="0" hidden="1">Producten!$A$1:$K${last}</definedName></definedNames></workbook>')
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        z.writestr('xl/workbook.xml', wb)
        z.writestr('xl/worksheets/sheet1.xml', sheet)
        z.writestr('xl/worksheets/sheet2.xml', readme)
        z.writestr('xl/styles.xml', styles)
    print(f'{OUT}: {len(ps)} producten')


def read_xlsx(path):
    import xml.etree.ElementTree as ET
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    z = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns):
            shared.append(''.join(t.text or '' for t in si.iter('{%s}t' % ns['m'])))
    root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows = []
    for r in root.iter('{%s}row' % ns['m']):
        vals = {}
        for c in r.findall('m:c', ns):
            ref = re.match(r'[A-Z]+', c.get('r')).group(0)
            t = c.get('t')
            if t == 'inlineStr':
                v = ''.join(x.text or '' for x in c.iter('{%s}t' % ns['m']))
            else:
                v = c.findtext('m:v', default='', namespaces=ns)
                if t == 's' and v:
                    v = shared[int(v)]
            vals[ref] = v.strip()
        rows.append(vals)
    return rows


def do_import(path):
    rows = read_xlsx(path)
    sel = {}
    for r in rows[1:]:
        pid = r.get('A')
        if not pid:
            continue
        keep = 'Nee' if r.get('J', 'Ja').lower().startswith('n') else 'Ja'
        sel[pid] = {'keep': keep, 'note': r.get('K', '')}
    json.dump(sel, open(SEL, 'w'), ensure_ascii=False, indent=1)
    off = [k for k, v in sel.items() if v['keep'] == 'Nee']
    print(f'{len(sel)} producten gelezen; {len(off)} op Nee: {", ".join(off) or "geen"}')
    subprocess.run([sys.executable, 'tools/mkcatalog.py'], check=True)
    subprocess.run([sys.executable, 'build.py'], check=True, stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'export':
        export()
    elif len(sys.argv) >= 3 and sys.argv[1] == 'import':
        do_import(sys.argv[2])
    else:
        print(__doc__)
