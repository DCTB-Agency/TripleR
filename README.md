# Triple R Europe — website

Nieuwe website voor **Triple R Europe nv** (Aartselaar, BE): een Nederlandstalige B2B-site (NL/EN/FR) voor bypass-oliefiltratie, gericht op leads (*Gratis olieanalyse*, *Advies aanvragen*).

## Status
**Stap 1 — design (pass 1).** De visuele richting en de eerste pagina's staan als klikbare prototypes in [`design/`](design/). De Astro-build (stap 2) moet nog starten.

| Pagina | Bestand |
|---|---|
| Homepage | `design/homepage.html` |
| Producten (keuzehulp, vergelijking, downloads) | `design/producten.html` |
| Besparingscalculator | `design/besparingscalculator.html` |
| Design system | `design/design-system.html` |
| Desktop + mobiel naast elkaar | `design/preview.html` |

### Lokaal bekijken
De zoekfunctie leest de PDF's in `design/pdf/`; daarvoor moet de map via http geserveerd worden:

```bash
python3 -m http.server 4321 --directory design
```

Open daarna http://localhost:4321/homepage.html.

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
