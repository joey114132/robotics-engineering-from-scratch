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
