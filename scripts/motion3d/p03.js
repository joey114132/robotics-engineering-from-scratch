// 03단계 3D: lesson의 질량과 lever arm으로 gravity를 버티는 joint torque를 계산한다.
(() => {
  const R = window.M3D, PI = Math.PI, G = 9.81;
  function pose(deg) {
    const q1 = deg * PI / 180, q2 = -q1 / 2;
    const elbow = [.4 * Math.cos(q1), 0, .4 * Math.sin(q1)];
    const tip = R.add(elbow, [.4 * Math.cos(q1 + q2), 0, .4 * Math.sin(q1 + q2)]);
    const com1 = [.2 * Math.cos(q1), 0, .2 * Math.sin(q1)];
    const com2 = R.add(elbow, [.2 * Math.cos(q1 + q2), 0, .2 * Math.sin(q1 + q2)]);
    const t2 = 1 * .2 * G * Math.cos(q1 + q2);
    return {q: [q1, q2], elbow, tip, com1, com2, torque: [(2 * .2 + 1 * .4) * G * Math.cos(q1) + t2, t2]};
  }
  function torque(s, o, tau, radius, max) {
    if (Math.abs(tau) < 1e-8) return;
    const arc = [], sweep = tau / max * PI * 1.5;
    for (let i = 0; i <= 20; i++) {
      const a = -PI / 2 + sweep * i / 20;
      arc.push(R.add(o, [radius * Math.cos(a), -.025, radius * Math.sin(a)]));
    }
    s.path(arc, '--ok', 3, {front: true});
    s.arrow(arc[19], arc[20], '--ok', 3, {front: true});
  }
  window.MOTION.three('gravity-torque-3d', {
    en: 'A two-link arm changes pose. Downward weight arrows and curved joint arrows show the torque needed to hold it still',
    ko: '두 link로 된 팔의 자세를 바꿉니다. 아래쪽 화살표는 무게이고 joint의 곡선 화살표는 팔을 가만히 버티는 데 필요한 torque입니다',
    cap: ['Weights are m1 g and m2 g at the centres of mass. Green arcs are the holding torques from gravity_torque, opposing gravity. Shaded solid links and joint housings show depth while arrows remain in the motion plane. The lesson uses m1=2, m2=1 kg, l1=0.4, lc1=lc2=0.2 m. Link 2 is drawn with its centre halfway along a 0.4 m link. The pose family is q2 = −q1/2.',
      '무게는 각 centre of mass에 작용하는 m1 g와 m2 g입니다. 초록색 호는 gravity_torque로 구한 holding torque이며 gravity에 맞섭니다. Link와 joint housing의 음영으로 깊이를 보여 주며 화살표는 운동 평면에 둡니다. Lesson의 값은 m1=2, m2=1 kg, l1=0.4, lc1=lc2=0.2 m입니다. 두 번째 link는 길이 0.4 m의 가운데에 질량 중심을 둡니다. 자세는 q2 = −q1/2로 바뀝니다.'],
    period: 12, rest: 3, H: 350, unit: 200, look: [.32, 0, .05], oy: 28,
    cam: {yaw: .25, pitch: .4, dist: 7},
    controls: [{id: 'pose', en: 'q1 (q2 = −q1/2)', ko: 'q1 (q2 = −q1/2)', min: -60, max: 90, step: 1, unit: '°', auto: t => 60 * Math.cos(2 * PI * t / 12)}],
  }, (s, t, m) => {
    const p = s.model = pose(s.v.pose), o = [0, 0, 0];
    for (const [start, end, color] of [[o, p.elbow, '--pf'], [p.elbow, p.tip, '--pl']]) {
      const d = R.sub(end, start), angle = Math.atan2(d[2], d[0]);
      s.box(R.mul(R.add(start, end), .5), [Math.hypot(...d) / 2, .03, .03], R.ry(-angle), color);
    }
    [o, p.elbow].forEach(q => {
      s.box(q, [.04, .055, .04], R.ry(-p.q[0]), '--pd');
      s.dot(q, '--fg', 7, {ring: true, front: true});
    });
    [p.com1, p.com2].forEach((q, i) => {
      s.dot(q, '--bad', 5, {ring: true});
      s.arrow(q, R.add(q, [0, 0, -.1 * (i === 0 ? 2 : 1)]), '--bad', 3);
    });
    torque(s, o, p.torque[0], .12, G); torque(s, p.elbow, p.torque[1], .08, .2 * G);
    s.text(14, 24, m.t('Holding torque counters gravity', 'holding torque가 gravity에 맞섭니다'), '--fg', 15);
    s.text(14, 44, `τ1 = ${p.torque[0].toFixed(3)} Nm`, '--ok', 15);
    s.text(14, 64, `τ2 = ${p.torque[1].toFixed(3)} Nm`, '--ok', 15);
  });
})();

// 03단계 3D (wave 1): sampling limit, impedance, PID windup, computed torque, LQR, arm dynamics, MPC, Lyapunov.
(() => {
  const R = window.M3D, PI = Math.PI, TAU = 2 * PI, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const keep = (cache, key, make) => { if (cache[key]) return cache[key]; if (cache.n > 24) { for (const k in cache) delete cache[k]; cache.n = 0; } cache.n = (cache.n || 0) + 1; return cache[key] = make(); };
  const flat = (s, a, b, c, hw, al) => {   // link lying on a table (x right, y away)
    const d = R.sub(b, a), ang = Math.atan2(d[1], d[0]);
    s.box(R.mul(R.add(a, b), .5), [Math.hypot(d[0], d[1]) / 2, hw, hw * .7], R.rz(ang), c, {a: al == null ? 1 : al});
  };
  const table = (s, cx, cy, hx, hy) => s.poly([[cx - hx, cy - hy, -.03], [cx + hx, cy - hy, -.03], [cx + hx, cy + hy, -.03], [cx - hx, cy + hy, -.03]], '--mut', {a: .1, edge: '--mut'});
  const mm2 = (A, B) => [[A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]], [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]];
  const tr2 = A => [[A[0][0], A[1][0]], [A[0][1], A[1][1]]];

  // ---- 03/01 main.py: pure inertia J = 0.02, torque tau = -kd v held for dt = 1 ms, v+ = v (1 - dt kd / J); smooth r <= 1, chatter r < 2, divergent r >= 2.
  const JS = .02, DTS = .001, TICK = .5, NB = 13;
  window.MOTION.three('damper-ticks-wheel-3d', {
    en: 'A flywheel is braked by a damper whose command is held for one whole tick. A weak damper slows it smoothly, a strong one flips its sign every tick, and a stronger one makes it run away',
    ko: 'Flywheel을 damper로 제동하되 명령을 한 tick 내내 붙들고 있습니다. 약한 damper는 부드럽게 줄이고, 센 damper는 tick마다 부호를 뒤집고, 더 센 damper는 속도를 키웁니다',
    cap: ['Inertia J = 0.02 kg m², tick dt = 1 ms and the command τ = −kd v held for the whole tick, as in step_damper: v ← v (1 − r), r = dt·kd/J. The bars are the speed after each tick, starting at 1 rad/s (green forward, red reversed), and the wheel turns by the same speeds. kd = 10, 30, 50 (r = 0.5, 1.5, 2.5) play in turn; kd = 20 (r = 1) stops it in one tick, and above kd = 40 (r = 2) it grows. Real ticks last 1 ms; here each tick is shown for 0.5 s, and tall bars are clipped.',
      'Inertia J = 0.02 kg m², tick dt = 1 ms이고 명령 τ = −kd v를 tick 내내 붙듭니다. step_damper와 같아서 v ← v (1 − r), r = dt·kd/J 입니다. 막대는 매 tick 뒤의 속도로 1 rad/s에서 시작하며 초록은 정방향, 빨강은 반대 방향이고 바퀴도 같은 속도로 돕니다. kd = 10, 30, 50(r = 0.5, 1.5, 2.5)을 차례로 보여 주고, kd = 20(r = 1)이면 한 tick에 멈추며 kd = 40(r = 2)을 넘으면 속도가 커집니다. 실제 tick은 1 ms이지만 여기서는 tick 하나를 0.5초 동안 보여 주며 너무 큰 막대는 잘랐습니다.'],
    period: 18, rest: 11.9, H: 340, unit: 118, look: [-.05, 0, .1], oy: 30,
    cam: {yaw: .25, pitch: .25, dist: 7},
    controls: [{id: 'kd', en: 'damper gain kd', ko: 'damper gain kd', min: 0, max: 60, step: 1, unit: ' Nm s/rad', val: 30, auto: t => t < 6 ? 10 : t < 12 ? 30 : 50}],
  }, (s, t, m) => {
    const kd = s.v.kd, r = DTS * kd / JS, n = Math.min(NB - 1, Math.floor((t % 6) / TICK)), frac = ((t % 6) / TICK) % 1;
    const v = k => Math.pow(1 - r, k), hub = [-1.5, 0, 0];
    let ang = 0; for (let k = 0; k < n; k++) ang += clamp(v(k), -3, 3) * .5;
    ang += clamp(v(n), -3, 3) * .5 * frac;
    s.path(Array.from({length: 49}, (_, i) => [hub[0] + .38 * Math.cos(i * TAU / 48), 0, .38 * Math.sin(i * TAU / 48)]), '--pf', 4);
    for (let k = 0; k < 3; k++) s.line(hub, [hub[0] + .38 * Math.cos(ang + k * TAU / 3), 0, .38 * Math.sin(ang + k * TAU / 3)], '--pl', 3);
    s.dot(hub, '--fg', 6, {ring: true, front: true});
    s.line([-.95, 0, 0], [1.65, 0, 0], '--mut', 1.5);
    for (let k = 0; k <= n; k++) {
      const x = -.8 + .2 * k, h = clamp(v(k), -1.6, 1.6) * .55, c = v(k) >= 0 ? '--ok' : '--bad';
      s.box([x, 0, h / 2], [.07, .07, Math.abs(h) / 2 + .004], I, c);
      if (k === n) s.dot([x, 0, h], '--fg', 4, {front: true});
    }
    const cls = r <= 1 + 1e-9 ? m.t('smooth', 'smooth') : r < 2 ? m.t('chatter', 'chatter') : m.t('divergent', 'divergent');
    s.text(14, 24, `kd = ${kd}  →  r = dt·kd/J = ${r.toFixed(2)}`, '--fg', 15);
    s.text(14, 44, `${cls}:  v after tick ${n} = ${v(n).toFixed(3)} rad/s`, r < 1 + 1e-9 ? '--ok' : r < 2 ? '--acc' : '--bad', 15);
  });

  // ---- 03/03 main.py simulate(): J = 1, constant external torque 2 Nm, q_des = 0, tau = K (q_des - q) - D qd, D = 2 zeta sqrt(K J), semi-implicit Euler dt = 1 ms.
  const FEXT = 2, EX = 8, imp = {};
  const impRun = (K, z) => keep(imp, K + '|' + Math.round(z * 100), () => {
    const D = 2 * z * Math.sqrt(K), n = 6000, q = new Float32Array(n); let a = 0, w = 0, peak = 0;
    for (let i = 0; i < n; i++) { w += .001 * (K * -a - D * w + FEXT); a += .001 * w; q[i] = a; peak = Math.max(peak, a); }
    return {q, peak, D};
  });
  window.MOTION.three('impedance-spring-joint-3d', {
    en: 'A lever is held by a virtual spring and damper while a steady push acts on its tip. The spring sets how far it gives way and the damper sets how it settles',
    ko: '레버를 가상 spring과 damper로 붙들고 끝에 일정한 힘을 가합니다. Spring은 얼마나 밀리는지를, damper는 어떻게 자리를 잡는지를 정합니다',
    cap: ['Joint inertia J = 1 kg m², constant external torque 2 Nm, target 0, control τ = K(q_des − q) − D q̇ with D = 2ζ√(KJ) and gravity cancelled, as in simulate(). It settles at F/K (0.02 rad for K = 100) and ζ = 0.2 overshoots by about 53%. The green zigzag is the virtual spring. The deflection is drawn 8 times larger than real so it can be seen. ζ = 0.2, 0.6, 1.0 play in turn.',
      'Joint inertia J = 1 kg m², 일정한 외부 torque 2 Nm, 목표 0, 제어 τ = K(q_des − q) − D q̇, D = 2ζ√(KJ)이며 gravity는 상쇄했습니다. simulate()와 같습니다. 결과는 F/K(K = 100이면 0.02 rad)에 자리를 잡고 ζ = 0.2이면 약 53% overshoot합니다. 초록 지그재그가 가상 spring입니다. 처짐은 눈에 보이도록 실제보다 8배 크게 그렸습니다. ζ = 0.2, 0.6, 1.0을 차례로 보여 줍니다.'],
    period: 18, rest: 5, H: 340, unit: 150, look: [.35, 0, .05], oy: 30,
    cam: {yaw: .3, pitch: .3, dist: 7},
    controls: [
      {id: 'K', en: 'stiffness K', ko: '강성 K', min: 20, max: 300, step: 5, unit: ' Nm/rad', val: 100},
      {id: 'z', en: 'damping ratio ζ', ko: 'damping ratio ζ', min: .1, max: 1.5, step: .05, dec: 2, val: .2, auto: t => t < 6 ? .2 : t < 12 ? .6 : 1},
    ],
  }, (s, t, m) => {
    const K = Math.round(s.v.K), z = s.v.z, run = impRun(K, z), i = Math.min(5999, Math.floor((t % 6) * 1000)), q = run.q[i], a = EX * q, LEN = .9;
    const tip = [LEN * Math.cos(a), 0, LEN * Math.sin(a)], rest = [LEN, 0, 0];
    s.box([-.12, 0, 0], [.06, .12, .25], I, '--pd');
    s.line([0, 0, 0], rest, '--mut', 1.5, {dash: [4, 4]});
    s.box(R.mul(tip, .5), [LEN / 2, .03, .03], R.ry(-a), '--pf');
    const coil = Array.from({length: 25}, (_, k) => { const u = k / 24, o = (k % 2 ? .05 : -.05) * (k > 0 && k < 24); return [rest[0] + (tip[0] - rest[0]) * u + o, 0, rest[2] + (tip[2] - rest[2]) * u]; });
    s.path(coil, '--ok', 2.5);
    s.dot([0, 0, 0], '--fg', 7, {ring: true, front: true}); s.dot(tip, '--acc', 7, {ring: true, front: true});
    s.arrow([tip[0], 0, tip[2] - .3], [tip[0], 0, tip[2] - .02], '--bad', 4, {front: true});
    s.text(14, 24, `K = ${K}, ζ = ${z.toFixed(2)}, D = ${run.D.toFixed(1)} Nm s/rad`, '--fg', 15);
    s.text(14, 44, `q = ${q.toFixed(4)} rad  (F/K = ${(FEXT / K).toFixed(4)})`, '--ok', 15);
    s.text(14, 64, `${m.t('peak', '최대')} ${run.peak.toFixed(4)} rad  (${Math.max(0, (run.peak / (FEXT / K) - 1) * 100).toFixed(0)}% ${m.t('over', '초과')})`, '--bad', 15);
  });

  // ---- 03/04 main.py simulate() with the windup case of figure.py: J = 1, b = 2, kp = 100, ki = 300, kd = 20, target 2 rad, |u| <= 20 Nm, dt = 1 ms, 12 s.
  const pidc = {};
  const pidRun = (ki, aw) => keep(pidc, ki + (aw ? 'a' : 'w'), () => {
    const n = 12000, q = new Float32Array(n), u = new Float32Array(n), Iw = new Float32Array(n); let a = 0, v = 0, ii = 0, peak = 0;
    for (let k = 0; k < n; k++) {
      const e = 2 - a, raw = 100 * e + ii - 20 * v, uu = clamp(raw, -20, 20);
      if (!aw || uu === raw || e * raw < 0) ii += ki * e * .001;
      v += .001 / 1 * (uu - 2 * v); a += .001 * v; q[k] = a; u[k] = uu; Iw[k] = ii; peak = Math.max(peak, a);
    }
    return {q, u, I: Iw, peak};
  });
  window.MOTION.three('pid-windup-lever-3d', {
    en: 'A saturated motor drives a lever to a target while the integral term keeps piling up. Without anti-windup the lever overshoots far past the target',
    ko: '포화된 motor가 레버를 목표로 보내는 동안 적분 항은 계속 쌓입니다. Anti-windup이 없으면 레버가 목표를 크게 지나칩니다',
    cap: ['Lesson windup case: J = 1 kg m², friction b = 2, kp = 100, ki = 300, kd = 20, target 2 rad, motor limit 20 Nm, 1 ms steps. The ghost lever is the target. The curve is q(t) over 12 s; the dashed line is the target. Without anti-windup the integral term grows while the motor is saturated and the lever passes the target by about 1.5 rad; with it (clamping) the integrator stops while saturated. The scene alternates between the two. The red arc is the motor torque.',
      'Lesson의 windup 경우입니다. J = 1 kg m², 마찰 b = 2, kp = 100, ki = 300, kd = 20, 목표 2 rad, motor 한계 20 Nm, 1 ms step입니다. 흐린 레버가 목표입니다. 곡선은 12초 동안의 q(t)이고 점선이 목표입니다. Anti-windup이 없으면 motor가 포화된 동안 적분 항이 커져서 레버가 목표를 약 1.5 rad 지나치고, anti-windup(clamping)을 쓰면 포화된 동안 적분을 멈춥니다. 두 경우를 번갈아 보여 줍니다. 빨간 호는 motor torque입니다.'],
    period: 24, rest: 11.9, H: 350, unit: 105, look: [.45, 0, .1], oy: 30,
    cam: {yaw: .25, pitch: .2, dist: 7},
    controls: [
      {id: 'ki', en: 'integral gain ki', ko: 'integral gain ki', min: 0, max: 400, step: 10, val: 300},
      {id: 'aw', toggle: true, en: 'anti-windup', ko: 'anti-windup', val: false, auto: t => Math.floor(t / 12) % 2 === 1},
    ],
  }, (s, t, m) => {
    const run = pidRun(Math.round(s.v.ki), s.v.aw), i = Math.min(11999, Math.floor((t % 12) * 1000)), q = run.q[i], piv = [-1.1, 0, 0], LEN = .6;
    const at = a => [piv[0] + LEN * Math.cos(a), 0, LEN * Math.sin(a)];
    s.box([piv[0], 0, -.25], [.1, .1, .25], I, '--pd');
    s.line(piv, at(2), '--mut', 4, {a: .5}); s.dot(at(2), '--mut', 6);
    s.box(R.mul(R.add(piv, at(q)), .5), [LEN / 2, .03, .03], R.ry(-q), s.v.aw ? '--ok' : '--pf');
    s.dot(piv, '--fg', 6, {ring: true, front: true});
    const sat = Math.abs(run.u[i]) >= 19.99, arcP = [];
    for (let k = 0; k <= 16; k++) { const a = -PI / 2 + run.u[i] / 20 * PI * 1.2 * k / 16; arcP.push([piv[0] + .2 * Math.cos(a), -.03, .2 * Math.sin(a)]); }
    if (Math.abs(run.u[i]) > .01) { s.path(arcP, sat ? '--bad' : '--ok', 3, {front: true}); s.arrow(arcP[15], arcP[16], sat ? '--bad' : '--ok', 3, {front: true}); }
    const X = k => -.15 + 2.2 * k / 12000, Z = a => (a - 2) * .26;
    s.line([X(0), 0, Z(0)], [X(12000), 0, Z(0)], '--mut', 1.5, {dash: [5, 4]}); s.line([X(0), 0, Z(-.5)], [X(0), 0, Z(4)], '--mut', 1.5);
    const pts = []; for (let k = 0; k <= i; k += 100) pts.push([X(k), 0, Z(run.q[k])]);
    if (pts.length > 1) s.path(pts, s.v.aw ? '--ok' : '--pf', 3);
    s.dot([X(i), 0, Z(q)], '--acc', 5, {ring: true, front: true});
    s.text(14, 24, `${s.v.aw ? m.t('anti-windup ON', 'anti-windup 켬') : m.t('anti-windup OFF', 'anti-windup 끔')},  t = ${(i / 1000).toFixed(1)} s`, s.v.aw ? '--ok' : '--bad', 15);
    s.text(14, 44, `q = ${q.toFixed(2)} rad,  I = ${run.I[i].toFixed(0)} Nm,  u = ${run.u[i].toFixed(0)} Nm`, '--fg', 15);
    s.text(14, 64, `${m.t('overshoot', 'overshoot')} = ${Math.max(0, run.peak - 2).toFixed(2)} rad`, '--bad', 15);
  });

  // ---- 03/05 main.py: horizontal 2-link arm, M and Coriolis from the lesson, 1 s trajectory, OMEGA = 20, RK4 dt = 1 ms, controller sees a model, the plant is PARAMS.
  const P5 = {m1: 1, m2: 1, l1: .5, lc1: .25, lc2: .25, I1: .02, I2: .02}, OM = 20, AMP = [1.2, 1.5], DT5 = .001, N5 = 2000;
  const mass5 = (q, p) => { const c2 = Math.cos(q[1]), a = p.m2 * p.l1 * p.lc2 * c2, m22 = p.I2 + p.m2 * p.lc2 ** 2; return [[p.I1 + p.m1 * p.lc1 ** 2 + p.m2 * (p.l1 ** 2 + p.lc2 ** 2) + p.I2 + 2 * a, m22 + a], [m22 + a, m22]]; };
  const cor5 = (q, w, p) => { const h = p.m2 * p.l1 * p.lc2 * Math.sin(q[1]); return [-h * (2 * w[0] * w[1] + w[1] ** 2), h * w[0] ** 2]; };
  const traj = t => { const c = Math.cos(TAU * t), sn = Math.sin(TAU * t); return [AMP.map(a => a * (1 - c) / 2), AMP.map(a => a * TAU * sn / 2), AMP.map(a => a * TAU * TAU * c / 2)]; };
  const fwd5 = (q, w, tau) => { const M = mass5(q, P5), h = cor5(q, w, P5), b = [tau[0] - h[0], tau[1] - h[1]], d = M[0][0] * M[1][1] - M[0][1] * M[1][0]; return [(M[1][1] * b[0] - M[0][1] * b[1]) / d, (M[0][0] * b[1] - M[1][0] * b[0]) / d]; };
  const ct5 = (q, w, ref, mdl) => { const M = mass5(q, mdl), h = cor5(q, w, mdl), u = [0, 1].map(i => ref[2][i] + 2 * OM * (ref[1][i] - w[i]) + OM * OM * (ref[0][i] - q[i])); return [M[0][0] * u[0] + M[0][1] * u[1] + h[0], M[1][0] * u[0] + M[1][1] * u[1] + h[1]]; };
  const pd5 = (q, w, ref, mdl) => { const M = mass5([.6, .75], mdl); return [0, 1].map(i => M[i][i] * (OM * OM * (ref[0][i] - q[i]) + 2 * OM * (ref[1][i] - w[i]))); };
  const ctc = {};
  const ctRun = err => keep(ctc, err, () => {
    const mdl = Object.assign({}, P5, {m1: P5.m1 * (1 + err / 100), m2: P5.m2 * (1 + err / 100)});
    return [ct5, pd5].map(ctrl => {
      let x = [0, 0, 0, 0], mx = 0; const qs = new Float32Array(2 * N5), es = new Float32Array(N5);
      for (let i = 0; i < N5; i++) {
        const ref = traj(i * DT5); qs[2 * i] = x[0]; qs[2 * i + 1] = x[1]; es[i] = Math.hypot(ref[0][0] - x[0], ref[0][1] - x[1]); mx = Math.max(mx, es[i]);
        const f = y => { const a = fwd5([y[0], y[1]], [y[2], y[3]], ctrl([x[0], x[1]], [x[2], x[3]], ref, mdl)); return [y[2], y[3], a[0], a[1]]; };
        const add = (y, d, k) => y.map((v, j) => v + d * k[j]);
        const k1 = f(x), k2 = f(add(x, DT5 / 2, k1)), k3 = f(add(x, DT5 / 2, k2)), k4 = f(add(x, DT5, k3));
        x = x.map((v, j) => v + DT5 / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]));
      }
      return {qs, es, mx};
    });
  });
  const tipOf = (b, q) => { const e = [b[0] + .5 * Math.cos(q[0]), b[1] + .5 * Math.sin(q[0]), .01]; return [e, [e[0] + .5 * Math.cos(q[0] + q[1]), e[1] + .5 * Math.sin(q[0] + q[1]), .01]]; };
  window.MOTION.three('computed-torque-pair-3d', {
    en: 'Three copies of a two-link arm on a table follow a fast swing: the reference, an arm with plain PD, and an arm with computed torque. PD lags where the model is not used',
    ko: '탁자 위의 두 link 팔 세 개가 빠른 swing을 따라갑니다. 기준 궤적, 단순 PD 팔, computed torque 팔입니다. 모델을 쓰지 않는 PD가 뒤처집니다',
    cap: ['Lesson arm: m1 = m2 = 1 kg, l1 = 0.5 m, lc1 = lc2 = 0.25 m, I = 0.02, no gravity (horizontal plane), reference swing of 1.2 and 1.5 rad in 1 s, both controllers tuned to ω = 20 rad/s, simulated with RK4 at 1 ms. Faint grey is the reference; green is computed torque (the model supplies M and Coriolis); red is joint PD with gains fixed at the mean pose. Link 2 is drawn 0.5 m long (twice lc2), which the lesson does not state. The slider makes the controller\'s masses wrong by a percentage while the arm keeps the true ones.',
      'Lesson의 팔은 m1 = m2 = 1 kg, l1 = 0.5 m, lc1 = lc2 = 0.25 m, I = 0.02이고 gravity가 없는(수평면) 경우입니다. 기준 swing은 1초 동안 1.2와 1.5 rad이며 두 controller 모두 ω = 20 rad/s로 맞추고 RK4 1 ms로 simulation합니다. 흐린 회색이 기준이고 초록은 computed torque(모델이 M과 Coriolis를 줍니다), 빨강은 평균 자세에서 gain을 고정한 joint PD입니다. Link 2는 lc2의 두 배인 0.5 m로 그렸으며 lesson에는 없는 값입니다. Slider는 controller가 아는 질량을 실제와 다르게 만들고 팔은 실제 질량을 유지합니다.'],
    period: 2, rest: 1, H: 340, unit: 140, look: [.3, .4, 0], oy: 36,
    cam: {yaw: .1, pitch: 1.0, dist: 7},
    controls: [{id: 'err', en: 'model mass error', ko: '모델 질량 오차', min: -50, max: 50, step: 5, unit: '%', val: 0}],
  }, (s, t, m) => {
    const [ct, pd] = ctRun(Math.round(s.v.err)), i = Math.min(N5 - 1, Math.floor(t / DT5)), b = [0, 0, 0], ref = traj(t)[0];
    table(s, .45, .45, 1.1, 1.0);
    s.path(Array.from({length: 61}, (_, k) => { const q = traj(k / 60)[0]; return tipOf(b, q)[1]; }), '--mut', 2, {dash: [3, 3]});
    [[ref, '--mut', .3], [[pd.qs[2 * i], pd.qs[2 * i + 1]], '--bad', .9], [[ct.qs[2 * i], ct.qs[2 * i + 1]], '--ok', .9]].forEach(([q, c, al], k) => {
      const [e, tp] = tipOf(b, q); flat(s, b, e, c, .03 - k * .004, al); flat(s, e, tp, c, .026 - k * .004, al); s.dot(tp, c, 5, {ring: true, front: true});
    });
    s.box(b, [.06, .06, .04], I, '--pd');
    s.text(14, 24, `${m.t('computed torque', 'computed torque')}: |e| = ${ct.es[i].toFixed(3)} rad  (max ${ct.mx.toFixed(3)})`, '--ok', 14);
    s.text(14, 44, `joint PD: |e| = ${pd.es[i].toFixed(3)} rad  (max ${pd.mx.toFixed(3)})`, '--bad', 14);
    s.text(14, 64, `${m.t('model mass error', '모델 질량 오차')} ${Math.round(s.v.err)}%`, '--mut', 14);
  });

  // ---- 03/06 main.py: double integrator dt = 0.05, Q = diag(1, 0.1), R from the slider (lesson 0.01 and 1.0), DARE by backward Riccati recursion.
  const AL = [[1, .05], [0, 1]], BL = [.05 * .05 / 2, .05], QL = [[1, 0], [0, .1]], lq = {};
  function lqr(R_) {
    let P = QL.map(r => r.slice()), K = [0, 0];
    for (let it = 0; it < 100000; it++) {
      const bP = [BL[0] * P[0][0] + BL[1] * P[1][0], BL[0] * P[0][1] + BL[1] * P[1][1]], S = R_ + bP[0] * BL[0] + bP[1] * BL[1];
      K = [(bP[0] * AL[0][0] + bP[1] * AL[1][0]) / S, (bP[0] * AL[0][1] + bP[1] * AL[1][1]) / S];
      const Ac = [[AL[0][0] - BL[0] * K[0], AL[0][1] - BL[0] * K[1]], [AL[1][0] - BL[1] * K[0], AL[1][1] - BL[1] * K[1]]], T = mm2(mm2(tr2(AL), P), Ac);
      const Pn = [[QL[0][0] + T[0][0], QL[0][1] + T[0][1]], [QL[1][0] + T[1][0], QL[1][1] + T[1][1]]];
      const done = Math.max(Math.abs(Pn[0][0] - P[0][0]), Math.abs(Pn[0][1] - P[0][1]), Math.abs(Pn[1][0] - P[1][0]), Math.abs(Pn[1][1] - P[1][1])) < 1e-12;
      P = Pn; if (done) break;
    }
    const bP = [BL[0] * P[0][0] + BL[1] * P[1][0], BL[0] * P[0][1] + BL[1] * P[1][1]], S = R_ + bP[0] * BL[0] + bP[1] * BL[1];
    return [(bP[0] * AL[0][0] + bP[1] * AL[1][0]) / S, (bP[0] * AL[0][1] + bP[1] * AL[1][1]) / S];
  }
  const lqrRun = lr => keep(lq, Math.round(lr * 10), () => {
    const R_ = Math.pow(10, Math.round(lr * 10) / 10), K = lqr(R_), xs = [], us = []; let x = [1, 0], cost = 0, peak = 0;
    for (let k = 0; k < 100; k++) {
      const u = -(K[0] * x[0] + K[1] * x[1]); xs.push(x); us.push(u); peak = Math.max(peak, Math.abs(u));
      cost += x[0] * x[0] + .1 * x[1] * x[1] + R_ * u * u; x = [AL[0][0] * x[0] + AL[0][1] * x[1] + BL[0] * u, AL[1][0] * x[0] + AL[1][1] * x[1] + BL[1] * u];
    }
    return {K, xs, us, cost, peak, R_};
  });
  window.MOTION.three('lqr-cart-rail-3d', {
    en: 'A cart on a rail is pulled back to the origin by the gain LQR computes. A cheap effort weight makes it brisk and a costly one makes it gentle',
    ko: '레일 위의 cart를 LQR이 계산한 gain으로 원점까지 끌어옵니다. 노력 가중치가 싸면 빠르고 비싸면 느긋합니다',
    cap: ['Double integrator with dt = 0.05 s (position and speed, the input is an acceleration held for one step) and Q = diag(1, 0.1), as in the lesson. The slider is the effort weight R from 0.01 to 1, the two values the lesson prints. K comes from the Riccati recursion and u = −Kx. The cart starts 1 m from the target at rest (a start the lesson does not give); the dots show where it has been and the green arrow is the push u (clipped for length). Cost is the sum of xᵀQx + uᵀRu over 5 s. No input limit, as in the lesson rollout.',
      'Lesson과 같이 dt = 0.05 s의 double integrator(위치와 속도, 입력은 한 step 동안 붙드는 가속도)와 Q = diag(1, 0.1)입니다. Slider는 노력 가중치 R로 0.01부터 1까지이며 lesson이 출력하는 두 값을 포함합니다. K는 Riccati recursion으로 구하고 u = −Kx 입니다. Cart는 목표에서 1 m 떨어진 정지 상태에서 출발하며(lesson이 주지 않은 시작점) 점은 지나온 자리, 초록 화살표는 미는 힘 u입니다(길이는 잘랐습니다). Cost는 5초 동안 xᵀQx + uᵀRu의 합입니다. Lesson의 rollout처럼 입력 한계는 없습니다.'],
    period: 14, rest: 13.9, H: 320, unit: 120, look: [0, 0, 0], oy: 20,
    cam: {yaw: .3, pitch: .35, dist: 7},
    controls: [{id: 'lr', en: 'effort weight R (log10)', ko: '노력 가중치 R (log10)', min: -2, max: 0, step: .1, dec: 1, val: -2, auto: t => t < 7 ? -2 : 0}],
  }, (s, t, m) => {
    const run = lqrRun(s.v.lr), f = Math.min(99, (t % 7) / .05), k = Math.floor(f), k2 = Math.min(99, k + 1), x = run.xs[k][0] + (run.xs[k2][0] - run.xs[k][0]) * (f - k);
    s.box([0, 0, -.12], [1.45, .12, .02], I, '--mut', {a: .6});
    s.line([0, -.12, -.1], [0, -.12, .5], '--ok', 3); s.dot([0, -.12, .5], '--ok', 6, {ring: true});
    for (let i = 0; i <= k; i += 3) s.dot([run.xs[i][0], .2, -.08], '--acc', 3, {a: .6});
    s.box([x, 0, .06], [.2, .12, .12], I, '--pf');
    s.dot([x - .12, 0, -.08], '--fg', 6, {ring: true}); s.dot([x + .12, 0, -.08], '--fg', 6, {ring: true});
    const u = run.us[k], len = clamp(u * .12, -.8, .8);
    if (Math.abs(len) > .01) s.arrow([x, 0, .32], [x + len, 0, .32], '--ok', 4, {front: true});
    s.text(14, 24, `R = ${run.R_.toFixed(3)},  K = (${run.K[0].toFixed(3)}, ${run.K[1].toFixed(3)})`, '--fg', 15);
    s.text(14, 44, `x = ${x.toFixed(3)} m,  u = ${u.toFixed(2)} m/s²`, '--ok', 15);
    s.text(14, 64, `${m.t('cost', 'cost')} = ${run.cost.toFixed(2)},  ${m.t('peak', '최대')} |u| = ${run.peak.toFixed(1)}`, '--mut', 14);
  });

  // ---- 03/07 main.py: kinetic(), mass() by polarisation, lagrange_tau() with numeric derivatives, newton_euler(); figure.py arm P and start q = (0.3, 1.0), qd = (2, -1), RK4 dt = 2 ms, free motion.
  const P7 = {m1: 1, m2: 1.5, l1: .5, lc1: .2, lc2: .3, I1: .03, I2: .05}, E7 = 1e-6;
  const kin7 = (q, w, p) => { const pr = a => [-Math.sin(a), Math.cos(a)], a = pr(q[0]), b = pr(q[0] + q[1]), v1 = [p.lc1 * w[0] * a[0], p.lc1 * w[0] * a[1]], v2 = [p.l1 * w[0] * a[0] + p.lc2 * (w[0] + w[1]) * b[0], p.l1 * w[0] * a[1] + p.lc2 * (w[0] + w[1]) * b[1]];
    return .5 * (p.m1 * (v1[0] ** 2 + v1[1] ** 2) + p.m2 * (v2[0] ** 2 + v2[1] ** 2) + p.I1 * w[0] ** 2 + p.I2 * (w[0] + w[1]) ** 2); };
  const mass7 = (q, p) => { const T = v => kin7(q, v, p), off = T([1, 1]) - T([1, 0]) - T([0, 1]); return [[2 * T([1, 0]), off], [off, 2 * T([0, 1])]]; };
  const lag7 = (q, w, a, p, sg) => {
    const dM = [0, 1].map(k => { const e = [0, 0]; e[k] = E7; const A = mass7([q[0] + e[0], q[1] + e[1]], p), B = mass7([q[0] - e[0], q[1] - e[1]], p); return A.map((r, i) => r.map((v, j) => (v - B[i][j]) / (2 * E7))); });
    const dT = [0, 1].map(k => { const e = [0, 0]; e[k] = E7; return (kin7([q[0] + e[0], q[1] + e[1]], w, p) - kin7([q[0] - e[0], q[1] - e[1]], w, p)) / (2 * E7); });
    const dMdt = [0, 1].map(i => [0, 1].map(j => dM[0][i][j] * w[0] + dM[1][i][j] * w[1])), M = mass7(q, p);
    return [0, 1].map(i => M[i][0] * a[0] + M[i][1] * a[1] + sg * (dMdt[i][0] * w[0] + dMdt[i][1] * w[1] - dT[i]));
  };
  const ne7 = (q, w, a, p) => {
    const perp = v => [-v[1], v[0]], cr = (u, v) => u[0] * v[1] - u[1] * v[0], u1 = [Math.cos(q[0]), Math.sin(q[0])], u12 = [Math.cos(q[0] + q[1]), Math.sin(q[0] + q[1])];
    const w1 = w[0], w2 = w[0] + w[1], al1 = a[0], al2 = a[0] + a[1], r1 = u1.map(v => p.lc1 * v), rj = u1.map(v => p.l1 * v), r2 = u12.map(v => p.lc2 * v);
    const a1 = perp(r1).map((v, i) => al1 * v - w1 * w1 * r1[i]), aj = perp(rj).map((v, i) => al1 * v - w1 * w1 * rj[i]), a2 = perp(r2).map((v, i) => aj[i] + al2 * v - w2 * w2 * r2[i]);
    const f2 = a2.map(v => p.m2 * v), tau2 = p.I2 * al2 + cr(r2, f2), f1 = a1.map((v, i) => p.m1 * v + f2[i]);
    return [p.I1 * al1 + cr(r1, f1) + cr([rj[0] - r1[0], rj[1] - r1[1]], f2) + tau2, tau2];
  };
  let free7 = null;
  const freeRun = () => free7 || (free7 = [1, -1].map(sg => {
    const n = 500, dt = 2e-3, qs = new Float32Array(2 * (n + 1)), ke = new Float32Array(n + 1); let x = [.3, 1, 2, -1];
    const acc = y => { const h = lag7([y[0], y[1]], [y[2], y[3]], [0, 0], P7, sg), M = mass7([y[0], y[1]], P7), d = M[0][0] * M[1][1] - M[0][1] * M[1][0]; return [(-M[1][1] * h[0] + M[0][1] * h[1]) / d, (M[1][0] * h[0] - M[0][0] * h[1]) / d]; };
    const f = y => { const a = acc(y); return [y[2], y[3], a[0], a[1]]; }, ad = (y, d, k) => y.map((v, j) => v + d * k[j]);
    for (let i = 0; i <= n; i++) {
      qs[2 * i] = x[0]; qs[2 * i + 1] = x[1]; ke[i] = kin7([x[0], x[1]], [x[2], x[3]], P7);
      if (i < n) { const k1 = f(x), k2 = f(ad(x, dt / 2, k1)), k3 = f(ad(x, dt / 2, k2)), k4 = f(ad(x, dt, k3)); x = x.map((v, j) => v + dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])); }
    }
    return {qs, ke};
  }));
  const road = (() => { const q = [.3, 1], w = [2, -1], a = [1, -.5], L = lag7(q, w, a, P7, 1), N = ne7(q, w, a, P7); return Math.max(Math.abs(L[0] - N[0]), Math.abs(L[1] - N[1])); })();
  window.MOTION.three('arm-energy-sign-3d', {
    en: 'Two identical arms swing freely with no motor torque. One uses the derived Coriolis term, the other has its sign flipped, and only the first keeps its kinetic energy',
    ko: '모터 torque 없이 똑같은 팔 두 개가 자유롭게 휘두릅니다. 하나는 유도한 Coriolis 항을 쓰고 다른 하나는 부호를 뒤집었으며, 운동 energy를 지키는 것은 앞의 것뿐입니다',
    cap: ['Lesson arm (m1 = 1, m2 = 1.5 kg, l1 = 0.5, lc1 = 0.2, lc2 = 0.3 m, I1 = 0.03, I2 = 0.05) from q = (0.3, 1.0) rad at q̇ = (2, −1) rad/s, no torque, RK4 at 2 ms for 1 s, horizontal plane. Left: τ = M q̈ + h from the Lagrange route. Right: the same with the Coriolis sign flipped. Each bar is the kinetic energy relative to its start; free motion must not gain energy. The text line compares the Lagrange torque with the Newton–Euler torque at one state (q̈ = (1, −0.5)). Link 2 is drawn 0.6 m long (twice lc2), which the lesson does not state.',
      'Lesson의 팔(m1 = 1, m2 = 1.5 kg, l1 = 0.5, lc1 = 0.2, lc2 = 0.3 m, I1 = 0.03, I2 = 0.05)이 q = (0.3, 1.0) rad, q̇ = (2, −1) rad/s에서 torque 없이 1초 동안 움직입니다. RK4 2 ms, 수평면입니다. 왼쪽은 Lagrange 방식의 τ = M q̈ + h를 쓰고, 오른쪽은 Coriolis 부호를 뒤집었습니다. 막대는 시작 값 대비 운동 energy이며 자유 운동에서 energy가 늘면 안 됩니다. 글줄은 한 상태(q̈ = (1, −0.5))에서 Lagrange torque와 Newton–Euler torque를 비교합니다. Link 2는 lc2의 두 배인 0.6 m로 그렸으며 lesson에는 없는 값입니다.'],
    period: 6, rest: 6, H: 340, unit: 130, look: [0, .35, 0], oy: 36,
    cam: {yaw: .1, pitch: 1.0, dist: 7},
    controls: [{id: 'time', en: 'time', ko: '시간', min: 0, max: 1, step: .01, dec: 2, unit: ' s', val: 1, auto: t => Math.min(1, t / 5)}],
  }, (s, t, m) => {
    const runs = freeRun(), i = Math.min(500, Math.round(s.v.time / .002)), ke0 = runs[0].ke[0];
    table(s, 0, .4, 1.4, .9);
    [[-.75, runs[0], '--ok', m.t('correct h', '올바른 h')], [.75, runs[1], '--bad', m.t('flipped sign', '부호 뒤집음')]].forEach(([x, r, c, name], k) => {
      const q = [r.qs[2 * i], r.qs[2 * i + 1]], b = [x, 0, 0], e = [x + .5 * Math.cos(q[0]), .5 * Math.sin(q[0]), .01], tp = [e[0] + .6 * Math.cos(q[0] + q[1]), e[1] + .6 * Math.sin(q[0] + q[1]), .01];
      flat(s, b, e, c, .03); flat(s, e, tp, c, .026); s.box(b, [.05, .05, .04], I, '--pd'); s.dot(tp, c, 5, {ring: true, front: true});
      const h = Math.max(.01, r.ke[i] / ke0 * .3);
      s.box([x, -.35, h / 2], [.06, .06, h / 2], I, c); s.box([x, -.35, .305], [.1, .02, .005], I, '--mut');
      s.text(14, 24 + 20 * k, `${name}: ΔKE = ${(r.ke[i] - ke0 >= 0 ? '+' : '') + (r.ke[i] - ke0).toFixed(3)} J`, c, 15);
    });
    s.text(14, 64, `max |τ Lagrange − τ Newton–Euler| = ${road.toExponential(1)} Nm`, '--mut', 13);
  });

  // ---- 03/08 main.py: double integrator dt = 0.1, Q = diag(1, 0.1), R = 0.1, terminal cost P from the Riccati recursion, x0 = (4, 0), 60 steps, FISTA 800 iterations.
  const AM = [[1, .1], [0, 1]], BM = [.005, .1], QM = [[1, 0], [0, .1]], RM = .1, mp = {};
  const riccP = (() => { let P = QM.map(r => r.slice()); for (let it = 0; it < 3000; it++) { const bP = [BM[0] * P[0][0] + BM[1] * P[1][0], BM[0] * P[0][1] + BM[1] * P[1][1]], S = RM + bP[0] * BM[0] + bP[1] * BM[1], K = [(bP[0] * AM[0][0] + bP[1] * AM[1][0]) / S, (bP[0] * AM[0][1] + bP[1] * AM[1][1]) / S];
    const Ac = [[AM[0][0] - BM[0] * K[0], AM[0][1] - BM[0] * K[1]], [AM[1][0] - BM[1] * K[0], AM[1][1] - BM[1] * K[1]]], T = mm2(mm2(tr2(AM), P), Ac); P = [[QM[0][0] + T[0][0], QM[0][1] + T[0][1]], [QM[1][0] + T[1][0], QM[1][1] + T[1][1]]]; } return P; })();
  const mpcRun = (N, umax) => keep(mp, N + '|' + Math.round(umax * 10), () => {
    const Ap = [[1, 0], [0, 1]], pw = []; let Ak = Ap;   // pw[i] = A^i
    for (let i = 0; i <= N; i++) { pw.push(Ak); Ak = mm2(Ak, AM); }
    const ab = pw.map(P => [P[0][0] * BM[0] + P[0][1] * BM[1], P[1][0] * BM[0] + P[1][1] * BM[1]]), Qi = i => i === N - 1 ? riccP : QM;
    const q2 = (Q, a, b) => a[0] * (Q[0][0] * b[0] + Q[0][1] * b[1]) + a[1] * (Q[1][0] * b[0] + Q[1][1] * b[1]);
    const H = Array.from({length: N}, (_, j) => Array.from({length: N}, (_, k) => { let v = j === k ? RM : 0; for (let i = Math.max(j, k); i < N; i++) v += q2(Qi(i), ab[i - j], ab[i - k]); return v; }));
    let z = Array(N).fill(1), lam = 1; for (let it = 0; it < 80; it++) { const y = H.map(r => r.reduce((a, v, j) => a + v * z[j], 0)); lam = Math.hypot(...y); z = y.map(v => v / lam); }
    const step = 1 / (lam * 1.02), xs = [], us = [], plans = []; let x = [4, 0], cost = 0;
    for (let k = 0; k < 60; k++) {
      const f = Array.from({length: N}, (_, j) => { let v = 0; for (let i = j; i < N; i++) v += q2(Qi(i), ab[i - j], [pw[i + 1][0][0] * x[0] + pw[i + 1][0][1] * x[1], pw[i + 1][1][0] * x[0] + pw[i + 1][1][1] * x[1]]); return v; });
      let U = Array(N).fill(0), Y = U.slice(), tt = 1;
      for (let it = 0; it < 800; it++) {
        const Un = Y.map((y, j) => clamp(y - step * (H[j].reduce((a, v, c) => a + v * Y[c], 0) + f[j]), -umax, umax)), tn = (1 + Math.sqrt(1 + 4 * tt * tt)) / 2;
        Y = Un.map((u, j) => u + (tt - 1) / tn * (u - U[j])); U = Un; tt = tn;
      }
      let px = x.slice(); const path = [];
      for (const u of U) { px = [AM[0][0] * px[0] + AM[0][1] * px[1] + BM[0] * u, AM[1][0] * px[0] + AM[1][1] * px[1] + BM[1] * u]; path.push(px[0]); }
      xs.push(x); us.push(U[0]); plans.push(path); cost += x[0] * x[0] + .1 * x[1] * x[1] + RM * U[0] * U[0];
      x = [AM[0][0] * x[0] + AM[0][1] * x[1] + BM[0] * U[0], AM[1][0] * x[0] + AM[1][1] * x[1] + BM[1] * U[0]];
    }
    return {xs, us, plans, cost};
  });
  window.MOTION.three('mpc-horizon-rail-3d', {
    en: 'A cart on a rail plans a short run of pushes ahead, applies only the first, then plans again. A longer look-ahead brakes earlier, and a push limit forces it to plan around it',
    ko: '레일 위의 cart가 앞으로의 짧은 입력열을 계획하고 첫 입력만 적용한 뒤 다시 계획합니다. 더 멀리 내다보면 일찍 브레이크를 걸고, 입력 한계가 있으면 그것을 피해 계획합니다',
    cap: ['Receding-horizon plan for the lesson double integrator (dt = 0.1 s, Q = diag(1, 0.1), R = 0.1, terminal cost from the Riccati recursion), starting 4 m from the target at rest, 60 steps, each plan found by 800 projected-gradient iterations within |u| ≤ the limit. The orange dots are the positions the current plan predicts; the green arrow is the push actually applied. The lesson plan uses 15 steps and a limit of 1.0. A very short horizon or a tight limit overshoots or crawls. Changing a slider replans all 60 steps, which takes a moment.',
      'Lesson의 double integrator(dt = 0.1 s, Q = diag(1, 0.1), R = 0.1, terminal cost는 Riccati recursion)를 receding horizon으로 계획합니다. 목표에서 4 m 떨어진 정지 상태에서 출발해 60 step을 가며, 각 계획은 |u| ≤ 한계 안에서 projected gradient 800번으로 풉니다. 주황 점은 현재 계획이 예측한 위치이고 초록 화살표는 실제로 적용한 입력입니다. Lesson은 15 step과 한계 1.0을 씁니다. 너무 짧은 horizon이나 빡빡한 한계는 overshoot하거나 기어갑니다. Slider를 바꾸면 60번의 계획을 다시 세우므로 잠시 걸립니다.'],
    period: 8, rest: 8, H: 320, unit: 80, look: [2, 0, 0], oy: 20,
    cam: {yaw: .3, pitch: .4, dist: 7},
    controls: [
      {id: 'N', en: 'horizon (steps)', ko: 'horizon (step 수)', min: 3, max: 20, step: 1, val: 15},
      {id: 'um', en: 'push limit |u|', ko: '입력 한계 |u|', min: .3, max: 2, step: .1, dec: 1, val: 1},
    ],
  }, (s, t, m) => {
    const run = mpcRun(Math.round(s.v.N), s.v.um), f = Math.min(59, t / .1), k = Math.floor(f), k2 = Math.min(59, k + 1), x = run.xs[k][0] + (run.xs[k2][0] - run.xs[k][0]) * (f - k);
    s.box([2, 0, -.14], [2.6, .12, .02], I, '--mut', {a: .6});
    s.line([0, -.12, -.12], [0, -.12, .45], '--ok', 3); s.dot([0, -.12, .45], '--ok', 6, {ring: true});
    run.plans[k].forEach((px, i) => s.dot([px, -.3, -.1], '--acc', 3.5, {a: 1 - .6 * i / run.plans[k].length}));
    s.box([x, 0, .04], [.26, .13, .12], I, '--pf');
    s.dot([x - .15, 0, -.1], '--fg', 6, {ring: true}); s.dot([x + .15, 0, -.1], '--fg', 6, {ring: true});
    const u = run.us[k];
    if (Math.abs(u) > .01) s.arrow([x, 0, .3], [x - u * .35, 0, .3], '--ok', 4, {front: true});
    s.text(14, 24, `${m.t('horizon', 'horizon')} ${Math.round(s.v.N)}, |u| ≤ ${s.v.um.toFixed(1)}`, '--fg', 15);
    s.text(14, 44, `x = ${x.toFixed(2)} m,  u = ${u.toFixed(2)} m/s²`, '--ok', 15);
    s.text(14, 64, `${m.t('cost over 60 steps', '60 step의 cost')} = ${run.cost.toFixed(1)}`, '--mut', 14);
  });

  // ---- 03/09 main.py: V = w²/2 + (g/l)(1 - cos th) + kp th²/2, g/l = 9.81, c = 0.1, kp = 10, simulate() with the controller seeing the rate `delay` seconds old.
  const GL = 9.81, CD = .1, KPL = 10, lyc = {};
  const Vf = (th, w) => .5 * w * w + GL * (1 - Math.cos(th)) + .5 * KPL * th * th;
  const lyRun = (kd, delay) => keep(lyc, Math.round(kd * 10) + '|' + Math.round(delay * 100), () => {
    const dt = .001, n = 10000, lag = Math.round(delay / dt), th = new Float32Array(n), om = new Float32Array(n), V = new Float32Array(n);
    let x = [2, 0];
    for (let i = 0; i < n; i++) {
      th[i] = x[0]; om[i] = x[1]; V[i] = Vf(x[0], x[1]);
      const seen = i - lag >= 0 ? om[i - lag] : 0, a = -GL * Math.sin(x[0]) - CD * x[1] - KPL * x[0] - kd * seen;
      x = [x[0] + dt * (x[1] + dt * a), x[1] + dt * a];
    }
    return {th, om, V};
  });
  const BOWL = {x: th => th * .4, y: w => w * .15, z: v => v / 110 - .25};
  window.MOTION.three('lyapunov-bowl-3d', {
    en: 'A marble rolls in a bowl whose height is the energy-like function V. With enough damping it always runs downhill, and with negative damping or a late rate signal it climbs',
    ko: 'Bowl의 높이가 energy 같은 함수 V인 곳에서 구슬이 구릅니다. Damping이 충분하면 늘 내리막이고, 음의 damping이나 늦은 rate 신호가 있으면 오르막을 탑니다',
    cap: ['Pendulum with the lesson PD law: g/l = 9.81, friction c = 0.1, kp = 10, and V = ½ω² + (g/l)(1 − cos θ) + ½ kp θ². The bowl is V over the angle θ (−3 to 3 rad) and rate ω (−8 to 8 rad/s). The marble starts at θ = 2 rad at rest (the lesson samples random states instead) and follows the lesson simulation for 10 s. With no delay dV/dt = −(c + kd) ω², so the marble goes downhill when c + kd ≥ 0; the delay slider feeds the controller a rate that is that many seconds old, as the lesson does with 0.3 s.',
      'Lesson의 PD 법칙을 쓰는 진자입니다. g/l = 9.81, 마찰 c = 0.1, kp = 10이고 V = ½ω² + (g/l)(1 − cos θ) + ½ kp θ² 입니다. Bowl은 각도 θ(−3~3 rad)와 속도 ω(−8~8 rad/s)에 대한 V입니다. 구슬은 θ = 2 rad의 정지 상태에서 출발하며(lesson은 무작위 상태를 뽑습니다) lesson simulation을 10초 따라갑니다. Delay가 없으면 dV/dt = −(c + kd) ω² 이므로 c + kd ≥ 0일 때 구슬은 내리막입니다. Delay slider는 controller가 그 시간만큼 옛 rate를 보게 하며 lesson은 0.3초를 씁니다.'],
    period: 10, rest: 10, H: 350, unit: 108, look: [0, 0, .1], oy: 30,
    cam: {yaw: .55, pitch: .55, dist: 7},
    controls: [
      {id: 'kd', en: 'damping gain kd', ko: 'damping gain kd', min: -1, max: 5, step: .5, dec: 1, val: 2},
      {id: 'delay', en: 'rate delay', ko: 'rate 지연', min: 0, max: .3, step: .05, dec: 2, unit: ' s', val: 0},
    ],
  }, (s, t, m) => {
    const run = lyRun(s.v.kd, s.v.delay), i = Math.min(9999, Math.floor(t * 1000)), th = run.th[i], w = run.om[i];
    for (let a = -3; a <= 3; a++) s.path(Array.from({length: 17}, (_, k) => { const ww = -8 + k; return [BOWL.x(a), BOWL.y(ww), BOWL.z(Vf(a, ww))]; }), '--mut', 1.5, {a: .7});
    for (let ww = -8; ww <= 8; ww += 2) s.path(Array.from({length: 13}, (_, k) => { const a = -3 + k * .5; return [BOWL.x(a), BOWL.y(ww), BOWL.z(Vf(a, ww))]; }), '--mut', 1.5, {a: .7});
    const trail = []; for (let k = Math.max(0, i - 800); k <= i; k += 20) trail.push([BOWL.x(clamp(run.th[k], -3, 3)), BOWL.y(clamp(run.om[k], -8, 8)), BOWL.z(Math.min(run.V[k], 100)) + .02]);
    if (trail.length > 1) s.path(trail, '--acc', 2.5, {front: true});
    s.dot([BOWL.x(clamp(th, -3, 3)), BOWL.y(clamp(w, -8, 8)), BOWL.z(Math.min(run.V[i], 100)) + .03], '--bad', 8, {ring: true, front: true});
    const rate = (run.V[i] - run.V[Math.max(0, i - 50)]) / .05;
    s.text(14, 24, `V = ${run.V[i].toFixed(2)},  dV/dt ≈ ${rate.toFixed(2)}`, rate > 1e-3 ? '--bad' : '--ok', 15);
    s.text(14, 44, `c + kd = ${(CD + s.v.kd).toFixed(1)}  →  ${s.v.delay > 0 ? m.t('delayed rate', 'rate 지연') : (CD + s.v.kd >= 0 ? m.t('downhill', '내리막') : m.t('uphill', '오르막'))}`, '--fg', 15);
    s.text(14, 64, `θ = ${th.toFixed(2)} rad,  ω = ${w.toFixed(2)} rad/s`, '--mut', 14);
  });
})();
