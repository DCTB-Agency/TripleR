# Triple R Europe: design handoff, pass 1, revision 3 ("premium industrial")

Date: 24 Sep 2026 · Status: **for review**

**Revision history**
- **v1:** expressive, dark, animated. Rejected as "too AI, too many frills".
- **v2:** very sober. Rejected as "too cheap and boring".
- **v3** (this version): the middle ground. Tight and technical, but with character, depth and atmosphere.

## Files

| File | What it is |
|---|---|
| `tokens.css` | v0.3 tokens: colour (incl. night-950 and the logo gradient), Geist type, spacing, radius 10/20/28, shadows, motion |
| `tailwind.tokens.cjs` | The same v0.3 tokens as a Tailwind `theme.extend` |
| `design-system.html` | Principles, colour + contrast, type, spacing/grid, buttons, forms, components, icons and imagery, motion |
| `homepage.html` | Responsive homepage (390 → 1440). Review bar at bottom left: **Te bevestigen** / **Annotaties**. URL flags: `?annot`, `?clean` |
| `preview.html` | Homepage at 1440 and 390 side by side |
| `img/` | Photos from the current site |

## Direction v3

- **Type: Geist** (600 for headings, tight −0.035 to −0.045 em tracking; 500 for key figures) + Geist Mono for ISO codes and specs.
  - Hero H1 is 76 px.
  - The second line uses the logo gradient (blue → indigo) as its text colour.
- **Colour:**
  - White and cool grey `grey-50` for content.
  - `night-950 #0E0B24` / deep brand blue for the dark moments (header + hero, results band, footer).
  - **The logo gradient** as the only decorative colour: product-finder result and closing CTA.
  - Buttons and links in `blue-700`.
- **Header + hero (v3.1, dark brand blue):**
  - Header and utility bar sit as dark glass over one continuous deep-blue hero (#0C0D2E → #111A52), with a white logo and a white CTA.
  - A blue glow sits behind the transparent product photo, with a 56 px technical grid (masked) and a horizon arc along the bottom.
  - The circular "lens" rings from the logo frame the product. Three glass spec labels: 450 bar, 114 mm, 1–10 µm.
  - H1 is white, with the second line in a blue-300 → white gradient.
  - The background drifts slowly (18 s); this stops under reduced motion.
- **Rhythm:** two strong visual moments.
  1. The dark hero; the problem section below it is now light (grey-50) with a 152 px key figure in an ink → blue gradient.
  2. Results on a full-bleed photo of clean oil (existing image) with a dark gradient.
- **Shape:** radius 10 px (buttons, fields), 20 px (cards, photos), 28 px (hero studio, closing CTA). Cards lift on hover (−3 px + shadow).
- **Motion:** functional only.
  - Hover lift, arrow shifts 3 px, 200 ms.
  - Product-photo zoom 1.045, 600 ms.
  - No scroll animation, counters or parallax.
  - Everything drops to 0 under reduced motion.
- **Photos not used:**
  - Dragon capsule (SpaceX, unrelated).
  - The small 300 px sector photos.

## Site structure (pass 1.4: lean homepage + subpages)

The homepage only gives a short overview and sends visitors on; the detail lives on the subpages (BRIEF §5).

**Homepage (`homepage.html`, 7 sections)**
1. **Hero:** full-bleed video background (`media/hero-*.mp4`, poster `hero-poster.jpg`). The visible credit line has been removed at the client's request, but **[CONFIRM] permission from TRIS to use the footage remains open**. The video autoplays muted on a loop, has a pause button (WCAG 2.2.2), pauses when out of view and shows only the poster under reduced motion. Left column: H1, intro, CTAs → olieanalyse and Filtration Systembuilder. **Right column: "Vraag het aan Triple R"** (see below). Under it: the reference names as a running carousel.
2. **Four contaminants:** 4 cards → `oplossingen.html`.
3. **Featured products:** 3 tiles → `producten.html` (the selector moved there).
4. **Results:** on the oil photo, with a link to the calculator.
5. **Sectors:** compact row of 12 pill links → `sectoren.html`.
6. **Free oil analysis:** compact, 3 check lines → `olieanalyse.html`.
7. **Closing CTA:** with Maxim Van Uytven.

**Subpages (all with a compact dark hero, breadcrumb, answer-first intro and closing CTA)**

| Page | Brief | Content |
|---|---|---|
| `oplossingen.html` | /oplossingen/ | Problem + 80% claim + bar chart, 4 contaminants, 114 mm cross-section, results, Reduce · Reuse · Recycle |
| `producten.html` | §6.4 | Filtration Systembuilder teaser (anchor `#keuze`), filterable list of 10 series, comparison table, 17 downloads, embedded search |
| `sectoren.html` | /sectoren/ | Atmospheric photo + 12 sectors, cases with ISO before/after |
| `olieanalyse.html` | §6.6 | Landing page with a **3-step form above the fold** (§3.3), what we measure (6 measurements), sample report (blurred values), 4-step process, FAQ |
| `faq.html` | §6.9 (replaces the knowledge base) | Veelgestelde vragen: Vraag het aan Triple R in the hero, 15 questions in 4 themes with a sticky theme nav, the 3 existing articles under "Meer lezen". Not in the main menu (footer, drawer, internal links). |
| `filtration-systembuilder.html` | §6.4 selector | **Filtration Systembuilder**: product configurator (improved take on oilcleaner.eu “Build my oil cleaner”), see below |
| `besparingscalculator.html` | §3.7 | Calculator with adjustable assumptions and a report form |

- **Navigation:** Oplossingen → `oplossingen.html`, Producten → mega menu (incl. "Alle producten"), Sectoren → `sectoren.html`, Diensten → `olieanalyse.html`, FAQ → `faq.html` (footer/drawer only). The active page is highlighted.
- **Header CTA:** "Gratis olieanalyse" → `olieanalyse.html`.
- **Footer:** full company details + KBO/BTW BE 0448.276.293.
- **Mobile:** sticky [Bel] [Gratis olieanalyse] bar below 768 px.
- **Oil analysis form (prototype):**
  1. Installation: system, sector, volume, problems, oil type.
  2. Company: company, first name, last name, job title, business email, phone, postcode + country.
  3. Confirmation: contact preference, remarks, GDPR (required), newsletter (optional, unchecked).
  - Validation per step with error messages linked to the fields.
  - Thank-you state with next steps.
  - Events: `form_start`, `form_step_2`, `form_step_3`, `lead_olieanalyse`.
- **Not done yet:** the minimal header for Ads traffic (logo + phone only, §6.6). For now the landing page uses the full header.

## "Vraag het aan Triple R": conversational search (BRIEF §17)

- **Trigger in the header:** a clearly visible bar (320 px, or 210 px below 1280) with a blue gradient border, an AI icon and example questions that change every 3.6 s ("Bv. filter voor 450 bar", …). `⌘K` and `/` open it too. Below 1024 px it is a search icon that opens the panel full-screen; the mobile menu has the same bar. "Contact" moved from the main navigation to the top bar to make room.
- **Panel:** `role=dialog`, focus trap, Esc closes, ↑↓ moves through results, Enter asks the question. States:
  1. **Empty:** 6 example questions + popular products.
  2. **Typing:** instant results grouped as Producten · Oplossingen · Kennisbank · Downloads · Sectoren. Search terms are highlighted and PDFs show as "PDF · p. N". "Stel deze vraag" sits at the top.
  3. **Answer:** streams word by word (`aria-busy`/`aria-live`) with clickable [n] citations. Then source cards (page section or PDF page), a product mini-card, the hand-off [Advies] [Gratis olieanalyse] [Bel], 3 follow-up questions and 👍/👎 feedback.
  4. **No reliable answer** (off-topic, prices, competitors): "Daar vind ik geen betrouwbaar antwoord op…" + referral to a specialist.
- **Disclaimer** always visible in the panel footer.
- **Prototype limits:** static index + 3 pre-written answers, built only on facts from the brief (BU-serie for injection moulding, water in gear oil, ISO 4406). Try the example questions.
- **Production:** Pagefind for instant search + `/api/ask` (SSE, Claude) with RAG over the pages and PDFs per page (see BRIEF §17.3).
- **Demo:** open the panel pre-filled with `?ask=<vraag>`.

## Pass 1.3: extra pages, animation and PDF search

**New pages (shared header/footer/search via `partials/` + `site.css` + `site.js`)**

- **`producten.html` (/nl/producten/, BRIEF §6.4):**
  - dark page hero with breadcrumb and answer-first intro;
  - **4-question selector** that slides in step by step with a live recommendation plus complementary series;
  - **filterable product list** with 10 series (filter chips, "Vergelijk" up to 3, which highlights rows in the table);
  - **comparison table** (HTML, sticky first column, D/V/W/L icons, links to the datasheets);
  - **downloads** for all 17 PDFs (ungated), with an embedded "Vraag het aan Triple R" field.
  - The TR-serie has no product photo on the current site, so it shows a placeholder.
- **`besparingscalculator.html` (/nl/besparingscalculator/, BRIEF §3.7):**
  - 7 inputs with sliders + number fields and 3 example profiles;
  - **assumptions in one config**, open for review and editing (all [CONFIRM]);
  - live result with count-up, KPIs (oil, CO₂, downtime), bars "Nu vs Met Triple R", optional payback period;
  - report form with validation (results are never behind the form);
  - methodology table;
  - sticky mini-total on mobile.
  - **Formula to align with the existing calculator [CONFIRM].**

**Animation (see design system → Motion):**
- hero intro;
- floating product with mouse parallax and a rotating orbit;
- reveal on scroll;
- counters and a growing bar chart;
- flowing oil in the cross-section;
- card spotlight;
- compact header + scroll progress bar;
- a zoom on the results photo.
Everything hangs off `html.motion` and is off under reduced motion; the resting state is always visible.

**"Vraag het aan Triple R" now also searches the PDFs**
- All 17 PDFs from the current site are in `pdf/`. When the panel is opened (or hovered), pdf.js (cdnjs, lazy) extracts the text **per page** → 28 searchable pages, cached in localStorage.
- **Instant search:** the "Downloads · in de PDF’s gevonden" group shows a snippet with highlighting and links to `pdf/file.pdf#page=N`.
- **Answers:**
  1. The 3 example answers cite the **real PDF page** where the fact appears.
  2. Other questions → **verbatim passages** from the datasheets (extractive, with page number). When a product is named, the search looks at its own datasheets first.
  3. Otherwise → "geen betrouwbaar antwoord".
- **NL → EN term expansion**, because the datasheets are English.
- **Production:** extraction happens at build time (Pagefind + a vector index per PDF page), and Claude writes a Dutch answer over the retrieved passages (BRIEF §17.3).
- **Note:** `se100e-bh.pdf` and `se100e-wh.pdf` are scans without a text layer → they need OCR at build time.

## Checks

- axe-core 4.10: **0 violations** on the homepage, producten and besparingscalculator (1440 and 390 px) and on the design system.
- No horizontal scroll at 390 px.
- Touch targets ≥ 44 px.
- Contrast for every text pair is on `design-system.html`.

## Notes for Astro

- **Almost everything is static HTML.** Islands:
  - search panel (on focus);
  - mega menu and drawer (vanilla, < 2 KB);
  - product finder (< 1 KB).
- **LCP:** the hero product photo. Preload it and set `fetchpriority=high`; convert to AVIF/WebP via `astro:assets`.
- **Product photos:** replace `mix-blend-mode` with properly background-removed PNG/WebP files on a fixed grey-50 background. That gives the same look without the blend trick.
- **[CONFIRM] items:** come from `src/data/facts.ts` with `confirm: true` → render the `.tb` marker; CI fails on production builds while any remain.
- **Finder logic:**
  - tank or > 1,000 l → OSCA;
  - engine oil → TR;
  - lubrication: up to 450 bar → SE, otherwise TR;
  - hydraulics: up to 450 bar → BU, otherwise SE.
  - Triple R must confirm these rules.

## Open review markers

1. Trust line about machine builders.
2. The 80% claim (vs 90%) and its source.
3. > 70% of machines running on contaminated oil.
4. > 50% shorter life from water.
5. 5–6× valve friction from varnish.
6. Source for the pump example.
7. The 4 results figures.
8. Case names and ISO values.
9. Oil analysis: turnaround time, scope and conditions.
10. Sustainability figures.
11. Logos in the trust strip.
12. Article author.
13. Element price.
14. Maxim's direct phone number.
15. Portrait photo (from the photo shoot).

## Next (pass 2, in this style)

- BU-serie page
- Scheepvaart sector page
- /gratis-olieanalyse/ landing page
- Advice form (3 steps)
- Mega menu + mobile nav in full
- "Vraag het aan Triple R" search panel with all states
- Components sheet


## Filtration Systembuilder (product configurator, pass 1.5)

This page (`filtration-systembuilder.html`) replaces the 4-question selector. It is modelled on oilcleaner.eu's "Build my oil cleaner", but avoids its dead ends and gives the visitor more feedback along the way.

**Name:** "Filtration Systembuilder" is used as the tool's brand name, marked `lang="en"`. The copy around it stays Dutch ("Vind uw oliereiniger", "Uw oliereiniger").
- **[CONFIRM] name and trademark use with Triple R:** it is very close to TRIS's "Build My Oil Cleaner".
- **[CONFIRM] EN/FR versions:** the brand name stays the same and only the explanatory copy is localised.

**Concept:** the visitor enters their own data and sees, live, which Triple R is assembled for them.

- **Hero demo:** a form that types itself field by field (fluid, volume, pressure, problem, at 45 ms per character with a caret). Then the assembled product appears ("Uw oliereiniger · op maat"). It cycles through 3 example cases (BU, OSCA, SE). Under reduced motion it is static, and it is hidden below 1024 px.
- **7 adaptive steps:**
  1. fluid;
  2. application (optional);
  3. system volume (log slider, number input, presets);
  4. ISO VG plus operating temperature, with a **live operating viscosity** via Walther/ASTM D341 and a gauge; skipped for coolant;
  5. connection, plus pressure only for a pressure line;
  6. problem (multi-select);
  7. installation, ATEX, and voltage (offline only).
- **Progress:** 7 numbered step buttons (`aria-current="step"`). Answered steps fill in and are clickable.
- **Live panel (sticky), "Uw oliereiniger":**
  - "Uw gegevens" (a `dl`, hidden on mobile because it repeats the form);
  - a **configuration code** (e.g. `RRR-HYD-0400-VG46/45C-P120-W-ANY`) that the customer quotes in their request; it is passed to the contact link as `?config=`;
  - the top 3 matches with score bars ("Samengesteld voor u").
- **Result:**
  - "Uw oliereiniger · xx% match" with `BU-serie met WE100`, the ✓ / ! / × reasons, the element, add-ons and alternatives;
  - CTAs to advice, the datasheet and the oil analysis;
  - a shareable URL and the event `product_selector_result`.
- **Never a dead end:** an "Uw installatie vraagt maatwerk" card plus a hand-off to a specialist.
- **Rules:** `P`, `evaluate()`, `element()` and `addons()` in the page script. **[CONFIRM] with Triple R:**
  - per-series viscosity, volume and pressure ranges;
  - application mapping;
  - element choice;
  - ATEX and wall-mount availability.
- **Astro:** build as a Preact island. Move the rules to `src/data/selector.ts` so they are shared with the header assistant (§17).

## Mobile layer (pass 1.6)

The mobile rules live in the last block of `site.css` (≤ 767 px). They make pages shorter and put less text on screen without removing content.

- Section padding drops to 48–64 px.
- **`.rail`:** a horizontal scroll-snap carousel at 78 % width, so the next card peeks in. Used for:
  - the homepage products;
  - the oplossingen contaminants;
  - the sectoren cases;
  - the olieanalyse measurements (`role="region"`, `tabindex="0"`).
- **`.four--compact` (homepage):** contaminants as a 2 × 2 grid with icon, title and key figure; the description is hidden.
- **Homepage hero:** the spec labels, the second promise and the second sentence of the intro (`.m-hide`) are hidden.
- **Product list:** compact rows (photo 104 px on the left, specs on the right); the description and tags are hidden.
- **Sectors:** 2 columns.
- **`[data-more="N"]` + site.js:** long lists show N items plus a "Toon alle (x)" button. Used for:
  - datasheets (5 of 17);
  - knowledge-base articles (4 of 12; a filter click opens the full list).
- **Result (390 px):** the homepage went from 9,382 to 6,810 px, producten from 15,017 to 9,011 px, with no horizontal scroll. axe (WCAG 2.2 AA) is clean on all 8 pages at 390 and 1440 px.

## Hero: Vraag het aan Triple R + reference carousel (pass 1.7)

- **`.heroask`:** a prominent conversational search in the right column of the homepage hero, visible without scrolling at 1440 × 900. It is a glass card with:
  - a white input;
  - suggestion chips;
  - a placeholder that types example questions (stops on focus, static under reduced motion).

  It uses the same `[data-ask-embed]` handler as the header, so it opens the answer panel with PDF passages. It replaces the spec labels (those figures are on the product pages).
- **Reference carousel (`.marquee`):** the list is rendered twice (the second copy `aria-hidden`) and scrolls at 40 s per loop, linear, with faded edges. It pauses on hover/focus. Under reduced motion it is static and wraps.
- **Results band fix:** the counter numbers inherited the caption style (`.results span`) and looked tiny next to "u" and "%". Now `.results div>span` is used for the caption and `.results b span` inherits the figure style.

## Calm-down pass (pass 1.8)

- **Header:**
  - no utility bar any more;
  - 5 menu items (Oplossingen, Producten, Sectoren, Diensten, Over ons);
  - language as a compact `NL` dropdown;
  - "Vraag het aan Triple R" as a short pill that only appears once the large search bar on the page is out of view (`.has-heroask` / `.heroask-gone`, site.js).
- **Copy rules:**
  - no em dashes (—) anywhere in the copy; table cells use "n.v.t.";
  - no eyebrow labels above section headings (only the brand name on the producten teaser remains);
  - no stat chips in subpage heroes.
- **Homepage:**
  - hero = H1, intro, 2 CTAs and the search card (3 example questions);
  - contaminant cards = icon, title, key figure;
  - product tiles without tag or specs, one button;
  - sectors = 6 text pills plus "Alle sectoren";
  - oil analysis = photo, heading, one sentence, button.
- **Oplossingen:** the fact list and the duplicated results band are removed.
- **Producten:** the downloads note is removed.
- **Kennisbank → FAQ:** `faq.html` replaces `kennisbank.html`; the 9 planned "in voorbereiding" articles have been dropped from the design.

## Contact button + hero (pass 1.9)

- **Contact button (`.fab`, in the footer partial):**
  - fixed at the bottom right of every page, on every screen size;
  - replaces the mobile bar with "Bel" and "Gratis olieanalyse";
  - opens a popup with 5 options: call, mail, free oil analysis, request advice, and Vraag het aan Triple R (which opens the answer panel);
  - it is a disclosure (`aria-expanded`): Esc or a click outside closes it, focus moves to the first option and returns to the button afterwards.
- **Header:** there is now 1.5–4 rem of space between the logo and the menu (≥ 1024 px).
- **Reference logos above the fold:**
  - on desktop, measured at 1440 × 900, 1366 × 768 and 1280 × 720;
  - on mobile, measured at 390 × 844 and 375 × 667;
  - on mobile, the logos come before the search card (flex order).
- **Video pause button removed at the client's request.** This fails WCAG 2.2.2 (Pause, Stop, Hide): video that autoplays for longer than 5 s needs a control. **[CONFIRM] a compliant alternative**, for example:
  - (a) the video plays once and stops on the last frame;
  - (b) a subtle pause control in the bottom corner of the hero;
  - (c) a still image instead of video.

  `prefers-reduced-motion` still shows only the poster image.

## Pass 1.11: quote request, network, rental, Systembuilder, Word copy

- **Header:**
  - menu: Oplossingen · Producten ▾ · Sectoren · Diensten ▾ (Gratis olieanalyse, Filtration Systembuilder, Verhuur, Besparingscalculator) · Netwerk · Over ons;
  - the main CTA is now **"Vraag het aan Triple R"** (blue gradient button) and replaces "Gratis olieanalyse". The free oil analysis stays in the hero, under Diensten and in the contact button;
  - a quote icon with a counter appears as soon as something is in the quote request.
- **Quote request (`offerte.html`)** ("winkelmandje" without prices):
  - "Voeg toe aan offerte" sits on every product tile, on the rental cards (type *huur*) and on the Systembuilder result. The Systembuilder adds its configuration code as a note.
  - The selection is stored per visitor in `localStorage` (`rrr-offerte-v1`). In production this becomes a cookie-free store or session storage.
  - On the quote page you can change quantities, add a note or remove an item. If there is a rental item, extra fields appear for the rental period and location.
  - **The selection is prefixed in the message field.**
  - Events: `quote_add` and `lead_offerte` (items as `id:type:quantity`). **[CONFIRM] add these to BRIEF §12.**
- **Netwerk (`netwerk.html`):**
  - Data lives in `data/dealers.json`. Locations and coordinates come from the map markers on triple-r-europe.com/contact (Oct 2026). Uddevalla and Reykjavik had no marker, so they use city coordinates.
  - **Company names are only filled in where a public source confirms them:**
    - Triple R Europe nv (HQ);
    - TRIPLE R Finland Oy AB (triple-r-europe.com/contact);
    - ITC Hydraulic Services Ltd, Inverurie (triple-r.co.uk).
  - The rest show as "Triple R <land>" with **[CONFIRM]**. TRIS B.V. (oilcleaner.eu) is deliberately left out: it is a separate European channel.
  - The map is our own SVG made from Natural Earth (npm world-atlas@2), built with `tools/mkmap.py`, so it needs no map service before consent.
  - Interaction: clicking a pin, country or list item zooms the map (700 ms) and shows a card; search filters both the list and the pins; "Heel Europa" resets the view.
- **Verhuur (`verhuur.html`):**
  - first selection: SE mobile, OSCA mobile, vacuum dehydrator **[CONFIRM]**;
  - "Huur aanvragen" puts the device in the quote request;
  - "Specifiek toestel" opens the quote page with a free-text line.
- **Filtration Systembuilder:** new name and URL for the configurator (`filtration-systembuilder.html`, previously Find My Oil Cleaner). On the homepage it is a striking button with a running border.
- **Homepage:**
  - the products are now a carousel of all 10 series (scroll-snap, arrows and a progress bar);
  - the "Vraag het aan Triple R" card has a glowing, rotating border (static under reduced motion).
- **Word copy:** see `copy/LEESMIJ.md`.
  - `copy/copytool.py export` writes all page copy (about 930 rows with an ID) to `copy/Triple-R-websiteteksten.docx`.
  - `copy/copytool.py import file.docx` writes the "Nieuwe tekst" column back into the sources and builds the site.

## Pass 1.12: catalogue per model, new datasheets, less whitespace

- **Catalogue per model:**
  - `tools/mkcatalog.py` writes `data/products.json` (the source for Astro content collections) and `catalog.js` (for the prototypes).
  - 73 products from the datasheets (46 systems in 12 series, 27 elements and pre-filters). Each product carries the article number, specs, fluid, version, oil volume from the datasheet selection chart, compatible elements, the systems an element fits, the datasheet page and [CONFIRM] notes.
- **Categories**, by installation method, inspired by oilcleaner.eu:
  - Op de drukleiding: BU, BU-100E-Wind, steel housings HP;
  - Bypass bij lage druk: TR, SS;
  - Offline met eigen pomp: SE, SE Mobile, OSCA;
  - Water verwijderen;
  - Lucht en schuim;
  - Koelvloeistof en proceswater;
  - Filterelementen.
- **`producten.html`:** category tabs plus filters (model or article-number search, oil volume, fluid, version, series), stored in the URL (`?cat=&serie=&vol=&q=`). Tiles are per model, grouped by series, with "Bekijk" and "Offerte".
- **`product.html?id=…`:** a prototype template; in Astro this becomes one static page per model. It includes:
  - breadcrumb Producten › category › series › model;
  - key facts and oil volume;
  - quantity plus quote button;
  - switcher to the other models in the series;
  - full spec table and series comparison table;
  - matching elements, or for an element, the systems it fits;
  - datasheet link with `#page=N`.
- **Everything else uses the same catalogue:**
  - the quote request (per model);
  - the Systembuilder, which recommends a concrete model by oil volume;
  - the assistant search, where every model and article number is indexed;
  - the mega menu.
- **New datasheets** (copied to `pdf/` and added to search and downloads):
  - V100-ENGLISH;
  - STEEL-housing-HP;
  - SE-Mobile-HF-ENGLISH;
  - Elements-ENGLISH;
  - Element-data-sheet-2023;
  - BU-100E-Wind-S (technical drawing, scanned).

  The other 8 attachments are byte-identical to PDFs already on the site.
- **[CONFIRM] found in the datasheets:**
  - **BU pressure:** the datasheet says flow is guaranteed from 10 to 245 bar; the brief says "tot 450 bar"; oilcleaner.eu says 315 bar.
  - **Steel housings HP:** page 1 says 25 bar, the table says 40 bar.
  - **M300 article numbers:** the 2023 data sheet (EL30004 / EL30025) and the element brochure (EL30008 for both) disagree.
  - **V100:** the datasheet says it fits all 100-size housings; the element brochure says it does not fit SU/SS housings.
  - **Missing data:** OSCA has no article numbers; SE100E-WH has only a 3D render; per-model product photos are missing (series photos are used for now).
  - **Element data sheet 2023** names competitors (CJC, Kleenoil) in its notice. [CONFIRM] whether it may be offered as a public download.
- **Whitespace:** `--section-y` went from 72–128 px to 56–88 px, `.head` margin from 40–64 px to 28–44 px, and the producten hero image is hidden on mobile.

## Pass 1.13: Marc, the digital assistant

- **Name:** "Vraag het Triple R" is now called **Marc** ("Vraag het aan Marc") everywhere:
  - header button;
  - hero card on the homepage and the FAQ;
  - answer panel;
  - contact button;
  - mobile menu;
  - search block on producten.
- **Face:** four poses cut from the supplied illustration (`img/marc/`, transparent PNG, 320–360 px wide), plus a round avatar (160 px):
  - `marc-denkt` (chin in hand, speech bubble): hero card, plus the empty panel ("Dag, ik ben Marc. Waarmee kan ik helpen?");
  - `marc-loep`: search state ("Marc zoekt in de webpagina's en datasheets…", gentle scan animation);
  - `marc-knipoog`: no reliable answer, hand-off to a specialist;
  - `marc-duim`: after "Nuttig" in the feedback ("Bedankt, dat hoort Marc graag!");
  - `marc-avatar`: header button, input field, answer heading, contact button.
- **AI transparency (EU AI Act art. 50):** Marc is always shown as an AI assistant: an "AI-assistent" badge, "Antwoord van Marc (AI)", and the footer line in the panel.
- **[CONFIRM]:**
  - consent from the person depicted to use the illustration as the bot's face;
  - in production, convert the images to WebP/AVIF (PNG is about 180–210 KB per pose).
- **Also fixed:**
  - the PDF index cache key is now `rrr-pdf-index-v2`, so the 6 new datasheets are indexed;
  - the example questions no longer use invalid listbox/option roles (keyboard navigation now uses `data-opt` + `.is-sel`);
  - the send button has an accessible name on mobile.

## Pass 1.14: Marc icon, product range per Triple R Europe

- **Marc icon:** the round face crop is gone. Every small spot now uses the full magnifying-glass pose (`img/marc/marc-icoon.png`, transparent, no circle):
  - header button (slightly larger than the button);
  - mobile search button;
  - input field in the panel;
  - answer heading;
  - contact button.
- **Product range adjusted to what Triple R Europe actually does** (compared with oilcleaner.eu):
  - **Added: category Vulpompen.** The SE200E Mobile High Flow is also listed there (`also: ['vullen']`). There is a placeholder "Vulpompen" with a [CONFIRM] request for models, article numbers, a photo and a datasheet.
  - **Not offered:** LS/LL series (the LL suction filter TR-21000 has been removed), Crystal Products desiccant breathers, spare parts.
  - **Options are handled differently and are not on the website:** the "Op aanvraag" rows have been removed from SE Mobile and SE200E-HF; the "Optie" mentions have been removed from rental, the mega menu and the assistant.
- **Photos:** the product photos on the site carry the Triple R/RRR brand (not TRIS). **[CONFIRM] the homepage hero video comes from TRIS** (oilcleaner.eu). Replace it with Triple R Europe's own footage or a still image.

## Pass 1.15: copy round 1 from Word, mobile density, filter fixes

- **Copy:** 34 changes from the client's Word document were applied via `copy/copytool.py import`. The main ones:
  - vacuümontwateraar → **vacuümdroger**, now also in the catalogue, menu and search synonyms;
  - Maxim Van Uytven → **Managing Director**;
  - "propere olie";
  - "drie soorten vervuiling" (the section still shows 4 cards; [CONFIRM]).
- **Reference carousel:** both lists are now identical (14 names). Typos fixed: "multinations" → "multinationals", "KMO's" → "kmo's".
  - "Apiroc" corrected to "Epiroc" (confirmed by the client).
  - **[CONFIRM]** logo permissions.
- **Mobile type scale:** `tokens.css` has a `max-width: 559px` block (display 36, h1 30, h2 26, h3 19, lead 16, body 15 px).
- **Marc icon** at 330 px for sharp retina display.
- **Pointer cursor** on the header button.
- **Catalogue:**
  - the filter fields used class `.kf`, which clashed with an old `.kf` (two columns) and is now `.kff`; the sidebar column is constrained to `minmax(0,1fr)`;
  - the category bar has scroll arrows and a faded edge when more tabs exist than fit;
  - long spec values in tiles now wrap.
- **Product photos:** the oilcleaner.eu photos all carry a "Triple R | TRIS" watermark. They are **not** used, and the watermark is not removed. Request the originals from TRIS or Triple R Japan.
