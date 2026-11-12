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
      'Capstone의 planned reference입니다. 길이 0.4 m인 link 두 개와 레슨의 elbow-down IK, 구간당 1 s인 quintic을 씁니다. Home에서 A 위로 이동해 집고 들어 올린 뒤 B 위로 옮겨 놓습니다. 점선 목표 A=(0.50,0.10) m와 B=(0.15,0.50) m의 라벨은 운반하는 상자에서 떨어져 있습니다. Hover는 각각 0.10 m 위입니다. 레슨의 평면을 세워 그렸으며 tracking dynamics와 grasp contact는 계산하지 않습니다.'],
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
      'Capstone의 A* 경로를 레슨의 line-of-sight planner로 줄인 결과입니다. (1.5,1.5)에서 레슨의 목표 (9.00,8.50) m로 갑니다. 40×40 grid의 cell은 0.25 m이고 planner의 nominal radius는 0.4 m로 유지합니다. 초록색 고리는 표시용 반지름 0.20 m이며 이 경로에서 가장 가까운 장애물과 0.175 m 떨어져 있습니다. Grid 단위 inflation은 반지름 0.4 m인 원의 통과를 보장하지 않습니다. Planned polyline을 일정한 경로 길이 간격으로 재생하며 모서리에서 heading이 바뀝니다. Pure pursuit나 odometry noise를 넣은 주행 결과는 아닙니다.'],
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

// Phase 16 (03): the capstone's cloned reaching policy with and without the deterministic safety wrapper, ported from the lesson.
(() => {
  const R = window.M3D, PI = Math.PI, clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const DT = .02, J = 1, B = .5, UMAX = 3;
  const plant = (q, v, u) => { v += DT * (u - B * v) / J; return [q + DT * v, v]; };
  const expert = (e, v) => clamp(8 * e - 4 * v, -UMAX, UMAX);
  // 40 episodes' (start q, target) from numpy default_rng(0), as in the lesson's demos()
  const EP = [[0.410885, -0.460427], [-1.377079, -0.966945], [0.939811, 0.825511], [0.319907, 0.458993], [0.130875, 0.870145], [0.947561, -0.994523], [1.072213, -0.932829], [0.688966, -0.648689], [1.089537, 0.082922], [-0.600864, -0.154626], [-1.415041, -0.751433], [0.511873, 0.294379], [0.346155, -0.232645], [1.49163, 0.961671], [0.556626, 0.300919], [0.56534, -0.222157], [-1.09471, 0.442977], [0.076063, -0.379516], [-0.042494, 0.778976], [1.302131, -0.28441], [0.214589, -0.356261], [0.2829, -0.324178], [-0.325143, 0.780549], [-0.818527, 0.246374], [-1.247954, 0.665288], [0.861295, -0.521261], [1.129453, -0.882864], [-0.491649, -0.699441], [-0.148982, 0.592649], [-0.808073, -0.895957], [-0.286344, -0.602974], [-1.227741, 0.160665], [-0.603912, 0.34399], [-0.901454, 0.884226], [-0.404669, -0.789009], [0.387324, 0.854309], [-0.178869, 0.909181], [-0.000313, -0.149543], [0.36064, 0.990193], [1.346831, -0.07991]];
  const X = [], Y = [];
  EP.forEach(([q0, target]) => { let q = q0, v = 0; for (let i = 0; i < 100; i++) { const e = target - q, u = expert(e, v); X.push([e, v]); Y.push(u); [q, v] = plant(q, v, u); } });
  function policy(e, v) {   // k = 5 nearest demonstrations, mean action
    const d = [], idx = [];
    for (let i = 0; i < X.length; i++) { const dx = X[i][0] - e, dy = X[i][1] - v, dd = dx * dx + dy * dy; if (idx.length < 5 || dd < d[4]) { let j = idx.length < 5 ? idx.length : 4; if (idx.length < 5) { idx.push(i); d.push(dd); } else { idx[4] = i; d[4] = dd; } while (j > 0 && d[j] < d[j - 1]) { [d[j], d[j - 1]] = [d[j - 1], d[j]]; [idx[j], idx[j - 1]] = [idx[j - 1], idx[j]]; j--; } } }
    return idx.reduce((a, i) => a + Y[i], 0) / 5;
  }
  function rollout(wrap, glitch, drop) {   // lesson rollout(): target 1.0, 150 steps; Safety(umax=3, du=0.5, max_age=3)
    let q = 0, v = 0, age = 0, last = [1, 0], u0 = 0; const n = {clip: 0, rate: 0, hold: 0}, r = {q: [], u: [], raw: [], n: []};
    for (let k = 0; k < 150; k++) {
      age = drop && k >= drop[0] && k < drop[1] ? age + 1 : 0;
      if (age === 0) last = [1 - q, v];
      const a = policy(last[0], last[1]) + (glitch && k === glitch ? 40 : 0);
      let u = a;
      if (wrap) {
        let raw = a; if (age > 3) { raw = 0; n.hold++; }
        const c = clamp(raw, -UMAX, UMAX); u = u0 + clamp(c - u0, -.5, .5);
        if (c !== raw) n.clip++; if (Math.abs(u - c) > 1e-9) n.rate++; u0 = u;   // the lesson counts `r != c`, which also fires on rounding error of u + (c − u)
      }
      [q, v] = plant(q, v, u); r.q.push(q); r.u.push(u); r.raw.push(a); r.n.push({...n});
    }
    return r;
  }
  const SCEN = [['clean', null, null], ['spike at step 30', 30, null], ['observation lost 10..35', null, [10, 36]]], cache = new Map();
  const get = sc => cache.get(sc) || (cache.set(sc, {raw: rollout(false, SCEN[sc][1], SCEN[sc][2]), wrapped: rollout(true, SCEN[sc][1], SCEN[sc][2])}), cache.get(sc));
  function arm(s, ox, q, u, c) {
    const o = [ox, 0, 0], tp = [ox + Math.cos(q), 0, Math.sin(q)];
    s.box([ox, 0, -.12], [.1, .08, .12], R.ry(0), '--pd'); s.box([(o[0] + tp[0]) / 2, 0, tp[2] / 2], [.5, .035, .035], R.ry(-q), c); s.dot(o, '--fg', 7, {ring: true, front: true});
    if (Math.abs(u) > 1e-6) { const sw = clamp(u / UMAX, -1, 1) * PI * 1.4, pts = Array.from({length: 25}, (_, i) => { const a = PI / 2 + sw * i / 24; return [ox + .2 * Math.cos(a), -.07, .2 * Math.sin(a)]; }); s.path(pts, c, 3, {front: true}); s.arrow(pts[23], pts[24], c, 3, {front: true}); }
  }
  window.MOTION.three('wrapped-policy-arms-3d', {
    en: 'Two identical joints run the same cloned reaching policy; the one behind the safety wrapper ignores a torque spike and a lost observation',
    ko: '똑같은 관절 둘이 같은 행동 복제 reaching policy를 돌립니다. 안전 wrapper 뒤의 관절은 torque 급등과 끊긴 관측을 무시합니다',
    cap: ['Both joints use the capstone’s nearest-neighbour policy (k = 5, fitted to 40 expert reaching episodes, the same 40 starts and targets as the lesson’s seed 0) to reach 1.0 rad. Left, raw: the policy’s action goes straight to the joint. Right, wrapped: clip to ±3 Nm, change at most 0.5 Nm per step, and command zero torque once the observation is more than 3 steps old. Scenario 1 adds +40 to the action at step 30; scenario 2 loses the observation at steps 10 to 35, so the policy keeps acting on the last one it saw. The curved arrows are the torque actually applied (full circle sweep at 3 Nm or more). The dashed line is the 1.0 rad target. Peak values match the lesson’s printout: raw spike 39.9 Nm and 1.36 rad against 3.0 Nm and 1.01 rad wrapped; lost observation 1.47 rad raw against 1.01 wrapped. The rate count here only counts real limiting (|u − c| above 1e-9), so it reads 5, 8 and 13 where the lesson prints 19, 20 and 19: its `r != c` test also counts floating-point rounding of u + (c − u).',
      '두 관절 모두 capstone의 nearest-neighbour policy(k = 5, expert reaching episode 40개로 fit, 시작점과 목표는 레슨의 seed 0과 같은 40개)로 1.0 rad에 가려고 합니다. 왼쪽 raw는 policy의 action이 관절로 곧바로 갑니다. 오른쪽 wrapped는 ±3 Nm로 clip하고 step당 변화를 0.5 Nm 이하로 제한하며 관측이 3 step보다 오래되면 torque 0을 명령합니다. 시나리오 1은 30 step에 action에 +40을 더하고 시나리오 2는 10~35 step 동안 관측이 끊겨 policy가 마지막으로 본 관측으로 계속 움직입니다. 굽은 화살표는 실제로 가해진 torque입니다(3 Nm 이상이면 원 한 바퀴 가까이 그립니다). 점선은 1.0 rad 목표입니다. 최댓값은 레슨의 출력과 같습니다. 급등 시나리오에서 raw는 39.9 Nm와 1.36 rad, wrapped는 3.0 Nm와 1.01 rad이고 관측 소실에서 raw 1.47 rad, wrapped 1.01 rad입니다. 여기서 rate 횟수는 실제로 제한된 경우(|u − c|가 1e-9보다 큼)만 세므로 5, 8, 13이고 레슨은 19, 20, 19를 출력합니다. 레슨의 `r != c` 검사가 u + (c − u)의 부동소수점 반올림 오차까지 세기 때문입니다.'],
    period: 12, rest: 5, H: 340, unit: 100, look: [.45, 0, .35], oy: 10, cam: {yaw: -.1, pitch: .2, dist: 7},
    controls: [{id: 'sc', en: 'scenario 0 clean, 1 spike, 2 lost observation', ko: '시나리오 0 정상, 1 급등, 2 관측 소실', min: 0, max: 2, step: 1, auto: t => Math.floor(t / 4) % 3},
      {id: 'k', en: 'step', ko: 'step', min: 0, max: 149, step: 1, auto: t => Math.floor((t % 4) / 4 * 149)}],
  }, (s, t, m) => {
    const {raw, wrapped} = get(s.v.sc), k = s.v.k, peak = (r, f) => Math.max(...r.slice(0, k + 1).map(f));
    s.model = {raw, wrapped, pu: [peak(raw.u, Math.abs), peak(wrapped.u, Math.abs)], pq: [peak(raw.q, x => x), peak(wrapped.q, x => x)]};
    const tgt = x => s.line([x, 0, 0], [x + 1.1, 0, 1.1 * Math.sin(1)].map((v, i) => i === 0 ? x + 1.1 * Math.cos(1) : v), '--ok', 2, {dash: [6, 4]});
    tgt(-1.3); tgt(1.3);
    arm(s, -1.3, raw.q[k], raw.u[k], '--bad'); arm(s, 1.3, wrapped.q[k], wrapped.u[k], '--ok');
    s.label([-1.3, 0, -.45], m.t('raw policy', 'raw policy'), '--bad', 13, 'center'); s.label([1.3, 0, -.45], m.t('with wrapper', 'wrapper 사용'), '--ok', 13, 'center');
    if (s.v.sc === 2 && k >= 10 && k < 36) s.label([0, 0, .8], m.t('observation lost', '관측 끊김'), '--mut', 13, 'center');
    const nn = wrapped.n[k];
    s.text(14, 24, m.t(`${SCEN[s.v.sc][0]}, step ${k}`, `${['정상', '30 step 급등', '관측 소실 10..35'][s.v.sc]}, step ${k}`), '--fg', 15);
    s.text(14, 44, m.t(`peak |u| so far: raw ${s.model.pu[0].toFixed(1)}, wrapped ${s.model.pu[1].toFixed(1)} Nm`, `지금까지 최대 |u|: raw ${s.model.pu[0].toFixed(1)}, wrapped ${s.model.pu[1].toFixed(1)} Nm`), '--mut', 15);
    s.text(14, 64, m.t(`peak q: raw ${s.model.pq[0].toFixed(2)}, wrapped ${s.model.pq[1].toFixed(2)} rad; wrapper clip ${nn.clip} rate ${nn.rate} hold ${nn.hold}`, `최대 q: raw ${s.model.pq[0].toFixed(2)}, wrapped ${s.model.pq[1].toFixed(2)} rad; wrapper clip ${nn.clip} rate ${nn.rate} hold ${nn.hold}`), '--ok', 14);
  });
})();
