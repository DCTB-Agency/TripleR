# Overstap triple-r-europe.com: inventaris WordPress

Stand: 6 november 2026. Deel A komt uit publieke controles (DNS, HTTP, WordPress REST-index), zonder login.
Deel B is de ronde in wp-admin: daar is alleen gelezen, niets gewijzigd.
De volledige oude URL-lijst staat in [oude-urls.txt](oude-urls.txt).

## A. Wat er nu draait (publiek vastgesteld)

### Domein, DNS en hosting
| Onderdeel | Waarde | Gevolg voor de overstap |
|---|---|---|
| Domein | Op naam van Triple R, beheerd door Quinten De Decker (registrar Realtime Register B.V.) | Geldig tot 25-03-2027. Blijft waar het is; een domeinverhuizing is niet nodig. |
| DNS-zone | Zelfde beheerder, nameservers nszero1/2.axc.nl | **Niet verhuizen.** Alleen de records hieronder wijzigen. |
| Webhosting | Unix-Solutions BV, 185.58.96.62 voor `@` en `www` (reverse DNS: hostingbelgie.com), nginx | Op de dag zelf naar de nieuwe host. WP Toolkit wijst op Plesk. **Nagaan wie dit contract heeft** en wie back-ups kan maken. |
| Technisch alias | `rrr.mailbox-marketing10.be` staat op hetzelfde IP en stuurt door naar de live site | Dit is geen aparte kopie: inloggen gebeurt op de live WordPress. Na de overstap vervalt dit adres. |
| Hostingpakketten bij Quinten | `triple-r-europe.com` (betaald, website draait er niet op) en `triple-r.co.uk` | Eerste pakket pas opzeggen na controle dat er niets meer op draait. `triple-r.co.uk` hoort niet bij deze overstap (zie sectie C). |
| Hoofdadres | `https://www.`; zonder www volgt een 301 naar www | Canonical met www behouden, zoals de BRIEF vraagt. |
| HSTS | 1 jaar, includeSubDomains, preload | Browsers weigeren elke pagina zonder geldig certificaat. Overschakelen op een rustig moment en het certificaat meteen controleren. |
| http | `http://www` geeft 200, geen redirect | Op de nieuwe host forceren naar https. |

### E-mail: los van WordPress
| Onderdeel | Waarde | Gevolg |
|---|---|---|
| Postvakken | Microsoft 365 (MX `…mail.protection.outlook.com`, autodiscover) | Blijft werken zolang MX en autodiscover ongemoeid blijven. |
| SPF | `v=spf1 +a +mx include:spf.protection.outlook.com ip4:185.58.96.62 -all` | `+a` zou na de overstap het IP van de nieuwe host toelaten. `-all` blokkeert elke nieuwe verzender. Aanpassen zodra de nieuwe verzendtool bekend is. |
| DMARC | Staat op het hoofddomein in plaats van op `_dmarc`; `_dmarc` is leeg | Werkt nu niet. Verplaatsen naar `_dmarc`. |
| DKIM | Niets gevonden op `selector1`/`selector2` en andere gangbare selectors | Lijkt uit te staan in Microsoft 365. Nakijken in het admin center. |

Formuliermails van WordPress lopen via Mailgun (zie deel B). Na de overstap verstuurt de nieuwe site ze zelf.

### WordPress-opbouw
| Functie | Plugin | Na de overstap |
|---|---|---|
| Paginabouwer | Elementor (+ Pro), Hello-thema, Happy Addons, JetElements, JetEngine | Vervalt. JetEngine levert de types application, tribology en product. |
| Formulieren | Gravity Forms (`gform_1` op /contact, spam: CleanTalk + reCAPTCHA) | Vervangen. Oude inzendingen eerst exporteren. |
| Mail | WP Mail SMTP | Vervangen. Instellingen nakijken. |
| Vertaling | TranslatePress (+ developer-add-on) | Vervalt. 9 talen, zie hieronder. |
| SEO | SEOPress | Titels en descriptions exporteren, redirects overnemen. |
| Tracking | GTM-NSM4G6X9, via GTM4WP | Dezelfde container herbruiken, inhoud nakijken. |
| Cookies | GDPR Cookie Compliance, met Consent Mode | Vervangen door eigen banner (BRIEF). |
| Beveiliging, snelheid | Wordfence, FlyingPress | Vervalt. Licenties opzeggen. |
| Eigen code | Code Snippets | **Nakijken:** kan functies bevatten die verder nergens staan. |

### Inhoud
- 14 pagina's, 2 berichten en 219 media-items in `wp/v2`, plus de eigen types.
- 405 URL's in de sitemap: 45 per taal × 9 talen (en, nl, fr, de, es, it, fi, sv, bg).
- Op `/nl/neem-contact-op-met/` staat geen formulier, op `/contact/` wel. Vermoedelijk heeft alleen EN een echt formulier; bevestigen in wp-admin.

## B. Vastgesteld in wp-admin (alleen gelezen)

| Formulier | Aan | BCC | Inzendingen |
|---|---|---|---|
| Contact | maxim.vanuytven@triple-r-europe.com | marc.vanuytven@triple-r-europe.com | 514 |
| Product | maxim.vanuytven@triple-r-europe.com | marc.vanuytven@triple-r-europe.com | 2 |
| Contact Fins | sf.edustus@co.inet.fi | maxim.vanuytven@triple-r-europe.com | 8 |

- **Afzender formulieren:** `email@mailserver-mailbox-marketing.be`, Reply-To is de bezoeker.
- **Mail:** WP Mail SMTP Lite met Mailgun (EU), domein `mail.mailserver-mailbox-marketing.be`. Formuliermail loopt dus **niet** via Microsoft 365 en niet via het domein triple-r-europe.com.
- **Bevestiging:** na verzending gaat de bezoeker naar de pagina "Thanks".
- **Extra plugins:** WP Time Capsule (back-up), MainWP Child (beheer op afstand door een bureau), EWWW, Breadcrumb NavXT, Post Types Order, SEOPress PRO.
- **Niet bekeken:** Code Snippets (pagina gaf 403), SEOPress-redirects, GTM-inhoud, gebruikers, JetEngine-velden.

**Fout op de live site:** anonieme bezoekers van NL- en FR-subpagina's krijgen uit de FlyingPress-cache een kale pagina van zo'n 600 tekens, met onder meer "WordPress insluiten". Ingelogd staat de volledige tekst er wel. Vermoedelijk zien Google en AI-crawlers ook die kale versie, wat de huidige NL- en FR-posities kan schaden. Dit is niet aangepast.

## C. Buiten WordPress te regelen

- [ ] Quinten vragen om het volledige overzicht van de DNS-records (aangeboden). Publiek zijn alleen de gangbare records te zien; de export toont ook de rest en de TTL's.
- [ ] Afspreken dat Quinten de records wijzigt, of toegang krijgen tot het DNS-paneel.
- [ ] Google Search Console, GA4, Google Ads en GTM: wie is eigenaar, en verwijzen advertenties naar oude URL's?
- [ ] Back-up van bestanden en database vóór de overstap (BRIEF §15, fase 0).
- [ ] WordPress-hosting bij Unix-Solutions pas opzeggen als de nieuwe site een tijd stabiel draait.
- [ ] `triple-r.co.uk` apart bekijken: staat publiek op Azure-DNS en 85.10.145.171, met eigen mailserver `mail.triple-r.co.uk`. De prototypes noemen dit domein bij dealer ITC Hydraulic Services. Niet meenemen in deze overstap.

## D. Stand van de nieuwe site

Zie [go-live.md](go-live.md) en [open-questions.md](../open-questions.md).

## E. Volgorde op de dag zelf

1. TTL van `@` en `www` verlagen, minstens een dag vooraf.
2. Back-up maken en bewaren.
3. Nieuwe site klaar op staging, met `noindex` uit de productie-instellingen.
4. Na uitdrukkelijk akkoord: alleen de records `@` en `www` wijzigen. MX, autodiscover en SPF blijven staan.
5. Certificaat, redirects, formulieren en mail testen.
6. Sitemap indienen, 404's opvolgen, daarna SPF opschonen.
