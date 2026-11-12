// 3D widgets for phase 07 (state estimation): imu-gravity-leak-3d
// A stationary robot with a gyro bias b: the tilt estimate is wrong by b t, so g sin(b t) of gravity looks like acceleration (code/main.py leaked_position, dt = 0.01 s).
(() => {
  const R = window.M3D, PI = Math.PI, G = 9.81, SC = .12, seg = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));
  const leak = (b, T) => { let v = 0, x = 0; const n = Math.round(T / .01); for (let i = 1; i <= n; i++) { v += G * Math.sin(b * i * .01) * .01; x += v * .01; } return x; };
  window.MOTION.three('imu-gravity-leak-3d', {
    en: 'A robot standing still. The gyro bias tilts its estimate of up, gravity is subtracted in the wrong direction, and the leftover looks like acceleration that carries the estimated position away',
    ko: '가만히 서 있는 로봇입니다. gyro bias 때문에 위쪽 방향의 추정이 기울고 중력이 엉뚱한 방향으로 빠져서 남은 성분이 가속도처럼 보이며 추정 위치가 멀어집니다',
    cap: ['The robot does not move (solid box). The tilt error is b t, so g sin(b t) of gravity is left over as a fake acceleration, and double integration walks the estimated position (dashed box) away. The default bias is 0.01 rad/s.',
      '로봇은 움직이지 않습니다(실선 상자). 기울기 오차는 b t이고 중력 중 g sin(b t)가 가짜 가속도로 남으며 이를 두 번 적분하면 추정 위치(점선 상자)가 멀어집니다. 기본 bias는 0.01 rad/s입니다.'],
    period: 12, rest: 11, cam: { yaw: .35, pitch: .4, dist: 7 }, unit: 140, oy: 64,
    controls: [{ id: 'T', en: 'time', ko: '시간', min: 0, max: 10, step: .1, dec: 1, unit: ' s', auto: t => 10 * seg(t, 1, 10) }, { id: 'b', en: 'gyro bias', ko: 'gyro bias', min: 0, max: .03, step: .001, dec: 3, unit: ' rad/s', val: .01 }],
  }, (s, t, m) => {
    const tilt = s.v.b * s.v.T, a = G * Math.sin(tilt), x = leak(s.v.b, s.v.T), H = [.22, .15, .09], gx = SC * 10;
    const C = p => [p[0] - gx, p[1], p[2] - .1];   // the ruler runs 0..20 m to the right of the robot; shift so the whole scene is centred
    s.line(C([-.5, 0, 0]), C([20 * SC + .3, 0, 0]), '--line', 2);
    for (let i = 0; i <= 4; i++) { s.line(C([i * 5 * SC, 0, 0]), C([i * 5 * SC, .12, 0]), '--mut', 1.5); s.label(C([i * 5 * SC, 0, 0]), i * 5 + ' m', '--mut', 15, 'center', 0, 20); }
    if (x > .05) s.line(C([0, 0, .02]), C([x * SC, 0, .02]), '--bad', 3.5);
    s.wire(C([x * SC, 0, H[2]]), H, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], '--bad', 2, { dash: [5, 4] });
    s.box(C([0, 0, H[2]]), H, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], '--pf', { a: .8 });
    const O = C([0, 0, .9]), dn = [Math.sin(tilt) * .6, 0, -Math.cos(tilt) * .6];
    s.arrow(O, R.add(O, [0, 0, -.6]), '--fg', 3, { front: true }); s.label(R.add(O, [0, 0, -.6]), m.t('true g', '실제 g'), '--fg', 15, 'center', 0, 20);
    s.arrow(O, R.add(O, dn), '--mut', 2.5, { dash: [5, 4], front: true });
    if (a > .02) { const L = [Math.sin(tilt) * 2.4, 0, 0]; s.arrow(O, R.add(O, L), '--bad', 3.5, { front: true }); s.label(R.add(O, L), m.t('leftover (drawn x4)', '남은 성분(4배로 그림)'), '--bad', 15, 'left', 8, -6); }
    s.text(14, 24, m.t(`tilt error b t = ${(tilt * 180 / PI).toFixed(1)}°`, `기울기 오차 b t = ${(tilt * 180 / PI).toFixed(1)}°`), '--fg', 15);
    s.text(14, 44, m.t(`fake acceleration g sin(b t) = ${a.toFixed(2)} m/s²`, `가짜 가속도 g sin(b t) = ${a.toFixed(2)} m/s²`), '--bad', 15);
    s.text(14, 64, m.t(`position error ${x.toFixed(1)} m`, `위치 오차 ${x.toFixed(1)} m`), '--bad', 15);
  });
})();
