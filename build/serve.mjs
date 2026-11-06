// Lokale preview van dist/ met _redirects-gedrag en een nep-/api/lead (verstuurt niets).
import { createServer } from 'node:http';
import { readFileSync, existsSync, statSync } from 'node:fs';
import { extname, join } from 'node:path';
import { gzipSync } from 'node:zlib';
const ROOT = new URL('../dist/', import.meta.url).pathname.replace(/%20/g, ' ');
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.pdf': 'application/pdf', '.xml': 'application/xml', '.txt': 'text/plain; charset=utf-8', '.mp4': 'video/mp4', '.webm': 'video/webm' };
const rules = new Map(readFileSync(join(ROOT, '_redirects'), 'utf8').split('\n').filter(l => l && !l.startsWith('#')).map(l => l.split(' ')).filter(p => p[2] === '301' && !p[0].includes('*')).map(p => [decodeURI(p[0]).replace(/\/$/, '') || '/', p[1]]));
const leads = [];
createServer((req, res) => { try {
  const url = new URL(req.url, 'http://localhost');
  if (url.pathname === '/api/lead') {
    if (req.method === 'GET') { res.setHeader('Content-Type', 'application/json'); return res.end(JSON.stringify(leads)); }
    let b = ''; req.on('data', c => b += c); req.on('end', () => { leads.push(JSON.parse(b)); res.setHeader('Content-Type', 'application/json'); res.end('{"ok":true}'); }); return;
  }
  const p = decodeURI(url.pathname);
  const key = p.replace(/\/$/, '') || '/';
  if (rules.has(key) && !existsSync(join(ROOT, p, 'index.html'))) { res.writeHead(301, { Location: rules.get(key) }); return res.end(); }
  if (key === '/') { res.writeHead(301, { Location: '/nl/' }); return res.end(); }
  let f = join(ROOT, p);
  if (existsSync(f) && statSync(f).isDirectory()) f = join(f, 'index.html');
  if (!existsSync(f)) { res.statusCode = 404; res.setHeader('Content-Type', MIME['.html']); return res.end(readFileSync(join(ROOT, p.slice(0, 4).match(/^\/(nl|en|fr)\//) ? p.slice(1, 3) + '/404.html' : '404.html'))); }
  res.setHeader('Content-Type', MIME[extname(f)] || 'application/octet-stream');
  res.setHeader('Cache-Control', p.startsWith('/assets/') ? 'public, max-age=31536000, immutable' : 'no-cache');
  const body = readFileSync(f);
  if (/\.(html|js|css|svg|txt|xml)$/.test(f)) { res.setHeader('Content-Encoding', 'gzip'); return res.end(gzipSync(body)); }
  res.end(body);
  } catch (e) { res.statusCode = 503; res.end('rebuild'); }
}).listen(+process.env.PORT || 4330, () => console.log('ok'));
