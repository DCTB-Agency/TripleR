"""Talen van de site: één centrale plek.

Primaire talen krijgen de volledige site. Secundaire talen krijgen de kernpagina's (CORE + productpagina's per model);
de overige links in die talen verwijzen naar de Engelse versie.
Een nieuwe taal wordt pas gebouwd zodra i18n/<taal>.meta.json bestaat (NL, EN en FR zijn altijd actief).

Welke teksten een secundaire taal nodig heeft: USED_OUT=/pad/used.json python3 build/site.py
schrijft alle opgezochte NL-teksten weg; vertaal de sleutels uit i18n/en.json die daarin staan.
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = os.path.join(ROOT, 'i18n')

# Vaste volgorde: tuples in de inhoudsbestanden (slugs, labels) volgen deze volgorde.
ORDER = ['nl', 'en', 'fr', 'de', 'it', 'es', 'fi', 'hu', 'sv', 'no']
PRIMARY_ALL = ['nl', 'en', 'fr', 'de']
SECONDARY_ALL = ['it', 'es', 'fi', 'hu', 'sv', 'no']
CORE = {'homepage', 'producten', 'olieanalyse', 'offerte', 'contact', 'netwerk', 'sectoren'}
FALLBACK = 'en'

NAME = {'nl': 'Nederlands', 'en': 'English', 'fr': 'Français', 'de': 'Deutsch', 'it': 'Italiano', 'es': 'Español', 'fi': 'Suomi', 'hu': 'Magyar', 'sv': 'Svenska', 'no': 'Norsk'}
LOCALE = {'nl': 'nl_BE', 'en': 'en_GB', 'fr': 'fr_BE', 'de': 'de_DE', 'it': 'it_IT', 'es': 'es_ES', 'fi': 'fi_FI', 'hu': 'hu_HU', 'sv': 'sv_SE', 'no': 'nb_NO'}


def _meta(l):
    p = os.path.join(I18N, l + '.meta.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


META = {l: _meta(l) for l in ORDER}
LANGS = [l for l in ORDER if l in ('nl', 'en', 'fr') or META[l]]
PRIMARY = [l for l in LANGS if l in PRIMARY_ALL]
SECONDARY = [l for l in LANGS if l in SECONDARY_ALL]


def ix(l):
    """Positie van een taal in de inhoudstuples (slugs, labels)."""
    return ORDER.index(l)


def pick(t, l):
    """Waarde voor taal l uit een tuple in ORDER-volgorde; Engels als die taal (nog) geen waarde heeft."""
    i = ix(l)
    return t[i] if i < len(t) else t[ix(FALLBACK)]


def has_page(page, l):
    return l in PRIMARY_ALL or page in CORE


def strings(l):
    """Vertalingen NL -> taal (leeg voor NL)."""
    p = os.path.join(I18N, l + '.json')
    return json.load(open(p, encoding='utf-8')) if l != 'nl' and os.path.exists(p) else {}
