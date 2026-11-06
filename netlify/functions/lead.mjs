// /api/lead: valideert een aanvraag, bewaart ze altijd en mailt ze via Mailgun.
// Zonder MAILGUN_API_KEY wordt niets verstuurd (veilig op staging); de lead blijft bewaard.
import { getStore } from '@netlify/blobs';

const env = k => process.env[k] || '';
const TO = () => env('LEAD_TO') || 'maxim.vanuytven@triple-r-europe.com';
const BCC = () => env('LEAD_BCC') || 'marc.vanuytven@triple-r-europe.com';
const FI_TO = () => env('LEAD_FI_TO') || 'sf.edustus@co.inet.fi';
const FROM = () => env('MAIL_FROM') || 'Triple R Europe <email@mailserver-mailbox-marketing.be>';
const DOMAIN = () => env('MAILGUN_DOMAIN') || 'mail.mailserver-mailbox-marketing.be';
const TYPES = { olieanalyse: 'Gratis olieanalyse', offerte: 'Offerteaanvraag', besparing: 'Besparingsrapport', contact: 'Contact' };
const FREEMAIL = /@(gmail|hotmail|outlook|live|yahoo|icloud|telenet|skynet|proximus|gmx|orange|free|wanadoo)\./i;

const REPLY = {
  nl: { s: 'We hebben uw aanvraag ontvangen', b: 'Bedankt voor uw aanvraag bij Triple R Europe. Een specialist neemt contact met u op. Dringend? Bel +32 (0)3 825 46 47.', o: 'Waar neemt u een oliestaal? Bij draaiende machine, op een vast punt in de retourleiding of tank, in een schone fles.' },
  en: { s: 'We have received your request', b: 'Thank you for your request to Triple R Europe. A specialist will contact you. Urgent? Call +32 (0)3 825 46 47.', o: 'Where to take an oil sample? With the machine running, at a fixed point in the return line or tank, in a clean bottle.' },
  fr: { s: 'Nous avons bien reçu votre demande', b: 'Merci pour votre demande à Triple R Europe. Un spécialiste vous contactera. Urgent ? Appelez le +32 (0)3 825 46 47.', o: "Où prélever un échantillon d'huile ? Machine en marche, à un point fixe de la conduite de retour ou du réservoir, dans un flacon propre." },
};

const str = (v, n = 500) => String(v ?? '').replace(/[\r\0]/g, '').slice(0, n).trim();
const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

export function allowedOrigin(origin, site = env('URL')) {
  if (!origin) return false;
  try {
    const h = new URL(origin).hostname;
    return h === 'www.triple-r-europe.com' || h === 'triple-r-europe.com' || h === 'localhost' || h === '127.0.0.1' || h.endsWith('.netlify.app') || (site && h === new URL(site).hostname);
  } catch { return false; }
}

export function clean(d) {
  const fields = (Array.isArray(d.fields) ? d.fields : []).slice(0, 40).map(f => ({ label: str(f?.label, 120), value: str(f?.value, 2000) })).filter(f => f.label && f.value);
  const extra = Object.fromEntries(Object.entries(d.extra && typeof d.extra === 'object' ? d.extra : {}).slice(0, 5).map(([k, v]) => [str(k, 60), str(v, 4000)]));
  const utm = Object.fromEntries(Object.entries(d.utm && typeof d.utm === 'object' ? d.utm : {}).slice(0, 8).map(([k, v]) => [str(k, 30), str(v, 200)]));
  return { type: str(d.type, 20), lang: ['nl', 'en', 'fr'].includes(d.lang) ? d.lang : 'nl', page: str(d.page, 300), referrer: str(d.referrer, 300), email: str(d.email, 200), name: str(d.name, 120), company: str(d.company, 160), phone: str(d.phone, 40), country: str(d.country, 80), message: str(d.message, 4000), consent: d.consent === true, newsletter: d.newsletter === true, fields, extra, utm };
}

export function validate(d, raw) {
  if (raw.website) return 'spam';
  if (typeof raw.elapsed === 'number' && raw.elapsed < 3000) return 'spam';
  if (!TYPES[d.type]) return 'type';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.email)) return 'email';
  if (!d.consent) return 'consent';
  if ((`${d.message} ${d.fields.map(f => f.value).join(' ')}`.match(/https?:\/\//g) || []).length > 3) return 'spam';
  return '';
}

// BRIEF §3.6: score in het onderwerp, zodat sales de prioriteit meteen ziet
export function score(d) {
  const all = `${d.fields.map(f => `${f.label} ${f.value}`).join(' ')} ${d.message}`;
  let s = 3;
  if (/(1\.000|10\.000|1,000|10,000|1 000|10 000)/.test(all)) s += 2;
  if (/dringend|urgent/i.test(all)) s += 2;
  if (/servo|proportion/i.test(all)) s += 2;
  s += Math.min(3, (all.match(/varnish|vernis|water|eau|deeltjes|particle|particule|schuim|foam|mousse/gi) || []).length);
  if (FREEMAIL.test(d.email)) s -= 3;
  return Math.max(0, Math.min(10, s));
}

export const isFinland = d => /^(fi|finland|finlande|suomi)$/i.test(d.country.trim());

export function route(d) {
  return isFinland(d) ? { to: FI_TO(), bcc: TO() } : { to: TO(), bcc: BCC() };
}

export function render(d, sc) {
  const lines = [`${TYPES[d.type]} (${d.lang.toUpperCase()}), score ${sc}/10`, '', `Naam: ${d.name}`, `Bedrijf: ${d.company}`, `E-mail: ${d.email}`, `Telefoon: ${d.phone}`, `Land: ${d.country}`, ''];
  d.fields.forEach(f => lines.push(`${f.label}: ${f.value}`));
  Object.entries(d.extra).forEach(([k, v]) => lines.push('', `${k}:`, v));
  lines.push('', `Pagina: ${d.page}`, `Verwijzer: ${d.referrer}`, `Nieuwsbrief: ${d.newsletter ? 'ja' : 'nee'}`);
  Object.entries(d.utm).forEach(([k, v]) => lines.push(`${k}: ${v}`));
  return lines.join('\n');
}

async function mail(p) {
  const key = env('MAILGUN_API_KEY');
  if (!key) return false;
  const body = new URLSearchParams(p);
  const r = await fetch(`https://api.eu.mailgun.net/v3/${DOMAIN()}/messages`, { method: 'POST', headers: { Authorization: 'Basic ' + Buffer.from('api:' + key).toString('base64') }, body });
  if (!r.ok) throw new Error('mailgun ' + r.status);
  return true;
}

export default async req => {
  if (req.method !== 'POST') return json(405, { ok: false });
  if (!allowedOrigin(req.headers.get('origin'))) return json(403, { ok: false });
  let raw;
  try { raw = await req.json(); } catch { return json(400, { ok: false }); }
  const d = clean(raw), err = validate(d, raw);
  if (err === 'spam') return json(200, { ok: true }); // bots krijgen geen aanwijzing
  if (err) return json(422, { ok: false, error: err });
  const sc = score(d), id = `${new Date().toISOString()}-${Math.random().toString(36).slice(2, 8)}`;
  let stored = false, sent = false;
  try { await getStore('leads').setJSON(id, { ...d, score: sc }); stored = true; } catch (e) { console.error('lead-opslag mislukt', e.message); }
  const { to, bcc } = route(d);
  try {
    sent = await mail({ from: FROM(), to, bcc, 'h:Reply-To': d.email, subject: `[LEAD ${sc}/10] ${TYPES[d.type]} – ${d.company || d.name}`, text: render(d, sc) });
    if (sent) {
      const r = REPLY[d.lang];
      await mail({ from: FROM(), to: d.email, 'h:Reply-To': 'info@triple-r-europe.com', subject: r.s, text: `${r.b}${d.type === 'olieanalyse' ? '\n\n' + r.o : ''}\n\nTriple R Europe nv\nCleydaellaan 16, unit 8, 2630 Aartselaar, België` });
    }
  } catch (e) { console.error('mail mislukt', e.message); }
  if (env('LEAD_WEBHOOK_URL')) { try { await fetch(env('LEAD_WEBHOOK_URL'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...d, score: sc }) }); } catch (e) { console.error('webhook mislukt', e.message); } }
  if (!stored && !sent) return json(502, { ok: false });
  return json(200, { ok: true });
};
