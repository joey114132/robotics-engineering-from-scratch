// 02단계 3D: DH 중간 frame과 URDF origin, 완전 신전에서 사라지는 Jacobian 방향을 그린다.
(() => {
  const R = window.M3D, PI = Math.PI, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  const ramp = t => Math.max(0, Math.min(1, (t - 1) / 8));
  // Constructed three-link geometry: .4/.3 from planar_craig, .1 and pi/2
  // from the lesson's origin-conversion test; terminal link .2. No robot specs.
  const rows = [[0, 0, 0], [.4, PI / 2, .1], [.3, 0, 0]], tool = [.2, 0, 0];
  function arm(q) {
    let A = I, B = I, p = [0, 0, 0], u = [0, 0, 0];
    const joints = [], axes = [], intermediate = [];
    rows.forEach(([a, alpha, d], i) => {
      const twist = R.rx(alpha), rotated = R.mm(A, twist);
      const pre = R.add(p, R.mv(A, [a, 0, 0]));
      A = R.mm(rotated, R.rz(q[i]));
      p = R.add(pre, R.mv(A, [0, 0, d])); // Craig: Rx Tx Rz Tz
      intermediate.push(pre); joints.push(p); axes.push(A);
      const origin = R.mv(twist, [a, 0, d]);
      u = R.add(u, R.mv(B, origin)); // URDF: Trans(origin) Rx Rz
      B = R.mm(R.mm(B, twist), R.rz(q[i]));
    });
    const tip = R.add(p, R.mv(A, tool)), urdfTip = R.add(u, R.mv(B, tool));
    return {q, joints, axes, intermediate, tip, urdfTip,
      offset: Math.hypot(...R.sub(joints[1], intermediate[1])), error: Math.hypot(...R.sub(tip, urdfTip))};
  }
  window.MOTION.three('dh-origins-3d', {
    en: 'Three links and joint frames. Craig DH applies the axial offset after the joint turn; URDF folds that offset into the fixed joint origin',
    ko: '세 link와 각 joint의 frame입니다. Craig DH는 joint 회전 뒤에 축 방향 거리를 더하고 URDF는 그 거리를 고정된 joint origin에 넣습니다',
    cap: ['Hollow DH2 is the intermediate Craig frame before Tz(d); solid U2 is the URDF joint origin. Their separation is d along the same joint axis. Completed DH and URDF FK coincide. This spatial example adds a third link to the lesson geometry; x, y, z labels at the base identify the axes used at every joint.',
      '빈 점 DH2는 Tz(d) 직전의 Craig 중간 frame이고 채운 점 U2는 URDF joint origin입니다. 두 점은 같은 joint 축 위에서 d만큼 떨어져 있습니다. 변환을 끝내면 두 FK는 같습니다. 레슨의 기하에 세 번째 link를 더한 예입니다. base의 x, y, z 표시는 모든 joint에서 쓰는 축을 구분합니다.'],
    period: 12, rest: 5, H: 330, unit: 290, look: [.35, 0, .05], oy: 35,
    cam: {yaw: .2, pitch: .45, dist: 7},
    controls: [{id: 'q2', en: 'joint 2', ko: 'joint 2', min: -90, max: 90, step: 1, unit: '°', auto: t => 60 * Math.sin(2 * PI * t / 12)}],
  }, (s, t, m) => {
    const a = s.model = arm([.5, s.v.q2 * PI / 180, .8]);
    s.path([[0, 0, 0], ...a.joints, a.tip], '--pf', 8);
    a.joints.forEach((p, i) => {
      s.dot(p, '--fg', 5, {ring: true});
      [[1, 0, 0], [0, 1, 0], [0, 0, 1]].forEach((e, k) => {
        const end = R.add(p, R.mv(a.axes[i], R.mul(e, .14))), color = ['--bad', '--ok', '--pd'][k];
        s.arrow(p, end, color, 2);
        if (i === 0) s.label(end, ['x', 'y', 'z'][k], color, 15, 'center', k === 1 ? -8 : 8, k === 1 ? 17 : -6);
      });
    });
    const pre = a.intermediate[1], origin = a.joints[1];
    s.dot(pre, '--mut', 7); s.dot(pre, '--card', 4);
    s.arrow(pre, origin, '--pl', 3, {front: true});
    s.label(pre, 'DH2', '--mut', 15, 'right', -10, -16);
    s.label(origin, 'U2', '--pl', 15, 'left', 10, 24);
    s.dot(a.tip, '--ok', 7, {ring: true});
    s.text(14, 24, m.t('Same arm, two transform orders', '같은 팔, 두 변환 순서'), '--fg', 15);
    s.text(14, 44, `d = ${a.offset.toFixed(2)} m; FK Δ = ${a.error.toFixed(6)} m`, '--mut', 15);
  });

  // Lesson 02/04 jacobian(q, L), with its planar y displayed as world z.
  // q1 keeps the tip on +x; the reach slider sets q2 by the cosine rule.
  function reachArm(reach) {
    const l1 = .5, l2 = .4;
    const q2 = Math.acos(Math.max(-1, Math.min(1, (reach * reach - l1 * l1 - l2 * l2) / (2 * l1 * l2))));
    const q1 = -Math.atan2(l2 * Math.sin(q2), l1 + l2 * Math.cos(q2));
    const elbow = [l1 * Math.cos(q1), 0, l1 * Math.sin(q1)];
    const tip = R.add(elbow, [l2 * Math.cos(q1 + q2), 0, l2 * Math.sin(q1 + q2)]);
    const J = [[-l1 * Math.sin(q1) - l2 * Math.sin(q1 + q2), -l2 * Math.sin(q1 + q2)],
      [l1 * Math.cos(q1) + l2 * Math.cos(q1 + q2), l2 * Math.cos(q1 + q2)]];
    const a = J[0][0] ** 2 + J[0][1] ** 2, b = J[0][0] * J[1][0] + J[0][1] * J[1][1], c = J[1][0] ** 2 + J[1][1] ** 2;
    const angle = Math.atan2(2 * b, a - c) / 2;
    let weak = [-Math.sin(angle), Math.cos(angle)];
    if (weak[0] < 0) weak = weak.map(x => -x);
    const sigma = Math.hypot(J[0][0] * weak[0] + J[1][0] * weak[1], J[0][1] * weak[0] + J[1][1] * weak[1]);
    return {q: [q1, q2], elbow, tip, weak, sigma, det: J[0][0] * J[1][1] - J[0][1] * J[1][0]};
  }
  window.MOTION.three('singular-reach-3d', {
    en: 'A two-link arm stretches to its maximum reach. The arrow marks the weakest tip-velocity direction, lost at full extension',
    ko: '두 link로 된 팔을 끝까지 뻗습니다. 화살표는 tip 속도를 내기 가장 어려운 방향이며 팔을 완전히 뻗으면 이 방향을 잃습니다',
    cap: ['The cosine rule turns reach into joint angles for the lesson lengths 0.5 and 0.4 m. Shaded solid links and a blue elbow marker keep the two links distinct even when straight; the floor grid shows depth. The arrow is the smallest left singular vector of J. At 0.9 m reach it is radial and J has rank one; the arm cannot produce velocity along that arrow.',
      'cosine rule로 reach를 joint 각도로 바꿉니다. Link 길이는 레슨의 0.5 m와 0.4 m입니다. 음영이 있는 link와 파란 elbow 표식으로 팔을 펼쳐도 두 link를 구분합니다. 바닥 grid는 깊이를 보여 줍니다. 화살표는 J의 가장 작은 left singular vector입니다. Reach가 0.9 m이면 이 방향은 팔을 따라 바깥쪽을 향하고 J의 rank는 1이 됩니다. 이때 화살표 방향의 속도를 낼 수 없습니다.'],
    period: 12, rest: 10, H: 370, unit: 260, look: [.5, 0, -.05], oy: 10,
    cam: {yaw: .25, pitch: .45, dist: 7},
    controls: [{id: 'reach', en: 'reach', ko: 'reach', min: .65, max: .9, step: .001, dec: 3, unit: ' m', auto: t => .65 + .25 * ramp(t)}],
  }, (s, t, m) => {
    const a = s.model = reachArm(s.v.reach), o = [0, 0, 0];
    for (const y of [-.2, 0, .2]) s.line([-.1, y, -.4], [1.25, y, -.4], '--mut', 1, { a: .45 });
    for (let x = 0; x <= 1.2; x += .2) s.line([x, -.2, -.4], [x, .2, -.4], '--mut', 1, { a: .45 });
    for (const [start, end, color] of [[o, a.elbow, '--pf'], [a.elbow, a.tip, '--pl']]) {
      const d = R.sub(end, start), angle = Math.atan2(d[2], d[0]);
      s.box(R.mul(R.add(start, end), .5), [Math.hypot(...d) / 2, .025, .025], R.ry(-angle), color);
    }
    [o, a.elbow].forEach(p => s.box(p, [.035, .045, .035], I, '--acc'));
    [o, a.elbow, a.tip].forEach(p => s.dot(p, '--acc', 8, {ring: true, front: true}));
    const end = R.add(a.tip, [.26 * a.weak[0], 0, .26 * a.weak[1]]);
    s.arrow(a.tip, end, '--bad', 4, {front: true});
    s.text(14, 24, `reach ${s.v.reach.toFixed(3)} m; det J = ${a.det.toFixed(4)}`, '--fg', 15);
    s.text(14, 44, `σ min = ${a.sigma.toFixed(4)}`, '--bad', 15);
    s.text(14, 64, a.sigma < 1e-8 ? m.t('Arrow: lost radial direction', '화살표: 잃어버린 radial 방향') : m.t('Arrow: weakest velocity direction', '화살표: 속도를 내기 가장 어려운 방향'), '--bad', 15);
  });
})();

// 02단계 3D (wave 1): IK 두 해, Jacobian, damped Newton IK.
(() => {
  const R = window.M3D, PI = Math.PI, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const link = (s, a, b, c, hw, al) => {
    const d = R.sub(b, a), ang = Math.atan2(d[1], d[0]);
    s.box(R.mul(R.add(a, b), .5), [Math.hypot(d[0], d[1]) / 2, hw, hw * .7], R.rz(ang), c, {a: al == null ? 1 : al});
  };
  const circle = r => Array.from({length: 73}, (_, i) => [r * Math.cos(i * PI / 36), r * Math.sin(i * PI / 36), .005]);
  const table = (s, h) => s.poly([[-h, -h, -.03], [h, -h, -.03], [h, h, -.03], [-h, h, -.03]], '--mut', {a: .1, edge: '--mut'});
  const arc = (s, o, tau, radius, max, c) => {
    if (Math.abs(tau) < 1e-8) return;
    const pts = [], sw = clamp(tau / max, -1, 1) * PI * 1.4;
    for (let i = 0; i <= 20; i++) { const a = -PI / 2 + sw * i / 20; pts.push([o[0] + radius * Math.cos(a), o[1] + radius * Math.sin(a), .05]); }
    s.path(pts, c, 3, {front: true}); s.arrow(pts[19], pts[20], c, 3, {front: true});
  };

  // 02/02 ik(): L = (0.5, 0.4), lesson target (0.6, 0.3).
  const L2 = [.5, .4];
  function ik(x, y, down) {
    const c2 = (x * x + y * y - L2[0] ** 2 - L2[1] ** 2) / (2 * L2[0] * L2[1]);
    if (Math.abs(c2) > 1 + 1e-9) return null;
    const c = clamp(c2, -1, 1), s2 = Math.sqrt(1 - c * c) * (down ? 1 : -1), q2 = Math.atan2(s2, c);
    return [Math.atan2(y, x) - Math.atan2(L2[1] * s2, L2[0] + L2[1] * c), q2];
  }
  const fk2 = q => [L2[0] * Math.cos(q[0]) + L2[1] * Math.cos(q[0] + q[1]), L2[0] * Math.sin(q[0]) + L2[1] * Math.sin(q[0] + q[1])];
  window.MOTION.three('ik-two-elbows-3d', {
    en: 'A two-link arm is asked to put its tip on a target. Two elbow poses reach it, and a target outside the reachable band has no pose at all',
    ko: '두 link 팔이 tip을 목표에 놓도록 합니다. 두 가지 elbow 자세가 닿고 도달 가능한 띠 밖의 목표에는 자세가 아예 없습니다',
    cap: ['Link lengths 0.5 and 0.4 m and the law of cosines from the lesson. The lesson target (0.6, 0.3) m is the default: elbow-down (q2 ≥ 0, blue) and elbow-up (q2 ≤ 0, green) both put the tip exactly there. Reach is the band |l1 − l2| = 0.1 m to l1 + l2 = 0.9 m, the two dashed circles; outside it ik raises "unreachable" and no arm is drawn.',
      'Link 길이 0.5와 0.4 m, 그리고 레슨의 law of cosines를 씁니다. 기본 목표는 레슨의 (0.6, 0.3) m이며 elbow-down(q2 ≥ 0, 파랑)과 elbow-up(q2 ≤ 0, 초록)이 모두 tip을 정확히 그 자리에 놓습니다. 도달 범위는 |l1 − l2| = 0.1 m부터 l1 + l2 = 0.9 m까지의 띠이며 점선 원 두 개입니다. 띠 밖에서는 ik가 "unreachable" 오류를 내므로 팔을 그리지 않습니다.'],
    period: 12, rest: 5, H: 340, unit: 135, look: [0, 0, 0], oy: 40,
    cam: {yaw: .3, pitch: 1.0, dist: 7},
    controls: [
      {id: 'r', en: 'target distance', ko: '목표까지 거리', min: 0, max: 1, step: .005, dec: 3, unit: ' m', val: Math.hypot(.6, .3), auto: t => .5 - .5 * Math.cos(2 * PI * t / 12)},
      {id: 'ang', en: 'target direction', ko: '목표 방향', min: -180, max: 180, step: 1, unit: '°', val: Math.atan2(.3, .6) * 180 / PI},
    ],
  }, (s, t, m) => {
    const a = s.v.ang * PI / 180, x = s.v.r * Math.cos(a), y = s.v.r * Math.sin(a), o = [0, 0, 0];
    table(s, .95);
    s.path(circle(L2[0] + L2[1]), '--ok', 2, {dash: [5, 4]}); s.path(circle(Math.abs(L2[0] - L2[1])), '--ok', 2, {dash: [5, 4]});
    const sols = [[true, '--pf', '--pl', 'down'], [false, '--ok', '--acc', 'up']].map(([down, c1, c2, name]) => {
      const q = ik(x, y, down);
      if (!q) return null;
      const e = [L2[0] * Math.cos(q[0]), L2[0] * Math.sin(q[0]), .01], tp = [...fk2(q), .01];
      link(s, o, e, c1, .03, down ? 1 : .8); link(s, e, tp, c2, .026, down ? 1 : .8);
      s.dot(e, '--fg', 5, {ring: true, front: true});
      return {q, name, tp, c1};
    });
    s.box(o, [.05, .05, .035], I, '--pd'); s.dot(o, '--fg', 6, {ring: true, front: true});
    const ok = sols[0];
    s.dot([x, y, .02], ok ? '--ok' : '--bad', 8, {ring: true, front: true});
    s.text(14, 24, `target (${x.toFixed(2)}, ${y.toFixed(2)}) m`, '--fg', 15);
    if (!ok) { s.text(14, 44, m.t('unreachable: band 0.100 to 0.900 m', 'unreachable: 도달 띠는 0.100~0.900 m'), '--bad', 15); return; }
    sols.forEach((sl, k) => s.text(14, 44 + 20 * k, `elbow ${sl.name}: q = (${(sl.q[0] * 180 / PI).toFixed(1)}°, ${(sl.q[1] * 180 / PI).toFixed(1)}°)`, sl.c1, 15));
  });

  // 02/03 example: q = (0.3, 0.8), qd = (0.5, -0.2), F = (0, -10) N.
  const QD = [.5, -.2], FORCE = [0, -10], Q1 = .3;
  const jac = q2 => {
    const s1 = Math.sin(Q1), c1 = Math.cos(Q1), s12 = Math.sin(Q1 + q2), c12 = Math.cos(Q1 + q2), [l1, l2] = L2;
    return [[-l1 * s1 - l2 * s12, -l2 * s12], [l1 * c1 + l2 * c12, l2 * c12]];
  };
  window.MOTION.three('jacobian-push-arm-3d', {
    en: 'A two-link arm moves its joints at fixed speeds. The Jacobian turns them into a tip velocity, and the same matrix turns a push on the tip into joint torques',
    ko: '두 link 팔이 joint를 정해진 속도로 움직입니다. Jacobian이 그 속도를 tip 속도로 바꾸고 같은 행렬이 tip에 가하는 힘을 joint torque로 바꿉니다',
    cap: ['Arm 0.5 and 0.4 m, q1 = 0.3 rad, joint speeds (0.5, −0.2) rad/s and a push of 10 N downward on the tip, all from the lesson example. Blue and teal arrows are the two Jacobian columns scaled by the joint speeds; their sum, the green arrow, is the tip velocity J q̇. The red arrow is the 10 N force (0.02 m per N) and the red arcs are the holding torques τ = Jᵀ F. Slide q2 toward 0 to straighten the arm. The lesson uses q2 = 0.8.',
      'Arm은 0.5와 0.4 m이고 q1 = 0.3 rad, joint 속도 (0.5, −0.2) rad/s, tip 아래쪽 10 N 힘은 모두 레슨 예제의 값입니다. 파랑과 청록 화살표는 Jacobian의 두 column에 joint 속도를 곱한 것이고 둘의 합인 초록 화살표가 tip 속도 J q̇ 입니다. 빨간 화살표는 10 N 힘(N당 0.02 m)이고 빨간 호는 버티는 torque τ = Jᵀ F 입니다. q2를 0 쪽으로 밀어 팔을 펴 보세요. 레슨은 q2 = 0.8을 씁니다.'],
    period: 12, rest: 4, H: 340, unit: 160, look: [.35, .15, 0], oy: 36,
    cam: {yaw: .3, pitch: 1.0, dist: 7},
    controls: [{id: 'q2', en: 'elbow q2', ko: 'elbow q2', min: .05, max: 3, step: .01, dec: 2, unit: ' rad', val: .8, auto: t => 1.5 + 1.35 * Math.cos(2 * PI * t / 12)}],
  }, (s, t, m) => {
    const q2 = s.v.q2, J = jac(q2), o = [0, 0, 0];
    const e = [L2[0] * Math.cos(Q1), L2[0] * Math.sin(Q1), .01], tp = [...fk2([Q1, q2]), .01];
    const col = [[J[0][0] * QD[0], J[1][0] * QD[0]], [J[0][1] * QD[1], J[1][1] * QD[1]]], v = [col[0][0] + col[1][0], col[0][1] + col[1][1]];
    const tau = [J[0][0] * FORCE[0] + J[1][0] * FORCE[1], J[0][1] * FORCE[0] + J[1][1] * FORCE[1]];
    table(s, .95);
    link(s, o, e, '--pd', .03); link(s, e, tp, '--pd', .026);
    s.box(o, [.05, .05, .035], I, '--pd'); [o, e].forEach(q => s.dot(q, '--fg', 5, {ring: true, front: true}));
    const mid = [tp[0] + col[0][0], tp[1] + col[0][1], .03];
    s.arrow(tp, mid, '--pf', 3, {front: true}); s.arrow(mid, [mid[0] + col[1][0], mid[1] + col[1][1], .03], '--pl', 3, {front: true});
    s.arrow(tp, [tp[0] + v[0], tp[1] + v[1], .03], '--ok', 4, {front: true});
    s.arrow(tp, [tp[0] + FORCE[0] * .02, tp[1] + FORCE[1] * .02, .03], '--bad', 4, {front: true});
    arc(s, o, tau[0], .1, 9, '--bad'); arc(s, e, tau[1], .08, 4, '--bad');
    s.dot(tp, '--acc', 6, {ring: true, front: true});
    s.text(14, 24, `q2 = ${q2.toFixed(2)} rad,  det J = ${(J[0][0] * J[1][1] - J[0][1] * J[1][0]).toFixed(3)}`, '--fg', 15);
    s.text(14, 44, `J q̇ = (${v[0].toFixed(3)}, ${v[1].toFixed(3)}) m/s`, '--ok', 15);
    s.text(14, 64, `τ = Jᵀ F = (${tau[0].toFixed(2)}, ${tau[1].toFixed(2)}) Nm`, '--bad', 15);
  });

  // 02/05: L = (0.4, 0.3, 0.2), limits (+-pi, +-2.5, +-2.5), lam 0.05, cap 0.3, q0 = (0.3, 0.3, 0.3).
  const L3 = [.4, .3, .2], LIM = [PI, 2.5, 2.5], LAM = .05, CAP = .3, traces = {};
  const chain = q => { let a = 0, x = 0, y = 0; return q.map((qi, i) => (a += qi, x += L3[i] * Math.cos(a), y += L3[i] * Math.sin(a), [x, y, .01])); };
  function trace(tx, ty) {
    const key = Math.round(tx * 1000) + ',' + Math.round(ty * 1000);
    if (traces[key]) return traces[key];
    let q = [.3, .3, .3].map((v, i) => clamp(v, -LIM[i], LIM[i]));
    const qs = [q], errs = [];
    for (let it = 0; it < 300; it++) {
      const p = chain(q)[2], e = [tx - p[0], ty - p[1]], err = Math.hypot(e[0], e[1]);
      errs.push(err);
      if (err < 1e-6) break;
      let a = 0, sx = [0, 0, 0], sy = [0, 0, 0];
      q.forEach((qi, i) => { a += qi; sx[i] = -L3[i] * Math.sin(a); sy[i] = L3[i] * Math.cos(a); });
      const J = [[0, 1, 2].map(j => sx.slice(j).reduce((u, w) => u + w, 0)), [0, 1, 2].map(j => sy.slice(j).reduce((u, w) => u + w, 0))];
      const A = [[J[0][0] ** 2 + J[0][1] ** 2 + J[0][2] ** 2 + LAM * LAM, J[0][0] * J[1][0] + J[0][1] * J[1][1] + J[0][2] * J[1][2]], [0, J[1][0] ** 2 + J[1][1] ** 2 + J[1][2] ** 2 + LAM * LAM]];
      A[1][0] = A[0][1];
      const det = A[0][0] * A[1][1] - A[0][1] * A[1][0], y = [(A[1][1] * e[0] - A[0][1] * e[1]) / det, (A[0][0] * e[1] - A[1][0] * e[0]) / det];
      const dq = [0, 1, 2].map(j => J[0][j] * y[0] + J[1][j] * y[1]), k = Math.min(1, CAP / Math.max(...dq.map(Math.abs)));
      q = q.map((qi, i) => clamp(qi + dq[i] * k, -LIM[i], LIM[i])); qs.push(q);
    }
    return traces[key] = {qs, errs, conv: errs[errs.length - 1] < 1e-6};
  }
  window.MOTION.three('numeric-ik-steps-3d', {
    en: 'A three-link arm closes in on a target one damped Newton step at a time, and a target beyond its reach never converges',
    ko: 'link 세 개의 팔이 damped Newton step을 한 번씩 밟으며 목표에 다가가고, 닿지 않는 목표에는 끝내 수렴하지 못합니다',
    cap: ['Link lengths 0.4, 0.3, 0.2 m, start pose (0.3, 0.3, 0.3) rad, damping λ = 0.05, joint step cap 0.3 rad and the limits of the lesson. Each step is Δq = Jᵀ(JJᵀ + λ²I)⁻¹ e; grey arms are earlier steps. With the target y fixed at 0.3 m, slide x: the arm converges in 6 to 12 steps up to a distance of about 0.9 m, and beyond that the error stays above zero.',
      'Link 길이는 0.4, 0.3, 0.2 m이고 시작 자세 (0.3, 0.3, 0.3) rad, damping λ = 0.05, joint step 상한 0.3 rad과 limit은 레슨과 같습니다. 한 step은 Δq = Jᵀ(JJᵀ + λ²I)⁻¹ e 이며 회색 팔은 이전 step입니다. 목표 y를 0.3 m로 두고 x를 움직이면 약 0.9 m 거리까지는 6~12 step에 수렴하고 그 너머에서는 오차가 0이 되지 못합니다.'],
    period: 12, rest: 12, H: 340, unit: 125, look: [.3, .3, 0], oy: 36,
    cam: {yaw: .3, pitch: 1.0, dist: 7},
    controls: [
      {id: 'it', en: 'step', ko: 'step', min: 0, max: 20, step: 1, val: 20, auto: t => Math.min(20, Math.floor(t * 2))},
      {id: 'tx', en: 'target x (y = 0.3 m)', ko: '목표 x (y = 0.3 m)', min: .2, max: 1.1, step: .01, dec: 2, unit: ' m', val: .5},
    ],
  }, (s, t, m) => {
    const tr = trace(s.v.tx, .3), k = Math.min(Math.round(s.v.it), tr.qs.length - 1), o = [0, 0, 0];
    table(s, 1.05);
    s.path(circle(.9), '--ok', 2, {dash: [5, 4]});
    for (let i = Math.max(0, k - 3); i < k; i++) {
      const p = chain(tr.qs[i]); link(s, o, p[0], '--mut', .02, .25); link(s, p[0], p[1], '--mut', .02, .25); link(s, p[1], p[2], '--mut', .02, .25);
    }
    s.path(tr.qs.slice(0, k + 1).map(q => chain(q)[2]), '--acc', 2, {dash: [3, 3]});
    const p = chain(tr.qs[k]);
    link(s, o, p[0], '--pf', .03); link(s, p[0], p[1], '--pl', .026); link(s, p[1], p[2], '--ok', .022);
    s.box(o, [.05, .05, .035], I, '--pd'); [o, p[0], p[1]].forEach(q => s.dot(q, '--fg', 5, {ring: true, front: true}));
    s.dot(p[2], '--acc', 6, {ring: true, front: true});
    s.dot([s.v.tx, .3, .02], tr.conv ? '--ok' : '--bad', 8, {ring: true, front: true});
    const err = tr.errs[Math.min(k, tr.errs.length - 1)];
    s.text(14, 24, `step ${k},  ‖e‖ = ${(err * 1000).toFixed(1)} mm`, '--fg', 15);
    s.text(14, 44, tr.conv ? m.t(`converges in ${tr.qs.length - 1} steps`, `${tr.qs.length - 1} step에 수렴`) : m.t('never converges: out of reach', '수렴 못 함: 도달 범위 밖'), tr.conv ? '--ok' : '--bad', 15);
  });
})();
