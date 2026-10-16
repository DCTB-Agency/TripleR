# Websiteteksten nalezen in Word

1. **Exporteren** (vanuit de map `design/`):
   `python3 copy/copytool.py export` → `copy/Triple-R-websiteteksten.docx`
2. **Nalezen:** de eigenaar vult in Word alleen de kolom **Nieuwe tekst** in.
   - Is een tekst goed, dan blijft de cel leeg.
   - Track changes en opmerkingen mogen.
   - De kolommen ID en "Huidige tekst" blijven onveranderd.
3. **Inlezen:**
   - Bekijk eerst wat er verandert: `python3 copy/copytool.py import pad/naar/bestand.docx --dry-run`
   - Pas daarna toe: `python3 copy/copytool.py import pad/naar/bestand.docx`

   Het script schrijft de nieuwe teksten in de `*.src.html`-bestanden en draait `build.py`.
   - Teksten die intussen op de pagina gewijzigd zijn, zoekt het terug op inhoud.
   - Wat niet meer te vinden is, meldt het met "LET OP".
4. **Controleren en publiceren:** bekijk de pagina's, commit en push. Netlify publiceert daarna automatisch naar staging.

**Niet in het document:** teksten die met JavaScript worden opgebouwd. Dat zijn:
- de productgegevens in lijsten en tabellen;
- de Filtration Systembuilder;
- de voorbeeldantwoorden van "Vraag het aan Triple R".

In de Astro-bouw komen die uit content collections.

**Automatiseren (optioneel):** een GitHub Action kan stap 3 en 4 overnemen. Je zet het Word-bestand in `design/copy/inbox/`. De Action leest het in, bouwt de site en zet het resultaat als pull request klaar ter controle.
