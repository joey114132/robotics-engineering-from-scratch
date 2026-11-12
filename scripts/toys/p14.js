// 토이: consensus-eps (합의 step 크기 eps: 수렴, 진동, 발산은 eps*lambda_max = 2 에서 갈린다)
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
  const N = 8, X0 = [4, -1, 2, 7, 0, 3, -5, 1];   // the lesson's starting values
  // x_i += eps * sum_j A_ij (x_j - x_i); ring: neighbours i+-1, complete: all others
  // same update as the lesson, written per graph: ring sums the two neighbours, complete sums all the others (total - N*x_i)
  // same update as the lesson, written per graph on typed arrays: ring sums the two neighbours, complete sums all the others (total - N*x_i)
  const step = (kind, x, y, eps) => { let tot = 0; for (let i = 0; i < N; i++) tot += x[i]; for (let i = 0; i < N; i++) y[i] = x[i] + eps * (kind === 'ring' ? x[(i + 1) % N] + x[(i + N - 1) % N] - 2 * x[i] : tot - N * x[i]); };
  const ptp = x => { let lo = x[0], hi = x[0]; for (let i = 1; i < N; i++) { if (x[i] < lo) lo = x[i]; if (x[i] > hi) hi = x[i]; } return hi - lo; };
  const path = new Float64Array(301 * N);   // the first 300 ticks, drawn as 8 lines

  window.TOYS['consensus-eps'] = (el, ctx) => {
    ctx.title('Eight robots agreeing: step size eps', '로봇 8대의 합의: step 크기 eps');
    const go = soon(ctx, () => draw());
    const { c, g, w, h } = ctx.canvas(360, 210);
    let eps = 0.05, kind = 'ring', ro;
    const btn = document.createElement('button');
    btn.type = 'button'; btn.style.cssText = 'margin:8px 0 2px;min-height:44px;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:6px 14px;font-size:13px;cursor:pointer';
    btn.onclick = () => { kind = kind === 'ring' ? 'complete' : 'ring'; draw(); };
    el.appendChild(btn);
    function draw() {
      if (!ro) return;   // sliders call draw before the readout exists
      // eigenvalues of L = D - A: ring 2 - 2cos(2 pi k / n); complete graph 0 and n
      const lam2 = kind === 'ring' ? 2 - 2 * Math.cos(2 * Math.PI / N) : N, lmax = kind === 'ring' ? 4 : N, prod = eps * lmax;
      let x = Float64Array.from(X0), y = new Float64Array(N), agree = -1, blew = false, np = 1; path.set(x);
      for (let k = 0; k < 5000; k++) {
        if (ptp(x) < 1e-3) { agree = k; break; }
        step(kind, x, y, eps); [x, y] = [y, x]; const sp = ptp(x); if (!isFinite(sp) || sp > 1e6) { blew = true; break; }
        if (k < 300) { path.set(x, np * N); np++; }
      }
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), ok = ctx.color('--ok'), bad = ctx.color('--bad'), ln = ctx.color('--line');
      const Lm = 30, Rm = 10, Tp = 12, Bt = 26, pw = w - Lm - Rm, ph = h - Tp - Bt, Ym = 8, SH = 300;
      const X = k => Lm + k / SH * pw, Y = v => Tp + (1 - (Math.max(-Ym, Math.min(Ym, v)) + Ym) / (2 * Ym)) * ph;
      g.clearRect(0, 0, w, h);
      [-Ym, 0, Ym].forEach(t => { L(g, Lm, Y(t), Lm + pw, Y(t), ln); T(g, t, Lm - 4, Y(t) + 4, mut, 'right'); });
      L(g, Lm, Y(1.375), Lm + pw, Y(1.375), ok, 1.2, [5, 4]);
      for (let i = 0; i < N; i++) {
        g.beginPath(); g.strokeStyle = blew || prod >= 2 ? bad : acc; g.lineWidth = 1.5; g.globalAlpha = 0.8;
        for (let k = 0; k < np; k++) k ? g.lineTo(X(k), Y(path[k * N + i])) : g.moveTo(X(0), Y(path[i])); g.stroke(); g.globalAlpha = 1;
      }
      T(g, ctx.t('8 robots\' values over 300 ticks, dashed = average', '로봇 8대의 값, 300 tick, 점선 = 평균'), w - Rm, h - 8, mut, 'right');
      const verdict = prod < 2 ? (prod > 1 ? ctx.t('stable, oscillates', '안정, 진동하며 수렴') : ctx.t('stable', '안정')) : ctx.t('unstable', '불안정');
      const res = agree >= 0 ? ctx.t(`agree in ${agree} steps`, `${agree} step 만에 합의`) : blew ? ctx.t('diverges', '발산') : ctx.t('no agreement', '합의 못 함');
      ro.textContent = ctx.t(`${kind} · λ2 ${lam2.toFixed(3)} · λmax ${lmax} · eps·λmax ${prod.toFixed(2)} (${verdict}) · ${res}`,
        `${kind === 'ring' ? '고리' : '완전'} · λ2 ${lam2.toFixed(3)} · λmax ${lmax} · eps·λmax ${prod.toFixed(2)} (${verdict}) · ${res}`);
      btn.textContent = ctx.t(`graph: ${kind}, tap to switch`, `그래프: ${kind === 'ring' ? '고리' : '완전'}, 눌러서 바꾸기`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    }
    ctx.slider('step size eps', 'step 크기 eps', 0.01, 0.6, 0.01, eps, v => { eps = v; go(); });
    ro = ctx.readout(); live(ctx, draw, el); draw();
  };
})();
