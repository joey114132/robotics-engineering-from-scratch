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
      '빈 점 DH2는 Tz(d) 직전의 Craig 중간 frame이고 채운 점 U2는 URDF joint origin입니다. 두 점은 같은 joint 축 위에서 d만큼 떨어져 있습니다. 변환을 끝내면 두 FK는 같습니다. lesson의 기하에 세 번째 link를 더한 예입니다. base의 x, y, z 표시는 모든 joint에서 쓰는 축을 구분합니다.'],
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
    ko: '두 link로 된 팔을 끝까지 뻗습니다. 화살표는 tip 속도를 내기 가장 어려운 방향이며 완전 신전에서 이 방향을 잃습니다',
    cap: ['The cosine rule turns reach into joint angles for the lesson lengths 0.5 and 0.4 m. Shaded solid links and a blue elbow marker keep the two links distinct even when straight; the floor grid shows depth. The arrow is the smallest left singular vector of J. At 0.9 m reach it is radial and J has rank one; the arm cannot produce velocity along that arrow.',
      'cosine rule로 reach를 joint 각도로 바꿉니다. Link 길이는 lesson의 0.5 m와 0.4 m입니다. 음영이 있는 link와 파란 elbow 표식으로 팔을 펼쳐도 두 link를 구분합니다. 바닥 grid는 깊이를 보여 줍니다. 화살표는 J의 가장 작은 left singular vector입니다. Reach가 0.9 m이면 이 방향은 팔을 따라 바깥쪽을 향하고 J의 rank는 1이 됩니다. 이때 화살표 방향의 속도를 낼 수 없습니다.'],
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
