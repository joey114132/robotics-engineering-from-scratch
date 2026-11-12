// Phase 04: gearbox의 shaft와 encoder disc로 감속 및 quantisation을 보여 준다.
(() => {
  const R = window.M3D, PI = Math.PI, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  // 04/01 main.py: kt=.05, resistance=1, voltage=24; use half no-load speed.
  const KT = .05, RESISTANCE = 1, VOLTAGE = 24, JR = 2e-5, JL = 2e-3;
  const WM = VOLTAGE / KT / 2, TM = KT * (VOLTAGE - KT * WM) / RESISTANCE;
  const gear = N => ({ tau: N * TM, omega: WM / N, reflected: JL / (N * N),
    rotorOutput: JR * N * N, sensitivity: (JR + JL / (N * N)) / JR });
  const ring = (x, radius) => Array.from({ length: 49 }, (_, i) => {
    const a = i * 2 * PI / 48;
    return [x, radius * Math.cos(a), radius * Math.sin(a)];
  });
  const inputRing = ring(-1.05, .32), outputRing = ring(1.05, .32);
  window.MOTION.three('gearbox-shafts-3d', {
    en: 'An ideal gearbox changes shaft speed, torque and reflected inertia',
    ko: '이상적인 gearbox가 shaft speed와 torque, reflected inertia를 바꿉니다',
    cap: ['At half no-load speed the lesson motor gives 0.6 Nm at 240 rad/s. An ideal ratio N gives N times the torque and 1/N the speed. Load inertia at the motor is Jload/N²; rotor inertia at the output is Jrotor N². Fixed motor/load labels sit below the shafts, above the inertia readout. Shaft motion plays 20 times slower; the housing is schematic.',
      '레슨 motor는 no-load speed의 절반에서 0.6 Nm와 240 rad/s를 냅니다. 이상적인 감속비 N은 torque를 N배로 늘리고 speed를 1/N로 줄입니다. Motor 쪽 load inertia는 Jload/N²이며 output 쪽 rotor inertia는 Jrotor N²입니다. Motor와 load 라벨은 shaft 아래, inertia 수치 위에 고정합니다. Shaft는 20배 느리게 재생하며 housing은 개념도입니다.'],
    period: 12, rest: 5, H: 340, unit: 110, look: [0, 0, 0], oy: 0,
    cam: { yaw: .3, pitch: .55, dist: 8 }, model: gear,
    controls: [{ id: 'N', en: 'gear ratio N', ko: '감속비 N', min: 1, max: 100, step: 1, val: 10 }],
  }, (s, t, m) => {
    const N = s.v.N, a = gear(N), phase = WM * t / 20;
    s.box([0, 0, 0], [.42, .3, .36], I, '--mut', { a: .35 });
    s.line([-1.5, 0, 0], [-.42, 0, 0], '--pf', 9);
    s.line([.42, 0, 0], [1.5, 0, 0], '--ok', 9);
    s.path(inputRing, '--pf', 3); s.path(outputRing, '--ok', 3);
    for (const [x, angle, color] of [[-1.05, phase, '--pf'], [1.05, phase / N, '--ok']]) {
      const tip = [x, .32 * Math.cos(angle), .32 * Math.sin(angle)];
      s.line([x, 0, 0], tip, color, 4); s.dot(tip, color, 6, { ring: true });
    }
    s.text(14, 24, `τ out = ${a.tau.toFixed(1)} Nm`, '--ok', 16);
    s.text(14, 46, `ω out = ${a.omega.toFixed(1)} rad/s`, '--ok', 16);
    s.text(14, 68, `J load / N² = ${a.reflected.toExponential(2)} kg m²`, '--fg', 15);
    // Reserve a fixed label row below the complete shaft/ring sweep, then the readout.
    s.text(110, 283, 'motor', '--pf', 16, 'center');
    s.text(370, 283, 'load', '--ok', 16, 'center');
    s.text(14, 310, `J rotor N² = ${a.rotorOutput.toExponential(2)} kg m²`, '--mut', 15);
  });

  // 04/03 counts() floors, including negative angles; no rounding to the nearest tick.
  const encoder = (theta, cpr) => {
    const count = Math.floor(theta / (2 * PI) * cpr);
    return { count, measured: count * 2 * PI / cpr, step: 2 * PI / cpr };
  };
  const rim = ring(0, 1), face = rim.slice(0, -1);
  let tickCPR = 0, ticks = [];
  function tickGeometry(cpr) {
    if (tickCPR !== cpr) {
      tickCPR = cpr;
      ticks = Array.from({ length: cpr }, (_, i) => {
        const a = i * 2 * PI / cpr, c = Math.cos(a), n = Math.sin(a);
        return [[0, .89 * c, .89 * n], [0, c, n]];
      });
    }
    return ticks;
  }
  window.MOTION.three('encoder-disc-3d', {
    en: 'An encoder disc turns continuously while its reported angle moves in counts',
    ko: 'Encoder disc는 연속으로 돌고 보고된 각도는 count 단위로 바뀝니다',
    cap: ['The cyan pointer is the true angle; the orange pointer is count × 2π/CPR. The lesson uses floor(theta × CPR/2π), so the measurement stays at the previous tick until the next edge. CPR here is adjustable teaching geometry and already includes all quadrature edges.',
      '하늘색 바늘은 true angle이고 주황색 바늘은 count × 2π/CPR입니다. 레슨은 floor(theta × CPR/2π)를 쓰므로 다음 edge를 지날 때까지 측정값이 이전 tick에 머뭅니다. CPR은 교육용으로 조절하며 quadrature edge를 모두 포함합니다.'],
    period: 12, rest: 4.3, H: 340, unit: 100, oy: 42,
    cam: { yaw: 1.1, pitch: .35, dist: 7 }, model: encoder,
    controls: [{ id: 'cpr', en: 'counts / revolution', ko: '회전당 count', min: 4, max: 64, step: 1, val: 16 },
      { id: 'theta', en: 'true angle', ko: '실제 각도', min: 0, max: 360, step: .1, dec: 1, unit: '°', auto: t => 360 * Math.min(1, Math.max(0, (t - 1) / 10)) }],
  }, (s, t, m) => {
    const theta = s.v.theta * PI / 180, a = encoder(theta, s.v.cpr);
    s.poly(face, '--mut', { a: .15 }); s.path(rim, '--fg', 2);
    for (const tick of tickGeometry(s.v.cpr)) s.line(tick[0], tick[1], '--mut', 2);
    s.line([-.35, 0, 0], [.35, 0, 0], '--mut', 7);
    const trueTip = [-.025, Math.cos(theta), Math.sin(theta)];
    const measuredTip = [-.05, .8 * Math.cos(a.measured), .8 * Math.sin(a.measured)];
    s.arrow([-.025, 0, 0], trueTip, '--pf', 4);
    s.arrow([-.05, 0, 0], measuredTip, '--bad', 3);
    s.dot(trueTip, '--pf', 6, { ring: true });
    s.text(14, 24, m.t(`true ${s.v.theta.toFixed(1)}°`, `실제 ${s.v.theta.toFixed(1)}°`), '--pf', 16);
    s.text(14, 46, m.t(`measured ${(a.measured * 180 / PI).toFixed(1)}°`, `측정 ${(a.measured * 180 / PI).toFixed(1)}°`), '--bad', 16);
    s.text(14, 68, `count ${a.count} / ${s.v.cpr}`, '--fg', 15);
    s.text(14, 303, `Δθ = ${(a.step * 180 / PI).toFixed(2)}°`, '--mut', 15);
  });
})();

// 04단계 3D (wave 1): torque mode와 position mode의 처짐, 제어 loop의 latency budget.
(() => {
  const R = window.M3D, PI = Math.PI, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const keep = (cache, key, make) => { if (cache[key]) return cache[key]; if (cache.n > 16) { for (const k in cache) delete cache[k]; cache.n = 0; } cache.n = (cache.n || 0) + 1; return cache[key] = make(); };

  // ---- 04/02 main.py run(): J = 0.1, b = 0.05, push 2 Nm from t = 0.5 s, q_des = 0, torque mode K and D = 1.4 sqrt(K J); position mode kp_in = 400, kd_in = 40; admittance q_cmd = q_des + ext/K; dt = 0.1 ms.
  const J4 = .1, B4 = .05, KIN = 400, DIN = 40, PUSH = 2, runs = {}, MODES = ['torque', 'position', 'admittance'];
  const modeRun = K => keep(runs, K, () => MODES.map(mode => {
    const D = 1.4 * Math.sqrt(K * J4), dt = 1e-4, n = 30000, out = new Float32Array(3001); let q = 0, qd = 0;
    for (let k = 0; k < n; k++) {
      const ext = k * dt >= .5 ? PUSH : 0, tau = mode === 'torque' ? K * -q - D * qd : mode === 'position' ? KIN * -q - DIN * qd : KIN * (ext / K - q) - DIN * qd;
      qd += dt * (tau - B4 * qd + ext) / J4; q += dt * qd;
      if ((k + 1) % 10 === 0) out[(k + 1) / 10] = q;
    }
    return out;
  }));
  window.MOTION.three('torque-position-push-3d', {
    en: 'Three identical joints are pushed with the same steady torque. The torque-mode joint gives way by its set stiffness, the position-mode joint hardly moves, and the admittance joint gives way on purpose',
    ko: '똑같은 joint 세 개를 같은 크기의 일정한 torque로 밉니다. Torque mode joint는 정한 강성만큼 밀리고, position mode joint는 거의 안 움직이며, admittance joint는 일부러 밀려납니다',
    cap: ['Joint inertia J = 0.1 kg m², friction 0.05, a 2 Nm push from t = 0.5 s, and the three modes of run(): torque mode (outer K(q_des − q) − D q̇, D = 1.4√(KJ)), position mode (the drive\'s own PD, kp = 400, kd = 40, so K does not matter) and admittance (that same drive, but the target is moved by the measured push divided by K). Levers start pointing up the screen and the dotted line is the target. The number under each lever is the felt stiffness, the push divided by the final deflection. K = 20, 5 and 60 Nm/rad play in turn; 100 µs steps.',
      'Joint inertia J = 0.1 kg m², 마찰 0.05, t = 0.5 s부터 2 Nm로 밀고, run()의 세 mode를 씁니다. Torque mode(바깥 K(q_des − q) − D q̇, D = 1.4√(KJ)), position mode(drive 자체의 PD, kp = 400, kd = 40이라 K는 상관없음), admittance(같은 drive이지만 측정한 힘을 K로 나눈 만큼 목표를 옮김)입니다. 레버는 화면 위쪽을 향해 시작하며 점선이 목표입니다. 각 레버 아래 숫자는 체감 강성으로 미는 힘을 최종 처짐으로 나눈 값입니다. K = 20, 5, 60 Nm/rad를 차례로 보여 주며 step은 100 µs입니다.'],
    period: 12, rest: 3.9, H: 330, unit: 105, look: [0, .4, 0], oy: 30,
    cam: {yaw: .12, pitch: 1.05, dist: 7},
    controls: [{id: 'K', en: 'torque-mode stiffness K', ko: 'torque mode 강성 K', min: 5, max: 100, step: 5, unit: ' Nm/rad', val: 20, auto: t => t < 4 ? 20 : t < 8 ? 5 : 60}],
  }, (s, t, m) => {
    const out = modeRun(Math.round(s.v.K)), i = Math.min(3000, Math.floor((t % 4) * 1000)), LEN = .8;
    s.poly([[-2.2, -.3, -.03], [2.2, -.3, -.03], [2.2, 1.1, -.03], [-2.2, 1.1, -.03]], '--mut', {a: .1, edge: '--mut'});
    MODES.forEach((name, k) => {
      const x = -1.25 + 1.25 * k, q = out[k][i], base = [x, 0, 0], tip = [x - LEN * Math.sin(q), LEN * Math.cos(q), .01], c = ['--pf', '--ok', '--acc'][k];
      s.line(base, [x, LEN, .005], '--mut', 1.5, {dash: [4, 4]});
      s.box([x, 0, 0], [.07, .07, .04], I, '--pd');
      s.box([(x + tip[0]) / 2, tip[1] / 2, .01], [LEN / 2, .03, .02], R.rz(PI / 2 + q), c);
      s.dot(base, '--fg', 5, {ring: true, front: true}); s.dot(tip, c, 6, {ring: true, front: true});
      if (t % 4 >= .5) s.arrow([tip[0] + .3, tip[1], .02], [tip[0] + .04, tip[1], .02], '--bad', 3, {front: true});
      const felt = PUSH / out[k][3000];
      s.label([x, -.15, 0], `${m.t(name, ['torque mode', 'position mode', 'admittance'][k])}`, c, 14, 'center');
      s.label([x, -.15, 0], `${felt.toFixed(0)} Nm/rad`, '--mut', 13, 'center', 0, 17);
    });
    s.text(14, 24, `K = ${Math.round(s.v.K)} Nm/rad,  t = ${(t % 4).toFixed(2)} s`, '--fg', 15);
    s.text(14, 44, `q = ${out.map(o => o[i].toFixed(3)).join(' | ')} rad`, '--fg', 14);
  });

  // ---- 04/04 main.py: J = 0.05, kp = 100; stages 0.5 + 2 + 1 + 0.5 + 1 ms and a hold of period/2 = 0.5 ms (total 5.5 ms); delay margin = PM / wc.
  const JL = .05, KP = 100, STAGES = [['sensor', .5], ['filter', 2], ['bus', 1], ['compute', .5], ['drive', 1], ['hold', .5]], SC = .2, X0 = -1.5, lat = {};
  const wcOf = kd => Math.sqrt((kd * kd + Math.sqrt(kd ** 4 + 4 * JL * JL * KP * KP)) / (2 * JL * JL));
  const latRun = (kd, delayMs) => keep(lat, Math.round(kd * 10) + '|' + Math.round(delayMs * 10), () => {
    const dt = 1e-4, n = 50000, lag = Math.round(delayMs / 1000 / dt), q = new Float64Array(n + 1), qd = new Float64Array(n + 1), out = new Float32Array(1001); q[0] = .1; let bad = false;
    for (let k = 0; k < n; k++) {
      const j = Math.max(k - lag, 0);
      qd[k + 1] = qd[k] + dt * (-KP * q[j] - kd * qd[j]) / JL; q[k + 1] = q[k] + dt * qd[k + 1];
      if (Math.abs(q[k + 1]) > 50) { bad = true; q.fill(Math.sign(q[k + 1]) * 50, k + 1); break; }   // diverged: hold the plot at the edge
    }
    for (let i = 0; i <= 1000; i++) out[i] = q[i * 50];
    return {q: out, bad};
  });
  window.MOTION.three('latency-budget-bars-3d', {
    en: 'Each stage of a control loop adds delay, and the phase margin of the damping loop can only pay for so much. Past that, the joint starts to shake and grows',
    ko: '제어 loop의 각 단계가 지연을 더하고, 감쇠 loop의 phase margin은 정해진 만큼의 지연만 감당합니다. 그 이상이면 joint가 떨기 시작해 점점 커집니다',
    cap: ['The five stages and the half-period hold are the lesson budget: sensor 0.5, filter 2, bus 1, compute 0.5, drive 1 and hold 0.5 ms, 5.5 ms in total (the lesson says these are made-up numbers). The green bar is the delay margin PM/ωc of the PD loop with J = 0.05 kg m² and kp = 100; the red block is extra delay you add. Right: the response from 0.1 rad over 5 s with the loop delayed that long. The lever shows the response angle drawn 6 times larger than real. At kd = 8 the margin is 9.3 ms; 5.5 ms settles and 11.5 ms (the slider maximum) grows.',
      '다섯 단계와 반 주기 hold는 레슨의 budget으로 sensor 0.5, filter 2, bus 1, compute 0.5, drive 1, hold 0.5 ms이며 합이 5.5 ms입니다(레슨이 지어낸 숫자라고 밝힙니다). 초록 막대는 J = 0.05 kg m², kp = 100인 PD loop의 delay margin PM/ωc이고 빨간 칸은 더하는 추가 지연입니다. 오른쪽은 loop가 그만큼 지연될 때 0.1 rad에서 5초 동안의 응답입니다. 레버는 응답 각도를 실제의 6배로 그렸습니다. kd = 8이면 margin이 9.3 ms이고 5.5 ms는 가라앉으며 slider 최대인 11.5 ms는 커집니다.'],
    period: 18, rest: 5.5, H: 340, unit: 100, look: [0, 0, 0], oy: 20,
    cam: {yaw: .1, pitch: .12, dist: 7},
    controls: [
      {id: 'kd', en: 'derivative gain kd', ko: 'derivative gain kd', min: 1, max: 40, step: .5, dec: 1, unit: ' Nm s/rad', val: 8},
      {id: 'extra', en: 'extra delay', ko: '추가 지연', min: 0, max: 6, step: .5, dec: 1, unit: ' ms', val: 0, auto: t => t < 6 ? 0 : t < 12 ? 2 : 6},
    ],
  }, (s, t, m) => {
    const kd = s.v.kd, extra = s.v.extra, total = 5.5 + extra, wc = wcOf(kd), pm = Math.atan(kd * wc / KP), dm = pm / wc * 1000, res = latRun(kd, total);
    let x = X0;
    STAGES.forEach(([name, ms], k) => { s.box([x + ms * SC / 2, 0, .85], [ms * SC / 2 - .01, .06, .09], I, k === 5 ? '--pd' : '--pl'); x += ms * SC; });
    if (extra > 0) s.box([x + extra * SC / 2, 0, .85], [extra * SC / 2 - .01, .06, .09], I, '--bad');
    s.line([X0, 0, .7], [X0 + total * SC, 0, .7], '--fg', 2);
    s.box([X0 + Math.min(dm, 14.5) * SC / 2, 0, .5], [Math.min(dm, 14.5) * SC / 2, .06, .05], I, total > dm ? '--bad' : '--ok', {a: .85});
    s.line([X0 + total * SC, 0, .38], [X0 + total * SC, 0, .62], total > dm ? '--bad' : '--fg', 3);
    const px = k => -.4 + 1.8 * k / 1000, pz = v => -.55 + clamp(v, -.25, .25) / .25 * .34;
    s.line([px(0), 0, pz(0)], [px(1000), 0, pz(0)], '--mut', 1.5, {dash: [4, 4]});
    const i = Math.min(1000, Math.floor(t % 6 / 5 * 1000)), pts = []; for (let k = 0; k <= i; k += 10) pts.push([px(k), 0, pz(res.q[k])]);
    if (pts.length > 1) s.path(pts, total > dm ? '--bad' : '--ok', 3);
    const ang = clamp(res.q[i] * 6, -1.4, 1.4), piv = [-1.1, 0, -.55];
    s.box([piv[0] + .25 * Math.cos(ang), 0, piv[2] + .25 * Math.sin(ang)], [.25, .03, .03], R.ry(-ang), total > dm ? '--bad' : '--pf'); s.dot(piv, '--fg', 6, {ring: true, front: true});
    s.label([0, 0, 1.0], m.t('stages: sensor, filter, bus, compute, drive, hold', '단계: sensor, filter, bus, compute, drive, hold'), '--mut', 12, 'center');
    s.text(14, 24, `kd = ${kd.toFixed(1)},  ${m.t('loop delay', 'loop 지연')} = ${total.toFixed(1)} ms`, '--fg', 15);
    s.text(14, 44, `${m.t('delay margin', 'delay margin')} = ${dm.toFixed(1)} ms  (ωc = ${wc.toFixed(0)}, PM = ${(pm * 180 / PI).toFixed(0)}°)`, total > dm ? '--bad' : '--ok', 14);
    s.text(14, 64, total > dm ? m.t('delay exceeds the margin: grows', '지연이 margin을 넘음: 커짐') : m.t(`uses ${(total / dm * 100).toFixed(0)}% of the margin: settles`, `margin의 ${(total / dm * 100).toFixed(0)}% 사용: 가라앉음`), total > dm ? '--bad' : '--ok', 14);
  });
})();
