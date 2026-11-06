"""Statische inhoud: kennispagina's, modellenlijsten en llms-bestanden (alles leesbaar zonder JavaScript)."""
import html, re
T = {
 'nl': dict(upd='Laatst bijgewerkt', by='Triple R Europe, oliefiltratiespecialist sinds 1992', rel='Lees ook', models='Modellen', model='Model', descr='Omschrijving', cta_h='Laat uw olie meten', cta='Vraag een gratis olieanalyse aan en krijg persoonlijk advies van een Triple R-specialist.', cta_b='Vraag een gratis olieanalyse aan', cta_c='Neem contact op', sp='Technische gegevens', arts='Artikelnummer', all='Alle modellen', all_s='Elk model met specificaties en datasheet.', topics='Alle onderwerpen', topics_s='Verdiep u in elk type vervuiling, in de techniek en in wat schone olie oplevert.', date='6 november 2026'),
 'en': dict(upd='Last updated', by='Triple R Europe, oil filtration specialist since 1992', rel='Read more', models='Models', model='Model', descr='Description', cta_h='Have your oil measured', cta='Request a free oil analysis and get personal advice from a Triple R specialist.', cta_b='Request a free oil analysis', cta_c='Get in touch', sp='Technical data', arts='Article number', all='All models', all_s='Every model with specifications and datasheet.', topics='All topics', topics_s='Explore each type of contamination, the technology and what clean oil delivers.', date='6 November 2026'),
 'fr': dict(upd='Dernière mise à jour', by='Triple R Europe, spécialiste de la filtration d\'huile depuis 1992', rel='À lire aussi', models='Modèles', model='Modèle', descr='Description', cta_h='Faites mesurer votre huile', cta='Demandez une analyse d\'huile gratuite et recevez les conseils personnalisés d\'un spécialiste Triple R.', cta_b='Demandez une analyse d\'huile gratuite', cta_c='Nous contacter', sp='Données techniques', arts='Numéro d\'article', all='Tous les modèles', all_s='Chaque modèle avec spécifications et fiche technique.', topics='Tous les sujets', topics_s='Découvrez chaque type de contamination, la technique et ce que rapporte une huile propre.', date='6 novembre 2026'),
}
e = lambda s: html.escape(s, quote=False)


def lead_from(blocks):
    """Antwoord bovenaan voor pagina's zonder eigen tekst: eerste alinea's tot circa 40-60 woorden."""
    words, used = [], 0
    for t, x in blocks:
        if t != 'p':
            if words:
                break
            continue
        words.append(x)
        used += 1
        if len(' '.join(words).split()) >= 40:
            break
    return ' '.join(words), used


def body(blocks):
    out, ul = [], []
    seen_h2 = [False]
    def flush():
        if ul:
            out.append('<ul>' + ''.join(f'<li>{e(x)}</li>' for x in ul) + '</ul>')
            ul.clear()
    for t, x in blocks:
        if t == 'li':
            ul.append(x)
            continue
        flush()
        if t in ('h2', 'h3', 'h4'):
            lvl = 'h2' if t == 'h2' or not seen_h2[0] else 'h3'
            seen_h2[0] = True
            out.append(f'<{lvl}>{e(x)}</{lvl}>')
        else:
            out.append(f'<p>{e(x)}</p>')
    flush()
    return '\n'.join(out)


def models_table(prods, lang, url):
    t = T[lang]
    rows = ''.join(f'<tr><td><a href="{url(p)}">{e(p["n"])}</a></td><td>{e(p["s"])}</td></tr>' for p in prods)
    return f'<h2>{t["models"]}</h2><table><thead><tr><th>{t["model"]}</th><th>{t["descr"]}</th></tr></thead><tbody>{rows}</tbody></table>'


def cta(lang):
    t = T[lang]
    return f'<section class="sec band"><div class="wrap"><h2>{t["cta_h"]}</h2><p style="margin-top:var(--s-2);max-width:60ch">{t["cta"]}</p><div class="btns" style="margin-top:var(--s-4)"><a class="btn btn--primary" href="olieanalyse.html">{t["cta_b"]}</a><a class="btn btn--secondary" href="contact.html">{t["cta_c"]}</a></div></div></section>'


def spec_table(p, lang):
    t = T[lang]
    rows = ''.join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>' for k, v in p.get('specs') or [])
    art = f'<p>{t["arts"]}: {e(p["art"])}</p>' if p.get('art') else ''
    return f'<h2 id="h-spec">{t["sp"]}</h2>{art}<table class="spec-static"><tbody>{rows}</tbody></table>' if rows else ''
