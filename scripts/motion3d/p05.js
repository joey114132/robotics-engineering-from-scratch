// Phase 05: timestamp에 맞는 interpolated transform과 latest transform을 비교한다.
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  // 05/06 __main__: endpoint poses (2t,0,0), quaternion (cos(t/2),0,0,sin(t/2)).
  const q0 = [1, 0, 0, 0], q1 = [Math.cos(.5), 0, 0, Math.sin(.5)];
  function model(stamp) {
    const om = Math.acos(q1[0]);
    const a = Math.sin((1 - stamp) * om) / Math.sin(om), b = Math.sin(stamp * om) / Math.sin(om);
    const q = q0.map((v, i) => a * v + b * q1[i]);
    const yaw = 2 * Math.atan2(q[3], q[0]), p = [2 * stamp, 0, 0];
    const point = R.add(p, [Math.cos(yaw), Math.sin(yaw), 0]);
    const latest = [2 + Math.cos(1), Math.sin(1), 0];
    return { p, q, yaw, point, latest, error: Math.hypot(...R.sub(point, latest)) };
  }
  const endpoint = model(1);
  window.MOTION.three('timestamp-frames-3d', {
    en: 'A timestamped sensor point goes to two different places when the lookup time is wrong',
    ko: 'Sensor point의 timestamp와 다른 시각으로 transform을 조회하면 위치가 어긋납니다',
    cap: ['The buffer stores t=0 and t=1 s with p=(2t,0,0) and yaw=t rad, as in the lesson. Position uses lerp and orientation uses slerp. A unit point (1,0,0) in the sensor frame uses its own timestamp (green); using the newest pose puts it at the orange point. All lookups stay inside the stored interval.',
      '수업처럼 buffer에 t=0과 t=1 s의 p=(2t,0,0), yaw=t rad를 저장합니다. 위치는 lerp, 방향은 slerp로 보간합니다. Sensor frame의 단위 점 (1,0,0)에 자신의 timestamp를 쓰면 초록색 위치가 됩니다. Latest pose를 쓰면 주황색 위치로 어긋납니다. 조회는 저장된 시간 범위 안에서만 합니다.'],
    period: 12, rest: 6, H: 340, unit: 110, look: [1.3, .3, .05], oy: 45,
    cam: { yaw: .15, pitch: .65, dist: 8 }, model,
    controls: [{ id: 'stamp', en: 'point timestamp', ko: '점의 timestamp', min: 0, max: 1, step: .01, dec: 2, unit: '\u00a0s', auto: t => Math.min(1, Math.max(0, (t - 1) / 10)) }],
  }, (s, t, m) => {
    const a = model(s.v.stamp), rot = R.rz(a.yaw);
    for (let i = 0; i <= 3; i++) {
      s.line([i, -.45, -.06], [i, 1.15, -.06], '--line', 1);
      s.label([i, -.45, -.06], `${i} m`, '--mut', 15, 'center', 0, 20);
    }
    s.line([0, 0, 0], [2, 0, 0], '--mut', 2, { dash: [4, 4] });
    s.wire([2, 0, .08], [.17, .12, .08], R.rz(1), '--mut', 2, { dash: [4, 4] });
    s.box(R.add(a.p, [0, 0, .08]), [.17, .12, .08], rot, '--pf');
    // Sensor origins coincide with robot origins in this lesson's buffer.
    for (const [p, rotation, scale] of [[a.p, rot, .4], [endpoint.p, R.rz(1), .25]]) {
      for (let k = 0; k < 3; k++) {
        const e = [0, 0, 0]; e[k] = scale;
        s.arrow(p, R.add(p, R.mv(rotation, e)), ['--bad', '--ok', '--pd'][k], 2);
      }
    }
    s.line(a.p, a.point, '--ok', 3); s.dot(a.point, '--ok', 8, { ring: true, front: true });
    s.line(endpoint.p, a.latest, '--bad', 2, { dash: [4, 4] });
    s.dot(a.latest, '--bad', 7, { ring: true, front: true });
    s.line(a.point, a.latest, '--bad', 2, { dash: [3, 4] });
    s.text(14, 24, m.t(`point stamp ${s.v.stamp.toFixed(2)} s`, `점의 timestamp ${s.v.stamp.toFixed(2)} s`), '--ok', 16);
    s.text(14, 46, m.t('orange: lookup at latest (1 s)', '주황: latest(1 s)로 조회'), '--bad', 15);
    s.text(14, 68, m.t(`position error ${a.error.toFixed(3)} m`, `위치 오차 ${a.error.toFixed(3)} m`), '--fg', 16);
  });
})();
