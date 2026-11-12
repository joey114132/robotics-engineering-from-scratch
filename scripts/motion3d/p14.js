// 14단계 3D: lesson의 ring consensus를 세 좌표에 각각 적용하고 보존되는 평균을 표시한다.
(() => {
  const N = 8, X0 = [4, -1, 2, 7, 0, 3, -5, 1], MEAN = X0.reduce((a, b) => a + b, 0) / N;
  // Coordinate permutations turn the lesson's scalar fixture into a spatial cloud.
  const initial = X0.map((x, i) => [x, X0[(i + 3) % N], X0[(i + 5) % N]]);
  const view = p => p.map(x => x / 5), centre = view([MEAN, MEAN, MEAN]);
  const ghost = initial.map(view);
  function consensus(gain) {
    const frames = [initial];
    for (let k = 0; k < 120; k++) {
      const prev = frames[k];
      frames.push(prev.map((p, i) => p.map((x, j) => x + gain * (prev[(i + 1) % N][j] + prev[(i + N - 1) % N][j] - 2 * x))));
    }
    return {gain, frames, draw: frames.map(f => f.map(view))};
  }
  window.MOTION.three('consensus-average-3d', {
    en: 'Eight agents in three-dimensional state space average with their ring neighbours; every coordinate converges to the unchanged initial average',
    ko: '3차원 상태 공간의 agent 여덟 개가 ring 이웃과 값을 나눕니다. 모든 좌표가 처음 평균을 유지하며 그 값으로 모입니다',
    cap: ['Apply x ← (I − εL)x independently to each coordinate on the lesson’s eight-agent ring. Initial y and z are permutations of its x values, so all three averages are 11/8 = 1.375. Faint dots show the start; the small green cross marks the fixed average. The rest frame shows partial convergence, with current agents still separate from the cross. Playback spends more time on the early updates. The gain range 0…0.25 keeps ελmax ≤ 1 for this ring (λmax=4).',
      'lesson의 여덟 agent ring에서 각 좌표에 x ← (I − εL)x를 적용합니다. 초기 y와 z는 x값의 순서만 바꿨으므로 세 좌표의 평균은 모두 11/8 = 1.375입니다. 흐린 점은 시작점이고 작은 초록색 십자는 고정된 평균입니다. 정지 화면은 수렴 중간을 보여 주므로 현재 agent 점들이 십자와 구분됩니다. 재생할 때는 초기 update를 더 천천히 보여 줍니다. Gain 범위 0…0.25에서는 이 ring의 ελmax가 1 이하입니다(λmax=4).'],
    period: 12, rest: 3, H: 400, unit: 100, look: centre, oy: 20,
    cam: {yaw: -.3, pitch: .8, dist: 8},
    controls: [{id: 'gain', en: 'coupling ε', ko: 'coupling ε', min: 0, max: .25, step: .01, dec: 2, val: .05},
      {id: 'steps', en: 'update step', ko: 'update 횟수', min: 0, max: 120, step: 1, auto: t => Math.floor(120 * Math.max(0, Math.min(1, (t - 1) / 9)) ** 2)}],
  }, (s, t, m) => {
    if (!s.cache || s.cache.gain !== s.v.gain) s.cache = consensus(s.v.gain);
    const k = s.v.steps, positions = s.cache.frames[k], dots = s.cache.draw[k];
    const spread = Math.max(...positions.map(p => Math.hypot(...p.map(x => x - MEAN))));
    s.model = {positions, mean: [MEAN, MEAN, MEAN], spread};
    ghost.forEach((p, i) => {
      s.line(p, ghost[(i + 1) % N], '--line', 1);
      s.dot(p, '--mut', 4, {a: .4});
      s.line(p, dots[i], '--mut', 1, {a: .35, dash: [3, 5]});
      s.line(dots[i], dots[(i + 1) % N], '--pf', 2);
      s.dot(dots[i], i % 2 ? '--pl' : '--pf', 7, {ring: true});
    });
    for (let axis = 0; axis < 3; axis++) {
      const a = centre.slice(), b = centre.slice(); a[axis] -= .08; b[axis] += .08;
      s.line(a, b, '--ok', 3, {front: true});
    }
    s.text(14, 24, m.t('Fixed average (each axis) = 1.375', '고정된 평균(각 축) = 1.375'), '--ok', 15);
    s.text(14, 44, m.t(`step ${k}; max distance = ${spread.toFixed(3)}`, `update ${k}회; 최대 거리 = ${spread.toFixed(3)}`), '--fg', 15);
    s.text(14, 64, m.t('Faint: start / cross: average', '흐린 점: 시작 / 십자: 평균'), '--mut', 15);
  });
})();

// Phase 14 (01 03): task allocation and traffic deadlock, drawn from each lesson's own code.
(() => {
  const R = window.M3D, PI = Math.PI, clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const pad = (s, cx, cy, h, c, o) => s.poly([[cx - h, cy - h, 0], [cx + h, cy - h, 0], [cx + h, cy + h, 0], [cx - h, cy + h, 0]], c, o);
  // ---- 14/01: greedy nearest-task assignment against the Hungarian optimum ----
  const ROBOTS = [[.636962, .269787], [.040974, .016528], [.81327, .912756], [.606636, .729497], [.543625, .935072], [.815854, .002739], [.857404, .033586], [.729655, .175656]];
  const TASKS = [[.863179, .541461], [.299712, .422687], [.02832, .124283], [.670624, .64719], [.615385, .383678], [.99721, .980835], [.685542, .650459], [.688447, .388921]];   // numpy default_rng(0), robots then tasks, as in the lesson
  const costs = n => Array.from({length: n}, (_, i) => Array.from({length: n}, (_, j) => Math.hypot(ROBOTS[i][0] - TASKS[j][0], ROBOTS[i][1] - TASKS[j][1])));
  const total = (C, a) => a.reduce((s, j, i) => s + C[i][j], 0);
  function greedy(C) {   // robots in index order, each takes the nearest free task
    const free = new Set(C.map((_, i) => i)), out = [];
    C.forEach(row => { let b = -1; free.forEach(j => { if (b < 0 || row[j] < row[b]) b = j; }); free.delete(b); out.push(b); });
    return out;
  }
  function hungarian(C) {   // O(n^3) row/column potentials, same steps as the lesson
    const n = C.length, u = Array(n + 1).fill(0), v = Array(n + 1).fill(0), p = Array(n + 1).fill(0), way = Array(n + 1).fill(0);
    for (let i = 1; i <= n; i++) {
      p[0] = i; let j0 = 0; const minv = Array(n + 1).fill(Infinity), used = Array(n + 1).fill(false);
      for (;;) {
        used[j0] = true; const i0 = p[j0]; let delta = Infinity, j1 = 0;
        for (let j = 1; j <= n; j++) if (!used[j]) {
          const cur = C[i0 - 1][j - 1] - u[i0] - v[j];
          if (cur < minv[j]) { minv[j] = cur; way[j] = j0; }
          if (minv[j] < delta) { delta = minv[j]; j1 = j; }
        }
        for (let j = 0; j <= n; j++) { if (used[j]) { u[p[j]] += delta; v[j] -= delta; } else minv[j] -= delta; }
        j0 = j1; if (p[j0] === 0) break;
      }
      while (j0) { const j1 = way[j0]; p[j0] = p[j1]; j0 = j1; }
    }
    const out = Array(n).fill(0); for (let j = 1; j <= n; j++) out[p[j] - 1] = j - 1; return out;
  }
  const SC = 2.4, W = (x, y, z) => [(x - .5) * SC, (y - .5) * SC, z || 0];
  window.MOTION.three('allocation-lines-3d', {
    en: 'Floor robots take the nearest free job one after another; the Hungarian assignment looks at every pairing and finishes with less total travel',
    ko: '바닥 로봇들이 차례로 가장 가까운 빈 일을 집습니다. Hungarian 배정은 모든 짝을 보고 총 이동 거리를 더 줄입니다',
    cap: ['Robots R0–R7 and jobs J0–J7 are the lesson’s 8 + 8 points in the unit square (numpy seed 0), cost = straight-line distance. Red lines are greedy: R0 first, each takes the nearest job still free. Green lines are the Hungarian optimum, lifted above the floor. The slider chooses how many robots and jobs take part (the first n of each); the second slider reveals the greedy picks one at a time. At n = 8 the lesson prints 2.2533 for greedy and 2.2334 for Hungarian, a small gap on this fixture. The square is drawn 2.4 times larger than the lesson’s unit. Playback shows n = 3 first, where the gap is wide, then the lesson’s n = 8.',
      'R0–R7 로봇과 J0–J7 일은 lesson의 단위 정사각형 안 8 + 8개 점(numpy seed 0)이고 cost는 직선 거리입니다. 빨간 선은 greedy로 R0부터 차례로 아직 비어 있는 가장 가까운 일을 집습니다. 초록 선은 Hungarian 최적 배정이며 바닥에서 띄워 그렸습니다. 첫 슬라이더는 참여하는 로봇과 일의 수를 고르고(각각 앞의 n개) 둘째 슬라이더는 greedy가 고르는 순서를 하나씩 보여 줍니다. n = 8일 때 lesson은 greedy 2.2533, Hungarian 2.2334를 출력하며 이 fixture에서는 차이가 작습니다. 정사각형은 lesson의 단위보다 2.4배 크게 그렸습니다. 재생은 차이가 큰 n = 3을 먼저 보여 준 뒤 lesson의 n = 8을 보여 줍니다.'],
    period: 12, rest: 11.5, H: 340, unit: 120, look: [0, 0, 0], oy: 8, cam: {yaw: -.1, pitch: .9, dist: 7},
    controls: [{id: 'n', en: 'robots and jobs n', ko: '로봇과 일의 수 n', min: 3, max: 8, step: 1, auto: t => t < 6 ? 3 : 8},
      {id: 'reveal', en: 'greedy picks shown', ko: 'greedy가 고른 수', min: 0, max: 8, step: 1, auto: t => Math.floor(clamp((t % 6) / .6, 0, 8))}],
  }, (s, t, m) => {
    const n = s.v.n, C = costs(n), g = greedy(C), h = hungarian(C), tg = total(C, g), th = total(C, h), shown = Math.min(s.v.reveal, n);
    s.model = {g, h, tg, th};
    pad(s, 0, 0, SC / 2, '--line', {a: .2, edge: '--line'});
    for (let i = 0; i < n; i++) {
      const T = W(TASKS[i][0], TASKS[i][1]);
      s.box([T[0], T[1], .06], [.07, .07, .06], R.ry(0), '--ok'); s.label([T[0], T[1], .16], 'J' + i, '--ok', 12, 'center');
      const P = W(ROBOTS[i][0], ROBOTS[i][1]);
      s.box([P[0], P[1], .04], [.1, .07, .04], R.rz(0), '--pf'); s.dot([P[0] + .08, P[1], .09], '--card', 3, {front: true}); s.label([P[0], P[1], .12], 'R' + i, '--fg', 12, 'center');
    }
    for (let i = 0; i < shown; i++) { const A = W(ROBOTS[i][0], ROBOTS[i][1], .02), B = W(TASKS[g[i]][0], TASKS[g[i]][1], .02); s.arrow(A, B, '--bad', 2, {a: .85}); }
    if (shown >= n) for (let i = 0; i < n; i++) { const A = W(ROBOTS[i][0], ROBOTS[i][1], .22), B = W(TASKS[h[i]][0], TASKS[h[i]][1], .22); s.arrow(A, B, '--ok', 3, {front: true}); }
    const gs = g.slice(0, shown).reduce((a, j, i) => a + C[i][j], 0);
    s.text(14, 24, m.t(`greedy total = ${gs.toFixed(4)}${shown < n ? ` (${shown} of ${n} picked)` : ''}`, `greedy 합계 = ${gs.toFixed(4)}${shown < n ? ` (${n}개 중 ${shown}개 선택)` : ''}`), '--bad', 15);
    s.text(14, 44, shown >= n ? m.t(`Hungarian total = ${th.toFixed(4)}`, `Hungarian 합계 = ${th.toFixed(4)}`) : m.t('Hungarian: shown after the last pick', 'Hungarian: 마지막 선택 뒤에 표시'), '--ok', 15);
    s.text(14, 64, shown >= n ? m.t(`greedy costs ${(tg - th).toFixed(4)} more`, `greedy가 ${(tg - th).toFixed(4)} 더 큼`) : '', '--mut', 15);
  });

  // ---- 14/03: four robots on a 2 x 2 grid wait on each other in a circle; reserving the whole route breaks the circle ----
  const RING = [[[0, 0], [1, 1]], [[1, 0], [1, 1]], [[1, 1], [0, 1]], [[0, 1], [0, 0]]], KEY = p => p[0] + ',' + p[1];
  function xyPath(a, b) {   // along x first, then y
    let [x, y] = a; const p = [[x, y]];
    while (x !== b[0]) { x += b[0] > x ? 1 : -1; p.push([x, y]); }
    while (y !== b[1]) { y += b[1] > y ? 1 : -1; p.push([x, y]); }
    return p;
  }
  function findCycle(g) {   // g[r] = the one robot r waits for; follow the pointers
    for (const start of Object.keys(g)) {
      const seen = []; let r = +start;
      while (r in g && !seen.includes(r)) { seen.push(r); r = g[r]; }
      if (seen.includes(r)) return seen.slice(seen.indexOf(r));
    }
    return null;
  }
  function simulate(K, policy, T) {   // lesson Sim.step(), recording a snapshot after every tick
    const paths = RING.map(j => xyPath(...j)), queue = RING.map((_, i) => i), at = new Map(), occ = new Map(), res = new Map();
    let done = 0; const snaps = [];
    const wait = () => { const g = {}; at.forEach((i, r) => { const p = paths[r]; if (i + 1 < p.length && occ.has(KEY(p[i + 1]))) g[r] = occ.get(KEY(p[i + 1])); }); return g; };
    const snap = () => { const g = wait(); snaps.push({at: new Map(at), queue: queue.slice(), res: new Map(res), done, wait: g, cycle: findCycle(g)}); };
    snap();
    for (let tick = 0; tick < T; tick++) {
      for (const r of queue.slice()) {
        const p = paths[r], need = policy === 'reserve' ? p : p.slice(0, 1);
        if (at.size < K && need.every(n => !occ.has(KEY(n)) && !res.has(KEY(n)))) {
          queue.splice(queue.indexOf(r), 1); at.set(r, 0); occ.set(KEY(p[0]), r);
          if (policy === 'reserve') p.forEach(n => res.set(KEY(n), r));
        }
      }
      const moved = new Set(); let changed = true;
      while (changed) {
        changed = false;
        for (const r of [...at.keys()]) {
          const p = paths[r], i = at.get(r); if (moved.has(r)) continue;
          if (i === p.length - 1) { occ.delete(KEY(p[i])); at.delete(r); res.delete(KEY(p[i])); done++; }
          else if (!occ.has(KEY(p[i + 1]))) { occ.delete(KEY(p[i])); res.delete(KEY(p[i])); occ.set(KEY(p[i + 1]), r); at.set(r, i + 1); }
          else continue;
          moved.add(r); changed = true;
        }
      }
      snap();
    }
    return {paths, snaps};
  }
  const cache3 = new Map(), COL = ['--pf', '--pl', '--pd', '--mut'], GP = (p, z) => [(p[0] - .5) * 2.2, (p[1] - .5) * 2.2, z || 0];
  window.MOTION.three('deadlock-grid-3d', {
    en: 'Four floor robots on a 2 by 2 grid each wait for the robot ahead and none can move; reserving a whole route before entering breaks the circle',
    ko: '2 × 2 격자 위 바닥 로봇 넷이 각자 앞 로봇을 기다려 아무도 못 움직입니다. 들어가기 전에 경로 전체를 예약하면 그 고리가 풀립니다',
    cap: ['The four jobs are the lesson’s ring: (0,0)→(1,1), (1,0)→(1,1), (1,1)→(0,1), (0,1)→(0,0), each driving x first and then y. A grid node holds one robot at a time. Red arrows point from a robot to the robot it waits for; a closed loop of them is the lesson’s find_cycle result. The first switch is the lesson’s admission policy: naive admits a robot once its start node is free, reserve admits it only when its whole route is free and then holds the route. The slider K is how many robots may be on the grid at once. A blue tint on a pad marks a reserved route node. Robots that have finished sit in the row at the right.',
      '네 작업은 lesson의 ring입니다. (0,0)→(1,1), (1,0)→(1,1), (1,1)→(0,1), (0,1)→(0,0)이고 모두 x를 먼저 간 뒤 y로 갑니다. 격자 node에는 한 번에 로봇 하나만 있을 수 있습니다. 빨간 화살표는 로봇이 기다리는 로봇을 가리키며 이 화살표가 닫힌 고리가 되면 lesson의 find_cycle 결과입니다. 첫 번째 스위치가 lesson의 admission policy입니다. naive는 출발 node가 비면 들여보내고 reserve는 경로 전체가 비어 있을 때만 들여보낸 뒤 경로를 잡아 둡니다. 슬라이더 K는 격자 위에 동시에 올라올 수 있는 로봇 수입니다. 패드의 파란 색조는 예약된 경로 node이고 일을 마친 로봇은 오른쪽 줄에 둡니다.'],
    period: 12, rest: 3, H: 340, unit: 98, look: [0, 0, 0], oy: 4, cam: {yaw: -.1, pitch: .85, dist: 7},
    controls: [{id: 'reserve', toggle: true, en: 'reserve the whole route', ko: '경로 전체를 예약', auto: t => t >= 6},
      {id: 'K', en: 'robots allowed on the grid K', ko: '격자에 올라올 수 있는 로봇 수 K', min: 1, max: 4, step: 1, val: 4}],
  }, (s, t, m) => {
    const policy = s.v.reserve ? 'reserve' : 'naive', key = policy + s.v.K;
    if (!cache3.has(key)) cache3.set(key, simulate(s.v.K, policy, 20));
    const {paths, snaps} = cache3.get(key), tick = Math.min(20, Math.floor((t % 6) / .5)), sn = snaps[tick];
    s.model = {tick, sn, snaps, policy};
    const nodes = [[0, 0], [1, 0], [1, 1], [0, 1]];
    nodes.forEach(p => { const c = GP(p), r = sn.res.has(KEY(p)); pad(s, c[0], c[1], .38, r ? '--pl' : '--line', {a: r ? .45 : .22, edge: '--line'}); });
    [[[0, 0], [1, 0]], [[1, 0], [1, 1]], [[1, 1], [0, 1]], [[0, 1], [0, 0]]].forEach(([a, b]) => s.line(GP(a, .01), GP(b, .01), '--line', 4));
    RING.forEach(([, b], r) => { const c = GP(b); s.path(Array.from({length: 17}, (_, i) => [c[0] + .14 * Math.cos(PI * i / 8), c[1] + .14 * Math.sin(PI * i / 8), .015]), COL[r], 2.5); });
    const posOf = r => { const i = sn.at.get(r); return i === undefined ? null : GP(paths[r][i]); };
    const robot = (c, r, z, hl) => { s.box([c[0], c[1], z + .07], [.16, .12, .07], R.rz(0), COL[r], hl ? {} : {a: .55}); s.label([c[0], c[1], z + .2], String(r), '--fg', 13, 'center'); };
    sn.at.forEach((_, r) => robot(posOf(r), r, 0, true));
    sn.queue.forEach((r, i) => robot([-1.75, .6 - i * .45, 0], r, 0, false));
    for (let r = 0; r < 4; r++) if (!sn.at.has(r) && !sn.queue.includes(r)) robot([1.75, -.6 + r * .45, 0], r, 0, false);
    Object.entries(sn.wait).forEach(([a, b]) => { const A = posOf(+a), B = posOf(b), v = [B[0] - A[0], B[1] - A[1]], L = Math.hypot(v[0], v[1]) || 1; s.arrow([A[0] + v[0] / L * .22, A[1] + v[1] / L * .22, .36], [B[0] - v[0] / L * .22, B[1] - v[1] / L * .22, .36], '--bad', 3, {front: true}); });
    if (sn.cycle) sn.cycle.forEach(r => { const c = posOf(r); s.dot([c[0], c[1], .42], '--bad', 5, {ring: true, front: true}); });
    s.label([-1.75, .95, 0], m.t('waiting', '대기'), '--mut', 12, 'center'); s.label([1.75, -.95, 0], m.t('done', '완료'), '--mut', 12, 'center');
    s.text(14, 24, m.t(`${policy}, K = ${s.v.K}, tick ${tick}: ${sn.done} of 4 done`, `${policy}, K = ${s.v.K}, tick ${tick}: 4개 중 ${sn.done}개 완료`), '--fg', 15);
    s.text(14, 44, sn.cycle ? m.t(`circular wait: robots ${sn.cycle.join(' → ')}`, `순환 대기: 로봇 ${sn.cycle.join(' → ')}`) : m.t('no circular wait', '순환 대기 없음'), sn.cycle ? '--bad' : '--ok', 15);
  });
})();
