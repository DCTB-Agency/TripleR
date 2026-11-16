// /api/ask en /api/ask/feedback: beveiligde doorgeefschakel naar de AI-backend van Marc (Kigumi).
// Edge Function, zodat een gestreamd antwoord tot 35 s mag duren (Kigumi vraagt minstens 30 s).
// De token staat alleen hier (omgevingsvariabele), nooit in de browser. Zie docs/marc-ai-backend-brief.md §2, §3 en §11.
//
// Omgevingsvariabelen (Netlify > Site configuration > Environment variables):
//   ASK_BACKEND_URL     https://cockpit.kigumi.be/api
//   ASK_BACKEND_TOKEN   token van Kigumi (Bearer)
//   ASSISTANT_ENABLED   "false" = kill switch: de site valt terug op de gewone zoekfunctie

const LANGS = ['nl', 'en', 'fr', 'de', 'it', 'es', 'fi', 'hu', 'sv', 'no'];
const TIMEOUT_MS = 35000;
const MAX_BODY = 16 * 1024;

const json = (status, body, extra = {}) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', ...extra } });

// e-mailadressen en telefoonnummers nooit doorsturen (§6, §11.1 regel 9)
export function scrub(s) {
  return String(s ?? '')
    .replace(/[^\s@<>()]+@[^\s@<>()]+\.[a-z]{2,}/gi, '[e-mail]')
    .replace(/(?:\+|00)\d[\d ()./-]{7,}\d|\b0\d[\d ()./-]{6,}\d\b/g, '[telefoon]');
}

const str = (v, max) => (typeof v === 'string' ? v.trim().slice(0, max) : '');

export function cleanAsk(b) {
  const question = scrub(str(b.question, 500));
  if (!question) return null;
  const lang = LANGS.includes(b.lang) ? b.lang : 'nl';
  const page = /^\/[\w\-./%]*$/.test(b.page || '') ? b.page.slice(0, 300) : '';
  const session_id = /^[\w-]{8,64}$/.test(b.session_id || '') ? b.session_id : undefined;
  const history = (Array.isArray(b.history) ? b.history : [])
    .filter(m => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string')
    .slice(-6)
    .map(m => ({ role: m.role, content: scrub(m.content.slice(0, 2000)) }));
  return { question, lang, page, session_id, history };
}

export function cleanFeedback(b) {
  if (!/^ans_[a-z0-9]{6,64}$/i.test(b.answer_id || '') || !['up', 'down'].includes(b.rating)) return null;
  const out = { answer_id: b.answer_id, rating: b.rating };
  const c = scrub(str(b.comment, 500));
  if (c) out.comment = c;
  return out;
}

// Alleen aanvragen van de eigen site (geen open proxy voor derden)
export function sameOrigin(req) {
  const o = req.headers.get('origin');
  if (!o) return true;
  try { return new URL(o).host === new URL(req.url).host; } catch { return false; }
}

export async function handle(req, env, doFetch = fetch) {
  if (req.method !== 'POST') return json(405, { code: 'method_not_allowed' }, { Allow: 'POST' });
  if (!sameOrigin(req)) return json(403, { code: 'forbidden' });
  const base = (env('ASK_BACKEND_URL') || '').replace(/\/$/, '');
  const token = env('ASK_BACKEND_TOKEN');
  if (env('ASSISTANT_ENABLED') === 'false' || !base || !token || !/^https:\/\//.test(base)) return json(503, { code: 'disabled' });
  const raw = await req.text();
  if (raw.length > MAX_BODY) return json(413, { code: 'bad_request' });
  let body;
  try { body = JSON.parse(raw); } catch { return json(400, { code: 'bad_request' }); }
  const isFeedback = new URL(req.url).pathname.replace(/\/$/, '').endsWith('/feedback');
  const payload = isFeedback ? cleanFeedback(body) : cleanAsk(body);
  if (!payload) return json(400, { code: 'bad_request' });
  const stream = !isFeedback && (req.headers.get('accept') || '').includes('text/event-stream');
  let up;
  try {
    up = await doFetch(`${base}/v1/${isFeedback ? 'feedback' : 'ask'}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', Accept: stream ? 'text/event-stream' : 'application/json' },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch (e) {
    return json(504, { code: 'timeout' });
  }
  if (isFeedback) return new Response(null, { status: up.ok ? 204 : up.status });
  if (!up.ok) {
    let code = 'internal';
    try { code = (await up.json()).code || code; } catch { /* lege of ongeldige foutbody */ }
    const extra = up.headers.get('retry-after') ? { 'Retry-After': up.headers.get('retry-after') } : {};
    return json(up.status, { code }, extra); // 'message' van de backend is niet voor de bezoeker
  }
  const type = up.headers.get('content-type') || (stream ? 'text/event-stream' : 'application/json');
  return new Response(up.body, { status: 200, headers: { 'Content-Type': type, 'Cache-Control': 'no-store', 'X-Accel-Buffering': 'no' } });
}

export default async req => handle(req, k => (globalThis.Netlify?.env?.get(k) ?? ''));

export const config = { path: ['/api/ask', '/api/ask/feedback'], method: ['POST'] };
