// 08단계 3D: 같은 wheel 명령을 실제 track과 nominal odometry에 적분해 drift를 보여 준다.
(() => {
  const R = window.M3D, PI = Math.PI, DT = .01, RAD = .05, TRACK = .3;
  const SIDE = 2, SPEED = .5, TURN = 157, STRAIGHT = Math.round(SIDE / SPEED / DT);
  const STEPS = 4 * (STRAIGHT + TURN), stride = 10;
  const ramp = t => Math.max(0, Math.min(1, (t - 1) / 9));
  // Same twist_to_wheels and exact-arc dead_reckon as code/main.py.
  function integrate(error) {
    const truth = [[0, 0, 0]], odom = [[0, 0, 0]];
    for (let i = 0; i < STEPS; i++) {
      const corner = i % (STRAIGHT + TURN) >= STRAIGHT;
      const v = corner ? 0 : SPEED, w = corner ? PI / 2 / (TURN * DT) : 0;
      const wl = (v - w * TRACK / 2) / RAD, wr = (v + w * TRACK / 2) / RAD;
      [truth, odom].forEach((out, j) => {
        const b = TRACK * (j === 0 ? 1 + error / 100 : 1), last = out[out.length - 1];
        const speed = RAD * (wr + wl) / 2, omega = RAD * (wr - wl) / b;
        const d = omega * DT, h = d / 2, chord = speed * DT * (h === 0 ? 1 : Math.sin(h) / h);
        out.push([last[0] + chord * Math.cos(last[2] + h), last[1] + chord * Math.sin(last[2] + h), last[2] + d]);
      });
    }
    return {error, truth, odom, shown: -1, actualLine: [], odomLine: []};
  }
  window.MOTION.three('odometry-drift-3d', {
    en: 'A differential-drive robot follows square wheel commands. Its actual track width differs from the value used by odometry, so the two paths separate',
    ko: '차동 구동 로봇에 정사각형을 도는 wheel 명령을 줍니다. 실제 track width가 odometry 설정과 달라 두 경로가 벌어집니다',
    cap: ['The solid line is the true path with the track wider by the slider percentage; the dashed line is nominal odometry, which still closes its square. Both integrate the same wheel commands with the lesson’s exact circular arcs. r=0.05 m, b=0.30 m, side=2 m, v=0.5 m/s, dt=0.01 s. Playback compresses model time.',
      '실선은 slider만큼 track이 넓어진 실제 경로이고 점선은 정사각형을 닫는 nominal odometry입니다. 같은 wheel 명령을 lesson의 정확한 원호 식으로 적분합니다. r=0.05 m, b=0.30 m, 한 변은 2 m, v=0.5 m/s, dt=0.01 s입니다. 재생 시간은 압축했습니다.'],
    period: 12, rest: 11, H: 350, unit: 70, look: [1, 1, 0], oy: 15,
    cam: {yaw: -.45, pitch: .85, dist: 9},
    controls: [{id: 'error', en: 'true track wider', ko: '실제 track 증가', min: 0, max: 5, step: .1, dec: 1, unit: '%', val: 2},
      {id: 'progress', en: 'route fraction', ko: '경로 진행 비율', min: 0, max: 1, step: .001, dec: 2, auto: ramp}],
  }, (s, t, m) => {
    if (!s.cache || s.cache.error !== s.v.error) s.cache = integrate(s.v.error);
    const c = s.cache, index = Math.round(s.v.progress * STEPS), truth = c.truth[index], odom = c.odom[index];
    // Reuse path arrays; only rebuild when the displayed step changes, not at camera frame rate.
    const shown = Math.floor(index / stride);
    if (shown !== c.shown) {
      c.shown = shown; c.actualLine.length = 0; c.odomLine.length = 0;
      for (let i = 0; i <= shown * stride; i += stride) {
        c.actualLine.push([c.truth[i][0], c.truth[i][1], 0]);
        c.odomLine.push([c.odom[i][0], c.odom[i][1], 0]);
      }
    }
    const gap = Math.hypot(truth[0] - odom[0], truth[1] - odom[1]);
    s.model = {truth, odom, gap, steps: STEPS};
    for (let i = 0; i <= 5; i++) {
      const x = i * SIDE / 4 - SIDE / 4;
      s.line([x, -.5, 0], [x, 2.5, 0], '--line', 1);
      s.line([-.5, x, 0], [2.5, x, 0], '--line', 1);
    }
    if (c.actualLine.length > 1) { s.path(c.actualLine, '--pf', 3.5); s.path(c.odomLine, '--mut', 2, {dash: [5, 4]}); }
    const body = [truth[0], truth[1], RAD * 2], rot = R.rz(truth[2]);
    s.box(body, [TRACK / 2, TRACK / 3, RAD], rot, '--pf');
    [-1, 1].forEach(sign => {
      const p = R.add([truth[0], truth[1], RAD], R.mv(rot, [0, sign * TRACK * (1 + s.v.error / 100) / 2, 0]));
      s.box(p, [RAD, RAD / 3, RAD], rot, '--fg');
    });
    s.wire([odom[0], odom[1], RAD * 2], [TRACK / 2, TRACK / 3, RAD], R.rz(odom[2]), '--mut', 2, {dash: [4, 4]});
    s.dot([0, 0, 0], '--ok', 5, {ring: true});
    s.line([truth[0], truth[1], .01], [odom[0], odom[1], .01], '--bad', 2);
    s.text(14, 24, m.t('Solid: true / dashed: odometry', '실선: 실제 / 점선: odometry'), '--fg', 15);
    s.text(14, 44, m.t(`position gap = ${gap.toFixed(3)} m`, `위치 차이 = ${gap.toFixed(3)} m`), '--bad', 15);
    s.text(14, 64, m.t(`model time ${(index * DT).toFixed(2)} s`, `모델 시간 ${(index * DT).toFixed(2)} s`), '--mut', 15);
  });
})();

// 08단계 3D (wave 3d): particle-floor-3d, occupancy-room-3d, pure-pursuit-3d, icp-room-3d, pose-graph-loop-3d. Each scene is a JavaScript port of the lesson's own code in code/main.py.
(() => {
  const R = window.M3D, PI = Math.PI, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  const rng = seed => { const u = () => { seed = seed + 0x6D2B79F5 | 0; let x = Math.imul(seed ^ seed >>> 15, 1 | seed); x = x + Math.imul(x ^ x >>> 7, 61 | x) ^ x; return ((x ^ x >>> 14) >>> 0) / 4294967296; }; u.g = () => Math.sqrt(-2 * Math.log(1 - u())) * Math.cos(2 * PI * u()); return u; };
  const wrap = a => ((a + PI) % (2 * PI) + 2 * PI) % (2 * PI) - PI;
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));

  // ---- 08/02: particle filter. Lesson: LANDMARKS = room corners, truth moves v 0.8, w 0.15, dt 0.1, 40 steps, range noise 0.3; pf_step with sv 0.4, sw 1.0 ----
  const LM = [[0, 0], [10, 0], [10, 10], [0, 10]], PSTEPS = 40, PDT = .1, PV = .8, PW = .15, PSIG = .3, pcache = {};
  const move1 = (x, y, th, v, w) => { const a = th + w * PDT / 2; return [x + v * PDT * Math.cos(a), y + v * PDT * Math.sin(a), th + w * PDT]; };
  function pfRun(N) {
    if (pcache[N]) return pcache[N];
    const u = rng(21), g = u.g; let P = new Float64Array(N * 3), tr = [2, 3, .3];
    for (let i = 0; i < N; i++) { P[3 * i] = 10 * u(); P[3 * i + 1] = 10 * u(); P[3 * i + 2] = (2 * u() - 1) * PI; }
    const est = P => { let x = 0, y = 0, c = 0, s = 0; for (let i = 0; i < N; i++) { x += P[3 * i]; y += P[3 * i + 1]; c += Math.cos(P[3 * i + 2]); s += Math.sin(P[3 * i + 2]); } return [x / N, y / N, Math.atan2(s / N, c / N)]; };
    const out = [{P: Float64Array.from(P), tr: tr.slice(), est: est(P), neff: N}];
    for (let k = 0; k < PSTEPS; k++) {
      tr = move1(tr[0], tr[1], tr[2], PV, PW);
      const z = LM.map(l => Math.hypot(tr[0] - l[0], tr[1] - l[1]) + PSIG * g()), Q = new Float64Array(N * 3), lw = new Float64Array(N); let mx = -1e300;
      for (let i = 0; i < N; i++) {
        const m = move1(P[3 * i], P[3 * i + 1], P[3 * i + 2], PV + .4 * g(), PW + 1 * g()); Q[3 * i] = m[0]; Q[3 * i + 1] = m[1]; Q[3 * i + 2] = m[2];
        let a = 0; for (let j = 0; j < 4; j++) a += ((Math.hypot(m[0] - LM[j][0], m[1] - LM[j][1]) - z[j]) / PSIG) ** 2; lw[i] = -.5 * a; mx = Math.max(mx, lw[i]);
      }
      let sum = 0; for (let i = 0; i < N; i++) { lw[i] = Math.exp(lw[i] - mx); sum += lw[i]; }
      let sq = 0; for (let i = 0; i < N; i++) { lw[i] /= sum; sq += lw[i] * lw[i]; }
      const u0 = u(); let c = lw[0], j = 0;   // systematic resampling: one random offset, N evenly spaced pointers into the cumulative weights
      const R2 = new Float64Array(N * 3);
      for (let i = 0; i < N; i++) { const target = (u0 + i) / N; while (c < target && j < N - 1) c += lw[++j]; R2[3 * i] = Q[3 * j]; R2[3 * i + 1] = Q[3 * j + 1]; R2[3 * i + 2] = Q[3 * j + 2]; }
      P = R2; out.push({P: Float64Array.from(P), tr: tr.slice(), est: est(P), neff: 1 / sq});
    }
    return pcache[N] = out;
  }
  window.MOTION.three('particle-floor-3d', {
    en: 'A floor robot knows nothing about where it is, so hundreds of guesses spread over the room. Range readings to four corner posts make the wrong guesses disappear',
    ko: '바닥 로봇은 자기 위치를 전혀 모르는 상태에서 시작해 방 전체에 추측 수백 개를 뿌립니다. 네 모서리 기둥까지의 거리를 읽으면 틀린 추측이 사라집니다',
    cap: ['Each blue square is one particle, a guess of the robot’s x, y and heading. Every step the guesses move with noise (speed noise 0.4, turn noise 1.0), get a weight from how well their ranges to the four corner posts match the measured ranges (noise 0.3 m), and are resampled so good guesses are copied and bad ones dropped. The green robot drives the lesson’s arc (0.8 m/s, 0.15 rad/s, 0.1 s steps, 40 steps from (2, 3)). N_eff is 1 / sum of squared weights before resampling: near the particle count means every guess is still plausible, a small value means only a few are. The code is the lesson’s pf_step with systematic resampling; the random numbers are a fixed JavaScript sequence, so errors differ a little from the lesson’s numpy seed (0.11 m at the end with 500 particles).',
      '파란 사각형 하나가 particle 하나이고 로봇의 x, y, 방향에 대한 추측입니다. 매 step 추측들이 noise(속도 noise 0.4, 회전 noise 1.0)와 함께 움직이고, 네 모서리 기둥까지 잰 거리와 얼마나 맞는지로 weight를 받은 뒤 resampling으로 잘 맞는 추측은 복사되고 안 맞는 추측은 사라집니다. 초록색 로봇은 수업의 호를 따라 달립니다(0.8 m/s, 0.15 rad/s, 0.1 s 간격, (2, 3)에서 40 step). N_eff는 resampling 전 weight 제곱합의 역수로, particle 수에 가까우면 모든 추측이 아직 그럴듯하다는 뜻이고 작으면 몇 개만 남았다는 뜻입니다. 코드는 수업의 pf_step과 systematic resampling이고 난수는 고정된 JavaScript 수열이라 수업의 numpy seed 결과(particle 500개로 마지막 오차 0.11 m)와 조금 다릅니다.'],
    period: 12, rest: 12, H: 400, unit: 34, look: [5, 5, 0], oy: 45, cam: {yaw: .1, pitch: 1.0, dist: 16},
    controls: [
      {id: 'n', en: 'particles', ko: 'particle 수', min: 20, max: 500, step: 20, val: 500},
      {id: 'k', en: 'step', ko: 'step', min: 0, max: PSTEPS, step: 1, auto: t => Math.min(PSTEPS, Math.floor(PSTEPS * Math.min(1, t / 11) ** 2))},
    ],
  }, (s, t, m) => {
    const N = s.v.n, S = pfRun(N)[s.v.k], P = S.P, pts = [];
    s.poly([[0, 0, -.02], [10, 0, -.02], [10, 10, -.02], [0, 10, -.02]], '--line', {a: .25, edge: '--line', w: 1});
    LM.forEach(l => { s.box([l[0], l[1], .35], [.12, .12, .35], I, '--pl'); s.line([S.tr[0], S.tr[1], .02], [l[0], l[1], .02], '--pl', 1, {dash: [3, 4], a: .55}); });
    for (let i = 0; i < N; i++) pts.push([P[3 * i], P[3 * i + 1], .03]);
    s.points(pts, '--pf', 2.2, {a: .85, bias: -1});
    s.box([S.tr[0], S.tr[1], .12], [.25, .16, .12], R.rz(S.tr[2]), '--ok'); s.dot([S.est[0], S.est[1], .1], '--fg', 6, {ring: true, front: true});
    const err = Math.hypot(S.est[0] - S.tr[0], S.est[1] - S.tr[1]);
    s.text(14, 24, m.t(`step ${s.v.k} of ${PSTEPS}, ${N} particles`, `step ${s.v.k} / ${PSTEPS}, particle ${N}개`), '--fg', 15);
    s.text(14, 44, m.t(`error of the mean guess ${err.toFixed(2)} m`, `평균 추측의 오차 ${err.toFixed(2)} m`), err < .5 ? '--ok' : '--bad', 15);
    s.text(14, 64, m.t(`N_eff ${S.neff.toFixed(0)} of ${N}`, `N_eff ${S.neff.toFixed(0)} / ${N}`), '--mut', 15);
  });

  // ---- 08/03: occupancy grid. Lesson: 40 x 40 cells of 0.25 m, walls plus a 2 m box, 180 beams, loop of 200 poses (radius 3 m), yaw drift per step ----
  const NC = 40, RES = .25, LOCC = .85, LFREE = .4, LMAX = 5, NB = 180, NP = 200;
  const WORLD = new Uint8Array(NC * NC); for (let i = 0; i < NC; i++) { WORLD[i] = WORLD[(NC - 1) * NC + i] = WORLD[i * NC] = WORLD[i * NC + NC - 1] = 1; }
  for (let r = 16; r < 24; r++) for (let c = 16; c < 24; c++) WORLD[r * NC + c] = 1;
  const cellOf = p => clamp(Math.trunc(p / RES), 0, NC - 1);
  const ANG = Array.from({length: NB}, (_, i) => -PI + 2 * PI * i / NB);
  const TRUEP = Array.from({length: NP}, (_, i) => { const a = 2 * PI * i / NP; return [5 + 3 * Math.cos(a), 5 + 3 * Math.sin(a), a + PI / 2]; });
  let SCANS = null;
  function scanOnce(pose, ang, noise) {
    const a = pose[2] + ang, dx = Math.cos(a), dy = Math.sin(a); let r = 8;
    for (let i = 0; i < 128; i++) { const t = i * RES / 4, px = pose[0] + t * dx, py = pose[1] + t * dy;
      if (px < 0 || py < 0 || px >= NC * RES || py >= NC * RES || WORLD[cellOf(py) * NC + cellOf(px)]) { r = t; break; } }
    return r + noise;
  }
  const driftPoses = e => {   // main.py drift(): step lengths stay exact, the heading gains e rad per step
    const out = [TRUEP[0].slice()]; let x = TRUEP[0][0], y = TRUEP[0][1];
    for (let k = 1; k < NP; k++) { const dx = TRUEP[k][0] - TRUEP[k - 1][0], dy = TRUEP[k][1] - TRUEP[k - 1][1], w = Math.atan2(dy, dx) + e * k, d = Math.hypot(dx, dy); x += d * Math.cos(w); y += d * Math.sin(w); out.push([x, y, TRUEP[k][2] + e * k]); }
    out[0][2] = TRUEP[0][2]; return out;
  };
  const gridCache = {};
  function buildMap(e) {
    const key = e.toFixed(4); if (gridCache[key]) return gridCache[key];
    if (!SCANS) { const u = rng(33); SCANS = TRUEP.map(p => ANG.map(a => scanOnce(p, a, .03 * u.g()))); }
    const est = e ? driftPoses(e) : TRUEP, L = new Float32Array(NC * NC), free = new Uint8Array(NC * NC), occ = new Uint8Array(NC * NC);
    for (let k = 0; k < NP; k++) {
      free.fill(0); occ.fill(0); const p = est[k], r = SCANS[k];
      for (let b = 0; b < NB; b++) {
        const a = p[2] + ANG[b], dx = Math.cos(a), dy = Math.sin(a);
        for (let i = 0; i < 64; i++) { const t = i * RES / 2; if (t < r[b] - RES / 2) free[cellOf(p[1] + t * dy) * NC + cellOf(p[0] + t * dx)] = 1; }
        if (r[b] < 8 - 1e-6) occ[cellOf(p[1] + r[b] * dy) * NC + cellOf(p[0] + r[b] * dx)] = 1;
      }
      for (let i = 0; i < NC * NC; i++) { if (occ[i]) L[i] = clamp(L[i] + LOCC, -LMAX, LMAX); else if (free[i]) L[i] = clamp(L[i] - LFREE, -LMAX, LMAX); }
    }
    const good = [], bad = []; for (let i = 0; i < NC * NC; i++) if (L[i] > 0) (WORLD[i] ? good : bad).push([((i % NC) + .5) * RES, (Math.floor(i / NC) + .5) * RES, .03]);
    return gridCache[key] = {good, bad, count: good.length + bad.length, precision: good.length / Math.max(good.length + bad.length, 1), path: est.filter((_, i) => i % 4 === 0).map(q => [q[0], q[1], .04])};
  }
  window.MOTION.three('occupancy-room-3d', {
    en: 'A floor robot circles a room and paints what its laser sees. If its heading estimate drifts, the same wall is painted in many places and the map smears',
    ko: '바닥 로봇이 방을 한 바퀴 돌며 laser로 본 것을 지도에 칠합니다. 방향 추정이 조금씩 틀어지면 같은 벽이 여러 곳에 칠해져 지도가 번집니다',
    cap: ['The room is the lesson’s 10 m x 10 m grid of 0.25 m cells with walls and a 2 m box. The robot drives a 3 m radius loop (200 poses, 180 beams, 0.03 m range noise) and updates a log-odds grid at the pose it believes it has. Blue squares are cells called occupied that really are occupied; red squares are cells called occupied that are empty. The slider is the yaw drift per step (the lesson tries 0, 0.001 and 0.003 rad); the green circle is the real loop and the red dashed curve is the believed one. Lesson numbers with this code: 206 occupied cells and precision 0.89 without drift, 305 and 0.54 at 0.001, 387 and 0.41 at 0.003. The noise here is a fixed JavaScript sequence, so counts differ by a few cells.',
      '방은 수업의 10 m x 10 m, 0.25 m 칸으로 된 격자이고 벽과 2 m짜리 상자가 있습니다. 로봇은 반지름 3 m의 원을 돌며(자세 200개, beam 180개, 거리 noise 0.03 m) 자기가 믿는 자세에서 log-odds 격자를 갱신합니다. 파란 사각형은 occupied라고 판단했고 실제로 occupied인 칸이고 빨간 사각형은 occupied라고 판단했지만 비어 있는 칸입니다. 슬라이더는 step마다 쌓이는 yaw drift입니다(수업은 0, 0.001, 0.003 rad을 시험합니다). 초록 원이 실제 경로이고 빨간 점선이 로봇이 믿는 경로입니다. 이 코드로 얻은 수업의 값은 drift 없을 때 occupied 206칸에 precision 0.89, 0.001에서 305칸과 0.54, 0.003에서 387칸과 0.41입니다. 여기서 noise는 고정된 JavaScript 수열이라 칸 수가 몇 개 다를 수 있습니다.'],
    period: 12, rest: 12, H: 420, unit: 33, look: [5, 5, 0], oy: 45, cam: {yaw: .1, pitch: 1.0, dist: 16},
    controls: [{id: 'e', en: 'yaw drift per step', ko: 'step당 yaw drift', min: 0, max: .003, step: .0005, dec: 4, unit: ' rad', auto: t => .003 * (.5 - .5 * Math.cos(2 * PI * t / 12))}],
  }, (s, t, m) => {
    const M = buildMap(s.v.e);
    s.poly([[0, 0, -.02], [10, 0, -.02], [10, 10, -.02], [0, 10, -.02]], '--line', {a: .22, edge: '--line', w: 1.5});
    s.poly([[4, 4, 0], [6, 4, 0], [6, 6, 0], [4, 6, 0]], '--line', {a: .3, edge: '--line', w: 1.5});
    s.points(M.good, '--pf', 2.4, {bias: -1}); s.points(M.bad, '--bad', 2.4, {bias: -2});
    s.path(TRUEP.concat([TRUEP[0]]).filter((_, i) => i % 4 === 0).map(q => [q[0], q[1], .05]), '--ok', 2, {front: true});
    s.path(M.path, '--bad', 1.5, {dash: [4, 4], front: true});
    s.text(14, 24, m.t(`yaw drift ${s.v.e.toFixed(4)} rad per step`, `step당 yaw drift ${s.v.e.toFixed(4)} rad`), '--fg', 15);
    s.text(14, 44, m.t(`cells called occupied: ${M.count}`, `occupied로 판단한 칸: ${M.count}`), '--fg', 15);
    s.text(14, 64, m.t(`share that really is occupied: ${M.precision.toFixed(2)}`, `실제로 occupied인 비율: ${M.precision.toFixed(2)}`), M.precision > .8 ? '--ok' : '--bad', 15);
  });

  // ---- 08/04: pure pursuit. Lesson follow(): corners (0,0) (10,0) (10,10), v 1 m/s, start (0, 0.6, 0), first-order turn-rate lag tau 0.4 s, dt 0.02 s ----
  const CORNERS = [[0, 0], [10, 0], [10, 10]], PPATH = [];
  CORNERS.slice(0, -1).forEach((a, i) => { const b = CORNERS[i + 1], n = Math.max(Math.floor(Math.hypot(b[0] - a[0], b[1] - a[1]) / .02), 2); for (let j = 0; j < n; j++) PPATH.push([a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n]); });
  PPATH.push(CORNERS[2]);
  const nearIdx = (x, y) => { let b = 0, bd = 1e300; for (let i = 0; i < PPATH.length; i++) { const d = (PPATH[i][0] - x) ** 2 + (PPATH[i][1] - y) ** 2; if (d < bd) { bd = d; b = i; } } return b; };
  const lookAt = (x, y, ld) => { for (let j = nearIdx(x, y); j < PPATH.length; j++) if (Math.hypot(PPATH[j][0] - x, PPATH[j][1] - y) >= ld) return PPATH[j]; return PPATH[PPATH.length - 1]; };
  const ppCache = {};
  function follow(ld) {
    const key = ld.toFixed(2); if (ppCache[key]) return ppCache[key];
    const dt = .02, tau = .4, v = 1; let x = 0, y = .6, th = 0, w = 0; const traj = [[x, y, th]];
    for (let i = 0; i < 3000; i++) {
      const tg = lookAt(x, y, ld), dx = tg[0] - x, dy = tg[1] - y, lat = -Math.sin(th) * dx + Math.cos(th) * dy;
      w += (v * 2 * lat / (dx * dx + dy * dy) - w) * (1 - Math.exp(-dt / tau));
      x += dt * v * Math.cos(th); y += dt * v * Math.sin(th); th += dt * w; traj.push([x, y, th]);
      if (Math.hypot(x - 10, y - 10) < .15) break;
    }
    let cut = 1e9; traj.forEach(q => { cut = Math.min(cut, Math.hypot(q[0] - 10, q[1])); });
    let flips = 0, last = 0; traj.forEach(q => { if (q[0] < 8 && Math.abs(q[1]) > .02) { const sg = Math.sign(q[1]); if (last && sg !== last) flips++; last = sg; } });
    return ppCache[key] = {traj, cut, flips};
  }
  window.MOTION.three('pure-pursuit-3d', {
    en: 'A delivery robot chases a point on its route a set distance ahead. A short look-ahead wiggles; a long one cuts the corner',
    ko: '배달 로봇이 경로 위의 앞쪽 한 점을 쫓아갑니다. Look-ahead가 짧으면 좌우로 흔들리고 길면 모퉁이를 가로질러 자릅니다',
    cap: ['The grey road is the lesson’s route: 10 m east, then 10 m north. The robot drives at 1 m/s and steers toward the first route point at least the look-ahead distance away (green dot; dashed ring = look-ahead). The steering turn rate follows the command with a lag of 0.4 s, as in the lesson. Lesson numbers with this code: look-ahead 0.4 m gives a 0.17 m corner cut and 10 sign changes of the offset on the first leg; 1.5 m gives 0.41 m and 1; 4.0 m gives 1.37 m and 0. The robot starts 0.6 m off the route. This is a point robot on a flat floor, no wheel slip or obstacles.',
      '회색 도로가 수업의 경로입니다. 동쪽으로 10 m 가고 북쪽으로 10 m 갑니다. 로봇은 1 m/s로 달리며 look-ahead 거리 이상 떨어진 첫 경로 점(초록 점, 점선 고리가 look-ahead)을 향해 조향합니다. 회전 속도는 수업처럼 0.4 s 지연으로 명령을 따라갑니다. 이 코드로 얻은 수업의 값은 look-ahead 0.4 m에서 모퉁이를 0.17 m 자르고 첫 구간에서 offset 부호가 10번 바뀌며 1.5 m에서는 0.41 m와 1번, 4.0 m에서는 1.37 m와 0번입니다. 로봇은 경로에서 0.6 m 떨어져 출발합니다. 평평한 바닥 위의 점 로봇이며 바퀴 미끄러짐이나 장애물은 없습니다.'],
    period: 12, rest: 12, H: 420, unit: 30, look: [5, 5, 0], oy: 40, cam: {yaw: 0, pitch: 1.1, dist: 16},
    controls: [{id: 'ld', en: 'look-ahead distance', ko: 'look-ahead 거리', min: .4, max: 4, step: .1, dec: 1, unit: ' m', val: 1.5}],
  }, (s, t, m) => {
    const F = follow(s.v.ld), i = Math.min(F.traj.length - 1, Math.floor(clamp(t / 10, 0, 1) * (F.traj.length - 1))), q = F.traj[i], tg = lookAt(q[0], q[1], s.v.ld);
    s.poly([[-.6, -.6, -.02], [10.6, -.6, -.02], [10.6, 10.6, -.02], [-.6, 10.6, -.02]], '--line', {a: .12});
    s.path(PPATH.filter((_, k) => k % 10 === 0).concat([[10, 10]]).map(p => [p[0], p[1], 0]), '--line', 9, {a: .6});
    s.path(PPATH.filter((_, k) => k % 10 === 0).concat([[10, 10]]).map(p => [p[0], p[1], .01]), '--mut', 1, {dash: [5, 5]});
    s.path(F.traj.slice(0, i + 1).filter((_, k) => k % 5 === 0 || k === i).map(p => [p[0], p[1], .05]), '--pf', 3, {front: true});
    const ring = Array.from({length: 25}, (_, k) => [q[0] + s.v.ld * Math.cos(2 * PI * k / 24), q[1] + s.v.ld * Math.sin(2 * PI * k / 24), .03]); s.path(ring, '--mut', 1, {dash: [3, 4]});
    s.line([q[0], q[1], .08], [tg[0], tg[1], .08], '--ok', 1.5, {dash: [3, 3]}); s.dot([tg[0], tg[1], .1], '--ok', 6, {ring: true, front: true});
    s.box([q[0], q[1], .13], [.3, .2, .13], R.rz(q[2]), '--pd');
    s.text(14, 24, m.t(`look-ahead ${s.v.ld.toFixed(1)} m`, `look-ahead ${s.v.ld.toFixed(1)} m`), '--fg', 15);
    s.text(14, 44, m.t(`corner cut ${F.cut.toFixed(2)} m`, `모퉁이를 자른 거리 ${F.cut.toFixed(2)} m`), F.cut > 1 ? '--bad' : '--fg', 15);
    s.text(14, 64, m.t(`offset sign changes on leg 1: ${F.flips}`, `첫 구간 offset 부호 변화: ${F.flips}번`), F.flips > 3 ? '--bad' : '--fg', 15);
  });

  // ---- 08/05: ICP. Lesson: L-shaped room outline, points every 0.05 m (second scan starts half a spacing in), moved = (cur - [0.3, -0.2]) rotated by the start angle, <= 60 iterations ----
  const ROOM = [[0, 0], [6, 0], [6, 2], [4, 2], [4, 4], [0, 4], [0, 0]];
  const roomPts = phase => { const o = []; for (let e = 0; e < 6; e++) { const a = ROOM[e], b = ROOM[e + 1], n = Math.hypot(b[0] - a[0], b[1] - a[1]); for (let i = 0, s; (s = phase * .05 + i * .05) < n - 1e-9; i++) o.push(a[0] + s * (b[0] - a[0]) / n, a[1] + s * (b[1] - a[1]) / n); } return Float64Array.from(o); };
  const REF = roomPts(0), CUR = roomPts(.5), icpCache = {};
  const nearest = (A, B) => { const out = new Int32Array(A.length / 2); for (let i = 0; i < A.length; i += 2) { let b = 0, bd = 1e300; for (let j = 0; j < B.length; j += 2) { const d = (A[i] - B[j]) ** 2 + (A[i + 1] - B[j + 1]) ** 2; if (d < bd) { bd = d; b = j; } } out[i / 2] = b; } return out; };
  const rmsTo = (A, B, idx) => { let s = 0; for (let i = 0; i < A.length; i += 2) s += (A[i] - B[idx[i / 2]]) ** 2 + (A[i + 1] - B[idx[i / 2] + 1]) ** 2; return Math.sqrt(s / (A.length / 2)); };
  function icp(ang) {
    const key = ang.toFixed(2); if (icpCache[key]) return icpCache[key];
    const c = Math.cos(ang), sn = Math.sin(ang), cur0 = new Float64Array(CUR.length);
    for (let i = 0; i < CUR.length; i += 2) { const x = CUR[i] - .3, y = CUR[i + 1] + .2; cur0[i] = x * c + y * sn; cur0[i + 1] = -x * sn + y * c; }   // row vector times [[c, -s], [s, c]]
    let cur = cur0; const snaps = [cur0], match = [], rms = []; let loops = 0;
    for (let it = 0; it < 60; it++) {
      const idx = nearest(cur, REF), n = cur.length / 2; match.push(idx); rms.push(rmsTo(cur, REF, idx)); loops++;
      let px = 0, py = 0, qx = 0, qy = 0; for (let i = 0; i < n; i++) { px += cur[2 * i]; py += cur[2 * i + 1]; qx += REF[idx[i]]; qy += REF[idx[i] + 1]; } px /= n; py /= n; qx /= n; qy /= n;
      let sd = 0, sc = 0; for (let i = 0; i < n; i++) { const ax = cur[2 * i] - px, ay = cur[2 * i + 1] - py, bx = REF[idx[i]] - qx, by = REF[idx[i] + 1] - qy; sd += ax * bx + ay * by; sc += ax * by - ay * bx; }
      const th = Math.atan2(sc, sd), cc = Math.cos(th), ss = Math.sin(th), tx = qx - (cc * px - ss * py), ty = qy - (ss * px + cc * py), nx = new Float64Array(cur.length);   // 2D Kabsch: the rotation that maximises the cross-covariance trace
      for (let i = 0; i < n; i++) { nx[2 * i] = cc * cur[2 * i] - ss * cur[2 * i + 1] + tx; nx[2 * i + 1] = ss * cur[2 * i] + cc * cur[2 * i + 1] + ty; }
      cur = nx; snaps.push(cur);
      if (rms.length > 1 && rms[rms.length - 2] - rms[rms.length - 1] < 1e-12) break;
    }
    const last = nearest(cur, REF); match.push(last); rms.push(rmsTo(cur, REF, last));
    return icpCache[key] = {snaps, match, rms, loops};
  }
  window.MOTION.three('icp-room-3d', {
    en: 'Two laser scans of an L-shaped room, one turned and shifted. ICP pairs each point with its nearest neighbour and slides the scan, again and again; a big start rotation can lock onto the wrong wall',
    ko: 'L자 방을 잰 laser scan 두 장이 있고 하나는 돌아가고 밀려 있습니다. ICP는 점마다 가장 가까운 점과 짝을 짓고 scan을 옮기는 일을 되풀이하는데, 처음 회전이 크면 엉뚱한 벽에 붙어 버립니다',
    cap: ['Green dots are the reference scan of the lesson’s L-shaped room (points every 0.05 m). Orange dots are the second scan, shifted by (0.3, −0.2) and turned by the slider angle. Thin lines are the nearest-point pairs of this iteration; each iteration moves the orange scan by the rotation and shift that best fit those pairs (the lesson’s Kabsch step, solved here with the closed-form 2D angle). With this code the lesson reports: start 0.2 rad, 12 iterations, final rms 0.016 m; 1.0 rad, 27 iterations, 0.016 m; 2.6 rad, 25 iterations, 0.538 m, which is a wrong local minimum. The rms shown is the nearest-point error before each iteration. The run is cached per angle and played at one iteration per step; the second scan has no noise, as in the lesson.',
      '초록 점은 수업의 L자 방(0.05 m 간격)의 reference scan입니다. 주황 점은 (0.3, −0.2)만큼 밀고 슬라이더 각도만큼 돌린 두 번째 scan입니다. 가는 선은 이번 iteration의 최근접 점 쌍이고, iteration마다 그 쌍에 가장 잘 맞는 회전과 이동으로 주황 scan을 옮깁니다(수업의 Kabsch 단계이며 여기서는 2D 각도의 닫힌 해로 풉니다). 이 코드로 수업이 보고하는 값은 시작 0.2 rad에서 12번 반복에 마지막 rms 0.016 m, 1.0 rad에서 27번에 0.016 m, 2.6 rad에서 25번에 0.538 m이며 마지막은 틀린 local minimum입니다. 표시한 rms는 각 iteration 직전의 최근접 점 오차입니다. 각도마다 한 번 계산해 두고 한 step에 iteration 하나씩 보여 주며 수업처럼 두 번째 scan에는 noise가 없습니다.'],
    period: 12, rest: 12, H: 400, unit: 52, look: [3, 2, 0], oy: 40, cam: {yaw: 0, pitch: 1.15, dist: 16},
    controls: [
      {id: 'ang', en: 'start rotation', ko: '처음 회전', min: .2, max: 2.8, step: .1, dec: 1, unit: ' rad', val: 1},
      {id: 'it', en: 'iteration', ko: 'iteration', min: 0, max: 30, step: 1, auto: t => Math.min(30, Math.floor(t / 11 * 31))},
    ],
  }, (s, t, m) => {
    const F = icp(s.v.ang), k = Math.min(s.v.it, F.loops), cur = F.snaps[k], idx = F.match[k], pts = [], refp = [];
    for (let i = 0; i < cur.length; i += 2) pts.push([cur[i], cur[i + 1], .03]);
    for (let i = 0; i < REF.length; i += 2) refp.push([REF[i], REF[i + 1], .02]);
    s.path(ROOM.map(p => [p[0], p[1], 0]), '--line', 1.5, {dash: [4, 4]});
    for (let i = 0; i < cur.length; i += 14) s.line([cur[i], cur[i + 1], .02], [REF[idx[i / 2]], REF[idx[i / 2] + 1], .02], '--mut', 1, {a: .6});
    s.points(refp, '--ok', 1.8, {bias: -1}); s.points(pts, '--pl', 1.8, {bias: -2});
    const stuck = F.rms[F.rms.length - 1] > .1;
    s.text(14, 24, m.t(`iteration ${k} of ${F.loops}`, `iteration ${k} / ${F.loops}`), '--fg', 15);
    s.text(14, 44, m.t(`rms nearest-point error ${F.rms[k].toFixed(3)} m`, `최근접 점 rms 오차 ${F.rms[k].toFixed(3)} m`), '--fg', 15);
    if (k >= F.loops) s.text(14, 64, stuck ? m.t('stuck on the wrong match', '엉뚱한 짝에 붙어 멈춤') : m.t('scans lined up', 'scan이 맞춰짐'), stuck ? '--bad' : '--ok', 15);
  });

  // ---- 08/06: pose graph. Lesson world(default_rng(0)): square loop of 20 one-metre steps with a 0.02 rad heading bias per step, plus one loop-closure edge (0, 20). TRUTH, X0 and Z are that run's output ----
  const TRUTH = [[0.0,0.0,0.0],[1.0,0.0,0.0],[2.0,0.0,0.0],[3.0,0.0,0.0],[4.0,0.0,0.0],[5.0,0.0,1.5708],[5.0,1.0,1.5708],[5.0,2.0,1.5708],[5.0,3.0,1.5708],[5.0,4.0,1.5708],[5.0,5.0,-3.14159],[4.0,5.0,-3.14159],[3.0,5.0,-3.14159],[2.0,5.0,-3.14159],[1.0,5.0,-3.14159],[0.0,5.0,-1.5708],[0.0,4.0,-1.5708],[0.0,3.0,-1.5708],[0.0,2.0,-1.5708],[0.0,1.0,-1.5708],[0.0,0.0,0.0]];
  const X0 = [[0.0,0.0,0.0],[1.00251,-0.00264,0.0264],[2.00455,0.0131,0.05002],[3.0284,0.08333,0.06298],[4.00194,0.13223,0.0834],[4.95249,0.2073,1.66173],[4.87385,1.18957,1.67857],[4.74467,2.18971,1.69728],[4.62827,3.21051,1.7208],[4.47426,4.21687,1.73337],[4.32443,5.18697,-2.95682],[3.36053,5.01107,-2.93841],[2.37137,4.8029,-2.91486],[1.40912,4.58357,-2.88702],[0.40611,4.34859,-2.85188],[-0.57355,4.04025,-1.25844],[-0.24043,3.10357,-1.21884],[0.14142,2.14012,-1.19526],[0.49924,1.23225,-1.1687],[0.88778,0.33882,-1.1444],[1.28556,-0.59412,0.43978]];
  const Z = [[1.00251,-0.00264,0.0264],[1.0021,-0.01071,0.02362],[1.02608,0.01894,0.01296],[0.97469,-0.01247,0.02041],[0.9535,-0.00438,1.57834],[0.98535,-0.01089,0.01684],[1.00823,0.02085,0.01871],[1.02733,-0.0133,0.02352],[1.01807,0.00188,0.01257],[0.98157,-0.00915,1.593],[0.97981,-0.00418,0.01841],[1.01082,0.00429,0.02355],[0.98692,-0.00259,0.02784],[1.02987,-0.02518,0.03514],[1.02692,0.01563,1.59344],[0.99372,0.02916,0.0396],[1.03603,0.0263,0.02357],[0.97583,-9e-05,0.02656],[0.97423,0.0079,0.0243],[1.01392,-0.02368,1.58418],[-0.00873,-0.0234,0.01739]];
  const PGW = [20, 20, 50], NPOSE = 21;
  const between = (a, b) => { const c = Math.cos(a[2]), s = Math.sin(a[2]), dx = b[0] - a[0], dy = b[1] - a[1]; return [c * dx + s * dy, -s * dx + c * dy, wrap(b[2] - a[2])]; };
  const EDGES = Z.map((z, k) => [k < 20 ? k : 0, k < 20 ? k + 1 : 20, z]);   // 20 odometry edges then the loop closure
  const residuals = X => { const out = []; EDGES.forEach(([i, j, z]) => { const b = between(X[i], X[j]); out.push(PGW[0] * (b[0] - z[0]), PGW[1] * (b[1] - z[1]), PGW[2] * wrap(b[2] - z[2])); }); return out; };
  function gaussNewton(X) {   // numeric Jacobian over poses 1..20 (pose 0 is the fixed gauge), normal equations solved by elimination
    const nv = 3 * (NPOSE - 1), r = residuals(X), J = []; const eps = 1e-6;
    for (let p = 1; p < NPOSE; p++) for (let c = 0; c < 3; c++) {
      const Xp = X.map(q => q.slice()), Xm = X.map(q => q.slice()); Xp[p][c] += eps; Xm[p][c] -= eps;
      const rp = residuals(Xp), rm = residuals(Xm); J.push(rp.map((v, i) => (v - rm[i]) / (2 * eps)));
    }
    const A = J.map(ci => J.map(cj => ci.reduce((a, v, i) => a + v * cj[i], 0))), b = J.map(ci => -ci.reduce((a, v, i) => a + v * r[i], 0));
    for (let i = 0; i < nv; i++) { let piv = i; for (let k = i + 1; k < nv; k++) if (Math.abs(A[k][i]) > Math.abs(A[piv][i])) piv = k; [A[i], A[piv]] = [A[piv], A[i]]; [b[i], b[piv]] = [b[piv], b[i]];
      for (let k = i + 1; k < nv; k++) { const f = A[k][i] / A[i][i]; for (let j = i; j < nv; j++) A[k][j] -= f * A[i][j]; b[k] -= f * b[i]; } }
    const dx = new Array(nv); for (let i = nv - 1; i >= 0; i--) { let sum = b[i]; for (let j = i + 1; j < nv; j++) sum -= A[i][j] * dx[j]; dx[i] = sum / A[i][i]; }
    return X.map((q, p) => p === 0 ? q.slice() : [q[0] + dx[3 * (p - 1)], q[1] + dx[3 * (p - 1) + 1], wrap(q[2] + dx[3 * (p - 1) + 2])]);
  }
  const ate = X => Math.sqrt(X.reduce((a, q, i) => a + (q[0] - TRUTH[i][0]) ** 2 + (q[1] - TRUTH[i][1]) ** 2, 0) / X.length), cost = X => residuals(X).reduce((a, v) => a + v * v, 0);
  let PGS = null;
  window.MOTION.three('pose-graph-loop-3d', {
    en: 'A floor robot drives around a square and returns 1.4 m from where it began. Tying the end back to the start (a loop closure) and re-solving pulls the whole trip back into shape',
    ko: '바닥 로봇이 정사각형을 한 바퀴 돌았는데 출발점에서 1.4 m 떨어진 곳에 돌아옵니다. 끝을 시작에 묶고(loop closure) 다시 풀면 여행 전체가 제자리로 당겨집니다',
    cap: ['Green dots are the true square (five 1 m steps per side, 21 poses). The blue path and boxes are the robot’s poses as estimated from odometry plus the loop-closure edge, shown after k Gauss-Newton iterations; at k = 0 that is plain dead reckoning, which drifts because every step has a 0.02 rad heading bias. The red line is the loop-closure edge joining the last pose to the first, which should be zero long. The data are the lesson’s world(default_rng(0)), run offline; the solver is a JavaScript port of the lesson’s numeric-Jacobian Gauss-Newton with pose 0 held fixed. Lesson numbers: the end of the odometry is 1.42 m from the start, and the rms position error goes 0.70 m to 0.09 m. Costs here: 1246 at k = 0, then 31, 22, 22. After 3 iterations nothing moves any more.',
      '초록 점은 실제 정사각형입니다(한 변에 1 m 걸음 5개, 자세 21개). 파란 경로와 상자는 odometry와 loop-closure 간선으로 추정한 자세이며 Gauss-Newton을 k번 돌린 뒤의 모습입니다. k = 0은 순수 dead reckoning이라 걸음마다 0.02 rad의 방향 bias 때문에 표류합니다. 빨간 선은 마지막 자세와 첫 자세를 잇는 loop-closure 간선이며 길이가 0이어야 합니다. 데이터는 수업의 world(default_rng(0))를 미리 돌린 결과이고 solver는 수업의 수치 Jacobian Gauss-Newton을 pose 0을 고정한 채 JavaScript로 옮긴 것입니다. 수업의 값은 odometry 끝이 출발점에서 1.42 m 떨어지고 rms 위치 오차가 0.70 m에서 0.09 m로 줄어드는 것입니다. 여기서 cost는 k = 0에서 1246, 이어서 31, 22, 22입니다. 3번 반복하면 더 움직이지 않습니다.'],
    period: 12, rest: 12, H: 400, unit: 50, look: [2, 2.5, 0], oy: 40, cam: {yaw: 0, pitch: 1.2, dist: 16},
    controls: [{id: 'k', en: 'Gauss-Newton iteration', ko: 'Gauss-Newton 반복', min: 0, max: 6, step: 1, auto: t => Math.min(6, Math.floor(t / 11 * 7))}],
  }, (s, t, m) => {
    if (!PGS) { PGS = [X0]; for (let i = 0; i < 6; i++) PGS.push(gaussNewton(PGS[i])); }
    const X = PGS[s.v.k];
    s.poly([[-1.5, -1.5, -.02], [6.5, -1.5, -.02], [6.5, 6.5, -.02], [-1.5, 6.5, -.02]], '--line', {a: .15});
    s.points(TRUTH.map(p => [p[0], p[1], .02]), '--ok', 3, {bias: -1});
    s.path(X.map(p => [p[0], p[1], .04]), '--pf', 2.5);
    X.forEach(p => s.box([p[0], p[1], .06], [.14, .09, .05], R.rz(p[2]), '--pf'));
    s.line([X[20][0], X[20][1], .06], [X[0][0], X[0][1], .06], '--bad', 3, {front: true});
    s.dot([X[0][0], X[0][1], .1], '--fg', 6, {ring: true, front: true}); s.label([X[0][0], X[0][1], 0], m.t('start', '출발'), '--mut', 14, 'center', 0, 20);
    const gap = Math.hypot(X[20][0] - X[0][0], X[20][1] - X[0][1]);
    s.text(14, 24, m.t(`iteration ${s.v.k}, cost ${cost(X).toFixed(0)}`, `반복 ${s.v.k}회, cost ${cost(X).toFixed(0)}`), '--fg', 15);
    s.text(14, 44, m.t(`end is ${gap.toFixed(2)} m from the start`, `끝이 출발점에서 ${gap.toFixed(2)} m`), gap < .2 ? '--ok' : '--bad', 15);
    s.text(14, 64, m.t(`rms position error ${ate(X).toFixed(2)} m`, `rms 위치 오차 ${ate(X).toFixed(2)} m`), ate(X) < .2 ? '--ok' : '--bad', 15);
  });
})();
