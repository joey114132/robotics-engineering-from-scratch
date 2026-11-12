// 3D widgets for phase 11 (contact and manipulation): grasp-hull-3d
// The planar wrench space (fx, fy, torque) is 3-D. Two jaws on a box of width 2, mu = 0.3, jaw offset d (the lesson's figure): four edge wrenches, their hull, and the origin.
(() => {
  const R = window.M3D, MU = .3, seg = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));
  const wrenches = d => { const W = []; [[-1, 0, 1], [1, d, -1]].forEach(([px, py, nx]) => [-1, 1].forEach(sg => { const fx = nx, fy = sg * MU * nx; W.push([fx, fy, px * fy - py * fx]); })); return W; };
  // largest ball around the origin inside the hull of the 4 wrenches (code/main.py epsilon); 0 when the origin is outside or the hull is flat
  const epsilon = W => { let best = 1e9;
    for (let l = 0; l < 4; l++) { const [i, j, k] = [0, 1, 2, 3].filter(q => q !== l), n = R.cross(R.sub(W[j], W[i]), R.sub(W[k], W[i])), L = Math.hypot(...n); if (L < 1e-9) return 0;
      let q = R.dot(n, W[i]) / L; if (R.dot(n, W[l]) / L - q > 0) q = -q; best = Math.min(best, q); }
    return Math.max(best, 0); };
  window.MOTION.three('grasp-hull-3d', {
    en: 'The hull of the contact wrenches in (fx, fy, torque) space. The grasp closes while the origin is inside the hull; sliding one jaw up pushes the origin out',
    ko: '접촉 wrench를 (fx, fy, torque) 공간에 놓고 그 볼록 껍질을 그렸습니다. 원점이 껍질 안에 있으면 파지가 닫히고 한쪽 jaw를 올리면 원점이 껍질 밖으로 밀려납니다',
    cap: ['Two jaws on a box of width 2 with mu = 0.3 give four friction-cone edge wrenches. The grasp closes while the origin is inside their hull, and the quality epsilon is the distance to the nearest face. Orbit to see the origin leave the hull at offset 2 mu = 0.6.',
      '폭 2인 상자를 mu = 0.3으로 두 jaw가 잡으면 마찰 원뿔의 가장자리 wrench가 네 개 생깁니다. 원점이 이 껍질 안에 있는 동안 파지가 닫히고 품질 epsilon은 가장 가까운 면까지의 거리입니다. 돌려 보면 offset이 2 mu = 0.6을 넘을 때 원점이 껍질 밖으로 나가는 것이 보입니다.'],
    period: 12, rest: 11, cam: { yaw: .75, pitch: .35, dist: 7 }, unit: 92, oy: 44,
    controls: [{ id: 'd', en: 'jaw offset d', ko: 'jaw offset d', min: 0, max: 1, step: .01, dec: 2, auto: t => .8 * seg(t, 1, 10) }],
  }, (s, t, m) => {
    const W = wrenches(s.v.d), eps = epsilon(W), ok = eps > 1e-9, c = ok ? '--ok' : '--bad';
    [['fx', [1.5, 0, 0]], ['fy', [0, 1.5, 0]], [m.t('torque', '토크'), [0, 0, 1.5]]].forEach(([n, v]) => { s.arrow([0, 0, 0], v, '--mut', 1.5); s.label(v, n, '--mut', 15, 'center', 0, -6); });
    [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]].forEach(f => s.poly(f.map(i => W[i]), c, { a: .24, edge: c, w: 1.8 }));
    W.forEach(w => s.dot(w, c, 5));
    s.dot([0, 0, 0], '--fg', 7, { ring: true, front: true });
    s.text(14, 24, m.t(`jaw offset d = ${s.v.d.toFixed(2)}, limit 2 mu = ${(2 * MU).toFixed(2)}`, `jaw offset d = ${s.v.d.toFixed(2)}, 한계 2 mu = ${(2 * MU).toFixed(2)}`), '--fg', 15);
    s.text(14, 44, `epsilon = ${eps.toFixed(3)}`, c, 15);
    s.text(14, 64, ok ? m.t('closes: the origin is inside the hull', '닫힘: 원점이 껍질 안에 있습니다') : m.t('opens: some twist is not resisted', '열림: 버티지 못하는 비틀림이 있습니다'), c, 15);
  });
})();

// 11단계 3D 추가: 기울어지는 경사면과 마찰 원뿔, 스프링 표면을 누르는 probe의 위치/힘 제어, wrist compliance에 따른 peg jam.
(() => {
  const R = window.M3D, PI = Math.PI, G = 9.81, I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];

  // ---- 11/01 contact models: a block on a tilting tray, tan(theta) against mu ----
  window.MOTION.three('tilting-ramp-cone-3d', {
    en: 'A tool lies on a tray that tilts. It stays put while the upward support force still fits inside the friction cone, and slides the moment it does not',
    ko: '도구가 놓인 쟁반을 기울입니다. 위로 받치는 힘이 마찰 원뿔 안에 들어오는 동안은 가만히 있고 벗어나는 순간 미끄러집니다',
    cap: ['The block holds while tan(theta) is at most mu, which is the lesson test. The cone around the surface normal has half-angle atan(mu); gravity needs an upward support force, tilted by theta from the normal, so it fits inside the cone exactly when theta is below atan(mu). With mu = 0.5 the limit is 26.6 deg, so 15 and 25 deg hold while 28 and 35 deg slide with a = g (sin theta - mu cos theta), 1.61 m/s^2 at 35 deg. Sliding is drawn with that closed-form acceleration, not with the penalty simulation of the lesson, and the cone is a flat section of the 3D cone.',
      'tan(theta)가 mu 이하이면 블록이 버티며 이것이 lesson의 판정식입니다. 표면 법선 둘레의 원뿔은 반각이 atan(mu)이고 중력에 맞서려면 위쪽으로 받치는 힘이 필요한데 이 힘은 법선에서 theta만큼 기울어 있으므로 theta가 atan(mu)보다 작을 때만 원뿔 안에 들어갑니다. mu = 0.5이면 한계는 26.6도라서 15도와 25도는 버티고 28도와 35도는 a = g (sin theta - mu cos theta)로 미끄러지며 35도에서 1.61 m/s^2입니다. 미끄러지는 모습은 lesson의 penalty simulation이 아니라 이 닫힌 식의 가속도로 그렸고 원뿔은 3D 원뿔의 평면 단면입니다.'],
    period: 16, rest: 2, H: 340, unit: 92, look: [0, 0, .1], oy: 30,
    cam: {yaw: .2, pitch: .2, dist: 7},
    controls: [{id: 'deg', en: 'tray tilt', ko: '쟁반 기울기', min: 0, max: 45, step: 1, unit: '°', auto: t => 8 + 33 * (.5 - .5 * Math.cos(2 * PI * t / 16))},
      {id: 'mu', en: 'friction mu', ko: '마찰 계수 mu', min: .2, max: .8, step: .05, dec: 2, val: .5}],
  }, (s, t, m) => {
    const th = s.v.deg * PI / 180, mu = s.v.mu, slide = Math.tan(th) > mu, a = G * (Math.sin(th) - mu * Math.cos(th)), phi = Math.atan(mu);
    const d = [Math.cos(th), 0, -Math.sin(th)], n = [Math.sin(th), 0, Math.cos(th)], Rt = R.ry(th);
    const tau = t % 3.6, run = slide ? Math.min(1.15, -1.1 + .5 * a * tau * tau) : -1.1, P = R.mul(d, run), c = slide ? '--bad' : '--ok';
    s.poly([[-2, -.9, -.62], [2, -.9, -.62], [2, .9, -.62], [-2, .9, -.62]], '--card', {a: 1, edge: '--pd', w: 1.5});
    s.box([0, 0, -.32], [.07, .22, .3], I3, '--pd');
    s.box(R.mul(n, -.04), [1.45, .45, .04], Rt, '--pf');
    s.box(R.add(R.add(P, R.mul(n, .06)), R.mul(d, .0)), [.2, .09, .05], Rt, '--pl');
    s.box(R.add(R.add(P, R.mul(n, .06)), R.mul(d, .17)), [.07, .04, .025], Rt, '--fg');
    const e1 = [Math.sin(th - phi), 0, Math.cos(th - phi)], e2 = [Math.sin(th + phi), 0, Math.cos(th + phi)], base = R.add(P, R.mul(n, .08));
    s.poly([base, R.add(base, R.mul(e1, .8)), R.add(base, R.mul(e2, .8))], c, {a: .22, edge: c, w: 1.6});
    s.line(base, R.add(base, R.mul(n, .8)), '--mut', 1.4, {dash: [4, 3]});
    s.arrow(base, R.add(base, [0, 0, .8]), '--fg', 3.2, {front: true});
    s.label(R.add(base, [0, 0, .8]), m.t('support force needed', '받쳐야 하는 힘'), '--fg', 15, 'left', 8, -8);
    s.label(R.add(base, R.mul(e2, .85)), m.t('friction cone', '마찰 원뿔'), c, 15, 'left', 6, 16);
    s.text(14, 24, m.t(`tilt ${s.v.deg.toFixed(0)}°, mu ${mu.toFixed(2)}: tan = ${Math.tan(th).toFixed(3)}`, `기울기 ${s.v.deg.toFixed(0)}°, mu ${mu.toFixed(2)}: tan = ${Math.tan(th).toFixed(3)}`), '--fg', 15);
    s.text(14, 44, m.t(`limit atan(mu) = ${(phi * 180 / PI).toFixed(1)}°`, `한계 atan(mu) = ${(phi * 180 / PI).toFixed(1)}°`), '--mut', 15);
    s.text(14, 64, slide ? m.t(`slides, a = ${a.toFixed(2)} m/s²`, `미끄러짐, a = ${a.toFixed(2)} m/s²`) : m.t('stays: support force is inside the cone', '정지: 받치는 힘이 원뿔 안에 있습니다'), c, 15);
  });

  // ---- 11/02 force and hybrid control: position mode trusts the surface, force mode measures it ----
  const FD = 10, K_EST = 5000, X_EST = .1, XS = .1004, KI = .01, VMAX = .01, KPOS = 20, DTP = 1e-3, NP = 3000, SC = 60, cacheP = {};
  function probe(mode, ke) {
    const xs = new Float32Array(NP), fs = new Float32Array(NP); let x = .09;
    for (let i = 0; i < NP; i++) {
      const f = ke * Math.max(x - XS, 0), v = mode === 'position' ? KPOS * (X_EST + FD / K_EST - x) : KI * (FD - f);
      x += Math.max(-VMAX, Math.min(VMAX, v)) * DTP; xs[i] = x; fs[i] = f;
    }
    return {x: xs, f: fs};
  }
  const zOf = x => 1 - (x - .09) * SC;
  function column(s, cx, run, color, label, m) {
    const i = Math.min(NP - 1, Math.floor((run.ph) * 1000)), x = run.x[i], f = run.f[i], top = zOf(Math.max(x, XS)), base = -.5;
    s.box([cx, 0, (top + base) / 2], [.5, .3, (top - base) / 2], I3, '--pd');
    s.box([cx, 0, top + .5], [.08, .08, .5], I3, '--mut');
    s.box([cx, 0, zOf(x) + .05], [.2, .12, .03], I3, color);
    s.box([cx + .75, 0, -.5 + f / 50 * 1.5 / 2 * 1], [.07, .07, Math.max(.001, f / 50 * 1.5 / 2)], I3, color);
    s.line([cx + .6, 0, -.5 + FD / 50 * 1.5], [cx + .9, 0, -.5 + FD / 50 * 1.5], '--fg', 2);
    s.label([cx, 0, 1.55], label, color, 15, 'center');
    s.label([cx + .75, 0, -.7], `${f.toFixed(1)} N`, color, 15, 'center');
    return f;
  }
  window.MOTION.three('probe-sponge-3d', {
    en: 'Two probes press a springy surface toward 10 N. The left one trusts a guessed surface height and stiffness, the right one reads the force and stops when it is right',
    ko: '두 probe가 스프링 같은 표면을 10 N으로 누르려 합니다. 왼쪽은 추정한 표면 높이와 강성을 믿고 오른쪽은 힘을 재서 맞는 순간 멈춥니다',
    cap: ['Lesson 11/02 setup: desired force 10 N, assumed stiffness 5000 N/m, assumed surface at 0.1000 m while the true surface is at 0.1004 m. Position mode drives to the assumed depth and ends at ke times (0.102 - 0.1004), which is 1.6 N at 1000 N/m, 8.0 N at 5000 and 40 N at 25000. Force mode uses velocity proportional to the force error (0.01 m/(N s), speed limit 0.01 m/s) and ends at 10 N whatever the stiffness, but needs more time on a soft surface. Depth is drawn 60x larger than real so a 2 mm error is visible; the probe is an ideal velocity-commanded slider.',
      'Lesson 11/02의 설정입니다. 원하는 힘 10 N, 가정한 강성 5000 N/m, 가정한 표면 위치 0.1000 m이고 실제 표면은 0.1004 m입니다. 위치 모드는 가정한 깊이까지 내려가 ke 곱하기 (0.102 - 0.1004)의 힘으로 끝나며 1000 N/m에서 1.6 N, 5000에서 8.0 N, 25000에서 40 N입니다. 힘 모드는 힘 오차에 비례하는 속도(0.01 m/(N s), 속도 제한 0.01 m/s)를 쓰며 강성과 상관없이 10 N으로 끝나지만 무른 표면에서는 시간이 더 걸립니다. 2 mm 오차가 보이도록 깊이를 실제의 60배로 그렸고 probe는 속도 명령을 그대로 따르는 이상적인 slider입니다.'],
    period: 20, rest: 3, H: 350, unit: 95, look: [0, 0, .45], oy: 50,
    cam: {yaw: .3, pitch: .18, dist: 7},
    controls: [{id: 'lk', en: 'surface stiffness, log10 N/m', ko: '표면 강성, log10 N/m', min: 3, max: 4.4, step: .05, dec: 2, auto: t => 3.7 + .7 * Math.sin(2 * PI * t / 20 - PI / 2)}],
  }, (s, t, m) => {
    const key = Math.round(s.v.lk * 20), ke = Math.pow(10, s.v.lk), ph = Math.min(t % 3.8, NP * DTP - .002);
    const r = cacheP[key] || (cacheP[key] = {pos: probe('position', ke), frc: probe('force', ke)});
    r.pos.ph = r.frc.ph = ph;
    const fp = column(s, -.95, r.pos, Math.abs(r.pos.f[NP - 1] - FD) < 1.5 ? '--ok' : '--bad', m.t('position mode', '위치 모드'), m);
    const ff = column(s, .95, r.frc, Math.abs(r.frc.f[NP - 1] - FD) < 1.5 ? '--ok' : '--bad', m.t('force mode', '힘 모드'), m);
    s.text(14, 24, m.t(`stiffness ${ke.toFixed(0)} N/m, target ${FD} N`, `강성 ${ke.toFixed(0)} N/m, 목표 ${FD} N`), '--fg', 15);
    s.text(14, 44, m.t(`position mode ends at ${r.pos.f[NP - 1].toFixed(1)} N`, `위치 모드는 ${r.pos.f[NP - 1].toFixed(1)} N에서 끝남`), Math.abs(r.pos.f[NP - 1] - FD) < 1.5 ? '--ok' : '--bad', 15);
    s.text(14, 64, m.t(`force mode ends at ${r.frc.f[NP - 1].toFixed(1)} N (t = ${ph.toFixed(1)} s)`, `힘 모드는 ${r.frc.f[NP - 1].toFixed(1)} N에서 끝남 (t = ${ph.toFixed(1)} s)`), '--ok', 15);
  });

  // ---- 11/04 compliance in assembly: a thin peg, two contacts, a wrist spring kx ----
  const PP = {h: 5e-4, L: .05, mu: 0.4, alpha: 3 * PI / 180, e: 1e-3, kth: 1, push: 5};
  const c2 = (a, b) => a[0] * b[1] - a[1] * b[0], cacheG = {};
  function wedge(zt, kx) {
    const {h, L, mu} = PP, th = Math.atan2(2 * h, zt), u = [Math.sin(th), -Math.cos(th)], n2 = [-Math.cos(th), -Math.sin(th)];
    const T = [-h, zt], E = [h, 0], W = [T[0] + L * u[0], T[1] + L * u[1]], Fw = [kx * (PP.e - W[0]), PP.push];
    const wr = [Fw[0], Fw[1], c2([W[0] - T[0], W[1] - T[1]], Fw) + PP.kth * (PP.alpha - th)];
    const wrench = (f, r) => [f[0], f[1], c2(r, f)], ET = [E[0] - T[0], E[1] - T[1]], z0 = [0, 0];
    const edges = [-1, 1].map(sg => wrench([1, sg * mu], z0)).concat([-1, 1].map(sg => wrench([n2[0] + sg * mu * u[0], n2[1] + sg * mu * u[1]], ET)));
    const cc1 = wrench([1, -mu], z0), cc2 = wrench([n2[0] + mu * u[0], n2[1] + mu * u[1]], ET), tau = [0, 1, -2 * h / (zt * zt + 4 * h * h)];
    return {th, wr, edges, cc1, cc2, tau, T, W};
  }
  function solve3(a, b, c, r) {   // columns a, b, c: Cramer's rule
    const D = R.dot(a, R.cross(b, c));
    return Math.abs(D) < 1e-300 ? null : [R.dot(r, R.cross(b, c)) / D, R.dot(a, R.cross(r, c)) / D, R.dot(a, R.cross(b, r)) / D];
  }
  function jammed(wr, edges) {
    for (const idx of [[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]]) {
      const [a, b, c] = idx.map(i => edges[i]);
      if (Math.abs(R.dot(a, R.cross(b, c))) <= 1e-12) continue;
      const x = solve3(a, b, c, wr.map(v => -v));
      if (x && x.every(v => v >= -1e-9)) return true;
    }
    return false;
  }
  function insert(kx) {
    const key = Math.round(Math.log10(kx) * 10); if (cacheG[key]) return cacheG[key];
    let zt = 2 * PP.h / Math.tan(PP.alpha);
    const z0 = zt;
    while (zt < .9 * PP.L) { if (jammed(wedge(zt, kx).wr, wedge(zt, kx).edges)) return cacheG[key] = {z0, jam: zt}; zt += 1e-4; }
    return cacheG[key] = {z0, jam: null, end: .9 * PP.L};
  }
  const SM = .028, XEX = 15;   // world units per mm of depth; lateral exaggeration
  const toW = (x, zt) => [x * 1e3 * XEX * SM, 0, -zt * 1e3 * SM];
  window.MOTION.three('peg-wrist-compliance-3d', {
    en: 'A robot wrist pushes a thin peg into a tight hole. A stiff wrist wedges the peg at a depth and stops; a wrist that gives sideways lets it slide in',
    ko: '로봇 손목이 가는 peg를 꽉 끼는 구멍에 밀어 넣습니다. 손목이 뻣뻣하면 어느 깊이에서 끼어 멈추고 옆으로 조금 물러나 주는 손목은 그대로 들어갑니다',
    cap: ['Lesson 11/04 two-point-contact model: peg length 50 mm, clearance half-width 0.5 mm, friction 0.4, push 5 N, initial tilt 3 deg, wrist torsion 1 Nm/rad and a sideways wrist spring kx. The tip rests on the left wall and the peg leans on the right mouth edge; the peg jams where the contact friction cones can hold the wrist wrench. With kx = 1e5 N/m the lesson jams at 34.6 mm depth; at 1e4, 1e3 and 100 it inserts. Sideways distances are drawn 15x wider than true so the 1 mm gap is visible, which also exaggerates the tilt. The spring is the sideways wrist spring only.',
      'Lesson 11/04의 두 점 접촉 모델입니다. peg 길이 50 mm, 틈 반폭 0.5 mm, 마찰 0.4, 미는 힘 5 N, 처음 기울기 3도, 손목 비틀림 강성 1 Nm/rad이고 옆 방향 손목 spring kx가 있습니다. 끝은 왼쪽 벽에 닿고 peg는 오른쪽 구멍 입구 모서리에 기대며 접촉 마찰 원뿔이 손목 wrench를 버틸 수 있는 깊이에서 끼입니다. kx = 1e5 N/m이면 lesson에서 34.6 mm 깊이에서 끼고 1e4, 1e3, 100에서는 들어갑니다. 1 mm 틈이 보이도록 옆 방향 거리를 실제의 15배로 그렸으며 이 때문에 기울기도 과장됩니다. 그려진 spring은 옆 방향 손목 spring 하나입니다.'],
    period: 20, rest: 6, H: 380, unit: 100, look: [0, 0, -.2], oy: 40,
    cam: {yaw: .06, pitch: .1, dist: 7},
    controls: [{id: 'lk', en: 'wrist stiffness kx, log10 N/m', ko: '손목 강성 kx, log10 N/m', min: 2, max: 5, step: .1, dec: 1, auto: t => 3.5 + 1.5 * Math.cos(2 * PI * t / 20)}],
  }, (s, t, m) => {
    const kx = Math.pow(10, Math.round(s.v.lk * 10) / 10), r = insert(kx), zEnd = r.jam != null ? r.jam : r.end, p = Math.min(1, (t % 6.4) / 4);
    const zt = r.z0 + p * (zEnd - r.z0), w = wedge(zt, kx), stuck = r.jam != null && p >= 1, c = stuck ? '--bad' : '--pl';
    const hw = PP.h * 1e3 * XEX * SM;
    s.box([-hw - .55, 0, -.84], [.55, .22, .84], I3, '--pd'); s.box([hw + .55, 0, -.84], [.55, .22, .84], I3, '--pd');
    const tip = toW(w.T[0], w.T[1]), top = toW(w.W[0], w.W[1]), dx = top[0] - tip[0], dz = top[2] - tip[2], len = Math.hypot(dx, dz);
    s.box([(tip[0] + top[0]) / 2, 0, (tip[2] + top[2]) / 2], [len / 2, .1, .08], R.ry(-Math.atan2(dz, dx)), c);
    s.box([top[0], 0, top[2] + .12], [.2, .14, .1], I3, '--fg');
    s.dot(tip, '--fg', 4, {ring: true, front: true}); s.dot(toW(PP.h, 0), '--fg', 4, {ring: true, front: true});
    const ax = PP.e * 1e3 * XEX * SM, zig = [[ax, 0, top[2] + .12]];
    for (let i = 1; i <= 10; i++) zig.push([ax + (top[0] - ax) * i / 10, (i % 2 ? .1 : -.1) * (i < 10), top[2] + .12]);
    s.path(zig, '--ok', 2.4, {front: true});
    s.box([ax, 0, top[2] + .12], [.025, .12, .12], I3, '--pd');
    s.arrow([top[0], 0, top[2] + .85], [top[0], 0, top[2] + .36], '--mut', 3);
    s.text(14, 24, m.t(`wrist kx = ${kx >= 1e4 ? (kx / 1e3).toFixed(0) + ' kN/m' : kx.toFixed(0) + ' N/m'}`, `손목 kx = ${kx >= 1e4 ? (kx / 1e3).toFixed(0) + ' kN/m' : kx.toFixed(0) + ' N/m'}`), '--fg', 15);
    s.text(14, 44, m.t(`tip depth ${(zt * 1e3).toFixed(1)} mm; sideways wrist force ${w.wr[0].toFixed(1)} N`, `끝 깊이 ${(zt * 1e3).toFixed(1)} mm, 옆 방향 손목 힘 ${w.wr[0].toFixed(1)} N`), '--mut', 15);
    s.text(14, 64, r.jam != null ? m.t(`jams at ${(r.jam * 1e3).toFixed(1)} mm${stuck ? ': stuck' : ''}`, `${(r.jam * 1e3).toFixed(1)} mm에서 낌${stuck ? ': 멈춤' : ''}`) : m.t('inserts without jamming', '끼지 않고 들어감'), r.jam != null ? '--bad' : '--ok', 15);
  });
})();
