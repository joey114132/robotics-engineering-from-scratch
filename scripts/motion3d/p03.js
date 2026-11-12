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
