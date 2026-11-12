// Phase 12: 수업의 두 Euler integrator로 진자 pose와 energy drift를 계산한다.
(() => {
  const I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], J = .05, K = .2, Q0 = 1, DURATION = 10;
  const energy = (q, w) => .5 * J * w * w + K * (1 - Math.cos(q));
  let cachedDt, cached;
  // Build once per dt change, never integrate the entire history on each animation frame.
  function model(dt) {
    if (dt === cachedDt) return cached;
    const result = {}, e0 = energy(Q0, 0), n = Math.round(DURATION / dt);
    for (const method of ['euler', 'semi']) {
      let q = Q0, w = 0, worst = 0;
      const trace = [{ q, w, energy: e0, worst }];
      for (let i = 0; i < n; i++) {
        const acc = -K / J * Math.sin(q), oldW = w;
        w += dt * acc;
        q += dt * (method === 'euler' ? oldW : w);
        const e = energy(q, w);
        worst = Math.max(worst, Math.abs(e - e0) / e0);
        trace.push({ q, w, energy: e, worst });
      }
      result[method] = trace;
    }
    cachedDt = dt; cached = result;
    return result;
  }
  const point = (x, q) => [x + Math.sin(q), 0, 1 - Math.cos(q)];
  window.MOTION.three('timestep-pendulums-3d', {
    en: 'Two pendulums compare explicit and semi-implicit Euler as timestep grows',
    ko: '두 진자로 timestep에 따른 explicit Euler와 semi-implicit Euler의 차이를 봅니다',
    cap: ['Both start at q=1 rad, at rest, with J=0.05 kg m² and mgl=0.2 Nm from the lesson. Explicit Euler moves q with the old velocity; semi-implicit uses the updated velocity. The displayed maximum energy drift is computed up to the drawn step. Rod length is one drawing unit; it does not specify a physical length.',
      '둘 다 수업의 J=0.05 kg m²와 mgl=0.2 Nm를 쓰며 q=1 rad에서 정지 상태로 출발합니다. Explicit Euler는 이전 velocity로 q를 갱신하고 semi-implicit은 새 velocity를 씁니다. 최대 energy drift는 화면에 그린 step까지 계산합니다. Rod 길이는 그림의 단위 길이이며 실제 길이를 뜻하지 않습니다.'],
    period: 12, rest: 11, H: 390, unit: 78, look: [0, 0, .8], oy: 20,
    cam: { yaw: .1, pitch: .25, dist: 8 }, model,
    controls: [{ id: 'dt', en: 'timestep dt', ko: 'timestep dt', min: .005, max: .2, step: .005, dec: 3, unit: '\u00a0s', val: .05 },
      { id: 'T', en: 'simulation time', ko: '시뮬레이션 시간', min: 0, max: 10, step: .01, dec: 2, unit: '\u00a0s', auto: t => Math.min(10, Math.max(0, t - 1)) }],
  }, (s, t, m) => {
    const traces = model(s.v.dt), index = Math.min(traces.euler.length - 1, Math.floor((s.v.T + 1e-12) / s.v.dt));
    const e = traces.euler[index], h = traces.semi[index], e0 = energy(Q0, 0);
    s.text(14, 24, m.t(`step ${index}, t = ${(index * s.v.dt).toFixed(3)} s`, `step ${index}, t = ${(index * s.v.dt).toFixed(3)} s`), '--fg', 15);
    s.text(14, 46, `Euler: ΔE max ${(e.worst * 100).toFixed(1)}%`, '--bad', 15);
    s.text(14, 68, `Semi: ΔE max ${(h.worst * 100).toFixed(1)}%`, '--ok', 15);
    const configs = [[-1.15, e, '--bad', 'Euler'], [1.15, h, '--ok', 'Semi']];
    for (const [x, state, color, name] of configs) {
      const pivot = [x, 0, 1], tip = point(x, state.q), start = point(x, Q0);
      s.box([x, 0, 1.06], [.16, .16, .06], I, '--mut');
      s.line(pivot, start, '--mut', 2, { dash: [4, 4] });
      s.dot(start, '--mut', 5, { a: .5 });
      s.line(pivot, tip, color, 5); s.box(tip, [.09, .09, .09], I, color);
      // Fixed row below every bob corner over the full pendulum circle.
      s.text(x < 0 ? 110 : 370, 330, name, color, 16, 'center');
    }
    s.text(14, 356, `E₀ = ${e0.toFixed(4)} J`, '--mut', 15);
  });
})();
