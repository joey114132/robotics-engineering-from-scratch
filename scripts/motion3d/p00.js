// Phase 00: URDF의 parent-frame origin과 joint axis로 link tree를 그린다.
(() => {
  const R = window.M3D, I = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  // Exact fields from 00/03 code/main.py URDF; fixed joints have no motion axis.
  const joints = [
    { name: 'shoulder', parent: 'base', child: 'upper', xyz: [0, 0, .1], yaw: 1.5707963, axis: [0, 0, 1] },
    { name: 'elbow', parent: 'upper', child: 'fore', xyz: [.3, 0, 0], yaw: 0, axis: [0, 0, 1] },
    { name: 'wrist', parent: 'fore', child: 'hand', xyz: [.2, 0, 0], yaw: 0 },
    { name: 'cam_mount', parent: 'upper', child: 'camera', xyz: [0, 0, .05], yaw: 0 },
  ];
  function model(shoulder, elbow) {
    const positions = { base: [0, 0, 0] }, rotations = { base: I }, axes = {};
    const angles = { shoulder, elbow };
    for (const j of joints) {
      const parentR = rotations[j.parent], originR = R.mm(parentR, R.rz(j.yaw));
      positions[j.child] = R.add(positions[j.parent], R.mv(parentR, j.xyz));
      if (j.axis) axes[j.name] = R.mv(originR, j.axis);
      rotations[j.child] = j.axis ? R.mm(originR, R.rz(angles[j.name])) : originR;
    }
    return { positions, rotations, axes };
  }
  window.MOTION.three('urdf-tree-3d', {
    en: 'URDF link tree with joint origins and axes in their parent frames',
    ko: '부모 frame을 기준으로 joint origin과 axis를 그린 URDF link tree입니다',
    cap: ['The lesson URDF has a labelled base → upper → fore → hand chain and a separate green camera branch. Each link has its own colour. A leader identifies the fixed camera mount above the shoulder. Each origin is transformed by its parent pose before the joint turns. Thick blue arrows show revolute axes; the wrist and camera mount are fixed. Thin x/y/z arrows show each joint frame.',
      '수업 URDF의 base → upper → fore → hand 연결과 초록색 camera branch를 각각 라벨로 표시합니다. Link마다 색을 나누고 shoulder 위의 고정 camera mount는 안내선으로 짚습니다. 부모 pose로 origin을 옮긴 뒤 joint를 돌립니다. 굵은 파란 화살표는 revolute axis입니다. Wrist와 camera mount는 고정이며 가는 x/y/z 화살표는 각 joint frame입니다.'],
    period: 12, rest: 4, H: 400, unit: 330, look: [0, 0, .1], oy: 25,
    cam: { yaw: -.5, pitch: .65, dist: 7 }, model,
    controls: [
      { id: 'shoulder', en: 'shoulder', ko: 'shoulder', min: -3, max: 3, step: .01, dec: 2, unit: ' rad', auto: t => .7 * Math.sin(2 * Math.PI * t / 12) },
      { id: 'elbow', en: 'elbow', ko: 'elbow', min: -1, max: 1, step: .01, dec: 2, unit: ' rad', val: .6 },
    ],
  }, (s, t, m) => {
    const a = model(s.v.shoulder, s.v.elbow), p = a.positions;
    // Keep a fixed framing over the whole legal joint range (reach <= 0.5 m).
    const colors = { upper: '--mut', fore: '--pf', hand: '--bad', camera: '--ok' };
    s.box(p.base, [.045, .045, .018], I, '--mut');
    for (const j of joints) {
      const o = p[j.child], r = a.rotations[j.child], color = colors[j.child];
      s.line(p[j.parent], o, color, j.child === 'camera' ? 9 : 8, { front: j.child === 'camera' });
      s.dot(o, color, 5, { ring: true });
      for (let k = 0; k < 3; k++) {
        const v = [0, 0, 0]; v[k] = .045;
        s.arrow(o, R.add(o, R.mv(r, v)), ['--bad', '--ok', '--pd'][k], 1.5);
      }
      if (j.axis) s.arrow(o, R.add(o, R.mul(a.axes[j.name], .075)), '--acc', 3);
    }
    s.box(p.camera, [.032, .024, .024], a.rotations.camera, '--ok');
    // Keep fix8's anchor offsets; place 23px padded boxes afresh in priority order.
    const yaw = s.cam?.yaw ?? -.5, pitch = s.cam?.pitch ?? .65;
    const view = R.mm(R.rx(pitch), R.rz(yaw)), inverse = R.mm(R.rz(-yaw), R.rx(-pitch));
    const placed = [], labels = [
      [p.base, -18, 28, 'base', '--mut', 'right'],
      [p.camera, -44, 33, 'camera', '--ok', 'right', true],
      [p.hand, -42, -5, 'hand', '--pd', 'right', true],
      [R.mul(R.add(p.upper, p.fore), .5), 80, 53, 'upper', '--pf', 'left', true],
      [R.mul(R.add(p.fore, p.hand), .5), 18, -40, 'fore', '--bad', 'center'],
    ];
    for (const [anchor, dx, dy, text, color, align, leader] of labels) {
      const q = R.mv(view, R.sub(anchor, [0, 0, .1])), scale = 330 * 7 / (7 + q[1]);
      const originY = 225 - scale * q[2];
      const x = 240 + scale * q[0] + dx, start = originY + dy, width = text.length * 10;
      const left = x - (align === 'right' ? width : align === 'center' ? width / 2 : 0) - 3, right = left + width + 6;
      let y = start, step = 23;
      while (placed.some(b => left <= b[1] && right >= b[0] && y - 19 <= b[3] && y + 4 >= b[2])) {
        y += step;
        if (y + 4 > 400) { step = -23; y = start - 23; }
      }
      placed.push([left, right, y - 19, y + 4]);
      if (leader || y !== start) {
        const endY = align === 'center' ? y + (y < originY ? 8 : -24) : y - 5;
        const endX = dx + (align === 'right' ? 8 : align === 'left' ? -8 : 0);
        const end = R.add(anchor, R.mv(inverse, [endX / scale, 0, -(endY - originY) / scale]));
        s.line(anchor, end, color, 1.5, { front: true });
      }
      s.label(anchor, text, color, 16, align, dx, y - originY);
    }
    s.text(14, 24, 'base → upper → fore → hand', '--fg', 15);
    s.text(14, 45, m.t('upper → camera (fixed branch)', 'upper → camera (고정 branch)'), '--ok', 15);
    s.text(14, 66, m.t('blue: joint axis; dots: origins', '파랑: joint axis, 점: origin'), '--acc', 15);
    s.text(14, 363, `shoulder ${s.v.shoulder.toFixed(2)} / elbow ${s.v.elbow.toFixed(2)} rad`, '--mut', 15);
  });
})();
