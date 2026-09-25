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

## Homepage structure

1. **Header:** a dark utility bar (38 px: HQ, phone, email, Word dealer, NL/EN/FR) above one white header row (76 px, blurred background) with the logo, navigation (pill hover), a "Vraag het Triple R" search pill and the primary CTA; the mega menu opens under Producten.
2. **Hero:** H1 + lead + 2 CTAs + 2 check lines. BU-serie product photo in the "studio" with 3 spec labels. Below it, a trust strip with reference names.
3. **Problem (dark):** the 80% claim + 3 facts, a bar chart to scale (3,000 vs 15 kg), and a key-figures row: 114 mm · 1–10 µm · < 100 ppm · up to 95%.
4. **Four contaminants:** 4 cards with icons on blue-50, specs and links to the solution pages.
5. **How it works:** technical cross-section of 114 mm with 3 layers + numbered steps.
6. **Products:** 6 tiles with a real photo and 2 specs; link to "Vergelijk alle 10 series".
7. **Product finder:** 3 native selects → live recommendation + CTA.
8. **Results:** 4 key figures on a full-bleed photo of clean oil.
9. **Sectors:** atmospheric photo + 12 links in 2 columns with line icons.
10. **Cases:** 3 cards with an ISO before/after table (values are layout examples).
11. **Free oil analysis:** lab photo + 4 steps + CTA.
12. **Sustainability:** Reduce · Reuse · Recycle, CO₂ example calculation, element-change photo.
13. **Knowledge base + FAQ.**
14. **Closing CTA (logo gradient):** Maxim Van Uytven's contact details with the team photo.
15. **Footer:** full company details + KBO/BTW BE 0448.276.293.
16. **Mobile:** a sticky [Bel] [Gratis olieanalyse] bar below 768 px.

## "Vraag het Triple R": conversational search (BRIEF §17)

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
  - **downloads** for all 17 PDFs (ungated), with an embedded "Vraag het Triple R" field.
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

**"Vraag het Triple R" now also searches the PDFs**
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
- "Vraag het Triple R" search panel with all states
- Components sheet
