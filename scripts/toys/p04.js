// 토이 2종: encoder-window (양자화와 창 길이), latency-ring (지연이 phase margin 을 먹는다)
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
  const trace = (g, ys, X, Y, col, wd = 2) => {
    g.beginPath(); g.strokeStyle = col; g.lineWidth = wd; g.lineJoin = 'round';
    ys.forEach((y, i) => i ? g.lineTo(X(i), Y(y)) : g.moveTo(X(i), Y(y))); g.stroke();
  };

  // ------------------------------------------------ encoder-window (lesson main.py: counts, window_velocity, window_lag)
  window.TOYS['encoder-window'] = (el, ctx) => {
    ctx.title('Encoder velocity: loop rate and window', 'Encoder 속도: 루프 주기와 창 길이');
    const go = soon(ctx, () => draw());
    const { c, g, w, h } = ctx.canvas(360, 200);
    const CPR = 4096, W0 = 0.1, TWO_PI = 2 * Math.PI;
    let fs = 1000, n = 1, ro; const cache = {};
    function draw() {
      if (!ro) return;   // sliders call draw before the readout exists
      const dt = 1 / fs, N = Math.round(10 * fs) + 1;
      if (cache.fs !== fs) { cache.fs = fs; cache.cnt = new Int32Array(N); for (let i = 0; i < N; i++) cache.cnt[i] = Math.floor(W0 * i / fs / TWO_PI * CPR); }
      const cnt = cache.cnt, k = TWO_PI / CPR / (n * dt), M = N - n;
      let s1 = 0, s2 = 0;   // v = d * k with d an integer count difference, so the mean and std come from exact integer sums
      for (let i = 0; i < M; i++) { const d = cnt[i + n] - cnt[i]; s1 += d; s2 += d * d; }
      const mean = s1 / M * k, sd = Math.sqrt(Math.max(0, s2 / M - (s1 / M) ** 2)) * k;
      const v = []; for (let i = 0, m = Math.min(M, Math.round(0.3 * fs)); i < m; i++) v.push((cnt[i + n] - cnt[i]) * k);
      const step = k, lag = n * dt / 2 * 1000, shown = v;
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), ok = ctx.color('--ok'), ln = ctx.color('--line');
      const Lm = 40, Rm = 10, Tp = 12, Bt = 26, pw = w - Lm - Rm, ph = h - Tp - Bt, ymax = Math.max(0.3, 1.1 * Math.max(...shown));
      const X = i => Lm + i / (shown.length - 1) * pw, Y = y => Tp + (1 - y / ymax) * ph;
      g.clearRect(0, 0, w, h);
      [0, ymax / 2, ymax].forEach(t => { L(g, Lm, Y(t), Lm + pw, Y(t), ln); T(g, t.toFixed(2), Lm - 4, Y(t) + 4, mut, 'right'); });
      L(g, Lm, Y(W0), Lm + pw, Y(W0), ok, 1.5, [5, 4]);
      trace(g, shown, X, Y, acc);
      g.fillStyle = ctx.color('--card'); g.fillRect(Lm + 2, Y(W0) - 17, 96, 15); T(g, ctx.t('true 0.1 rad/s', '실제 0.1 rad/s'), Lm + 4, Y(W0) - 5, ok);
      T(g, ctx.t('first 0.3 s of the estimate (rad/s)', '추정값 처음 0.3초 (rad/s)'), w - Rm, h - 8, mut, 'right');
      ro.textContent = ctx.t(`smallest step ${step.toFixed(3)} rad/s · std ${sd.toFixed(4)} · lag ${lag.toFixed(2)} ms`,
        `최소 단계 ${step.toFixed(3)} rad/s · std ${sd.toFixed(4)} · 지연 ${lag.toFixed(2)} ms`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    }
    ctx.slider('loop rate (Hz)', '루프 주기 (Hz)', 100, 2000, 100, fs, v => { fs = v; go(); });
    ctx.slider('window n (samples)', '창 길이 n (샘플)', 1, 40, 1, n, v => { n = v; go(); });
    ro = ctx.readout(); live(ctx, draw, el); draw();
  };

  // ------------------------------------------------ latency-ring (lesson main.py: crossover, phase_margin, delay_margin, simulate)
  window.TOYS['latency-ring'] = (el, ctx) => {
    ctx.title('Delay until the loop rings', '지연을 늘려 루프를 떨게 하기');
    const go = soon(ctx, () => draw());
    const { c, g, w, h } = ctx.canvas(360, 200);
    const J = 0.05, KP = 100, DT = 1e-4, TT = 2, Q0 = 0.1;
    let delay = 10, kd = 2, ro;
    const q = new Float64Array(Math.round(TT / DT) + 1), qd = new Float64Array(q.length);
    const crossover = (kp, d) => Math.sqrt((d * d + Math.sqrt(d ** 4 + 4 * J * J * kp * kp)) / (2 * J * J));
    function draw() {
      if (!ro) return;   // sliders call draw before the readout exists
      const wc = crossover(KP, kd), dm = Math.atan(kd * wc / KP) / wc * 1000, ratio = delay / dm;
      const n = Math.round(TT / DT), lag = Math.round(delay / 1000 / DT);
      q[0] = Q0; qd[0] = 0;   // buffers are reused; every entry up to `last` is written before it is read
      let last = n;
      for (let i = 0; i < n; i++) {
        const j = Math.max(i - lag, 0);
        qd[i + 1] = qd[i] + DT * (-KP * q[j] - kd * qd[j]) / J; q[i + 1] = q[i] + DT * qd[i + 1];
        if (Math.abs(q[i + 1]) > 1e3) { last = i + 1; break; }
      }
      const amp = (a, b) => { let m = 0; for (let i = Math.round(a / DT); i < Math.min(Math.round(b / DT), last); i++) m = Math.max(m, Math.abs(q[i])); return m; };
      const a1 = amp(1, 1.5), a2 = last < n ? Infinity : amp(1.5, 2);
      const verdict = a2 > 1.05 * a1 && a2 > 0.005 ? ctx.t('grows', '커짐') : a2 < 0.01 ? ctx.t('settles', '가라앉음') : ctx.t('still ringing', '계속 떪');
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), bad = ctx.color('--bad'), ln = ctx.color('--line');
      const Lm = 36, Rm = 10, Tp = 12, Bt = 26, pw = w - Lm - Rm, ph = h - Tp - Bt, Ym = 0.2;
      const X = i => Lm + i / 400 * pw, Y = y => Tp + (1 - (Math.max(-Ym, Math.min(Ym, y)) + Ym) / (2 * Ym)) * ph;
      g.clearRect(0, 0, w, h);
      [-Ym, 0, Ym].forEach(t => { L(g, Lm, Y(t), Lm + pw, Y(t), ln); T(g, t.toFixed(1), Lm - 4, Y(t) + 4, mut, 'right'); });
      const ys = []; let cut = -1;   // a blown-up run stops where it leaves the plot range, so it cannot read as "settled"
      for (let i = 0; i <= 400 && cut < 0; i++) { const y = q[Math.min(i * n / 400 | 0, last)]; ys.push(y); if (Math.abs(y) > Ym) cut = i; }
      trace(g, ys, X, Y, last < n ? bad : acc);
      if (cut >= 0) { g.beginPath(); g.arc(X(cut), Y(ys[cut]), 4, 0, 7); g.fillStyle = bad; g.fill(); }
      T(g, ctx.t('joint angle over 2 s (rad)', '관절 각도 2초 (rad)'), w - Rm, h - 8, mut, 'right');
      if (cut >= 0) T(g, ctx.t('blew up', '발산'), Math.min(X(cut) + 10, w - Rm - 40), Tp + ph / 2 - 8, bad, 'left', '600');
      ro.textContent = ctx.t(`crossover ${wc.toFixed(1)} rad/s · delay margin ${dm.toFixed(1)} ms · delay ${ratio.toFixed(2)}× margin → ${verdict}`,
        `crossover ${wc.toFixed(1)} rad/s · delay margin ${dm.toFixed(1)} ms · 지연은 margin의 ${ratio.toFixed(2)}배 → ${verdict}`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    }
    ctx.slider('loop delay (ms)', '루프 지연 (ms)', 0, 30, 0.5, delay, v => { delay = v; go(); });
    ctx.slider('kd (damping)', 'kd (댐핑)', 0.5, 16, 0.5, kd, v => { kd = v; go(); });
    ro = ctx.readout(); live(ctx, draw, el); draw();
  };
})();
