// toy bootstrap: each toy is TOYS[name](el, ctx); ctx = {lang(), canvas(w,h), slider(label_en,label_ko,min,max,step,val,cb), readout()}
// Lazy: a toy is built when its slot comes within 300px of the screen and torn down again when it is far away or its lesson is removed.
// Slider values are remembered per toy in rfs-ui (window.RFSUI). A toy that registers anything global (matchMedia or MutationObserver
// listeners, observers, animation frames) hands the undo to ctx.onDispose(fn); the core runs those on teardown.
window.TOYS = window.TOYS || {};
(function () {
  const root = document.documentElement;
  const css = n => getComputedStyle(root).getPropertyValue(n).trim();
  const seen = new WeakSet();
  const live = new Set();       // built toys still in the document: the language button redraws their labels
  let wired = false;
  function wire() {
    if (wired) return; wired = true;
    const lb = document.getElementById('lang');
    lb && lb.addEventListener('click', () => setTimeout(() => live.forEach(t => {
      if (!t.el.isConnected) { live.delete(t); return; }
      t.redraw.forEach(f => f());
    }), 0));
  }
  function build(el) {
    const fn = window.TOYS[el.dataset.toy]; if (!fn || !el.isConnected) return;
    const redraw = [], undo = [];
    const entry = { el, redraw, dispose() { while (undo.length) { try { undo.pop()(); } catch (e) { /* keep tearing down */ } } redraw.length = 0; } };
    live.add(entry);
    if (ioFar) ioFar.observe(el);
    const ctx = {
      onDispose: f => undo.push(f),
      lang: () => root.lang === 'ko' ? 'ko' : 'en',
      t: (en, ko) => (root.lang === 'ko' ? ko : en),
      color: css,
      onRedraw: f => redraw.push(f),
      canvas(w, h) {
        const c = document.createElement('canvas'); c.width = w * 2; c.height = h * 2; c.style.aspectRatio = w + '/' + h;
        const g = c.getContext('2d'); g.scale(2, 2); el.appendChild(c); return { c, g, w, h };
      },
      title(en, ko) { const h = document.createElement('h4'); const set = () => h.textContent = ctx.t(en, ko); set(); redraw.push(set); el.appendChild(h); },
      slider(en, ko, min, max, step, val, cb) {
        const l = document.createElement('label'), s = document.createElement('input'), n = document.createElement('span'), v = document.createElement('b');
        s.type = 'range'; s.min = min; s.max = max; s.step = step; s.value = val;
        const kept = window.RFSUI && window.RFSUI.UI.d.ty[el.dataset.toy], at = el.querySelectorAll('input[type=range]').length;
        if (kept && typeof kept[at] === 'number') s.value = kept[at];   // the browser clamps it to min/max/step
        const set = () => n.textContent = ctx.t(en, ko); set(); redraw.push(set);
        const upd = () => { v.textContent = (+s.value).toFixed(step < 1 ? 2 : 0); cb(+s.value); };
        s.oninput = upd; l.append(n, s, v); el.appendChild(l); upd(); return s;
      },
      readout() { const d = document.createElement('div'); d.className = 'readout'; el.appendChild(d); return d; },
    };
    fn(el, ctx);
    el.dispatchEvent(new Event('rfs-built'));
  }
  // one toy per task, nearest first
  const queue = []; let pumping = false;
  function pump() {
    const el = queue.shift();
    try { if (el) build(el); } finally { if (queue.length) setTimeout(pump, 0); else pumping = false; }
  }
  const ioNear = 'IntersectionObserver' in window ? new IntersectionObserver(es => {
    es.forEach(e => { if (e.isIntersecting) { ioNear.unobserve(e.target); queue.push(e.target); } });
    if (queue.length && !pumping) { pumping = true; setTimeout(pump, 0); }
  }, { rootMargin: '300px 0px' }) : null;
  // far from the screen (about 1.5 screens): tear the toy down. The slot is replaced by an empty clone, so listeners on the old element go too;
  // it is observed again and rebuilt when it comes back near. Slider values live in rfs-ui, the rest of the toy state restarts.
  function release(el) {
    for (const t of live) if (t.el === el) { t.dispose(); live.delete(t); }
    if (ioFar) ioFar.unobserve(el);
    if (!el.isConnected) return;
    const h = el.offsetHeight, fresh = el.cloneNode(false);
    fresh.style.minHeight = h + 'px';   // same height while empty: nothing below it moves
    el.replaceWith(fresh);
    seen.add(fresh);
    if (ioNear) { ioNear.observe(fresh); fresh.addEventListener('rfs-built', () => { fresh.style.minHeight = ''; }, { once: true }); }
  }
  const ioFar = 'IntersectionObserver' in window ? new IntersectionObserver(es => es.forEach(e => { if (!e.isIntersecting) release(e.target); }), { rootMargin: '1200px 0px' }) : null;
  // scan() is safe to call again (the single-file router calls it after it inflates a lesson)
  function scan() {
    wire();
    document.querySelectorAll('.toy[data-toy]').forEach(el => {
      if (seen.has(el)) return; seen.add(el);
      if (!window.TOYS[el.dataset.toy]) { el.style.display = 'none'; return; }
      if (ioNear) ioNear.observe(el); else build(el);
    });
  }
  window.TOYS.__dispose = rootEl => rootEl.querySelectorAll('.toy[data-toy]').forEach(el => {
    if (ioNear) ioNear.unobserve(el);
    if (ioFar) ioFar.unobserve(el);
    for (const t of live) if (t.el === el) { t.dispose(); live.delete(t); }
  });
  window.TOYS.__stats = () => ({ live: live.size });
  window.addEventListener('DOMContentLoaded', scan);
})();
