// 단계 03 토이 4종
(() => {
  const FONT = '-apple-system,"Pretendard","Noto Sans KR",system-ui,sans-serif';
  function live(ctx, draw) {
    ctx.onRedraw(draw);
    const mq = matchMedia('(prefers-color-scheme: dark)'), mo = new MutationObserver(draw);
    mq.addEventListener('change', draw); mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    ctx.onDispose(() => { mq.removeEventListener('change', draw); mo.disconnect(); });
  }
  const path = (g, pts, c, w = 2, d = []) => { g.beginPath(); g.setLineDash(d); g.strokeStyle = c; g.lineWidth = w; g.lineJoin = 'round'; pts.forEach((p, i) => g[i ? 'lineTo' : 'moveTo'](p[0], p[1])); g.stroke(); g.setLineDash([]); };
  const ln = (g, x1, y1, x2, y2, c, w = 1, d = []) => path(g, [[x1, y1], [x2, y2]], c, w, d);
  const tx = (g, s, x, y, c, a = 'left') => { g.font = '12.5px ' + FONT; g.fillStyle = c; g.textAlign = a; g.fillText(s, x, y); };
  const mul = (A, B) => A.map(r => B[0].map((_, j) => r.reduce((s, a, k) => s + a * B[k][j], 0)));
  const T = A => A[0].map((_, j) => A.map(r => r[j]));
  const plant = dt => ({ A: [[1, dt], [0, 1]], B: [dt * dt / 2, dt] });
  const m2 = (X, Y) => [X[0] * Y[0] + X[1] * Y[2], X[0] * Y[1] + X[1] * Y[3], X[2] * Y[0] + X[3] * Y[2], X[2] * Y[1] + X[3] * Y[3]];   // 2x2 를 [a, b, c, d] 로
  function dare(A, B, Q, R) {
    const At = [A[0][0], A[1][0], A[0][1], A[1][1]], Af = [A[0][0], A[0][1], A[1][0], A[1][1]], Qf = [Q[0][0], Q[0][1], Q[1][0], Q[1][1]];
    let P = Qf, K = [0, 0];
    for (let n = 0; n < 20000; n++) {
      const s = R + B[0] * (P[0] * B[0] + P[1] * B[1]) + B[1] * (P[2] * B[0] + P[3] * B[1]), PA = m2(P, Af);
      K = [(B[0] * PA[0] + B[1] * PA[2]) / s, (B[0] * PA[1] + B[1] * PA[3]) / s];
      const AK = [Af[0] - B[0] * K[0], Af[1] - B[0] * K[1], Af[2] - B[1] * K[0], Af[3] - B[1] * K[1]], N = m2(At, m2(P, AK));
      const Pn = Qf.map((q, i) => q + N[i]), d = Math.max(...Pn.map((v, i) => Math.abs(v - P[i])));
      P = Pn; if (d < 1e-12) break;
    }
    return { K, P: [[P[0], P[1]], [P[2], P[3]]] };
  }
  const axes = (g, x0, y0, w, h, t0, t1, v0, v1, col) => {
    const X = t => x0 + (t - t0) / (t1 - t0) * w, Y = v => y0 + (v1 - v) / (v1 - v0) * h;
    for (let t = Math.ceil(t0); t <= t1; t++) ln(g, X(t), y0, X(t), y0 + h, col.ln);
    ln(g, x0, Y(0), x0 + w, Y(0), col.mut, 1.2, [4, 3]);
    return [X, Y];
  };
  const cols = ctx => ({ fg: ctx.color('--fg'), mut: ctx.color('--mut'), acc: ctx.color('--acc'), ok: ctx.color('--ok'), bad: ctx.color('--bad'), ln: ctx.color('--line') });

  // 06 lqr-tradeoff
  window.TOYS['lqr-tradeoff'] = (el, ctx) => {
    ctx.title('LQR: price effort, get the gain', 'LQR: 노력에 값을 매기면 게인이 나온다');
    const { g, w, h } = ctx.canvas(360, 250);
    const DT = 0.05, N = 120, memo = {}; let lr = -2, lq = -1, ro, fr;
    const soon = () => { cancelAnimationFrame(fr); fr = requestAnimationFrame(draw); };
    ctx.onDispose(() => cancelAnimationFrame(fr));
    function draw() {
      const c = cols(ctx), { A, B } = plant(DT), R = Math.pow(10, lr), Q = [[1, 0], [0, Math.pow(10, lq)]];
      const key = lr + '/' + lq, { K } = memo[key] || (memo[key] = dare(A, B, Q, R));
      let x = [1, 0], xs = [], us = [], last = -1, pk = 0;
      for (let i = 0; i < N; i++) {
        const u = -(K[0] * x[0] + K[1] * x[1]); xs.push(x[0]); us.push(u); pk = Math.max(pk, Math.abs(u));
        if (Math.abs(x[0]) > 0.02) last = i;
        x = [A[0][0] * x[0] + A[0][1] * x[1] + B[0] * u, x[1] + B[1] * u];
      }
      g.clearRect(0, 0, w, h);
      const L = 40, pw = w - L - 10, um = Math.max(10, pk * 1.05);
      const [X1, Y1] = axes(g, L, 12, pw, 92, 0, N * DT, -0.3, 1.1, c), [X2, Y2] = axes(g, L, 134, pw, 92, 0, N * DT, -um, um, c);
      path(g, xs.map((v, i) => [X1(i * DT), Y1(v)]), c.acc);
      path(g, us.map((v, i) => [X2(i * DT), Y2(v)]), c.bad);
      tx(g, ctx.t('position error (m), 0–6 s', '위치 오차 (m), 0–6 s'), L + 4, 24, c.acc);
      tx(g, ctx.t('push u (m/s²)', '밀기 u (m/s²)'), L + 4, 146, c.bad);
      ro.textContent = ctx.t(`R = ${R.toPrecision(2)} · K = [${K[0].toFixed(2)}, ${K[1].toFixed(2)}] · first push ${pk.toFixed(1)} m/s² · settles ${last < N - 1 ? ((last + 1) * DT).toFixed(2) + ' s' : 'not within 6 s'}`,
        `R = ${R.toPrecision(2)} · K = [${K[0].toFixed(2)}, ${K[1].toFixed(2)}] · 첫 밀기 ${pk.toFixed(1)} m/s² · 정착 ${last < N - 1 ? ((last + 1) * DT).toFixed(2) + ' s' : '6 s 안에 못 함'}`);
    }
    ctx.slider('effort cost R = 10^x', '노력 값 R = 10^x', -2, 1, 0.25, lr, v => { lr = v; ro && soon(); });
    ctx.slider('speed cost Q22 = 10^x', '속도 값 Q22 = 10^x', -2, 1, 0.25, lq, v => { lq = v; ro && soon(); });
    ro = ctx.readout(); live(ctx, draw); soon();
  };

  // 08 mpc-horizon
  window.TOYS['mpc-horizon'] = (el, ctx) => {
    ctx.title('MPC: plan with the limit inside', 'MPC: 한계를 안에 넣고 계획한다');
    const { g, w, h } = ctx.canvas(360, 230);
    const DT = 0.1, STEPS = 120, Q = [[1, 0], [0, 0.1]], R = 0.1, X0 = [4, 0];
    let N = 20, umax = 0.5, ro, tm, res, job = 0, fr;
    const later = () => { clearTimeout(tm); job++; cancelAnimationFrame(fr); ro.textContent = ctx.t('computing…', '계산 중…'); tm = setTimeout(compute, 120); };
    ctx.onDispose(() => { clearTimeout(tm); cancelAnimationFrame(fr); job++; });
    const { A, B } = plant(DT), { K, P: Pf } = dare(A, B, Q, R);
    const step = (x, u) => [x[0] + DT * x[1] + B[0] * u, x[1] + B[1] * u];
    function setup() {
      const Ap = [[[1, 0], [0, 1]]]; for (let i = 0; i < N; i++) Ap.push(mul(A, Ap[i]));
      const Gm = Array.from({ length: 2 * N }, () => new Float64Array(N)), Ph = [];
      for (let i = 0; i < N; i++) { Ph.push(Ap[i + 1][0], Ap[i + 1][1]); for (let j = 0; j <= i; j++) { const v = mul(Ap[i - j], T([B])); Gm[2 * i][j] = v[0][0]; Gm[2 * i + 1][j] = v[1][0]; } }
      const qb = M => M.map((r, i) => i < 2 * N - 2 ? r.map(v => v * Q[i % 2][i % 2]) : r.map((v, j) => Pf[i - 2 * N + 2][0] * M[2 * N - 2][j] + Pf[i - 2 * N + 2][1] * M[2 * N - 1][j])), QG = qb(Gm), QP = qb(Ph);
      const Hm = Array.from({ length: N }, (_, a) => Float64Array.from({ length: N }, (_, b) => { let s = a === b ? R : 0; for (let i = 0; i < 2 * N; i++) s += Gm[i][a] * QG[i][b]; return s; }));
      const Gx = Array.from({ length: N }, (_, a) => [0, 1].map(c => { let s = 0; for (let i = 0; i < 2 * N; i++) s += Gm[i][a] * QP[i][c]; return s; }));
      let v = Array(N).fill(1), lam = 1;
      for (let n = 0; n < 60; n++) { const z = Hm.map(r => r.reduce((a, b, j) => a + b * v[j], 0)); lam = Math.hypot(...z); v = z.map(a => a / lam); }
      const st = 1 / lam / 1.02;
      const plan = (x, g0) => {
        const f = Gx.map(r => r[0] * x[0] + r[1] * x[1]); let U = new Float64Array(N), Y = new Float64Array(N), Wn = new Float64Array(N), t = 1; U.set(g0); Y.set(g0);
        for (let n = 0; n < 800; n++) {
          const tn = (1 + Math.sqrt(1 + 4 * t * t)) / 2; let dm = 0;
          for (let a = 0, Ha; a < N; a++) {
            Ha = Hm[a]; let g = f[a]; for (let j = 0; j < N; j++) g += Ha[j] * Y[j];
            Wn[a] = Math.max(-umax, Math.min(umax, Y[a] - st * g));
          }
          for (let a = 0; a < N; a++) { dm = Math.max(dm, Math.abs(Wn[a] - U[a])); Y[a] = Wn[a] + (t - 1) / tn * (Wn[a] - U[a]); U[a] = Wn[a]; }
          t = tn; if (dm < 1e-6) break;
        }
        return U;
      };
      return plan;
    }
    function compute() {
      const id = ++job; cancelAnimationFrame(fr); ro.textContent = ctx.t('computing…', '계산 중…');
      const n = N, um = umax; let plan, x = X0.slice(), xs = [], at40 = null, g0 = new Float64Array(n), i = 0;
      const tick = () => {
        if (id !== job) return;
        if (!plan) plan = setup();
        for (const t = performance.now(); i < STEPS && performance.now() - t < 6; i++) { const U = plan(x, g0); if (i === 40) at40 = [x, U]; xs.push(x[0]); x = step(x, U[0]); g0 = U.map((_, a) => U[Math.min(a + 1, n - 1)]); }
        if (i < STEPS) fr = requestAnimationFrame(tick); else { res = { xs, at40, n, um }; draw(); }
      };
      fr = requestAnimationFrame(tick);
    }
    function draw() {
      if (!res) return;
      const c = cols(ctx), { xs, at40, n: N, um: umax } = res;
      let x = X0.slice(), cl = [];
      for (let i = 0; i < STEPS; i++) { cl.push(x[0]); x = step(x, Math.max(-umax, Math.min(umax, -(K[0] * x[0] + K[1] * x[1])))); }
      g.clearRect(0, 0, w, h);
      const L = 34, [X, Y] = axes(g, L, 14, w - L - 10, h - 44, 0, STEPS * DT, -2, 4.5, c);
      path(g, cl.map((v, i) => [X(i * DT), Y(v)]), c.bad); path(g, xs.map((v, i) => [X(i * DT), Y(v)]), c.acc, 2.4);
      if (at40) {
        let p = at40[0], pts = [[X(4), Y(p[0])]]; for (let i = 0; i < N; i++) { p = step(p, at40[1][i]); pts.push([X(4 + DT * (i + 1)), Y(p[0])]); }
        path(g, pts, c.fg, 1.5, [3, 3]); pts.forEach((q, i) => { if (i % 2 === 0) { g.beginPath(); g.arc(q[0], q[1], 2.5, 0, 6.3); g.fillStyle = c.fg; g.fill(); } });
      }
      [-2, 0, 2, 4].forEach(v => tx(g, v, L - 5, Y(v) + 4, c.mut, 'right'));
      tx(g, ctx.t('clipped LQR', '자른 LQR'), w - 10, h - 24, c.bad, 'right'); tx(g, 'MPC', w - 10, h - 8, c.acc, 'right');
      tx(g, ctx.t('dots: plan made at 4 s', '점: 4 s 에 세운 계획'), L + 4, h - 8, c.fg);
      const a = Math.max(0, -Math.min(...cl)), b = Math.max(0, -Math.min(...xs));
      ro.textContent = ctx.t(`overshoot: clipped LQR ${a.toFixed(2)} m · MPC ${b.toFixed(2)} m`, `넘침: 자른 LQR ${a.toFixed(2)} m · MPC ${b.toFixed(2)} m`);
    }
    ctx.slider('horizon N (steps)', '예측 길이 N (걸음)', 2, 20, 1, N, v => { N = v; ro && later(); });
    ctx.slider('limit umax (m/s²)', '한계 umax (m/s²)', 0.2, 2, 0.1, umax, v => { umax = v; ro && later(); });
    ro = ctx.readout(); live(ctx, draw); compute();
  };

  // 09 lyapunov-arrows
  window.TOYS['lyapunov-arrows'] = (el, ctx) => {
    ctx.title('Lyapunov: do all arrows point inward?', 'Lyapunov: 화살표가 전부 안쪽을 향하나?');
    const { g, w, h } = ctx.canvas(360, 290);
    const GL = 9.81, CD = 0.1, KP = 10, TH = 3, WM = 8;
    let kd = 2, delay = 0, ro, fr;
    const soon = () => { cancelAnimationFrame(fr); fr = requestAnimationFrame(draw); };
    ctx.onDispose(() => cancelAnimationFrame(fr));
    const V = (a, r) => 0.5 * r * r + GL * (1 - Math.cos(a)) + 0.5 * KP * a * a;
    const acc = (a, r, rc) => -GL * Math.sin(a) - CD * r - KP * a - kd * rc;
    const L = 10, Tp = 8, pw = w - 2 * L, ph = h - 34, X = a => L + (a + TH) / (2 * TH) * pw, Y = r => Tp + (WM - r) / (2 * WM) * ph;
    const rings = [2, 6, 12, 20, 30].map(lv => {
      const pts = [];
      for (let k = 0; k <= 72; k++) {
        const f = k / 72 * 2 * Math.PI; let lo = 0, hi = 1.5;
        for (let n = 0; n < 20; n++) { const m = (lo + hi) / 2; (V(m * TH * Math.cos(f), m * WM * Math.sin(f)) < lv ? lo = m : hi = m); }
        pts.push([X(lo * TH * Math.cos(f)), Y(lo * WM * Math.sin(f))]);
      }
      return pts;
    });
    const memo = {};
    function field() {   // kd 와 delay 에만 달린 값: 화살표, 레슨 simulate() 의 궤적, 지연 속도는 고리 버퍼
      const ok = [], bad = [];
      let worst = 0;
      for (let i = 0; i < 15; i++) for (let j = 0; j < 13; j++) {
        const a = -2.8 + 5.6 * i / 14, r = -7.5 + 15 * j / 12, ac = acc(a, r, r), vd = (GL * Math.sin(a) + KP * a) * r + r * ac;
        const dx = r * pw / (2 * TH), dy = -ac * ph / (2 * WM), m = Math.hypot(dx, dy) || 1;
        worst = Math.max(worst, vd); (vd > 1e-9 ? bad : ok).push([X(a), Y(r), dx / m, dy / m]);
      }
      const dt = 1e-3, buf = new Float64Array(Math.round(delay / dt) + 1);
      let a = 1, r = 0, pts = [[X(a), Y(r)]], Vend = V(1, 0), out = false;
      for (let n = 0, p = 0; n < 10000 && !out; n++) {
        const q = acc(a, r, buf[p]); r += dt * q; a += dt * r; buf[p] = r; p = (p + 1) % buf.length;
        Vend = V(a, r); out = !isFinite(Vend) || Vend > 1e6;
        if (n % 25 === 0 && Math.abs(a) < TH * 1.2 && Math.abs(r) < WM * 1.2) pts.push([X(a), Y(r)]);
      }
      return { ok, bad, worst, pts, Vend, out };
    }
    function draw() {
      const c = cols(ctx);
      g.clearRect(0, 0, w, h);
      rings.forEach(p => path(g, p, c.mut, 1));
      const key = kd + '/' + delay, m = memo[key] || (memo[key] = field());
      [[m.ok, c.acc], [m.bad, c.bad]].forEach(([arr, col]) => {   // 색마다 한 번에 그린다
        g.beginPath(); g.strokeStyle = col; g.lineWidth = 1.6; g.setLineDash([]);
        arr.forEach(([x0, y0, ux, uy]) => { g.moveTo(x0 - ux * 5, y0 - uy * 5); g.lineTo(x0 + ux * 5, y0 + uy * 5); }); g.stroke();
        g.beginPath(); g.fillStyle = col;
        arr.forEach(([x0, y0, ux, uy]) => { g.moveTo(x0 + ux * 7, y0 + uy * 7); g.lineTo(x0 + ux * 2 - uy * 3, y0 + uy * 2 + ux * 3); g.lineTo(x0 + ux * 2 + uy * 3, y0 + uy * 2 - ux * 3); }); g.fill();
      });
      path(g, m.pts, c.fg, 2); g.beginPath(); g.arc(X(1), Y(0), 4, 0, 6.3); g.fillStyle = c.fg; g.fill();
      const bad = m.bad.length, tot = bad + m.ok.length, worst = m.worst, Vend = m.Vend, out = m.out;
      tx(g, ctx.t('black: run from the dot (θ across, ω up)', '검정: 점에서 출발한 궤적 (가로 θ, 세로 ω)'), w / 2, h - 8, c.fg, 'center');
      ro.textContent = ctx.t(`zero-delay arrows: outward ${bad}/${tot} · worst dV/dt ${worst.toFixed(2)} · delayed run V(10 s)/V(0) = ${out ? 'blew up' : (Vend / V(1, 0)).toPrecision(2)}`,
        `지연 없는 법칙의 화살표: 바깥 ${bad}/${tot} · 최악 dV/dt ${worst.toFixed(2)} · 지연 반영 궤적 V(10 s)/V(0) = ${out ? '발산' : (Vend / V(1, 0)).toPrecision(2)}`);
    }
    ctx.slider('damping gain kd', '댐핑 게인 kd', -1, 6, 0.5, kd, v => { kd = v; ro && soon(); });
    ctx.slider('rate signal delay (s)', '속도 신호 지연 (s)', 0, 0.3, 0.05, delay, v => { delay = v; ro && soon(); });
    ro = ctx.readout(); live(ctx, draw); soon();
  };

  // 07 inertia-by-pose
  window.TOYS['inertia-by-pose'] = (el, ctx) => {
    ctx.title('Where M(q) comes from', 'M(q) 는 어디서 나오나');
    const { g, w, h } = ctx.canvas(360, 230);
    const P = { m1: 1, l1: 0.5, lc1: 0.2, lc2: 0.3, I1: 0.03, I2: 0.05 };
    let m2 = 1.5, q2 = 60, ro;
    const M = (m, q) => { const c = Math.cos(q); return [P.m1 * P.lc1 ** 2 + P.I1 + m * (P.l1 ** 2 + P.lc2 ** 2 + 2 * P.l1 * P.lc2 * c) + P.I2, m * (P.lc2 ** 2 + P.l1 * P.lc2 * c) + P.I2, m * P.lc2 ** 2 + P.I2]; };
    function draw() {
      const c = cols(ctx), L = 36, pw = w - L - 10, X = d => L + (d + 180) / 360 * pw, Y = v => 16 + (3 - v) / 3.5 * 150;
      g.clearRect(0, 0, w, h);
      for (let d = -180; d <= 180; d += 90) { ln(g, X(d), 16, X(d), 166, c.ln); tx(g, d + '°', X(d), 186, c.mut, d < 0 ? 'left' : d > 0 ? 'right' : 'center'); }
      ln(g, L, Y(0), L + pw, Y(0), c.mut, 1.2, [4, 3]);
      [0, 1, 2, 3].forEach(v => tx(g, v, L - 5, Y(v) + 4, c.mut, 'right'));
      const cur = M(m2, q2 * Math.PI / 180), sty = [[c.acc, [], 'M11'], [c.bad, [6, 3], 'M12'], [c.ok, [2, 3], 'M22']];
      sty.forEach(([col, d, name], k) => {
        const pts = []; for (let a = -180; a <= 180; a += 6) pts.push([X(a), Y(M(m2, a * Math.PI / 180)[k])]);
        path(g, pts, col, 2.2, d); g.beginPath(); g.arc(X(q2), Y(cur[k]), 4, 0, 6.3); g.fillStyle = col; g.fill();
        tx(g, name, L + 4 + k * 46, 30, col);
      });
      ln(g, X(q2), 16, X(q2), 166, c.fg, 1, [2, 3]);
      ro.textContent = ctx.t(`M11 ${cur[0].toFixed(3)} · M12 ${cur[1].toFixed(3)} · M22 ${cur[2].toFixed(3)} kg m² at elbow ${q2}°`, `M11 ${cur[0].toFixed(3)} · M12 ${cur[1].toFixed(3)} · M22 ${cur[2].toFixed(3)} kg m² (팔꿈치 ${q2}°)`);
    }
    ctx.slider('link 2 mass m2 (kg)', '링크 2 질량 m2 (kg)', 0.5, 4, 0.5, m2, v => { m2 = v; ro && draw(); });
    ctx.slider('elbow angle q2 (°)', '팔꿈치 각도 q2 (°)', -180, 180, 5, q2, v => { q2 = v; ro && draw(); });
    ro = ctx.readout(); live(ctx, draw); draw();
  };
})();
