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
