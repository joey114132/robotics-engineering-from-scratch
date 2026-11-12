// 15단계 3D: 결함 주입, watchdog 정지 거리, 계층별 limit, fake clock 테스트를 각 레슨의 코드 그대로 관절 팔에 그린다.
(() => {
  const R = window.M3D, PI = Math.PI, clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  // one link turning in the x-z plane about the origin (angle a from +x, up positive)
  function link(s, o, len, a, c, thick) {
    const mid = [o[0] + len / 2 * Math.cos(a), o[1], o[2] + len / 2 * Math.sin(a)];
    s.box(mid, [len / 2, thick || .035, thick || .035], R.ry(-a), c);
  }
  const tip = (o, len, a) => [o[0] + len * Math.cos(a), o[1], o[2] + len * Math.sin(a)];
  const arcPts = (o, r, a0, a1, y) => Array.from({length: 25}, (_, i) => { const a = a0 + (a1 - a0) * i / 24; return [o[0] + r * Math.cos(a), o[1] + (y || 0), o[2] + r * Math.sin(a)]; });
  function pivot(s, o) { s.box([o[0], o[1], o[2] - .12], [.1, .08, .12], R.ry(0), '--pd'); s.dot(o, '--fg', 7, {ring: true, front: true}); }
  function torqueArc(s, o, tau, max, c, r) {   // curved arrow around the pivot, sweep proportional to tau
    if (Math.abs(tau) < 1e-6) return;
    const sw = clamp(tau / max, -1, 1) * PI * 1.4, pts = arcPts(o, r, PI / 2, PI / 2 + sw, -.07);
    s.path(pts, c, 3, {front: true}); s.arrow(pts[23], pts[24], c, 3, {front: true});
  }

  // ---- 15/01: five faults injected into a joint PD loop ----
  const FAULTS = ['none', 'stuck', 'dropout', 'delay', 'saturation', 'wrong_sign'], P1 = {J: .5, b: .2, kp: 40, kd: 4, tauMax: 10, qRef: 1, qLim: 2}, DT1 = 1e-3, N1 = 3000;
  function sim1(fault, delay = .1, sat = .5, tFault = .3) {   // rows of (t, q, qd, tau, reading), lesson simulate()
    const t0 = fault === 'saturation' || fault === 'wrong_sign' ? 0 : tFault, lagN = Math.round(delay / DT1);
    const lagQ = new Float64Array(lagN), lagV = new Float64Array(lagN), rows = new Float64Array(N1 * 5);
    let q = 0, qd = 0, held = null, li = 0;
    for (let i = 0; i < N1; i++) {
      const t = i * DT1, on = t >= t0; let qm = q, qdm = qd;
      if (fault === 'stuck' && on) { if (!held) held = [q, qd]; qm = held[0]; qdm = held[1]; }
      else if (fault === 'dropout' && on && t < t0 + .3) { qm = 0; qdm = 0; }
      else if (fault === 'delay') { const oq = lagQ[li], ov = lagV[li]; lagQ[li] = q; lagV[li] = qd; li = (li + 1) % lagN; if (on) { qm = oq; qdm = ov; } }
      let tau = clamp(P1.kp * (P1.qRef - qm) - P1.kd * qdm, -P1.tauMax, P1.tauMax);
      if (fault === 'saturation') tau = clamp(tau, -sat, sat);
      if (fault === 'wrong_sign') tau = -tau;
      qd += (tau - P1.b * qd) / P1.J * DT1; q += qd * DT1;
      if (Math.abs(q) >= P1.qLim) { q = Math.sign(q) * P1.qLim; qd = 0; }
      rows.set([t, q, qd, tau, qm], i * 5);
    }
    return rows;
  }
  function alarm1(rows) {   // first time a cheap check on the controller's own signals trips (lesson alarm_time)
    const w = 50, g = 100, r = i => rows[i * 5 + 4], e = i => Math.abs(P1.qRef - r(i)), tau = i => rows[i * 5 + 3], t = i => rows[i * 5];
    for (let i = g; i < N1; i++) {
      let lo = Infinity, hi = -Infinity; for (let j = i - w; j <= i; j++) { lo = Math.min(lo, r(j)); hi = Math.max(hi, r(j)); }
      if ((hi - lo === 0 && Math.abs(tau(i)) > .5) || Math.abs(r(i) - r(i - 1)) > .3 || e(i) - e(i - g) > .3 || (t(i) >= 2 && e(i) > .1)) return t(i);
    }
    return null;
  }
  function metrics1(rows) {
    let hit = -1, peak = 0; for (let i = 0; i < N1; i++) { const a = Math.abs(rows[i * 5 + 1]); peak = Math.max(peak, a); if (hit < 0 && a >= P1.qLim) hit = i; }
    return {peak, finalErr: Math.abs(rows[(N1 - 1) * 5 + 1] - P1.qRef), tLimit: hit < 0 ? null : rows[hit * 5]};
  }
  const RUNS1 = {}, runOf = f => RUNS1[f] || (RUNS1[f] = (rows => ({rows, alarm: alarm1(rows), ...metrics1(rows)}))(sim1(f)));
  window.MOTION.three('fault-joint-3d', {
    en: 'A joint arm is driven toward 1 rad by a PD loop while one of five faults corrupts what the controller sees; most faults end against the hard stop at 2 rad',
    ko: '관절 팔이 PD 제어로 1 rad를 향해 가는데 다섯 가지 결함 중 하나가 제어기가 보는 값을 망가뜨립니다. 대부분 2 rad hard stop에 부딪힙니다',
    cap: ['One joint with J = 0.5, damping 0.2, kp = 40, kd = 4 and a torque limit of 10 Nm, taken from the lesson’s P. Green line: target 1 rad. Dashed grey line: the angle the controller reads, which differs from the arm during a fault. Red blocks: hard stops at ±2 rad. The fault starts at 0.3 s (sensor faults) or at 0 s (saturation to ±0.5 Nm, wrong sign). The lamp turns red at the lesson’s alarm_time, the first time a cheap check on the controller’s own signals trips; the back wall shows q over 3 s. The picture simplifies the hard stop as the lesson does: the joint stops instantly with zero velocity. Slider 1 picks the fault (0 none, 1 stuck, 2 dropout, 3 delay, 4 saturation, 5 wrong sign).',
      '관절 하나의 값은 레슨의 P에서 가져왔습니다. J = 0.5, 감쇠 0.2, kp = 40, kd = 4, torque 한계 10 Nm입니다. 초록 선은 목표 1 rad이고 회색 점선은 제어기가 읽는 각도로 결함이 있는 동안 실제 팔과 달라집니다. 빨간 블록은 ±2 rad의 hard stop입니다. Sensor 결함은 0.3 s에, saturation(±0.5 Nm)과 wrong sign은 0 s부터 시작합니다. 램프는 레슨의 alarm_time, 즉 제어기 자신의 신호로 하는 간단한 검사가 처음 걸리는 순간에 빨갛게 변하고 뒤쪽 벽은 3초 동안의 q를 보여 줍니다. Hard stop은 레슨처럼 속도 0으로 즉시 멈추는 것으로 단순화했습니다. 첫째 슬라이더가 결함을 고릅니다(0 none, 1 stuck, 2 dropout, 3 delay, 4 saturation, 5 wrong sign).'],
    period: 12, rest: 3, H: 340, unit: 112, look: [0, 0, .1], oy: 14, cam: {yaw: -.12, pitch: .22, dist: 7},
    controls: [{id: 'f', en: 'fault 0–5 (name on the picture)', ko: '결함 0–5 (이름은 그림에)', min: 0, max: 5, step: 1, auto: t => Math.floor(t / 2) % 6},
      {id: 'time', en: 'time', ko: '시간', min: 0, max: 2.99, step: .01, dec: 2, unit: ' s', auto: t => (t % 2) * 1.5}],
  }, (s, t, m) => {
    const name = FAULTS[s.v.f], run = s.model = runOf(name), i = Math.min(N1 - 1, Math.round(s.v.time / DT1)), q = run.rows[i * 5 + 1], qm = run.rows[i * 5 + 4], tau = run.rows[i * 5 + 3];
    const O = [0, 0, 0], L = 1;
    pivot(s, O); link(s, O, L, q, Math.abs(q) >= P1.qLim - 1e-9 ? '--bad' : '--pf');
    s.line(O, tip(O, 1.05, P1.qRef), '--ok', 2, {dash: [6, 4]}); s.line(O, tip(O, 1.05, qm), '--mut', 2, {dash: [3, 4], front: true});
    [P1.qLim, -P1.qLim].forEach(a => { link(s, O, 1.1, a, '--bad', .015); s.box(tip(O, 1.1, a), [.07, .07, .07], R.ry(-a), '--bad'); });
    s.path(arcPts(O, 1.2, -P1.qLim, P1.qLim), '--line', 1.5, {a: .6});
    torqueArc(s, O, tau, P1.tauMax, name === 'wrong_sign' ? '--bad' : '--ok', .2);
    const lamp = run.alarm !== null && i * DT1 >= run.alarm; s.dot([-.9, 0, 1.0], lamp ? '--bad' : '--ok', 9, {ring: true});
    s.label([-.9, 0, 1.0], lamp ? m.t('alarm', '알람') : m.t('quiet', '조용'), lamp ? '--bad' : '--ok', 12, 'center', 0, -14);
    const X = k => -1.3 + 2.6 * k / N1, Z = v => .35 + v * .25;
    s.line([-1.3, 1.4, Z(P1.qLim)], [1.3, 1.4, Z(P1.qLim)], '--bad', 1, {dash: [3, 3]}); s.line([-1.3, 1.4, Z(1)], [1.3, 1.4, Z(1)], '--ok', 1, {dash: [3, 3]}); s.line([-1.3, 1.4, Z(-P1.qLim)], [1.3, 1.4, Z(-P1.qLim)], '--bad', 1, {dash: [3, 3]});
    s.path(Array.from({length: Math.floor(i / 25) + 1}, (_, k) => [X(k * 25), 1.4, Z(run.rows[k * 25 * 5 + 1])]), '--pf', 2);
    const tl = run.tLimit, f3 = x => x === null ? m.t('never', '없음') : x.toFixed(3) + ' s';
    s.text(14, 24, `${s.v.f}: ${name}   t = ${(i * DT1).toFixed(2)} s   q = ${q.toFixed(2)} rad`, '--fg', 15);
    s.text(14, 44, m.t(`reaches a ±2 rad stop at: ${f3(tl)}`, `±2 rad stop 도달: ${f3(tl)}`), tl === null ? '--ok' : '--bad', 15);
    s.text(14, 64, m.t(`alarm_time: ${f3(run.alarm)}`, `alarm_time: ${f3(run.alarm)}`), run.alarm === null ? '--mut' : '--ok', 15);
  });

  // ---- 15/02: a watchdog must trip early enough that timeout travel plus braking fits in the room ----
  function sim2(ramp, timeout) {   // lesson simulate(): joint at 2 rad/s, heartbeats and commands stop at 0.5 s, hard stop at 1.5 rad
    const v0 = 2, a = 8, qLim = 1.5, tLoss = .5, dt = 1e-3, hb = .01, J = .5, b = .2, kv = 20, n = 4000, hbN = Math.round(hb / dt);
    let last = 0, q = 0, v = v0, trip = null, hit = false; const log = {qLoss: null, vLoss: null, qTrip: null, vTrip: null, tStop: null}, tr = new Float64Array(n * 2);
    for (let i = 0; i < n; i++) {
      const t = i * dt;
      if (t < tLoss && i % hbN === 0) last = t;
      if (log.qLoss === null && t >= tLoss) { log.qLoss = q; log.vLoss = v; }
      if (trip === null && t - last > timeout) { trip = t; log.qTrip = q; log.vTrip = v; }
      let tau;
      if (trip === null) tau = kv * (v0 - v); else if (!ramp) tau = 0; else tau = -Math.sign(v) * Math.min(J * a, J * Math.abs(v) / dt);
      v += (tau - b * v) / J * dt; q += v * dt;
      if (q >= qLim) { q = qLim; v = 0; hit = true; }
      tr[2 * i] = q; tr[2 * i + 1] = v;
      if (trip !== null && log.tStop === null && Math.abs(v) < 1e-3) log.tStop = t;
    }
    const room = qLim - log.qLoss, vMax = log.vLoss;
    return {...log, tr, trip, hit, qFinal: q, stopDist: q - log.qTrip, stopTime: log.tStop === null ? null : log.tStop - trip, room, brake: vMax * vMax / (2 * a), maxTimeout: (room - vMax * vMax / (2 * a)) / vMax, qLim};
  }
  const cache2 = new Map();
  window.MOTION.three('watchdog-stop-3d', {
    en: 'A joint moving at 2 rad/s loses its commands; the longer the watchdog waits, the closer it runs to the hard stop before braking begins',
    ko: '2 rad/s로 움직이던 관절이 명령을 잃습니다. watchdog이 오래 기다릴수록 제동을 시작하기 전에 hard stop에 더 가까이 갑니다',
    cap: ['A joint at 2 rad/s loses its heartbeat at 0.5 s (yellow tick, 1.0 rad). The watchdog trips after the timeout (orange tick), then the joint ramps down at a = 8 rad/s² or, with the ramp switched off, only friction slows it. The hard stop is at 1.5 rad, so the room after the loss is 0.5 rad. Braking alone needs v²/(2a) = 0.25 rad, so the longest timeout is (0.5 − 0.25) / 2 = 0.125 s, the lesson’s max_timeout(0.5, 2, 8). The number on the picture uses the simulated room (0.509 rad) and speed (1.99 rad/s), so it reads 0.134 s. A clearly longer timeout hits the stop even with a ramp. The pictured joint stops instantly at the hard stop with no impact model, as in the lesson. Playback runs 0 to 3 s of the simulation and repeats.',
      '2 rad/s로 가던 관절이 0.5 s에 heartbeat를 잃습니다(노란 눈금, 1.0 rad). Watchdog은 timeout이 지나면 trip하고(주황 눈금) 그 뒤 관절은 a = 8 rad/s²로 속도를 줄입니다. Ramp를 끄면 마찰만 관절을 늦춥니다. Hard stop은 1.5 rad이므로 신호를 잃은 뒤 남은 여유는 0.5 rad입니다. 제동만 해도 v²/(2a) = 0.25 rad가 필요해서 가장 긴 timeout은 (0.5 − 0.25) / 2 = 0.125 s이고 레슨의 max_timeout(0.5, 2, 8)과 같습니다. 그림의 숫자는 시뮬레이션이 낸 여유(0.509 rad)와 속도(1.99 rad/s)를 쓰므로 0.134 s로 읽힙니다. 이보다 확실히 길면 ramp가 있어도 stop에 부딪힙니다. 그림의 관절은 레슨처럼 충돌 모델 없이 hard stop에서 즉시 멈춥니다. 재생은 시뮬레이션 0~3 s를 반복합니다.'],
    period: 12, rest: 4.5, H: 340, unit: 130, look: [0, 0, .4], oy: 10, cam: {yaw: -.12, pitch: .22, dist: 7},
    controls: [{id: 'timeout', en: 'watchdog timeout', ko: 'watchdog timeout', min: .02, max: .4, step: .01, dec: 2, unit: ' s', val: .05},
      {id: 'ramp', toggle: true, en: 'ramp stop (off: only friction)', ko: 'ramp 정지 (끄면 마찰만)', val: true}],
  }, (s, t, m) => {
    const key = s.v.timeout.toFixed(2) + (s.v.ramp ? 'r' : 'c'); if (!cache2.has(key)) cache2.set(key, sim2(s.v.ramp, +s.v.timeout.toFixed(2)));
    const r = s.model = cache2.get(key), ts = (t % 6) * .5, i = Math.min(3999, Math.round(ts * 1000)), q = r.tr[2 * i], O = [0, 0, 0];
    pivot(s, O); link(s, O, 1, q, q >= r.qLim - 1e-9 ? '--bad' : '--pf');
    link(s, O, 1.1, r.qLim, '--bad', .015); s.box(tip(O, 1.1, r.qLim), [.07, .07, .07], R.ry(-r.qLim), '--bad');
    s.path(arcPts(O, 1.2, r.qLoss, r.qLim), '--bad', 4, {a: .5});
    s.path(arcPts(O, 1.2, 0, r.qLoss), '--line', 2, {a: .7});
    [[r.qLoss, '--ok', m.t('heartbeat lost', 'heartbeat 끊김')], [r.qTrip, '--bad', m.t('watchdog trips', 'watchdog trip')]].forEach(([a, c, txt], k) => { s.line(tip(O, 1.12, a), tip(O, 1.32, a), c, 3); s.label(tip(O, 1.38 + k * .13, a), txt, c, 12, 'left'); });
    if (i * 1e-3 > r.trip && Math.abs(r.tr[2 * i + 1]) < 1e-3) s.line(tip(O, 1.05, q), tip(O, 1.18, q), '--pf', 3);   // came to rest
    s.dot([-.8, 0, 1.0], i * 1e-3 < .5 ? '--ok' : '--mut', 9, {ring: true}); s.label([-.8, 0, 1.0], m.t('heartbeat', 'heartbeat'), '--mut', 12, 'center', 0, -14);
    s.dot([-.4, 0, 1.0], r.trip !== null && i * 1e-3 >= r.trip ? '--bad' : '--mut', 9, {ring: true}); s.label([-.4, 0, 1.0], m.t('tripped', 'trip'), '--mut', 12, 'center', 0, -14);
    const over = s.v.timeout > r.maxTimeout;
    s.text(14, 24, m.t(`timeout ${s.v.timeout.toFixed(2)} s; longest that still fits ${r.maxTimeout.toFixed(3)} s`, `timeout ${s.v.timeout.toFixed(2)} s; 여유 안에 드는 최대 ${r.maxTimeout.toFixed(3)} s`), over ? '--bad' : '--ok', 15);
    s.text(14, 44, m.t(`braking distance v²/(2a) = ${r.brake.toFixed(3)} rad; room = ${r.room.toFixed(3)} rad`, `제동 거리 v²/(2a) = ${r.brake.toFixed(3)} rad; 여유 = ${r.room.toFixed(3)} rad`), '--mut', 15);
    s.text(14, 64, r.hit ? m.t('hits the hard stop at 1.5 rad', '1.5 rad hard stop에 부딪힘') : m.t(`stops after ${r.stopDist.toFixed(2)} rad in ${r.stopTime.toFixed(3)} s`, `${r.stopDist.toFixed(2)} rad 뒤 ${r.stopTime.toFixed(3)} s에 정지`), r.hit ? '--bad' : '--ok', 15);
  });

  // ---- 15/03: the tightest limit in the stack wins silently ----
  const LAYERS = ['planner', 'controller', 'drive'], QS = ['pos', 'vel', 'tau'];
  const ALIGNED = {planner: {pos: 1.5, vel: 1, tau: null}, controller: {pos: 1.8, vel: 1.5, tau: 6}, drive: {pos: 2, vel: 2, tau: 8}};
  const MISMATCHED = {planner: {pos: 2.2, vel: 3, tau: null}, controller: {pos: 1.8, vel: 3, tau: 10}, drive: {pos: 2, vel: 1.5, tau: 6}};
  function mismatches(L) {   // lesson check_limits(): every neighbouring pair that both set a limit, upstream must not be looser
    const out = [];
    QS.forEach(q => { const set = LAYERS.filter(n => L[n][q] !== null).map(n => [n, L[n][q]]); for (let i = 0; i + 1 < set.length; i++) if (set[i][1] > set[i + 1][1]) out.push({q, a: set[i][0], b: set[i + 1][0]}); });
    return out;
  }
  function effective(L, q) { return LAYERS.filter(n => L[n][q] !== null).map(n => [L[n][q], n]).sort((a, b) => a[0] - b[0] || (a[1] < b[1] ? -1 : 1))[0]; }
  function sim3(L, goal = 1.4) {   // planner rate-limits a reference, controller runs PD with its own clamps, drive clamps last
    const [P, C, D] = LAYERS.map(n => L[n]), dt = 1e-3, J = .5, b = .2, kp = 60, kd = 6, N = 2500, tr = new Float64Array(N * 2);
    let q = 0, qd = 0, ref = 0, peak = 0, vmax = 0;
    for (let i = 0; i < N; i++) {
      ref += clamp(clamp(goal, -P.pos, P.pos) - ref, -P.vel * dt, P.vel * dt);
      const qr = clamp(ref, -C.pos, C.pos); let tau = clamp(kp * (qr - q) - kd * qd, -C.tau, C.tau);
      tau = clamp(tau, -D.tau, D.tau);
      if (qd >= D.vel || q >= D.pos) tau = Math.min(tau, 0);
      if (qd <= -D.vel || q <= -D.pos) tau = Math.max(tau, 0);
      qd += (tau - b * qd) / J * dt; q += qd * dt;
      peak = Math.max(peak, Math.abs(ref - q)); vmax = Math.max(vmax, Math.abs(qd)); tr[2 * i] = ref; tr[2 * i + 1] = q;
    }
    return {peak, vmax, tr};
  }
  const cache3 = new Map();
  window.MOTION.three('limit-stack-3d', {
    en: 'Three stacked layers each set a speed limit; the lowest one is the real limit, and a looser limit upstream makes the arm lag behind its own plan',
    ko: '세 계층이 각자 속도 limit을 정합니다. 가장 낮은 값이 실제 limit이고 위쪽 limit이 더 느슨하면 팔이 자기 계획보다 뒤처집니다',
    cap: ['Three columns are the speed limits of the planner, controller and drive in the lesson’s two fixtures (aligned: 1.0, 1.5, 2.0 rad/s; mismatched: 3.0, 3.0, 1.5). The slider replaces only the planner’s speed limit. The green plane is the limit the joint really feels, the minimum, and red arrows mark a neighbour pair where the upstream layer is looser (the lesson’s check_limits, counted over position, speed and torque). The arm on the right is the lesson’s joint driven to 1.4 rad: the dashed green arm is the planner’s reference, the solid arm is the joint. Peak lag is the largest gap between them over 2.5 s. At the lesson’s own settings it is 0.12 rad aligned and 0.82 rad mismatched.',
      '세 기둥은 레슨의 두 fixture에서 planner, controller, drive의 속도 limit입니다(aligned: 1.0, 1.5, 2.0 rad/s, mismatched: 3.0, 3.0, 1.5). 슬라이더는 planner의 속도 limit만 바꿉니다. 초록 평면은 관절이 실제로 느끼는 limit, 즉 최솟값이고 빨간 화살표는 위쪽 계층이 더 느슨한 이웃 쌍(레슨의 check_limits이며 위치, 속도, torque 전체에서 셉니다)을 표시합니다. 오른쪽 팔은 1.4 rad로 가는 레슨의 관절입니다. 초록 점선 팔은 planner의 기준값이고 실선 팔이 관절입니다. 최대 lag은 2.5초 동안 둘 사이의 가장 큰 간격이며 레슨의 설정에서 aligned는 0.12 rad, mismatched는 0.82 rad입니다.'],
    period: 12, rest: 9, H: 340, unit: 104, look: [-.2, 0, .5], oy: 8, cam: {yaw: -.3, pitch: .3, dist: 7},
    controls: [{id: 'mis', toggle: true, en: 'use the mismatched fixture', ko: 'mismatched fixture 사용', auto: t => t >= 6},
      {id: 'pv', en: 'planner speed limit', ko: 'planner 속도 limit', min: .5, max: 3, step: .1, dec: 1, unit: ' rad/s', auto: t => 1 + 2 * clamp(((t % 6) - 1) / 4, 0, 1)}],
  }, (s, t, m) => {
    const base = s.v.mis ? MISMATCHED : ALIGNED, L = {planner: {...base.planner, vel: +s.v.pv.toFixed(1)}, controller: base.controller, drive: base.drive};
    const key = (s.v.mis ? 'm' : 'a') + s.v.pv.toFixed(1); if (!cache3.has(key)) cache3.set(key, sim3(L));
    const r = cache3.get(key), bad = mismatches(L), eff = effective(L, 'vel'), K = .33, xs = [-1.9, -1.45, -1.0];
    s.model = {L, r, bad, eff};
    LAYERS.forEach((n, i) => { const h = L[n].vel * K; s.box([xs[i], 0, h / 2], [.15, .15, h / 2], R.ry(0), ['--pf', '--pl', '--pd'][i]); s.label([xs[i], 0, h + .05], L[n].vel.toFixed(1), '--fg', 12, 'center'); s.label([xs[i], .3, 0], n.slice(0, 4), '--mut', 11, 'center', 0, 14); });
    s.poly([[-2.1, -.3, eff[0] * K], [-.8, -.3, eff[0] * K], [-.8, .3, eff[0] * K], [-2.1, .3, eff[0] * K]], '--ok', {a: .3, edge: '--ok', w: 2});
    bad.filter(x => x.q === 'vel').forEach(x => { const a = LAYERS.indexOf(x.a), z = L[x.a].vel * K + .15; s.arrow([xs[a], -.2, z], [xs[a + 1], -.2, L[x.b].vel * K + .05], '--bad', 3, {front: true}); });
    const O = [.7, 0, .1]; pivot(s, O);
    const i = Math.min(2499, Math.round(clamp((t % 6) / 5, 0, 1) * 2499));
    link(s, O, 1.1, r.tr[2 * i], '--ok', .015); link(s, O, 1.1, r.tr[2 * i + 1], '--pf');
    s.text(14, 24, m.t(`limit mismatches (pos, vel, tau): ${bad.length}`, `limit 불일치(pos, vel, tau): ${bad.length}`), bad.length ? '--bad' : '--ok', 15);
    s.text(14, 44, m.t(`real speed limit ${eff[0].toFixed(1)} rad/s, owned by ${eff[1]}`, `실제 속도 limit ${eff[0].toFixed(1)} rad/s, 주인은 ${eff[1]}`), '--ok', 15);
    s.text(14, 64, m.t(`peak lag ${r.peak.toFixed(2)} rad; top speed ${r.vmax.toFixed(2)} rad/s`, `최대 lag ${r.peak.toFixed(2)} rad; 최고 속도 ${r.vmax.toFixed(2)} rad/s`), r.peak > .3 ? '--bad' : '--mut', 15);
  });

  // ---- 15/04: a fake clock makes the run repeatable, so a recorded trace catches a sign bug on the first sample ----
  function run4(kp, pol) {   // lesson FakeClock + MockJoint + Controller + run(): 300 ticks of 0.01 s to q_ref = 1
    let now = 0, q = 0, qd = 0, lastT = null, lastQ = null; const rows = new Float64Array(300 * 3);
    for (let i = 0; i < 300; i++) {
      now += .01; const qm = q; let tau;
      const stale = lastT !== null && now - lastT > .05;
      const prevT = lastT, prevQ = lastQ; lastT = now; lastQ = qm;
      if (stale) tau = 0; else { const dq = prevT !== null && now > prevT ? (qm - prevQ) / (now - prevT) : 0; tau = pol * clamp(kp * (1 - qm) - 4 * dq, -10, 10); }
      qd += (tau - .2 * qd) / .5 * .01; q += qd * .01; rows[3 * i] = qm; rows[3 * i + 1] = 1; rows[3 * i + 2] = tau;
    }
    return rows;
  }
  const GOLDEN = run4(40, 1), cache4 = new Map();
  window.MOTION.three('sign-bug-replay-3d', {
    en: 'A controller run on a fake clock gives the same trace every time, so replaying the recorded trace shows a wrong-sign bug on the very first sample',
    ko: 'fake clock으로 돌린 제어기는 매번 같은 trace를 만들어서, 녹화한 trace를 다시 돌리면 부호 버그가 첫 sample부터 드러납니다',
    cap: ['A joint (J = 0.5, damping 0.2) with the lesson’s PD controller (kp = 40, kd = 4 by default, torque limit 10 Nm) steps to 1 rad over 300 ticks of 0.01 s on a clock that moves only when the test advances it. The dashed arm is the recorded golden run (kp = 40, correct sign); the solid arm is the current run. The back wall plots q against time. The lesson’s checks are shown as numbers: the step-direction test (after 0.3 s the joint must be closer than 0.7 rad to the target, which the wrong sign fails), the settling test (within 0.02 rad after 2 s), and the replay, which reports the first sample whose torque differs from the recording. Lowering kp from 40 breaks the replay and the settling test but not the direction test.',
      'J = 0.5, 감쇠 0.2인 관절에 레슨의 PD 제어기(기본 kp = 40, kd = 4, torque 한계 10 Nm)를 붙여 테스트가 직접 넘길 때만 움직이는 시계로 0.01 s tick 300개 동안 1 rad로 step합니다. 점선 팔은 녹화한 golden run(kp = 40, 올바른 부호)이고 실선 팔은 지금 실행입니다. 뒤쪽 벽은 시간에 따른 q입니다. 레슨의 검사는 숫자로 표시합니다. Step-direction test는 0.3 s 뒤 관절이 목표에서 0.7 rad보다 가까워야 하며 부호가 틀리면 실패하고 settling test는 2 s 뒤 0.02 rad 안에 들어와야 하며 replay는 녹화와 torque가 다른 첫 sample을 알려 줍니다. kp를 40보다 낮추면 replay와 settling test는 깨지지만 direction test는 통과합니다.'],
    period: 12, rest: 9, H: 340, unit: 118, look: [0, 0, .3], oy: 10, cam: {yaw: -.12, pitch: .22, dist: 7},
    controls: [{id: 'bug', toggle: true, en: 'sign bug (polarity = −1)', ko: '부호 버그 (polarity = −1)', auto: t => t >= 6},
      {id: 'kp', en: 'kp', ko: 'kp', min: 20, max: 60, step: 1, val: 40}],
  }, (s, t, m) => {
    const key = s.v.kp + (s.v.bug ? 'b' : 'g'); if (!cache4.has(key)) cache4.set(key, run4(s.v.kp, s.v.bug ? -1 : 1));
    const rows = cache4.get(key); let first = -1; for (let i = 0; i < 300 && first < 0; i++) if (Math.abs(rows[3 * i + 2] - GOLDEN[3 * i + 2]) > 1e-9) first = i;
    const k = Math.min(299, Math.floor((t % 6) / 6 * 300)), q = rows[3 * k], g = GOLDEN[3 * k], O = [0, 0, 0];
    const q03 = rows[3 * 30], q20 = rows[3 * 200], dirOk = Math.abs(1 - q03) < .7, setOk = Math.abs(q20 - 1) < .02;
    s.model = {rows, first, q03, q20, dirOk, setOk, k};
    pivot(s, O); link(s, O, 1, g, '--mut', .015); link(s, O, 1, q, s.v.bug ? '--bad' : '--pf'); s.line(O, tip(O, 1.05, 1), '--ok', 2, {dash: [6, 4]});
    torqueArc(s, O, rows[3 * k + 2], 10, s.v.bug ? '--bad' : '--ok', .2);
    const c = [-.9, 0, 1.0]; s.path(Array.from({length: 25}, (_, i) => [c[0] + .16 * Math.cos(2 * PI * i / 24), 0, c[2] + .16 * Math.sin(2 * PI * i / 24)]), '--fg', 2);
    const ha = PI / 2 - 2 * PI * (k * .01) / 3; s.line(c, [c[0] + .14 * Math.cos(ha), 0, c[2] + .14 * Math.sin(ha)], '--pf', 3, {front: true}); s.label(c, m.t('fake clock', 'fake clock'), '--mut', 12, 'center', 0, 30);
    const X = i => -1.3 + 2.6 * i / 299, Z = v => .15 + clamp(v, -1.2, 1.5) * .55;   // the wrong-sign run races off to −60 rad: the wall plot is clipped
    s.line([-1.3, 1.4, Z(1)], [1.3, 1.4, Z(1)], '--ok', 1, {dash: [3, 3]});
    s.path(Array.from({length: 60}, (_, j) => [X(j * 5), 1.4, Z(GOLDEN[3 * j * 5])]), '--mut', 1.5, {dash: [4, 3]});
    s.path(Array.from({length: Math.floor(k / 5) + 1}, (_, j) => [X(j * 5), 1.4, Z(rows[3 * j * 5])]), s.v.bug ? '--bad' : '--pf', 2.5);
    if (first >= 0) s.dot([X(first), 1.4, Z(rows[3 * first])], '--bad', 6, {ring: true});
    s.text(14, 24, m.t(`sample ${k}, fake clock ${(k * .01).toFixed(2)} s, q = ${q.toFixed(2)} rad`, `sample ${k}, fake clock ${(k * .01).toFixed(2)} s, q = ${q.toFixed(2)} rad`), '--fg', 14);
    s.text(14, 44, m.t(`step test (0.3 s): |1 − q| = ${Math.abs(1 - q03).toFixed(2)} ${dirOk ? 'pass' : 'FAIL'}; settle (2 s): ${setOk ? 'pass' : 'FAIL'}`, `step test (0.3 s): |1 − q| = ${Math.abs(1 - q03).toFixed(2)} ${dirOk ? '통과' : '실패'}; settle (2 s): ${setOk ? '통과' : '실패'}`), dirOk && setOk ? '--ok' : '--bad', 14);
    s.text(14, 64, first < 0 ? m.t('replay: all 300 samples match', 'replay: 300개 sample 모두 일치') : m.t(`replay: first mismatch at sample ${first}`, `replay: 첫 불일치는 sample ${first}`), first < 0 ? '--ok' : '--bad', 14);
  });
})();
