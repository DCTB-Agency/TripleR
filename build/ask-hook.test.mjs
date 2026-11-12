// Test van netlify/functions/deploy-succeeded.mjs (zonder netwerk).
import assert from 'node:assert/strict';
import { buildNotice } from '../netlify/functions/deploy-succeeded.mjs';

const E = o => k => o[k] || '';
const deploy = { id: 'd1', context: 'production', branch: 'main', ssl_url: 'https://triplereurope.netlify.app', commit_ref: 'abc' };

assert.ok(buildNotice(deploy, E({})).skip, 'zonder URL/token: overslaan');
assert.ok(buildNotice(deploy, E({ ASK_REINDEX_URL: 'https://b.example/v1/reindex' })).skip, 'zonder token: overslaan');

const ok = buildNotice(deploy, E({ ASK_REINDEX_URL: 'https://b.example/v1/reindex', ASK_BACKEND_TOKEN: 'tok' }));
assert.equal(ok.url, 'https://b.example/v1/reindex');
assert.equal(ok.init.headers.Authorization, 'Bearer tok');
const body = JSON.parse(ok.init.body);
assert.equal(body.export_url, 'https://triplereurope.netlify.app/ask-content.json');
assert.equal(body.deploy_id, 'd1');
assert.equal(body.schema, 'triple-r-ask-content/1');

assert.ok(buildNotice({ ...deploy, context: 'deploy-preview' }, E({ ASK_REINDEX_URL: 'https://b.example', ASK_BACKEND_TOKEN: 't' })).skip, 'previews: overslaan');
assert.ok(!buildNotice({ ...deploy, context: 'deploy-preview' }, E({ ASK_REINDEX_URL: 'https://b.example', ASK_BACKEND_TOKEN: 't', ASK_REINDEX_CONTEXTS: 'production,deploy-preview' })).skip, 'context instelbaar');
assert.ok(buildNotice({ ...deploy, ssl_url: 'http://x' }, E({ ASK_REINDEX_URL: 'https://b.example', ASK_BACKEND_TOKEN: 't' })).skip, 'alleen https');

console.log('deploy-hook: alle tests geslaagd');
