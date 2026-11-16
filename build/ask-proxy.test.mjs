// Test van netlify/edge-functions/ask.js zonder netwerk (met een nagebootste backend).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { handle, scrub, cleanAsk, cleanFeedback } from '../netlify/edge-functions/ask.js';

const ENV = o => k => o[k] || '';
const ON = ENV({ ASK_BACKEND_URL: 'https://cockpit.kigumi.be/api', ASK_BACKEND_TOKEN: 'tok' });
const req = (path, body, h = {}) => new Request('https://triplereurope.netlify.app' + path, { method: 'POST', headers: { 'Content-Type': 'application/json', ...h }, body: typeof body === 'string' ? body : JSON.stringify(body) });
const sample = JSON.parse(readFileSync(new URL('./fixtures/kigumi-voorbeeldantwoorden.json', import.meta.url)));

// persoonsgegevens eruit
assert.equal(scrub('mail jan@firma.be of bel +32 3 825 46 47'), 'mail [e-mail] of bel [telefoon]');
assert.equal(scrub('BU200E bij 350 bar, 4,0 l/min'), 'BU200E bij 350 bar, 4,0 l/min', 'gewone getallen blijven');
assert.equal(cleanAsk({ question: '  ' }), null);
assert.equal(cleanAsk({ question: 'x'.repeat(900) }).question.length, 500);
assert.equal(cleanAsk({ question: 'q', lang: 'xx' }).lang, 'nl');
assert.equal(cleanAsk({ question: 'q', history: Array(9).fill({ role: 'user', content: 'a' }) }).history.length, 6);
assert.equal(cleanAsk({ question: 'q', page: 'https://evil.example/' }).page, '');
assert.equal(cleanFeedback({ answer_id: 'ans_ad2b78704902411e9cfa', rating: 'up' }).rating, 'up');
assert.equal(cleanFeedback({ answer_id: 'x', rating: 'up' }), null);

// uitgeschakeld / niet ingesteld
assert.equal((await handle(req('/api/ask', { question: 'q' }), ENV({}))).status, 503);
assert.equal((await handle(req('/api/ask', { question: 'q' }), ENV({ ASK_BACKEND_URL: 'https://x', ASK_BACKEND_TOKEN: 't', ASSISTANT_ENABLED: 'false' }))).status, 503);
// alleen POST en alleen de eigen site
assert.equal((await handle(new Request('https://triplereurope.netlify.app/api/ask'), ON)).status, 405);
assert.equal((await handle(req('/api/ask', { question: 'q' }, { Origin: 'https://evil.example' }), ON)).status, 403);
assert.equal((await handle(req('/api/ask', '{kapot'), ON)).status, 400);

// doorsturen: juiste URL, token, gefilterde body; antwoord ongewijzigd terug
let seen;
const backend = (status, body, headers = {}) => async (url, init) => { seen = { url, init }; return new Response(status === 204 ? null : typeof body === 'string' ? body : JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', ...headers } }); };
let r = await handle(req('/api/ask', { question: 'Werkt de BU200E nog bij 350 bar? Mail me op a@b.be', lang: 'nl', page: '/nl/producten/bu200e/', session_id: 'abcdef1234' }), ON, backend(200, sample[0].response));
assert.equal(seen.url, 'https://cockpit.kigumi.be/api/v1/ask');
assert.equal(seen.init.headers.Authorization, 'Bearer tok');
assert.ok(!JSON.parse(seen.init.body).question.includes('a@b.be'));
assert.equal(r.status, 200);
assert.equal((await r.json()).answer_id, sample[0].response.answer_id);

// stroom: Accept wordt doorgegeven, inhoud ongewijzigd
const sse = 'event: meta\ndata: {"answer_id":"ans_x1234567"}\n\nevent: done\ndata: {"no_answer":false}\n\n';
r = await handle(req('/api/ask', { question: 'q' }, { Accept: 'text/event-stream' }), ON, backend(200, sse, { 'Content-Type': 'text/event-stream' }));
assert.equal(seen.init.headers.Accept, 'text/event-stream');
assert.equal(r.headers.get('content-type'), 'text/event-stream');
assert.equal(await r.text(), sse);

// fouten: code door, boodschap niet; Retry-After door
r = await handle(req('/api/ask', { question: 'q' }), ON, backend(429, { code: 'rate_limited', message: 'intern detail' }, { 'Retry-After': '30' }));
assert.equal(r.status, 429); assert.equal(r.headers.get('retry-after'), '30');
assert.deepEqual(await r.json(), { code: 'rate_limited' });
r = await handle(req('/api/ask', { question: 'q' }), ON, async () => { throw new Error('timeout'); });
assert.equal(r.status, 504);

// feedback
r = await handle(req('/api/ask/feedback', { answer_id: 'ans_ad2b78704902411e9cfa', rating: 'down', comment: 'klopt niet, bel 0475 12 34 56' }), ON, backend(204, ''));
assert.equal(seen.url, 'https://cockpit.kigumi.be/api/v1/feedback');
assert.ok(JSON.parse(seen.init.body).comment.includes('[telefoon]'));
assert.equal(r.status, 204);

console.log('ask-proxy: alle tests geslaagd');
