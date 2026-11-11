# Open vragen

Inhoud die op de site staat, maar nog door Triple R bevestigd moet worden. De markeringen zijn uit de productiepagina's gehaald; de claims zelf staan er wel.

## Voor go-live

- [ ] **Hoofdclaims op de homepage en oplossingen:** 50.000 uur olielevensduur, 90% minder oliegerelateerde kosten, 2–5× langere levensduur, tot 99% en 95% verwijderd, 20+ jaar dezelfde olie. Kloppen ze en mogen ze zo?
- [ ] **Klantenlogo's en -namen:** mogen Komatsu, Rolls-Royce, Ferrari, Castrol enzovoort genoemd worden? De sectorpagina's bevatten ook referentielijsten van de oude site.
- [ ] **Ervaring:** de oude teksten noemen 30, 33, 40 en 45 jaar. Op de sectorpagina's staat nog "40 jaar". Eén formulering kiezen.
- [ ] **Oprichting en mijlpalen:** 1992, 2013, 2019 en 2022 (Over ons).
- [ ] **Tijdlijn Over ons:** de oude site zet de uitvinding in 1976, de overname van het octrooi in 1974 en de ontwikkeling in de jaren 1960. Op de nieuwe pagina staat "Jaren 1960". Welk jaar klopt?
- [ ] **30 jaar Triple R Europe (2020):** de oprichting staat op 1992, dat is 28 jaar. Klopt het jaartal?
- [ ] **Slogan en marktleider:** "de originele en nog steeds de beste" en "onbetwiste marktleider" zijn overgenomen. Willen jullie die claims en de 45 en 40 jaar zo gebruiken?
- [ ] **ISO 14001 en ISO 9001:** staan nu als geschiedenis in de tijdlijn (2004 en 2012). Zijn ze nog geldig?
- [ ] **Vacature servicetechnicus:** de tekst zegt "37 jaar", de Over ons-pagina "45 jaar" en "meer dan 40 jaar". Welk getal gebruiken we?
- [ ] **Tweede vacature:** tekst aanleveren; het overzicht en de build zijn er klaar voor (`content/vacatures.py`).
- [ ] **Bewaartermijn cv's:** sollicitaties en cv's worden bewaard in Netlify (opslag `leads` en `cvs`). Hoelang bewaren we ze, en wie ruimt ze op?
- [x] **Functie Maxim Van Uytven:** CEO (bevestigd 11/11/2026, overal aangepast).
- [ ] **Gratis olieanalyse:** voorwaarden (1 staal, Benelux en Frankrijk, alleen bedrijven), exacte metingen en doorlooptijd. De [X] werkdagen is weggehaald tot er een termijn is.
- [ ] **Prijs filterelement** (€ 25 tot € 90) en de aannames in de besparingscalculator.
- [ ] **Besparingsrapport als PDF:** de site belooft een PDF. Die wordt nog niet automatisch gemaakt: sales krijgt de waarden per mail en stuurt het rapport zelf.
- [ ] **Privacy- en cookiebeleid:** juridisch nalezen. Bewaartermijnen en de lijst met diensten in Google Tag Manager aanvullen.
- [ ] **Algemene voorwaarden:** link weggehaald, tekst ontbreekt.
- [ ] **Distributeurs:** sommige staan nog als "naam volgt" of "contactgegevens volgen".
- [ ] **Productdata:** 73 modellen hebben interne notities uit `mkcatalog.py` (`confirm`), bv. "tot 450 bar" tegenover "10 tot 245 bar". Ze staan niet online, maar moeten nagekeken worden. Foto's en datasheets ontbreken bij enkele modellen.
- [ ] **Vertalingen:** de 34 inhoudspagina's komen van de oude site en zijn deels machinevertaald. De NL- en FR-versie moeten nagelezen worden; de termen zijn al rechtgezet.

## Markeringen per pagina

### oplossingen
- 80% of 90%, met bron: “>80 % 80% van de machinestoringen begint in de olie.”
- bron rekenvoorbeeld: “R op basis van ISO 4406-deeltjestellingen. Balken op schaal.”
- algemeen: “R educe Olieverbruik tot 90% lager, minder afgewerkte olie.”
- algemeen: “e jarenlang in gebruik; sommige klanten al meer dan 20 jaar.”
- aanname calculator: “ie die niet ververst wordt (aanname: 1 l olie ≈ 3,0 kg CO₂).”
- direct nummer: “20 4 13.6 3.5 5.1A1.5 1.5 0 0 1 5 3.5z"/> +32 (0)3 825 46 47”

### netwerk
- bedrijfsnaam, adres en website van deze distributeur: “ceerde distributeur'} ${esc(title(d))}${d.confirmed ? '' : '”

### olieanalyse
- scope: “ing ISO 4406 en NAS 1638, water, viscositeit, TAN en varnish”
- doorlooptijd: “den="true"> Rapport met concreet advies binnen [X] werkdagen”
- voorwaarden: “r bedrijven · 1 staal per installatie · Benelux en Frankrijk”
- scope gratis versie: “etingen in de gratis analyse zitten, bevestigt Triple R nog.”
- doorlooptijd: “van een Triple R-specialist. Resultaat binnen [X] werkdagen.”
- scope gratis analyse: “. Labo-analyse Deeltjes, water, viscositeit, TAN en varnish.”
- voorwaarden: “r bedrijven · 1 staal per installatie · Benelux en Frankrijk”
- voorwaarden: “ zijn gratis voor bedrijven, voor één staal per installatie.”
- direct nummer: “20 4 13.6 3.5 5.1A1.5 1.5 0 0 1 5 3.5z"/> +32 (0)3 825 46 47”

### verhuur
- welke toestellen te huur zijn: “e huur Een eerste selectie; het aanbod wordt nog uitgebreid.”
- huurvoorwaarden: “tiging We bevestigen beschikbaarheid, huurprijs en levering.”
- levering, opstart en ophaling: “ toestel wordt geleverd en na de huurperiode weer opgehaald.”
- direct nummer: “20 4 13.6 3.5 5.1A1.5 1.5 0 0 1 5 3.5z"/> +32 (0)3 825 46 47”

### offerte
- antwoordtermijn: “">U ontvangt een offerte op maat; prijzen staan niet online.”
- antwoordtermijn: “})` : ''} en nemen contact met u op met een offerte op maat.”

### filtration-systembuilder
- naam en merkgebruik met Triple R (gelijkenis met ‘Build My Oil Cleaner’ van TRIS): “ation Systembuilder : de Triple R op maat van uw installatie”
- selectieregels en productgrenzen door Triple R: “ple R. Een specialist bevestigt de definitieve configuratie.”

### sectoren
- toestemming naam: “ags"> Rubber &amp; kunststof Filterelementen Yokohama Rubber”
- toestemming naam: “div class="case__body"> Bouwmachines TR-serie Komatsu”
- toestemming naam: “v class="case__body"> Tandwielolie OSCA-serie Castrol”
- Te vervangen door echte data: “lden en worden vervangen door de gegevens uit de case-PDF’s.”
- direct nummer: “20 4 13.6 3.5 5.1A1.5 1.5 0 0 1 5 3.5z"/> +32 (0)3 825 46 47”

### besparingscalculator
- formule en aannames afstemmen met de bestaande rekenmachine: “uidige Triple R-documentatie en moeten nog bevestigd worden.”

### homepage
- toestemming logo's: “gekeurd zijn"> Vertrouwd door OEM’s, multinationals en kmo’s”
- algemeen: “ults"> 50.000 u olielevensduur in hydraulische systemen”
- algemeen: “bevestigen"> − 90 % oliegerelateerde kosten”
- algemeen: “Te bevestigen"> 2–5× langere levensduur van full-flowfilters”
- algemeen: “igen"> &gt; 90 % minder pomp- en klepfalen”
- doorlooptijd: “van een Triple R-specialist. Resultaat binnen [X] werkdagen.”
- direct nummer: “20 4 13.6 3.5 5.1A1.5 1.5 0 0 1 5 3.5z"/> +32 (0)3 825 46 47”

### product
- ${esc(t)}: “oducts.filter(x => x.series === p.series); const tb = t => `”

### faq
- algemeen door Triple R: “ water-glycol? Ja, met het WG/DWG-element voor water-glycol.”
- prijs tonen: “n type en maat. Eén element volstaat voor tanks tot 1.000 l.”
- voorwaarden: “ zijn gratis voor bedrijven, voor één staal per installatie.”
- direct nummer: “20 4 13.6 3.5 5.1A1.5 1.5 0 0 1 5 3.5z"/> +32 (0)3 825 46 47”

## Ronde 'Website attentie puntjes' (11/11/2026)
- [x] **Tijdwinst-cijfer**: geen cijfer; 'Minder stilstand' blijft zonder cijfer.
- **Reuse '30 jaar'**: de tekst zegt nu 'sommige klanten al meer dan 30 jaar' (was 20). Klopt dit, en waar gaat het over (dezelfde olie, of dezelfde machine)?
- **Marc**: in de begroeting staat 'u' in plaats van 'je', zoals de rest van de site. Akkoord?
- **Team**: foto's van Maxim, Lily en Valérie komen van LinkedIn; akkoord gegeven (11/11/2026). Naam Lily Bastiaens – Van Uytven, zoals op LinkedIn (bevestigd). Foto van Shani ontbreekt nog.
- [x] **CEO vs managing director**: overal CEO (bevestigd).
- **Tijdlijn**: historische foto's per jaartal (nu alleen 2019 = kantoor en 2022 = team; de rest heeft een icoon).
- **Sectorfoto's**: de foto's van de oude site zijn maar 300 px breed en worden wat wazig op grote schermen. Grotere versies?
- **Filterelement-doorsnede**: de tekening van de oude site is 507 px. Een grotere versie of de bronfile (Illustrator/PDF)?
- **Diensten-pagina** (voorbeeld TRIS): bestaat er een aparte Diensten-pagina met kaarten (assemblage & engineering, diensten ter plaatse, olieanalyse, installatie & reparatie, verhuur)? Welke diensten biedt Triple R Europe zelf aan, en met welke foto's?
- **Video homepage**: wordt vervangen; nieuwe video volgt van de klant.

## Productlijst opgekuist (11/11/2026)
- Verwijderd: TR-serie, centrifuges, BF-15, BF-20, SE50E-BH, WS-WD-1PF, WS-SU103-1R-WS20. Oude URL's van de TR-serie en centrifuges verwijzen nu door naar het productoverzicht.
- SE200E Mobile High Flow staat niet meer onder Vulpompen (wel nog bij SE Mobile). Te bevestigen of hij volledig weg moet.
- Nieuw: VP20 vul- en overpomp, 20 l/min. Nog nodig: foto, artikelnummer, datasheet.
- Foto AL100-HP (stalen huis): bestand nodig; de foto in de chat kon niet als bestand worden opgeslagen.

## Over ons – copycheck (11/11/2026)
- **Oprichtingsjaar**: de tijdlijn zegt "1992 oprichting Triple R Europe NV" en "2020: 30 jaar Triple R Europe" (dat wijst op 1990). Zo staat het ook op de huidige site. Welk jaar klopt?
- **Jubileumclaims**: "45 jaar" en "meer dan 40 jaar" (oude tekst) spraken elkaar tegen en passen niet bij "jaren 1960". Nu neutraal geformuleerd als "decennia". Een exact aantal jaren mag terug als het bevestigd is.
- **Tijdlijnfoto's** 1974, 1992 en 2013 komen uit de eigen mediabibliotheek van de huidige site (filterelementen, nieuwe elementen, assemblage-unit): illustratief, geen historische foto's. Echte archieffoto's zijn welkom.
