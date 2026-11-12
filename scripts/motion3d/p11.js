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
