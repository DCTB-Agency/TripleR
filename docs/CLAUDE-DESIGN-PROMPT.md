# Claude Design — prompt for Triple R Europe (paste as-is, attach TRIPLE-R_WEBSITE-BRIEF.md)

You are the lead designer for the new website of **Triple R Europe nv** (Aartselaar, Belgium) — makers of bypass / off-line oil purification systems and 3-in-1 filter elements that remove **solid particles, varnish, water and air** from industrial oil. Read the attached brief fully (sections 1, 3, 4, 5 and 6 matter most for design).

## Goal
A Dutch-first (Belgian Dutch, "u"), B2B website that feels like a premium engineering brand — not a generic industrial template — and converts maintenance managers, marine engineers and dealers into leads. The two primary conversions are **"Gratis olieanalyse"** and **"Advies aanvragen"**.

## Brand constraints
- **Keep the existing Triple R logo and brand colours** (logo: https://www.triple-r-europe.com/wp-content/uploads/2023/10/mark_horizon_color.svg — use its exact colours as the primary palette).
- Everything else is open: typography, layout, imagery treatment, illustration, motion, supporting neutrals and accents (accents must harmonise with the logo colours).
- Only the images from the current website are available → design with product cut-outs on consistent backdrops, custom line illustrations/diagrams and data visuals. No fake stock "customers".

## Creative concept: "Zie het verschil — clean oil, made visible"
The site tells one story: from dark, contaminated oil to clear, clean oil.
- Hero: macro oil visual that clears up on scroll; the 4 contaminants (deeltjes, varnish, water, lucht) appear and get "caught".
- Signature: a tall scroll-driven cross-section of the **114 mm filter element** with its 3 filtration stages; reuse its strata lines as a graphic motif.
- Data as design: large mono-type numbers (ISO 4406 codes like 21/18/16 → 15/13/10, "3.000 kg vs 15 kg vuil per jaar"), an interactive ISO-cleanliness slider.
- Dark sections = problem; light sections = solution. WCAG AA contrast everywhere. Motion is subtle and respects reduced-motion.
- Tone: expert, direct, concrete, numbers with units.

## Deliverables (desktop 1440 + mobile 390 for each)
1. **Design system:** colour tokens (from logo + neutrals + one accent), type scale (heading grotesk + mono for data), spacing, grid, radii, shadows, icon style (line), illustration style, button/link/input states, motion principles.
2. **Homepage** — sections as in brief §6.1 (hero with H1 "Stop met olie verversen. Begin met olie reinigen.", problem data, 4 contaminants, filter cross-section, benefits, product-finder teaser, sectors grid, cases, free-analysis process, sustainability Reduce·Reuse·Recycle, logo wall, FAQ, final CTA with contact person).
3. **Product page — BU-serie** (brief §6.3): hero with product cut-out + spec chips, how-it-works diagram (BU on the high-pressure line), spec table, compatible elements, sectors, downloads, FAQ, sticky mobile CTA bar [Bel] [Gratis olieanalyse] [Advies].
4. **Sector page — Scheepvaart** (brief §6.5): vessel-type list, applications (motoren, thrusters, kranen, lieren), recommended products, references, ATEX note, sector-prefilled CTA.
5. **Landing page — /nl/gratis-olieanalyse/** (brief §6.6): minimal header (logo + phone), form step 1 above the fold, what's measured, sample report preview, 4-step process, trust, FAQ.
6. **Multi-step form "Advies aanvragen"** (brief §3.4): 3 steps with progress bar, validation/error states, success/thank-you screen.
7. **Mega menu + mobile navigation** (Oplossingen · Producten · Sectoren · Diensten · Kennisbank · Over ons · Contact; conversational search bar; phone + "Gratis olieanalyse" button; NL/EN/FR switch).
8. **Conversational search "Vraag het Triple R"** (brief §17): header search bar (desktop) + icon/full-screen panel (mobile); states: empty (suggested questions), typing (instant grouped results: Producten, Oplossingen, Kennisbank, Downloads with "PDF · p. 3", Sectoren), streaming AI answer with numbered source cards (page sections and PDF pages), inline mini product cards, follow-up suggestions, "no reliable answer" state, feedback 👍/👎, and the hand-off CTAs [Vraag advies] [Gratis olieanalyse] [Bel]. Plus the AI disclaimer line.
9. **Components sheet:** product card, comparison table, "Welke filter past?" selector (4 questions → result), case card (ISO before/after), stats band, process steps, FAQ accordion, author box, breadcrumbs, 3 CTA block variants, footer (full company details incl. KBO/BTW BE 0448.276.293).

## Real content to use (don't use lorem ipsum)
- Triple R Europe nv · Cleydaellaan 16, unit 8, 2630 Aartselaar · +32 (0)3 825 46 47 · info@triple-r-europe.com
- Products: Filterelementen, BU-serie, SE-serie, TR-serie, OSCA-serie, WS-serie, Quicktoron, SS-serie, Vacuümontwateraar, Centrifuges
- Sectors: Hydraulische systemen, Scheepvaart, Windenergie, Energie, Petrochemie, Staal & metaal, Papierindustrie, Automobielindustrie, Bouwmachines, Transport, Spoorwegen, Luchtvaart
- Claims needing client confirmation must be visibly marked **[CONFIRM]** (e.g. "tot 80% van de storingen", "olielevensduur tot 50.000 uur", "tot 90% lagere oliekosten").

## Output for handoff to Claude Code
Export the design tokens (CSS variables / Tailwind config), component specs with states, spacing and breakpoints, and annotated screens so Claude Code can build it in Astro exactly. Note every animation's trigger, duration and easing, plus the static fallback.
