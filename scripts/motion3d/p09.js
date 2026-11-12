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
