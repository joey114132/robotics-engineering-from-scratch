// motion graphics bootstrap: window.MOTION[name] = (el, m) => {...}; m gives svg(), loop(), colors, easing, text, replay.
// Lazy: a widget is built when its slot comes within 300px of the screen. Every loop runs from ONE shared driver (gsap.ticker when GSAP
// is loaded, requestAnimationFrame otherwise) and only while its slot is on screen. Registration of window.MOTION[name] stays eager.
window.MOTION = window.MOTION || {};
(function () {
  const root = document.documentElement;
  const reduceMq = matchMedia('(prefers-reduced-motion: reduce)');
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const ease = {
    out: t => 1 - Math.pow(1 - clamp(t), 3),
    inOut: t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; },
    sine: t => .5 - .5 * Math.cos(Math.PI * clamp(t)),
    back: t => { t = clamp(t); const c = 1.70158; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); },
    spring: t => { t = clamp(t); return 1 - Math.exp(-6 * t) * Math.cos(11 * t); },
    lerp: (a, b, t) => a + (b - a) * clamp(t),
    seg: (t, a, b) => clamp((t - a) / (b - a)),   // 0..1 progress of t inside [a,b]
  };
  const NS = 'http://www.w3.org/2000/svg';
  function mk(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  // widgets written as GSAP timelines need gsap: wait for it (it loads late on some pages), give up with a quiet note after 12 s
  const waiters = [];
  function whenGsap(cb, el) {
    if (window.gsap) return cb();
    waiters.push(cb);
    if (waiters.length === 1) {
      let n = 0; const iv = setInterval(() => {
        if (window.gsap) { clearInterval(iv); waiters.splice(0).forEach(f => f()); }
        else if (++n > 80) {
          clearInterval(iv); const held = waiters.splice(0);
          document.querySelectorAll('.motion:not(.motion-on)').forEach(e => { if (!e.dataset.nogsap) { e.dataset.nogsap = '1'; e.textContent = (document.documentElement.lang === 'ko' ? '애니메이션을 불러오지 못했습니다. 연결을 확인한 뒤 새로고침하세요.' : 'The animation did not load. Check your connection and reload.'); e.classList.add('mnote'); } });
          // a slow connection can still deliver gsap later: keep checking once a second for a minute, then build what was waiting
          let k = 0; const slow = setInterval(() => {
            if (window.gsap) { clearInterval(slow); held.forEach(f => f()); }
            else if (++k > 60) clearInterval(slow);
          }, 1000);
        }
      }, 150);
    }
  }
  const live = new Set();       // built widgets still in the document: theme, language and reduced-motion changes reach them
  const active = new Set();     // widgets whose loop runs now (on screen, motion allowed)
  const byEl = new WeakMap(), seen = new WeakSet();

  // ---- one driver for every loop ----
  let driver = 0, rafId = 0;     // 1 = requestAnimationFrame, 2 = gsap.ticker
  // ONE clock for every loop: performance.now(). The drivers (requestAnimationFrame, gsap.ticker) only decide WHEN to draw, so an animation
  // that moves from one driver to the other keeps its elapsed time (the two drivers' own timestamps have different origins).
  function tick() {
    const now = performance.now();
    for (const w of active) {
      if (!w.el.isConnected) { if (w.tl) w.tl.kill(); active.delete(w); live.delete(w); continue; }
      if (document.hidden || reduceMq.matches) { w.last = 0; continue; }
      if (!w.t0) w.t0 = now;
      const dt = Math.min(.05, (now - (w.last || now)) / 1000); w.last = now;
      w.tRaw = (now - w.t0) / 1000;
      w.lastT = phase(w);
      try { w.loopFn(w.lastT, dt); }
      catch (e) { active.delete(w); setTimeout(() => { throw e; }); }
    }
    if (!active.size) halt();
  }
  const gtick = () => tick();
  const rtick = () => { rafId = 0; tick(); if (active.size) rafId = requestAnimationFrame(rtick); };
  function kick() {
    if (driver) return;
    if (window.gsap) { driver = 2; gsap.ticker.add(gtick); } else { driver = 1; rafId = requestAnimationFrame(rtick); }
  }
  function halt() {
    if (driver === 2) gsap.ticker.remove(gtick); else if (rafId) cancelAnimationFrame(rafId);
    rafId = 0; driver = 0;
  }
  // first time a timeline widget runs it starts at 0 (m.play leaves it at its rest frame until then); later entries resume where it paused
  const start = w => { if (w.tl) { if (reduceMq.matches && !w.once) return; if (!w.began) { w.began = 1; w.tl.time(0, true); w.draw && w.draw(0); } w.tl.play(); return; } if (w.loopFn) { w.last = 0; active.add(w); kick(); } };
  const stop = w => { if (w.tl) w.tl.pause(); active.delete(w); };

  // on screen -> loop runs; off screen -> paused (nothing is torn down, nothing keeps ticking)
  const ioVis = 'IntersectionObserver' in window ? new IntersectionObserver(es => es.forEach(e => {
    const w = byEl.get(e.target); if (!w) return;
    w.visible = e.isIntersecting;
    if (w.visible) { if (!reduceMq.matches || w.once) start(w); } else stop(w);
  })) : null;

  // the one definition of "now" for a widget: wrapped by its period, exactly what tick() passes. Every redraw (theme, language, reduced motion) uses it,
  // so a widget never gets a time past the end of its own tables.
  const phase = w => (w.period ? w.tRaw % w.period : w.tRaw);
  const redraw = w => {
    if (w.tl) { if (reduceMq.matches && !w.once) { w.tl.pause().time(w.rest); w.draw && w.draw(w.rest); } else if (w.draw) w.draw(w.tl.time()); return; }
    if (w.loopFn) w.loopFn(reduceMq.matches ? w.rest : phase(w), 0); };
  const refresh = () => live.forEach(w => { if (!w.el.isConnected) { live.delete(w); active.delete(w); return; } w.themeCbs.forEach(f => f()); redraw(w); });
  let wired = false;
  function wire() {              // shared listeners, installed once: no per-widget global listeners
    if (wired) return; wired = true;
    const re = () => setTimeout(refresh, 0);
    const lb = document.getElementById('lang'), tb = document.getElementById('theme');
    lb && lb.addEventListener('click', re); tb && tb.addEventListener('click', re);
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change', re);
    reduceMq.addEventListener('change', () => live.forEach(w => { stop(w); w.began = 0; if (w.once) { w.once = 0; w.tl.eventCallback('onComplete', null).repeat(-1); } redraw(w); if (!reduceMq.matches && w.visible) start(w); }));
  }

  function build(el) {
    const fn = window.MOTION[el.dataset.motion]; if (!fn || !el.isConnected) return;
    if (fn.gsap && !window.gsap) { whenGsap(() => build(el), el); return; }
    if (el.dataset.nogsap) { delete el.dataset.nogsap; el.classList.remove('mnote'); el.textContent = ''; }
    const lp = el.closest('[data-f]') || root;
    const cs = () => getComputedStyle(lp);
    const w = { el, themeCbs: [], tl: null, draw: null, loopFn: null, visible: false, t0: 0, last: 0, tRaw: 0, rest: 4, period: 0 };
    const themeCbs = w.themeCbs;
    const m = {
      mk, ease, clamp, NS,
      reduced: () => reduceMq.matches,
      lang: () => (root.lang === 'ko' ? 'ko' : 'en'),
      t: (en, ko) => (root.lang === 'ko' ? ko : en),
      // theme + phase-family colours, read live so dark mode and each phase hue work
      c: name => cs().getPropertyValue(name).trim(),
      fam: () => ({ f: cs().getPropertyValue('--pf').trim(), b: cs().getPropertyValue('--pb').trim(), l: cs().getPropertyValue('--pl').trim(), d: cs().getPropertyValue('--pd').trim() }),
      onTheme: f => themeCbs.push(f),
      // svg(w,h,labelEn,labelKo): responsive svg inside a figure; returns {svg,g,W,H}
      svg(W, H, en, ko) {
        el.classList.add('motion-on');
        const svg = mk('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': m.t(en || '', ko || en || '') }, el);
        svg.style.cssText = 'display:block;width:100%;height:auto';
        const lab = () => svg.setAttribute('aria-label', m.t(en || '', ko || en || ''));
        themeCbs.push(lab);
        return { svg, g: mk('g', {}, svg), W, H };
      },
      caption(en, ko) {
        const c = document.createElement('p'); c.className = 'mcap';
        const set = () => { c.textContent = m.t(en, ko); }; set(); themeCbs.push(set); el.appendChild(c);
      },
      // loop(draw, {rest, period}): draw(t_seconds, dt). Animated only while visible and motion allowed.
      // rest = a seconds value whose frame is a complete, readable still (used for reduced motion).
      // period = seconds after which t wraps (loop length); 0 = keep counting.
      loop(draw, o) {
        w.loopFn = draw; w.rest = (o && o.rest != null) ? o.rest : 4; w.period = (o && o.period) || 0;
        draw(reduceMq.matches ? w.rest : 0, 0);
        if (w.visible && !reduceMq.matches) start(w);
      },
      // timeline(opts): a paused, repeating GSAP timeline owned by this widget. Build the choreography on it with tl.to / fromTo / set / add and labels.
      // opts: repeatDelay (s), defaults (tween defaults). Colours: use CSS variables in style (fill:var(--pf)) so theme changes need no redraw.
      timeline(o) {
        o = o || {};
        w.tl = gsap.timeline({ paused: true, repeat: -1, repeatDelay: o.repeatDelay || 0, defaults: Object.assign({ ease: 'power2.inOut' }, o.defaults) });
        return w.tl;
      },
      // play(tl, {rest, draw}): rest = a time (s) inside the timeline whose frame is a complete readable still (reduced motion, and the poster before it scrolls in).
      // draw(t) is optional: called on every update with the timeline time, for state that is computed (physics, filters) rather than tweened.
      play(tl, o) {
        o = o || {}; w.tl = tl; w.rest = o.rest != null ? o.rest : 4; w.draw = o.draw || null;
        if (w.draw) tl.eventCallback('onUpdate', () => w.draw(tl.time()));
        tl.time(w.rest, true); if (w.draw) w.draw(w.rest);
        w.began = 0;
        if (!reduceMq.matches && w.visible) start(w);
      },
      redraw() { redraw(w); },
      replayButton() {
        const b = document.createElement('button'); b.type = 'button'; b.className = 'mreplay';
        const set = () => { b.textContent = m.t('Replay', '다시 보기'); }; set(); themeCbs.push(set);
        b.onclick = () => {
          if (w.tl) {
            const tl = w.tl; w.began = 1;
            if (!reduceMq.matches) { tl.restart(); return; }
            // reduced motion: one pass only, then back to the still frame
            w.once = 1;   // the one pass survives leaving the screen and theme/language refreshes
            tl.repeat(0).eventCallback('onComplete', () => {
              tl.eventCallback('onComplete', null).repeat(-1); w.began = 0; w.once = 0;
              if (reduceMq.matches) { tl.pause().time(w.rest, true); w.draw && w.draw(w.rest); } else start(w);
            });
            tl.restart(); return;
          } w.t0 = 0; w.tRaw = 0; if (!reduceMq.matches) start(w); else w.loopFn && w.loopFn(w.rest, 0); };
        el.appendChild(b);
      },
    };
    byEl.set(el, w); live.add(w);
    if (ioVis) ioVis.observe(el); else w.visible = true;
    fn(el, m);
  }

  // ---- lazy build: one slot per task, nearest first, so a page with several widgets never makes one long task ----
  const queue = []; let pumping = false;
  function pump() {
    const el = queue.shift();
    try { if (el) build(el); } finally { if (queue.length) setTimeout(pump, 0); else pumping = false; }
  }
  const ioNear = 'IntersectionObserver' in window ? new IntersectionObserver(es => {
    es.forEach(e => { if (e.isIntersecting) { ioNear.unobserve(e.target); queue.push(e.target); } });
    if (queue.length && !pumping) { pumping = true; setTimeout(pump, 0); }
  }, { rootMargin: '300px 0px' }) : null;

  // scan() is safe to call again (the single-file router calls it after it inflates a lesson)
  function scan() {
    wire();
    document.querySelectorAll('.motion[data-motion]').forEach(el => {
      if (seen.has(el)) return; seen.add(el);
      if (ioNear) ioNear.observe(el); else build(el);
    });
  }
  // release the slots of a lesson that is leaving the document
  window.MOTION.__dispose = rootEl => rootEl.querySelectorAll('.motion[data-motion]').forEach(el => {
    if (ioNear) ioNear.unobserve(el); if (ioVis) ioVis.unobserve(el);
    const w = byEl.get(el); if (w) { if (w.tl) w.tl.kill(); active.delete(w); live.delete(w); }
  });
  // GSAP can arrive after the first loops started (it loads when the page is idle): hand the running driver over to gsap.ticker
  window.MOTION.__rehome = () => { if (driver === 1 && window.gsap) { if (rafId) cancelAnimationFrame(rafId); rafId = 0; driver = 2; gsap.ticker.add(gtick); } };
  window.MOTION.__probe = el => { const w = byEl.get(el); return w ? { tRaw: w.tRaw, t: w.tl ? w.tl.time() : w.lastT, t0: w.t0, period: w.tl ? w.tl.duration() : w.period, timeline: !!w.tl } : null; };
  window.MOTION.__refresh = refresh;   // what a theme or language change runs, callable at once (tests)
  window.MOTION.__stats = () => ({ live: live.size, active: active.size, driver: driver === 2 ? 'gsap.ticker' : driver === 1 ? 'raf' : 'idle' });
  // register a widget written as a GSAP timeline: MOTION.gs('name', (el, m) => { const tl = m.timeline(); ...; m.play(tl, {rest}) })
  window.MOTION.gs = (name, fn) => { fn.gsap = true; window.MOTION[name] = fn; };
  window.addEventListener('DOMContentLoaded', scan);
})();
