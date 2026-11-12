// 09단계 3D: lesson의 RRT extend와 segment 검사를 구와 3차원 거리로 확장한다.
(() => {
  const R = window.M3D, STEP = .4, SEED = 0;
  const obstacles = [[[5, 5, 5], 2], [[3, 7.5, 5], 1.2], [[7.5, 3, 5], 1.2]];
  // A reproducible integer sampler, not a browser RNG. Seed 0 has a pinned tree.
  const random = seed => { let state = seed + 1; return () => { state = (Math.imul(state, 1664525) + 1013904223) >>> 0; return state / 2 ** 32; }; };
  function free(a, b) {
    const d = R.sub(b, a), l2 = R.dot(d, d);
    for (const [c, r] of obstacles) {
      const u = l2 === 0 ? 0 : Math.max(0, Math.min(1, R.dot(R.sub(c, a), d) / l2));
      if (Math.hypot(...R.sub(R.add(a, R.mul(d, u)), c)) <= r) return false;
    }
    return true;
  }
  function grow() {
    const rng = random(SEED), nodes = [[1, 1, 1]], parents = [-1], goal = [9, 9, 9];
    let path = [];
    for (let it = 0; it < 3000; it++) {
      const sample = rng() < .1 ? goal : [rng() * 10, rng() * 10, rng() * 10];
      let near = 0, best = Infinity;
      nodes.forEach((p, i) => { const d = R.sub(sample, p), d2 = R.dot(d, d); if (d2 < best) {best = d2; near = i;} });
      const d = R.sub(sample, nodes[near]), dist = Math.sqrt(best);
      if (dist === 0) continue;
      const next = R.add(nodes[near], R.mul(d, Math.min(STEP, dist) / dist));
      if (!free(nodes[near], next)) continue;
      nodes.push(next); parents.push(near);
      if (Math.hypot(...R.sub(goal, next)) <= STEP && free(next, goal)) {
        parents.push(nodes.length - 1); nodes.push(goal);
        for (let k = nodes.length - 1; k !== -1; k = parents[k]) path.push(nodes[k]);
        path.reverse(); break;
      }
    }
    return {seed: SEED, step: STEP, nodes, parents, path, obstacles};
  }
  // Static geometry and the tree are built once per loaded phase, never per draw.
  const tree = grow(), rings = obstacles.map(([c, r]) => [0, 1, 2].map(axis => {
    const pts = [];
    for (let i = 0; i <= 32; i++) {
      const a = i * 2 * Math.PI / 32, p = [r * Math.cos(a), r * Math.sin(a), 0];
      if (axis === 1) [p[1], p[2]] = [p[2], p[1]];
      if (axis === 2) [p[0], p[2]] = [p[2], p[0]];
      pts.push(R.add(c, p));
    }
    return pts;
  }));
  // Fixed sphere faces provide occlusion; back-facing faces are culled per view.
  const surfaces = obstacles.map(([c, r]) => {
    const point = (lat, lon) => R.add(c, [r * Math.cos(lat) * Math.cos(lon), r * Math.cos(lat) * Math.sin(lon), r * Math.sin(lat)]);
    const faces = [];
    for (let j = 0; j < 8; j++) for (let i = 0; i < 16; i++) {
      const a = -Math.PI / 2 + j * Math.PI / 8, b = a + Math.PI / 8, u = i * Math.PI / 8, v = u + Math.PI / 8;
      const pts = [point(a, u), point(a, v), point(b, v), point(b, u)];
      const normal = R.sub(point((a + b) / 2, (u + v) / 2), c);
      faces.push({ pts, normal });
    }
    return faces;
  });
  window.MOTION.three('rrt-volume-3d', {
    en: 'A seeded RRT grows through a cube around spherical obstacles; short collision-free edges join the start to the goal',
    ko: 'seed를 고정한 RRT가 구형 장애물을 피해 정육면체 안에서 자랍니다. 충돌 없는 짧은 edge를 이어 start에서 goal로 갑니다',
    cap: ['The lesson’s nearest-node step, capped at 0.4, and closest-point segment collision test are extended from 2D circles to 3D spheres. The cube is [0,10]³; z coordinates lift the lesson’s start, goal and obstacle centres. Seed 0 fixes the samples. Dark branches show the search tree; shaded sphere faces obscure branches behind them and rear outlines fade. The green path appears only after the goal connects.',
      'lesson의 nearest-node step을 최대 0.4로 제한하고 segment의 가장 가까운 점을 검사합니다. 2D 원을 3D 구로 확장한 예입니다. 영역은 [0,10]³이고 lesson의 start, goal, 장애물 중심에 z좌표를 더했습니다. Seed는 0입니다. 진한 가지는 탐색 tree입니다. 구의 음영 면은 뒤쪽 가지를 가리고 뒤쪽 윤곽선은 흐리게 표시합니다. Goal에 연결된 뒤에만 초록색 경로를 표시합니다.'],
    period: 12, rest: 10, H: 380, unit: 17, look: [5, 5, 5], oy: 10,
    cam: {yaw: .55, pitch: .45, dist: 30},
    controls: [{id: 'growth', en: 'tree fraction', ko: 'tree 진행 비율', min: 0, max: 1, step: .01, dec: 2, auto: t => Math.max(0, Math.min(1, (t - 1) / 8))}],
  }, (s, t, m) => {
    const n = 1 + Math.floor(s.v.growth * (tree.nodes.length - 1));
    s.model = tree;
    s.wire([5, 5, 5], [5, 5, 5], [[1, 0, 0], [0, 1, 0], [0, 0, 1]], '--line', 1);
    const cam = s.cam || { yaw: .55, pitch: .45 }, view = R.mm(R.rx(cam.pitch), R.rz(cam.yaw));
    surfaces.forEach(sphere => sphere.forEach(({ pts, normal }) => {
      if (R.mv(view, normal)[1] <= 0) s.poly(pts, '--bad', { a: .85 });
    }));
    rings.forEach((sphere, k) => sphere.forEach(ring => {
      for (let i = 1; i < ring.length; i++) {
        const radial = R.sub(R.mul(R.add(ring[i - 1], ring[i]), .5), obstacles[k][0]);
        const back = R.mv(view, radial)[1] > 0;
        s.line(ring[i - 1], ring[i], '--bad', back ? 1 : 2, { a: back ? .12 : .95 });
      }
    }));
    for (let i = 1; i < n; i++) s.line(tree.nodes[tree.parents[i]], tree.nodes[i], '--fg', 2, {a: .8});
    if (n === tree.nodes.length) for (let i = 1; i < tree.path.length; i++) s.line(tree.path[i - 1], tree.path[i], '--ok', 4);
    s.dot(tree.nodes[0], '--ok', 6, {ring: true});
    s.dot([9, 9, 9], '--pl', 6, {ring: true});
    s.dot(tree.nodes[n - 1], '--pf', 5, {ring: true});
    s.text(14, 24, m.t('Seed 0 / thin tree / thick path', 'seed 0 / 가는 tree / 굵은 경로'), '--fg', 15);
    s.text(14, 44, m.t(`${n} nodes; step ≤ ${STEP}`, `node ${n}개; step ≤ ${STEP}`), '--mut', 15);
  });
})();

// 09단계 3D 추가: 속도 프로파일 카트, 간격 검사의 터널링, 경로 줄다리기, 격자 탐색 가중치.
(() => {
  const R = window.M3D, PI = Math.PI, I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  function post(s, c, r, h, color, n) {   // vertical cylinder: side quads and a cap
    const ring = z => Array.from({length: n}, (_, i) => [c[0] + r * Math.cos(2 * PI * i / n), c[1] + r * Math.sin(2 * PI * i / n), z]);
    const lo = ring(0), hi = ring(h);
    for (let i = 0; i < n; i++) { const j = (i + 1) % n; s.poly([lo[i], lo[j], hi[j], hi[i]], color, {a: 1, edge: '--card', w: 1}); }
    s.poly(hi, color, {a: 1, edge: '--card', w: 1.5});
  }

  const circ = (c, r, z, n) => Array.from({length: n + 1}, (_, i) => [c[0] + r * Math.cos(2 * PI * i / n), c[1] + r * Math.sin(2 * PI * i / n), z]);

  // 09/01 trajectory profiles
  const prof = {
    cubic: (u, T) => ({q: 3 * u * u - 2 * u ** 3, a: 6 / T / T * (1 - 2 * u)}),
    quintic: (u, T) => ({q: 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5, a: (60 * u - 180 * u * u + 120 * u ** 3) / T / T}),
    trapezoid: (u, T) => {   // ta = T/4 as in the lesson (ta 0.5 s for T 2 s)
      const ta = T / 4, t = u * T, vm = 1 / (T - ta), a = vm / ta;
      if (t < ta) return {q: .5 * a * t * t, a};
      if (t > T - ta) return {q: 1 - .5 * a * (T - t) ** 2, a: -a};
      return {q: vm * (t - ta / 2), a: 0};
    },
  };
  const LANES = [['cubic', '--pf', .62], ['quintic', '--ok', 0], ['trapezoid', '--pl', -.62]];
  window.MOTION.three('trajectory-lanes-3d', {
    en: 'Three carts travel the same 1 m in the same time; their acceleration curves show which start with a jump',
    ko: '같은 1 m를 같은 시간에 가는 카트 세 대입니다. 가속도 곡선으로 어느 쪽이 튀며 출발하는지 보입니다',
    cap: ['Each lane moves d = 1 m in T s (lesson formulas; trapezoid accelerates for T/4). The curve is acceleration against time, the arrow is acceleration now. Cubic and trapezoid jump at t = 0 (infinite jerk); quintic starts at 0, peak jerk 60 d/T^3 = 7.5 m/s^3 at T = 2.',
      '세 lane은 lesson의 식대로 1 m를 T초에 이동합니다(trapezoid는 T/4 동안 가속). 곡선은 시간에 따른 가속도, 화살표는 지금의 가속도입니다. cubic과 trapezoid는 t = 0에서 튀고(jerk 무한대) quintic은 0에서 시작하며 T = 2에서 peak jerk 60 d/T^3 = 7.5 m/s^3입니다.'],
    period: 12, rest: 5, H: 350, unit: 230, look: [.5, 0, .15], oy: 26,
    cam: {yaw: .5, pitch: .38, dist: 7},
    controls: [{id: 'T', en: 'move time T', ko: '이동 시간 T', min: 1, max: 3, step: .1, dec: 1, unit: ' s', auto: t => 2 + .9 * Math.sin(2 * PI * t / 12)}],
  }, (s, t, m) => {
    const T = s.v.T, u = clamp((t % (T + 1.2)) / T, 0, 1);
    s.text(14, 24, `T = ${T.toFixed(1)} s, d = 1 m`, '--fg', 15);
    LANES.forEach(([name, color, y], k) => {
      const f = prof[name], now = f(u, T);
      s.box([.5, y, -.03], [.62, .03, .012], I3, '--pd');
      s.box([now.q, y, .04], [.07, .1, .045], I3, color);
      const trace = [];
      const jump = Math.abs(f(0, T).a);
      for (let i = 0; i <= 40; i++) { const a = f(i / 40, T).a; trace.push([i / 40, y, .34 + a * .04]); }
      s.path(trace, color, 2.2);
      const bad = name !== 'quintic';
      s.dot([u, y, .34 + now.a * .04], color, 5, {ring: true});
      s.arrow([now.q, y, .16], [now.q + now.a * .08, y, .16], '--bad', 2.5, {front: true});
      s.label([-.1, y, .02], name, color, 15, 'right');
      const txt = bad ? m.t(`a jumps ${jump.toFixed(2)} at start`, `시작에서 a가 ${jump.toFixed(2)} 튐`)
        : m.t(`jerk ≤ ${(60 / T ** 3).toFixed(1)}, a starts at 0`, `jerk ≤ ${(60 / T ** 3).toFixed(1)}, a는 0에서 시작`);
      s.text(14, 48 + 20 * k, `${name}: ${txt}`, bad ? '--bad' : '--ok', 15);
    });
  });

  // 09/03 collision checking
  const A = 0, B = 10, POST = 5.5, RAD = .1;
  function sweep(step, pad) {
    const n = Math.max(1, Math.ceil((B - A) / step)), pts = [];
    let hit = false;
    for (let i = 0; i <= n; i++) { const x = i === n ? B : A + i * (1 / n) * (B - A), h = Math.abs(x - POST) <= RAD + pad; hit = hit || h; pts.push([x, h]); }
    return {pts, hit};
  }
  window.MOTION.three('swept-check-corridor-3d', {
    en: 'A robot is checked only at sample points along a corridor with one thin post; coarse samples step over it',
    ko: '복도의 sample 지점에서만 로봇을 검사하면 간격이 클 때 가는 기둥을 건너뜁니다',
    cap: ['Lesson line (0, 0) to (10, 0), post r = 0.1 at x = 5.5, top view at true scale. Dots are checked points (red inside the post); the dashed ring is the post padded by step/2. Plain sampling misses at step 1.0 and 0.4 and hits at 0.1; padding never misses. The robot is a point. The view crops the corridor to x = 2.7 to 8.3.',
      'Lesson의 선분 (0, 0)~(10, 0)과 x = 5.5의 기둥(r = 0.1)을 실제 척도로 위에서 본 그림입니다. 점은 검사 지점(기둥 안이면 빨강), 점선 고리는 step/2만큼 부풀린 기둥입니다. 점만 검사하면 step 1.0과 0.4에서 놓치고 0.1에서 잡으며 부풀리면 놓치지 않습니다. 로봇은 점이며 화면은 복도의 x = 2.7~8.3만 보여 줍니다.'],
    period: 14, rest: 6, unit: 90, look: [5.5, 0, 0], oy: 8,
    cam: {yaw: .12, pitch: .95, dist: 9},
    controls: [{id: 'step', en: 'sample spacing', ko: 'sample 간격', min: .05, max: 1.2, step: .05, dec: 2, unit: ' m', auto: t => .65 + .55 * Math.cos(2 * PI * t / 14)}],
  }, (s, t, m) => {
    const step = s.v.step, plain = sweep(step, 0), padded = sweep(step, step / 2), pad = step / 2;
    post(s, [POST, 0], RAD, .5, '--pd', 10);
    s.path(circ([POST, 0], RAD + pad, .02, 24), '--pl', 1.8, {dash: [4, 3]});
    s.line([0, 0, 0], [10, 0, 0], '--mut', 1.5);
    plain.pts.forEach(([x, h]) => s.dot([x, 0, .03], h ? '--bad' : '--ok', 3.4));
    const x = (t * 1.4) % 11;
    s.box([Math.min(x, 10), 0, .1], [.18, .12, .08], I3, '--pf');
    const w = h => h ? m.t('hit', '충돌') : m.t('miss', '놓침');
    s.text(14, 24, m.t(`step ${step.toFixed(2)} m, ${plain.pts.length} points`, `간격 ${step.toFixed(2)} m, 점 ${plain.pts.length}개`), '--fg', 15);
    s.text(14, 44, m.t('exact segment test: hit', '정확한 선분 검사: 충돌'), '--bad', 15);
    s.text(14, 64, m.t(`swept points only: ${w(plain.hit)}`, `점만 검사: ${w(plain.hit)}`), plain.hit ? '--ok' : '--bad', 15);
    s.text(14, 84, m.t(`padded by step/2: ${w(padded.hit)}`, `step/2만큼 부풀림: ${w(padded.hit)}`), padded.hit ? '--ok' : '--bad', 15);
  });

  // 09/04 trajectory optimisation
  const OBS = [[[3.5, .3], 1], [[7, -.5], 1]], MARGIN = .4, NP = 22, cacheOpt = {};
  function optimise(wo) {
    const key = Math.round(wo * 4);
    if (cacheOpt[key]) return cacheOpt[key];
    const X = Array.from({length: NP}, (_, i) => [10 * i / (NP - 1), 0]), g = Array.from({length: NP}, () => [0, 0]);
    for (let it = 0; it < 4000; it++) {
      for (let i = 1; i < NP - 1; i++) {
        g[i][0] = 2 * X[i][0] - X[i - 1][0] - X[i + 1][0]; g[i][1] = 2 * X[i][1] - X[i - 1][1] - X[i + 1][1];
        for (const [c, r] of OBS) {
          const vx = X[i][0] - c[0], vy = X[i][1] - c[1], d = Math.hypot(vx, vy), pen = Math.max(0, r + MARGIN - d);
          if (pen > 0) { g[i][0] -= 2 * wo * pen * vx / Math.max(d, 1e-9); g[i][1] -= 2 * wo * pen * vy / Math.max(d, 1e-9); }
        }
      }
      for (let i = 1; i < NP - 1; i++) { X[i][0] -= .04 * g[i][0]; X[i][1] -= .04 * g[i][1]; }
    }
    let clear = 1e9;
    X.forEach(p => { for (const [c, r] of OBS) clear = Math.min(clear, Math.hypot(p[0] - c[0], p[1] - c[1]) - r); });
    return cacheOpt[key] = {X, clear};
  }
  window.MOTION.three('path-rubber-band-3d', {
    en: 'A cable pulled tight past two posts: smoothness straightens it, the obstacle push keeps it off the posts',
    ko: '두 기둥 옆으로 팽팽히 당긴 줄입니다. 부드러움은 곧게 펴고 장애물의 밀어내는 힘은 기둥에서 떼어 놓습니다',
    cap: ['Top view of the lesson setup: 22 waypoints (0, 0) to (10, 0), radius-1 posts at (3.5, 0.3) and (7, -0.5), margin 0.4 m, 4000 gradient steps at rate 0.04 on smoothness plus wo times squared margin violation. At the lesson wo = 8 the closest approach is 0.388 m outside; at wo = 0 the cable passes through the posts.',
      '위에서 본 lesson 설정입니다. waypoint 22개가 (0, 0)에서 (10, 0)까지 이어지고 반지름 1인 기둥이 (3.5, 0.3)과 (7, -0.5)에 있으며 margin은 0.4 m입니다. 부드러움 비용과 wo 곱하기 margin 침범 제곱을 gradient descent로 4000번 줄입니다. wo = 8에서 기둥 바깥 0.388 m까지 접근하고 wo = 0이면 기둥을 관통합니다.'],
    period: 12, rest: 0, unit: 42, look: [5, 0, 0], oy: 10,
    cam: {yaw: .1, pitch: .95, dist: 9},
    controls: [{id: 'wo', en: 'obstacle push wo', ko: '장애물 밀어내는 힘 wo', min: 0, max: 12, step: .25, dec: 2, auto: t => 6 + 6 * Math.cos(2 * PI * t / 12)}],
  }, (s, t, m) => {
    const o = optimise(s.v.wo), inside = o.clear < 0, color = inside ? '--bad' : '--ok';
    s.line([0, 0, .01], [10, 0, .01], '--mut', 1.5, {dash: [5, 4]});
    OBS.forEach(([c, r]) => {
      post(s, c, r, .45, '--pd', 18);
      s.path(circ(c, r + MARGIN, .02, 28), '--pl', 1.6, {dash: [4, 3]});
    });
    s.path(o.X.map(p => [p[0], p[1], .12]), color, 3.4, {front: true});
    o.X.forEach(p => s.dot([p[0], p[1], .12], color, 3, {front: true}));
    s.dot([0, 0, .12], '--fg', 6, {ring: true, front: true}); s.dot([10, 0, .12], '--fg', 6, {ring: true, front: true});
    s.text(14, 24, `wo = ${s.v.wo.toFixed(2)}`, '--fg', 15);
    s.text(14, 44, m.t(`closest approach ${o.clear.toFixed(3)} m ${inside ? 'inside a post' : 'outside'}`, `가장 가까운 거리 ${o.clear.toFixed(3)} m, 기둥 ${inside ? '안쪽' : '바깥'}`), color, 15);
  });

  // 09/05 grid search
  const FLOOR = ['..................', '..S...............', '..................', '......#########...', '......#.......#...', '......#..###..#...', '......#..#G#..#...', '......#.......#...', '..#####.......#...', '..................'];
  const GW = FLOOR[0].length, GH = FLOOR.length, walls = [], cacheG = {};
  let S0, G0;
  FLOOR.forEach((r, i) => [...r].forEach((c, j) => { if (c === '#') walls.push([i, j]); if (c === 'S') S0 = [i, j]; if (c === 'G') G0 = [i, j]; }));
  const isWall = (i, j) => FLOOR[i][j] === '#';
  function search(w) {
    const key = Math.round(w * 4); if (cacheG[key]) return cacheG[key];
    const man = (a, b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]), id = c => c[0] * GW + c[1];
    const g = {[id(S0)]: 0}, par = {[id(S0)]: null}, closed = new Set(), exp = [], heap = [[w * man(S0, G0), 0, S0]];
    while (heap.length) {
      heap.sort((a, b) => a[0] - b[0] || a[1] - b[1] || id(a[2]) - id(b[2]));
      const c = heap.shift()[2]; if (closed.has(id(c))) continue; closed.add(id(c)); exp.push(c);
      if (c[0] === G0[0] && c[1] === G0[1]) { const path = []; let q = c; while (q) { path.push(q); q = par[id(q)]; } return cacheG[key] = {path: path.reverse(), exp}; }
      for (const d of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const n = [c[0] + d[0], c[1] + d[1]];
        if (n[0] >= 0 && n[0] < GH && n[1] >= 0 && n[1] < GW && !isWall(n[0], n[1]) && g[id(c)] + 1 < (g[id(n)] != null ? g[id(n)] : 1e9)) { g[id(n)] = g[id(c)] + 1; par[id(n)] = c; heap.push([g[id(n)] + w * man(n, G0), -g[id(n)], n]); }
      }
    }
    return cacheG[key] = {path: [S0], exp};
  }
  const cell = (i, j, z) => [j - GW / 2 + .5, GH / 2 - i - .5, z];
  window.MOTION.three('warehouse-astar-3d', {
    en: 'A floor robot plans through a warehouse; blue tiles are the cells the search opened',
    ko: '창고 바닥에서 로봇이 경로를 찾습니다. 파란 칸은 탐색이 열어 본 칸입니다',
    cap: ['Lesson search: 4-connected, unit cost, f = g + w x Manhattan distance. w = 0 is Dijkstra, 1 is A*, above 1 overestimates and can return a longer path. The floor is a hand-made 18 by 10 map, not the lesson random 40 by 40 grid, so counts differ. Darker tiles were opened later.',
      'Lesson의 탐색입니다. 4방향, 칸당 비용 1, f = g + w 곱하기 Manhattan 거리입니다. w = 0이 Dijkstra, 1이 A*, 1보다 크면 과대 추정이라 더 긴 경로가 나올 수 있습니다. 바닥은 18 곱하기 10 수제 지도라서 칸 수가 lesson의 무작위 격자와 다릅니다. 진한 칸일수록 늦게 열렸습니다.'],
    period: 16, rest: 0, H: 340, unit: 15, look: [0, 0, 0], oy: 30,
    cam: {yaw: .15, pitch: .85, dist: 9},
    controls: [{id: 'w', en: 'heuristic weight w', ko: 'heuristic 가중치 w', min: 0, max: 6, step: .25, dec: 2, auto: t => 3 - 3 * Math.cos(2 * PI * t / 16)}],
  }, (s, t, m) => {
    const r = search(s.v.w), best = search(1), n = r.exp.length, cost = r.path.length - 1, longer = cost > best.path.length - 1;
    s.poly([cell(-.5, -.5, -.02), cell(-.5, GW - .5, -.02), cell(GH - .5, GW - .5, -.02), cell(GH - .5, -.5, -.02)], '--card', {a: 1, edge: '--pd', w: 2});
    r.exp.forEach((c, k) => { const q = [[-.5, -.5], [-.5, .5], [.5, .5], [.5, -.5]].map(d => cell(c[0] + d[0], c[1] + d[1], 0));
      s.poly(q, '--pf', {a: .12 + .5 * k / Math.max(1, n - 1), edge: '--card', w: .8}); });
    walls.forEach(([i, j]) => s.box(cell(i, j, .22), [.48, .48, .22], I3, '--pd'));
    s.path(r.path.map(c => cell(c[0], c[1], .08)), longer ? '--bad' : '--ok', 3.4, {front: true});
    s.box(cell(S0[0], S0[1], .1), [.35, .35, .1], I3, '--pl'); s.box(cell(G0[0], G0[1], .1), [.35, .35, .1], I3, '--ok');
    s.label(cell(G0[0], G0[1], .5), 'G', '--fg', 15, 'center');
    s.text(14, 24, `w = ${s.v.w.toFixed(2)} ${s.v.w === 0 ? 'Dijkstra' : s.v.w === 1 ? 'A*' : s.v.w > 1 ? m.t('overestimates', '과대 추정') : ''}`, '--fg', 15);
    s.text(14, 44, m.t(`cells opened ${n} (Dijkstra opens ${search(0).exp.length})`, `연 칸 ${n} (Dijkstra는 ${search(0).exp.length})`), '--mut', 15);
    s.text(14, 64, `${m.t('path cost', '경로 비용')} ${cost}${longer ? ` (${m.t('best', '최적')} ${best.path.length - 1})` : ''}`, longer ? '--bad' : '--ok', 15);
  });
})();
