// phase 11 concept animations (480x270) on the window.MB kit; one micro-story each
(function () {
 const R = window.MOTION, K = window.MB; if (!K) return;
 const {$, A, RR, CC, fin, cl, hd} = K, DA = 'stroke-dasharray';
 const T = (m, p, x, y, en, ko, c, an) => K.T(m, p, x, y, en, ko, c, an, 15);
 const D = (p, x, y, c, an) => {const e = $(p, 'text', {x, y, 'font-size': 15, class: c || '', 'text-anchor': an || 'start'}); let l = ''; const f = s => {if (s !== l) e.textContent = l = s;}; f.e = e; return f;};
 const stage = (m, en, ko) => {const g = K.stage(m, en, ko, 480, 270); m.caption(en, ko); m.replayButton(); return g;};
 const LN = (p, a, b, c, d, k) => $(p, 'path', {d: `M${a} ${b}L${c} ${d}`, class: 's n ' + k});

 // 11/02: the same depth command on three surfaces; lesson probe() laws, dt = 1 ms
 R.gs('force-loop-surface-swap', (el, m) => {
  const g = stage(m, 'The same depth command on three surfaces (ke = 1000, 5000, 25000 N/m). Position control presses 1.6, 8 and 40 N; the force loop returns to 10 N every time.', '같은 깊이 명령을 세 표면에 줍니다(ke = 1000, 5000, 25000 N/m). position 제어는 1.6, 8, 40 N으로 누르고 힘 루프는 매번 10 N으로 돌아옵니다.');
  const KE = [1e3, 5e3, 2.5e4], XS = .1004, X = [[], []], F = [[], []]; let a = .09, b = .09;
  for (let i = 0; i < 10200; i++) {
   const ke = KE[Math.min(2, i / 3400 | 0)], f = [a, b].map(x => ke * Math.max(x - XS, 0));
   X[0].push(a); X[1].push(b); F[0].push(f[0]); F[1].push(f[1]);
   a += cl(20 * (.102 - a), -.01, .01) * 1e-3; b += cl(.01 * (10 - f[1]), -.01, .01) * 1e-3;   // KP (X_EST + FD/K_EST - x), KI (FD - f), speed limit .01
  }
  const cx = [120, 360], tx = D(g, 240, 24, 'm', 'middle'), val = [D(g, 410, 217, 'g'), D(g, 410, 245, 'g')];
  LN(g, 60, 101, 420, 101, 'sm'); g.lastChild.setAttribute(DA, '3 5');
  const u = cx.map((x, c) => {
   RR(g, x - 40, 170, 80, 8, 3, 'f s st'); T(m, g, x, 46, c ? 'force control' : 'position control', c ? '힘 제어' : '위치 제어', 'g', 'middle');
   return [$(g, 'path', {class: 's n sm'}), RR(g, x - 22, 0, 44, 18, 4, 'f s st'), RR(g, 100, 204 + 28 * c, 0, 16, 3, c ? 'k' : 'w')];
  });
  T(m, g, 16, 217, 'position', '위치 제어'); T(m, g, 16, 245, 'force', '힘 제어'); T(m, g, 150, 196, '10 N', '10 N', 'g', 'middle'); LN(g, 150, 199, 150, 250, 'sw');
  const draw = t => {
   const i = cl(Math.round((t - .3) * 1e3), 0, 10199), s = Math.min(2, i / 3400 | 0);
   tx(m.t('surface stiffness ', '표면 강성 ') + KE[s] + ' N/m');
   u.forEach(([sp, tool, bar], c) => {
    const y = 70 + (X[c][i] - .09) * 3000, top = Math.max(y, 101), x = cx[c];
    let d = `M${x} 170`; for (let k = 1; k < 11; k++) d += `L${x + (k % 2 ? 14 : -14)} ${170 + (top - 170) * k / 11}`;
    A(sp, {d: d + `L${x} ${top}`}); sp.style.strokeWidth = [2, 3.5, 5][s]; A(tool, {y: y - 18}); A(bar, {width: F[c][i] * 5}); val[c](F[c][i].toFixed(1) + ' N');
   });
  };
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 11.6); m.play(tl, {rest: 9.9, draw});
 });

 // 11/03: two jaws, mu = 0.3, box 2 wide; epsilon = distance from the origin to the nearest facet of the wrench hull (lesson epsilon())
 R.gs('grasp-slide-jaw', (el, m) => {
  const g = stage(m, 'A box 2 wide, mu = 0.3. Slide the right jaw up: the grasp stays closed while the line between the contacts is inside both friction cones, up to offset 2 mu = 0.6. Past that the box twists out.', '폭 2인 상자, mu = 0.3. 오른쪽 jaw를 올립니다. 두 접촉점을 잇는 선이 두 마찰 원뿔 안에 있는 동안 파지가 닫혀 있고 offset 2 mu = 0.6에서 끝납니다. 그 너머에서는 상자가 돌아 빠집니다.');
  const MU = .3, dot = (u, v) => u[0] * v[0] + u[1] * v[1] + u[2] * v[2];
  const eps = d => {
   const W = []; [[-1, 0, 1], [1, d, -1]].forEach(([px, py, nx]) => [-1, 1].forEach(s => {const fx = nx, fy = s * MU * nx; W.push([fx, fy, px * fy - py * fx]);}));
   let best = 1e9;
   for (let l = 0; l < 4; l++) {
    const [i, j, k] = [0, 1, 2, 3].filter(q => q != l), u = W[j].map((v, q) => v - W[i][q]), w = W[k].map((v, q) => v - W[i][q]);
    let n = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]; const nn = Math.hypot(...n); if (nn < 1e-9) return 0;
    n = n.map(v => v / nn); let q = dot(n, W[i]); if (dot(n, W[l]) - q > 0) q = -q; best = Math.min(best, q);
   }
   return Math.max(best, 0);
  };
  const EP = Array.from({length: 41}, (_, k) => eps(k / 50)), PX = d => 285 + d * 212.5, PY = e => 220 - e * 500, o = {d: 0};
  const bx = $(g, 'g', {}); RR(bx, 60, 80, 140, 140, 6, 'c s st');
  const cone = [0, 1].map(() => $(g, 'polygon', {class: 'k', opacity: .3})), jn = $(g, 'path', {class: 's n w3'}), cs = [60, 200].map(x => CC(g, x, 150, 6, 'g'));
  LN(g, 285, 220, 455, 220, 'sm'); LN(g, 285, 220, 285, 100, 'sm'); LN(g, PX(.6), 100, PX(.6), 220, 'sw'); g.lastChild.setAttribute(DA, '4 4');
  T(m, g, PX(.6), 242, '2 μ', '2 μ', 'm', 'middle'); T(m, g, 370, 262, 'jaw offset', 'jaw offset', 'm', 'middle'); T(m, g, 285, 94, 'ε', 'ε', 'm');
  const cv = $(g, 'path', {class: 's n w3 sf'}), pt = CC(g, 0, 0, 6, 'g'), r1 = D(g, 16, 26, 'g'), r2 = D(g, 16, 50, 'k');
  const draw = () => {
   const d = o.d, e = EP[Math.round(d * 50)], ok = e > 1e-6, yr = 150 - 70 * d, c = ok ? 'k' : 'x';
   A(bx, {transform: ok ? '' : `rotate(${-Math.min(12, (d - .6) * 60)} 130 150)`});
   [[60, 150, 1], [200, yr, -1]].forEach(([x, y, n], q) => A(cone[q], {class: c, points: `${x},${y} ${x + n * 55},${y - 16.5} ${x + n * 55},${y + 16.5}`}));
   A(jn, {d: `M60 150L200 ${yr}`, class: 's n w3 s' + c}); A(cs[1], {cy: yr}); A(pt, {cx: PX(d), cy: PY(e)});
   A(cv, {d: 'M' + EP.slice(0, Math.round(d * 50) + 1).map((v, k) => `${PX(k / 50)} ${PY(v)}`).join('L')});
   r1(m.t('jaw offset ', 'jaw offset ') + d.toFixed(2)); r2(`ε = ${e.toFixed(3)}  ` + (ok ? m.t('closed', '닫힘') : m.t('open: twists out', '열림: 돌아 빠짐'))); A(r2.e, {class: c});
  };
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 11);
  tl.to(o, {d: .8, duration: 6.4, ease: 'none'}, 1.2); m.play(tl, {rest: 9, draw});
 });

 // 11/04: wedged peg, h = 0.5 mm, L = 50 mm, e = 1 mm; the tip depth fixes the pose, wrist side force Fx = kx (e - Wx); jam depth 34.6 mm for kx = 1e5 (lesson code)
 R.gs('peg-wrist-stiffness', (el, m) => {
  const g = stage(m, 'The same 1 mm offset, two wrists. The stiff wrist (kx = 1e5 N/m) starts with a side force of about 112 N and jams at 34.6 mm; the soft one (1e3 N/m) slides in. Sideways scale stretched 10x.', '같은 1 mm offset에 손목 두 개. 뻣뻣한 손목(kx = 1e5 N/m)은 약 112 N의 옆힘으로 시작해 34.6 mm에서 끼고, 부드러운 손목(1e3 N/m)은 미끄러져 들어갑니다. 옆 방향은 10배 늘려 그렸습니다.');
  const H = .0005, LP = .05, E = .001, Z0 = 19.08, ZJ = 34.58, ZE = 45, wx = z => -H + LP * 2 * H / Math.hypot(2 * H, z / 1e3);
  const col = [[120, 1e5, ZJ, 'stiff wrist kx = 1e5', '뻣뻣한 손목 kx = 1e5'], [360, 1e3, ZE, 'soft wrist kx = 1e3', '부드러운 손목 kx = 1e3']].map(([x, kx, zm, en, ko]) => {
   RR(g, x - 90, 120, 80, 95, 3, 'c s sl'); RR(g, x + 10, 120, 80, 95, 3, 'c s sl'); LN(g, x + 20, 70, x + 20, 126, 'sm'); g.lastChild.setAttribute(DA, '3 4');
   T(m, g, x, 24, en, ko, 'g', 'middle');
   return {x, kx, zm, peg: $(g, 'path', {class: 's n w4 st'}), tip: CC(g, x - 10, 0, 5, 'g'), arr: $(g, 'path', {class: 's n w3 sw'}), a: D(g, x, 44, 'g', 'middle'), b: D(g, x, 246, 'g', 'middle'), c: D(g, x, 264, 'g', 'middle'), edge: CC(g, x + 10, 120, 5, 'g')};
  });
  const draw = t => col.forEach(u => {
   const z = Math.min(Z0 + 4 * Math.max(0, t - 1), u.zm), th = Math.atan2(2 * H, z / 1e3), jam = u.zm == ZJ && z >= ZJ, fx = u.kx * (E - wx(z)), ty = 120 + 2 * z, tx = u.x - 10;
   const px = tx + 20 * LP * 1e3 * Math.sin(th), py = ty - 2 * LP * 1e3 * Math.cos(th), c = jam ? 'x' : 'g';
   A(u.peg, {d: `M${tx} ${ty}L${px} ${py}`}); A(u.tip, {cy: ty, class: c}); A(u.edge, {class: c}); A(u.arr, {d: Math.abs(fx) > 8 ? hd(px, py, cl(fx * .5, -60, 60), 0) : ''});
   u.a(jam ? m.t('jammed', '낌') : z >= ZE ? m.t('inserted', '삽입됨') : m.t('pushing', '미는 중')); A(u.a.e, {class: jam ? 'x' : z >= ZE ? 'k' : 'm'});
   u.b(m.t('depth ', '깊이 ') + z.toFixed(1) + ' mm'); u.c(m.t('side force ', '옆힘 ') + fx.toFixed(1) + ' N');
  });
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 11); m.play(tl, {rest: 8.5, draw});
 });
})();
