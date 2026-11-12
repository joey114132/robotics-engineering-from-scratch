// 3D widgets for phase 07 (state estimation): imu-gravity-leak-3d
// A stationary robot with a gyro bias b: the tilt estimate is wrong by b t, so g sin(b t) of gravity looks like acceleration (code/main.py leaked_position, dt = 0.01 s).
(() => {
  const R = window.M3D, PI = Math.PI, G = 9.81, SC = .12, seg = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));
  const leak = (b, T) => { let v = 0, x = 0; const n = Math.round(T / .01); for (let i = 1; i <= n; i++) { v += G * Math.sin(b * i * .01) * .01; x += v * .01; } return x; };
  window.MOTION.three('imu-gravity-leak-3d', {
    en: 'A robot standing still. The gyro bias tilts its estimate of up, gravity is subtracted in the wrong direction, and the leftover looks like acceleration that carries the estimated position away',
    ko: '가만히 서 있는 로봇입니다. gyro bias 때문에 위쪽 방향의 추정이 기울고 중력이 엉뚱한 방향으로 빠져서 남은 성분이 가속도처럼 보이며 추정 위치가 멀어집니다',
    cap: ['The robot does not move (solid box). The tilt error is b t, so g sin(b t) of gravity is left over as a fake acceleration, and double integration walks the estimated position (dashed box) away. The default bias is 0.01 rad/s.',
      '로봇은 움직이지 않습니다(실선 상자). 기울기 오차는 b t이고 중력 중 g sin(b t)가 가짜 가속도로 남으며 이를 두 번 적분하면 추정 위치(점선 상자)가 멀어집니다. 기본 bias는 0.01 rad/s입니다.'],
    period: 12, rest: 11, cam: { yaw: .35, pitch: .4, dist: 7 }, unit: 140, oy: 64,
    controls: [{ id: 'T', en: 'time', ko: '시간', min: 0, max: 10, step: .1, dec: 1, unit: ' s', auto: t => 10 * seg(t, 1, 10) }, { id: 'b', en: 'gyro bias', ko: 'gyro bias', min: 0, max: .012, step: .001, dec: 3, unit: ' rad/s', val: .01 }],
  }, (s, t, m) => {
    const tilt = s.v.b * s.v.T, a = G * Math.sin(tilt), x = leak(s.v.b, s.v.T), H = [.22, .15, .09], gx = SC * 10;
    const C = p => [p[0] - gx, p[1], p[2] - .1];   // the ruler runs 0..20 m to the right of the robot; shift so the whole scene is centred
    s.line(C([-.5, 0, 0]), C([20 * SC + .3, 0, 0]), '--line', 2);
    for (let i = 0; i <= 4; i++) { s.line(C([i * 5 * SC, 0, 0]), C([i * 5 * SC, .12, 0]), '--mut', 1.5); s.label(C([i * 5 * SC, 0, 0]), i * 5 + ' m', '--mut', 15, 'center', 0, 20); }
    if (x > .05) s.line(C([0, 0, .02]), C([x * SC, 0, .02]), '--bad', 3.5);
    s.wire(C([x * SC, 0, H[2]]), H, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], '--bad', 2, { dash: [5, 4] });
    s.box(C([0, 0, H[2]]), H, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], '--pf', { a: .8 });
    const O = C([0, 0, .9]), dn = [Math.sin(tilt) * .6, 0, -Math.cos(tilt) * .6];
    s.arrow(O, R.add(O, [0, 0, -.6]), '--fg', 3, { front: true }); s.label(R.add(O, [0, 0, -.6]), m.t('true g', '실제 g'), '--fg', 15, 'center', 0, 20);
    s.arrow(O, R.add(O, dn), '--mut', 2.5, { dash: [5, 4], front: true });
    if (a > .02) { const L = [Math.sin(tilt) * 2.4, 0, 0]; s.arrow(O, R.add(O, L), '--bad', 3.5, { front: true }); s.label(R.add(O, L), m.t('leftover (drawn x4)', '남은 성분(4배로 그림)'), '--bad', 15, 'left', 8, -6); }
    s.text(14, 24, m.t(`tilt error b t = ${(tilt * 180 / PI).toFixed(1)}°`, `기울기 오차 b t = ${(tilt * 180 / PI).toFixed(1)}°`), '--fg', 15);
    s.text(14, 44, m.t(`fake acceleration g sin(b t) = ${a.toFixed(2)} m/s²`, `가짜 가속도 g sin(b t) = ${a.toFixed(2)} m/s²`), '--bad', 15);
    s.text(14, 64, m.t(`position error ${x.toFixed(1)} m`, `위치 오차 ${x.toFixed(1)} m`), '--bad', 15);
  });
})();

// 07/01 bayes-ring-3d (wave 3d): the histogram Bayes filter on the lesson's 20-cell ring corridor (DOORS, KERNEL, P_HIT; truth and readings from simulate(DOORS, 7, [1]*25, default_rng(1))).
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], N = 20, KERNEL = [.05, .9, .05], P_HIT = .9, RING = 2, STEPS = 25;
  const DOORS = [1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0];
  const TRUTH = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 1, 2, 3, 4, 5, 6, 6, 7, 8, 9, 10, 11, 12], ZS = [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1];
  const mod = i => (i % N + N) % N;
  const predict = (bel, mv) => bel.map((_, i) => KERNEL.reduce((a, p, k) => a + p * bel[mod(i - (mv + k - 1))], 0));   // np.roll(bel, move + k)[i] = bel[i - move - k]
  const update = (bel, z) => { const p = bel.map((b, i) => b * (DOORS[i] === z ? P_HIT : 1 - P_HIT)), s = p.reduce((a, b) => a + b, 0); return p.map(x => x / s); };
  const entropy = bel => -bel.reduce((a, p) => a + (p > 0 ? p * Math.log(p) : 0), 0);
  const run = useUpdate => { let b = new Array(N).fill(1 / N); const out = [b]; for (let k = 0; k < STEPS; k++) { b = predict(b, 1); if (useUpdate) b = update(b, ZS[k]); out.push(b); } return out; };
  const BEL = {1: run(true), 0: run(false)};
  const at = (i, r, z) => [r * Math.cos(2 * Math.PI * i / N), r * Math.sin(2 * Math.PI * i / N), z];
  window.MOTION.three('bayes-ring-3d', {
    en: 'A robot circles a ring corridor with doors and walls. Bars are its belief about which cell it is in; each door or wall reading sharpens them',
    ko: '문과 벽이 있는 원형 복도를 로봇이 돕니다. 막대는 로봇이 어느 칸에 있는지에 대한 belief이고 문이나 벽을 읽을 때마다 뾰족해집니다',
    cap: ['The ring has 20 cells with the lesson’s door pattern (tall orange posts are doors, low grey blocks are walls). Every step the robot moves one cell with the lesson’s motion kernel (0.05 one cell short, 0.9 exact, 0.05 one cell long) and reads door or wall with P(hit) = 0.9. Bar height is the belief of each cell; blue = the robot’s true cell. The move blurs the bars and the reading multiplies them by the likelihood and renormalises. The 25 true cells and readings are the lesson’s run with seed 1. Without the sensor the belief stays flat: a move alone teaches nothing about where you are on a symmetric ring. The ring is drawn as a flat track, not a map of a real building.',
      '고리는 레슨의 문 배치를 가진 20칸이고 주황색 기둥이 문, 낮은 회색 블록이 벽입니다. 로봇은 매 step 레슨의 motion kernel(한 칸 모자라게 0.05, 정확히 0.9, 한 칸 넘치게 0.05)로 한 칸 움직이고 P(hit) = 0.9로 문인지 벽인지 읽습니다. 막대 높이는 칸마다의 belief이고 파란색이 로봇의 실제 칸입니다. 움직이면 막대가 번지고 읽기는 likelihood를 곱한 뒤 다시 정규화합니다. 실제 칸 25개와 읽은 값은 seed 1로 돌린 레슨의 실행입니다. 센서를 끄면 belief가 평평한 채로 남습니다. 대칭인 고리에서는 움직이기만 해서는 내 위치를 알 수 없기 때문입니다. 고리는 평평한 트랙 그림이며 실제 건물의 지도가 아닙니다.'],
    period: 12, rest: 12, H: 350, unit: 56, look: [0, 0, .3], oy: 40, cam: {yaw: .2, pitch: .95, dist: 8},
    controls: [
      {id: 'k', en: 'step', ko: 'step', min: 0, max: STEPS, step: 1, auto: t => Math.min(STEPS, Math.floor(t / 11 * (STEPS + 1)))},
      {id: 'sensor', toggle: true, en: 'use door/wall readings', ko: '문/벽 읽기 사용', val: true},
    ],
  }, (s, t, m) => {
    const k = s.v.k, bel = BEL[s.v.sensor ? 1 : 0][k], H = entropy(bel), tr = k ? TRUTH[k - 1] : -1;
    let best = 0; bel.forEach((b, i) => { if (b > bel[best]) best = i; });
    s.poly(Array.from({length: 40}, (_, j) => at(j * N / 40, RING + .55, -.02)), '--line', {a: .25});
    for (let i = 0; i < N; i++) {
      const a = 2 * Math.PI * i / N, c = at(i, RING, 0), h = Math.min(2.2, bel[i] * 4);
      s.box(at(i, RING + .38, DOORS[i] ? .3 : .06), [.05, .12, DOORS[i] ? .3 : .06], R.rz(a), DOORS[i] ? '--pl' : '--mut');
      s.box(at(i, RING, Math.max(h, .01) / 2), [.09, .13, Math.max(h, .01) / 2], R.rz(a), i === tr ? '--pf' : '--pd', {a: i === tr ? 1 : .8});
    }
    if (tr >= 0) { s.box(at(tr, RING - .5, .12), [.1, .1, .1], R.rz(2 * Math.PI * tr / N), '--pf'); }
    s.dot(at(best, RING, Math.min(2.2, bel[best] * 4) + .15), '--ok', 6, {ring: true, front: true});
    s.text(14, 24, m.t(`step ${k} of ${STEPS}`, `step ${k} / ${STEPS}`), '--fg', 15);
    s.text(14, 44, k ? m.t(`reading: ${ZS[k - 1] ? 'door' : 'wall'}`, `읽은 값: ${ZS[k - 1] ? '문' : '벽'}`) : m.t('no reading yet', '아직 읽은 값 없음'), '--mut', 15);
    s.text(14, 64, m.t(`entropy ${H.toFixed(2)} nats (flat = ${Math.log(N).toFixed(2)})`, `entropy ${H.toFixed(2)} nats (평평 = ${Math.log(N).toFixed(2)})`), H < 1.6 ? '--ok' : '--bad', 15);
    s.text(466, 24, tr >= 0 && H < 2.9 ? m.t(`best guess cell ${best}, true cell ${tr}`, `가장 유력한 칸 ${best}, 실제 칸 ${tr}`) : '', best === tr ? '--ok' : '--mut', 14, 'right');
  });
})();

// 07/02 kalman-lane-3d (wave 3d): the lesson's constant-velocity Kalman filter (DT 1 s, accel noise 0.1, position noise R_STD slider, prior mean (0, 1), P0 = diag(4, 1)); noise draws are a fixed JavaScript sequence.
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]], STEPS = 60, DT = 1, SA = .1, SC = .5, DY = .1;
  const rng = seed => () => { seed = seed + 0x6D2B79F5 | 0; let x = Math.imul(seed ^ seed >>> 15, 1 | seed); x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; };
  const u = rng(5), gauss = () => Math.sqrt(-2 * Math.log(1 - u())) * Math.cos(2 * Math.PI * u());
  const Z0 = [gauss(), gauss()], ZA = [], ZM = []; for (let i = 0; i < STEPS; i++) { ZA.push(gauss()); ZM.push(gauss()); }
  // truth: x0 = X0 + chol(P0) z, then x' = F x + sa G a; reading = position + r n
  const truth = []; { let p = 0 + 2 * Z0[0], v = 1 + 1 * Z0[1]; for (let k = 0; k < STEPS; k++) { truth.push(p); if (k < STEPS - 1) { const a = SA * ZA[k]; p += v * DT + a * DT * DT / 2; v += a * DT; } } }
  function filter(r) {
    let x = [0, 1], P = [[4, 0], [0, 1]]; const out = [], q = [DT * DT / 2, DT];
    for (let k = 0; k < STEPS; k++) {
      if (k) {
        x = [x[0] + DT * x[1], x[1]];
        const A = [[P[0][0] + DT * P[1][0], P[0][1] + DT * P[1][1]], [P[1][0], P[1][1]]];   // F P
        P = [[A[0][0] + DT * A[0][1] + SA * SA * q[0] * q[0], A[0][1] + SA * SA * q[0] * q[1]], [A[1][0] + DT * A[1][1] + SA * SA * q[1] * q[0], A[1][1] + SA * SA * q[1] * q[1]]];
      }
      const z = truth[k] + r * ZM[k], S = P[0][0] + r * r, K = [P[0][0] / S, P[1][0] / S], y = z - x[0];
      x = [x[0] + K[0] * y, x[1] + K[1] * y];
      P = [[(1 - K[0]) * P[0][0], (1 - K[0]) * P[0][1]], [P[1][0] - K[1] * P[0][0], P[1][1] - K[1] * P[0][1]]];
      out.push({est: x[0], sig: Math.sqrt(P[0][0]), z});
    }
    return out;
  }
  window.MOTION.three('kalman-lane-3d', {
    en: 'A cart rolls down a rail and a noisy position sensor reads it every second. The filter’s estimate stays much closer to the cart than the raw readings, and it knows how close',
    ko: '수레가 레일을 따라 가고 잡음 있는 위치 센서가 1초마다 읽습니다. 필터의 추정은 원래 측정값보다 수레에 훨씬 가깝고 얼마나 가까운지도 스스로 압니다',
    cap: ['Seen from above, the cart’s true path is the centre line and time runs away from you (60 s). Red dots are the raw position readings’ error; the blue line is the Kalman estimate’s error; the green band is the filter’s own claim, plus and minus sqrt(P00). Model from the lesson: constant velocity, dt 1 s, acceleration noise 0.1 m/s², prior mean (0, 1) and P0 = diag(4, 1); the slider is the measurement noise std (lesson 2 m). The band comes from the lesson’s covariance recursion, which does not look at any data; the noise draws are a fixed JavaScript sequence (one run), so the estimate errors are one sample, not the lesson’s average over 2000 runs. 1 unit of width = 2 m.',
      '위에서 본 그림입니다. 수레의 실제 경로가 가운데 선이고 시간은 멀어지는 방향으로 흐릅니다(60초). 빨간 점은 원래 위치 측정값의 오차이고 파란 선은 Kalman 추정의 오차이며 초록 띠는 필터 자신의 주장, 곧 plus minus sqrt(P00)입니다. 레슨의 모델을 씁니다. 등속, dt 1 s, 가속도 noise 0.1 m/s², 사전 평균 (0, 1), P0 = diag(4, 1)이고 슬라이더는 측정 noise 표준편차입니다(레슨은 2 m). 띠는 데이터를 보지 않는 레슨의 공분산 점화식에서 나옵니다. Noise는 고정된 JavaScript 수열이라 한 번 돌린 결과이며 추정 오차는 레슨의 2000회 평균이 아니라 표본 하나입니다. 폭 1 단위 = 2 m입니다.'],
    period: 12, rest: 12, H: 380, unit: 50, look: [0, 3, 0], oy: 80, cam: {yaw: .15, pitch: .95, dist: 8},
    controls: [{id: 'r', en: 'sensor noise std', ko: '센서 noise 표준편차', min: .5, max: 5, step: .25, dec: 2, unit: ' m', val: 2}, {id: 'k', en: 'time', ko: '시간', min: 0, max: STEPS - 1, step: 1, unit: ' s', auto: t => Math.min(STEPS - 1, Math.floor(t / 11 * STEPS))}],
  }, (s, t, m) => {
    const F = filter(s.v.r), kk = s.v.k, row = (k, e) => [e * SC, k * DY, 0];
    s.poly([[-3.2, -.2, -.02], [3.2, -.2, -.02], [3.2, STEPS * DY, -.02], [-3.2, STEPS * DY, -.02]], '--line', {a: .22});
    s.line([0, -.2, 0], [0, STEPS * DY, 0], '--fg', 2);
    for (let g = -4; g <= 4; g += 2) s.line([g * SC, -.2, 0], [g * SC, STEPS * DY, 0], '--line', 1, {a: .5});
    const up = [], lo = [], est = [];
    for (let k = 0; k <= kk; k++) { const f = F[k]; up.push(row(k, f.sig)); lo.push(row(k, -f.sig)); est.push(row(k, f.est - truth[k])); }
    if (kk > 0) s.poly(up.concat(lo.slice().reverse()), '--ok', {a: .22});
    for (let k = 0; k <= kk; k++) s.dot(row(k, F[k].z - truth[k]), '--bad', 3);
    s.path(est, '--pf', 3, {front: true});
    s.box([0, kk * DY, .1], [.2, .12, .1], I, '--pd'); s.dot(est[kk], '--pf', 6, {ring: true, front: true});
    const f = F[kk];
    s.text(14, 24, m.t(`t = ${kk} s`, `t = ${kk} s`), '--fg', 15);
    s.text(14, 44, m.t(`sensor error ${(f.z - truth[kk]).toFixed(2)} m`, `센서 오차 ${(f.z - truth[kk]).toFixed(2)} m`), '--bad', 15);
    s.text(14, 64, m.t(`filter error ${(f.est - truth[kk]).toFixed(2)} m, its own claim ±${f.sig.toFixed(2)} m`, `필터 오차 ${(f.est - truth[kk]).toFixed(2)} m, 스스로 주장하는 범위 ±${f.sig.toFixed(2)} m`), '--pf', 15);
  });
})();

// 07/04 tilt-planks-3d (wave 3d): complementary filter on the lesson's still-robot tilt test (dt 0.01 s, truth 0.3 sin(1.9 t), gyro noise 0.02, accelerometer noise 0.05; bias and tau are sliders).
(() => {
  const R = window.M3D, DT = .01, N = 2000, SG = .02, SA = .05;
  const rng = seed => () => { seed = seed + 0x6D2B79F5 | 0; let x = Math.imul(seed ^ seed >>> 15, 1 | seed); x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; };
  const u = rng(3), gauss = () => Math.sqrt(-2 * Math.log(1 - u())) * Math.cos(2 * Math.PI * u());
  const GG = [], GA = [], TR = [], OM = []; for (let i = 0; i < N; i++) { GG.push(gauss()); GA.push(gauss()); TR.push(.3 * Math.sin(1.9 * DT * i)); OM.push(.3 * 1.9 * Math.cos(1.9 * DT * i)); }
  const alpha = (tau, dt) => tau / (tau + dt), best = (b, sa = SA, dt = DT) => Math.cbrt(sa * sa * dt / (4 * b * b));
  const predicted = (tau, b) => { const a = alpha(tau, DT); return Math.sqrt((tau * b) ** 2 + SA * SA * (1 - a) / (1 + a)); };
  let key = '', cache = null;
  function sim(tau, b) {
    const k = tau + ':' + b; if (k === key) return cache;
    const a = alpha(tau, DT), acc = [], gyr = [], fus = []; let g = 0, f = 0, e = [0, 0, 0];
    for (let i = 0; i < N; i++) {
      const gy = OM[i] + b + SG * GG[i], z = TR[i] + SA * GA[i];
      g += gy * DT; f = a * (f + gy * DT) + (1 - a) * z; acc.push(z); gyr.push(g); fus.push(f);
      e[0] += (z - TR[i]) ** 2; e[1] += (g - TR[i]) ** 2; e[2] += (f - TR[i]) ** 2;
    }
    key = k; return cache = {acc, gyr, fus, rmse: e.map(x => Math.sqrt(x / N))};
  }
  window.MOTION.three('tilt-planks-3d', {
    en: 'A plank is rocked back and forth. A gyro alone drifts, an accelerometer alone is jittery, and the complementary filter blends them',
    ko: '판자를 앞뒤로 흔듭니다. Gyro만 쓰면 표류하고 가속도계만 쓰면 떨리는데 상보 필터는 둘을 섞어 줍니다',
    cap: ['Three planks show the same 20 s of rocking (0.3 sin(1.9 t) rad), played in 12 s. Dashed outlines are the true tilt; solid planks are what each sensor path believes. The gyro reads the true rate plus a bias b and noise 0.02; the accelerometer reads the tilt plus noise 0.05; the fused estimate is theta = a (theta + gyro dt) + (1 − a) accel with a = tau / (tau + dt), dt = 0.01 s. The sliders are tau and the gyro bias (lesson: 0.01 rad/s, best tau = 0.40 s). The rms numbers come from this one run with a fixed JavaScript noise sequence, not the lesson’s numpy seed; the “formula” line is the lesson’s predicted_rmse for a still robot. The planks are a picture of one tilt angle, not a balancing robot.',
      '판자 세 개가 같은 20초의 흔들림(0.3 sin(1.9 t) rad)을 12초에 압축해 보여 줍니다. 점선 윤곽이 실제 기울기이고 실선 판자가 각 센서 경로가 믿는 기울기입니다. Gyro는 실제 각속도에 bias b와 noise 0.02를 더해 읽고 가속도계는 기울기에 noise 0.05를 더해 읽습니다. 합친 추정은 theta = a (theta + gyro dt) + (1 − a) accel이고 a = tau / (tau + dt), dt = 0.01 s입니다. 슬라이더는 tau와 gyro bias입니다(레슨은 0.01 rad/s, 최적 tau = 0.40 s). Rms 값은 레슨의 numpy seed가 아니라 고정된 JavaScript noise 수열로 한 번 돌린 결과이고 “formula” 줄은 가만히 선 로봇에 대한 레슨의 predicted_rmse입니다. 판자는 기울기 한 개를 그린 그림이며 균형 잡는 로봇이 아닙니다.'],
    period: 12, rest: 12, H: 300, unit: 72, look: [0, 0, .4], oy: 15, cam: {yaw: .15, pitch: .35, dist: 8},
    controls: [
      {id: 'tau', en: 'time constant tau', ko: '시간상수 tau', min: .05, max: 3, step: .05, dec: 2, unit: ' s', val: .4},
      {id: 'b', en: 'gyro bias', ko: 'gyro bias', min: .0025, max: .03, step: .0025, dec: 4, unit: ' rad/s', val: .01},
    ],
  }, (s, t, m) => {
    const M = sim(s.v.tau, s.v.b), i = Math.min(N - 1, Math.floor(Math.min(1, t / 11) * N)), I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    [[-2.3, M.acc[i], m.t('accelerometer only', '가속도계만'), '--pl'], [0, M.gyr[i], m.t('gyro only', 'gyro만'), '--bad'], [2.3, M.fus[i], m.t('fused', '합친 값'), '--ok']].forEach(([x, th, name, c]) => {
      const C = [x, 0, .45];
      s.box([x, 0, .2], [.06, .1, .2], I, '--mut');
      s.wire(C, [.9, .13, .04], R.ry(-TR[i]), '--fg', 1.5, {dash: [4, 4]});
      s.box(C, [.9, .13, .04], R.ry(-th), c);
      s.label([x, 0, 0], name, '--mut', 14, 'center', 0, 20);
    });
    const p = predicted(s.v.tau, s.v.b);
    s.text(14, 24, m.t(`rms error  accel ${M.rmse[0].toFixed(3)}  gyro ${M.rmse[1].toFixed(3)}  fused ${M.rmse[2].toFixed(3)} rad`, `rms 오차  가속도계 ${M.rmse[0].toFixed(3)}  gyro ${M.rmse[1].toFixed(3)}  합침 ${M.rmse[2].toFixed(3)} rad`), '--fg', 14);
    s.text(14, 44, m.t(`formula for a still robot: ${p.toFixed(3)} rad`, `가만히 선 로봇의 공식값: ${p.toFixed(3)} rad`), '--mut', 14);
    s.text(14, 64, m.t(`best tau for this bias: ${best(s.v.b).toFixed(2)} s`, `이 bias의 최적 tau: ${best(s.v.b).toFixed(2)} s`), Math.abs(s.v.tau - best(s.v.b)) < .1 ? '--ok' : '--mut', 14);
    s.text(466, 84, `t = ${(i * DT).toFixed(1)} s`, '--mut', 14, 'right');
  });
})();

// 07/05 ekf-circle-3d (wave 3d): the lesson's unicycle EKF with range-bearing landmarks (DT 0.1, U = (1, 0.3), landmarks LMS, R = diag(0.2², 0.03²), P0 = diag(0.3², 0.3², 0.1²)); noise draws are a fixed JavaScript sequence.
(() => {
  const R = window.M3D, PI = Math.PI, DT = .1, SV = .05, SW = .03, U = [1, .3], LMS = [[4, 1], [0, 5.5], [-4, 1], [0, -2]], RMAX = 8, STEPS = 80;
  const RN = [.2 * .2, .03 * .03], P0 = [.3, .3, .1];
  const wrap = a => ((a + PI) % (2 * PI) + 2 * PI) % (2 * PI) - PI;
  const rng = seed => { const u = () => { seed = seed + 0x6D2B79F5 | 0; let x = Math.imul(seed ^ seed >>> 15, 1 | seed); x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; }; return () => Math.sqrt(-2 * Math.log(1 - u())) * Math.cos(2 * PI * u()); };
  const mm = (A, B) => A.map(r => B[0].map((_, j) => r.reduce((a, v, k) => a + v * B[k][j], 0))), tr = A => A[0].map((_, j) => A.map(r => r[j]));
  const add = (A, B) => A.map((r, i) => r.map((v, j) => v + B[i][j]));
  const inv2 = A => { const d = A[0][0] * A[1][1] - A[0][1] * A[1][0]; return [[A[1][1] / d, -A[0][1] / d], [-A[1][0] / d, A[0][0] / d]]; };
  const inv3 = A => { const [[a, b, c], [d, e, f], [g, h, i]] = A, D = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
    return [[(e * i - f * h) / D, (c * h - b * i) / D, (b * f - c * e) / D], [(f * g - d * i) / D, (a * i - c * g) / D, (c * d - a * f) / D], [(d * h - e * g) / D, (b * g - a * h) / D, (a * e - b * d) / D]]; };
  const f = (x, u) => [x[0] + u[0] * DT * Math.cos(x[2]), x[1] + u[0] * DT * Math.sin(x[2]), wrap(x[2] + u[1] * DT)];
  const h = (x, lm) => { const dx = lm[0] - x[0], dy = lm[1] - x[1]; return [Math.hypot(dx, dy), wrap(Math.atan2(dy, dx) - x[2])]; };
  function predict(x, P, u) {
    const F = [[1, 0, -u[0] * DT * Math.sin(x[2])], [0, 1, u[0] * DT * Math.cos(x[2])], [0, 0, 1]], G = [[DT * Math.cos(x[2]), 0], [DT * Math.sin(x[2]), 0], [0, DT]];
    return [f(x, u), add(mm(mm(F, P), tr(F)), mm(mm(G, [[SV * SV, 0], [0, SW * SW]]), tr(G)))];
  }
  function update(x, P, z, lm) {
    const dx = lm[0] - x[0], dy = lm[1] - x[1], q = dx * dx + dy * dy, r = Math.sqrt(q), H = [[-dx / r, -dy / r, 0], [dy / q, -dx / q, -1]];
    const S = add(mm(mm(H, P), tr(H)), [[RN[0], 0], [0, RN[1]]]), K = mm(mm(P, tr(H)), inv2(S)), hz = h(x, lm), y = [z[0] - hz[0], wrap(z[1] - hz[1])];
    const IKH = add([[1, 0, 0], [0, 1, 0], [0, 0, 1]], mm(K, H).map(r => r.map(v => -v))), nx = x.map((v, i) => v + K[i][0] * y[0] + K[i][1] * y[1]); nx[2] = wrap(nx[2]);
    return [nx, add(mm(mm(IKH, P), tr(IKH)), mm(mm(K, [[RN[0], 0], [0, RN[1]]]), tr(K)))];
  }
  function run(seed, steps, off, n) {
    const g = rng(seed); let est = [0, 0, 0], x = [P0[0] * g(), P0[1] * g(), P0[2] * g() + off], P = [[P0[0] ** 2, 0, 0], [0, P0[1] ** 2, 0], [0, 0, P0[2] ** 2]], dr = est.slice();
    const out = [{x, est, dr, P}];
    for (let k = 0; k < steps; k++) {
      x = f(x, [U[0] + SV * g(), U[1] + SW * g()]); dr = f(dr, U); [est, P] = predict(est, P, U);
      for (let j = 0; j < n; j++) { const z = h(x, LMS[j]); if (z[0] < RMAX) [est, P] = update(est, P, [z[0] + Math.sqrt(RN[0]) * g(), z[1] + Math.sqrt(RN[1]) * g()], LMS[j]); }
      out.push({x, est, dr, P});
    }
    return out;
  }
  const nees = o => { const e = [o.est[0] - o.x[0], o.est[1] - o.x[1], wrap(o.est[2] - o.x[2])], w = mm(inv3(o.P), e.map(v => [v])); return e[0] * w[0][0] + e[1] * w[1][0] + e[2] * w[2][0]; };
  // the lesson's own mean_nees(30, offset, lms=LMS[:n]) run offline: row = offset 0.0 to 1.5 step 0.1, column = 1 to 4 posts
  const MEAN = [[3.6,3.1,2.8,3.0],[4.0,3.1,2.8,2.9],[5.4,3.1,2.7,2.9],[7.8,3.1,2.7,2.8],[11.6,3.1,2.7,2.8],[17.2,3.1,2.7,2.8],[25.2,3.0,7.8,2.8],[36.5,3.0,2.7,2.8],[52.1,3.0,2.7,2.8],[73.0,3.0,2.7,2.8],[100.5,3.0,2.8,2.7],[135.9,3.1,2.8,2.7],[180.5,3.3,2.9,2.7],[235.5,3.5,3.0,2.7],[301.7,3.9,3.1,2.7],[379.3,4.4,3.2,2.7]];
  const meanNees = (off, n) => MEAN[Math.round(off / .1)][n - 1];
  let vk = '', vr = null;
  const view = (off, n) => { const k = off + ':' + n; if (k !== vk) { vk = k; vr = run(7, STEPS, off, n); } return vr; };
  window.MOTION.three('ekf-circle-3d', {
    en: 'A floor robot drives a circle among four posts and corrects its position estimate from range and bearing. A wrong start heading with only one post leaves the filter confidently wrong',
    ko: '바닥 로봇이 기둥 네 개 사이에서 원을 그리며 거리와 방위로 위치 추정을 고칩니다. 출발 방향이 틀린데 기둥을 하나만 쓰면 필터가 자신 있게 틀립니다',
    cap: ['Green is the true path and robot, grey dashed is dead reckoning from the commands only, blue is the EKF estimate and the blue ring is its 2-sigma position uncertainty. The robot starts with a heading that is off by the slider’s angle without the filter knowing (as in the lesson’s mean_nees(heading_offset)). The posts are the lesson’s LMS in the order shown; the slider picks how many the filter can use. “Mean NEES” is the lesson’s consistency number, the average of e^T P^-1 e over 30 runs, and should be 3 for a consistent filter. It is read from a table made by running the lesson’s own mean_nees(30, offset, lms) offline (with one post: 3.6, 25.2 and 379 for offsets 0, 0.6 and 1.5; with four posts about 2.7 to 3.0). The path you see is one run of a JavaScript port of the lesson’s filter with a fixed noise sequence, not the lesson’s numpy seed, so its single-step values differ from the table. “NEES now” is that run’s value at the current step.',
      '초록색이 실제 경로와 로봇이고 회색 점선은 명령만으로 계산한 dead reckoning이며 파란색이 EKF 추정과 그 2-sigma 위치 불확실성 고리입니다. 로봇은 필터가 모르는 채로 슬라이더 값만큼 틀린 방향에서 출발합니다(레슨의 mean_nees(heading_offset)와 같습니다). 기둥은 레슨의 LMS이고 보이는 순서대로이며 슬라이더로 필터가 쓸 수 있는 개수를 고릅니다. “Mean NEES”는 레슨의 일관성 지표로 30회 실행에서 e^T P^-1 e를 평균한 값이고 일관된 필터는 3이어야 합니다. 레슨의 mean_nees(30, offset, lms)를 미리 돌려 만든 표에서 읽습니다(기둥 1개일 때 offset 0, 0.6, 1.5에서 3.6, 25.2, 379이고 기둥 4개일 때는 약 2.7~3.0). 화면의 경로는 레슨의 필터를 JavaScript로 옮겨 고정 noise 수열로 한 번 돌린 결과이며 레슨의 numpy seed가 아니므로 step별 값은 표와 다릅니다. “지금 NEES”는 그 실행의 현재 step 값입니다.'],
    period: 12, rest: 12, H: 380, unit: 44, look: [0, 2.2, 0], oy: 60, cam: {yaw: 0, pitch: 1.05, dist: 8},
    controls: [
      {id: 'off', en: 'start heading error', ko: '출발 방향 오차', min: 0, max: 1.5, step: .1, dec: 1, unit: ' rad', val: .6},
      {id: 'n', en: 'posts the filter uses', ko: '필터가 쓰는 기둥 수', min: 1, max: 4, step: 1, val: 1},
    ],
  }, (s, t, m) => {
    const off = s.v.off, n = s.v.n, V = view(off, n), k = Math.min(STEPS, Math.floor(Math.min(1, t / 11) * (STEPS + 1))), o = V[k], I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    const xy = a => [a[0], a[1], .02];
    s.poly([[-4.7, -2.7, -.03], [4.7, -2.7, -.03], [4.7, 6.6, -.03], [-4.7, 6.6, -.03]], '--line', {a: .2});
    LMS.forEach((l, j) => { s.box([l[0], l[1], .3], [.1, .1, .3], I, j < n ? '--pl' : '--mut', {a: j < n ? 1 : .4}); if (j < n && h(o.x, l)[0] < RMAX) s.line(xy(o.x), xy(l), '--pl', 1, {dash: [3, 4], a: .6}); });
    s.path(V.slice(0, k + 1).map(q => xy(q.x)), '--ok', 2.5); s.path(V.slice(0, k + 1).map(q => xy(q.dr)), '--mut', 2, {dash: [4, 4]}); s.path(V.slice(0, k + 1).map(q => xy(q.est)), '--pf', 2.5);
    const P = o.P, a = P[0][0], b = P[0][1], c = P[1][1], mid = (a + c) / 2, dd = Math.sqrt(((a - c) / 2) ** 2 + b * b), ang = .5 * Math.atan2(2 * b, a - c), l1 = Math.sqrt(Math.max(mid + dd, 0)) * 2, l2 = Math.sqrt(Math.max(mid - dd, 0)) * 2, ring = [];
    for (let i = 0; i <= 24; i++) { const q = 2 * PI * i / 24, ex = l1 * Math.cos(q), ey = l2 * Math.sin(q); ring.push([o.est[0] + ex * Math.cos(ang) - ey * Math.sin(ang), o.est[1] + ex * Math.sin(ang) + ey * Math.cos(ang), .03]); }
    s.path(ring, '--pf', 2, {front: true});
    s.box([o.x[0], o.x[1], .08], [.22, .14, .08], R.rz(o.x[2]), '--ok'); s.dot(xy(o.est), '--pf', 5, {ring: true, front: true});
    const err = Math.hypot(o.est[0] - o.x[0], o.est[1] - o.x[1]), mn = meanNees(off, n);
    s.text(14, 24, m.t(`position error ${err.toFixed(2)} m, claims ±${(Math.sqrt(a + c)).toFixed(2)} m`, `위치 오차 ${err.toFixed(2)} m, 스스로 ±${(Math.sqrt(a + c)).toFixed(2)} m라고 주장`), '--fg', 14);
    s.text(14, 44, m.t(`NEES now ${nees(o).toFixed(1)}`, `지금 NEES ${nees(o).toFixed(1)}`), '--mut', 14);
    s.text(14, 64, m.t(`mean NEES (lesson, 30 runs) ${mn.toFixed(1)}; consistent = 3`, `평균 NEES (레슨, 30회) ${mn.toFixed(1)}; 일관되면 3`), mn < 6 ? '--ok' : '--bad', 14);
  });
})();
