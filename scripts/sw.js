// 서비스 워커 원본: build_site.py 가 __V__ 등을 채워 site/sw.js 로 내보낸다. 앱 셸 precache, 이미지 cache-first, 레슨 HTML stale-while-revalidate
const V = '__V__', AV = '__AV__', SHELL = __SHELL__, LH = __LESSONS__;   // LH: lesson page -> hash of its content in this build
const LESSONS = Object.keys(LH);
const BASE = new URL('./', self.location).pathname;
// every cache name carries the registration scope, so two sites on one origin never touch each other's caches
const NS = 'rfs:' + BASE + ':';
const C_SHELL = NS + 'shell:' + V, C_PAGES = NS + 'pages:' + V, C_ASSETS = NS + 'assets:' + AV;
const PAGES = new Set(['index.html', ...LESSONS]);
const SHELLSET = new Set(SHELL);
const MAX_ASSETS = 400;   // runtime image cache: oldest first beyond this
const fresh = u => new Request(u, { cache: 'reload' });

// one key per resource: no query string, no hash
const keyOf = u => new Request(u.origin + u.pathname);
const relOf = u => u.pathname.slice(BASE.length) || 'index.html';

async function trim(cache, max) {
  const keys = await cache.keys();
  for (const k of keys.slice(0, Math.max(0, keys.length - max))) await cache.delete(k);
}
// a put that survives a full disk: on quota errors make room once, then give up quietly
// returns whether the write happened. The retry body is cloned BEFORE the first attempt (a body that was handed to put() cannot be read again).
async function put(cache, key, res, max, retry = true) {
  const spare = retry ? res.clone() : null;
  try { await cache.put(key, res); return true; }
  catch (e) {
    if (!spare) return false;
    try { await trim(cache, Math.floor((max || MAX_ASSETS) / 2)); await cache.put(key, spare); return true; } catch (_) { return false; }   // no room: served from the network next time
  }
}
const sha = async res => [...new Uint8Array(await crypto.subtle.digest('SHA-1', await res.clone().arrayBuffer()))].slice(0, 8).map(b => b.toString(16).padStart(2, '0')).join('');

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    // new caches only: the active version keeps its own shell until this worker activates
    const [shell, pages] = await Promise.all([caches.open(C_SHELL), caches.open(C_PAGES)]);
    await Promise.all([shell.addAll(SHELL.map(fresh)), pages.add(fresh('index.html'))]);
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keep = new Set([C_SHELL, C_PAGES, C_ASSETS]);
    const pages = await caches.open(C_PAGES);
    const have = new Set((await pages.keys()).map(r => relOf(new URL(r.url))));
    for (const k of await caches.keys()) {
      if (!k.startsWith(NS) || keep.has(k)) continue;
      if (k.startsWith(NS + 'pages:')) {   // carry over the lesson pages that still exist; drop the ones this build no longer has
        const old = await caches.open(k);
        for (const r of await old.keys()) {
          const rel = relOf(new URL(r.url));
          if (!PAGES.has(rel) || have.has(rel)) continue;
          const hit = await old.match(r);
          // only a page whose content is byte-for-byte what this build ships goes along; a changed lesson is fetched fresh the next time it is opened
          if (hit && LH[rel] && (await sha(hit)) === LH[rel] && await put(pages, keyOf(new URL(r.url)), hit, 100, false)) have.add(rel);
        }
      }
      await caches.delete(k);
    }
    for (const r of await pages.keys()) if (!PAGES.has(relOf(new URL(r.url)))) await pages.delete(r);
    await self.clients.claim();
  })());
});

// the page asks for 'skip' after the user clicks "Reload", 'warm' once it is idle (every lesson page works offline), 'prefetch' (the next lesson's
// figures, small), and 'pack' / 'pack-cancel' (the Offline pack: every figure, only when the reader asked for it)
self.addEventListener('message', e => {
  const d = e.data || {}, m = d.type;
  if (m === 'skip') self.skipWaiting();
  if (m === 'warm') e.waitUntil(warm());
  if (m === 'prefetch') e.waitUntil(fetchFigures(d.urls, { max: 40, workers: 1 }));
  if (m === 'pack') e.waitUntil(startPack(d.urls));
  if (m === 'pack-cancel') e.waitUntil(cancelPack(d.id));
});

const FIGURE = /^assets\/[^?#]+\.(png|webp|jpe?g|gif|svg)$/i;
async function say(m) { for (const w of await self.clients.matchAll()) w.postMessage(m); }

// ---- the Offline pack: one job at a time. A second start while one runs is ignored and answered with the running job's progress. ----
let job = null, jobSeq = 0;   // job = { id, abort, total, done, bytes, promise }
async function startPack(urls) {
  if (job) { await say({ type: 'pack-start', job: job.id, running: true }); await say({ type: 'pack-progress', job: job.id, done: job.done, total: job.total, bytes: job.bytes }); return; }
  const j = job = { id: ++jobSeq, abort: false, total: 0, done: 0, bytes: 0 };
  await say({ type: 'pack-start', job: j.id, running: false });
  j.promise = fetchFigures(urls, { job: j, workers: 3 }).catch(() => {}).finally(() => { if (job === j) job = null; });
  await j.promise;
}
// cancel and wait until the worker has really stopped writing; the page deletes caches only after this acknowledgement
async function cancelPack(id) {
  const j = job;
  if (j) { j.abort = true; await j.promise; }
  await say({ type: 'pack-cancel-ack', id, was: !!j });
}

// fetch figures into the assets cache. done counts figures that are confirmed in the cache (already there, or written now); a failed or non-OK
// response is listed in `failed` and never counted. Stops on: cancel, no network, no room (quota).
async function fetchFigures(list, o) {
  const urls = [...new Set((list || []).filter(u => typeof u === 'string' && FIGURE.test(u)))].slice(0, o.max || 1000);
  const j = o.job;
  if (j) j.total = urls.length;
  const c = await caches.open(C_ASSETS);
  let got = 0, failed = [], reason = 'done', stop = false;
  const queue = urls.slice();
  const work = async () => {
    while (queue.length && !stop && !(j && j.abort)) {
      const u = queue.shift(), key = keyOf(new URL(u, self.location));
      let saved = !!(await c.match(key));
      if (!saved) {
        let r;
        try { r = await fetch(u); } catch (e) { reason = 'offline'; stop = true; break; }
        if (r.status !== 200) failed.push([u, r.status]);
        else if (await put(c, key, r, null, false)) { saved = true; got++; if (j) j.bytes += +r.headers.get('content-length') || 0; }
        else { reason = 'quota'; stop = true; failed.push([u, 'write']); break; }
      }
      if (saved && j) { j.done++; if (j.done % 3 === 0 || !queue.length) await say({ type: 'pack-progress', job: j.id, done: j.done, total: j.total, bytes: j.bytes }); }
    }
  };
  await Promise.all(Array.from({ length: o.workers || 1 }, work));
  if (j) await say({ type: 'pack-end', job: j.id, reason: j.abort ? 'cancelled' : reason !== 'done' ? reason : failed.length ? 'incomplete' : 'done', done: j.done, total: j.total, got, failed: failed.length, bytes: j.bytes });
}

async function warm() {
  const c = await caches.open(C_PAGES);
  const todo = [];
  for (const u of LESSONS) if (!(await c.match(u))) todo.push(u);
  for (let i = 0; i < todo.length; i += 4) {
    await Promise.all(todo.slice(i, i + 4).map(u => fetch(u).then(r => r.ok ? put(c, keyOf(new URL(u, self.location)), r, 100) : null).catch(() => {})));
  }
  for (const w of await self.clients.matchAll()) w.postMessage({ type: 'warm-done', pages: LESSONS.length });
}

// lesson pages: answer from the cache, refresh in the background; a 404 or 410 from the network drops the cached copy
async function swr(e, key) {
  const c = await caches.open(C_PAGES);
  const hit = await c.match(key);
  const net = fetch(key.url).then(async r => {
    if (r.status === 200) await put(c, key, r.clone(), 100);
    else if (r.status === 404 || r.status === 410) await c.delete(key);
    return r;
  }).catch(() => null);
  if (hit) { e.waitUntil(net); return hit; }
  return (await net) || (await c.match(keyOf(new URL('index.html', self.location)))) || Response.error();
}

async function cacheFirst(e, req, key, name, max) {
  const c = await caches.open(name);
  const hit = await c.match(key);
  if (hit) return hit;
  const r = await fetch(req);
  if (r.status === 200) e.waitUntil((async () => { await put(c, key, r.clone(), max); if (max) await trim(c, max); })());
  return r;
}

self.addEventListener('fetch', e => {
  const req = e.request, u = new URL(req.url);
  if (req.method !== 'GET' || u.origin !== self.location.origin || !u.pathname.startsWith(BASE)) return;
  const rel = relOf(u);
  if (rel === 'sw.js') return;
  const key = keyOf(u);
  if (PAGES.has(rel)) return e.respondWith(swr(e, u.pathname === BASE ? keyOf(new URL('index.html', self.location)) : key));
  if (SHELLSET.has(rel)) return e.respondWith(caches.match(key, { cacheName: C_SHELL }).then(r => r || fetch(req)));
  if (rel.startsWith('assets/')) return e.respondWith(cacheFirst(e, req, key, C_ASSETS, MAX_ASSETS));
});
