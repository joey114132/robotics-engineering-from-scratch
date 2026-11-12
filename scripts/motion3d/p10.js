// 10단계 3D: LIPM의 support와 capture point, 네 rotor 차등 추력의 planar 운동을 그린다.
(() => {
  const R = window.M3D, G = 9.81, H = .9, HALF = .05, TC = Math.sqrt(H / G);
  const clamp = x => Math.max(0, Math.min(1, x));
  // Closed-form lipm_state, with the same push and .1 s step as fall_or_recover.
  function lipm(x0, v0, p, time) {
    const c = Math.cosh(time / TC), sn = Math.sinh(time / TC);
    return [p + (x0 - p) * c + TC * v0 * sn, (x0 - p) * sn / TC + v0 * c];
  }
  const atStep = lipm(0, .4, HALF, .1), landing = atStep[0] + TC * atStep[1];
  function balance(time, step) {
    const moved = step && time >= .1, p = moved ? landing : HALF;
    const [x, v] = moved ? lipm(atStep[0], atStep[1], landing, time - .1) : lipm(0, .4, HALF, time);
    const acc = G / H * (x - p);
    return {x, v, acc, p, zmp: x - H * acc / G, capture: x + TC * v, tc: TC, moved};
  }
  const foot = (s, centre, color, alpha) => s.poly([[centre - HALF, -HALF, 0], [centre + HALF, -HALF, 0],
    [centre + HALF, HALF, 0], [centre - HALF, HALF, 0]], color, {a: alpha, edge: color});
  const trajectories = [false, true].map(step => Array.from({length: 61}, (_, i) => [balance(i / 100, step).x, 0, H]));
  window.MOTION.three('lipm-support-3d', {
    en: 'A constant-height centre of mass moves after a push. Its capture point lies beyond the foot, and a step brings the support underneath it',
    ko: '밀린 뒤 일정한 높이의 centre of mass가 움직입니다. capture point가 발 밖에 있으므로 step으로 support를 그 아래에 옮깁니다',
    cap: ['The lesson’s 0.4 m/s push, h=0.9 m and foot half-length 0.05 m. The shaded foot is the support region, the green dot is ZMP and the orange cross is ξ. The foot inset separates their symbols left/right; leaders show their positions in the foot plane. Without a step the ZMP stays at the foot edge and CoM diverges. A step at 0.1 s puts ZMP and ξ at the same position (p=ξ) and CoM slows. The line is a massless telescoping leg, not a fixed-length pendulum. Toggle the step to compare the first 0.6 s.',
      '레슨의 조건은 초기 속도 0.4 m/s, h=0.9 m, 발 반길이 0.05 m입니다. 색칠한 발은 support region, 초록색 점은 ZMP, 주황색 십자는 ξ입니다. 발 inset에서는 두 표식을 좌우로 나누고 안내선으로 발 평면 위의 위치를 짚습니다. Step이 없으면 ZMP가 발 끝에 머물고 CoM은 멀어집니다. 0.1 s에 step하면 ZMP와 ξ가 같은 위치(p=ξ)에 놓이고 CoM이 느려집니다. 선은 질량이 없고 길이가 변하는 다리입니다. Step을 켜고 꺼서 처음 0.6 s를 비교할 수 있습니다.'],
    period: 12, rest: 10, H: 390, unit: 215, look: [.18, 0, .45], oy: 10,
    cam: {yaw: .35, pitch: .4, dist: 7},
    controls: [{id: 'time', en: 'model time', ko: '모델 시간', min: 0, max: .6, step: .001, dec: 3, unit: ' s', auto: t => .6 * clamp((t - 1) / 8)},
      {id: 'step', en: 'Step at 0.1 s', ko: '0.1 s에 step', toggle: true, val: true}],
  }, (s, t, m) => {
    const a = s.model = balance(s.v.time, s.v.step), com = [a.x, 0, H];
    const history = trajectories[s.v.step ? 1 : 0], n = Math.round(s.v.time * 100);
    // Keep one prefix per instance; moving the camera does not allocate a new trail.
    if (!s.cache || s.cache.n !== n || s.cache.step !== s.v.step) s.cache = {n, step: s.v.step, trail: history.slice(0, n + 1)};
    s.line([-.15, 0, 0], [.65, 0, 0], '--line', 2);
    foot(s, 0, '--mut', a.moved ? .15 : .4);
    if (a.moved) foot(s, landing, '--ok', .4);
    s.path(s.cache.trail, '--pf', 3);
    s.line([a.p, 0, 0], com, '--pf', 5);
    s.line(com, [a.x, 0, 0], '--mut', 1.5, {dash: [4, 4]});
    s.dot(com, '--pf', 10, {ring: true});
    s.dot([a.zmp, 0, .005], '--ok', 6, {ring: true});
    s.line([a.capture, -.04, 0], [a.capture, .04, 0], '--bad', 3);
    s.line([a.capture - .04, 0, 0], [a.capture + .04, 0, 0], '--bad', 3);
    // Camera-facing foot inset: symbols are callouts, not displaced physical points.
    const yaw = s.cam?.yaw ?? .35, pitch = s.cam?.pitch ?? .4;
    const inverse = R.mm(R.rz(-yaw), R.rx(-pitch));
    const inset = (x, y) => R.add([.18, 0, .45], R.mv(inverse, [(x - 240) / 215, 0, (205 - y) / 215]));
    const support = a.moved ? a.p : 0;
    const lo = Math.min(support - HALF, a.capture), hi = Math.max(support + HALF, a.capture);
    const px = x => 350 + 100 * (x - lo) / (hi - lo);
    s.poly([inset(px(support - HALF), 240), inset(px(support + HALF), 240),
      inset(px(support + HALF), 260), inset(px(support - HALF), 260)], '--mut', { a: .4, edge: '--mut' });
    const zmp = inset(px(a.zmp), 250), capture = a.moved ? zmp : inset(px(a.capture), 250);
    s.line(inset(360, 216), zmp, '--ok', 1.5, { front: true });
    s.line(inset(440, 216), capture, '--bad', 1.5, { front: true });
    s.dot(inset(360, 216), '--ok', 6, { ring: true, front: true });
    s.line(inset(434, 210), inset(446, 222), '--bad', 3, { front: true });
    s.line(inset(434, 222), inset(446, 210), '--bad', 3, { front: true });
    s.text(400, 172, m.t('Foot inset', '발 inset'), '--mut', 15, 'center');
    s.text(360, 198, 'ZMP', '--ok', 15, 'center');
    s.text(440, 198, 'ξ', '--bad', 15, 'center');
    if (a.moved) s.text(400, 283, 'p=ξ', '--fg', 15, 'center');
    s.text(14, 24, m.t('Push, support and capture point', '밀린 뒤 support와 capture point'), '--fg', 15);
    s.text(14, 44, `x = ${a.x.toFixed(3)} m; v = ${a.v.toFixed(3)} m/s`, '--pf', 15);
    s.text(14, 64, `p = ${a.zmp.toFixed(3)} m; ξ = ${a.capture.toFixed(3)} m`, '--mut', 15);
    s.text(14, 333, m.t('Shaded foot: support region', '색칠한 발: support region'), '--mut', 15);
    s.text(14, 356, m.t('Green dot: ZMP', '초록색 점: ZMP'), '--ok', 15);
    s.text(260, 356, m.t('Orange cross: ξ', '주황색 십자: ξ'), '--bad', 15);
  });

  // Four equal point masses m/4 on a plus: Iy = m*arm²/2, hence arm=sqrt(2I/m).
  // Two opposite rotors differ by ±delta: tau_y = -sum(x_i F_i) = 2*arm*delta.
  const MASS = .5, INERTIA = .004, ARM = Math.sqrt(2 * INERTIA / MASS), TOTAL = MASS * G, DT = .001;
  const DELTA = .002 / (2 * ARM), rotorCentres = [[-ARM, 0, 0], [ARM, 0, 0], [0, -ARM, 0], [0, ARM, 0]];
  const circle = Array.from({length: 25}, (_, i) => [ARM / 3 * Math.cos(i * 2 * Math.PI / 24), ARM / 3 * Math.sin(i * 2 * Math.PI / 24), 0]);
  function deriv(q, tau) {
    return [q[3], q[4], q[5], TOTAL * Math.sin(q[2]) / MASS, TOTAL * Math.cos(q[2]) / MASS - G, tau / INERTIA];
  }
  function flight(delta) {
    const tau = 2 * ARM * delta, states = [[0, 0, 0, 0, 0, 0]];
    for (let i = 0; i < 1000; i++) {
      const q = states[i], k1 = deriv(q, tau), k2 = deriv(q.map((v, j) => v + DT / 2 * k1[j]), tau);
      const k3 = deriv(q.map((v, j) => v + DT / 2 * k2[j]), tau), k4 = deriv(q.map((v, j) => v + DT * k3[j]), tau);
      states.push(q.map((v, j) => v + DT / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])));
    }
    return {delta, states};
  }
  window.MOTION.three('quad-differential-3d', {
    en: 'Four rotor thrust arrows on a schematic quadrotor. A thrust difference creates pitch torque, then tilt produces sideways acceleration',
    ko: 'quadrotor의 네 rotor thrust를 화살표로 나타냅니다. 추력 차이가 pitch torque를 만들고 기울어진 thrust가 옆 방향 가속도를 만듭니다',
    cap: ['A geometric four-rotor schematic uses the lesson’s m=0.5 kg and I=0.004 kg m²; four equal point masses give arm=√(2I/m). Opposite thrusts change by ±ΔF, giving τ=2 arm ΔF while total thrust stays mg. Each arrow draws its rotor’s change from hover 50 times larger, because the real change is under 1%. Attitude and translation use the lesson’s full planar RK4 model, not the small-angle approximation. Height is relative to the start.',
      '레슨의 m=0.5 kg와 I=0.004 kg m²로 구성한 기하 예입니다. 같은 질량 네 개를 배치하면 arm=√(2I/m)입니다. 마주 보는 rotor의 thrust를 ±ΔF만큼 바꾸면 τ=2 arm ΔF가 되고 총 thrust는 mg로 유지됩니다. 실제 변화는 1%가 안 되어서 화살표는 hover 대비 변화를 50배 키워 그렸습니다. 자세와 위치는 small-angle 근사 대신 레슨의 planar RK4 모델로 구합니다. 높이는 시작점을 기준으로 합니다.'],
    period: 12, rest: 10, H: 350, unit: 360, look: [.1, 0, .2], oy: 35,
    cam: {yaw: .45, pitch: .55, dist: 7},
    controls: [{id: 'delta', en: 'rotor ΔF', ko: 'rotor ΔF', min: -DELTA, max: DELTA, step: DELTA / 100, dec: 4, unit: ' N', val: DELTA},
      {id: 'time', en: 'model time', ko: '모델 시간', min: 0, max: 1, step: .001, dec: 3, unit: ' s', auto: t => clamp((t - 1) / 8)}],
  }, (s, t, m) => {
    if (!s.cache || s.cache.delta !== s.v.delta) s.cache = flight(s.v.delta);
    const state = s.cache.states[Math.round(s.v.time / DT)], rotation = R.ry(state[2]);
    const centre = [state[0], 0, 3 * ARM + state[1]], normal = R.mv(rotation, [0, 0, 1]);
    const thrusts = [TOTAL / 4 + s.v.delta, TOTAL / 4 - s.v.delta, TOTAL / 4, TOTAL / 4];
    s.model = {state, arm: ARM, rotors: rotorCentres, thrusts, torque: 2 * ARM * s.v.delta};
    s.line([-.15, 0, 0], [.4, 0, 0], '--line', 2);
    s.box(centre, [ARM / 2, ARM / 3, ARM / 10], rotation, '--pf');
    rotorCentres.forEach((local, i) => {
      const p = R.add(centre, R.mv(rotation, local));
      s.line(centre, p, '--fg', 4);
      s.path(circle.map(q => R.add(p, R.mv(rotation, q))), '--pf', 2);
      s.arrow(p, R.add(p, R.mul(normal, (1 + 50 * (thrusts[i] / (TOTAL / 4) - 1)) * ARM)), i < 2 ? '--pl' : '--ok', 3);   // the change from hover is under 1%, so it is drawn 50 times larger
    });
    s.dot(centre, '--fg', 4, {ring: true});
    s.text(14, 24, `ΣF = ${TOTAL.toFixed(3)} N; τ = ${s.model.torque.toFixed(4)} Nm`, '--fg', 15);
    s.text(14, 44, `pitch = ${(state[2] * 180 / Math.PI).toFixed(2)}°`, '--pl', 15);
    s.text(14, 64, `x = ${state[0].toFixed(3)} m; Δz = ${state[1].toFixed(3)} m`, '--mut', 15);
  });
})();

// 10단계 3D 추가: 발 위치로 속도를 정하는 LIPM 보행자와 돌풍을 받는 pitch 자세 제어(PD와 cascade).
(() => {
  const R = window.M3D, PI = Math.PI, G = 9.81, I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];

  // ---- 10/02 walking by foot placement: step_scale times the deadbeat step ----
  const H = .9, T = .4, VT = .6, NSTEP = 8, TC = Math.sqrt(H / G), cacheW = {}, look = [0, 0, .5];
  const lipm = (x0, v0, p, t) => { const a = x0 - p, c = Math.cosh(t / TC), sh = Math.sinh(t / TC); return [p + a * c + TC * v0 * sh, a * sh / TC + v0 * c]; };
  function walk(scale) {
    const key = Math.round(scale * 20); if (cacheW[key]) return cacheW[key];
    let x = -.05, v = .3, foot = 0; const st = [];
    for (let k = 0; k < NSTEP; k++) {
      const [xe, ve] = lipm(x, v, foot, T), u = (VT - ve * Math.cosh(T / TC)) * TC / Math.sinh(T / TC);
      st.push({x, v, foot, ve});
      foot = foot + scale * ((xe - u) - foot); x = xe; v = ve;
    }
    return cacheW[key] = st;
  }
  window.MOTION.three('foot-placement-walker-3d', {
    en: 'A walker modelled as a point mass on a stiff leg picks each next foot spot. Step a little too short and its speed runs away instead of settling at the target',
    ko: '점 질량이 뻣뻣한 다리 위에 있는 보행자가 다음 발 자리를 정합니다. 걸음이 조금만 짧아도 속도가 목표에 수렴하지 않고 계속 커집니다',
    cap: ['Linear inverted pendulum with height h = 0.9 m, a stance of T = 0.4 s and a target speed of 0.6 m/s, started at x = -0.05 m and 0.3 m/s as in the lesson. At each touchdown the deadbeat foot (from next_foot) is scaled by the slider: 1.0 reaches 0.6 m/s after one correction, 0.6 ends at 9.85 m/s after 8 steps and 1.5 ends at 8.11 m/s while swinging sign. The camera follows the walker; the ground ticks are 0.5 m apart. The torso is just the point mass and the leg is a line; the swing leg is not drawn.',
      '높이 h = 0.9 m의 선형 inverted pendulum이며 한 번의 stance는 T = 0.4초, 목표 속도는 0.6 m/s입니다. 레슨처럼 x = -0.05 m, 0.3 m/s에서 출발합니다. 발이 닿을 때마다 next_foot이 준 deadbeat 발 위치에 slider 값을 곱합니다. 1.0이면 한 번 보정한 뒤 0.6 m/s에 닿고 0.6이면 8걸음 뒤 9.85 m/s까지 커지며 1.5이면 부호를 바꿔 흔들리다 8.11 m/s가 됩니다. 카메라는 보행자를 따라가고 바닥 눈금은 0.5 m 간격입니다. 몸통은 점 질량이고 다리는 선이며 휘두르는 다리는 그리지 않았습니다.'],
    period: 24, rest: 3, H: 350, unit: 150, look, oy: 30,
    cam: {yaw: .45, pitch: .3, dist: 7},
    controls: [{id: 'scale', en: 'step length vs deadbeat', ko: '걸음 길이 / deadbeat 걸음', min: .5, max: 1.5, step: .05, dec: 2, unit: '×', auto: t => 1 + .5 * Math.cos(2 * PI * t / 24 + PI)}],
  }, (s, t, m) => {
    const st = walk(s.v.scale), total = NSTEP * T, ph = Math.min(t % (total + 1.2), total - 1e-6), k = Math.floor(ph / T), c = st[k];
    const [x, v] = lipm(c.x, c.v, c.foot, ph - k * T);
    look[0] = x;
    for (let g = Math.floor(x - 4) * 2; g <= (x + 4) * 2; g++) s.line([g / 2, -.45, 0], [g / 2, .45, 0], '--mut', g % 2 ? 1 : 2, {a: .5});
    s.box([x, 0, -.02], [4.2, .5, .015], I3, '--card', {a: .8});
    for (let j = 0; j <= k; j++) s.box([st[j].foot, 0, .015], [.07, .1, .015], I3, j === k ? '--pl' : '--mut');
    s.line([c.foot, 0, .03], [x, 0, H], '--pd', 5);
    s.box([x, 0, H], [.09, .14, .17], I3, '--pf');
    s.dot([x, 0, H], '--fg', 4, {ring: true, front: true});
    s.arrow([x, 0, H + .3], [x + Math.min(Math.abs(v), 2.5) * .3 * Math.sign(v), 0, H + .3], Math.abs(v - VT) < .08 ? '--ok' : '--bad', 3);
    const len = k ? st[k].foot - st[k - 1].foot : st[0].foot, good = Math.abs(c.ve - VT) < .05 && k > 1;
    s.text(14, 24, m.t(`step length ${s.v.scale.toFixed(2)}x the deadbeat step`, `걸음 길이 = deadbeat의 ${s.v.scale.toFixed(2)}배`), '--fg', 15);
    s.text(14, 44, m.t(`speed ${v.toFixed(2)} m/s, target ${VT}`, `속도 ${v.toFixed(2)} m/s, 목표 ${VT}`), Math.abs(v - VT) < .08 ? '--ok' : '--bad', 15);
    s.text(14, 64, m.t(`step ${k + 1}: length ${len.toFixed(2)} m, speed at its end ${c.ve.toFixed(2)}`, `${k + 1}번째 걸음: 길이 ${len.toFixed(2)} m, 끝 속도 ${c.ve.toFixed(2)}`), good ? '--ok' : '--mut', 15);
  });

  // ---- 10/04 cascaded attitude control: PD against angle-P + rate-PI under a gust ----
  const INERTIA = .004, KP = .9, KD = .084, DT = 1e-3, TEND = 3, EXAG = 4, cacheA = {};
  function simulate(ctrl) {
    const n = TEND / DT, th = new Float32Array(n + 1); let w = 0, a = 0;
    for (let i = 0; i < n; i++) {
      const t = i * DT, d = t >= .5 && t < 1.5 ? .1 : 0, tau = ctrl(-a, w);
      w += (tau + d) / INERTIA * DT; a += w * DT; th[i + 1] = a;
    }
    return th;
  }
  function runs(ki) {
    const key = Math.round(ki * 20); if (cacheA[key]) return cacheA[key];
    const pd = simulate((e, w) => KP * e - KD * w); let z = 0;
    const kt = KP / KD, cas = simulate((e, w) => { const ew = kt * e - w; z += ew * DT; return KD * ew + ki * z; });
    const pk = a => { let p = 0; for (let i = 0; i < a.length; i++) p = Math.max(p, Math.abs(a[i])); return p * 180 / PI; };
    return cacheA[key] = {pd, cas, pkPd: pk(pd), pkCas: pk(cas)};
  }
  function stand(s, x, color, tr, ph, label) {
    const i = Math.min(3000, Math.round(ph * 1000)), phi = tr[i] * EXAG, d = [Math.cos(phi), 0, Math.sin(phi)], c = [x, 0, .5];
    s.box([x, 0, .22], [.04, .04, .22], I3, '--pd'); s.box([x, 0, .02], [.3, .2, .02], I3, '--pd');
    s.line([x - .55, 0, .5], [x + .55, 0, .5], '--mut', 1.2, {dash: [4, 3]});
    s.box(c, [.55, .035, .025], R.ry(-phi), color);
    s.box(R.add(c, [0, 0, .06 * Math.cos(phi)]), [.12, .1, .06], R.ry(-phi), '--fg');
    for (const sg of [-1, 1]) { const p = R.add(c, R.mul(d, .55 * sg)); s.dot(R.add(p, [0, 0, .04]), '--pd', 9, {ring: true}); s.box(R.add(p, [0, 0, .03]), [.14, .14, .008], R.ry(-phi), '--mut', {a: .6}); }
    const pts = []; for (let i = 0; i <= 120; i++) pts.push([x - .5 + i / 120, 0, -.12 + tr[Math.round(i / 120 * 3000)] * 180 / PI * .04]);
    s.path(pts, color, 2);
    s.dot([x - .5 + i / 3000, 0, -.12 + tr[i] * 180 / PI * .04], color, 5, {ring: true});
    s.label([x, 0, -.38], label, color, 15, 'center');
    return tr[i] * 180 / PI;
  }
  window.MOTION.three('attitude-gust-stand-3d', {
    en: 'Two identical flying bodies on a test stand take the same gust torque. The single PD loop is left leaning; the cascade with an integral term pushes back to level',
    ko: '같은 비행체 두 대를 시험대에 올리고 같은 돌풍 토크를 줍니다. PD 한 겹은 기운 채 남고 적분 항이 있는 cascade는 수평으로 되돌립니다',
    cap: ['Plant I theta-double-dot = tau + d with I = 0.004 kg m^2 and a 0.1 N m gust between 0.5 s and 1.5 s, simulated with the lesson\'s semi-implicit Euler at 1 ms. Left: PD with kp = 0.9, kd = 0.084. Right: angle P (kp / kd) feeding a rate PI (kd, ki). At ki = 0.5 the lesson gives a peak of 6.65 deg for PD against 3.93 deg for the cascade, and 6.37 deg against 0.05 deg at 1.5 s. At ki = 0 the cascade reduces to the PD loop, so both stands move together. The tilt of the bar is drawn 4x larger than real; the curves below each stand are the true angle against time, 3 s wide.',
      '식은 I theta-double-dot = tau + d이며 I = 0.004 kg m^2이고 0.5초에서 1.5초 사이에 0.1 N m 돌풍이 들어옵니다. 레슨의 semi-implicit Euler를 1 ms로 돌렸습니다. 왼쪽은 kp = 0.9, kd = 0.084인 PD이고 오른쪽은 각도 P(kp / kd)가 속도 PI(kd, ki)를 구동하는 cascade입니다. ki = 0.5에서 레슨 값은 peak가 PD 6.65도, cascade 3.93도이고 1.5초에는 6.37도와 0.05도입니다. ki = 0이면 cascade가 PD와 같은 loop가 되어 두 시험대가 똑같이 움직입니다. 막대의 기울기는 실제의 4배로 그렸고 각 시험대 아래 곡선은 실제 각도를 시간에 따라 그린 것입니다(폭 3초).'],
    period: 12, rest: 1.4, H: 350, unit: 100, look: [0, 0, .2], oy: 30,
    cam: {yaw: .25, pitch: .25, dist: 7},
    controls: [{id: 'ki', en: 'integral gain ki', ko: '적분 gain ki', min: 0, max: 1.5, step: .05, dec: 2, auto: t => .75 - .75 * Math.cos(2 * PI * t / 12)}],
  }, (s, t, m) => {
    const r = runs(s.v.ki), ph = Math.min(t % (TEND + .6), TEND), gust = ph >= .5 && ph < 1.5;
    const a = stand(s, -1.05, '--bad', r.pd, ph, 'PD'), b = stand(s, 1.05, '--ok', r.cas, ph, 'cascade');
    if (gust) for (const x of [-1.05, 1.05]) s.arrow([x + .55, 0, .1], [x + .55, 0, .38], '--pl', 3.4, {front: true});
    s.text(14, 24, m.t(`ki = ${s.v.ki.toFixed(2)}${gust ? '; gust on' : ''}`, `ki = ${s.v.ki.toFixed(2)}${gust ? '; 돌풍 중' : ''}`), '--fg', 15);
    s.text(14, 44, m.t(`PD: ${a.toFixed(2)} deg now, peak ${r.pkPd.toFixed(2)}`, `PD: 지금 ${a.toFixed(2)}도, peak ${r.pkPd.toFixed(2)}`), '--bad', 15);
    s.text(14, 64, m.t(`cascade: ${b.toFixed(2)} deg now, peak ${r.pkCas.toFixed(2)}`, `cascade: 지금 ${b.toFixed(2)}도, peak ${r.pkCas.toFixed(2)}`), '--ok', 15);
  });
})();
