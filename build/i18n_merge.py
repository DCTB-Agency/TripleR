#!/usr/bin/env python3
"""Voegt i18n/extra.txt (NL ¦ EN ¦ FR per regel) toe aan i18n/en.json en i18n/fr.json. Bestaande vertalingen blijven staan."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
en = json.load(open(f'{R}/i18n/en.json', encoding='utf-8'))
fr = json.load(open(f'{R}/i18n/fr.json', encoding='utf-8'))
n = 0
for ln in open(f'{R}/i18n/extra.txt', encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.startswith('#'):
        continue
    a = ln.split(' ¦ ')
    if len(a) != 3:
        print('FOUT', ln[:80]); continue
    k = a[0].strip()
    en[k], fr[k] = a[1], a[2]; n += 1
json.dump(en, open(f'{R}/i18n/en.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
json.dump(fr, open(f'{R}/i18n/fr.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
print(len(en), 'vertalingen;', n, 'uit extra.txt')
