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
      'lesson의 조건은 초기 속도 0.4 m/s, h=0.9 m, 발 반길이 0.05 m입니다. 색칠한 발은 support region, 초록색 점은 ZMP, 주황색 십자는 ξ입니다. 발 inset에서는 두 표식을 좌우로 나누고 안내선으로 발 평면 위의 위치를 짚습니다. Step이 없으면 ZMP가 발 끝에 머물고 CoM은 멀어집니다. 0.1 s에 step하면 ZMP와 ξ가 같은 위치(p=ξ)에 놓이고 CoM이 느려집니다. 선은 질량이 없고 길이가 변하는 다리입니다. Step을 켜고 꺼서 처음 0.6 s를 비교할 수 있습니다.'],
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
    cap: ['A geometric four-rotor schematic uses the lesson’s m=0.5 kg and I=0.004 kg m²; four equal point masses give arm=√(2I/m). Opposite thrusts change by ±ΔF, giving τ=2 arm ΔF while total thrust stays mg. Attitude and translation use the lesson’s full planar RK4 model, not the small-angle approximation. Height is relative to the start.',
      'lesson의 m=0.5 kg와 I=0.004 kg m²로 구성한 기하 예입니다. 같은 질량 네 개를 배치하면 arm=√(2I/m)입니다. 마주 보는 rotor의 thrust를 ±ΔF만큼 바꾸면 τ=2 arm ΔF가 되고 총 thrust는 mg로 유지됩니다. 자세와 위치는 small-angle 근사 대신 lesson의 planar RK4 모델로 구합니다. 높이는 시작점을 기준으로 합니다.'],
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
      s.arrow(p, R.add(p, R.mul(normal, thrusts[i] / (TOTAL / 4) * ARM)), i < 2 ? '--pl' : '--ok', 3);
    });
    s.dot(centre, '--fg', 4, {ring: true});
    s.text(14, 24, `ΣF = ${TOTAL.toFixed(3)} N; τ = ${s.model.torque.toFixed(4)} Nm`, '--fg', 15);
    s.text(14, 44, `pitch = ${(state[2] * 180 / Math.PI).toFixed(2)}°`, '--pl', 15);
    s.text(14, 64, `x = ${state[0].toFixed(3)} m; Δz = ${state[1].toFixed(3)} m`, '--mut', 15);
  });
})();
