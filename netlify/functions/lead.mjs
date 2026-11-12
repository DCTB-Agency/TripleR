// /api/lead: valideert een aanvraag, bewaart ze altijd en mailt ze via Mailgun.
// Zonder MAILGUN_API_KEY wordt niets verstuurd (veilig op staging); de lead blijft bewaard.
import { getStore } from '@netlify/blobs';

const env = k => process.env[k] || '';
const TO = () => env('LEAD_TO') || 'maxim.vanuytven@triple-r-europe.com';
const BCC = () => env('LEAD_BCC') || 'info@triple-r-europe.com';
const FI_TO = () => env('LEAD_FI_TO') || 'sf.edustus@co.inet.fi';
const FROM = () => env('MAIL_FROM') || 'Triple R Europe <email@mailserver-mailbox-marketing.be>';
const DOMAIN = () => env('MAILGUN_DOMAIN') || 'mail.mailserver-mailbox-marketing.be';
const TYPES = { olieanalyse: 'Gratis olieanalyse', offerte: 'Offerteaanvraag', besparing: 'Besparingsrapport', contact: 'Contact', sollicitatie: 'Sollicitatie', marc: 'Vraag via Marc (AI-assistent)' };
const JOBS_TO = () => env('JOBS_TO') || 'info@triple-r-europe.com';
const CV_MAX = 4 * 1024 * 1024;
const FREEMAIL = /@(gmail|hotmail|outlook|live|yahoo|icloud|telenet|skynet|proximus|gmx|orange|free|wanadoo)\./i;

const SITE = () => env('URL') || 'https://www.triple-r-europe.com';
const LOGO = () => env('MAIL_LOGO') || `${SITE()}/assets/img/mail-logo.png`;
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// Bevestiging aan de klant. Bewust zonder ingevulde vrije tekst, zodat niemand het formulier kan gebruiken om via ons berichten naar derden te sturen.
const REPLY = {
  nl: { hi: n => (n ? `Beste ${n},` : 'Beste,'), s: { olieanalyse: 'We hebben uw aanvraag voor een gratis olieanalyse ontvangen', offerte: 'We hebben uw offerteaanvraag ontvangen', besparing: 'We hebben uw rapportaanvraag ontvangen', contact: 'We hebben uw bericht ontvangen', sollicitatie: 'We hebben uw sollicitatie ontvangen', marc: 'We hebben uw vraag ontvangen' },
    b: { olieanalyse: 'Bedankt voor uw aanvraag. Een specialist van Triple R neemt contact met u op over de staalname.', offerte: 'Bedankt voor uw aanvraag. Een specialist bekijkt uw selectie en bezorgt u een offerte op maat van uw installatie.', besparing: 'Bedankt voor uw aanvraag. Een specialist bezorgt u het rapport met uw waarden en aannames.', contact: 'Bedankt voor uw bericht. Een specialist van Triple R neemt contact met u op.', marc: 'Bedankt voor uw vraag. Marc vond er geen betrouwbaar antwoord op in onze documentatie, daarom bezorgen we ze aan een specialist van Triple R. Die neemt contact met u op.', sollicitatie: 'Bedankt voor uw sollicitatie bij Triple R Europe. Maxim Van Uytven bekijkt ze en neemt contact met u op.' },
    h: 'Zo gaat het verder', steps: ['U ontvangt een staalnamekit met uitleg, of we plannen een bezoek.', 'Het labo analyseert uw staal.', 'U krijgt het rapport met concreet advies.'], th: 'Waar neemt u een oliestaal?', tip: 'Bij draaiende machine, op een vast punt in de retourleiding of tank, in een schone fles.', u: 'Dringend? Bel ons op', cta: 'Bezoek onze website', bye: 'Met vriendelijke groeten,', team: 'Het team van Triple R Europe', legal: 'U ontvangt deze e-mail omdat u een formulier invulde op onze website.', c: 'België' },
  en: { hi: n => (n ? `Dear ${n},` : 'Hello,'), s: { olieanalyse: 'We have received your free oil analysis request', offerte: 'We have received your quote request', besparing: 'We have received your report request', contact: 'We have received your message', sollicitatie: 'We have received your application', marc: 'We have received your question' },
    b: { olieanalyse: 'Thank you for your request. A Triple R specialist will contact you about the oil sample.', offerte: 'Thank you for your request. A specialist will review your selection and send you a quote tailored to your installation.', besparing: 'Thank you for your request. A specialist will send you the report with your values and assumptions.', contact: 'Thank you for your message. A Triple R specialist will contact you.', marc: 'Thank you for your question. Marc could not find a reliable answer in our documentation, so we have passed it on to a Triple R specialist, who will contact you.', sollicitatie: 'Thank you for applying to Triple R Europe. Maxim Van Uytven will review your application and contact you.' },
    h: 'What happens next', steps: ['You receive a sampling kit with instructions, or we schedule a visit.', 'The lab analyses your sample.', 'You receive the report with practical advice.'], th: 'Where to take an oil sample?', tip: 'With the machine running, at a fixed point in the return line or tank, in a clean bottle.', u: 'Urgent? Call us on', cta: 'Visit our website', bye: 'Kind regards,', team: 'The Triple R Europe team', legal: 'You are receiving this email because you filled in a form on our website.', c: 'Belgium' },
  fr: { hi: n => (n ? `Bonjour ${n},` : 'Bonjour,'), s: { olieanalyse: "Nous avons bien reçu votre demande d'analyse d'huile gratuite", offerte: 'Nous avons bien reçu votre demande de devis', besparing: 'Nous avons bien reçu votre demande de rapport', contact: 'Nous avons bien reçu votre message', sollicitatie: 'Nous avons bien reçu votre candidature', marc: 'Nous avons bien reçu votre question' },
    b: { olieanalyse: "Merci pour votre demande. Un spécialiste Triple R vous contactera au sujet de l'échantillon d'huile.", offerte: 'Merci pour votre demande. Un spécialiste examinera votre sélection et vous enverra un devis adapté à votre installation.', besparing: 'Merci pour votre demande. Un spécialiste vous enverra le rapport avec vos valeurs et hypothèses.', contact: 'Merci pour votre message. Un spécialiste Triple R vous contactera.', marc: "Merci pour votre question. Marc n'a pas trouvé de réponse fiable dans notre documentation ; nous l'avons donc transmise à un spécialiste Triple R, qui vous contactera.", sollicitatie: 'Merci pour votre candidature chez Triple R Europe. Maxim Van Uytven l\'examinera et vous contactera.' },
    h: 'La suite', steps: ['Vous recevez un kit de prélèvement avec des instructions, ou nous planifions une visite.', 'Le laboratoire analyse votre échantillon.', 'Vous recevez le rapport avec des conseils concrets.'], th: "Où prélever un échantillon d'huile ?", tip: 'Machine en marche, à un point fixe de la conduite de retour ou du réservoir, dans un flacon propre.', u: 'Urgent ? Appelez-nous au', cta: 'Visitez notre site', bye: 'Cordialement,', team: "L'équipe Triple R Europe", legal: 'Vous recevez cet e-mail parce que vous avez rempli un formulaire sur notre site.', c: 'Belgique' },
  de: { hi: n => (n ? `Guten Tag ${n},` : 'Guten Tag,'), s: { olieanalyse: 'Wir haben Ihre Anfrage für eine kostenlose Ölanalyse erhalten', offerte: 'Wir haben Ihre Angebotsanfrage erhalten', besparing: 'Wir haben Ihre Berichtsanfrage erhalten', contact: 'Wir haben Ihre Nachricht erhalten', sollicitatie: 'Wir haben Ihre Bewerbung erhalten', marc: 'Wir haben Ihre Frage erhalten' },
    b: { olieanalyse: 'Vielen Dank für Ihre Anfrage. Ein Triple R-Spezialist meldet sich bei Ihnen wegen der Ölprobe.', offerte: 'Vielen Dank für Ihre Anfrage. Ein Spezialist prüft Ihre Auswahl und schickt Ihnen ein Angebot, abgestimmt auf Ihre Anlage.', besparing: 'Vielen Dank für Ihre Anfrage. Ein Spezialist schickt Ihnen den Bericht mit Ihren Werten und Annahmen.', contact: 'Vielen Dank für Ihre Nachricht. Ein Triple R-Spezialist meldet sich bei Ihnen.', marc: 'Vielen Dank für Ihre Frage. Marc hat in unserer Dokumentation keine verlässliche Antwort gefunden; deshalb haben wir sie an einen Triple R-Spezialisten weitergegeben, der sich bei Ihnen meldet.', sollicitatie: 'Vielen Dank für Ihre Bewerbung bei Triple R Europe. Maxim Van Uytven prüft sie und meldet sich bei Ihnen.' },
    h: 'So geht es weiter', steps: ['Sie erhalten ein Probenahme-Set mit Anleitung, oder wir planen einen Besuch.', 'Das Labor analysiert Ihre Probe.', 'Sie erhalten den Bericht mit konkreter Empfehlung.'], th: 'Wo nehmen Sie eine Ölprobe?', tip: 'Bei laufender Maschine, an einer festen Stelle in der Rücklaufleitung oder im Tank, in eine saubere Flasche.', u: 'Dringend? Rufen Sie uns an:', cta: 'Besuchen Sie unsere Website', bye: 'Mit freundlichen Grüßen', team: 'Ihr Team von Triple R Europe', legal: 'Sie erhalten diese E-Mail, weil Sie auf unserer Website ein Formular ausgefüllt haben.', c: 'Belgien' },
};

const firstName = d => { const n = d.name.trim().split(/\s+/)[0] || ''; return /^[\p{L}'-]{2,30}$/u.test(n) ? n : ''; };

// Tabellen en inline stijlen: de enige opmaak die ook Outlook betrouwbaar toont
function shell(inner, preheader, footer) {
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0;padding:0;background:#F1F4F8">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">${esc(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F1F4F8"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#fff;border-radius:12px;overflow:hidden;font-family:Helvetica,Arial,sans-serif;color:#1B1B2B">
<tr><td style="background:#0E0B24;padding:22px 32px"><img src="${esc(LOGO())}" alt="Triple R" height="36" style="display:block;height:36px;border:0"></td></tr>
${inner}
<tr><td style="padding:20px 32px;background:#F7F8FA;border-top:1px solid #E6E9EF;font-size:12px;line-height:18px;color:#5B6072">${footer}</td></tr>
</table></td></tr></table></body></html>`;
}

export function replyMail(d) {
  const r = REPLY[d.lang], subject = r.s[d.type], hi = r.hi(firstName(d)), oil = d.type === 'olieanalyse';
  const addr = `Triple R Europe nv · Cleydaellaan 16, unit 8 · 2630 Aartselaar · ${r.c}`;
  const text = [hi, '', r.b[d.type], ...(oil ? ['', `${r.h}:`, ...r.steps.map((x, i) => `${i + 1}. ${x}`), '', `${r.th} ${r.tip}`] : []), '', `${r.u} +32 (0)3 825 46 47.`, '', r.bye, r.team, '', addr, r.legal].join('\n');
  const steps = oil ? `<tr><td style="padding:0 32px 8px"><p style="margin:0 0 12px;font-size:17px;line-height:24px;font-weight:bold">${esc(r.h)}</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">${r.steps.map((x, i) => `<tr><td width="34" valign="top" style="padding:0 0 12px"><div style="width:24px;height:24px;line-height:24px;border-radius:12px;background:#EAF4FA;color:#006BA6;font-size:13px;font-weight:bold;text-align:center">${i + 1}</div></td><td style="padding:2px 0 12px;font-size:15px;line-height:22px">${esc(x)}</td></tr>`).join('')}</table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td style="padding:14px 16px;background:#F7F8FA;border-left:3px solid #006BA6;font-size:14px;line-height:21px"><b>${esc(r.th)}</b><br>${esc(r.tip)}</td></tr></table></td></tr>` : '';
  const inner = `<tr><td style="padding:32px 32px 8px"><h1 style="margin:0 0 16px;font-size:22px;line-height:29px;font-weight:bold">${esc(subject)}</h1><p style="margin:0 0 12px;font-size:15px;line-height:23px">${esc(hi)}</p><p style="margin:0 0 16px;font-size:15px;line-height:23px">${esc(r.b[d.type])}</p></td></tr>${steps}
<tr><td style="padding:16px 32px 28px;font-size:15px;line-height:23px"><p style="margin:0 0 20px">${esc(r.u)} <a href="tel:+3238254647" style="color:#006BA6;font-weight:bold;text-decoration:none;white-space:nowrap">+32 (0)3 825 46 47</a></p><p style="margin:0">${esc(r.bye)}<br><b>${esc(r.team)}</b></p></td></tr>`;
  return { subject, text, html: shell(inner, r.b[d.type], `<b style="color:#1B1B2B">Triple R Europe nv</b><br>Cleydaellaan 16, unit 8, 2630 Aartselaar, ${esc(r.c)}<br><a href="mailto:info@triple-r-europe.com" style="color:#006BA6">info@triple-r-europe.com</a><br><span style="color:#7A7F90">${esc(r.legal)}</span>`) };
}

// Leadmail voor sales: wie, hoe bereikbaar, wat gevraagd
export function leadMail(d, sc) {
  const job = d.type === 'sollicitatie';
  const subject = job ? `[SOLLICITATIE] ${d.extra.Vacature || ''} – ${d.name}` : `[LEAD ${sc}/10] ${TYPES[d.type]} – ${d.company || d.name}`;
  const skip = /^(naam|name|nom|bedrijf|bedrijfsnaam|company|company name|entreprise|nom de l'entreprise|e-?mail|zakelijk e-mailadres|business email address|adresse e-mail professionnelle|telefoon|phone|téléphone|land|country|pays|voornaam|first name|prénom|last name)$/i;
  const rows = d.fields.filter(f => !skip.test(f.label)).map(f => `<tr><td valign="top" width="38%" style="padding:9px 12px 9px 0;border-top:1px solid #E6E9EF;font-size:13px;line-height:19px;color:#5B6072">${esc(f.label)}</td><td style="padding:9px 0;border-top:1px solid #E6E9EF;font-size:14px;line-height:20px;white-space:pre-wrap">${esc(f.value)}</td></tr>`).join('');
  const extra = Object.entries(d.extra).map(([k, v]) => `<tr><td style="padding:0 32px 20px"><p style="margin:0 0 6px;font-size:13px;font-weight:bold;color:#5B6072">${esc(k)}</p><div style="padding:12px 14px;background:#F7F8FA;border-radius:8px;font-size:14px;line-height:21px;white-space:pre-wrap">${esc(v)}</div></td></tr>`).join('');
  const color = sc >= 7 ? '#0B7A45' : sc >= 4 ? '#006BA6' : '#5B6072';
  const inner = `<tr><td style="padding:28px 32px 4px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td style="font-size:13px;font-weight:bold;color:#006BA6">${esc(TYPES[d.type])} · ${d.lang.toUpperCase()}</td><td align="right">${job ? (d.cv ? `<span style="font-size:12px;color:#5B6072">cv: ${esc(d.cv.name)}</span>` : '') : `<span style="display:inline-block;padding:3px 10px;border-radius:12px;background:${color};color:#fff;font-size:12px;font-weight:bold">Score ${sc}/10</span>`}</td></tr></table>
<h1 style="margin:10px 0 2px;font-size:24px;line-height:30px;font-weight:bold">${esc(d.company || d.name)}</h1><p style="margin:0 0 18px;font-size:15px;line-height:22px;color:#5B6072">${esc(d.company ? d.name : '')}${d.country ? `${d.company ? ' · ' : ''}${esc(d.country)}` : ''}</p>
<a href="mailto:${esc(d.email)}" style="display:inline-block;padding:11px 20px;margin:0 8px 8px 0;border-radius:8px;background:#006BA6;color:#fff;font-size:14px;font-weight:bold;text-decoration:none">${esc(d.email)}</a>${d.phone ? `<a href="tel:${esc(d.phone.replace(/[^+\d]/g, ''))}" style="display:inline-block;padding:10px 20px;margin:0 0 8px;border-radius:8px;border:1px solid #C9D2DE;color:#1B1B2B;font-size:14px;font-weight:bold;text-decoration:none">${esc(d.phone)}</a>` : ''}</td></tr>
${rows ? `<tr><td style="padding:14px 32px 12px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">${rows}</table></td></tr>` : ''}${extra}`;
  const meta = [`Pagina: ${esc(d.page)}`, d.referrer ? `Verwijzer: ${esc(d.referrer)}` : '', `Nieuwsbrief: ${d.newsletter ? 'ja' : 'nee'}`, ...Object.entries(d.utm).map(([k, v]) => `${esc(k)}: ${esc(v)}`)].filter(Boolean).join('<br>');
  return { subject, text: render(d, sc), html: shell(inner, `${d.name} · ${d.email}`, `Antwoorden op deze mail gaat rechtstreeks naar de klant.<br>${meta}`) };
}

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
  let cv = null;
  if (d.cv && typeof d.cv === 'object' && typeof d.cv.data === 'string') {
    const buf = Buffer.from(d.cv.data.slice(0, Math.ceil(CV_MAX * 1.4)), 'base64'), name = str(d.cv.name, 120).replace(/[^\w .()-]/g, '_');
    const pdf = buf.subarray(0, 4).toString() === '%PDF', doc = buf[0] === 0xd0 && buf[1] === 0xcf, docx = buf[0] === 0x50 && buf[1] === 0x4b;
    if (buf.length && buf.length <= CV_MAX && ((pdf && /\.pdf$/i.test(name)) || (doc && /\.doc$/i.test(name)) || (docx && /\.docx$/i.test(name)))) cv = { name, buf, type: pdf ? 'application/pdf' : doc ? 'application/msword' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' };
    else cv = false;
  }
  return { cv, type: str(d.type, 20), lang: Object.keys(REPLY).includes(d.lang) ? d.lang : 'nl', page: str(d.page, 300), referrer: str(d.referrer, 300), email: str(d.email, 200), name: str(d.name, 120), company: str(d.company, 160), phone: str(d.phone, 40), country: str(d.country, 80), message: str(d.message, 4000), consent: d.consent === true, newsletter: d.newsletter === true, fields, extra, utm };
}

export function validate(d, raw) {
  if (raw.website) return 'spam';
  if (d.cv === false) return 'cv';
  if (typeof raw.elapsed === 'number' && raw.elapsed < 3000) return 'spam';
  if (!TYPES[d.type]) return 'type';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.email)) return 'email';
  if (!d.consent) return 'consent';
  if (d.type === 'sollicitatie' && !d.cv) return 'cv';
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
  if (d.type === 'sollicitatie') return { to: JOBS_TO(), bcc: TO() };
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

async function mail(p, file) {
  const key = env('MAILGUN_API_KEY');
  if (!key) return false;
  let body;
  if (file) { body = new FormData(); Object.entries(p).forEach(([k, v]) => body.append(k, v)); body.append('attachment', new Blob([file.buf], { type: file.type }), file.name); }
  else body = new URLSearchParams(p);
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
  const { cv, ...rest } = d;
  try { await getStore('leads').setJSON(id, { ...rest, cv: cv ? cv.name : null, score: sc }); if (cv) await getStore('cvs').set(id, cv.buf); stored = true; } catch (e) { console.error('lead-opslag mislukt', e.message); }
  const { to, bcc } = route(d);
  try {
    sent = await mail({ from: FROM(), to, bcc, 'h:Reply-To': d.email, ...leadMail(d, sc) }, d.cv || null);
    if (sent) await mail({ from: FROM(), to: d.email, 'h:Reply-To': 'info@triple-r-europe.com', ...replyMail(d) });
  } catch (e) { console.error('mail mislukt', e.message); }
  if (env('LEAD_WEBHOOK_URL')) { try { await fetch(env('LEAD_WEBHOOK_URL'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...d, score: sc }) }); } catch (e) { console.error('webhook mislukt', e.message); } }
  if (!stored && !sent) return json(502, { ok: false });
  return json(200, { ok: true });
};
