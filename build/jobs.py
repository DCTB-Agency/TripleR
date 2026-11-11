"""Vacatures: overzicht en detailpagina's, met JobPosting-data voor Google."""
import html
e = lambda s: html.escape(s, quote=False)
a = lambda s: html.escape(s, quote=True)
GO = '<svg class="go" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4"/></svg>'


def _ic(d):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'


IC = {
    'tool': _ic('<path d="M14.7 6.3a4 4 0 0 0 5 5L21 13l-8 8-3-3 6.7-6.7a4 4 0 0 1-5-5L10 5l-1-1 2-2 3.7 4.3z"/><path d="M3 21l6-6"/>'),
    'site': _ic('<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>'),
    'team': _ic('<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M15 14.5c3 0 6 1.8 6 5.5"/>'),
    'mix': _ic('<path d="M4 7h11M4 17h6"/><circle cx="18" cy="7" r="2.5"/><circle cx="13" cy="17" r="2.5"/><path d="M20 17h-4.5"/>'),
    'up': _ic('<path d="M4 18l6-6 4 4 6-8"/><path d="M15 8h5v5"/>'),
    'book': _ic('<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/>'),
    'home': _ic('<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>'),
    'bolt': _ic('<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>'),
    'gear': _ic('<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>'),
}
CHK = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8.5l3 3 7-7"/></svg>'


def _checks(items, cls='jb-checks'):
    return f'<ul class="{cls}">' + ''.join(f'<li>{CHK}<span>{e(x)}</span></li>' for x in items) + '</ul>'


def overview(l, O, UI, jobs, url, crumbs):
    o, u = O[l], UI[l]
    pts = ''.join(f'<div class="jb-pt"><span class="jb-ic">{IC[k]}</span><h3>{e(t)}</h3><p>{e(x)}</p></div>' for k, (t, x) in zip(('home', 'bolt', 'gear'), o['points']))
    cards = ''.join(f"""<a class="jb-card" href="{url(j, l)}"><span class="jb-card__img"><img src="img/element-change.jpg" alt="" width="800" height="533" loading="eager"></span>
<span class="jb-card__body"><span class="jb-meta">{e(u["loc"])} · {e(u["type"])} · {e(u["contract"])}</span><h3>{e(j[l]["h1"])}</h3><p>{e(j[l]["card"])}</p>
<span class="jb-tags">{''.join(f'<span>{e(h)}</span>' for h, _ in u['hl'])}</span><span class="jb-go">{e(o["view"])} {GO}</span></span></a>""" for j in jobs)
    return f"""<section class="hero hero--page" aria-labelledby="h1"><div class="hero__bg" aria-hidden="true"></div><div class="wrap"><div class="hero__copy" style="gap:0">
{crumbs}<h1 id="h1">{e(o['h1'])}</h1><p class="lead">{e(o['lead'])}</p></div></div></section>
<section class="sec"><div class="wrap">
<h2 class="jb-h">{e(o['open'])} <span class="jb-count">{len(jobs)}</span></h2><div class="jb-list">{cards}</div>
<p class="jb-none">{e(o['none'])} <a href="contact.html">{e(o['none_b'])}</a></p>
</div></section>
<section class="sec band"><div class="wrap jb-ov">
<div><h2>{e(o['why'])}</h2><div class="jb-pts">{pts}</div></div>
<figure class="ab-team"><img src="img/team.jpg" alt="{a(u['team_alt'])}" width="768" height="1024" loading="lazy"></figure>
</div></section>"""


def detail(j, l, UI, crumbs, posted):
    t, u = j[l], UI[l]
    S = t['sections']
    about, roles, grow, prof, offer = S[0], S[1:4], S[4], S[5], S[6]
    hl = ''.join(f'<div class="jb-hl__i"><span class="jb-ic">{IC[k]}</span><div><h3>{e(h)}</h3><p>{e(x)}</p></div></div>' for k, (h, x) in zip(('mix', 'up', 'book'), u['hl']))
    imgs = (('engineering.jpg', 1200, 900, '50% 40%'), ('industry.jpg', 1800, 1200, '50% 30%'), ('oil-samples.jpg', 1400, 933, '50% 50%'))
    rc = ''.join(f"""<article class="jb-role"><div class="jb-role__img"><img src="img/{im}" alt="" width="{w}" height="{hh}" loading="lazy" style="object-position:{pos}"><span class="jb-ic">{IC[k]}</span></div>
<div class="jb-role__body"><h3>{e(h)}</h3>{_checks(lis)}</div></article>""" for (h, _, lis), k, (im, w, hh, pos) in zip(roles, ('tool', 'site', 'team'), imgs))
    steps = ''.join(f'<li><span class="jb-step__n">{i}</span><h3>{e(h)}</h3><p>{e(x)}</p></li>' for i, (h, x) in enumerate(u['path'], 1))
    form = f"""<form class="ct-form" id="solliciteer" data-apply data-job="{a(t['h1'])}" data-job-id="{a(j['id'])}" data-thanks="{a(u['thanks'])}" data-thanks-p="{a(u['thanks_p'])}" novalidate>
<div class="f"><label for="a-name">{e(u['name'])}</label><input id="a-name" name="name" type="text" autocomplete="name" required aria-describedby="a-name-e"><span class="err" id="a-name-e" hidden>{e(u['e_name'])}</span></div>
<div class="f"><label for="a-mail">{e(u['email'])}</label><input id="a-mail" name="email" type="email" autocomplete="email" required aria-describedby="a-mail-e"><span class="err" id="a-mail-e" hidden>{e(u['e_mail'])}</span></div>
<div class="f"><label for="a-tel">{e(u['phone'])} <em>{e(u['opt'])}</em></label><input id="a-tel" name="phone" type="tel" autocomplete="tel"></div>
<div class="f"><label for="a-li">{e(u['linkedin'])} <em>{e(u['opt'])}</em></label><input id="a-li" name="linkedin" type="url" inputmode="url" placeholder="https://www.linkedin.com/in/…"></div>
<div class="f"><label for="a-msg">{e(u['motiv'])}</label><textarea id="a-msg" name="message"></textarea></div>
<div class="f"><label for="a-cv">{e(u['cv'])}</label><input id="a-cv" name="cv" type="file" accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" required aria-describedby="a-cv-h a-cv-e"><span class="hint" id="a-cv-h">{e(u['cv_h'])}</span><span class="err" id="a-cv-e" hidden>{e(u['e_cv'])}</span></div>
<label class="chk"><input type="checkbox" id="a-ok" required><span>{e(u['consent'])}<a href="privacy.html">{e(u['privacy'])}</a>).</span></label>
<span class="err" id="a-ok-e" hidden style="font-size:12.5px;color:var(--err-700);font-weight:500">{e(u['e_ok'])}</span>
<button class="btn btn--primary" type="submit">{e(u['send'])}</button></form>"""
    chips = ''.join(f'<li>{e(x)}</li>' for x in (u['loc'], u['type'], u['contract']))
    return f"""<section class="hero hero--page" aria-labelledby="h1"><div class="hero__bg" aria-hidden="true"></div><div class="wrap"><div class="hero__copy" style="gap:0">
{crumbs}<h1 id="h1">{e(t['h1'])}</h1><ul class="jb-chips">{chips}</ul><p class="lead">{e(t['lead'])}</p>
<div class="jb-hero-cta"><a class="btn btn--light" href="#solliciteer">{e(u['apply'])}</a><a class="jb-back" href="vacatures.html">{e(u['back'])}</a></div></div></div></section>
<section class="jb-hl" aria-label="{a(u['hl_h'])}"><div class="wrap"><div class="jb-hl__grid">{hl}</div></div></section>
<section class="sec"><div class="wrap"><h2 class="jb-h">{e(u['do_h'])}</h2><div class="jb-roles">{rc}</div></div></section>
<section class="sec dark jb-path"><div class="wrap"><h2>{e(u['path_h'])}</h2><p class="lead">{e(grow[1][0])}</p><ol class="jb-steps">{steps}</ol></div></section>
<section class="sec"><div class="wrap jb-fit">
<div class="jb-box"><h2>{e(prof[0])}</h2>{_checks(prof[2])}</div>
<div class="jb-box jb-box--blue"><h2>{e(offer[0])}</h2>{_checks(offer[2])}</div>
</div></section>
<section class="sec band"><div class="wrap jb-about">
<div class="prose"><h2>{e(about[0])}</h2>{''.join(f'<p>{e(p)}</p>' for p in about[1])}</div>
<figure class="ab-team"><img src="img/team.jpg" alt="{a(u['team_alt'])}" width="768" height="1024" loading="lazy"></figure>
</div></section>
<section class="sec" id="apply"><div class="wrap jb-apply">
<div class="jb-apply__info"><h2>{e(u['apply_h'])}</h2><p>{e(u['apply_p'])}</p>
<p class="jb-apply__c">{e(u['contact'])}<br><a href="mailto:info@triple-r-europe.com">info@triple-r-europe.com</a><br><a href="tel:+3238254647">+32 (0)3 825 46 47</a></p>
<p class="tp__upd">{e(u['posted'])} {e(posted)}</p></div>
{form}
</div></section>"""


def posting(j, l, desc_html, url, org):
    t = j[l]
    return {'@type': 'JobPosting', 'title': t['h1'], 'description': desc_html, 'datePosted': j['posted'], 'employmentType': 'FULL_TIME', 'directApply': True,
            'hiringOrganization': {'@type': 'Organization', 'name': 'Triple R Europe', 'sameAs': org['url'], 'logo': org['logo']},
            'jobLocation': {'@type': 'Place', 'address': {'@type': 'PostalAddress', 'streetAddress': 'Cleydaellaan 16, unit 8', 'addressLocality': 'Aartselaar', 'postalCode': '2630', 'addressCountry': 'BE'}},
            'inLanguage': l, 'url': url, 'identifier': {'@type': 'PropertyValue', 'name': 'Triple R Europe', 'value': j['id']}}
