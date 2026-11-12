// 단계 07 토이: ekf-consistency (레슨 07/05). landmark 수와 초기 heading 오차를 바꾸며 EKF 경로, 공분산 타원, NEES 를 본다. 00-core.js 의 ctx 사용
(() => {
  const FONT = '-apple-system,"Pretendard","Noto Sans KR","Apple SD Gothic Neo",system-ui,sans-serif';
  const root = document.documentElement;
  function live(ctx, draw) {
    ctx.onRedraw(draw);
    const mq = matchMedia('(prefers-color-scheme: dark)'), mo = new MutationObserver(draw);
    mq.addEventListener('change', draw); mo.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    ctx.onDispose(() => { mq.removeEventListener('change', draw); mo.disconnect(); });
  }
  // 레슨 main.py 의 상수와 모델 (해석적 Jacobian, Joseph form)
  const DT = 0.1, SV = 0.05, SW = 0.03, U = [1, 0.3], RN = [0.2, 0.03], MAXR = 8;
  const P0 = [[0.09, 0, 0], [0, 0.09, 0], [0, 0, 0.01]];
  const LMS = [[4, 1], [0, 5.5], [-4, 1], [0, -2]];
  const wrap = a => ((a + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
  const mul = (A, B) => A.map(r => B[0].map((_, j) => r.reduce((s, a, k) => s + a * B[k][j], 0)));
  const tr = A => A[0].map((_, j) => A.map(r => r[j]));
  const add = (A, B) => A.map((r, i) => r.map((a, j) => a + B[i][j]));
  const f = (x, u) => [x[0] + u[0] * DT * Math.cos(x[2]), x[1] + u[0] * DT * Math.sin(x[2]), wrap(x[2] + u[1] * DT)];
  const h = (x, lm) => { const dx = lm[0] - x[0], dy = lm[1] - x[1]; return [Math.hypot(dx, dy), wrap(Math.atan2(dy, dx) - x[2])]; };
  function inv(M) {   // 3x3 여인수 역행렬
    const [[a, b, c], [d, e, g], [k, l, m]] = M, A = e * m - g * l, B = g * k - d * m, C = d * l - e * k, det = a * A + b * B + c * C;
    return [[A, c * l - b * m, b * g - c * e], [B, a * m - c * k, c * d - a * g], [C, b * k - a * l, a * e - b * d]].map(r => r.map(v => v / det));
  }
  function predict(x, P, dt = DT) {
    const F = [[1, 0, -U[0] * dt * Math.sin(x[2])], [0, 1, U[0] * dt * Math.cos(x[2])], [0, 0, 1]];
    const G = [[dt * Math.cos(x[2]), 0], [dt * Math.sin(x[2]), 0], [0, dt]], Gq = G.map(r => [r[0] * SV * SV, r[1] * SW * SW]);
    return [f(x, U), add(mul(F, mul(P, tr(F))), mul(Gq, tr(G)))];
  }
  function update(x, P, z, lm) {
    const dx = lm[0] - x[0], dy = lm[1] - x[1], q = dx * dx + dy * dy, r = Math.sqrt(q);
    const H = [[-dx / r, -dy / r, 0], [dy / q, -dx / q, -1]], Ht = tr(H), S = add(mul(H, mul(P, Ht)), [[RN[0] ** 2, 0], [0, RN[1] ** 2]]);
    const dS = S[0][0] * S[1][1] - S[0][1] * S[1][0], Si = [[S[1][1] / dS, -S[0][1] / dS], [-S[1][0] / dS, S[0][0] / dS]];
    const K = mul(P, mul(Ht, Si)), zh = h(x, lm), y = [z[0] - zh[0], wrap(z[1] - zh[1])];   // 각도 차는 감싼다
    const IKH = add([[1, 0, 0], [0, 1, 0], [0, 0, 1]], mul(K, H).map(rw => rw.map(v => -v)));
    const KRK = mul(K, mul([[RN[0] ** 2, 0], [0, RN[1] ** 2]], tr(K)));
    return [x.map((v, i) => v + K[i][0] * y[0] + K[i][1] * y[1]), add(mul(IKH, mul(P, tr(IKH))), KRK)];
  }
  function rng(seed) {   // mulberry32 + Box-Muller
    let s = seed;
    const u = () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return (((t ^ (t >>> 14)) >>> 0) + 1) / 4294967297; };
    return () => Math.sqrt(-2 * Math.log(u())) * Math.cos(2 * Math.PI * u());
  }
  function run(seed, steps, off, lms) {
    const n = rng(seed); let est = [0, 0, 0], P = P0, dr = [0, 0, 0];
    let x = [0.3 * n(), 0.3 * n(), 0.1 * n() + off];
    const out = [[x, est, dr, P]];
    for (let k = 0; k < steps; k++) {
      x = f(x, [U[0] + SV * n(), U[1] + SW * n()]); dr = f(dr, U); [est, P] = predict(est, P);
      lms.forEach(lm => { const z = h(x, lm); if (z[0] < MAXR) [est, P] = update(est, P, [z[0] + RN[0] * n(), z[1] + RN[1] * n()], lm); });
      out.push([x, est, dr, P]);
    }
    return out;
  }
  // 평균 NEES(레슨의 mean_nees 와 같은 정의, 이 토이의 난수 20개 seed). 이전 버전이 계산하던 값을 landmark 1~4개(행), 초기 오차 0.0~1.5 rad(열)로 미리 구워 둔 표
  const NEES = [[2.9, 2.9, 3.6, 5.1, 7.6, 11.4, 16.9, 24.8, 35.8, 50.8, 70.9, 97.3, 131.1, 173.8, 226.1, 288.7], [3, 3, 3.1, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.8, 3.9, 4.1, 4.4, 4.7, 5.1, 5.5],
    [3.1, 3.2, 3.3, 3.3, 3.4, 3.4, 3.4, 3.3, 3.3, 3.4, 3.3, 3.4, 3.5, 3.7, 3.8, 3.9], [2.8, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.7, 2.8, 2.7, 2.7, 2.7, 2.7, 2.7, 2.8]];
  window.TOYS['ekf-consistency'] = (el, ctx) => {
    ctx.title('EKF: honest covariance or a straight-faced lie', 'EKF: 정직한 공분산인가, 태연한 거짓말인가');
    const { g, w, h: H } = ctx.canvas(360, 310);
    const S = 32, X = x => w / 2 + S * x, Y = y => 10 + (7 - y) * S;
    let nl = 4, off = 0, ro, fr; const memo = {};
    const soon = () => { cancelAnimationFrame(fr); fr = requestAnimationFrame(draw); };   // 한 프레임에 한 번만 그린다
    ctx.onDispose(() => cancelAnimationFrame(fr));
    function draw() {
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), bad = ctx.color('--bad'), ln = ctx.color('--line');
      const lms = LMS.slice(0, nl), key = nl + '/' + off, r = memo[key] || (memo[key] = run(3, 80, off, lms));
      g.clearRect(0, 0, w, H);
      const line = (pts, col, wd, dash) => { g.beginPath(); g.setLineDash(dash || []); g.strokeStyle = col; g.lineWidth = wd; g.lineJoin = 'round'; pts.forEach((p, i) => i ? g.lineTo(X(p[0]), Y(p[1])) : g.moveTo(X(p[0]), Y(p[1]))); g.stroke(); g.setLineDash([]); };
      g.globalAlpha = 0.35; line(r.map(q => q[0]), fg, 7); g.globalAlpha = 1;
      line(r.map(q => q[2]), bad, 1.8, [5, 4]); line(r.map(q => q[1]), acc, 2);
      for (let k = 10; k <= 80; k += 10) {   // 2σ 타원: 위치 공분산의 고유 분해
        const [e, P] = [r[k][1], r[k][3]], a = P[0][0], b = P[0][1], d = P[1][1], m = (a + d) / 2, s = Math.hypot((a - d) / 2, b), l1 = m + s, l2 = Math.max(0, m - s), th = 0.5 * Math.atan2(2 * b, a - d);
        g.beginPath(); for (let i = 0; i <= 40; i++) { const t = i / 40 * 2 * Math.PI, u = 8 * Math.sqrt(l1) * Math.cos(t), v = 8 * Math.sqrt(l2) * Math.sin(t); const px = e[0] + u * Math.cos(th) - v * Math.sin(th), py = e[1] + u * Math.sin(th) + v * Math.cos(th); i ? g.lineTo(X(px), Y(py)) : g.moveTo(X(px), Y(py)); }
        g.strokeStyle = acc; g.lineWidth = 1.2; g.stroke();
      }
      lms.forEach(lm => { g.beginPath(); g.moveTo(X(lm[0]), Y(lm[1]) - 8); g.lineTo(X(lm[0]) + 7, Y(lm[1]) + 5); g.lineTo(X(lm[0]) - 7, Y(lm[1]) + 5); g.closePath(); g.fillStyle = fg; g.fill(); });
      g.font = '12.5px ' + FONT; g.textAlign = 'left';
      [[ctx.t('truth', '실제 경로'), mut], [ctx.t('dead reckoning', '추측 항법'), bad], [ctx.t('EKF + 2σ ellipses (drawn 4× larger)', 'EKF + 2σ 타원 (4배 확대)'), acc]].forEach(([s, c], i) => { g.fillStyle = c; g.fillText(s, 8, H - 8 - 16 * i); });
      const v = NEES[nl - 1][Math.round(off * 10)];
      ro.textContent = ctx.t(`mean NEES ${v.toFixed(1)} over this toy's own random draws (consistent: about 3) · ${nl} landmark${nl > 1 ? 's' : ''}, heading start error ${off.toFixed(1)} rad`,
        `평균 NEES ${v.toFixed(1)} (이 토이의 난수 기준, 일관되면 약 3) · landmark ${nl}개, 초기 heading 오차 ${off.toFixed(1)} rad`);
    }
    ctx.slider('landmarks in view', '보이는 landmark 수', 1, 4, 1, nl, v => { nl = v; ro && soon(); });
    ctx.slider('initial heading error (rad)', '초기 heading 오차 (rad)', 0, 1.5, 0.1, off, v => { off = v; ro && soon(); });
    ro = ctx.readout(); live(ctx, draw); soon();
  };
})();
