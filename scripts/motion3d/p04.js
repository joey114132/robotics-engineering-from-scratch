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
      '수업 motor는 no-load speed의 절반에서 0.6 Nm와 240 rad/s를 냅니다. 이상적인 감속비 N은 torque를 N배로 늘리고 speed를 1/N로 줄입니다. Motor 쪽 load inertia는 Jload/N²이며 output 쪽 rotor inertia는 Jrotor N²입니다. Motor와 load 라벨은 shaft 아래, inertia 수치 위에 고정합니다. Shaft는 20배 느리게 재생하며 housing은 개념도입니다.'],
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
      '하늘색 바늘은 true angle이고 주황색 바늘은 count × 2π/CPR입니다. 수업은 floor(theta × CPR/2π)를 쓰므로 다음 edge를 지날 때까지 측정값이 이전 tick에 머뭅니다. CPR은 교육용으로 조절하며 quadrature edge를 모두 포함합니다.'],
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
