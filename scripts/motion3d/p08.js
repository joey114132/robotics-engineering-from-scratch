// 08단계 3D: 같은 wheel 명령을 실제 track과 nominal odometry에 적분해 drift를 보여 준다.
(() => {
  const R = window.M3D, PI = Math.PI, DT = .01, RAD = .05, TRACK = .3;
  const SIDE = 2, SPEED = .5, TURN = 157, STRAIGHT = Math.round(SIDE / SPEED / DT);
  const STEPS = 4 * (STRAIGHT + TURN), stride = 10;
  const ramp = t => Math.max(0, Math.min(1, (t - 1) / 9));
  // Same twist_to_wheels and exact-arc dead_reckon as code/main.py.
  function integrate(error) {
    const truth = [[0, 0, 0]], odom = [[0, 0, 0]];
    for (let i = 0; i < STEPS; i++) {
      const corner = i % (STRAIGHT + TURN) >= STRAIGHT;
      const v = corner ? 0 : SPEED, w = corner ? PI / 2 / (TURN * DT) : 0;
      const wl = (v - w * TRACK / 2) / RAD, wr = (v + w * TRACK / 2) / RAD;
      [truth, odom].forEach((out, j) => {
        const b = TRACK * (j === 0 ? 1 + error / 100 : 1), last = out[out.length - 1];
        const speed = RAD * (wr + wl) / 2, omega = RAD * (wr - wl) / b;
        const d = omega * DT, h = d / 2, chord = speed * DT * (h === 0 ? 1 : Math.sin(h) / h);
        out.push([last[0] + chord * Math.cos(last[2] + h), last[1] + chord * Math.sin(last[2] + h), last[2] + d]);
      });
    }
    return {error, truth, odom, shown: -1, actualLine: [], odomLine: []};
  }
  window.MOTION.three('odometry-drift-3d', {
    en: 'A differential-drive robot follows square wheel commands. Its actual track width differs from the value used by odometry, so the two paths separate',
    ko: '차동 구동 로봇에 정사각형을 도는 wheel 명령을 줍니다. 실제 track width가 odometry 설정과 달라 두 경로가 벌어집니다',
    cap: ['The solid line is the true path with the track wider by the slider percentage; the dashed line is nominal odometry, which still closes its square. Both integrate the same wheel commands with the lesson’s exact circular arcs. r=0.05 m, b=0.30 m, side=2 m, v=0.5 m/s, dt=0.01 s. Playback compresses model time.',
      '실선은 slider만큼 track이 넓어진 실제 경로이고 점선은 정사각형을 닫는 nominal odometry입니다. 같은 wheel 명령을 lesson의 정확한 원호 식으로 적분합니다. r=0.05 m, b=0.30 m, 한 변은 2 m, v=0.5 m/s, dt=0.01 s입니다. 재생 시간은 압축했습니다.'],
    period: 12, rest: 11, H: 350, unit: 70, look: [1, 1, 0], oy: 15,
    cam: {yaw: -.45, pitch: .85, dist: 9},
    controls: [{id: 'error', en: 'true track wider', ko: '실제 track 증가', min: 0, max: 5, step: .1, dec: 1, unit: '%', val: 2},
      {id: 'progress', en: 'route fraction', ko: '경로 진행 비율', min: 0, max: 1, step: .001, dec: 2, auto: ramp}],
  }, (s, t, m) => {
    if (!s.cache || s.cache.error !== s.v.error) s.cache = integrate(s.v.error);
    const c = s.cache, index = Math.round(s.v.progress * STEPS), truth = c.truth[index], odom = c.odom[index];
    // Reuse path arrays; only rebuild when the displayed step changes, not at camera frame rate.
    const shown = Math.floor(index / stride);
    if (shown !== c.shown) {
      c.shown = shown; c.actualLine.length = 0; c.odomLine.length = 0;
      for (let i = 0; i <= shown * stride; i += stride) {
        c.actualLine.push([c.truth[i][0], c.truth[i][1], 0]);
        c.odomLine.push([c.odom[i][0], c.odom[i][1], 0]);
      }
    }
    const gap = Math.hypot(truth[0] - odom[0], truth[1] - odom[1]);
    s.model = {truth, odom, gap, steps: STEPS};
    for (let i = 0; i <= 5; i++) {
      const x = i * SIDE / 4 - SIDE / 4;
      s.line([x, -.5, 0], [x, 2.5, 0], '--line', 1);
      s.line([-.5, x, 0], [2.5, x, 0], '--line', 1);
    }
    if (c.actualLine.length > 1) { s.path(c.actualLine, '--pf', 3.5); s.path(c.odomLine, '--mut', 2, {dash: [5, 4]}); }
    const body = [truth[0], truth[1], RAD * 2], rot = R.rz(truth[2]);
    s.box(body, [TRACK / 2, TRACK / 3, RAD], rot, '--pf');
    [-1, 1].forEach(sign => {
      const p = R.add([truth[0], truth[1], RAD], R.mv(rot, [0, sign * TRACK * (1 + s.v.error / 100) / 2, 0]));
      s.box(p, [RAD, RAD / 3, RAD], rot, '--fg');
    });
    s.wire([odom[0], odom[1], RAD * 2], [TRACK / 2, TRACK / 3, RAD], R.rz(odom[2]), '--mut', 2, {dash: [4, 4]});
    s.dot([0, 0, 0], '--ok', 5, {ring: true});
    s.line([truth[0], truth[1], .01], [odom[0], odom[1], .01], '--bad', 2);
    s.text(14, 24, m.t('Solid: true / dashed: odometry', '실선: 실제 / 점선: odometry'), '--fg', 15);
    s.text(14, 44, m.t(`position gap = ${gap.toFixed(3)} m`, `위치 차이 = ${gap.toFixed(3)} m`), '--bad', 15);
    s.text(14, 64, m.t(`model time ${(index * DT).toFixed(2)} s`, `모델 시간 ${(index * DT).toFixed(2)} s`), '--mut', 15);
  });
})();
