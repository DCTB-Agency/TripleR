# Go-live triple-r-europe.com

Niets hiervan is uitgevoerd. De live site en de mail zijn tijdens de bouw niet aangeraakt; in wp-admin is alleen gelezen.

## Wat al klaar staat
- `dist/` met 370 pagina's in NL, EN en FR (`npm run check` geeft 0 fouten).
- 438 redirects: alle 405 oude URL's in de sitemap, plus PDF's en oude links uit de brief.
- `/api/lead` met de ontvangers uit Gravity Forms.
- Cookiebanner met Consent Mode v2. GTM-NSM4G6X9 laadt alleen na toestemming.

## Vooraf nodig
1. **Mailgun-sleutel:** de site verstuurt pas mail als `MAILGUN_API_KEY` in Netlify staat. Zonder sleutel wordt een aanvraag wel bewaard in Netlify Blobs, maar niet gemaild. WordPress gebruikt nu een Mailgun-account op `mail.mailserver-mailbox-marketing.be`, dat bij het bureau lijkt te horen. Vraag dezelfde sleutel of een eigen domein (`MAILGUN_DOMAIN`, `MAIL_FROM`).
2. **Ontvangers:** standaard staan die zoals vandaag. Wijzigen kan met `LEAD_TO`, `LEAD_BCC` en `LEAD_FI_TO`.
3. **Testen op staging:** alle formulieren met een echte sleutel, in de drie talen.
4. **Back-up:** volledige back-up van WordPress. WP Time Capsule staat op de site; controleer of die echt draait en waar de bestanden staan.
5. **Inzendingen exporteren:** 514 Contact, 8 Contact Fins en 2 Product. Dat zijn persoonsgegevens, dus dit doet iemand van Triple R zelf.
6. **Search Console-export:** pagina's en zoekwoorden, om na te gaan welke pagina's verkeer brengen. Ahrefs zit niet in het huidige abonnement.
7. **Inhoud van GTM:** nakijken welke tags er in de container zitten en of ze op de nieuwe paden werken.

## Op de dag zelf
1. Quinten verlaagt de TTL van `@` en `www`, minstens een dag vooraf.
2. In Netlify: `SITE_ENV=production` zetten en opnieuw deployen. Dit haalt de noindex weg.
3. Domein toevoegen in Netlify en het certificaat voorbereiden.
4. **Na uitdrukkelijk akkoord:** Quinten wijzigt alleen `@` en `www` naar de waarden van Netlify. MX, autodiscover en SPF blijven staan. De nameservers en het domein verhuizen niet.
5. Testen: https, www, redirects, formulieren, mail in en uit.
6. Sitemap indienen in Google Search Console en Bing Webmaster Tools.

**Let op HSTS:** het domein staat op HSTS met preload. Zonder geldig certificaat weigeren browsers de site. Kies daarom een rustig moment.

## Daarna
- 404's dagelijks volgen gedurende 2 weken.
- Pas na een stabiele periode opruimen: `ip4:185.58.96.62` en `+a` uit SPF, hosting bij Unix-Solutions, het hostingpakket van triple-r-europe.com bij Quinten.
- E-mail los van deze overstap verbeteren: DMARC op `_dmarc` zetten en DKIM aanzetten in Microsoft 365.

## Zichtbaar worden in Google en AI-antwoorden
**Op de site gebouwd:** alle inhoud staat als gewone HTML, ook zonder JavaScript leesbaar. AI-crawlers zijn toegelaten in `robots.txt`, `llms.txt` en `llms-full.txt` staan klaar, elke pagina heeft JSON-LD, inhoudspagina's openen met een direct antwoord, en elke pagina verwijst met hreflang naar de andere talen.

**Buiten de site, en minstens even belangrijk:**
- Google Bedrijfsprofiel en Bing Places, met overal hetzelfde adres en telefoonnummer.
- LinkedIn-bedrijfspagina opfrissen.
- Vermeldingen op Kompass, Europages en DirectIndustry, en bij distributeurs.
- Artikels in vakmedia en echte cases met meetwaarden. Externe bronnen wegen zwaar voor ChatGPT en Gemini.
- GA4: AI-verwijzers (chatgpt.com, perplexity.ai, gemini.google.com, copilot.microsoft.com) als apart kanaal volgen.
- Maandelijks 20 vaste vragen stellen aan ChatGPT, Gemini en Perplexity, in NL, EN en FR.

Niemand kan een toppositie in Google of een vermelding in ChatGPT garanderen. Bij een domeinoverstap zijn tijdelijke schommelingen in Google normaal.
