// 3D widgets for phase 01 (math foundations): rotation-order-3d
// One body, two orders of the same two 90-degree turns about the FIXED world axes (docs/en.md: x then z sends (1,0,0) to (0,1,0); z then x sends it to (0,0,1)).
(() => {
  const PI = Math.PI, R = window.M3D, deg = a => Math.round(a * 180 / PI);
  const ease = t => { t = Math.min(1, Math.max(0, t)); return t * t * (3 - 2 * t); };
  const seg = (t, a, b) => ease((t - a) / (b - a));
  const fmt = v => '(' + v.map(x => { x = Math.round(x); return x === 0 ? 0 : x; }).join(', ') + ')';
  const H = [.62, .36, .2], TIP = [1, 0, 0], Q = PI / 2;
  // pose of the body at time t for one order: first turn about axis a1 during [t0,t0+2], second about a2 during [t0+2.6,t0+4.6]
  const pose = (t, t0, a1, a2) => { const f = (a, k) => R[a === 'x' ? 'rx' : 'rz'](k * Q); return R.mm(f(a2, seg(t, t0 + 2.6, t0 + 4.6)), f(a1, seg(t, t0, t0 + 2))); };
  // trail of the tip as it moves: first turn, then second turn (always upto <= 1 of the whole path measured by the turn parameter)
  const trail = (a1, a2, t, t0) => { const n = 30, out = []; for (let i = 0; i <= n; i++) { const tt = t0 + i / n * 4.6; if (tt > t) break; out.push(R.mv(pose(tt, t0, a1, a2), TIP)); } return out; };
  const A = [R.mm(R.rz(Q), R.rx(Q)), 'x', 'z'], B = [R.mm(R.rx(Q), R.rz(Q)), 'z', 'x'];
  window.MOTION.three('rotation-order-3d', {
    en: 'A box turned 90 degrees about x then z, and again about z then x, ends in two different poses; the tip of its x axis lands on two different points of the unit sphere',
    ko: '상자를 x축 다음 z축으로 90도씩 돌렸을 때와 z축 다음 x축으로 돌렸을 때 서로 다른 자세로 끝나고 x축 끝은 단위 구 위의 서로 다른 점에 놓입니다',
    cap: ['The same two quarter turns about the fixed world axes, in two orders. The cyan dot is the tip of the body x axis. Drag to look from other sides.',
      '같은 90도 회전 두 번을 고정된 세계 좌표축 기준으로 두 가지 순서로 했습니다. 하늘색 점이 상자 x축의 끝입니다. 드래그해서 다른 쪽에서 볼 수 있습니다.'],
    period: 13, rest: 12.6, cam: { yaw: .62, pitch: .38, dist: 7 }, unit: 112,
  }, (s, t, m) => {
    const o = [0, 0, 0], ring = (ax) => { const p = []; for (let i = 0; i <= 64; i++) { const a = i / 64 * 2 * PI, c = Math.cos(a), n = Math.sin(a); p.push(ax === 0 ? [0, c, n] : ax === 1 ? [c, 0, n] : [c, n, 0]); } return p; };
    // world frame and unit sphere (three great circles)
    [0, 1, 2].forEach(ax => s.path(ring(ax), '--line', 1.5, { a: .9 }));
    [[1.35, 0, 0, 'x'], [0, 1.35, 0, 'y'], [0, 0, 1.35, 'z']].forEach(a => { s.line(o, a.slice(0, 3), '--mut', 1.5, { a: .7 }); s.label(a.slice(0, 3), a[3], '--mut', 16, 'center', 0, -4); });
    // the pose now, and the finished pose of order A as a dashed ghost once it exists
    const Rn = t < 6.2 ? pose(t, .6, 'x', 'z') : t < 7.4 ? pose(Math.max(.6, 5.2 - (t - 6.2) * 3.83), .6, 'x', 'z') : pose(t, 7.4, 'z', 'x');   // 6.2-7.4: order A runs backwards to the start
    if (t >= 6.2) s.wire(o, H, A[0], '--mut', 1.8, { dash: [5, 4] });
    s.box(o, H, Rn, '--pf', { a: .62 });
    // body axes: x red-ish, y green-ish, z blue-ish (the same three colours in both themes through the variables)
    [['--bad', [1, 0, 0]], ['--ok', [0, 1, 0]], ['--pd', [0, 0, 1]]].forEach(([c, e]) => s.line(o, R.mv(Rn, e.map(x => x * .95)), c, 3.5, { front: true }));
    const tip = R.mv(Rn, TIP);
    // trails: A grey-dashed once finished, B drawn live; both on the unit sphere
    s.path(trail('x', 'z', Math.min(t, 5.4), .6), '--pl', 3.5, { a: t >= 7.4 ? .55 : 1 });
    if (t >= 7.4) s.path(trail('z', 'x', t, 7.4), '--pl', 3.5);
    if (t >= 5.4) s.dot(R.mv(A[0], TIP), '--pf', 6, { ring: true });
    if (t >= 12) s.dot(R.mv(B[0], TIP), '--pf', 6, { ring: true });
    s.dot(tip, '--pf', 8, { ring: true, front: true });
    // text: every number is computed from the same pose that is drawn
    const turn = (t0_, a1, a2) => t < t0_ + 2.3 ? ['1', a1, deg(seg(t, t0_, t0_ + 2) * Q)] : ['2', a2, deg(seg(t, t0_ + 2.6, t0_ + 4.6) * Q)];
    const lbl = (en, ko) => m.t(en, ko);
    if (t < 0.6) s.text(14, 24, lbl('Start: both orders begin from the same pose', '시작: 두 순서 모두 같은 자세에서 출발합니다'), '--fg', 15);
    else if (t < 5.4 || (t >= 7.4 && t < 12)) { const [n, ax, d] = t < 5.4 ? turn(.6, 'x', 'z') : turn(7.4, 'z', 'x'); const ord = t < 5.4 ? 'x → z' : 'z → x';
      s.text(14, 24, lbl(`Order ${ord}: turn ${n} of 2`, `순서 ${ord}: ${n}번째 회전`), '--fg', 15); s.text(14, 44, lbl(`${d}° about world ${ax}`, `세계 ${ax}축 기준 ${d}°`), '--mut', 15); }
    if (t >= 5.4 && t < 7.4) s.text(14, 24, lbl(`x → z ends at ${fmt(R.mv(A[0], TIP))}`, `x → z는 ${fmt(R.mv(A[0], TIP))}에서 끝납니다`), '--fg', 15);
    if (t >= 12) { s.text(14, 24, lbl(`x → z: tip at ${fmt(R.mv(A[0], TIP))}`, `x → z: 끝점 ${fmt(R.mv(A[0], TIP))}`), '--fg', 15);
      s.text(14, 44, lbl(`z → x: tip at ${fmt(R.mv(B[0], TIP))}`, `z → x: 끝점 ${fmt(R.mv(B[0], TIP))}`), '--fg', 15); }
  });

  // ---- 01-05 gimbal lock: three nested rings; at pitch 90 degrees the roll ring lies in the yaw ring's plane (R = Rz(yaw) Ry(pitch) Rx(roll), as in code/main.py) ----
  const rad = d => d * PI / 180, ring = (Rm, ax, r) => { const p = []; for (let i = 0; i <= 40; i++) { const a = i / 40 * 2 * PI, c = Math.cos(a), n = Math.sin(a); p.push(R.mv(Rm, (ax === 2 ? [c, n, 0] : ax === 1 ? [c, 0, n] : [0, c, n]).map(x => x * r))); } return p; };
  const I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], O = [0, 0, 0];
  window.MOTION.three('gimbal-rings-3d', {
    en: 'Three nested rings for yaw, pitch and roll. As pitch reaches 90 degrees the roll ring lies in the yaw ring plane, and the two turn the tool the same way',
    ko: 'yaw, pitch, roll을 나타내는 고리 세 개입니다. pitch가 90도에 이르면 roll 고리가 yaw 고리와 같은 평면에 놓여 둘이 도구를 같은 방향으로 돌립니다',
    cap: ['ZYX order, R = Rz(yaw) Ry(pitch) Rx(roll). Each ring turns about its own axis. At pitch 90 degrees the roll axis coincides with the yaw axis, so one degree of freedom is gone and det E = cos(pitch) reaches 0.',
      'ZYX 순서이고 R = Rz(yaw) Ry(pitch) Rx(roll)입니다. 고리는 각자의 축을 중심으로 돕니다. pitch가 90도이면 roll 축이 yaw 축과 겹쳐 자유도 하나가 사라지고 det E = cos(pitch)는 0이 됩니다.'],
    period: 12, rest: 0, cam: { yaw: .75, pitch: .55, dist: 7 }, unit: 112,
    controls: [{ id: 'pitch', en: 'pitch', ko: 'pitch', min: 50, max: 130, step: 1, unit: '°', auto: t => 90 + 35 * Math.sin(2 * PI * t / 12) },
      { id: 'roll', en: 'roll', ko: 'roll', min: -180, max: 180, step: 1, val: 30, unit: '°' }, { id: 'yaw', en: 'yaw', ko: 'yaw', min: -180, max: 180, step: 1, val: 40, unit: '°' }],
  }, (s, t, m) => {
    const p = s.v.pitch, R1 = R.rz(rad(s.v.yaw)), R2 = R.mm(R1, R.ry(rad(p))), R3 = R.mm(R2, R.rx(rad(s.v.roll)));
    s.path(ring(I3, 2, 1.3), '--pd', 3); s.path(ring(R1, 1, 1), '--ok', 3); s.path(ring(R2, 0, .72), '--bad', 3);
    s.line([0, 0, -1.55], [0, 0, 1.55], '--pd', 1.5, { dash: [4, 4] }); s.line(R.mv(R1, [0, -1.15, 0]), R.mv(R1, [0, 1.15, 0]), '--ok', 1.5, { dash: [4, 4] });
    s.box(O, [.58, .12, .12], R3, '--pf', { a: .75 }); s.dot(R.mv(R3, [.58, 0, 0]), '--fg', 5, { ring: true, front: true });
    // what a reader of angles would report for this very rotation (R_to_euler of the lesson): at +-90 deg roll is set to 0
    const pr = Math.asin(Math.max(-1, Math.min(1, -R3[2][0]))), lock = Math.abs(R3[2][0]) > 1 - 1e-9;
    const rr = lock ? 0 : Math.atan2(R3[2][1], R3[2][2]), yr = lock ? Math.atan2(-R3[0][1], R3[1][1]) : Math.atan2(R3[1][0], R3[0][0]), d = x => Math.round(x * 180 / PI);
    s.text(14, 24, m.t(`det E = cos(pitch) = ${Math.cos(rad(p)).toFixed(3)}`, `det E = cos(pitch) = ${Math.cos(rad(p)).toFixed(3)}`), '--fg', 15);
    s.text(14, 44, m.t(`reads roll ${d(rr)}, pitch ${d(pr)}, yaw ${d(yr)}`, `읽히는 값 roll ${d(rr)}, pitch ${d(pr)}, yaw ${d(yr)}`), '--mut', 15);
    s.text(14, 64, lock ? m.t('locked: only one angle is defined', '잠김: 각도 하나만 정해집니다') : m.t(`spin rate needed ~ 1/cos = ${(1 / Math.abs(Math.cos(rad(p)))).toFixed(1)}`, `필요한 회전 속도 ~ 1/cos = ${(1 / Math.abs(Math.cos(rad(p)))).toFixed(1)}`), lock ? '--bad' : '--mut', 15);
  });

  // ---- 01-03 quaternions: the target arrives as -q. Without the sign fix the slerp takes the far side of the circle (354.3 deg), with it 5.7 deg ----
  const slerp = (q0, q1, u, fix) => {
    let d = q0[0] * q1[0] + q0[1] * q1[1] + q0[2] * q1[2] + q0[3] * q1[3]; if (fix && d < 0) { q1 = q1.map(x => -x); d = -d; }
    const om = Math.acos(Math.max(-1, Math.min(1, d))), a = Math.sin((1 - u) * om) / Math.sin(om), b = Math.sin(u * om) / Math.sin(om);
    return q0.map((x, i) => a * x + b * q1[i]);
  };
  const Q0 = [1, 0, 0, 0], Q1 = [-Math.cos(.05), 0, 0, -Math.sin(.05)];   // the same rotation as 0.1 rad about z, written with the opposite sign
  const phi = (u, fix) => { const q = slerp(Q0, Q1, u, fix); return 2 * Math.atan2(q[3], q[0]); };
  window.MOTION.three('slerp-long-way-3d', {
    en: 'A wrist asked to turn 0.1 radian about z: without the quaternion sign fix it sweeps 354.3 degrees the long way round, with the fix 5.7 degrees',
    ko: '손목에 z축 기준 0.1 rad 회전을 지시했을 때 quaternion 부호를 고치지 않으면 반대쪽으로 354.3도를 돌고 고치면 5.7도만 돕니다',
    cap: ['The target quaternion arrives with the opposite sign, which names the same rotation (the dashed box). Plain interpolation follows the sign and takes the far side of the circle; negating q1 when dot(q0, q1) < 0 takes the short arc.',
      '목표 quaternion이 반대 부호로 들어옵니다. 같은 회전을 가리키며 점선 상자가 그 자세입니다. 부호를 그대로 쓰면 원의 먼 쪽으로 돌고 dot(q0, q1) < 0일 때 q1의 부호를 바꾸면 짧은 호를 따라갑니다.'],
    period: 12, rest: 5, cam: { yaw: .55, pitch: .75, dist: 7 }, unit: 112,
    controls: [{ id: 'fix', toggle: true, en: 'Apply the sign fix', ko: '부호 고치기 적용', auto: t => t >= 6 }],
  }, (s, t, m) => {
    const u = Math.min(1, Math.max(0, ((t % 6) - .5) / 4)), fix = s.v.fix, f = phi(u, fix), swept = Math.abs(f) * 180 / PI, trail = [];
    for (let i = 0; i <= 90; i++) { const x = phi(i / 90 * u, fix); trail.push([Math.cos(x), Math.sin(x), 0]); }
    const circle = []; for (let i = 0; i <= 64; i++) circle.push([Math.cos(i / 64 * 2 * PI), Math.sin(i / 64 * 2 * PI), 0]);
    s.path(circle, '--line', 1.5); s.line([0, 0, -.9], [0, 0, 1.2], '--mut', 1.5, { dash: [4, 4] });
    s.wire(O, H, R.rz(.1), '--mut', 1.8, { dash: [5, 4] });
    if (trail.length > 1) s.path(trail, fix ? '--ok' : '--bad', 4);
    s.box(O, H, R.rz(f), '--pf', { a: .62 }); s.dot([Math.cos(f), Math.sin(f), 0], '--pf', 7, { ring: true, front: true });
    const dp = Q0[0] * Q1[0] + Q0[3] * Q1[3];
    s.text(14, 24, `dot(q0, q1) = ${dp.toFixed(3)}`, '--fg', 15);
    s.text(14, 44, m.t(`swept so far: ${swept.toFixed(1)}°`, `지금까지 돈 각도: ${swept.toFixed(1)}°`), fix ? '--ok' : '--bad', 15);
    if (u >= 1) s.text(14, 64, fix ? m.t('short arc', '짧은 호') : m.t('the long way round', '반대쪽으로 한 바퀴 가까이'), fix ? '--ok' : '--bad', 15);
  });

  // ---- 01-04 frames: the cup in the camera frame, carried to the base by the right product and by two wrong ones (same numbers as code/figure.py) ----
  const cupC = [.2, 0, .5], tCam = [.5, 0, .4];
  window.MOTION.three('tf-wrong-product-3d', {
    en: 'A cup seen by a camera, carried to the base frame by the right product and by two wrong ones that still give valid points',
    ko: '카메라가 본 컵을 올바른 곱과 잘못된 곱 두 가지로 베이스 좌표계로 옮깁니다. 잘못된 곱도 올바른 점처럼 보이는 값을 줍니다',
    cap: ['The camera sits at (0.5, 0, 0.4) in the base frame and the cup at (0.2, 0, 0.5) in the camera frame. Turn the camera: the right product follows the cup, the wrong ones land elsewhere and nothing raises an error.',
      '카메라는 베이스 좌표계의 (0.5, 0, 0.4)에 있고 컵은 카메라 좌표계의 (0.2, 0, 0.5)에 있습니다. 카메라를 돌리면 올바른 곱은 컵을 따라가고 잘못된 곱은 엉뚱한 곳에 놓이지만 오류는 나지 않습니다.'],
    period: 12, rest: 3, cam: { yaw: .35, pitch: .55, dist: 7 }, unit: 150, look: [.3, 0, .4],
    controls: [{ id: 'yaw', en: 'camera yaw', ko: '카메라 yaw', min: 0, max: 180, step: 1, unit: '°', auto: t => 90 - 90 * Math.cos(2 * PI * t / 12) }],
  }, (s, t, m) => {
    const Rc = R.rz(rad(s.v.yaw)), Rt = [0, 1, 2].map(i => [0, 1, 2].map(j => Rc[j][i])), right = R.add(R.mv(Rc, cupC), tCam);
    const swapped = R.add(tCam, cupC), inv = R.sub(R.mv(Rt, cupC), R.mv(Rt, tCam)), err = q => Math.hypot(...R.sub(q, right));   // T_cam_cup @ T_base_cam, and inv(T_base_cam) @ T_cam_cup
    const frame = (Rm, o, len, w, c) => [['--bad', [1, 0, 0]], ['--ok', [0, 1, 0]], ['--pd', [0, 0, 1]]].forEach(([k, e]) => s.arrow(o, R.add(o, R.mv(Rm, e.map(x => x * len))), c || k, w));
    for (let i = -2; i <= 2; i++) { s.line([i * .4, -.8, 0], [i * .4, .8, 0], '--line', 1); s.line([-.8, i * .4, 0], [.8, i * .4, 0], '--line', 1); }
    frame(I3, O, .55, 3.5); s.label([0, 0, -.12], 'base', '--mut', 16, 'center', 0, 18);
    frame(Rc, tCam, .4, 3.5); s.label(R.add(tCam, [0, 0, -.1]), 'cam', '--mut', 16, 'center', 0, 18);
    s.arrow(tCam, right, '--ok', 2, { dash: [5, 4] }); s.dot(right, '--ok', 8, { ring: true, front: true });
    [[swapped, '--bad'], [inv, '--acc']].forEach(([q, c]) => { s.line(right, q, c, 1.5, { dash: [3, 4] }); s.dot(q, c, 7, { ring: true, front: true }); });
    s.text(14, 24, m.t('T_base_cam @ T_cam_cup', 'T_base_cam @ T_cam_cup'), '--ok', 15);
    s.text(14, 44, m.t(`swapped factors: off ${err(swapped).toFixed(2)} m`, `곱의 순서 바꿈: ${err(swapped).toFixed(2)} m 어긋남`), '--bad', 15);
    s.text(14, 64, m.t(`stray inverse: off ${err(inv).toFixed(2)} m`, `inverse 잘못 사용: ${err(inv).toFixed(2)} m 어긋남`), '--acc', 15);
  });
})();
