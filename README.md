# Triple R Europe — website

Nieuwe website voor **Triple R Europe nv** (Aartselaar, BE): een Nederlandstalige B2B-site (NL/EN/FR) voor bypass-oliefiltratie, gericht op leads (*Gratis olieanalyse*, *Advies aanvragen*).

## Status
**Klaar voor staging.** `design/` is de Nederlandse bron, `i18n/` en `content/` bevatten vertalingen en inhoud, en `npm run build` maakt `dist/` met NL, EN en FR. `npm run check` controleert alles. Go-live: [`docs/migratie/go-live.md`](docs/migratie/go-live.md). Open vragen: [`docs/open-questions.md`](docs/open-questions.md).

| Pagina | Bestand |
|---|---|
| Homepage (beknopt overzicht) | `design/homepage.html` |
| Oplossingen (probleem, werking, resultaten, duurzaamheid) | `design/oplossingen.html` |
| Producten (keuzehulp, vergelijking, downloads) | `design/producten.html` |
| Sectoren en cases | `design/sectoren.html` |
| Gratis olieanalyse (landingspagina + formulier) | `design/olieanalyse.html` |
| Veelgestelde vragen (artikels + FAQ) | `design/faq.html` |
| Filtration Systembuilder (productconfigurator) | `design/filtration-systembuilder.html` |
| Netwerk van distributeurs | `design/netwerk.html` |
| Verhuur | `design/verhuur.html` |
| Offerte aanvragen | `design/offerte.html` |
| Productpagina (per model) | `design/product.html?id=bu100e` |
| Besparingscalculator | `design/besparingscalculator.html` |

Websiteteksten nalezen in Word: zie `design/copy/LEESMIJ.md`.
Productcatalogus per model: `design/tools/mkcatalog.py` → `design/data/products.json` + `design/catalog.js`.
| Design system | `design/design-system.html` |
| Desktop + mobiel naast elkaar | `design/preview.html` |

### Lokaal bekijken
De zoekfunctie leest de PDF's in `design/pdf/`; daarvoor moet de map via http geserveerd worden:

```bash
python3 -m http.server 4321 --directory design
```

Open daarna http://localhost:4321/homepage.html.

### Online (Netlify)
`netlify.toml` bouwt `dist/`. Elke push naar `main` zet een nieuwe versie op staging, met `X-Robots-Tag: noindex` zolang `SITE_ENV` niet op `production` staat.

### Designbronnen aanpassen
Pagina's worden opgebouwd uit `*.src.html` + `partials/` (gedeelde header, footer en zoekpaneel):

```bash
cd design && python3 build.py
```

## Documentatie
- [`docs/BRIEF.md`](docs/BRIEF.md) — volledige projectbriefing (inhoud, SEO, GEO, leads, techniek)
- [`docs/CLAUDE-DESIGN-PROMPT.md`](docs/CLAUDE-DESIGN-PROMPT.md) — designopdracht
- [`design/HANDOFF.md`](design/HANDOFF.md) — tokens, componenten, animatiespec, zoekfunctie, open punten [CONFIRM]
- [`CLAUDE.md`](CLAUDE.md) — projectregels voor Claude Code

## Let op
- Alle claims met een geel **?**-markering (`.tb`) zijn nog **niet bevestigd** door Triple R en mogen niet live.
- Case-waarden (ISO vóór/na) zijn layoutvoorbeelden.
- Beelden en PDF's komen van de huidige site van Triple R.
