// phase 12 concept animations (480x270) on the window.MB kit; one micro-story each
(function () {
 const R = window.MOTION, K = window.MB; if (!K) return;
 const {$, A, RR, CC, fin, cl} = K, DA = 'stroke-dasharray';
 const T = (m, p, x, y, en, ko, c, an) => K.T(m, p, x, y, en, ko, c, an, 15);
 const D = (p, x, y, c, an) => {const e = $(p, 'text', {x, y, 'font-size': 15, class: c || '', 'text-anchor': an || 'start'}); let l = ''; const f = s => {if (s !== l) e.textContent = l = s;}; f.e = e; return f;};
 const stage = (m, en, ko) => {const g = K.stage(m, en, ko, 480, 270); m.caption(en, ko); m.replayButton(); return g;};
 const LN = (p, a, b, c, d, k) => $(p, 'path', {d: `M${a} ${b}L${c} ${d}`, class: 's n ' + k});

 // 12/01: the lesson's RK4 joint (REAL, command(t), 6 s) replayed on plants that each miss one effect; running RMS of the measured angle
 R.gs('sim-missing-effects', (el, m) => {
  const g = stage(m, 'The same open-loop torque on the real joint (thick) and on three sims, each missing one effect. Without friction the joint drifts away (RMS 0.545 rad); without motor lag 0.042 rad; without sensor delay 0.029 rad.', '같은 open-loop 토크를 실제 관절(굵은 선)과 효과가 하나씩 빠진 sim 세 개에 줍니다. 마찰이 없으면 멀리 어긋나고(RMS 0.545 rad) 모터 지연이 없으면 0.042 rad, 센서 지연이 없으면 0.029 rad입니다.');
  const P0 = {J: .05, b: .02, c: .05, k: .2, Tm: .03, dl: .02}, N = 6000;
  const u = t => .35 * Math.sin(2 * Math.PI * .7 * t) + .15 * Math.sin(2 * Math.PI * 1.9 * t);
  const meas = p => {   // RK4 of J w' = tm - b w - c tanh(w/eps) - k sin q, Tm tm' = u - tm; the encoder shows q delayed by dl
   const f = (q, w, tm, e) => [w, (tm - p.b * w - p.c * Math.tanh(w / .01) - p.k * Math.sin(q)) / p.J, p.Tm ? (e - tm) / p.Tm : 0], Q = []; let s = [0, 0, 0];
   for (let i = 0; i < N; i++) {
    Q.push(s[0]); const e = u(i * 1e-3); if (!p.Tm) s[2] = e;
    const k1 = f(...s, e), k2 = f(...s.map((v, j) => v + k1[j] / 2e3), e), k3 = f(...s.map((v, j) => v + k2[j] / 2e3), e), k4 = f(...s.map((v, j) => v + k3[j] * 1e-3), e);
    s = s.map((v, j) => v + (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]) * 1e-3 / 6);
   }
   const n = Math.round(p.dl * 1e3); return n ? Array(n).fill(0).concat(Q.slice(0, N - n)) : Q;
  };
  const Q = [P0, {b: 0, c: 0}, {Tm: 0}, {dl: 0}].map((o, k) => meas(k ? Object.assign({}, P0, o) : P0));
  const E = Q.slice(1).map(q => { let s = 0; return q.map((v, i) => (s += (v - Q[0][i]) ** 2, s)); });   // running sum of squared error
  const nm = [['friction', '마찰', 'w', 'sw'], ['motor lag', '모터 지연', 'f', 'sf'], ['sensor delay', '센서 지연', 'k', 'sk']];
  const PX = 110, PY = 90, L = 66, ln = [$(g, 'path', {class: 's n w6 st'}), ...nm.map(n => $(g, 'path', {class: 's n w3 ' + n[3]}))];
  CC(g, PX, PY, 5, 'g'); const bob = CC(g, 0, 0, 8, 't'), tx = D(g, 16, 26, 'm');
  T(m, g, 16, 236, 'thick: real joint', '굵은 선: 실제 관절'); T(m, g, 16, 256, 'thin: sim missing one effect', '얇은 선: 효과 하나 뺀 sim');
  const bars = nm.map((n, k) => (T(m, g, 250, 78 + 54 * k, n[0], n[1]), [D(g, 460, 78 + 54 * k, 'g', 'end'), RR(g, 250, 88 + 54 * k, 0, 14, 3, n[2])]));
  const draw = t => {
   const i = cl(Math.round((t - 1) * 1e3), 0, N - 1);
   ln.forEach((l, k) => A(l, {d: `M${PX} ${PY}L${PX + L * Math.sin(Q[k][i])} ${PY + L * Math.cos(Q[k][i])}`})); A(bob, {cx: PX + L * Math.sin(Q[0][i]), cy: PY + L * Math.cos(Q[0][i])});
   tx('t = ' + (i / 1e3).toFixed(1) + ' s'); bars.forEach(([v, r], k) => {const e = Math.sqrt(E[k][i] / (i + 1)); v(e.toFixed(3) + ' rad'); A(r, {width: e * 330});});
  };
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 10.6); m.play(tl, {rest: 9.5, draw});
 });

 // 12/02: lesson step(): explicit Euler vs semi-implicit on a 1 kg mass dropped 0.1 m onto a 10 kN/m spring floor, 0.6 s, slowed 5x
 R.gs('dt-bounce', (el, m) => {
  const g = stage(m, 'A 1 kg mass dropped 0.1 m onto a 10 kN/m spring floor, slowed 5x. Raise the time step and explicit Euler rebounds higher than it fell (0.14, 0.27, 5.03 m); semi-implicit stays near 0.1 m until it too drifts (0.65 m at 19 ms).', '1 kg 질량을 0.1 m에서 10 kN/m 스프링 바닥에 떨어뜨립니다(5배 느리게). time step을 키우면 explicit Euler는 떨어진 높이보다 높이 튑니다(0.14, 0.27, 5.03 m). semi-implicit은 0.1 m 근처에 머물다 19 ms에서 0.65 m까지 올라갑니다.');
  const DTS = [1e-3, 3e-3, 1.9e-2], acc = x => -9.81 + 1e4 * Math.max(-x, 0);
  const run = (semi, dt) => {
   let x = .1, v = 0, hit = 0, ap = 0; const Y = [[0, x, 0]];
   for (let i = 1; i <= Math.round(.6 / dt); i++) {
    if (semi) {v += dt * acc(x); x += dt * v;} else {const a = acc(x); x += dt * v; v += dt * a;}
    hit = hit || x < 0; if (hit && x > 0) ap = Math.max(ap, x); Y.push([i * dt, x, ap]);
   }
   return Y;
  };
  const S = DTS.map(dt => [0, 1].map(s => run(s, dt))), CX = [120, 360], Y = x => 240 - 280 * x;
  LN(g, 40, 240, 440, 240, 'st'); LN(g, 40, Y(.1), 440, Y(.1), 'sw'); g.lastChild.setAttribute(DA, '4 5'); T(m, g, 16, Y(.1) - 6, '0.1 m', '0.1 m', 'm');
  const dtx = D(g, 240, 24, 'g', 'middle');
  const u = CX.map((x, c) => [CC(g, x, 0, 8, 'f'), LN(g, x - 24, 0, x + 24, 0, 'sw'), D(g, x, 264, 'g', 'middle'), D(g, x + 30, 0, 'm')]);
  const draw = t => {
   const k = cl(Math.floor((t - .6) / 3.5), 0, 2), ts = cl((t - .6 - 3.5 * k) / 5, 0, .6), dt = DTS[k];
   dtx(m.t('time step ', 'time step ') + dt * 1e3 + m.t(' ms (5x slower)', ' ms (5배 느리게)'));
   u.forEach(([ball, tick, rd, off], c) => {
    const Z = S[k][c][Math.min(Math.round(ts / dt), S[k][c].length - 1)], x = Z[1], ap = Z[2];
    A(ball, {cy: Y(cl(x, -.05, .7)) - 8, cx: CX[c]}); A(tick, {d: ap ? `M${CX[c] - 24} ${Y(Math.min(ap, .7))}h48` : ''}); rd((c ? 'semi-implicit: ' : 'explicit Euler: ') + ap.toFixed(2) + ' m');
    A(off.e, {y: Y(.71) + 3}); off(x > .7 ? m.t('off scale', '범위 밖') : '');
   });
  };
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 11.5); m.play(tl, {rest: 10.6, draw});
 });

 // 12/03: friction model F(w) = b w + c tanh(w/0.01), true b = 0.02, c = 0.05. A slow run visits one speed (0.3 rad/s); a rich run visits many
 R.gs('excitation-pins-down-b', (el, m) => {
  const g = stage(m, 'Friction torque against speed. One slow run sees a single speed, so every (b, c) pair through that point fits it equally. A rich run spreads the data and only b = 0.02, c = 0.05 fits.', '속도에 따른 마찰 토크입니다. 느린 run 하나는 속도 하나만 보므로 그 점을 지나는 (b, c) 쌍이 모두 똑같이 맞습니다. 풍부한 run은 데이터를 펼쳐서 b = 0.02, c = 0.05만 맞습니다.');
  const F = (w, b, c) => b * w + c * Math.tanh(w / .01), PX = w => 240 + 57 * w, PY = f => 150 - 200 * f, W0 = .3, o = {b: -.1, ph: 0};
  const WS = Array.from({length: 24}, (_, i) => W0 + 1.5 * Math.sin(.8 * Math.PI * i * .8) + Math.sin(2.6 * Math.PI * i * .8) + .5 * Math.sin(6.2 * Math.PI * i * .8)).map(w => cl(w, -3.4, 3.4));
  LN(g, 40, 150, 440, 150, 'sm'); LN(g, 240, 66, 240, 234, 'sm'); T(m, g, 436, 170, 'speed', '속도', 'm', 'end'); T(m, g, 246, 76, 'torque', '토크', 'm');
  const tr = $(g, 'path', {class: 's n sm', d: 'M' + Array.from({length: 141}, (_, i) => {const w = (i - 70) / 20; return PX(w) + ' ' + PY(F(w, .02, .05));}).join('L')}); tr.setAttribute(DA, '3 4');
  const dots = WS.map(() => CC(g, 0, 0, 4, 'g')), ln = $(g, 'path', {class: 's n w3 sw'});
  const t1 = D(g, 16, 26, 'g'), r1 = D(g, 16, 48, 'm'), r2 = D(g, 16, 250, 'm');
  const draw = () => {
   const b = o.b, c = .056 - W0 * b, pts = o.ph ? WS : [W0];   // the line is forced through the single speed's data
   dots.forEach((d, i) => A(d, {cx: PX(pts[i] || 0), cy: PY(F(pts[i] || 0, .02, .05)), opacity: i < pts.length ? 1 : 0}));
   A(ln, {d: 'M' + Array.from({length: 141}, (_, i) => {const w = (i - 70) / 20; return PX(w) + ' ' + PY(F(w, b, c));}).join('L')});
   const mis = Math.sqrt(pts.reduce((s, w) => s + (F(w, b, c) - F(w, .02, .05)) ** 2, 0) / pts.length);
   t1(o.ph ? m.t('a rich run: speed varies', '풍부한 run: 속도가 변함') : m.t('one slow run: constant speed', '느린 run 하나: 일정한 속도'));
   r1(`b = ${b.toFixed(3)}   c = ${c.toFixed(3)}`); r2(m.t('misfit at the data ', '데이터에서의 어긋남 ') + mis.toFixed(3) + ' Nm');
  };
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 11.5);
  tl.to(o, {b: .1, duration: 4, ease: 'sine.inOut'}, 1).set(o, {ph: 1, b: -.1}, 5.3).to(o, {b: .02, duration: 4, ease: 'power2.out'}, 5.6); m.play(tl, {rest: 10.4, draw});
 });
})();
