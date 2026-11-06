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


def topic(key, l, h1, lead, blocks, TOPIC, UI, LABEL, route, crumb_html, upd):
    """Vervuilingspagina: overzicht, gevolgen, oplossing, producten, FAQ; de langere tekst blijft leesbaar onder Technische achtergrond."""
    i = ['nl', 'en', 'fr'].index(l)
    t, u, keys = TOPIC[key][l], UI[l], list(TOPIC)
    nxt = keys[(keys.index(key) + 1) % len(keys)]
    GO = '<svg class="go" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4"/></svg>'
    pills = ''.join(f'<li><a href="{route(k, l)}"' + (' aria-current="page"' if k == key else '') + f'>{e(LABEL[k][i])}</a></li>' for k in keys)
    facts = ''.join(f'<div><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in t['facts'])
    why = ''.join(f'<div><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in t['why'])
    prods = ''.join(f'<li><a href="{route(k, l)}">{e(n)} {GO}</a></li>' for k, n in TOPIC[key]['_names'][l])
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in t['faq'])
    return f"""<section class="hero hero--page" aria-labelledby="h1"><div class="hero__bg" aria-hidden="true"></div><div class="wrap"><div class="hero__copy" style="gap:0">
{crumb_html}<h1 id="h1">{e(h1)}</h1><p class="lead">{e(lead)}</p></div></div></section>
<nav class="tp-nav" aria-label="{e(u['nav'])}"><div class="wrap"><ul>{pills}</ul></div></nav>
<section class="tp-facts" aria-label="{e(u['toc'])}"><div class="wrap">{facts}</div></section>
<section class="sec tp"><div class="wrap tp__grid">
<div class="tp__main">
<h2>{e(u['why'])}</h2><div class="tp__why">{why}</div>
<h2>{e(u['how'])}</h2><p class="tp__how">{e(t['how'])}</p>
<h2>{e(u['faq'])}</h2><div class="faq">{faq}</div>
<details class="tp__tech"><summary>{e(u['tech'])}</summary><div class="prose">{body(blocks)}</div></details>
<p class="tp__upd">{upd}</p>
<a class="tp__next" href="{route(nxt, l)}"><span>{e(u['next'])}</span><b>{e(LABEL[nxt][i])}</b>{GO}</a>
</div>
<aside class="tp__side"><div class="tp__cta"><h2>{e(u['side_h'])}</h2><p>{e(u['side_p'])}</p><a class="btn btn--light" href="olieanalyse.html">{e(u['side_b'])}</a><p class="tp__tel">{e(u['side_o'])} <a href="tel:+3238254647">+32 (0)3 825 46 47</a></p></div>
<div class="tp__prods"><h2>{e(u['prods'])}</h2><ul>{prods}</ul></div></aside>
</div></section>"""
