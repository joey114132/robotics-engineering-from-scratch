// 토이: dt-blowup (time step 을 키우면 explicit Euler 공은 더 높이 튄다)
(() => {
  const F = '-apple-system,"Pretendard","Noto Sans KR",system-ui,sans-serif';
  const T = (g, s, x, y, c, a = 'left', w = '') => { g.font = `${w} 12px ${F}`; g.fillStyle = c; g.textAlign = a; g.fillText(s, x, y); };
  const L = (g, x1, y1, x2, y2, c, w = 1, d = []) => { g.beginPath(); g.setLineDash(d); g.strokeStyle = c; g.lineWidth = w; g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); g.setLineDash([]); };
  // one shared theme observer per file; a toy redraws for theme/language only while on screen, otherwise on its next view
  const subs = new Set(); let mo, mq;
  const onTheme = () => subs.forEach(f => f());
  const live = (ctx, draw, el) => {
    let vis = true, stale = false;
    const f = () => { if (vis) draw(); else stale = true; };
    const io = new IntersectionObserver(es => { vis = es[es.length - 1].isIntersecting; if (vis && stale) { stale = false; draw(); } });
    io.observe(el); ctx.onRedraw(f);
    if (!subs.size) { mo = new MutationObserver(onTheme); mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] }); mq = matchMedia('(prefers-color-scheme: dark)'); mq.addEventListener('change', onTheme); }
    subs.add(f);
    ctx.onDispose(() => { io.disconnect(); subs.delete(f); if (!subs.size) { mo.disconnect(); mq.removeEventListener('change', onTheme); } });
  };
  // slider events only mark the toy dirty; one redraw per frame, latest value wins
  const soon = (ctx, f) => { let q = 0; ctx.onDispose(() => cancelAnimationFrame(q)); return () => { q = q || requestAnimationFrame(() => { q = 0; f(); }); }; };
  // lesson main.py: step(), rebound_height() with the 10 kN/m penalty floor, h0 0.1 m, T 0.6 s
  const KC = 1e4, G = 9.81, H0 = 0.1, TT = 0.6;
  function drop(method, dt) {
    const acc = x => -G + KC * Math.max(-x, 0), n = Math.round(TT / dt), xs = new Float64Array(n + 1);
    let x = H0, v = 0, hit = false, apex = 0, m = 1; xs[0] = H0;
    for (let i = 0; i < n; i++) {
      if (method === 'euler') { const x2 = x + dt * v; v += dt * acc(x); x = x2; } else { v += dt * acc(x); x += dt * v; }
      if (Math.abs(x) > 1e6) return { apex: Infinity, xs: xs.subarray(0, m) };
      xs[m++] = x; hit = hit || x < 0; if (hit && x > 0) apex = Math.max(apex, x);
    }
    return { apex, xs };
  }

  window.TOYS['dt-blowup'] = (el, ctx) => {
    ctx.title('Bounce height against the time step', 'time step 에 따른 반발 높이');
    const go = soon(ctx, () => draw());
    const { c, g, w, h } = ctx.canvas(360, 210);
    let ms = 3, ro;
    function draw() {
      if (!ro) return;   // sliders call draw before the readout exists
      const dt = ms / 1000, E = drop('euler', dt), S = drop('semi', dt);
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), ok = ctx.color('--ok'), bad = ctx.color('--bad'), ln = ctx.color('--line');
      let hi = 0, lo = 0; for (const xs of [E.xs, S.xs]) for (let i = 0; i < xs.length; i++) { const x = xs[i]; if (x > hi) hi = x; if (x < lo) lo = x; }
      const top = Math.max(0.15, 1.08 * Math.max(hi, H0)), bot = Math.min(-0.02, lo);
      const Lm = 40, Rm = 10, Tp = 12, Bt = 26, pw = w - Lm - Rm, ph = h - Tp - Bt;
      const X = t => Lm + t / TT * pw, Y = y => Tp + (top - Math.max(bot, Math.min(top, y))) / (top - bot) * ph;
      g.clearRect(0, 0, w, h);
      [0, 0.1, top].forEach(t => { L(g, Lm, Y(t), Lm + pw, Y(t), t === 0.1 ? ok : ln, 1.2, t === 0.1 ? [5, 4] : []); T(g, t.toFixed(2), Lm - 4, Y(t) + 4, mut, 'right'); });
      const line = (r, col) => {
        const stride = Math.max(1, Math.round(r.xs.length / 300));
        g.beginPath(); g.strokeStyle = col; g.lineWidth = 2; g.lineJoin = 'round';
        for (let i = 0; i < r.xs.length; i += stride) i ? g.lineTo(X(i * dt), Y(r.xs[i])) : g.moveTo(X(0), Y(r.xs[0])); g.stroke();
      };
      line(E, bad); line(S, acc);
      T(g, ctx.t('explicit Euler', 'explicit Euler'), Lm + pw, Tp + 12, bad, 'right', '600');
      T(g, ctx.t('semi-implicit', 'semi-implicit'), Lm + pw, Tp + 28, acc, 'right', '600');
      T(g, ctx.t('height over 0.6 s (m), dashed = drop height', '높이 0.6초 (m), 점선 = 떨어뜨린 높이'), w - Rm, h - 8, mut, 'right');
      const f = a => isFinite(a) ? a.toFixed(3) + ' m' : ctx.t('blew up', '발산');
      ro.textContent = ctx.t(`dt ${ms} ms · rebound: euler ${f(E.apex)}, semi-implicit ${f(S.apex)} · ideal ${H0} m`,
        `dt ${ms} ms · 반발: euler ${f(E.apex)}, semi-implicit ${f(S.apex)} · 이상값 ${H0} m`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    }
    ctx.slider('time step dt (ms)', 'time step dt (ms)', 0.1, 20, 0.1, ms, v => { ms = v; go(); });
    ro = ctx.readout(); live(ctx, draw, el); draw();
  };
})();
