# Triple R Europe website — project rules for Claude Code

## Mission
Dutch-first (Belgian Dutch, "u"), NL/EN/FR B2B website for Triple R Europe nv (bypass oil filtration, Aartselaar BE).
Primary KPI: qualified leads — "Gratis olieanalyse" and "Advies aanvragen". Full brief: docs/BRIEF.md (always read it first).

## Non-negotiables
- Never modify or deploy to the live site/domain without explicit approval. Work on staging. Keep backups (docs/BRIEF.md §15 phase 0).
- Ask before deleting files or changing redirects/DNS.
- Never invent facts, figures, customers, certificates or quotes. Use src/data/facts.ts; unknowns → visible [CONFIRM] placeholder + entry in docs/open-questions.md.
- Every page: one H1, answer-first intro (40–60 words), title ≤ 60 chars, meta description ≤ 155 chars, canonical, hreflang, JSON-LD, OG image, breadcrumb, contextual CTA.
- No noindex on production content pages. Staging gets X-Robots-Tag: noindex via host headers only.
- Native copy per language; no literal translations; no English on NL pages.
- Performance budget: LCP < 2.0s, CLS < 0.05, INP < 200ms, Lighthouse ≥ 95 (all four).
- WCAG 2.2 AA. Respect prefers-reduced-motion.
- No third-party requests (analytics, maps, video, fonts) before cookie consent.
- Header assistant (BRIEF §17): answers only from own pages/PDFs, always cites sources (PDF links with #page=N), never invents specs/prices, hands off to lead forms. Re-index on every deploy.

## Stack
Astro + TypeScript (strict) + Content Collections (MDX/Zod) + Tailwind (tokens from design) + islands (Preact/vanilla) + serverless /api/lead + /api/ask (Claude RAG) + Pagefind + Turnstile. Hosting: [Netlify|Vercel|Cloudflare — CONFIRM].

## Conventions
- Content ids shared across locales; slugs per locale (see BRIEF §5).
- Components: src/components/seo/{Meta,Hreflang,JsonLd,Breadcrumbs}.astro
- Lead events: see BRIEF §12 (exact names).
- Run `npm run check` (types, lint, html-validate, links, axe, Lighthouse CI) before saying a task is done.
- Stop after each phase (BRIEF §15) and summarise what changed + what needs review.

## Design (pass 1, approved direction pending)
- Visual design + prototypes live in `design/` — open `design/homepage.html`, `design/producten.html`, `design/besparingscalculator.html`, `design/design-system.html` (serve the folder over http, e.g. `python3 -m http.server --directory design`, so the PDF search works).
- Tokens: `design/tokens.css` (source of truth) and `design/tailwind.tokens.cjs`. Build notes, animation spec and open [CONFIRM] items: `design/HANDOFF.md`.
- Treat `design/` as reference, not as production code: rebuild components in Astro per BRIEF §11.

