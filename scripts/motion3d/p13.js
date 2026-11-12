// Phase 13: 수업 gridworld의 Bellman sweep마다 value bar와 greedy policy를 그린다.
(() => {
  const I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  const layout = ['......G', '.##.##.', '...X...', '.#.##..', '.......'];
  const moves = [[-1, 0], [1, 0], [0, -1], [0, 1]], sideways = [[2, 3], [2, 3], [0, 1], [0, 1]];
  const gamma = .9, slip = .2, cells = [], index = new Map(), terminal = [];
  for (let r = 0; r < layout.length; r++) for (let c = 0; c < layout[r].length; c++) {
    if (layout[r][c] === '#') continue;
    index.set(`${r},${c}`, cells.length); cells.push([r, c]);
    terminal.push(layout[r][c] === 'G' || layout[r][c] === 'X');
  }
  // Precompute each action's sparse transition and entry reward, including walls and slips.
  const transitions = cells.map(([r, c], s) => moves.map((_, a) => {
    if (terminal[s]) return [[s, 1, 0]];
    return [a, ...sideways[a]].map((b, j) => {
      const dest = index.get(`${r + moves[b][0]},${c + moves[b][1]}`) ?? s;
      const [dr, dc] = cells[dest], char = layout[dr][dc];
      return [dest, j === 0 ? 1 - slip : slip / 2, char === 'G' ? 1 : char === 'X' ? -1 : 0];
    });
  }));
  function backup(V) {
    return transitions.map(actions => actions.map(edges => {
      let reward = 0, next = 0;
      for (const [dest, probability, entry] of edges) {
        reward += probability * entry; next += probability * V[dest];
      }
      return reward + gamma * next;
    }));
  }
  const history = [cells.map(() => 0)], policies = [], deltas = [0];
  for (;;) {
    const previous = history[history.length - 1], Q = backup(previous);
    const next = Q.map(actions => Math.max(...actions));
    const delta = Math.max(...next.map((v, s) => Math.abs(v - previous[s])));
    history.push(next); deltas.push(delta);
    if (delta < 1e-6) break;
  }
  for (const V of history) policies.push(backup(V).map(q => q.indexOf(Math.max(...q))));
  const sweeps = history.length - 1;
  const model = k => {
    k = Math.max(0, Math.min(sweeps, Math.floor(k)));
    return { values: history[k], policy: policies[k], delta: deltas[k], sweeps };
  };
  const origin = (r, c, z = 0) => [c - 3, 2 - r, z];
  window.MOTION.three('value-bars-3d', {
    en: 'Value iteration spreads the goal reward through a slippery gridworld',
    ko: '미끄러지는 gridworld에서 value iteration으로 goal의 보상이 퍼집니다',
    cap: ['The lesson map uses slip=0.2 and γ=0.9. Signed bar height is 0.65V(s); arrows above the bars show greedy actions for the displayed V and are drawn in front. Reward is paid on entering G (+1) or X (−1), so both terminal states have V=0. Walls block moves. Each sweep updates all states from the previous sweep.',
      '수업 지도는 slip=0.2와 γ=0.9를 씁니다. Bar 높이는 부호를 포함한 0.65V(s)이며 bar 위의 화살표는 현재 V에서의 greedy action입니다. 화살표를 앞에 그려 가려지지 않게 합니다. G(+1)나 X(−1)에 들어갈 때 보상을 받으므로 두 terminal state의 V는 0입니다. Wall은 이동을 막으며 매 sweep은 이전 sweep의 값으로 모든 state를 갱신합니다.'],
    period: 12, rest: 7, H: 400, unit: 42, look: [0, 0, .15], oy: 3,
    cam: { yaw: .3, pitch: .9, dist: 20 }, model,
    controls: [{ id: 'sweep', en: 'Bellman sweep', ko: 'Bellman sweep', min: 0, max: sweeps, step: 1,
      auto: t => Math.min(sweeps, Math.floor(Math.max(0, t - 1) * sweeps / 9)) }],
  }, (s, t, m) => {
    const k = s.v.sweep, a = model(k);
    for (let r = 0; r < 5; r++) for (let c = 0; c < 7; c++) {
      const char = layout[r][c];
      if (char === '#') { s.box(origin(r, c, .12), [.46, .46, .12], I, '--mut', { a: .45 }); continue; }
      const state = index.get(`${r},${c}`), v = a.values[state];
      s.poly([origin(r - .48, c - .48), origin(r - .48, c + .48), origin(r + .48, c + .48), origin(r + .48, c - .48)], '--line', { a: .2 });
      if (terminal[state]) {
        s.label(origin(r, c, .06), char, char === 'G' ? '--ok' : '--bad', 18, 'center');
      } else {
        const height = .65 * Math.abs(v), bar = origin(r, c, Math.sign(v) * height / 2);
        bar[1] += .15;
        if (height > 1e-8) s.box(bar, [.22, .2, height / 2], I, v >= 0 ? '--pf' : '--bad', { a: .8 });
        const [dr, dc] = moves[a.policy[state]], o = origin(r, c, Math.max(0, .65 * v) + .16);
        s.arrow([o[0] - .17 * dc, o[1] + .17 * dr, o[2]], [o[0] + .17 * dc, o[1] - .17 * dr, o[2]], '--fg', 2, { front: true });
      }
    }
    const start = index.get('4,0');
    s.text(14, 24, m.t(`sweep ${k} / ${sweeps}`, `sweep ${k} / ${sweeps}`), '--fg', 16);
    s.text(14, 46, `V(start) = ${a.values[start].toFixed(3)}`, '--pf', 16);
    s.text(14, 68, `max |ΔV| = ${a.delta.toExponential(2)}`, '--mut', 15);
  });
})();

// Phase 13 (01 02 03 04 06): imitation, drift, policy-gradient variance, safety wrapper, action chunks. Each scene ports its lesson's own code.
(() => {
  const R = window.M3D, PI = Math.PI;
  const mulberry = a => () => { a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const gauss = r => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * PI * r());
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const GOAL = [1, 0], R_OB = .3, DT = .05;
  // lesson 01/02 expert: unit pull to the goal plus a swirl around the obstacle that fades 0.35 m from its edge
  function expert(x, y) {
    const dx = GOAL[0] - x, dy = GOAL[1] - y, n = Math.hypot(dx, dy) + 1e-9, r = Math.hypot(x, y) + 1e-9;
    let ax = dx / n, ay = dy / n;
    if (r < R_OB + .35) {
      const side = x * dy - y * dx >= 0 ? 1 : -1, w = 2.5 * (1 - (r - R_OB) / .35);
      ax += w * side * -y / r + w * .6 * x / r; ay += w * side * x / r + w * .6 * y / r;
    }
    const m = Math.max(1, Math.hypot(ax, ay));
    return [ax / m, ay / m];
  }
  const starts = (rng, n) => Array.from({length: n}, () => [-1.5 + .7 * rng(), -.8 + 1.6 * rng()]);
  function knn(D, k) {   // mean action of the k (=3) nearest stored states
    return (x, y) => {
      let d0 = 1e30, d1 = 1e30, d2 = 1e30, i0 = 0, i1 = 0, i2 = 0;
      for (let i = 0; i < D.n; i++) {
        const dx = D.x[i] - x, dy = D.y[i] - y, d = dx * dx + dy * dy;
        if (d < d2) { if (d < d1) { d2 = d1; i2 = i1; if (d < d0) { d1 = d0; i1 = i0; d0 = d; i0 = i; } else { d1 = d; i1 = i; } } else { d2 = d; i2 = i; } }
      }
      return [(D.ax[i0] + D.ax[i1] + D.ax[i2]) / 3, (D.ay[i0] + D.ay[i1] + D.ay[i2]) / 3];
    };
  }
  function roll(pol, x0, y0, T, z, noise) {   // execution noise z (standard normals) is added to the commanded velocity
    const xs = [x0], ys = [y0];
    for (let i = 0; i < T; i++) {
      const a = pol(xs[i], ys[i]), nz = z ? noise : 0;
      xs.push(xs[i] + DT * (clamp(a[0], -1, 1) + nz * (z ? z[2 * i] : 0))); ys.push(ys[i] + DT * (clamp(a[1], -1, 1) + nz * (z ? z[2 * i + 1] : 0)));
    }
    return {xs, ys};
  }
  const hits = p => p.xs.some((x, i) => Math.hypot(x, p.ys[i]) < R_OB);
  const reachGoal = (p, tol) => Math.hypot(p.xs[p.xs.length - 1] - GOAL[0], p.ys[p.ys.length - 1] - GOAL[1]) < tol;
  const pts = (p, step) => p.xs.filter((_, i) => i % step === 0 || i === p.xs.length - 1).map((x, j) => { const i = Math.min(j * step, p.xs.length - 1); return [x, p.ys[i], .012]; });
  function cyl(s, cx, cy, r, h, side, top) {
    const n = 14, a = i => 2 * PI * i / n;
    for (let i = 0; i < n; i++) s.poly([[cx + r * Math.cos(a(i)), cy + r * Math.sin(a(i)), 0], [cx + r * Math.cos(a(i + 1)), cy + r * Math.sin(a(i + 1)), 0], [cx + r * Math.cos(a(i + 1)), cy + r * Math.sin(a(i + 1)), h], [cx + r * Math.cos(a(i)), cy + r * Math.sin(a(i)), h]], side, {a: 1, edge: '--card', w: 1});
    s.poly(Array.from({length: n}, (_, i) => [cx + r * Math.cos(a(i)), cy + r * Math.sin(a(i)), h]), top, {a: 1, edge: '--card', w: 1});
  }
  const floor = (s, x0, x1, y0, y1) => s.poly([[x0, y0, 0], [x1, y0, 0], [x1, y1, 0], [x0, y1, 0]], '--line', {a: .22, edge: '--line'});
  function rover(s, x, y, hx, hy, c) {   // floor robot: body, nose and heading
    const h = Math.atan2(hy, hx);
    s.box([x, y, .035], [.07, .05, .035], R.rz(h), c);
    s.dot([x + .06 * Math.cos(h), y + .06 * Math.sin(h), .05], '--card', 4, {front: true});
  }
  function scene(s, goalLabel) {
    floor(s, -1.5, 1.25, -.9, .9);
    cyl(s, 0, 0, R_OB, .12, '--pd', '--mut');
    s.path(Array.from({length: 25}, (_, i) => [GOAL[0] + .1 * Math.cos(PI * i / 12), GOAL[1] + .1 * Math.sin(PI * i / 12), .01]), '--ok', 3);
    s.label([1, 0, .02], goalLabel, '--ok', 13, 'center', 0, -14);
  }

  // ---- 13/01: how many demonstrations does 3-NN need ----
  const DEMO_STARTS = starts(mulberry(1), 30), TEST_STARTS = starts(mulberry(2), 20), cache1 = new Map();
  function build1(n) {
    if (cache1.has(n)) return cache1.get(n);
    const D = {x: [], y: [], ax: [], ay: [], n: 0}, demos = [];
    DEMO_STARTS.slice(0, n).forEach(([x0, y0]) => {
      const p = roll(expert, x0, y0, 120); demos.push(p);
      for (let i = 0; i < 120; i++) { const a = expert(p.xs[i], p.ys[i]); D.x.push(p.xs[i]); D.y.push(p.ys[i]); D.ax.push(a[0]); D.ay.push(a[1]); D.n++; }
    });
    const pol = knn(D, 3), tests = TEST_STARTS.map(([x0, y0]) => { const p = roll(pol, x0, y0, 120); p.ok = !hits(p) && reachGoal(p, .1); return p; });
    const r = {demos, tests, ok: tests.filter(p => p.ok).length};
    cache1.set(n, r); return r;
  }
  window.MOTION.three('imitation-demos-3d', {
    en: 'A floor robot learns to drive around a post by copying demonstrations; more demonstrations make its 3-nearest-neighbour copy reach the goal',
    ko: '바닥 로봇이 기둥을 돌아 가는 시연을 따라 배웁니다. 시연이 늘어날수록 3-nearest-neighbour 복사본이 목표에 닿습니다',
    cap: ['Grey lines are expert demonstrations (n of them, 120 steps each) around a post of radius 0.3 m toward the goal at (1, 0). The robot replays the mean action of the 3 nearest stored states, as fit_knn does in the lesson. Green paths reached the goal within 0.1 m without touching the post; red ones did not. The success count is over 20 fixed test starts in the lesson’s start box, so it differs from the lesson’s printed rates because the starts are drawn by a different random generator.',
      '회색 선은 expert 시연(n개, 각 120 step)이며 반지름 0.3 m 기둥을 돌아 (1, 0)의 목표로 갑니다. 로봇은 lesson의 fit_knn처럼 가장 가까운 저장 상태 3개의 평균 action을 따라 합니다. 초록 경로는 기둥을 건드리지 않고 목표 0.1 m 안에 닿은 경우이고 빨강은 실패한 경우입니다. 성공 횟수는 lesson의 시작 영역에서 고정한 test start 20개로 센 값이라 난수 생성기가 달라 lesson이 출력한 비율과는 다릅니다.'],
    period: 12, rest: 3, H: 340, unit: 128, look: [-.12, 0, 0], oy: 8, cam: {yaw: -.05, pitch: .8, dist: 7},
    controls: [{id: 'n', en: 'demonstrations n', ko: '시연 수 n', min: 1, max: 30, step: 1, auto: t => [1, 3, 10, 30][Math.floor(t / 3) % 4]}],
  }, (s, t, m) => {
    const b = s.model = build1(s.v.n);
    scene(s, m.t('goal', '목표'));
    b.demos.forEach(p => s.path(pts(p, 3), '--mut', 1, {a: .55}));
    b.tests.slice(0, 6).forEach(p => s.path(pts(p, 2), p.ok ? '--ok' : '--bad', 2.5, {front: true}));
    const p = b.tests[0], i = Math.floor(clamp((t % 6) / 5, 0, 1) * 119);
    rover(s, p.xs[i], p.ys[i], p.xs[i + 1] - p.xs[i], p.ys[i + 1] - p.ys[i], p.ok ? '--ok' : '--bad');
    s.text(14, 24, m.t(`demonstrations n = ${s.v.n} (${s.v.n * 120} state-action pairs)`, `시연 n = ${s.v.n} (${s.v.n * 120} state-action 쌍)`), '--fg', 15);
    s.text(14, 44, m.t(`3-NN success: ${b.ok} / 20 test starts`, `3-NN 성공: test start 20개 중 ${b.ok}개`), b.ok >= 18 ? '--ok' : '--bad', 15);
  });

  // ---- 13/02: execution noise pushes the clone off the data; DAgger relabels the states it visits ----
  const NOISE = .8, SEEDS = 6, N_EVAL = 12, B2 = {};
  const noiseSeq = rng => Array.from({length: 240}, () => gauss(rng));
  function init2() {
    B2.evalStarts = starts(mulberry(6), N_EVAL); B2.evalNoise = Array.from({length: N_EVAL}, (_, i) => noiseSeq(mulberry(100 + i)));
    B2.sets = Array.from({length: SEEDS}, (_, k) => {
      const rng = mulberry(5 + k), D = {x: [], y: [], ax: [], ay: [], n: 0}, add = (x, y) => { const a = expert(x, y); D.x.push(x); D.y.push(y); D.ax.push(a[0]); D.ay.push(a[1]); D.n++; };
      starts(rng, 4).forEach(([x0, y0]) => { const p = roll(expert, x0, y0, 120); for (let i = 0; i < 120; i++) add(p.xs[i], p.ys[i]); });
      return {rng, D, add, snaps: []};
    });
  }
  function snap2(S) {   // evaluate the current learner under noise on the fixed test rollouts
    const pol = knn(S.D, 3), paths = B2.evalStarts.map(([x0, y0], i) => roll(pol, x0, y0, 120, B2.evalNoise[i], NOISE));
    paths.forEach(p => { p.ok = !hits(p) && reachGoal(p, .15); });
    let gap = 0, cnt = 0;
    paths.slice(0, 4).forEach(p => { for (let i = 0; i < 120; i += 2) { let d = 1e30; for (let j = 0; j < S.D.n; j++) d = Math.min(d, (S.D.x[j] - p.xs[i]) ** 2 + (S.D.y[j] - p.ys[i]) ** 2); gap += Math.sqrt(d); cnt++; } });
    S.snaps.push({n: S.D.n, paths, ok: paths.filter(p => p.ok).length, gap: gap / cnt, points: Array.from({length: S.D.n}, (_, i) => [S.D.x[i], S.D.y[i], .006])});
  }
  function build2(r) {
    if (!B2.sets) init2();
    B2.sets.forEach(S => { for (let k = S.snaps.length; k <= r; k++) {
      if (k > 0) {   // roll out the current learner under noise, let the expert relabel every state it visits
        const pol = knn(S.D, 3);
        starts(S.rng, 5).forEach(([x0, y0]) => { const p = roll(pol, x0, y0, 120, noiseSeq(S.rng), NOISE); for (let i = 0; i < 120; i++) S.add(p.xs[i], p.ys[i]); });
      }
      snap2(S);
    } });
    if (B2.pick === undefined) { const mean = B2.sets.reduce((a, S) => a + S.snaps[0].ok, 0) / SEEDS; B2.pick = B2.sets.map((S, k) => [Math.abs(S.snaps[0].ok - mean), k]).sort((a, b) => a[0] - b[0])[0][1]; }
    const all = B2.sets.map(S => S.snaps[r]);
    return Object.assign({rate: all.reduce((a, q) => a + q.ok, 0) / (SEEDS * N_EVAL), gapMean: all.reduce((a, q) => a + q.gap, 0) / SEEDS}, all[B2.pick]);
  }
  window.MOTION.three('bc-drift-3d', {
    en: 'A cloned floor robot is nudged by execution noise away from the demonstrated states; each DAgger round adds the states it wandered into',
    ko: '행동 복제된 바닥 로봇이 실행 noise에 밀려 시연한 상태에서 벗어납니다. DAgger를 한 라운드 돌릴 때마다 헤맨 상태가 데이터에 더해집니다',
    cap: ['Grey dots are the 4 expert demonstrations (480 states); green dots are states the noisy learner visited and the expert relabelled, 5 rollouts per DAgger round. Velocity noise is 0.8 on the commanded velocity, as in the lesson. One data set is drawn, the one whose success without DAgger is closest to the 6-set average (8 of its 12 noisy test rollouts; green reached the goal within 0.15 m clear of the post, red did not). The success rate and the mean distance to the nearest stored state average 6 independent data sets, because 4 demonstrations vary a lot from set to set. The lesson prints 0.525, 0.9 and 0.933 at 0, 2 and 4 rounds; this picture’s random generator gives different numbers with the same trend.',
      '회색 점은 expert 시연 4개(상태 480개)이고 초록 점은 noise가 낀 learner가 방문해 expert가 다시 label한 상태로 DAgger 라운드마다 rollout 5개입니다. 속도 noise는 lesson처럼 명령 속도에 0.8을 더합니다. 데이터 세트 하나만 그렸고 DAgger 없을 때 성공률이 6개 평균에 가장 가까운 세트입니다(noisy test rollout 12개 중 8개, 초록은 기둥을 피해 목표 0.15 m 안에 도착, 빨강은 실패) 성공률과 가장 가까운 저장 상태까지의 평균 거리는 독립 데이터 세트 6개의 평균입니다. 시연 4개는 세트마다 편차가 크기 때문입니다. Lesson은 0, 2, 4라운드에서 0.525, 0.9, 0.933을 출력하며 이 그림은 난수 생성기가 달라 숫자는 다르고 추세는 같습니다.'],
    period: 12, rest: 9, H: 340, unit: 128, look: [-.12, 0, 0], oy: 8, cam: {yaw: -.05, pitch: .8, dist: 7},
    controls: [{id: 'r', en: 'DAgger rounds', ko: 'DAgger 라운드', min: 0, max: 4, step: 1, auto: t => Math.floor(t / 2.4) % 5}],
  }, (s, t, m) => {
    const b = s.model = build2(s.v.r);
    scene(s, m.t('goal', '목표'));
    s.points(b.points.slice(0, 480), '--mut', 1.5);
    s.points(b.points.slice(480), '--ok', 1.5);
    b.paths.slice(0, 8).forEach(p => s.path(pts(p, 2), p.ok ? '--ok' : '--bad', 2, {front: true, a: .9}));
    s.text(14, 24, m.t(`DAgger rounds = ${s.v.r}; data states = ${b.n}`, `DAgger 라운드 = ${s.v.r}; 데이터 상태 = ${b.n}`), '--fg', 15);
    s.text(14, 44, m.t(`success under noise: ${(b.rate * 100).toFixed(0)}% (6 data sets)`, `noise 아래 성공: ${(b.rate * 100).toFixed(0)}% (데이터 세트 6개)`), b.rate >= .8 ? '--ok' : '--bad', 15);
    s.text(14, 64, m.t(`mean gap to nearest data state: ${b.gapMean.toFixed(3)} m`, `가장 가까운 데이터 상태까지 평균 거리: ${b.gapMean.toFixed(3)} m`), '--mut', 15);
  });

  // ---- 13/03: the baseline shrinks the spread of the REINFORCE gradient estimate, not its centre ----
  const SIG = .5, T3 = 15, BONUS = 3, cache3 = new Map();
  function episode3(rng) {   // theta = (0, 0): a ~ N(0, sigma^2); x' = x + 0.2 a; reward BONUS - x'^2 - 0.01 a^2
    let x = -1 + 2 * rng(); const xs = [], as = [], rs = [];
    for (let i = 0; i < T3; i++) { const a = SIG * gauss(rng); xs.push(x); as.push(a); x += .2 * a; rs.push(BONUS - x * x - .01 * a * a); }
    return {xs, as, rs};
  }
  function gradW(eps, baseline) {   // w-component of the lesson's grad_estimate at theta = 0; baseline = mean return-to-go of the OTHER episodes
    const B = eps.length, G = eps.map(e => { const g = []; let c = 0; for (let i = T3 - 1; i >= 0; i--) { c += e.rs[i]; g[i] = c; } return g; });
    let g = 0;
    eps.forEach((e, i) => { for (let t = 0; t < T3; t++) { let b = 0; if (baseline) { for (let j = 0; j < B; j++) if (j !== i) b += G[j][t]; b /= B - 1; } g += e.as[t] / (SIG * SIG) * e.xs[t] * (G[i][t] - b); } });
    return g / B;
  }
  const stats = a => { const mu = a.reduce((x, y) => x + y, 0) / a.length; return {mu, sd: Math.sqrt(a.reduce((x, y) => x + (y - mu) ** 2, 0) / a.length)}; };
  function build3(B) {
    if (cache3.has(B)) return cache3.get(B);
    const rng = mulberry(30 + B), plain = [], base = [];
    for (let k = 0; k < 40; k++) { const eps = Array.from({length: B}, () => episode3(rng)); plain.push(gradW(eps, false)); base.push(gradW(eps, true)); }
    const r = {plain, base, sp: stats(plain), sb: stats(base)}; cache3.set(B, r); return r;
  }
  const FAN = (() => { const rng = mulberry(77); return Array.from({length: 8}, () => episode3(rng)); })(), GSCALE = 130;
  window.MOTION.three('baseline-spread-3d', {
    en: 'A cart on a rail is trained by sampled episodes; subtracting the average return of the other episodes tightens the spread of the gradient estimate',
    ko: '레일 위 수레를 sample한 episode로 학습시킵니다. 다른 episode들의 평균 return을 빼면 gradient 추정값의 퍼짐이 줄어듭니다',
    cap: ['Back wall: 8 sampled episodes of the lesson’s 1-D reach task at theta = (0, 0) (policy a ~ N(0, 0.5²), x′ = x + 0.2a, 15 steps, time upward); the cart replays the first one. Front: each dot is one estimate of the w-gradient from a batch of the chosen size, 40 batches per row. Top row has no baseline, bottom row subtracts the leave-one-out mean return-to-go. Both rows centre on the same value (the baseline stays unbiased); only the spread changes. The lesson’s reward includes a +3 per-step alive bonus, which is what makes the no-baseline spread large. Only the w part of the gradient is drawn.',
      '뒤쪽 벽에는 lesson의 1차원 도달 과제를 theta = (0, 0)에서 sample한 episode 8개를 그렸습니다(policy a ~ N(0, 0.5²), x′ = x + 0.2a, 15 step, 위쪽이 시간). 수레는 첫 episode를 재생합니다. 앞쪽의 점 하나는 고른 크기의 batch로 구한 w-gradient 추정값 하나이며 한 줄에 batch 40개입니다. 위 줄은 baseline이 없고 아래 줄은 나머지 episode의 평균 return-to-go를 뺍니다. 두 줄은 같은 값을 중심으로 모이고(baseline은 unbiased) 퍼짐만 달라집니다. Lesson의 reward에는 step마다 +3인 alive bonus가 들어 있고 이것이 baseline이 없을 때 퍼짐을 키웁니다. Gradient 중 w 성분만 그렸습니다.'],
    period: 12, rest: 3, H: 360, unit: 105, look: [0, .5, .35], oy: 20, cam: {yaw: -.1, pitch: .5, dist: 7},
    controls: [{id: 'B', en: 'batch size', ko: 'batch 크기', min: 2, max: 32, step: 1, auto: t => Math.round(2 + 30 * (1 + Math.cos(2 * PI * t / 12)) / 2)}],
  }, (s, t, m) => {
    const b = s.model = build3(s.v.B), wall = 2.1;
    s.box([0, wall, -.02], [1.6, .03, .02], R.ry(0), '--pd');
    FAN.forEach((e, k) => s.path(e.xs.map((x, i) => [x, wall, .06 + i * .045]), k ? '--mut' : '--pf', k ? 1 : 2.5, {a: k ? .55 : 1}));
    const e0 = FAN[0], i0 = Math.floor(clamp((t % 6) / 5, 0, 1) * (T3 - 1));
    s.box([e0.xs[i0], wall, .05], [.1, .07, .05], R.ry(0), '--pf'); s.dot([e0.xs[i0], wall, .13], '--card', 3, {front: true});
    [[b.plain, b.sp, -.2, '--bad'], [b.base, b.sb, .5, '--ok']].forEach(([arr, st, y, c]) => {
      s.box([0, y, -.01], [1.5, .1, .01], R.ry(0), '--pd');
      s.poly([[(st.mu - st.sd) / GSCALE, y - .1, .012], [(st.mu + st.sd) / GSCALE, y - .1, .012], [(st.mu + st.sd) / GSCALE, y + .1, .012], [(st.mu - st.sd) / GSCALE, y + .1, .012]], c, {a: .3});
      arr.forEach(g => s.dot([clamp(g / GSCALE, -1.45, 1.45), y, .03], c, 4));
      s.line([st.mu / GSCALE, y - .14, .03], [st.mu / GSCALE, y + .14, .03], '--fg', 2, {front: true});
    });
    s.label([-1.45, -.2, .06], m.t('no baseline', 'baseline 없음'), '--bad', 13, 'left', 0, -9); s.label([-1.45, .5, .06], m.t('baseline', 'baseline 있음'), '--ok', 13, 'left', 0, -9);
    s.text(14, 24, m.t(`batch size ${s.v.B}; 40 gradient estimates per row`, `batch 크기 ${s.v.B}; 줄마다 gradient 추정 40개`), '--fg', 15);
    s.text(14, 44, m.t(`spread (std) no baseline = ${b.sp.sd.toFixed(0)}`, `퍼짐(std) baseline 없음 = ${b.sp.sd.toFixed(0)}`), '--bad', 15);
    s.text(14, 64, m.t(`spread (std) with baseline = ${b.sb.sd.toFixed(0)}`, `퍼짐(std) baseline 있음 = ${b.sb.sd.toFixed(0)}`), '--ok', 15);
  });

  // ---- 13/04: the wrapper clips, rate-limits, holds and falls back; a bare actuator does not ----
  const DT4 = .05;
  const flaky = (t, x) => t >= 20 && t < 28 ? 8 : t === 45 ? NaN : -2 * x;   // lesson flaky_policy: flipped-sign burst and one NaN
  function run4(wrapped, maxStep) {   // lesson simulate(): Wrapper(lo=-1, hi=1, max_step, max_age=1, deadline=10); observation dropped on ticks 70-84
    let x = 1, seen = 1, lastOut = 0, lastGood = 0; const r = {x: [1], raw: [], out: [], kind: []};
    for (let t = 0; t < 140; t++) {
      const dropped = t >= 70 && t < 85; if (!dropped) seen = x;
      const raw = flaky(t, seen); let u, kind = null;
      if (wrapped) {
        let target;
        if (!dropped) { lastGood = t; if (!isFinite(raw)) { target = 0; kind = 'nonfinite'; } else { target = Math.min(1, Math.max(-1, raw)); if (target !== raw) kind = 'clip'; } }
        else if (t - lastGood > 10) { target = 0; kind = 'fallback'; } else { target = lastOut; kind = 'hold'; }
        u = Math.min(lastOut + maxStep, Math.max(lastOut - maxStep, target));
        if (u !== target && kind === null) kind = 'rate';
        lastOut = u;
      } else u = Math.min(10, Math.max(-10, isFinite(raw) ? raw : 0));   // a bare actuator saturates at +-10 and ignores NaN
      x += DT4 * u; r.x.push(x); r.raw.push(raw); r.out.push(u); r.kind.push(kind);
    }
    return r;
  }
  const cache4 = new Map();
  window.MOTION.three('wrapper-rails-3d', {
    en: 'Two carts get the same flaky learned commands; the one behind the safety wrapper stays within 1.0 while the bare one runs off the rail',
    ko: '같은 불안정한 learned 명령을 받는 수레 둘 중 안전 wrapper 뒤의 수레는 1.0 안에 머물고 맨 수레는 레일 밖으로 달려갑니다',
    cap: ['Both carts start at x = 1 and should go to 0 with the policy u = −2x. Ticks 20–27 flip it to +8, tick 45 returns NaN, and ticks 70–84 drop the observation (15 ticks, longer than the 10-tick deadline). The near cart gets the raw command (NaN becomes 0, clipped at ±10). The far cart sits behind the lesson’s Wrapper: clip to ±1, change per tick at most the slider value, hold a stale observation, fall back to 0 after the deadline. The arrow on each cart is the command it executes. Height above each rail is time (140 ticks of 0.05 s). Counts are the wrapper’s interventions so far; at the end with 0.2 they are clip 20, rate 9, nonfinite 1, hold 10, fallback 5, the lesson’s printed log.',
      '두 수레 모두 x = 1에서 출발해 policy u = −2x로 0에 가야 합니다. 20–27 tick에는 부호가 뒤집혀 +8이 되고 45 tick에는 NaN이 나오며 70–84 tick에는 관측이 끊깁니다(15 tick으로 10 tick deadline보다 깁니다). 가까운 수레는 raw 명령을 그대로 받습니다(NaN은 0, ±10에서 clip). 먼 수레는 lesson의 Wrapper 뒤에 있어서 ±1로 clip하고 tick당 변화량을 슬라이더 값 이하로 제한하며 오래된 관측은 hold하고 deadline이 지나면 0으로 fallback합니다. 수레의 화살표는 실제로 실행한 명령입니다. 각 레일 위쪽 높이는 시간입니다(0.05 s tick 140개). 개수는 wrapper가 지금까지 개입한 횟수이고 0.2로 끝까지 가면 clip 20, rate 9, nonfinite 1, hold 10, fallback 5로 lesson이 출력한 log와 같습니다.'],
    period: 12, rest: 5, H: 360, unit: 76, look: [1.1, 0, .35], oy: 22, cam: {yaw: -.05, pitch: .55, dist: 7.5},
    controls: [{id: 'step', en: 'max change per tick', ko: 'tick당 최대 변화', min: .02, max: .5, step: .01, dec: 2, val: .2},
      {id: 'tick', en: 'tick', ko: 'tick', min: 0, max: 139, step: 1, auto: t => Math.floor(clamp((t - .5) / 10, 0, 1) * 139)}],
  }, (s, t, m) => {
    const key = s.v.step.toFixed(2); if (!cache4.has(key)) cache4.set(key, {w: run4(true, +key), b: run4(false, +key)});
    const {w, b} = cache4.get(key), k = s.v.tick, cnt = {};
    for (let i = 0; i <= k; i++) if (w.kind[i]) cnt[w.kind[i]] = (cnt[w.kind[i]] || 0) + 1;
    const peak = r => Math.max(...r.x.slice(0, k + 2).map(Math.abs));
    s.model = {w, b, counts: cnt, maxW: peak(w), maxB: peak(b)};
    [[.9, w, '--ok', true], [-.9, b, '--bad', false]].forEach(([y, r, c, wrapped]) => {
      s.box([1.1, y, -.03], [2.6, .13, .03], R.ry(0), '--pd');
      s.path(r.x.slice(0, k + 2).map((x, i) => [x, y + (wrapped ? .32 : -.32), .05 + i * .004]), c, 1.5, {a: .8});
      s.box([r.x[k + 1], y, .07], [.14, .1, .07], R.ry(0), c); s.dot([r.x[k + 1], y, .17], '--card', 4, {front: true});
      const u = r.out[k]; if (Math.abs(u) > 1e-6) s.arrow([r.x[k + 1], y, .27], [r.x[k + 1] + u * .12, y, .27], c, 3, {front: true});
      if (wrapped && isFinite(r.raw[k]) && Math.abs(r.raw[k] - u) > 1e-6) s.arrow([r.x[k + 1], y, .36], [r.x[k + 1] + clamp(r.raw[k], -10, 10) * .12, y, .36], '--mut', 1.5, {dash: [3, 3]});
    });
    if (!isFinite(w.raw[k])) s.label([w.x[k + 1], .9, .4], m.t('NaN from the policy', 'policy가 NaN을 냄'), '--bad', 13, 'center');
    s.line([0, -1.3, 0], [0, 1.3, 0], '--ok', 1.5, {dash: [4, 4]});
    s.label([0, 1.3, 0], m.t('target 0', '목표 0'), '--ok', 12, 'center', 0, -4);
    s.label([-1.45, .9, .1], m.t('wrapper', 'wrapper'), '--ok', 12, 'left', 0, -9); s.label([-1.45, -.9, .1], m.t('bare', '맨 수레'), '--bad', 12, 'left', 0, -9);
    const c = n => cnt[n] || 0;
    s.text(14, 24, m.t(`tick ${k}: wrapped x = ${w.x[k + 1].toFixed(2)}, bare x = ${b.x[k + 1].toFixed(2)}`, `tick ${k}: wrapper x = ${w.x[k + 1].toFixed(2)}, 맨 수레 x = ${b.x[k + 1].toFixed(2)}`), '--fg', 14);
    s.text(14, 44, m.t(`max |x| so far: wrapped ${s.model.maxW.toFixed(2)}, bare ${s.model.maxB.toFixed(2)}`, `지금까지 최대 |x|: wrapper ${s.model.maxW.toFixed(2)}, 맨 수레 ${s.model.maxB.toFixed(2)}`), '--mut', 14);
    s.text(14, 64, `clip ${c('clip')} rate ${c('rate')} nonfinite ${c('nonfinite')} hold ${c('hold')} fallback ${c('fallback')}`, '--ok', 14);
  });

  // ---- 13/06: averaging two ways round the post hits it; sampling one chunk commits to a side ----
  const SIGMA6 = .15, SIGMA_A = .01, T6 = 40, cache6 = new Map();
  function demos6() {
    const rng = mulberry(11), P = [];
    for (let k = 0; k < 6; k++) {
      const amp = .45 + .2 * rng(), up = Array.from({length: T6 + 1}, (_, i) => { const x = -1 + 2 * i / T6, w = i === 0 || i === T6 ? 0 : .004 * gauss(rng); return [x + w, amp * (1 - x * x) + (i === 0 || i === T6 ? 0 : .004 * gauss(rng))]; });
      P.push(up, up.map(p => [p[0], -p[1]]));
    }
    return {P, A: P.map(p => p.slice(1).map((q, i) => [q[0] - p[i][0], q[1] - p[i][1]]))};
  }
  const D6 = demos6(), V6 = [], S6 = [];
  D6.P.forEach((p, d) => p.slice(0, T6).forEach((q, i) => { S6.push(q); V6.push(D6.A[d][i]); }));
  function meanPol(x, y) {   // kernel regression over every demo state (lesson mean_policy)
    let d2m = 1e30; const d2 = S6.map(q => { const d = (q[0] - x) ** 2 + (q[1] - y) ** 2; d2m = Math.min(d2m, d); return d; });
    let sx = 0, sy = 0, sw = 0; d2.forEach((d, i) => { const w = Math.exp(-(d - d2m) / (2 * SIGMA6 ** 2)); sx += w * V6[i][0]; sy += w * V6[i][1]; sw += w; });
    return [sx / sw, sy / sw];
  }
  function chunk6(x, y, H, rng, prefix) {
    const n = D6.P.length, ch = [], logw = [];
    for (let d = 0; d < n; d++) {
      let j = 0, best = 1e30; for (let i = 0; i < T6; i++) { const q = D6.P[d][i], dd = (q[0] - x) ** 2 + (q[1] - y) ** 2; if (dd < best) { best = dd; j = i; } }
      const c = Array.from({length: H}, (_, i) => D6.A[d][j + i] || [0, 0]); ch.push(c);
      let lw = -best / (2 * SIGMA6 ** 2); if (prefix) prefix.forEach((a, i) => { lw -= ((c[i][0] - a[0]) ** 2 + (c[i][1] - a[1]) ** 2) / (2 * SIGMA_A ** 2); });
      logw.push(lw);
    }
    const mx = Math.max(...logw), w = logw.map(l => Math.exp(l - mx)), tot = w.reduce((a, b) => a + b, 0); let u = rng() * tot, d = 0;
    while (d < n - 1 && u > w[d]) { u -= w[d]; d++; }
    return ch[d];
  }
  function runChunks(H, overlap, seed) {
    const rng = mulberry(seed), stride = H - overlap; let x = -1, y = 0, nw = null, old = null, t1 = 0; const path = [[x, y]];
    for (let t = 0; t < 60; t++) {
      if (t % stride === 0) { old = nw; nw = chunk6(x, y, H, rng, old === null ? null : nw.slice(stride)); t1 = t; }
      const k = t - t1, w = old !== null && k < overlap ? (k + 1) / (overlap + 1) : 1;
      const a = w < 1 ? [w * nw[k][0] + (1 - w) * old[k + stride][0], w * nw[k][1] + (1 - w) * old[k + stride][1]] : nw[k];
      x += a[0]; y += a[1]; path.push([x, y]);
    }
    return path;
  }
  function build6(H) {
    if (cache6.has(H)) return cache6.get(H);
    const o = Math.floor(H / 2), runs = Array.from({length: 50}, (_, i) => runChunks(H, o, i));
    const clear = p => p.every(q => Math.hypot(q[0], q[1]) >= R_OB), jit = p => { let s = 0; for (let i = 0; i + 2 < p.length; i++) s += Math.hypot(p[i + 2][0] - 2 * p[i + 1][0] + p[i][0], p[i + 2][1] - 2 * p[i + 1][1] + p[i][1]); return s / (p.length - 2); };
    const r = {H, o, runs, clear: runs.filter(clear).length / 50, jitter: runs.reduce((a, p) => a + jit(p), 0) / 50}; cache6.set(H, r); return r;
  }
  const MEAN6 = (() => { let x = -1, y = 0; const p = [[x, y]]; for (let i = 0; i < 60; i++) { const a = meanPol(x, y); x += a[0]; y += a[1]; p.push([x, y]); } return p; })();
  window.MOTION.three('action-chunk-fork-3d', {
    en: 'A floor robot has demonstrations passing left and right of a post; averaging them drives into the post, while sampling an overlapping chunk commits to one side',
    ko: '바닥 로봇은 기둥의 왼쪽과 오른쪽으로 지나간 시연을 가졌습니다. 평균을 내면 기둥에 부딪히고 겹치는 chunk를 sample하면 한쪽을 골라 끝까지 갑니다',
    cap: ['Grey curves are 12 demonstrations (6 over the post, 6 mirrored under it) from (−1, 0) to (1, 0), post radius 0.3 m. The red path is the lesson’s kernel-regression mean policy: the two sides cancel and it goes straight into the post. The coloured paths sample action chunks of length H, overlapping by H/2 as the lesson’s (8, 4) pair does, with the blend ramp of rollout_chunks. Clear rate and jitter are over 50 seeded runs per H. Jitter is the mean change of the action between steps; the lesson prints 0.0342 at H = 1 and 0.0108 at H = 8, and this picture’s random generator gives somewhat different values.',
      '회색 곡선은 (−1, 0)에서 (1, 0)으로 가는 시연 12개(기둥 위쪽 6개와 거울상 아래쪽 6개)이고 기둥 반지름은 0.3 m입니다. 빨간 경로는 lesson의 kernel-regression 평균 policy로 양쪽이 서로 상쇄되어 기둥으로 곧장 갑니다. 색이 있는 경로는 길이 H인 action chunk를 sample하며 lesson의 (8, 4) 조합처럼 H/2만큼 겹치고 rollout_chunks의 blend ramp를 씁니다. 통과율과 jitter는 H마다 seed를 고정한 50번 실행으로 구했습니다. Jitter는 step 사이 action 변화의 평균이고 lesson은 H = 1에서 0.0342, H = 8에서 0.0108을 출력합니다. 이 그림은 난수 생성기가 달라 값이 조금 다릅니다.'],
    period: 12, rest: 4, H: 340, unit: 150, look: [0, 0, 0], oy: 8, cam: {yaw: -.05, pitch: .8, dist: 7},
    controls: [{id: 'H', en: 'chunk length H (overlap H/2)', ko: 'chunk 길이 H (겹침 H/2)', min: 1, max: 16, step: 1, auto: t => Math.round(1 + 15 * (1 - Math.cos(2 * PI * t / 12)) / 2)}],
  }, (s, t, m) => {
    const b = s.model = build6(s.v.H), z = .012;
    floor(s, -1.25, 1.25, -.8, .8);
    cyl(s, 0, 0, R_OB, .12, '--pd', '--mut');
    D6.P.forEach(p => s.path(p.map(q => [q[0], q[1], z]), '--mut', 1, {a: .5}));
    s.path(MEAN6.slice(0, 45).map(q => [q[0], q[1], z]), '--bad', 3, {front: true});
    b.runs.slice(0, 5).forEach((p, i) => s.path(p.slice(0, 45).map(q => [q[0], q[1], z]), ['--pf', '--pl', '--ok', '--pf', '--pl'][i], 2, {front: true, a: .9}));
    const p = b.runs[0], i = Math.floor(clamp((t % 6) / 5, 0, 1) * 43);
    rover(s, p[i][0], p[i][1], p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1], '--pf');
    s.label([-1, 0, 0], m.t('start', '출발'), '--fg', 12, 'center', 0, 16); s.label([1, 0, 0], m.t('goal', '목표'), '--ok', 12, 'center', 0, 16);
    s.text(14, 24, m.t(`chunk length H = ${b.H}, overlap = ${b.o}`, `chunk 길이 H = ${b.H}, 겹침 = ${b.o}`), '--fg', 15);
    s.text(14, 44, m.t(`clear of the post: ${(b.clear * 100).toFixed(0)}% of 50 runs`, `기둥을 피한 실행: 50번 중 ${(b.clear * 100).toFixed(0)}%`), '--ok', 15);
    s.text(14, 64, m.t(`jitter = ${b.jitter.toFixed(4)}; mean policy: hits the post`, `jitter = ${b.jitter.toFixed(4)}; 평균 policy: 기둥에 부딪힘`), '--mut', 15);
  });
})();
