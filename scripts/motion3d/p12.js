// Phase 12: 수업의 두 Euler integrator로 진자 pose와 energy drift를 계산한다.
(() => {
  const I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], J = .05, K = .2, Q0 = 1, DURATION = 10;
  const energy = (q, w) => .5 * J * w * w + K * (1 - Math.cos(q));
  let cachedDt, cached;
  // Build once per dt change, never integrate the entire history on each animation frame.
  function model(dt) {
    if (dt === cachedDt) return cached;
    const result = {}, e0 = energy(Q0, 0), n = Math.round(DURATION / dt);
    for (const method of ['euler', 'semi']) {
      let q = Q0, w = 0, worst = 0;
      const trace = [{ q, w, energy: e0, worst }];
      for (let i = 0; i < n; i++) {
        const acc = -K / J * Math.sin(q), oldW = w;
        w += dt * acc;
        q += dt * (method === 'euler' ? oldW : w);
        const e = energy(q, w);
        worst = Math.max(worst, Math.abs(e - e0) / e0);
        trace.push({ q, w, energy: e, worst });
      }
      result[method] = trace;
    }
    cachedDt = dt; cached = result;
    return result;
  }
  const point = (x, q) => [x + Math.sin(q), 0, 1 - Math.cos(q)];
  window.MOTION.three('timestep-pendulums-3d', {
    en: 'Two pendulums compare explicit and semi-implicit Euler as timestep grows',
    ko: '두 진자로 timestep에 따른 explicit Euler와 semi-implicit Euler의 차이를 봅니다',
    cap: ['Both start at q=1 rad, at rest, with J=0.05 kg m² and mgl=0.2 Nm from the lesson. Explicit Euler moves q with the old velocity; semi-implicit uses the updated velocity. The displayed maximum energy drift is computed up to the drawn step. Rod length is one drawing unit; it does not specify a physical length.',
      '둘 다 수업의 J=0.05 kg m²와 mgl=0.2 Nm를 쓰며 q=1 rad에서 정지 상태로 출발합니다. Explicit Euler는 이전 velocity로 q를 갱신하고 semi-implicit은 새 velocity를 씁니다. 최대 energy drift는 화면에 그린 step까지 계산합니다. Rod 길이는 그림의 단위 길이이며 실제 길이를 뜻하지 않습니다.'],
    period: 12, rest: 11, H: 390, unit: 78, look: [0, 0, .8], oy: 20,
    cam: { yaw: .1, pitch: .25, dist: 8 }, model,
    controls: [{ id: 'dt', en: 'timestep dt', ko: 'timestep dt', min: .005, max: .2, step: .005, dec: 3, unit: '\u00a0s', val: .05 },
      { id: 'T', en: 'simulation time', ko: '시뮬레이션 시간', min: 0, max: 10, step: .01, dec: 2, unit: '\u00a0s', auto: t => Math.min(10, Math.max(0, t - 1)) }],
  }, (s, t, m) => {
    const traces = model(s.v.dt), index = Math.min(traces.euler.length - 1, Math.floor((s.v.T + 1e-12) / s.v.dt));
    const e = traces.euler[index], h = traces.semi[index], e0 = energy(Q0, 0);
    s.text(14, 24, m.t(`step ${index}, t = ${(index * s.v.dt).toFixed(3)} s`, `step ${index}, t = ${(index * s.v.dt).toFixed(3)} s`), '--fg', 15);
    s.text(14, 46, `Euler: ΔE max ${(e.worst * 100).toFixed(1)}%`, '--bad', 15);
    s.text(14, 68, `Semi: ΔE max ${(h.worst * 100).toFixed(1)}%`, '--ok', 15);
    const configs = [[-1.15, e, '--bad', 'Euler'], [1.15, h, '--ok', 'Semi']];
    for (const [x, state, color, name] of configs) {
      const pivot = [x, 0, 1], tip = point(x, state.q), start = point(x, Q0);
      s.box([x, 0, 1.06], [.16, .16, .06], I, '--mut');
      s.line(pivot, start, '--mut', 2, { dash: [4, 4] });
      s.dot(start, '--mut', 5, { a: .5 });
      s.line(pivot, tip, color, 5); s.box(tip, [.09, .09, .09], I, color);
      // Fixed row below every bob corner over the full pendulum circle.
      s.text(x < 0 ? 110 : 370, 330, name, color, 16, 'center');
    }
    s.text(14, 356, `E₀ = ${e0.toFixed(4)} J`, '--mut', 15);
  });
})();

// 12단계 3D 추가: 시뮬에서 빠진 효과의 비용, 궤적에서 관절 parameter를 맞추는 system identification, 무작위 plant 묶음에 같은 gain을 쓴 결과.
(() => {
  const R = window.M3D, PI = Math.PI, I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const rng = seed => () => { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const gauss = r => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * PI * r());
  function bar(s, x, y, h, half, color, o) { const hh = Math.max(.004, Math.abs(h) / 2); s.box([x, y, h / 2], [half, half, hh], I3, color, o || {}); }

  // ---- 12/01 what a simulator approximates: the same command on the real joint and on a sim missing one effect ----
  const DT = 1e-3, EPS = .01, TS = 6, REAL = {J: .05, b: .02, c: .05, k: .2, Tm: .03, delay: .02}, cacheS = {};
  const cmd = t => .35 * Math.sin(2 * PI * .7 * t) + .15 * Math.sin(2 * PI * 1.9 * t);
  function measured(p) {
    const n = Math.round(TS / DT), q = new Float64Array(n);
    let a = 0, w = 0, tm = 0;
    const f = (a, w, tm, u) => [w, (tm - p.b * w - p.c * Math.tanh(w / EPS) - p.k * Math.sin(a)) / p.J, p.Tm > 0 ? (u - tm) / p.Tm : 0];
    for (let i = 0; i < n; i++) {
      q[i] = a; const u = cmd(i * DT); if (p.Tm === 0) tm = u;
      const k1 = f(a, w, tm, u), k2 = f(a + .5 * DT * k1[0], w + .5 * DT * k1[1], tm + .5 * DT * k1[2], u);
      const k3 = f(a + .5 * DT * k2[0], w + .5 * DT * k2[1], tm + .5 * DT * k2[2], u), k4 = f(a + DT * k3[0], w + DT * k3[1], tm + DT * k3[2], u);
      a += DT / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); w += DT / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); tm += DT / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]);
    }
    const d = Math.round(p.delay / DT), out = new Float64Array(n);
    for (let i = 0; i < n; i++) out[i] = q[Math.max(0, i - d)];
    return out;
  }
  const EFFECTS = [['friction', {b: 0, c: 0}], ['motor lag', {Tm: 0}], ['sensor delay', {delay: 0}], ['all three', {b: 0, c: 0, Tm: 0, delay: 0}]];
  function gap(c) {
    const key = Math.round(c / .005); if (cacheS[key]) return cacheS[key];
    const real = Object.assign({}, REAL, {c}), ref = measured(real), runs = EFFECTS.map(([, off]) => measured(Object.assign({}, real, off)));
    const rms = runs.map(q => Math.sqrt(q.reduce((acc, v, i) => acc + (v - ref[i]) ** 2, 0) / q.length));
    return cacheS[key] = {ref, runs, rms};
  }
  const arm = (s, piv, ang, color, w, a) => {
    const d = [Math.sin(ang), 0, -Math.cos(ang)], tip = R.add(piv, R.mul(d, .75));
    s.box(R.add(piv, R.mul(d, .375)), [.375, .04 * w, .04 * w], R.ry(-Math.atan2(d[2], d[0])), color, {a});
    s.dot(tip, color, 8 * w, {ring: true, a});
  };
  window.MOTION.three('joint-sim-gap-3d', {
    en: 'The same torque command drives a real swinging joint and a simulated copy missing one effect. The bars show how far each missing effect makes the copy drift',
    ko: '같은 토크 명령으로 실제 관절과, 효과 하나가 빠진 시뮬 복사본을 흔듭니다. 막대는 빠진 효과마다 복사본이 얼마나 어긋나는지 보여 줍니다',
    cap: ['The joint from lesson 12/01: J = 0.05, viscous b = 0.02, Coulomb friction c = 0.05 (slider), gravity term 0.2 sin q, motor lag 0.03 s and sensor delay 0.02 s, driven by two sines of 0.35 and 0.15 Nm. The solid arm is the real joint as the encoder reports it; the red ghost is the copy without the effect highlighted in the bar chart (it rotates through the four every 6 s). Bars are RMS angle error over 6 s. At c = 0.05 the lesson gives friction 0.545, motor lag 0.042, sensor delay 0.029 and all three 0.543 rad, so friction is the costly effect. The arm swings in a plane and the bars are scaled 1 rad to 1.4 units.',
      'Lesson 12/01의 관절입니다. J = 0.05, 점성 b = 0.02, Coulomb 마찰 c = 0.05(slider), 중력항 0.2 sin q, 모터 지연 0.03초, 센서 지연 0.02초이고 0.35와 0.15 Nm인 두 sine으로 구동합니다. 실선 팔은 encoder가 보고하는 실제 관절이고 붉은 유령은 막대 그래프에서 강조한 효과를 뺀 복사본입니다(6초마다 네 가지를 차례로 돕니다). 막대는 6초 동안의 RMS 각도 오차입니다. c = 0.05에서 lesson 값은 마찰 0.545, 모터 지연 0.042, 센서 지연 0.029, 셋 모두 0.543 rad이므로 마찰이 비싼 효과입니다. 팔은 한 평면에서 흔들리고 막대는 1 rad을 1.4 단위로 그렸습니다.'],
    period: 24, rest: 2, H: 340, unit: 100, look: [.6, 0, .45], oy: 24,
    cam: {yaw: .25, pitch: .15, dist: 7},
    controls: [{id: 'c', en: 'real Coulomb friction c', ko: '실제 Coulomb 마찰 c', min: 0, max: .1, step: .005, dec: 3, unit: ' Nm', auto: t => .05 + .045 * Math.sin(2 * PI * t / 24)}],
  }, (s, t, m) => {
    const g = gap(s.v.c), ph = t % TS, i = Math.min(g.ref.length - 1, Math.floor(ph / DT)), e = Math.floor(t / TS) % 4, piv = [-1.05, 0, .95];
    s.box([-1.05, 0, .1], [.05, .05, .85], I3, '--pd'); s.box([-1.05, 0, -.74], [.3, .2, .02], I3, '--pd');
    arm(s, piv, g.ref[i], '--pf', 1, 1); arm(s, piv, g.runs[e][i], '--bad', .6, .6);
    s.dot(piv, '--fg', 6, {ring: true, front: true});
    g.rms.forEach((v, k) => {
      const x = .5 + .62 * k, h = v / 1 * 1.4;
      bar(s, x, 0, clamp(h, 0, 1.6), .17, k === e ? '--bad' : '--mut', {a: k === e ? 1 : .55});
      s.label([x, 0, -.12], m.t(['friction', 'motor', 'sensor', 'all'][k], ['마찰', '모터', '센서', '전부'][k]), k === e ? '--bad' : '--mut', 15, 'center');
      s.label([x, 0, clamp(h, 0, 1.6) + .1], v.toFixed(3), k === e ? '--bad' : '--fg', 15, 'center');
    });
    s.text(14, 24, m.t(`friction c = ${s.v.c.toFixed(3)} Nm`, `마찰 c = ${s.v.c.toFixed(3)} Nm`), '--fg', 15);
    s.text(14, 44, m.t(`missing: ${EFFECTS[e][0]}; rms ${g.rms[e].toFixed(3)} rad`, `빠진 효과: ${['마찰', '모터 지연', '센서 지연', '셋 모두'][e]}; rms ${g.rms[e].toFixed(3)} rad`), '--bad', 15);
    s.text(14, 64, m.t('bars: rms angle error over 6 s (rad)', '막대: 6초 동안 rms 각도 오차 (rad)'), '--mut', 15);
  });

  // ---- 12/03 system identification: fit J, b, c, Tm from a recorded run ----
  const TRUE = {J: .05, b: .02, c: .05, Tm: .03}, KG = .2, KV = 3, cacheI = {};
  function experiment(a) {
    const v0 = .3, p = TRUE, n = 20000, rows = new Float64Array(n * 3);   // u, q, w per DT
    const ref = t => v0 + a * (1.5 * Math.sin(.8 * PI * t) + Math.sin(2.6 * PI * t) + .5 * Math.sin(6.2 * PI * t));
    let q = 0, w = v0, tm = p.b * v0 + p.c;
    const f = (q, w, tm, u) => [w, (tm - p.b * w - p.c * Math.tanh(w / EPS) - KG * Math.sin(q)) / p.J, (u - tm) / p.Tm];
    for (let i = 0; i < n; i++) {
      const u = KV * (ref(i * DT) - w) + KG * Math.sin(q); rows[3 * i] = u; rows[3 * i + 1] = q; rows[3 * i + 2] = w;
      const k = f(q, w, tm, u), h = f(q + .5 * DT * k[0], w + .5 * DT * k[1], tm + .5 * DT * k[2], u);
      q += DT * h[0]; w += DT * h[1]; tm += DT * h[2];
    }
    return rows;
  }
  function fit(rows) {
    const rn = rng(12345), step = 2, n = rows.length / 3 / step, dt = step * DT, u = new Float64Array(n), q = new Float64Array(n), w = new Float64Array(n);
    for (let i = 0; i < n; i++) { u[i] = rows[3 * i * step]; q[i] = rows[3 * i * step + 1] + 1e-4 * gauss(rn); w[i] = rows[3 * i * step + 2] + .01 * gauss(rn); }
    const cum = y => { const c = new Float64Array(n); for (let i = 1; i < n; i++) c[i] = c[i - 1] + .5 * (y[i] + y[i - 1]) * dt; return c; };
    const iw = cum(w), isg = cum(w.map(v => Math.tanh(v / EPS))), win = 25, cnt = Math.floor((n - 1 - win) / win) + 1, best = {res: 1e99};
    for (let g = 0; g <= 50; g++) {
      const Tm = g * .002, al = Math.exp(-dt / Tm), lag = new Float64Array(n);
      if (Tm <= 0) lag.set(u); else for (let i = 1; i < n; i++) lag[i] = al * lag[i - 1] + (1 - al) * u[i - 1];
      const ig = cum(lag.map((v, i) => v - KG * Math.sin(q[i]))), X = [], y = [];
      for (let k = 0; k < cnt; k++) { const i = k * win; X.push([ig[i + win] - ig[i], -(iw[i + win] - iw[i]), -(isg[i + win] - isg[i])]); y.push(w[i + win] - w[i]); }
      const nm = [0, 1, 2].map(j => Math.sqrt(X.reduce((a, r) => a + r[j] * r[j], 0))), Gm = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], rhs = [0, 0, 0];
      X.forEach((r, k) => { for (let a = 0; a < 3; a++) { rhs[a] += r[a] / nm[a] * y[k]; for (let b = 0; b < 3; b++) Gm[a][b] += r[a] * r[b] / nm[a] / nm[b]; } });
      const th = R.cross, c0 = [Gm[0][0], Gm[1][0], Gm[2][0]], c1 = [Gm[0][1], Gm[1][1], Gm[2][1]], c2 = [Gm[0][2], Gm[1][2], Gm[2][2]], D = R.dot(c0, th(c1, c2));
      const sol = [R.dot(rhs, th(c1, c2)) / D, R.dot(c0, th(rhs, c2)) / D, R.dot(c0, th(c1, rhs)) / D];
      const res = X.reduce((a, r, k) => a + (y[k] - r.reduce((z, v, j) => z + v * sol[j] / nm[j], 0)) ** 2, 0);
      if (res < best.res) { const e = R.eig3(Gm).w; Object.assign(best, {res, Tm, J: nm[0] / sol[0], th: sol.map((v, j) => v / nm[j]), cond: Math.sqrt(e[0] / e[2])}); }
    }
    const t0 = best.th[0];
    return {J: 1 / t0, b: best.th[1] / t0, c: best.th[2] / t0, Tm: best.Tm, cond: best.cond};
  }
  function ident(a) {
    const key = Math.round(a * 10); if (cacheI[key]) return cacheI[key];
    const rows = experiment(a); return cacheI[key] = {rows, est: fit(rows)};
  }
  window.MOTION.three('excitation-wheel-3d', {
    en: 'A joint is shaken while its angle is recorded, then its inertia, damping and friction are fitted. A slow constant spin cannot tell them apart; a rich shake can',
    ko: '관절을 흔들면서 각도를 기록한 다음 관성, 감쇠, 마찰을 맞춥니다. 천천히 일정하게 돌리면 셋을 구별하지 못하고 풍부하게 흔들면 구별합니다',
    cap: ['Lesson 12/03: the lesson-12/01 joint under a speed loop around 0.3 rad/s plus a three-sine shake of size a, recorded at 500 Hz for 20 s with noise (0.01 rad/s on speed, 1e-4 rad on angle), then fitted by windowed least squares inside a grid search over the motor lag. The bars are the fitted value divided by the true one for J, b and c (grey = 1). The lesson reports condition number 330 and a nonsense b at a = 0 against 4 and a b within 8% at a = 1. The noise here comes from a small JavaScript generator, not numpy, so individual estimates differ from the lesson printout. Off-scale bars are clipped and marked with !. The wheel replays the recorded angle at 2x speed.',
      'Lesson 12/03입니다. Lesson 12/01의 관절에 0.3 rad/s 주변의 speed loop와 크기 a의 세 sine 흔들기를 가해 20초 동안 500 Hz로 기록하고 잡음(속도 0.01 rad/s, 각도 1e-4 rad)을 더한 뒤 모터 지연에 대한 격자 탐색 안에서 구간별 최소제곱으로 맞춥니다. 막대는 J, b, c의 추정값을 참값으로 나눈 값입니다(회색 = 1). Lesson은 a = 0에서 조건수 330과 엉터리 b, a = 1에서 조건수 4와 8% 이내의 b를 보고합니다. 여기의 잡음은 numpy가 아니라 작은 JavaScript 난수 발생기에서 나오므로 개별 추정값은 lesson 출력과 조금 다릅니다. 범위를 넘는 막대는 잘라서 !로 표시합니다. 바퀴는 기록된 각도를 2배 속도로 다시 재생합니다.'],
    period: 16, rest: 8, H: 340, unit: 105, look: [.5, 0, .3], oy: 24,
    cam: {yaw: .25, pitch: .2, dist: 7},
    controls: [{id: 'a', en: 'shake size a', ko: '흔드는 크기 a', min: 0, max: 1.5, step: .1, dec: 1, unit: ' rad/s', auto: t => .75 - .75 * Math.cos(2 * PI * t / 16)}],
  }, (s, t, m) => {
    const r = ident(s.v.a), e = r.est, n = r.rows.length / 3, i = Math.min(n - 1, Math.floor((t * 2 % 10.5) * 1000)), ang = r.rows[3 * i + 1], c = [-.95, 0, .6];
    const ring = []; for (let k = 0; k <= 32; k++) ring.push([c[0] + .5 * Math.cos(2 * PI * k / 32), 0, c[2] + .5 * Math.sin(2 * PI * k / 32)]);
    s.poly(ring, '--pf', {a: .25, edge: '--pf', w: 3});
    const tip = [c[0] + .45 * Math.sin(ang), 0, c[2] + .45 * Math.cos(ang)];
    s.line(c, tip, '--fg', 4, {front: true}); s.dot(tip, '--bad', 7, {ring: true, front: true}); s.dot(c, '--fg', 6, {ring: true, front: true});
    s.box([c[0], .08, c[2] - .75], [.06, .06, .2], I3, '--pd');
    const props = [['J', est => est.J / TRUE.J], ['b', est => est.b / TRUE.b], ['c', est => est.c / TRUE.c]];
    props.forEach(([nm, fn], k) => {
      const x = .5 + .65 * k, v = fn(e), clipped = v > 3 || v < -1, cv = clamp(v, -1, 3), err = Math.abs(v - 1);
      bar(s, x - .14, 0, .5, .11, '--mut'); bar(s, x + .14, 0, cv * .5, .11, err < .15 ? '--ok' : '--bad');
      s.label([x, 0, -.35], nm, '--fg', 15, 'center'); s.label([x + .14, 0, Math.max(cv * .5, 0) + .12], clipped ? '!' : v.toFixed(2), err < .15 ? '--ok' : '--bad', 15, 'center');
    });
    s.text(14, 24, m.t(`shake a = ${s.v.a.toFixed(1)} rad/s, condition number ${e.cond.toFixed(0)}`, `흔들기 a = ${s.v.a.toFixed(1)} rad/s, 조건수 ${e.cond.toFixed(0)}`), e.cond < 30 ? '--ok' : '--bad', 15);
    s.text(14, 44, `J ${e.J.toFixed(3)}  b ${e.b.toFixed(3)}  c ${e.c.toFixed(3)}  Tm ${e.Tm.toFixed(3)}`, '--mut', 15);
    s.text(14, 64, m.t('true: J 0.050  b 0.020  c 0.050  Tm 0.030', '참값: J 0.050  b 0.020  c 0.050  Tm 0.030'), '--mut', 15);
  });

  // ---- 12/04 domain randomisation: one fixed controller on a swarm of random plants ----
  const NOM = {J: .05, b: .02, c: .05, k: .2, Tm: .03, dl: .02}, KEYS = Object.keys(NOM), NPL = 24, DT2 = 2e-3, NS = 1500, REF = 1, UMAX = 1, cacheD = {};
  const WIDTHS = [0, .15, .3, .6], kpOf = i => 2 * Math.pow(100, i / 17), kdOf = j => .1 * Math.pow(40, j / 17), GAINS = [[3, 9], [6, 13], [5, 12], [3, 10]];
  const rnd = rng(7), U = Array.from({length: NPL}, () => KEYS.map(() => 2 * rnd() - 1));
  function fan(gi, w) {
    const key = gi * 100 + Math.round(w * 20); if (cacheD[key]) return cacheD[key];
    const kp = kpOf(GAINS[gi][0]), kd = kdOf(GAINS[gi][1]), qs = [], ok = [];
    U.forEach(u => {
      const p = {}; KEYS.forEach((k, j) => { p[k] = NOM[k] * (1 + w * u[j]); });
      const d = Math.round(p.dl / DT2), q = new Float32Array(NS), ws = new Float32Array(NS); let a = 0, v = 0, tm = 0, mx = 0, last = -1;
      const f = (a, v, tm, c) => [v, (tm - p.b * v - p.c * Math.tanh(v / EPS) - p.k * Math.sin(a)) / p.J, (c - tm) / p.Tm];
      for (let i = 0; i < NS; i++) {
        q[i] = a; ws[i] = v; const j = Math.max(i - d, 0), c = clamp(kp * (REF - q[j]) - kd * ws[j] + NOM.k * Math.sin(q[j]), -UMAX, UMAX);
        const k1 = f(a, v, tm, c), k2 = f(a + .5 * DT2 * k1[0], v + .5 * DT2 * k1[1], tm + .5 * DT2 * k1[2], c), k3 = f(a + .5 * DT2 * k2[0], v + .5 * DT2 * k2[1], tm + .5 * DT2 * k2[2], c), k4 = f(a + DT2 * k3[0], v + DT2 * k3[1], tm + DT2 * k3[2], c);
        a += DT2 / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); v += DT2 / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); tm += DT2 / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]);
        mx = Math.max(mx, q[i]); if (Math.abs(q[i] - REF) > .05) last = i;
      }
      qs.push(q); ok.push((last + 1) * DT2 <= .8 && mx < 1.05);
    });
    return cacheD[key] = {qs, ok, rate: ok.filter(Boolean).length / NPL, kp, kd};
  }
  window.MOTION.three('gain-fan-3d', {
    en: 'One fixed controller drives 24 slightly different copies of a joint to the same target. Gains tuned on a wider spread of copies hold up when the real joint is off',
    ko: '고정된 controller 하나가 조금씩 다른 관절 24개를 같은 목표로 보냅니다. 더 넓은 범위의 복사본으로 맞춘 gain이 실제 관절이 다를 때 더 잘 버팁니다',
    cap: ['Each thin arm is one random joint: every parameter of the lesson-12/01 joint (J, b, c, gravity, motor lag, sensor delay) is scaled by 1 + spread times a random number in -1 to 1, and all arms run the same PD with gravity feed-forward, torque limit 1 Nm, from rest to 1 rad. Green arms settle inside +-0.05 rad by 0.8 s without passing 1.05 rad; red arms do not. The four gain pairs are the lesson grid-search results for tuning widths 0, 0.15, 0.3 and 0.6, from running its tune with 40 plants. The 24 plants here come from a small JavaScript generator, so the success rate is a sample and differs from the lesson 300-plant figures (0.57, 0.88, 0.99, 1.00 at spread 0.3).',
      '가는 팔 하나가 무작위 관절 하나입니다. Lesson 12/01 관절의 모든 parameter(J, b, c, 중력, 모터 지연, 센서 지연)에 1 + spread 곱하기 -1에서 1 사이 난수를 곱하고, 모든 팔이 같은 PD와 중력 feed-forward, 토크 제한 1 Nm로 정지 상태에서 1 rad까지 갑니다. 초록 팔은 0.8초 안에 +-0.05 rad 안에 들어와 머물고 1.05 rad를 넘지 않은 것이며 빨간 팔은 그렇지 못한 것입니다. 네 gain 쌍은 tuning 폭 0, 0.15, 0.3, 0.6에 대해 lesson의 tune을 plant 40개로 돌려 얻은 격자 탐색 결과입니다. 여기의 plant 24개는 작은 JavaScript 난수에서 나오므로 성공률은 표본이며 lesson의 300개 plant 수치(spread 0.3에서 0.57, 0.88, 0.99, 1.00)와 다릅니다.'],
    period: 16, rest: 2.5, H: 340, unit: 120, look: [.5, 0, .55], oy: 30,
    cam: {yaw: .15, pitch: .15, dist: 7},
    controls: [{id: 'tuned', en: 'gains tuned on spread: 0, .15, .3, .6', ko: 'gain을 맞춘 spread: 0, .15, .3, .6', min: 0, max: 3, step: 1, auto: t => Math.floor(t / 4) % 4},
      {id: 'spread', en: 'real joint spread', ko: '실제 관절의 spread', min: 0, max: .6, step: .05, dec: 2, val: .3}],
  }, (s, t, m) => {
    const gi = Math.round(s.v.tuned), r = fan(gi, s.v.spread), ph = t % 3.6, i = Math.min(NS - 1, Math.floor(ph / DT2)), piv = [-1.05, 0, 1.0], L = .8;
    const px = f => .3 + 1.8 * f, pz = q => .1 + .9 * q;   // step-response plot: time 0 to 3 s, angle 0 to 1.3 rad
    s.box([piv[0], 0, .45], [.05, .05, .5], I3, '--pd'); s.box([piv[0], 0, -.06], [.4, .22, .02], I3, '--pd');
    for (const a of [REF, REF - .05, REF + .05]) s.line(piv, [piv[0] + Math.sin(a) * L * 1.12, 0, 1 - Math.cos(a) * L * 1.12], '--fg', a === REF ? 1.6 : 1, {dash: [4, 4]});
    s.line([px(0), 0, pz(0)], [px(1), 0, pz(0)], '--mut', 1.5); s.line([px(0), 0, pz(0)], [px(0), 0, pz(1.3)], '--mut', 1.5);
    for (const a of [REF - .05, REF + .05]) s.line([px(.8 / 3), 0, pz(a)], [px(1), 0, pz(a)], '--fg', 1, {dash: [4, 4]});
    s.line([px(ph / 3), 0, pz(0)], [px(ph / 3), 0, pz(1.3)], '--mut', 1);
    r.qs.forEach((q, k) => {
      const c = r.ok[k] ? '--ok' : '--bad', tip = [piv[0] + Math.sin(q[i]) * L, 0, 1 - Math.cos(q[i]) * L];
      s.line(piv, tip, c, 1.6, {a: .55}); s.dot(tip, c, 4, {a: .8});
      s.path(Array.from({length: 51}, (_, j) => [px(j / 50), 0, pz(q[Math.min(NS - 1, j * 30)])]), c, 1.3, {a: .6});
    });
    s.label([px(.5), 0, pz(0) - .12], m.t('time 0 to 3 s', '시간 0~3 s'), '--mut', 15, 'center');
    s.dot(piv, '--fg', 6, {ring: true, front: true});
    s.text(14, 24, m.t(`gains tuned on spread ${WIDTHS[gi]}: kp ${r.kp.toFixed(1)}, kd ${r.kd.toFixed(2)}`, `spread ${WIDTHS[gi]}로 맞춘 gain: kp ${r.kp.toFixed(1)}, kd ${r.kd.toFixed(2)}`), '--fg', 15);
    s.text(14, 44, m.t(`real spread ${s.v.spread.toFixed(2)}: ${Math.round(r.rate * NPL)} of ${NPL} settle in time`, `실제 spread ${s.v.spread.toFixed(2)}: ${NPL}개 중 ${Math.round(r.rate * NPL)}개가 제때 안정`), r.rate > .9 ? '--ok' : '--bad', 15);
    s.text(14, 64, m.t(`t = ${ph.toFixed(1)} s; dashed: 1 rad and +-0.05`, `t = ${ph.toFixed(1)} s; 점선: 1 rad와 +-0.05`), '--mut', 15);
  });
})();
