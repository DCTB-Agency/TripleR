// Draait automatisch na elke geslaagde deploy (Netlify event-functie "deploy-succeeded").
// Meldt de AI-backend van Marc dat er een nieuwe inhoudsexport klaarstaat (/ask-content.json),
// zodat die alleen de gewijzigde stukken opnieuw indexeert. Zie docs/marc-ai-backend-brief.md §4.3.
//
// Omgevingsvariabelen (Netlify > Site configuration > Environment variables):
//   ASK_REINDEX_URL     bv. https://backend.example.com/v1/reindex   (leeg = niets doen)
//   ASK_BACKEND_TOKEN   geheime token van de subleverancier (Bearer)
//   ASK_REINDEX_CONTEXTS optioneel, komma-gescheiden deploy-contexten (standaard: production)

const env = k => process.env[k] || '';

export function buildNotice(deploy, e = env) {
  const url = e('ASK_REINDEX_URL');
  const token = e('ASK_BACKEND_TOKEN');
  if (!url || !token) return { skip: 'ASK_REINDEX_URL of ASK_BACKEND_TOKEN ontbreekt' };
  const contexts = (e('ASK_REINDEX_CONTEXTS') || 'production').split(',').map(s => s.trim()).filter(Boolean);
  const context = deploy.context || 'production';
  if (!contexts.includes(context)) return { skip: `context ${context} niet in ${contexts.join(',')}` };
  const base = (deploy.ssl_url || deploy.url || e('URL') || '').replace(/\/$/, '');
  if (!/^https:\/\//.test(base)) return { skip: 'geen https-adres van de site' };
  return {
    url,
    init: {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', 'User-Agent': 'triple-r-europe-deploy-hook/1' },
      body: JSON.stringify({
        event: 'deploy-succeeded',
        schema: 'triple-r-ask-content/1',
        export_url: `${base}/ask-content.json`,
        site_url: base,
        context,
        branch: deploy.branch || null,
        deploy_id: deploy.id || null,
        commit: deploy.commit_ref || null,
        published_at: deploy.published_at || new Date().toISOString(),
      }),
    },
  };
}

export default async req => {
  let deploy = {};
  try {
    const body = await req.json();
    deploy = body.payload || body || {};
  } catch (err) { /* geen body: verder met lege payload */ }
  const n = buildNotice(deploy);
  if (n.skip) {
    console.log('ask reindex overgeslagen:', n.skip);
    return new Response('skipped', { status: 200 });
  }
  // Nooit de deploy laten falen: fouten worden alleen gelogd.
  for (let attempt = 1; attempt <= 2; attempt++) {
    try {
      const r = await fetch(n.url, { ...n.init, signal: AbortSignal.timeout(8000) });
      console.log(`ask reindex: HTTP ${r.status} (poging ${attempt})`);
      if (r.ok || r.status < 500) break;
    } catch (err) {
      console.log(`ask reindex mislukt (poging ${attempt}): ${err.message}`);
    }
  }
  return new Response('ok', { status: 200 });
};
