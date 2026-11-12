// Phase 16: capstone의 IK reference와 실제 planner waypoint를 3D에서 재생한다.
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], L = [.4, .4];
  const A = [.5, .1], B = [.15, .5];
  const waypoints = [[.4, .4], [A[0], A[1] + .1], A, [A[0], A[1] + .1], [B[0], B[1] + .1], B];
  function ik(p) {
    const [x, y] = p, c = (x * x + y * y - L[0] ** 2 - L[1] ** 2) / (2 * L[0] * L[1]);
    const n = Math.sqrt(1 - c * c);
    return [Math.atan2(y, x) - Math.atan2(L[1] * n, L[0] + L[1] * c), Math.atan2(n, c)];
  }
  const angles = waypoints.map(ik);
  const fk = q => [L[0] * Math.cos(q[0]) + L[1] * Math.cos(q[0] + q[1]),
    L[0] * Math.sin(q[0]) + L[1] * Math.sin(q[0] + q[1])];
  function arm(T) {
    const t = Math.min(5.5, Math.max(0, T)), i = Math.min(Math.floor(t), angles.length - 2), u = Math.min(t - i, 1);
    const blend = 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5;
    const q = angles[i].map((v, k) => v + (angles[i + 1][k] - v) * blend), tip = fk(q);
    return { q, elbow: [L[0] * Math.cos(q[0]), L[0] * Math.sin(q[0])], tip,
      object: t < 2 ? A : t < 5 ? tip : B, stage: t < 1 ? 0 : t < 2 ? 1 : t < 3 ? 2 : t < 4 ? 3 : t < 5 ? 4 : 5 };
  }
  // The lesson's planar y is vertical here: (x,y) -> (x,0,z=y), no kinematic change.
  const world = p => [p[0], 0, p[1]];
  const tipPath = Array.from({ length: 121 }, (_, i) => world(arm(5 * i / 120).tip));
  const stages = [['hover A', 'A 위로 이동'], ['pick A', 'A에서 집기'], ['lift', '들어 올리기'],
    ['hover B', 'B 위로 이동'], ['place B', 'B에 놓기'], ['placed', '놓기 완료']];
  window.MOTION.three('pick-place-arm-3d', {
    en: 'The capstone arm follows its six joint-space pick-and-place waypoints',
    ko: 'Capstone arm이 여섯 joint-space waypoint로 pick-and-place를 수행합니다',
    cap: ['This is the capstone planned reference: two 0.4 m links, its elbow-down IK, and 1 s quintic segments. It goes home → hover A → pick A → lift → hover B → place B. Dashed targets A=(0.50,0.10) m and B=(0.15,0.50) m have labels offset from the carried box; hover is 0.10 m above each. The lesson plane is drawn vertically. Tracking dynamics and grasp contact are not simulated here.',
      'Capstone의 planned reference입니다. 길이 0.4 m인 link 두 개와 수업의 elbow-down IK, 구간당 1 s인 quintic을 씁니다. Home에서 A 위로 이동해 집고 들어 올린 뒤 B 위로 옮겨 놓습니다. 점선 목표 A=(0.50,0.10) m와 B=(0.15,0.50) m의 라벨은 운반하는 상자에서 떨어져 있습니다. Hover는 각각 0.10 m 위입니다. 수업의 평면을 세워 그렸으며 tracking dynamics와 grasp contact는 계산하지 않습니다.'],
    period: 12, rest: 8, H: 390, unit: 300, look: [.25, 0, .17], oy: 28,
    cam: { yaw: .25, pitch: .3, dist: 7 }, model: arm,
    controls: [{ id: 'T', en: 'sequence time', ko: '동작 시간', min: 0, max: 5.5, step: .01, dec: 2, unit: ' s',
      auto: t => Math.min(5.5, Math.max(0, (t - 1) * 5.5 / 9)) }],
  }, (s, t, m) => {
    const a = arm(s.v.T), elbow = world(a.elbow), tip = world(a.tip), item = world(a.object);
    s.path(tipPath, '--line', 2, { dash: [3, 4] });
    // Floor and pedestal are schematic geometry; all joint origins stay at the lesson coordinates.
    s.poly([[-.08, -.15, -.06], [.65, -.15, -.06], [.65, .15, -.06], [-.08, .15, -.06]], '--mut', { a: .15 });
    s.box([0, 0, -.025], [.06, .08, .025], I, '--mut');
    for (const [p, name, color, offset] of [[world(A), 'A', '--bad', [.13, -.12, .04]], [world(B), 'B', '--ok', [-.13, -.12, .04]]]) {
      s.wire(p, [.035, .04, .025], I, color, 1.5, { dash: [4, 4] });
      const anchor = R.add(p, offset);
      s.line(p, anchor, color, 1, { dash: [2, 3] });
      s.label(anchor, name, color, 17, 'center', 0, -8);
    }
    s.line([0, 0, 0], elbow, '--pf', 12); s.line(elbow, tip, '--pl', 10);
    s.dot([0, 0, 0], '--fg', 6, { ring: true }); s.dot(elbow, '--fg', 7, { ring: true });
    s.box(item, [.025, .035, .025], I, '--bad');
    const closed = s.v.T >= 2 && s.v.T < 5, gap = closed ? .035 : .07;
    for (const sign of [-1, 1]) s.line(R.add(tip, [0, sign * gap, .025]), R.add(tip, [0, sign * gap, -.025]), '--fg', 3);
    s.text(14, 24, m.t(...stages[a.stage]), '--fg', 16);
    s.text(14, 46, m.t(`planned tip (${a.tip[0].toFixed(3)}, ${a.tip[1].toFixed(3)}) m`, `계획한 tip (${a.tip[0].toFixed(3)}, ${a.tip[1].toFixed(3)}) m`), '--pf', 15);
    s.text(14, 68, `q = (${a.q[0].toFixed(2)}, ${a.q[1].toFixed(2)}) rad`, '--mut', 15);
  });

  // 16/02 plan(inflate(make_world()), (1.5,1.5), (9,8.5)).
  // Keep full-precision cell-centre coordinates. The parity test reruns the lesson's A* and shortcut planner.
  const path = [[1.5, 1.5], [3.625, 7.375], [4.875, 7.375], [6.625, 2.625], [7.875, 2.625], [9, 8.5]];
  const lengths = [], cumulative = [0];
  for (let i = 0; i < path.length - 1; i++) {
    lengths.push(Math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]));
    cumulative.push(cumulative[i] + lengths[i]);
  }
  const total = cumulative[cumulative.length - 1];
  function navigation(u) {
    const distance = Math.max(0, Math.min(1, u)) * total;
    let i = 0;
    while (i < lengths.length - 1 && distance > cumulative[i + 1]) i++;
    const a = path[i], b = path[i + 1], f = (distance - cumulative[i]) / lengths[i];
    return { x: a[0] + f * (b[0] - a[0]), y: a[1] + f * (b[1] - a[1]),
      yaw: Math.atan2(b[1] - a[1], b[0] - a[0]), length: total, distance, segment: i };
  }
  const floorPath = path.map(([x, y]) => [x, y, .035]);
  // Six rectangular unions exactly cover make_world()'s occupied cells (40 x 40, RES=.25).
  const walls = [
    [[5, .125, .22], [5, .125, .22]], [[5, 9.875, .22], [5, .125, .22]],
    [[.125, 5, .22], [.125, 4.75, .22]], [[9.875, 5, .22], [.125, 4.75, .22]],
    [[4.25, 3.5, .22], [.25, 3.5, .22]], [[7.25, 6.5, .22], [.25, 3.5, .22]],
  ];
  // Display a smaller robot inside the nominal planning radius: the grid's
  // discrete inflation does not guarantee continuous clearance for a .4 m disc.
  const displayRadius = .2;
  const footprint = Array.from({ length: 33 }, (_, i) => [displayRadius * Math.cos(i * 2 * Math.PI / 32), displayRadius * Math.sin(i * 2 * Math.PI / 32), .03]);
  const data = { path, walls, resolution: .25, cells: 40, radius: .4, displayRadius };
  window.MOTION.three('navigation-floor-3d', {
    en: 'A mobile robot replays the capstone planned path around two staggered walls',
    ko: 'Mobile robot이 엇갈린 두 wall을 돌아가는 capstone의 planned path를 재생합니다',
    cap: ['The exact capstone A* path, shortened by its line-of-sight planner, runs from (1.5,1.5) to the lesson goal (9.00,8.50) m. The 40×40 grid has 0.25 m cells; planning still inflates obstacles by a nominal 0.4 m radius. The green ring shows a smaller 0.20 m display footprint, with 0.175 m minimum edge clearance along this path. Discrete inflation does not guarantee clearance for a 0.4 m disc. This replays the planned polyline at constant arc progress, with corner heading changes; it is not the pure-pursuit or noisy-odometry run.',
      'Capstone의 A* 경로를 수업의 line-of-sight planner로 줄인 결과입니다. (1.5,1.5)에서 수업의 목표 (9.00,8.50) m로 갑니다. 40×40 grid의 cell은 0.25 m이고 planner의 nominal radius는 0.4 m로 유지합니다. 초록색 고리는 표시용 반지름 0.20 m이며 이 경로에서 가장 가까운 장애물과 0.175 m 떨어져 있습니다. Grid 단위 inflation은 반지름 0.4 m인 원의 통과를 보장하지 않습니다. Planned polyline을 일정한 경로 길이 간격으로 재생하며 모서리에서 heading이 바뀝니다. Pure pursuit나 odometry noise를 넣은 주행 결과는 아닙니다.'],
    period: 12, rest: 7, H: 400, unit: 27, look: [5, 5, 0], oy: 38,
    cam: { yaw: .15, pitch: .9, dist: 28 }, model: navigation, data,
    controls: [{ id: 'u', en: 'path progress', ko: '경로 진행률', min: 0, max: 1, step: .001, dec: 3,
      auto: t => Math.min(1, Math.max(0, (t - 1) / 9)) }],
  }, (s, t, m) => {
    const a = navigation(s.v.u), rot = R.rz(a.yaw);
    s.poly([[0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 10, 0]], '--mut', { a: .13 });
    for (let i = 1; i < 10; i++) {
      s.line([i, 0, .01], [i, 10, .01], '--line', 1);
      s.line([0, i, .01], [10, i, .01], '--line', 1);
    }
    for (const [centre, half] of walls) s.box(centre, half, I, '--mut');
    s.path(floorPath, '--pf', 3);
    s.dot(floorPath[0], '--pf', 6, { ring: true }); s.dot(floorPath[floorPath.length - 1], '--ok', 7, { ring: true });
    for (const p of floorPath.slice(1, -1)) s.dot(p, '--pf', 3);
    s.path(footprint.map(p => [p[0] + a.x, p[1] + a.y, p[2]]), '--ok', 2);
    s.box([a.x, a.y, .2], [.14, .1, .17], rot, '--ok');
    s.arrow([a.x, a.y, .4], [a.x + .65 * Math.cos(a.yaw), a.y + .65 * Math.sin(a.yaw), .4], '--fg', 2.5);
    s.text(14, 24, m.t('A* + line-of-sight shortcuts', 'A* + line-of-sight 경로 단축'), '--fg', 15);
    s.text(14, 46, m.t(`distance ${a.distance.toFixed(2)} / ${total.toFixed(2)} m`, `경로 길이 ${a.distance.toFixed(2)} / ${total.toFixed(2)} m`), '--pf', 15);
    s.text(14, 68, `x ${a.x.toFixed(2)}, y ${a.y.toFixed(2)} m`, '--ok', 15);
  });
})();
