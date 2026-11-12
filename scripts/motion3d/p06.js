// 3D widgets for phase 06 (perception and calibration): pinhole-ray-3d, handeye-twist-3d, depth-cloud-3d
// Camera frame as in the lessons: x right, y down, z forward. The engine's world has z up, so a camera point (x, y, z) is drawn at (x, z, -y).
(() => {
  const R = window.M3D, PI = Math.PI, rad = d => d * PI / 180, seg = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));
  const mk = (cx, cy, cz) => c => [c[0] - cx, c[2] - cz, -(c[1] - cy)];

  // ---- 06-01 pinhole: a pixel is a ray; the depth picks the point on it (fx = fy = 600, principal point (320, 240) as in the lesson's example) ----
  const FX = 600, CX = 320, CY = 240, ZC = 2;
  window.MOTION.three('pinhole-ray-3d', {
    en: 'A camera, its image plane and the ray through one pixel. A wrong depth slides the 3D point along the ray, away from the cup',
    ko: '카메라와 이미지 평면 그리고 픽셀 하나를 지나는 광선입니다. 깊이가 틀리면 3D 점이 광선을 따라 미끄러져 컵에서 멀어집니다',
    cap: ['A pixel is a ray; depth picks the point on it. The cup is at 2 m (an example value). A depth error dz moves the point along the ray, sideways by dz (u - cx) / fx, and more the further the pixel is from the image centre.',
      '픽셀은 광선이고 깊이가 그 위의 점을 고릅니다. 컵은 2 m에 있습니다(예시 값입니다). 깊이 오차 dz는 점을 광선 방향으로 옮기고 옆으로는 dz (u - cx) / fx만큼 어긋나며 픽셀이 이미지 중심에서 멀수록 커집니다.'],
    period: 12, rest: 9, cam: { yaw: 1.2, pitch: .42, dist: 7 }, unit: 88, oy: 40,
    controls: [{ id: 'z', en: 'depth read', ko: '읽은 깊이', min: .5, max: 4, step: .01, dec: 2, unit: ' m', auto: t => 2 + 1.5 * Math.sin(2 * PI * t / 12) },
      { id: 'u', en: 'pixel column u', ko: '픽셀 열 u', min: 320, max: 620, step: 1, val: 520 }],
  }, (s, t, m) => {
    const D = mk(0, 0, 2), a = (s.v.u - CX) / FX, dir = [a, 0, 1], at = z => [a * z, 0, z], P = at(s.v.z), Pc = at(ZC);
    const plane = [[-CX / FX, -CY / FX, 1], [CX / FX, -CY / FX, 1], [CX / FX, CY / FX, 1], [-CX / FX, CY / FX, 1]];
    s.line(D([0, 0, 0]), D([0, 0, 4.4]), '--line', 1.5, { dash: [4, 4] });
    s.poly(plane.map(D), '--pf', { a: .14, edge: '--pf', w: 1.5 });
    plane.forEach(c => s.line(D([0, 0, 0]), D(c), '--line', 1.2));
    s.dot(D([0, 0, 0]), '--fg', 5, { ring: true }); s.label(D([0, 0, 0]), m.t('camera', '카메라'), '--mut', 15, 'center', 0, -10);
    s.label(D([CX / FX, -CY / FX, 1]), m.t('image', '이미지'), '--mut', 15, 'left', 6, -6);
    s.line(D([0, 0, 0]), D(at(4.2)), '--pd', 2.5);
    s.dot(D(dir), '--pd', 6, { ring: true, front: true });
    s.box(D(Pc), [.1, .1, .1], [[1, 0, 0], [0, 1, 0], [0, 0, 1]], '--ok', { a: .8 }); s.label(D(Pc), m.t('cup', '컵'), '--ok', 15, 'center', 0, 26);
    s.line(D(Pc), D(P), '--bad', 2.5, { front: true }); s.dot(D(P), '--bad', 7, { ring: true, front: true });
    const side = Math.abs(P[0] - Pc[0]);
    s.text(14, 24, m.t(`pixel (${s.v.u}, ${CY}), depth ${s.v.z.toFixed(2)} m`, `픽셀 (${s.v.u}, ${CY}), 깊이 ${s.v.z.toFixed(2)} m`), '--fg', 15);
    s.text(14, 44, m.t(`point (${P[0].toFixed(2)}, ${P[1].toFixed(2)}, ${P[2].toFixed(2)}) m`, `점 (${P[0].toFixed(2)}, ${P[1].toFixed(2)}, ${P[2].toFixed(2)}) m`), '--mut', 15);
    s.text(14, 64, m.t(`sideways error ${(side * 1000).toFixed(0)} mm`, `옆으로 어긋남 ${(side * 1000).toFixed(0)} mm`), '--bad', 15);
    s.text(14, 84, m.t(`0.5 px at this depth: ${(s.v.z * .5 / FX * 1000).toFixed(1)} mm`, `이 깊이에서 0.5 px: ${(s.v.z * .5 / FX * 1000).toFixed(1)} mm`), '--mut', 15);
  });

  // ---- 06-04 hand-eye: the rotation axes of the calibration motions. alpha = R_X beta, so a twist about the common axis changes nothing when all axes are parallel ----
  const N = 8, AX = ang => Array.from({ length: N }, (_, i) => { const f = i * 2 * PI / N + .3; return [Math.sin(ang) * Math.cos(f), Math.sin(ang) * Math.sin(f), Math.cos(ang)]; });
  window.MOTION.three('handeye-twist-3d', {
    en: 'Rotation axes of eight calibration motions as arrows from one point. A twist about z of the camera-to-gripper rotation changes nothing when all axes are parallel and is rejected when they are spread',
    ko: '보정 동작 여덟 개의 회전축을 한 점에서 뻗는 화살표로 그렸습니다. 모든 축이 평행하면 카메라와 그리퍼 사이 회전을 z축으로 비틀어도 달라지는 것이 없고 축이 퍼져 있으면 그 비틀림이 걸러집니다',
    cap: ['Solid arrows are the gripper rotation axes. Dashed arrows are what a twisted calibration (R_X turned about z) predicts for the same motions. With one axis the two sets coincide for every twist, so the twist cannot be found; with spread axes they separate.',
      '실선 화살표는 그리퍼의 회전축입니다. 점선 화살표는 R_X를 z축으로 비튼 보정이 같은 동작에 대해 예측하는 축입니다. 축이 하나뿐이면 어떤 비틀림에서도 두 묶음이 겹쳐서 비틀림을 알 수 없고 축이 퍼져 있으면 두 묶음이 갈라집니다.'],
    period: 12, rest: 9, cam: { yaw: .5, pitch: .5, dist: 7 }, unit: 96,
    controls: [{ id: 'psi', en: 'axis spread', ko: '축의 퍼짐', min: 0, max: 40, step: 1, unit: '°', auto: t => t < 6 ? 0 : 30 },
      { id: 'th', en: 'twist of R_X about z', ko: 'R_X의 z축 비틀림', min: -90, max: 90, step: 1, unit: '°', auto: t => 70 * Math.sin(2 * PI * t / 6 + 1) }],
  }, (s, t, m) => {
    const al = AX(rad(s.v.psi)), Rz = R.rz(rad(s.v.th)), pr = al.map(v => R.mv(Rz, v)), O = [0, 0, 0];
    const err = Math.sqrt(al.reduce((e, v, i) => e + R.dot(R.sub(pr[i], v), R.sub(pr[i], v)), 0) / N);
    const C = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]; al.forEach(v => { for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) C[i][j] += v[i] * v[j]; });
    const w = R.eig3(C).w, ratio = Math.max(0, w[2]) / w[0];
    for (const [ax, ex] of [[0, 1], [1, 0]]) { const r = []; for (let i = 0; i <= 56; i++) { const a = i / 56 * 2 * PI; r.push(ax ? [Math.cos(a), 0, Math.sin(a)] : [Math.cos(a), Math.sin(a), 0]); } s.path(r, '--line', 1.5); }
    s.line([0, 0, -1.1], [0, 0, 1.4], '--mut', 1.2, { dash: [4, 4] });
    pr.forEach(v => s.arrow(O, R.mul(v, 1.15), '--pd', 2, { dash: [5, 4], a: .9 }));
    al.forEach(v => s.arrow(O, R.mul(v, 1.15), '--pf', 3.5, { front: true }));
    s.dot(O, '--fg', 5, { ring: true });
    s.text(14, 24, m.t(`smallest / largest singular value ${ratio.toFixed(3)}`, `가장 작은 / 가장 큰 특이값 ${ratio.toFixed(3)}`), '--fg', 15);
    s.text(14, 44, m.t(`axes differ by ${err.toFixed(3)} at twist ${s.v.th}°`, `비틀림 ${s.v.th}°에서 축 차이 ${err.toFixed(3)}`), '--mut', 15);
    s.text(14, 64, err < .02 ? m.t('this twist cannot be told from the true one', '이 비틀림은 참값과 구별되지 않습니다') : m.t('this twist is rejected by the data', '이 비틀림은 데이터가 걸러냅니다'), err < .02 ? '--bad' : '--ok', 15);
  });

  // ---- 06-03 depth to cloud: the lesson's scene (tilted table n.X = 1 m, box 0.2 m nearer, noise 0.003, 2 percent flyers) sampled every 4th pixel ----
  const TN = [0, .5, Math.sqrt(.75)], K = [150, 150, 80, 60], THR = .012, ROUNDS = 12;
  const rng = seed => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const fit = Q => { const c = Q.reduce((a, p) => R.add(a, p), [0, 0, 0]).map(x => x / Q.length), C = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
    Q.forEach(p => { const d = R.sub(p, c); for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) C[i][j] += d[i] * d[j]; });
    let n = R.eig3(C).v[2], d = R.dot(n, c); if (d < 0) { n = n.map(x => -x); d = -d; } return [n, d]; };   // least squares plane n.X = d, smallest eigenvector of the scatter
  let scene = null;
  const build = (s1 = 5, s2 = 3) => {
    const r = rng(s1), g = () => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * PI * r()), P = [];
    for (let v = 0; v < 120; v += 4) for (let u = 0; u < 160; u += 4) {
      const ray = [(u - K[2]) / K[0], (v - K[3]) / K[1], 1]; let z = 1 / R.dot(ray, TN);
      if (v >= 40 && v < 80 && u >= 60 && u < 110) z -= .2;
      z += .003 * g(); if (r() < .02) z = .3 + 2.7 * r();
      P.push([ray[0] * z, ray[1] * z, z]);
    }
    const rr = rng(s2), best = []; let top = -1, topN = 0, topPlane = null;
    for (let k = 0; k < ROUNDS; k++) {   // RANSAC: three random points, a plane, the points within THR; keep the best round so far
      const i = []; while (i.length < 3) { const j = Math.floor(rr() * P.length); if (!i.includes(j)) i.push(j); }
      const [a, b, c] = i.map(j => P[j]), n0 = R.cross(R.sub(b, a), R.sub(c, a)), L = Math.hypot(...n0);
      if (L > 1e-9) { const n = n0.map(x => x / L), cnt = P.reduce((q, p) => q + (Math.abs(R.dot(R.sub(p, a), n)) < THR), 0); if (cnt > topN) { topN = cnt; top = k; topPlane = [n, a]; } }
      best.push({ top, topN, topPlane });
    }
    const memo = {}, refit = k => memo[k] || (memo[k] = (() => { const b = best[k]; if (b.top < 0) return null; const inl = P.filter(p => Math.abs(R.dot(R.sub(p, b.topPlane[1]), b.topPlane[0])) < THR), [n, d] = fit(inl); return { n, d, inl: P.map(p => Math.abs(R.dot(p, n) - d) < THR) }; })());
    const ls = fit(P); return { P, ls, refit, best };
  };
  const tilt = n => Math.acos(Math.min(1, Math.abs(R.dot(n, TN)))) * 180 / PI;
  window.MOTION.three('depth-cloud-3d', {
    en: 'A depth image unprojected into a 3D cloud: a tilted table, a box on it and a few flyers. The least-squares plane leans toward the box, the RANSAC plane follows the table',
    ko: '깊이 이미지를 3D 점군으로 바꾼 장면입니다. 기울어진 탁자 위에 상자가 있고 튀는 점이 조금 있습니다. 최소제곱 평면은 상자 쪽으로 기울고 RANSAC 평면은 탁자를 따라갑니다',
    cap: ['The lesson scene sampled every 4th pixel: a table, a box 0.2 m nearer to the camera, and garbage depth on 2 percent of pixels. Each RANSAC round fits a plane to 3 random points and keeps the plane with the most points within 12 mm.',
      '레슨의 장면을 4픽셀마다 한 점씩 뽑았습니다. 탁자와 카메라 쪽으로 0.2 m 나온 상자가 있고 2퍼센트의 픽셀은 깊이 값이 엉터리입니다. RANSAC은 한 번에 임의의 점 3개로 평면을 만들고 12 mm 안에 점이 가장 많은 평면을 남깁니다.'],
    period: 12, rest: 11, cam: { yaw: .7, pitch: .45, dist: 7 }, unit: 104, oy: 30,
    controls: [{ id: 'k', en: 'RANSAC rounds', ko: 'RANSAC 횟수', min: 0, max: ROUNDS, step: 1, auto: t => Math.round(ROUNDS * seg(t, 1, 8)) }, { id: 'ls', toggle: true, en: 'Show the least-squares plane', ko: '최소제곱 평면 보기', val: true }],
  }, (s, t, m) => {
    scene = scene || build();
    const D = mk(0, 0, 1.15), k = s.v.k, fitR = k ? scene.refit(k - 1) : null, ctr = [[-.45, -.35], [.55, -.35], [.55, .45], [-.45, .45]];
    const quad = (n, d) => ctr.map(([x, y]) => D([x, y, (d - n[0] * x - n[1] * y) / n[2]]));
    if (s.v.ls) s.poly(quad(...scene.ls), '--bad', { a: .22, edge: '--bad', w: 2 });
    if (fitR) s.poly(quad(fitR.n, fitR.d), '--ok', { a: .26, edge: '--ok', w: 2 });
    const P = scene.P, inl = fitR ? fitR.inl : null;
    s.points(P.filter((_, i) => !inl || inl[i]).map(D), inl ? '--ok' : '--pl', 2.2);
    if (inl) s.points(P.filter((_, i) => !inl[i]).map(D), '--bad', 2.2);
    s.dot(D([0, 0, 0]), '--fg', 5, { ring: true }); s.label(D([0, 0, 0]), m.t('camera', '카메라'), '--mut', 15, 'center', 0, -10);
    const nn = fitR ? fitR.inl.filter(Boolean).length : 0;
    const w = scene.best[ROUNDS - 1].topN / P.length, need = Math.ceil(Math.log(.01) / Math.log(1 - w ** 3));   // the lesson's N = log(1 - p) / log(1 - w^3), p = 0.99
    s.text(14, 24, m.t(`RANSAC round ${k} / ${ROUNDS}: ${nn} points within 12 mm`, `RANSAC ${k} / ${ROUNDS}회: 12 mm 안의 점 ${nn}개`), '--fg', 15);
    s.text(14, 44, m.t(`least squares plane tilt: ${tilt(scene.ls[0]).toFixed(1)}°`, `최소제곱 평면의 기울기 오차: ${tilt(scene.ls[0]).toFixed(1)}°`), '--bad', 15);
    s.text(14, 64, fitR ? m.t(`RANSAC plane tilt: ${tilt(fitR.n).toFixed(2)}°`, `RANSAC 평면의 기울기 오차: ${tilt(fitR.n).toFixed(2)}°`) : m.t('RANSAC: no plane yet', 'RANSAC: 아직 평면 없음'), fitR ? '--ok' : '--mut', 15);
    s.text(14, 84, m.t(`inlier fraction ${(w * 100).toFixed(0)}%: 99% needs ${need} rounds`, `inlier 비율 ${(w * 100).toFixed(0)}%: 99%에는 ${need}회가 필요합니다`), '--mut', 15);
  });
})();
