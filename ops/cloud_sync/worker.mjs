// Research radar reading-state sync API.
// Protect with Cloudflare Access (email OTP) and/or RADAR_SYNC_TOKEN secret.
// Stores one plaintext JSON blob in KV. No GitHub tokens in source.

export const KEY = 'reading:owner:v1';
export const MAX_BYTES = 1_500_000;

const BLOCKED = new Set(['__proto__', 'prototype', 'constructor']);

export function corsHeaders(origin, allowedOrigin) {
  const allow = origin === allowedOrigin ? origin : allowedOrigin;
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Methods': 'GET,PUT,OPTIONS',
    'Access-Control-Allow-Headers': 'content-type, authorization',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

export function accessOk(request, env) {
  if (env && env.SKIP_ACCESS_CHECK === '1') return true;
  const assertion = request.headers.get('Cf-Access-Jwt-Assertion');
  if (typeof assertion === 'string' && assertion.length > 20) return true;
  const expected = env && typeof env.RADAR_SYNC_TOKEN === 'string' ? env.RADAR_SYNC_TOKEN : '';
  if (!expected) return false;
  const auth = request.headers.get('Authorization') || '';
  const match = auth.match(/^Bearer\s+(.+)$/i);
  return !!(match && match[1] === expected);
}

function cleanBoolMap(value) {
  const out = Object.create(null);
  if (!value || typeof value !== 'object' || Array.isArray(value)) return out;
  for (const [k, v] of Object.entries(value)) {
    if (BLOCKED.has(k) || k.length > 512) continue;
    if (v === true) out[k] = true;
  }
  return out;
}

function cleanNoteMap(value) {
  const out = Object.create(null);
  if (!value || typeof value !== 'object' || Array.isArray(value)) return out;
  for (const [k, v] of Object.entries(value)) {
    if (BLOCKED.has(k) || k.length > 512) continue;
    if (typeof v === 'string' && v.length <= 20000) out[k] = v;
  }
  return out;
}

function cleanKept(value) {
  const out = Object.create(null);
  if (!value || typeof value !== 'object' || Array.isArray(value)) return out;
  for (const [k, v] of Object.entries(value)) {
    if (BLOCKED.has(k) || !v || typeof v !== 'object' || Array.isArray(v)) continue;
    if (v.k !== k || typeof v.t !== 'string') continue;
    out[k] = v;
  }
  return out;
}

export function normalizeReading(raw) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) throw Error('invalid-root');
  if (raw.format !== 'research-radar-reading') throw Error('invalid-format');
  const version = Number(raw.version) || 1;
  if (version !== 1 && version !== 2) throw Error('invalid-version');
  const updatedAt = typeof raw.updatedAt === 'string' ? raw.updatedAt : new Date().toISOString();
  if (Number.isNaN(Date.parse(updatedAt))) throw Error('invalid-updatedAt');
  return {
    format: 'research-radar-reading',
    version: 2,
    updatedAt,
    deviceId: typeof raw.deviceId === 'string' ? raw.deviceId.slice(0, 64) : '',
    view: typeof raw.view === 'string' ? raw.view.slice(0, 32) : 'today',
    topics: Array.isArray(raw.topics) ? raw.topics.filter(v => typeof v === 'string').slice(0, 40) : [],
    sources: Array.isArray(raw.sources) ? raw.sources.filter(v => typeof v === 'string').slice(0, 20) : [],
    q: typeof raw.q === 'string' ? raw.q.slice(0, 200) : '',
    sort: typeof raw.sort === 'string' ? raw.sort.slice(0, 32) : 'score',
    date: typeof raw.date === 'string' ? raw.date.slice(0, 32) : null,
    quick: Array.isArray(raw.quick) ? raw.quick.filter(v => typeof v === 'string').slice(0, 10) : [],
    theme: typeof raw.theme === 'string' ? raw.theme.slice(0, 16) : 'auto',
    read: cleanBoolMap(raw.read),
    star: cleanBoolMap(raw.star),
    queue: cleanBoolMap(raw.queue),
    note: cleanNoteMap(raw.note),
    kept: cleanKept(raw.kept),
  };
}

export function mergeReading(local, remote) {
  if (!remote) return normalizeReading({ ...local, updatedAt: local.updatedAt || new Date().toISOString() });
  if (!local) return normalizeReading(remote);
  const a = normalizeReading(local);
  const b = normalizeReading(remote);
  const newer = Date.parse(a.updatedAt) >= Date.parse(b.updatedAt) ? a : b;
  const older = newer === a ? b : a;
  const union = (x, y) => {
    const out = Object.create(null);
    for (const k of Object.keys(x)) out[k] = true;
    for (const k of Object.keys(y)) out[k] = true;
    return out;
  };
  const notes = Object.create(null);
  for (const src of [older.note, newer.note]) {
    for (const [k, v] of Object.entries(src)) {
      if (!notes[k]) notes[k] = v;
      else if (notes[k] !== v) notes[k] = newer.note[k] || notes[k];
    }
  }
  const kept = Object.create(null);
  for (const src of [older.kept, newer.kept]) Object.assign(kept, src);
  return normalizeReading({
    ...newer,
    read: union(a.read, b.read),
    star: union(a.star, b.star),
    queue: union(a.queue, b.queue),
    note: notes,
    kept,
    updatedAt: new Date(Math.max(Date.parse(a.updatedAt), Date.parse(b.updatedAt))).toISOString(),
  });
}

function bridgeHtml(allowedOrigin) {
  const origin = JSON.stringify(allowedOrigin);
  return `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>科研雷达同步</title>
<body style="font:14px/1.6 system-ui;padding:24px;max-width:420px">
<p id="status">正在连接同步服务…</p>
<script>
(()=>{
const PARENT=${origin};
const status=document.getElementById('status');
function reply(data,source,origin){try{source.postMessage({channel:'research-radar-sync',...data},origin||PARENT)}catch{}}
async function reading(method,body){
  const opts={method,credentials:'include',headers:{}};
  if(body!==undefined){opts.headers['content-type']='application/json';opts.body=JSON.stringify(body)}
  const response=await fetch('/v1/reading',opts);
  const text=await response.text();
  let json=null;try{json=JSON.parse(text)}catch{}
  return {ok:response.ok,status:response.status,json};
}
window.addEventListener('message',async (event)=>{
  if(event.origin!==PARENT)return;
  const msg=event.data||{};
  if(msg.channel!=='research-radar-sync')return;
  try{
    if(msg.type==='ping'){reply({type:'pong',ok:true},event.source,event.origin);return}
    if(msg.type==='get'){const r=await reading('GET');reply({type:'get-result',requestId:msg.requestId,...r},event.source,event.origin);return}
    if(msg.type==='put'){const r=await reading('PUT',msg.body);reply({type:'put-result',requestId:msg.requestId,...r},event.source,event.origin);return}
  }catch(err){reply({type:'error',requestId:msg.requestId,message:String(err&&err.message||err)},event.source,event.origin)}
});
reading('GET').then(r=>{
  if(r.ok){status.textContent='已登录同步。可以关闭此页，回到科研雷达。';if(window.opener)reply({type:'ready',ok:true},window.opener,PARENT)}
  else if(r.status===401)status.textContent='尚未通过 Access 登录。请按提示完成邮箱验证后刷新。';
  else status.textContent='同步服务返回 '+r.status;
}).catch(()=>{status.textContent='无法连接同步服务。'});
})();
</script></body></html>`;
}

async function handleReading(request, env, headers) {
  if (!env.READING_KV) {
    return new Response(JSON.stringify({ error: 'kv-missing' }), { status: 500, headers });
  }
  if (request.method === 'GET') {
    const text = await env.READING_KV.get(KEY);
    if (!text) return new Response(JSON.stringify({ empty: true }), { status: 200, headers });
    const data = normalizeReading(JSON.parse(text));
    return new Response(JSON.stringify(data), { status: 200, headers });
  }
  if (request.method === 'PUT') {
    const rawText = await request.text();
    if (rawText.length > MAX_BYTES) {
      return new Response(JSON.stringify({ error: 'too-large' }), { status: 413, headers });
    }
    const incoming = normalizeReading(JSON.parse(rawText));
    const existingText = await env.READING_KV.get(KEY);
    const existing = existingText ? normalizeReading(JSON.parse(existingText)) : null;
    const merged = mergeReading(incoming, existing);
    merged.updatedAt = new Date().toISOString();
    await env.READING_KV.put(KEY, JSON.stringify(merged));
    return new Response(JSON.stringify(merged), { status: 200, headers });
  }
  return new Response(JSON.stringify({ error: 'method' }), { status: 405, headers });
}

export default {
  async fetch(request, env) {
    const allowed = env.ALLOWED_ORIGIN || 'https://jsdwxdzy-lab.github.io';
    const origin = request.headers.get('Origin') || '';
    const url = new URL(request.url);

    if (url.pathname === '/v1/bridge' || url.pathname === '/v1/bridge/') {
      return new Response(bridgeHtml(allowed), {
        status: 200,
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': 'no-store',
          'X-Frame-Options': 'ALLOWALL',
          'Content-Security-Policy': "frame-ancestors 'self' " + allowed,
        },
      });
    }

    const headers = {
      ...corsHeaders(origin, allowed),
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
    };
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers });
    }
    if (url.pathname !== '/v1/reading' && url.pathname !== '/v1/reading/') {
      return new Response(JSON.stringify({ error: 'not-found' }), { status: 404, headers });
    }
    // Same-origin bridge calls have no Origin; cross-origin must match Pages.
    if (origin && origin !== allowed) {
      return new Response(JSON.stringify({ error: 'origin-denied' }), { status: 403, headers });
    }
    if (!accessOk(request, env)) {
      return new Response(JSON.stringify({ error: 'login-required' }), { status: 401, headers });
    }
    try {
      return await handleReading(request, env, headers);
    } catch (err) {
      const message = err && err.message ? String(err.message) : 'bad-request';
      return new Response(JSON.stringify({ error: message.slice(0, 80) }), { status: 400, headers });
    }
  },
};
