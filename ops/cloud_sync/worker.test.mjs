import test from 'node:test';
import assert from 'node:assert/strict';
import worker, { normalizeReading, mergeReading, accessOk, corsHeaders } from './worker.mjs';

test('normalize accepts v1 backup shape', () => {
  const n = normalizeReading({
    format: 'research-radar-reading',
    version: 1,
    updatedAt: '2026-10-29T01:00:00.000Z',
    read: { a: true },
    star: {},
    queue: {},
    note: { a: 'x' },
    kept: {},
  });
  assert.equal(n.version, 2);
  assert.equal(n.read.a, true);
  assert.equal(n.note.a, 'x');
});

test('merge unions flags and prefers newer view', () => {
  const local = {
    format: 'research-radar-reading', version: 2, updatedAt: '2026-10-29T02:00:00.000Z',
    view: 'week', read: { a: true }, star: {}, queue: {}, note: {}, kept: {},
  };
  const remote = {
    format: 'research-radar-reading', version: 2, updatedAt: '2026-10-29T01:00:00.000Z',
    view: 'today', read: { b: true }, star: { c: true }, queue: {}, note: { b: 'n' }, kept: {},
  };
  const m = mergeReading(local, remote);
  assert.equal(m.view, 'week');
  assert.equal(m.read.a, true);
  assert.equal(m.read.b, true);
  assert.equal(m.star.c, true);
  assert.equal(m.note.b, 'n');
});

test('accessOk accepts Access assertion or bearer token', () => {
  const req = new Request('https://example/v1/reading');
  assert.equal(accessOk(req, {}), false);
  assert.equal(accessOk(req, { SKIP_ACCESS_CHECK: '1' }), true);
  const ok = new Request('https://example/v1/reading', { headers: { 'Cf-Access-Jwt-Assertion': 'x'.repeat(40) } });
  assert.equal(accessOk(ok, {}), true);
  const tok = new Request('https://example/v1/reading', { headers: { Authorization: 'Bearer secret-token' } });
  assert.equal(accessOk(tok, { RADAR_SYNC_TOKEN: 'secret-token' }), true);
  assert.equal(accessOk(tok, { RADAR_SYNC_TOKEN: 'other' }), false);
});

test('cors reflects allowed origin', () => {
  const h = corsHeaders('https://jsdwxdzy-lab.github.io', 'https://jsdwxdzy-lab.github.io');
  assert.equal(h['Access-Control-Allow-Origin'], 'https://jsdwxdzy-lab.github.io');
});

test('PUT merges through worker with fake KV', async () => {
  const store = new Map();
  const env = {
    SKIP_ACCESS_CHECK: '1',
    ALLOWED_ORIGIN: 'https://jsdwxdzy-lab.github.io',
    READING_KV: {
      async get(k) { return store.get(k) || null; },
      async put(k, v) { store.set(k, v); },
    },
  };
  const body = JSON.stringify({
    format: 'research-radar-reading', version: 2, updatedAt: '2026-10-29T03:00:00.000Z',
    view: 'all', read: { p1: true }, star: {}, queue: {}, note: {}, kept: {},
  });
  const put = await worker.fetch(new Request('https://sync.example/v1/reading', {
    method: 'PUT',
    headers: { Origin: 'https://jsdwxdzy-lab.github.io', 'content-type': 'application/json' },
    body,
  }), env);
  assert.equal(put.status, 200);
  const get = await worker.fetch(new Request('https://sync.example/v1/reading', {
    method: 'GET',
    headers: { Origin: 'https://jsdwxdzy-lab.github.io' },
  }), env);
  const data = await get.json();
  assert.equal(data.read.p1, true);
  assert.equal(data.view, 'all');
});

test('bridge page is served', async () => {
  const response = await worker.fetch(new Request('https://sync.example/v1/bridge'), {
    ALLOWED_ORIGIN: 'https://jsdwxdzy-lab.github.io',
  });
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /research-radar-sync/);
});
