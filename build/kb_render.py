"""Statische inhoud: kennispagina's, modellenlijsten en llms-bestanden (alles leesbaar zonder JavaScript)."""
import html, re
T = {
 'nl': dict(upd='Laatst bijgewerkt', by='Triple R Europe, oliefiltratiespecialist sinds 1992', rel='Lees ook', models='Modellen', model='Model', descr='Omschrijving', cta_h='Laat uw olie meten', cta='Vraag een gratis olieanalyse aan en krijg persoonlijk advies van een Triple R-specialist.', cta_b='Vraag een gratis olieanalyse aan', cta_c='Neem contact op', sp='Technische gegevens', arts='Artikelnummer', all='Alle modellen', all_s='Elk model met specificaties en datasheet.', topics='Alle onderwerpen', topics_s='Verdiep u in elk type vervuiling, in de techniek en in wat schone olie oplevert.', date='6 november 2026'),
 'en': dict(upd='Last updated', by='Triple R Europe, oil filtration specialist since 1992', rel='Read more', models='Models', model='Model', descr='Description', cta_h='Have your oil measured', cta='Request a free oil analysis and get personal advice from a Triple R specialist.', cta_b='Request a free oil analysis', cta_c='Get in touch', sp='Technical data', arts='Article number', all='All models', all_s='Every model with specifications and datasheet.', topics='All topics', topics_s='Explore each type of contamination, the technology and what clean oil delivers.', date='6 November 2026'),
 'fr': dict(upd='Dernière mise à jour', by='Triple R Europe, spécialiste de la filtration d\'huile depuis 1992', rel='À lire aussi', models='Modèles', model='Modèle', descr='Description', cta_h='Faites mesurer votre huile', cta='Demandez une analyse d\'huile gratuite et recevez les conseils personnalisés d\'un spécialiste Triple R.', cta_b='Demandez une analyse d\'huile gratuite', cta_c='Nous contacter', sp='Données techniques', arts='Numéro d\'article', all='Tous les modèles', all_s='Chaque modèle avec spécifications et fiche technique.', topics='Tous les sujets', topics_s='Découvrez chaque type de contamination, la technique et ce que rapporte une huile propre.', date='6 novembre 2026'),
}
e = lambda s: html.escape(s, quote=False)
from langs import META as _META, LANGS as _LANGS, ix as _ix
for _l in _LANGS[3:]:
    T[_l] = _META[_l]['ui']['kb_t']


def lead_from(blocks):
    """Antwoord bovenaan voor pagina's zonder eigen tekst: eerste alinea's tot circa 40-60 woorden."""
    words, used = [], 0
    for t, x in blocks:
        if t == 'p' and JUNK.search(x.strip()):
            used += 1
            continue
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


TOPIC_IMG = {'kb-deeltjes': ('se100e-wh.jpg', ('Triple R SE100E-WH-oliereiniger aan de wand', 'Triple R SE100E-WH wall-mounted oil cleaner', 'Épurateur d\'huile mural Triple R SE100E-WH', 'Triple R SE100E-WH Ölreiniger für die Wandmontage')),
             'kb-varnish': ('v100-element.jpg', ('Triple R V100-filterelement tegen varnish', 'Triple R V100 filter element against varnish', 'Élément filtrant Triple R V100 contre les vernis', 'Triple R V100-Filterelement gegen Varnish')),
             'kb-water': ('vacuum.png', ('Triple R-vacuümdroger', 'Triple R vacuum dehydrator', 'Déshydrateur sous vide Triple R', 'Triple R-Vakuumtrockner')),
             'kb-lucht': ('quicktoron.png', ('Triple R Quicktoron-ontluchter', 'Triple R Quicktoron de-aerator', 'Désaérateur Triple R Quicktoron', 'Triple R Quicktoron-Entlüfter'))}


def topic(key, l, h1, lead, blocks, TOPIC, UI, LABEL, route, crumb_html, upd):
    """Vervuilingspagina in aparte blokken: kerncijfers, waarom een probleem (met vaste CTA ernaast), oplossing met foto, FAQ."""
    i = _ix(l)
    t, u, keys = TOPIC[key][l], UI[l], list(TOPIC)
    nxt = keys[(keys.index(key) + 1) % len(keys)]
    GO = '<svg class="go" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4"/></svg>'
    pills = ''.join(f'<li><a href="{route(k, l)}"' + (' aria-current="page"' if k == key else '') + f'>{e(LABEL[k][i])}</a></li>' for k in keys)
    facts = ''.join(f'<div><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in t['facts'])
    why = ''.join(f'<div><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in t['why'])
    prods = ''.join(f'<li><a href="{route(k, l)}">{e(n)} {GO}</a></li>' for k, n in TOPIC[key]['_names'][l])
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in t['faq'])
    img, alt = TOPIC_IMG.get(key, ('element-cut.png', ('', '', '')))
    fig = f'<figure class="zz__img{" zz__img--contain" if img.endswith(".png") or img.startswith(("v100", "se100e")) else ""}"><img src="img/{img}" alt="{html.escape(alt[i] if i < len(alt) else alt[1])}" loading="lazy"></figure>'
    return f"""<section class="hero hero--page" aria-labelledby="h1"><div class="hero__bg" aria-hidden="true"></div><div class="wrap"><div class="hero__copy" style="gap:0">
{crumb_html}<h1 id="h1">{e(h1)}</h1><p class="lead">{e(lead)}</p></div></div></section>
<nav class="tp-nav" aria-label="{e(u['nav'])}"><div class="wrap"><ul>{pills}</ul></div></nav>
<section class="tp-facts sec--tint" aria-label="{e(u['toc'])}"><div class="wrap">{facts}</div></section>
<section class="sec tp"><div class="wrap tp__grid">
<div class="tp__main"><h2 class="zz-h">{e(u['why'])}</h2><div class="tp__why">{why}</div></div>
<aside class="tp__side"><div class="tp__cta"><h2>{e(u['side_h'])}</h2><p>{e(u['side_p'])}</p><a class="btn btn--light" href="olieanalyse.html">{e(u['side_b'])}</a><p class="tp__tel">{e(u['side_o'])} <a href="tel:+3238254647">+32 (0)3 825 46 47</a></p></div>
<div class="tp__prods"><h2>{e(u['prods'])}</h2><ul>{prods}</ul></div></aside>
</div></section>
<section class="sec sec--tint"><div class="wrap zz">
<div class="zz__txt"><h2 class="zz-h">{e(u['how'])}</h2><p class="tp__how">{e(t['how'])}</p></div>{fig}
</div></section>
<section class="sec"><div class="wrap tp-faq">
<h2 class="zz-h">{e(u['faq'])}</h2><div class="faq">{faq}</div>
<details class="tp__tech"><summary>{e(u['tech'])}</summary><div class="prose">{body(blocks)}</div></details>
<p class="tp__upd">{upd}</p>
<a class="tp__next" href="{route(nxt, l)}"><span>{e(u['next'])}</span><b>{e(LABEL[nxt][i])}</b>{GO}</a>
</div></section>"""


# ---- inhoudspagina's in blokken: per titel een eigen sectie, afwisselend wit en lichtblauw, foto links/rechts
ZT = {'nl': dict(ind='Toegepast in deze sectoren', prods='Producten voor deze sector', refs='Referenties'),
      'en': dict(ind='Used in these industries', prods='Products for this industry', refs='References'),
      'fr': dict(ind='Utilisé dans ces secteurs', prods='Produits pour ce secteur', refs='Références')}
for _l in _LANGS[3:]:
    if 'zt' in _META[_l]['ui']:
        ZT[_l] = _META[_l]['ui']['zt']
SECTOR = {'zee': 's-marine', 'windenergie': 's-wind', 'luchtvaart': 's-lucht', 'spoorweg': 's-spoor', 'bouwmachines': 's-bouw', 'papierindustrie': 's-papier',
          'staal & ijzer': 's-staal', 'autofabrikanten': 's-auto', 'hydraulische systemen': 's-hyd', 'petrochemisch': 's-petro', 'energie': 's-energie', 'transport': 's-transport'}
SECTOR_IMG = {'s-marine': 'sec-marine.jpg', 's-wind': 'sec-wind.jpg', 's-lucht': 'sec-lucht.jpg', 's-spoor': 'sec-spoor.jpg', 's-bouw': 'sec-bouw.jpg', 's-papier': 'sec-papier.jpg',
              's-staal': 'sec-staal.jpg', 's-auto': 'sec-auto.jpg', 's-hyd': 'sec-hyd.jpg', 's-petro': 'sec-petro.jpg', 's-energie': 'sec-energie.jpg', 's-transport': 'sec-transport.jpg'}
SERIES_PAGE = [('bu', 'p-bu'), ('se', 'p-se'), ('osca', 'p-osca'), ('ws', 'p-ws'), ('ss', 'p-ss'), ('quicktoron', 'p-qt'), ('vacu', 'p-vac'), ('element', 'p-el')]
PAGE_IMG = {'p-bu': 'BU-Series.png', 'p-se': 'se.png', 'p-osca': 'osca.png', 'p-ws': 'ws.png', 'p-ss': 'ss.png', 'p-qt': 'quicktoron.png', 'p-vac': 'vacuum.png', 'p-el': 'elements.png'}
SERIES_IMG = {'el-v': 'v100-element.jpg'}
JUNK = re.compile(r'verplichte velden|required fields|champs obligatoires|Pflichtfelder|^Laden Sie die Fallstudie herunter$|^Download de casestudy van$|^Download the case study|^Téléchargez l', re.I)


def groups(blocks):
    """Splitst blokken op elke H2: [(titel of None, [blokken])]. Titels zonder inhoud schuiven als bovenschrift door naar de volgende groep."""
    out, cur, kick = [], [None, [], None], None
    for t, x in blocks:
        if t == 'p' and JUNK.search(x.strip()):
            continue
        if t == 'h2':
            if cur[0] is not None or cur[1]:
                out.append(cur)
            cur = [x, [], None]
        else:
            cur[1].append((t, x))
    out.append(cur)
    res, carry = [], None
    for g in out:
        if g[0] is not None and not g[1]:
            carry = g[0] if carry is None else carry
            continue
        g[2], carry = carry, None
        res.append(g)
    return res


def gbody(blocks):
    out, ul = [], []
    def flush():
        if ul:
            out.append('<ul>' + ''.join(f'<li>{e(x)}</li>' for x in ul) + '</ul>')
            ul.clear()
    for t, x in blocks:
        if t == 'li':
            ul.append(x)
            continue
        flush()
        out.append(f'<h3>{e(x)}</h3>' if t in ('h3', 'h4') else f'<p>{e(x)}</p>')
    flush()
    return '\n'.join(out)


def words(blocks):
    return sum(len(x.split()) for _, x in blocks)


def fig(img, alt=''):
    c = ' zz__img--contain' if img.endswith('.png') or img.startswith(('v100', 'se100e')) else ''
    return f'<figure class="zz__img{c}"><img src="img/{img}" alt="{html.escape(alt)}" loading="lazy"></figure>'


def section(inner, tint, cls='', label=None):
    return f'<section class="sec{" sec--tint" if tint else ""}{cls}">{inner}</section>'


def zz(title, kick, blocks, img, rev, h='h2'):
    k = f'<p class="zz__kick">{e(kick)}</p>' if kick else ''
    head = f'{k}<{h} class="zz-h">{e(title)}</{h}>' if title else k
    if img:
        return f'<div class="wrap zz{" zz--rev" if rev else ""}"><div class="zz__txt prose">{head}{gbody(blocks)}</div>{fig(img)}</div>'
    return f'<div class="wrap zz zz--solo"><div class="zz__txt prose">{head}{gbody(blocks)}</div></div>'


def ind_cards(names_keys, l, route, KB):
    li = ''.join(f'<li><a class="tcard" href="{route(k, l)}"><span class="tcard__img"><img src="img/{SECTOR_IMG[k]}" alt="" loading="lazy"></span><span class="tcard__b"><b>{e(n)}</b></span></a></li>' for n, k in names_keys)
    return f'<ul class="tcards">{li}</ul>'


def page_cards(keys, l, route, KB):
    li = ''.join(f'<li><a class="tcard" href="{route(k, l)}"><span class="tcard__img tcard__img--contain"><img src="img/{PAGE_IMG[k]}" alt="" loading="lazy"></span><span class="tcard__b"><b>{e(KB[k][l][0])}</b><span>{e(KB[k][l][3] if len(KB[k][l]) > 3 else KB[k][l][2])}</span></span></a></li>' for k in keys)
    return f'<ul class="tcards">{li}</ul>'


def model_cards(prods, l, url, cat=None):
    def im(p):
        s = p.get('series')
        return SERIES_IMG.get(s) or p.get('img') or ((cat or {}).get('series', {}).get(s, {}).get('img')) or 'elements.png'
    li = ''.join(f'<li><a class="mcard" href="{url(p)}"><span class="mcard__img"><img src="img/{im(p)}" alt="" loading="lazy"></span><span class="mcard__b"><b>{e(p["n"])}</b><span>{e(p["s"])}</span></span></a></li>' for p in prods)
    return f'<ul class="mcards">{li}</ul>'


def blocks_page(key, l, sec, groups_l, groups_nl, imgs, route, KB, extra_ind=None, models_html='', start_tint=False):
    """Bouwt de secties onder de hero. groups_nl bepaalt de bijzondere groepen (industrieën, producten, referenties) per index."""
    out, tint, rev, pool = [], start_tint, False, list(imgs)
    if models_html:
        out.append(section(models_html, tint))
        tint = not tint
    same = len(groups_l) == len(groups_nl)
    ind_done = False
    for n, (title, bl, kick) in enumerate(groups_l):
        nl_title = (groups_nl[n][0] or '').lower() if same else ''
        nl_bl = groups_nl[n][1] if same else []
        if same and nl_title.startswith('industrieën waar') and all(t == 'h3' for t, _ in bl):
            nk = [(x, SECTOR.get(nl_bl[j][1].strip().lower())) for j, (_, x) in enumerate(bl)]
            nk = [(x, k) for x, k in nk if k]
            out.append(section(f'<div class="wrap"><h2 class="zz-h">{e(ZT[l]["ind"])}</h2>{ind_cards(nk, l, route, KB)}</div>', tint))
            tint, ind_done = not tint, True
            continue
        if same and sec == 'sec' and nl_title == 'producten':
            pk = []
            for j, (t, x) in enumerate(bl):
                if t == 'li':
                    k = next((pg for pre, pg in SERIES_PAGE if nl_bl[j][1].lower().startswith(pre)), None)
                    if k and k not in pk:
                        pk.append(k)
            intro = ''.join(f'<p>{e(x)}</p>' for t, x in bl if t == 'p')
            rest = [(t, x) for j, (t, x) in enumerate(bl) if t == 'li' and not any(nl_bl[j][1].lower().startswith(pre) for pre, _ in SERIES_PAGE)]
            extra = gbody(rest) if rest else ''
            out.append(section(f'<div class="wrap"><h2 class="zz-h">{e(title)}</h2><div class="prose">{intro}{extra}</div>{page_cards(pk, l, route, KB)}</div>', tint))
            tint = not tint
            continue
        if same and sec == 'sec' and nl_title == 'referenties':
            ps = ''.join(f'<p>{e(x)}</p>' for t, x in bl if t == 'p')
            chips = ''.join(f'<li>{e(x)}</li>' for t, x in bl if t == 'li')
            out.append(section(f'<div class="wrap zz zz--solo"><div class="zz__txt prose"><h2 class="zz-h">{e(title)}</h2>{ps}</div><ul class="chips">{chips}</ul></div>', tint))
            tint = not tint
            continue
        img = pool.pop(0) if pool and (words(bl) >= 12 or len(bl) >= 3) else None
        if title is None and not bl:
            continue
        out.append(section(zz(title, kick, bl, img, rev), tint))
        if img:
            rev = not rev
        tint = not tint
    if extra_ind and not ind_done:
        out.append(section(f'<div class="wrap"><h2 class="zz-h">{e(ZT[l]["ind"])}</h2>{ind_cards([(KB[k][l][0], k) for k in extra_ind], l, route, KB)}</div>', tint))
        tint = not tint
    return ''.join(out), tint
