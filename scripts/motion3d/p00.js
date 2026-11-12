// Phase 00: URDF의 parent-frame origin과 joint axis로 link tree를 그린다.
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  // Exact fields from 00/03 code/main.py URDF; fixed joints have no motion axis.
  const joints = [
    { name: 'shoulder', parent: 'base', child: 'upper', xyz: [0, 0, .1], yaw: 1.5707963, axis: [0, 0, 1] },
    { name: 'elbow', parent: 'upper', child: 'fore', xyz: [.3, 0, 0], yaw: 0, axis: [0, 0, 1] },
    { name: 'wrist', parent: 'fore', child: 'hand', xyz: [.2, 0, 0], yaw: 0 },
    { name: 'cam_mount', parent: 'upper', child: 'camera', xyz: [0, 0, .05], yaw: 0 },
  ];
  function model(shoulder, elbow) {
    const positions = { base: [0, 0, 0] }, rotations = { base: I }, axes = {};
    const angles = { shoulder, elbow };
    for (const j of joints) {
      const parentR = rotations[j.parent], originR = R.mm(parentR, R.rz(j.yaw));
      positions[j.child] = R.add(positions[j.parent], R.mv(parentR, j.xyz));
      if (j.axis) axes[j.name] = R.mv(originR, j.axis);
      rotations[j.child] = j.axis ? R.mm(originR, R.rz(angles[j.name])) : originR;
    }
    return { positions, rotations, axes };
  }
  window.MOTION.three('urdf-tree-3d', {
    en: 'URDF link tree with joint origins and axes in their parent frames',
    ko: '부모 frame을 기준으로 joint origin과 axis를 그린 URDF link tree입니다',
    cap: ['The lesson URDF has a labelled base → upper → fore → hand chain and a separate green camera branch. Each link has its own colour. A leader identifies the fixed camera mount above the shoulder. Each origin is transformed by its parent pose before the joint turns. Thick blue arrows show revolute axes; the wrist and camera mount are fixed. Thin x/y/z arrows show each joint frame.',
      '레슨 URDF의 base → upper → fore → hand 연결과 초록색 camera branch를 각각 라벨로 표시합니다. Link마다 색을 나누고 shoulder 위의 고정 camera mount는 안내선으로 짚습니다. 부모 pose로 origin을 옮긴 뒤 joint를 돌립니다. 굵은 파란 화살표는 revolute axis입니다. Wrist와 camera mount는 고정이며 가는 x/y/z 화살표는 각 joint frame입니다.'],
    period: 12, rest: 4, H: 400, unit: 330, look: [0, 0, .1], oy: 25,
    cam: { yaw: -.5, pitch: .65, dist: 7 }, model,
    controls: [
      { id: 'shoulder', en: 'shoulder', ko: 'shoulder', min: -3, max: 3, step: .01, dec: 2, unit: ' rad', auto: t => .7 * Math.sin(2 * Math.PI * t / 12) },
      { id: 'elbow', en: 'elbow', ko: 'elbow', min: -1, max: 1, step: .01, dec: 2, unit: ' rad', val: .6 },
    ],
  }, (s, t, m) => {
    const a = model(s.v.shoulder, s.v.elbow), p = a.positions;
    // Keep a fixed framing over the whole legal joint range (reach <= 0.5 m).
    const colors = { upper: '--mut', fore: '--pf', hand: '--bad', camera: '--ok' };
    s.box(p.base, [.045, .045, .018], I, '--mut');
    for (const j of joints) {
      const o = p[j.child], r = a.rotations[j.child], color = colors[j.child];
      s.line(p[j.parent], o, color, j.child === 'camera' ? 9 : 8, { front: j.child === 'camera' });
      s.dot(o, color, 5, { ring: true });
      for (let k = 0; k < 3; k++) {
        const v = [0, 0, 0]; v[k] = .045;
        s.arrow(o, R.add(o, R.mv(r, v)), ['--bad', '--ok', '--pd'][k], 1.5);
      }
      if (j.axis) s.arrow(o, R.add(o, R.mul(a.axes[j.name], .075)), '--acc', 3);
    }
    s.box(p.camera, [.032, .024, .024], a.rotations.camera, '--ok');
    // Keep fix8's anchor offsets; place 23px padded boxes afresh in priority order.
    const yaw = s.cam?.yaw ?? -.5, pitch = s.cam?.pitch ?? .65;
    const view = R.mm(R.rx(pitch), R.rz(yaw)), inverse = R.mm(R.rz(-yaw), R.rx(-pitch));
    const placed = [], labels = [
      [p.base, -18, 28, 'base', '--mut', 'right'],
      [p.camera, -44, 33, 'camera', '--ok', 'right', true],
      [p.hand, -42, -5, 'hand', '--pd', 'right', true],
      [R.mul(R.add(p.upper, p.fore), .5), 80, 53, 'upper', '--pf', 'left', true],
      [R.mul(R.add(p.fore, p.hand), .5), 18, -40, 'fore', '--bad', 'center'],
    ];
    for (const [anchor, dx, dy, text, color, align, leader] of labels) {
      const q = R.mv(view, R.sub(anchor, [0, 0, .1])), scale = 330 * 7 / (7 + q[1]);
      const originY = 225 - scale * q[2];
      const x = 240 + scale * q[0] + dx, start = originY + dy, width = text.length * 10;
      const left = x - (align === 'right' ? width : align === 'center' ? width / 2 : 0) - 3, right = left + width + 6;
      let y = start, step = 23;
      while (placed.some(b => left <= b[1] && right >= b[0] && y - 19 <= b[3] && y + 4 >= b[2])) {
        y += step;
        if (y + 4 > 400) { step = -23; y = start - 23; }
      }
      placed.push([left, right, y - 19, y + 4]);
      if (leader || y !== start) {
        const endY = align === 'center' ? y + (y < originY ? 8 : -24) : y - 5;
        const endX = dx + (align === 'right' ? 8 : align === 'left' ? -8 : 0);
        const end = R.add(anchor, R.mv(inverse, [endX / scale, 0, -(endY - originY) / scale]));
        s.line(anchor, end, color, 1.5, { front: true });
      }
      s.label(anchor, text, color, 16, align, dx, y - originY);
    }
    s.text(14, 24, 'base → upper → fore → hand', '--fg', 15);
    s.text(14, 45, m.t('upper → camera (fixed branch)', 'upper → camera (고정 branch)'), '--ok', 15);
    s.text(14, 66, m.t('blue: joint axis; dots: origins', '파랑: joint axis, 점: origin'), '--acc', 15);
    s.text(14, 363, `shoulder ${s.v.shoulder.toFixed(2)} / elbow ${s.v.elbow.toFixed(2)} rad`, '--mut', 15);
  });
})();

// 00단계 3D (wave 1): 도/라디안 guard 팔, 진자 time step, ROS 2 topic queue.
(() => {
  const R = window.M3D, PI = Math.PI, TAU = 2 * PI, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));

  // ---- 00/01 main.py: looks_like_degrees(q, limit = 2*pi); joint_angles refuses the number, numpy alone rotates by it as radians.
  window.MOTION.three('degrees-guard-arm-3d', {
    en: 'A joint is sent one number. Read as radians it spins the arm many turns, read as degrees it is a small angle, and the guard refuses anything above 2π',
    ko: 'joint에 숫자 하나를 보냅니다. radian으로 읽으면 팔이 여러 바퀴 돌고 degree로 읽으면 작은 각도이며, guard는 2π보다 큰 값을 거부합니다',
    cap: ['Solid arm: the number read as radians, as numpy would use it (cos and sin wrap, so 90 rad is 14.3 turns and lands near 115°). Faint green arm: the same number meant as degrees. With the guard on, joint_angles raises ValueError when max |q| > 2π = 6.283 (the lesson limit), so the arm stays at rest; 1.5 and 0.8 pass silently. A continuous joint can really pass 2π, which the lesson notes. The picture shows one joint only.',
      '굵은 팔은 숫자를 radian으로 읽은 자세이며 numpy가 그대로 쓰는 값입니다(cos와 sin이 한 바퀴씩 돌아 90 rad는 14.3바퀴이고 약 115° 근처에 놓입니다). 옅은 초록 팔은 같은 숫자를 degree로 뜻했을 때의 자세입니다. Guard를 켜면 max |q| > 2π = 6.283(레슨의 limit)일 때 joint_angles가 ValueError를 내므로 팔은 정지 자세에 머물고 1.5와 0.8은 조용히 통과합니다. Continuous joint는 2π를 넘을 수 있다고 레슨이 말합니다. 그림은 joint 하나만 보여 줍니다.'],
    period: 12, rest: 10, H: 340, unit: 120, look: [0, 0, 0], oy: 40,
    cam: {yaw: .25, pitch: .3, dist: 7},
    controls: [
      {id: 'q', en: 'number sent as q', ko: 'q로 보낸 숫자', min: 0, max: 100, step: .1, dec: 1, auto: t => clamp((t - .5) / 9, 0, 1) * 100},
      {id: 'guard', toggle: true, en: 'joint_angles guard', ko: 'joint_angles guard', val: true},
    ],
  }, (s, t, m) => {
    const v = s.v.q, refused = s.v.guard && v > TAU, a = refused ? 0 : v, o = [0, 0, 0];
    const ring = Array.from({length: 61}, (_, i) => [.8 * Math.cos(i * TAU / 60), -.02, .8 * Math.sin(i * TAU / 60)]);
    s.path(ring, '--mut', 1.5, {a: .5, dash: [4, 4]});
    [0, 90, 180, 270].forEach(d => s.line([.74 * Math.cos(d * PI / 180), -.02, .74 * Math.sin(d * PI / 180)], [.86 * Math.cos(d * PI / 180), -.02, .86 * Math.sin(d * PI / 180)], '--mut', 2));
    s.box([0, 0, -.2], [.12, .1, .2], I, '--pd');
    const arm = (ang, c, al, y) => {
      const e = [.8 * Math.cos(ang), y, .8 * Math.sin(ang)];
      s.box([e[0] / 2, y, e[2] / 2], [.4, .035, .035], R.ry(-ang), c, {a: al});
      return e;
    };
    arm(v * PI / 180, '--ok', .35, .05);
    const tip = arm(a, refused ? '--mut' : v > TAU ? '--bad' : '--pf', 1, 0);
    s.dot(o, '--fg', 7, {ring: true, front: true}); s.dot(tip, refused ? '--mut' : '--acc', 6, {ring: true, front: true});
    s.text(14, 24, `q = ${v.toFixed(1)}  →  ${(v / TAU).toFixed(1)} turns as radians`, '--fg', 15);
    s.text(14, 44, `as radians: cos q = ${Math.cos(v).toFixed(3)}`, '--bad', 15);
    s.text(14, 64, `as degrees: cos q = ${Math.cos(v * PI / 180).toFixed(3)}`, '--ok', 15);
    s.text(14, 84, !s.v.guard ? m.t('guard off: the arm just spins', 'guard 꺼짐: 팔이 그냥 돕니다') : refused ? `ValueError: max |q| ${v.toFixed(1)} > 2π = 6.283` : m.t('guard silent: |q| ≤ 2π', 'guard 조용함: |q| ≤ 2π'), refused ? '--bad' : '--mut', 15);
  });

  // ---- 00/02 main.py step(): omega -= dt*(g/L)*sin(theta); semi uses the NEW omega for theta, explicit uses the old one. L = 1 m.
  const G = 9.81, L1 = 1, TH0 = .3, sims = {};
  function swing(dtMs, semi) {
    const key = dtMs + (semi ? 's' : 'e');
    if (sims[key]) return sims[key];
    const dt = dtMs / 1000, n = Math.round(12 / dt), th = new Float64Array(n + 1), om = new Float64Array(n + 1);
    th[0] = TH0;
    for (let i = 0; i < n; i++) {
      om[i + 1] = om[i] - dt * (G / L1) * Math.sin(th[i]);
      th[i + 1] = th[i] + dt * (semi ? om[i + 1] : om[i]);
    }
    return sims[key] = {th, om, n};
  }
  const energy = (th, om) => .5 * (L1 * om) ** 2 + G * L1 * (1 - Math.cos(th));
  window.MOTION.three('pendulum-timestep-3d', {
    en: 'Two identical pendulums start together. One uses the semi-implicit update, the other the explicit one, and a bigger time step makes the explicit one gain energy',
    ko: '똑같은 진자 두 개가 함께 출발합니다. 하나는 semi-implicit update, 하나는 explicit update를 쓰며 time step이 커지면 explicit 쪽이 energy를 얻습니다',
    cap: ['Both use the lesson step: ω ← ω − dt (g/L) sin θ, then θ ← θ + dt ω with the new ω (semi-implicit, green) or the old ω (explicit, red). L = 1 m, so small swings take 2π√(L/g) = 2.006 s. The lesson starts at 0.05 rad; the picture starts at 0.3 rad so the swing is visible. E is energy per unit mass, ½(Lω)² + gL(1 − cos θ), compared with its start value. A point-mass pendulum without friction or MuJoCo contacts.',
      '두 진자 모두 레슨의 step인 ω ← ω − dt (g/L) sin θ를 쓰고, θ는 새 ω(semi-implicit, 초록) 또는 옛 ω(explicit, 빨강)로 갱신합니다. L = 1 m이므로 작은 진동의 주기는 2π√(L/g) = 2.006 s입니다. 레슨은 0.05 rad에서 시작하지만 그림은 진동이 보이도록 0.3 rad에서 시작합니다. E는 단위 질량당 energy ½(Lω)² + gL(1 − cos θ)이며 시작값과 비교합니다. 마찰이나 MuJoCo contact가 없는 점질량 진자입니다.'],
    period: 12, rest: 3, H: 340, unit: 130, look: [0, 0, -.45], oy: 40,
    cam: {yaw: .45, pitch: .22, dist: 7},
    controls: [{id: 'dt', en: 'time step dt', ko: 'time step dt', min: 1, max: 50, step: 1, unit: ' ms', val: 25}],
  }, (s, t, m) => {
    const E0 = energy(TH0, 0), top = [0, 0, 0];
    s.box([0, 0, .04], [.08, .5, .04], I, '--pd');
    [-.5, .5].forEach(y => s.box([0, y, -.45], [.025, .025, .5], I, '--pd'));
    [[-.3, true, '--ok', 'semi-implicit', 22], [.3, false, '--bad', 'explicit', 22]].forEach(([y, semi, c, name], k) => {
      const dtm = Math.round(s.v.dt), r = swing(dtm, semi), i = Math.min(r.n, Math.floor(t / (dtm / 1000))), th = r.th[i];
      const bob = [L1 * Math.sin(th), y, -L1 * Math.cos(th)], pv = [0, y, 0];
      s.line(pv, bob, c, 3); s.dot(bob, c, 11, {ring: true, front: true}); s.dot(pv, '--fg', 4, {front: true});
      s.text(14, 24 + 20 * k, `${name}: E / E0 = ${(energy(th, r.om[i]) / E0).toFixed(2)}`, c, 15);
    });
    s.text(14, 64, `dt = ${Math.round(s.v.dt)} ms, T = 2π√(L/g) = ${(TAU * Math.sqrt(L1 / G)).toFixed(3)} s`, '--mut', 14);
  });

  // ---- 00/04 main.py Bus/run(): publisher 100 Hz, subscriber takes one message per tick at 40 Hz, KEEP_LAST depth, 10 s run.
  const PUB = 100, SUB = 40, SECS = 10, ev = [], qs = {};
  for (let i = 0; i < PUB * SECS; i++) ev.push([i / PUB, 0]);
  for (let j = 0; j < SUB * SECS; j++) ev.push([j / SUB, 1]);
  ev.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  function queue(d) {   // one row per event: time, head, tail (queue = messages head..tail-1), dropped, age of the last taken message
    if (qs[d]) return qs[d];
    let head = 0, tail = 0, dropped = 0, age = 0;
    return qs[d] = ev.map(([tm, k]) => {
      if (k === 0) { if (tail - head === d) { head++; dropped++; } tail++; }
      else if (tail > head) { age = tm - head / PUB; head++; }
      return [tm, head, tail, dropped, age];
    });
  }
  window.MOTION.three('topic-queue-tray-3d', {
    en: 'A fast publisher fills a tray of fixed depth, a slower subscriber takes one message at a time, and the oldest messages fall off when the tray is full',
    ko: '빠른 publisher가 정해진 depth의 tray를 채우고 느린 subscriber가 메시지를 하나씩 가져가며, tray가 차면 가장 오래된 메시지가 떨어집니다',
    cap: ['The publisher sends at 100 Hz and the subscriber takes one message per tick at 40 Hz, as in the lesson run of 10 s (1000 sent). The tray is the KEEP_LAST queue of the chosen depth; paler cells are older messages. The red column counts messages thrown away; a deeper tray drops fewer but the message taken is older. One topic, one subscriber, no network.',
      'Publisher는 100 Hz로 보내고 subscriber는 40 Hz tick마다 하나씩 가져갑니다. 레슨의 10초 실행(1000개 전송)과 같습니다. Tray는 고른 depth의 KEEP_LAST queue이며 옅은 칸일수록 오래된 메시지입니다. 빨간 기둥은 버려진 메시지 수입니다. 더 깊은 tray는 덜 버리지만 가져가는 메시지가 더 오래됩니다. topic 하나와 subscriber 하나이며 network는 없습니다.'],
    period: 10, rest: 10, H: 330, unit: 100, look: [0, 0, 0], oy: 30,
    cam: {yaw: .3, pitch: .5, dist: 7},
    controls: [{id: 'depth', en: 'queue depth', ko: 'queue depth', min: 1, max: 50, step: 1, val: 10}],
  }, (s, t, m) => {
    const d = Math.round(s.v.depth), rows = queue(d), now = Math.min(t, SECS - 1e-9);
    let lo = 0, hi = rows.length - 1;
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (rows[mid][0] <= now) lo = mid; else hi = mid - 1; }
    const [tm, head, tail, dropped, age] = rows[lo], cw = Math.min(.2, 2.4 / d), x0 = -d * cw / 2;
    s.box([-1.85, 0, 0], [.18, .2, .2], I, '--pf'); s.box([1.85, 0, 0], [.18, .2, .2], I, '--ok');
    s.arrow([-1.6, 0, 0], [-1.3, 0, 0], '--pf', 3); s.arrow([1.3, 0, 0], [1.6, 0, 0], '--ok', 3);
    s.box([0, 0, -.1], [d * cw / 2 + .02, .18, .02], I, '--mut', {a: .6});
    for (let k = 0; k < tail - head; k++) {   // k = 0 is the oldest message, nearest the subscriber
      const old = (tm - (head + k) / PUB) / (d / PUB + .02);
      s.box([x0 + d * cw - (k + .5) * cw, 0, .0], [cw * .42, .13, .09], I, '--pl', {a: clamp(1 - .65 * old, .3, 1)});
    }
    s.box([-1.1, -.55, -.1 + dropped / 1000 * .5], [.12, .12, dropped / 1000 * .5 + .01], I, '--bad');
    s.text(14, 24, `depth ${d}, published ${tail}, dropped ${dropped}`, '--fg', 15);
    s.text(14, 44, `${m.t('age of the last message taken', '마지막으로 가져간 메시지의 나이')}: ${(age * 1000).toFixed(0)} ms`, '--fg', 15);
    s.label([-1.85, 0, .3], 'pub 100 Hz', '--pf', 14, 'center'); s.label([1.85, 0, .3], 'sub 40 Hz', '--ok', 14, 'center');
    s.label([-1.1, -.55, .62], m.t('dropped', '버려짐'), '--bad', 14, 'center');
  });
})();
