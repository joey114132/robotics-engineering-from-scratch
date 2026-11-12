// phase 13 concept animations (480x270) on the window.MB kit; one micro-story each
(function () {
 const R = window.MOTION, K = window.MB; if (!K) return;
 const {$, A, RR, CC, fin, cl} = K, DA = 'stroke-dasharray';
 const T = (m, p, x, y, en, ko, c, an) => K.T(m, p, x, y, en, ko, c, an, 15);
 const D = (p, x, y, c, an) => {const e = $(p, 'text', {x, y, 'font-size': 15, class: c || '', 'text-anchor': an || 'start'}); let l = '', k = ''; const f = (s, c2) => {if (s !== l) e.textContent = l = s; if (c2 && c2 !== k) A(e, {class: k = c2});}; f.e = e; return f;};
 const stage = (m, en, ko) => {const g = K.stage(m, en, ko, 480, 270); m.caption(en, ko); m.replayButton(); return g;};
 const LN = (p, a, b, c, d, k) => $(p, 'path', {d: `M${a} ${b}L${c} ${d}`, class: 's n ' + k});

 // 13/01: lesson expert, 3-NN and linear policies; N demos from fixed random starts, then both policies roll out from one test start
 R.gs('demos-fan-in', (el, m) => {
  const g = stage(m, 'Collect expert demos, then let each policy drive from the same start. With 1 demo 3-NN fails; from 3 demos it swerves around the disc. The linear policy averages left and right into straight and goes through the disc.', '전문가 시연을 모은 뒤 두 정책이 같은 시작점에서 달립니다. 시연 1개로는 3-NN이 실패하고 3개부터 원판을 돌아갑니다. 선형 정책은 왼쪽과 오른쪽을 평균해 직진하므로 원판을 뚫고 지나갑니다.');
  let s = 6; const rnd = () => (s = (s * 9301 + 49297) % 233280) / 233280, R0 = .3;
  const exp = (x, y) => {
   const dx = 1 - x, dy = -y, n = Math.hypot(dx, dy) + 1e-9, r = Math.hypot(x, y) + 1e-9; let ax = dx / n, ay = dy / n;
   if (r < R0 + .35) {const sd = x * dy - y * dx >= 0 ? 1 : -1, w = 2.5 * (1 - (r - R0) / .35); ax += w * sd * -y / r + w * .6 * x / r; ay += w * sd * x / r + w * .6 * y / r;}
   const q = Math.max(1, Math.hypot(ax, ay)); return [ax / q, ay / q];
  };
  const roll = (pol, x, y) => {const P = [[x, y]]; for (let i = 0; i < 120; i++) {const [a, b] = pol(x, y).map(v => cl(v, -1, 1)); x += .05 * a; y += .05 * b; P.push([x, y]);} return P;};
  const win = P => !P.some(p => Math.hypot(...p) < R0) && Math.hypot(P[120][0] - 1, P[120][1]) < .1;
  const DM = Array.from({length: 30}, () => roll(exp, -1.5 + .7 * rnd(), -.8 + 1.6 * rnd())), NS = [1, 3, 10, 30], SX = -1.2, SY = .15;
  const RS = NS.map(N => {
   const X = [], Y = []; DM.slice(0, N).forEach(P => P.slice(0, 120).forEach(p => (X.push(p), Y.push(exp(...p)))));
   const knn = (x, y) => X.map((p, i) => [(p[0] - x) ** 2 + (p[1] - y) ** 2, i]).sort((a, b) => a[0] - b[0]).slice(0, 3).reduce((r, q) => [r[0] + Y[q[1]][0] / 3, r[1] + Y[q[1]][1] / 3], [0, 0]);
   const M = [0, 1, 2].map(() => [0, 0, 0, 0, 0]);   // normal equations of the least-squares fit [x, y, 1] -> action
   X.forEach((p, i) => {const f = [p[0], p[1], 1]; for (let a = 0; a < 3; a++) {for (let b = 0; b < 3; b++) M[a][b] += f[a] * f[b]; M[a][3] += f[a] * Y[i][0]; M[a][4] += f[a] * Y[i][1];}});
   for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) if (j != i) {const f = M[j][i] / M[i][i]; for (let k = i; k < 5; k++) M[j][k] -= f * M[i][k];}
   const lin = (x, y) => [3, 4].map(k => M[0][k] / M[0][0] * x + M[1][k] / M[1][1] * y + M[2][k] / M[2][2]);
   return [roll(knn, SX, SY), roll(lin, SX, SY)];
  });
  const PX = p => `${190 + 100 * p[0]} ${140 - 100 * p[1]}`, pd = (P, f) => 'M' + P.slice(0, Math.ceil(f * 120) + 1).map(PX).join('L');
  CC(g, 190, 140, 30, 'c'); CC(g, 290, 140, 7, 'k'); CC(g, 190 + 100 * SX, 140 - 100 * SY, 6, 'g');
  const dp = DM.map(() => $(g, 'path', {class: 's n sm', opacity: .5})), rp = ['sd w3', 'sw w3'].map(c => $(g, 'path', {class: 's n ' + c}));
  const tx = D(g, 16, 26, 'g'), res = [16, 250].map((x, i) => (LN(g, x, 244, x + 18, 244, rp[i].getAttribute('class').slice(4)), D(g, x + 24, 250)));
  const draw = t => {
   const k = cl(Math.floor((t - .3) / 2.9), 0, 3), u = t - .3 - 2.9 * k, a = cl(u), b = cl(u - 1, 0, 1.4) / 1.4;
   tx(m.t('expert demos: ', '전문가 시연: ') + NS[k]); dp.forEach((p, i) => A(p, {d: i < NS[k] ? pd(DM[i], a) : ''}));
   RS[k].forEach((P, i) => {A(rp[i], {d: pd(P, b)}); res[i](`${i ? m.t('linear', '선형') : '3-NN'}: ` + (b < 1 ? '' : win(P) ? m.t('reaches goal', '도착') : m.t('hits the disc', '원판 충돌')), b < 1 ? 'g' : win(P) ? 'k' : 'x');});
  };
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 11.9); m.play(tl, {rest: 11.4, draw});
 });

 // 13/03: lesson episode() and leave-one-out baseline at theta = 0, batch 32; 40 gradient estimates per estimator
 R.gs('baseline-narrows-gradient', (el, m) => {
  const g = stage(m, 'Each dot is one gradient estimate from a batch of 32 episodes. Both estimators aim at the same mean, but subtracting the leave-one-out baseline shrinks the cloud to about a third.', '점 하나는 에피소드 32개 batch로 얻은 gradient 추정입니다. 두 추정은 같은 평균을 겨냥하지만 leave-one-out baseline을 빼면 구름이 약 3분의 1로 줄어듭니다.');
  let s = 1; const rnd = () => {s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296;};
  const gs = () => Math.sqrt(-2 * Math.log(rnd() || 1e-9)) * Math.cos(2 * Math.PI * rnd());
  const est = base => {
   const E = Array.from({length: 32}, () => {let x = 2 * rnd() - 1; const xs = [], as = [], G = []; let c = 0, r = [];
    for (let t = 0; t < 15; t++) {const a = .5 * gs(); xs.push(x); as.push(a); x += .2 * a; r.push(3 - x * x - .01 * a * a);}
    for (let t = 14; t >= 0; t--) G[t] = c += r[t]; return [xs, as, G];});
   const g2 = [0, 0]; E.forEach(([xs, as, G]) => xs.forEach((x, t) => {const b = base ? (E.reduce((q, e) => q + e[2][t], 0) - G[t]) / 31 : 0, sc = as[t] / .25 * (G[t] - b); g2[0] += sc * x / 32; g2[1] += sc / 32;}));
   return g2;
  };
  const C = [0, 1].map(b => Array.from({length: 40}, () => est(b))), mu = C.map(c => [0, 1].map(k => c.reduce((q, v) => q + v[k], 0) / 40));
  const sp = C.map((c, i) => Math.sqrt(c.reduce((q, v) => q + (v[0] - mu[i][0]) ** 2 + (v[1] - mu[i][1]) ** 2, 0) / 40)), U = 40 / sp[0], cls = ['w', 'k'];
  const dots = C.map((c, i) => c.map(v => CC(g, 240 + U * (v[0] - mu[0][0]), cl(140 - U * (v[1] - mu[0][1]), 50, 232), 4.5, cls[i]))), rg = C.map((_, i) => $(g, 'circle', {cx: 240 + U * (mu[i][0] - mu[0][0]), cy: 140 - U * (mu[i][1] - mu[0][1]), r: U * sp[i], class: 'n s s' + cls[i]}));
  const tx = D(g, 16, 26, 'g'), bt = [D(g, 16, 262, 'w'), D(g, 464, 262, 'k', 'end')];
  const draw = t => {
   const n = [cl((t - 1) / 4) * 40 | 0, cl((t - 5.6) / 4) * 40 | 0];
   dots.forEach((d, i) => d.forEach((c, j) => A(c, {opacity: j < n[i] ? 1 : 0}))); rg.forEach((r, i) => A(r, {opacity: n[i] == 40 ? 1 : 0}));
   tx(n[1] ? m.t('with the leave-one-out baseline', 'leave-one-out baseline 사용') : m.t('raw returns, no baseline', '원래 return, baseline 없음'), n[1] ? 'k' : 'w');
   bt[0](n[0] == 40 ? m.t('no baseline: spread ', 'baseline 없음: 퍼짐 ') + sp[0].toFixed(1) : ''); bt[1](n[1] == 40 ? m.t('baseline: spread ', 'baseline: 퍼짐 ') + sp[1].toFixed(1) + ` (${(sp[1] / sp[0]).toFixed(2)}x)` : '');
  };
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 11.2); m.play(tl, {rest: 10.4, draw});
 });

 // 13/04: lesson Wrapper.act() and simulate(): bare policy against wrapped policy, 140 ticks of 0.05 s
 R.gs('wrapper-contains-burst', (el, m) => {
  const g = stage(m, 'A point should go from x = 1 to 0. The policy sends a sign-flipped burst, one NaN and then a dropped camera. Bare, it is thrown out to x = 3.32. Wrapped, x never exceeds 1 and the log counts 45 interventions.', '점은 x = 1에서 0으로 가야 합니다. policy가 부호가 뒤집힌 burst, NaN 하나, 그리고 끊긴 카메라를 보냅니다. wrapper가 없으면 x = 3.32까지 튕겨 나가고 있으면 x가 1을 넘지 않으며 개입 45번이 기록됩니다.');
  const run = wr => {
   let x = 1, seen = 1, last = 0, good = 0; const X = [1], C = [{}], c = {};
   for (let t = 0; t < 140; t++) {
    const drop = t >= 70 && t < 85, pol = v => t >= 20 && t < 28 ? 8 : t == 45 ? NaN : -2 * v; let u;
    if (!drop) seen = x;
    if (wr) {
     let tg, k = null;
     if (!drop) {good = t; const r = pol(x); if (!isFinite(r)) {tg = 0; k = 'NaN';} else {tg = cl(r, -1, 1); k = tg != r ? 'clip' : null;}}
     else if (t - good > 10) {tg = 0; k = 'fallback';} else {tg = last; k = 'hold';}
     u = cl(tg, last - .2, last + .2); if (u != tg && !k) k = 'rate'; if (k) c[k] = (c[k] || 0) + 1; last = u;
    } else {const r = pol(seen); u = cl(isFinite(r) ? r : 0, -10, 10);}
    x += .05 * u; X.push(x); C.push(Object.assign({}, c));
   }
   return [X, C];
  };
  const RN = [run(0), run(1)], PX = x => 60 + 100 * x, Y = [120, 190], cls = ['w', 'k'];
  LN(g, PX(-.2), 120, PX(3.6), 120, 'sm'); LN(g, PX(-.2), 190, PX(3.6), 190, 'sm'); LN(g, PX(1), 70, PX(1), 200, 'sw'); g.lastChild.setAttribute(DA, '4 4'); T(m, g, PX(1), 66, 'x = 1', 'x = 1', 'm', 'middle'); T(m, g, PX(0), 66, 'goal', '목표', 'm', 'middle');
  T(m, g, 16, 104, 'without wrapper', 'wrapper 없음', 'w'); T(m, g, 16, 174, 'with wrapper', 'wrapper 있음', 'k');
  const pt = Y.map((y, i) => CC(g, 0, y, 9, cls[i])), mx = Y.map((y, i) => D(g, 464, y - 16, cls[i], 'end')), ev = D(g, 16, 26, 'g'), n1 = D(g, 16, 240, 'g'), n2 = D(g, 16, 262, 'm'); T(m, g, 464, 26, 'slowed 1.6x', '1.6배 느리게', 'm', 'end');
  const draw = t => {
   const k = cl(Math.floor((t - .5) / .08), 0, 140), c = RN[1][1][k], tot = Object.values(c).reduce((a, b) => a + b, 0);
   RN.forEach(([X], i) => {A(pt[i], {cx: PX(X[k])}); mx[i](m.t('max x ', '최대 x ') + Math.max(...X.slice(0, k + 1).map(Math.abs)).toFixed(2));});
   ev(k >= 20 && k < 28 ? m.t('policy: sign-flipped burst', 'policy: 부호가 뒤집힌 burst') : k >= 45 && k < 52 ? m.t('policy: outputs NaN', 'policy: NaN 출력') : k >= 70 && k < 85 ? m.t('camera: no observation', '카메라: 관측 없음') : '', 'w');
   n1(m.t('wrapper interventions: ', 'wrapper 개입: ') + tot); n2(Object.keys(c).map(q => q + ' ' + c[q]).join('   '));
  };
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 12.2); m.play(tl, {rest: 11.6, draw});
 });

 // 13/05: one Bellman backup of cell (0,5), left of the goal, at sweeps 1 to 4 (lesson gridworld: slip 0.2, gamma 0.9)
 R.gs('bellman-backup', (el, m) => {
  const g = stage(m, 'One backup of the cell left of the goal (slip 0.2, gamma 0.9). Each action scores its reward now (green) plus gamma times the value ahead (pink); the best score becomes the cell\'s new value. Sweep after sweep the goal\'s value reaches it.', '목표 왼쪽 칸 하나의 backup입니다(slip 0.2, gamma 0.9). 각 행동의 점수는 지금의 보상(초록)에 gamma를 곱한 앞으로의 value(분홍)를 더한 값이고 가장 높은 점수가 이 칸의 새 value가 됩니다. sweep을 거듭하면 목표의 value가 이 칸에 닿습니다.');
  const L = ['......G', '.##.##.', '...X...', '.#.##..', '.......'], MV = [[-1, 0], [1, 0], [0, -1], [0, 1]], SD = [[2, 3], [2, 3], [0, 1], [0, 1]];
  const ch = (r, c) => (L[r] || '')[c] || '#', rw = x => x == 'G' ? 1 : x == 'X' ? -1 : 0;
  const Q = (V, r, c, a) => {   // [reward now, gamma * value ahead] of action a
   const q = [0, 0]; [[a, .8], [SD[a][0], .1], [SD[a][1], .1]].forEach(([b, p]) => {
    let rr = r + MV[b][0], cc = c + MV[b][1]; if (ch(rr, cc) == '#') {rr = r; cc = c;}
    q[0] += p * rw(ch(rr, cc)); q[1] += p * .9 * V[rr][cc];
   });
   return q;
  };
  const V = [L.map(s => [...s].map(() => 0))];
  for (let k = 0; k < 4; k++) V.push(V[k].map((row, r) => row.map((_, c) => 'G#X'.includes(ch(r, c)) ? 0 : Math.max(...[0, 1, 2, 3].map(a => Q(V[k], r, c, a).reduce((x, y) => x + y))))));
  const BX = [90, 185, 280, 375], BY = 214, S = 160;
  LN(g, 30, BY, 450, BY, 'sm'); const nv = LN(g, 30, BY, 450, BY, 'sw'); nv.setAttribute(DA, '5 4');
  const bars = BX.map((x, a) => (T(m, g, x, 238, '↑↓←→'[a], '↑↓←→'[a], 'g', 'middle'), [RR(g, x - 28, BY, 56, 0, 2, 'k'), RR(g, x - 28, BY, 56, 0, 2, 'f'), D(g, x, 0, 'g', 'middle')]));
  const best = RR(g, 0, 0, 60, 0, 3, 'n s sw'), tx = D(g, 16, 26, 'g'), nt = D(g, 16, 0, 'w');
  RR(g, 16, 252, 12, 12, 2, 'k'); T(m, g, 34, 264, 'reward now', '지금의 보상'); RR(g, 200, 252, 12, 12, 2, 'f'); T(m, g, 218, 264, 'gamma × value ahead', 'gamma × 앞으로의 value');
  const draw = t => {
   const k = cl(Math.floor((t - .3) / 2.6), 0, 3), u = (t - .3 - 2.6 * k) / 2.6, gr = K.EO(cl(u / .4)), Qs = [0, 1, 2, 3].map(a => Q(V[k], 0, 5, a)), tot = Qs.map(q => q[0] + q[1]), top = Math.max(...tot), bi = tot.indexOf(top), sh = u > .5;
   bars.forEach(([r, f, d], a) => {
    const h0 = Qs[a][0] * S * gr, h1 = Qs[a][1] * S * gr;
    A(r, {y: BY - h0, height: h0}); A(f, {y: BY - h0 - h1, height: h1}); A(d.e, {y: BY - h0 - h1 - 6}); d((tot[a] * gr).toFixed(2));
   });
   A(best, {x: BX[bi] - 30, y: BY - top * S * gr - 2, height: top * S * gr + 4, opacity: sh ? 1 : 0}); A(nv, {opacity: sh ? 1 : 0, d: `M30 ${BY - top * S}H450`});
   A(nt.e, {y: BY - top * S - 8, opacity: sh ? 1 : 0}); nt(m.t('new value ', '새 value ') + top.toFixed(2));
   tx(m.t(`sweep ${k + 1}: value ${V[k][0][5].toFixed(2)}`, `sweep ${k + 1}: value ${V[k][0][5].toFixed(2)}`) + (sh ? ' → ' + top.toFixed(2) : ''));
  };
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 10.9); m.play(tl, {rest: 9.9, draw});
 });

 // 13/06: at the start two answers are right and their mean is wrong; lesson mean_policy against one committed demo (chunks of H = 8)
 R.gs('average-or-commit', (el, m) => {
  const g = stage(m, 'Half the demos go over the disc, half under. A mean policy averages up and down into straight, and drives into the disc. A chunk sampler commits to one demo and runs its next 8 actions at a time, so it clears.', '시연의 절반은 원판 위로, 절반은 아래로 갑니다. 평균 정책은 위와 아래를 평균해 직진하므로 원판에 부딪힙니다. 청크 표본기는 시연 하나를 골라 다음 행동 8개씩 이어서 실행하므로 원판을 피합니다.');
  let s = 8; const rnd = () => (s = (s * 9301 + 49297) % 233280) / 233280, T0 = 40, SG = .15;
  const P = []; for (let n = 0; n < 6; n++) {const h = .45 + .2 * rnd(), up = Array.from({length: T0 + 1}, (_, i) => {const x = -1 + 2 * i / T0; return [x, h * (1 - x * x)];}); P.push(up, up.map(p => [p[0], -p[1]]));}
  const A2 = P.map(p => p.slice(1).map((q, i) => [q[0] - p[i][0], q[1] - p[i][1]])), S2 = [], V2 = [];
  P.forEach((p, d) => p.slice(0, T0).forEach((q, i) => (S2.push(q), V2.push(A2[d][i]))));
  const pol = x => {   // kernel mean of nearby demo actions
   const d2 = S2.map(q => (q[0] - x[0]) ** 2 + (q[1] - x[1]) ** 2), lo = Math.min(...d2), w = d2.map(d => Math.exp(-(d - lo) / (2 * SG * SG))), z = w.reduce((a, b) => a + b);
   return [0, 1].map(k => w.reduce((q, v, i) => q + v * V2[i][k], 0) / z);
  };
  const MP = [[-1, 0]]; while (MP[MP.length - 1][0] < 1 && MP.length < 80) {const a = pol(MP[MP.length - 1]); MP.push([MP[MP.length - 1][0] + a[0], MP[MP.length - 1][1] + a[1]]);}
  const U = P[0], PX = p => `${240 + 160 * p[0]} ${140 - 160 * p[1]}`, pd = (Pt, f, a = 0) => 'M' + Pt.slice(a, Math.ceil(f * (Pt.length - 1)) + 1).map(PX).join('L'), a0 = [A2[0][0], A2[1][0], pol([-1, 0])];
  CC(g, 240, 140, 48, 'c'); CC(g, 80, 140, 6, 'g'); CC(g, 400, 140, 6, 'k');
  const dm = [0, 1].map(() => $(g, 'path', {class: 's n sm', opacity: .6})), ar = ['sf', 'sd', 'sw'].map(c => $(g, 'path', {class: 's n w4 ' + c})), mp = $(g, 'path', {class: 's n w3 sw'}), ck = [0, 1, 2, 3, 4].map(i => $(g, 'path', {class: 's n w3 ' + (i % 2 ? 'sd' : 'sk')}));
  const tx = D(g, 16, 26, 'g'), r1 = D(g, 16, 266, 'k'), r2 = D(g, 16, 246, 'w'), lab = ['up demo', 'down demo', 'mean'].map((e, i) => T(m, g, 12, [98, 196, 126][i], e, ['위 시연', '아래 시연', '평균'][i], 'm'));
  const o = {a: 0, b: 0, c: 0}, near = (Pt, n) => Math.min(...Pt.slice(0, n + 1).map(p => Math.hypot(p[0], p[1])));
  const draw = () => {
   A(dm[0], {d: pd(U, o.a)}); A(dm[1], {d: pd(P[1], o.a)});
   ar.forEach((p, i) => A(p, {d: K.hd(80, 140, 4 * 160 * a0[i][0], -4 * 160 * a0[i][1]), opacity: i < 2 ? cl(o.a * 3 - 1.2) : cl(o.a * 3 - 2)}));
   lab.forEach((l, i) => A(l, {opacity: i < 2 ? cl(o.a * 3 - 1.2) : cl(o.a * 3 - 2)}));
   const n = Math.round(o.b * (MP.length - 1)), n2 = Math.round(o.c * 40);
   A(mp, {d: o.b ? pd(MP, o.b) : ''}); ck.forEach((c, i) => A(c, {d: o.c > i / 5 ? 'M' + U.slice(8 * i, Math.min(40, Math.round(o.c * 40), 8 * i + 8) + 1).map(PX).join('L') : ''}));
   tx(o.c ? m.t('chunk sampler: one demo, 8 actions at a time', '청크 표본기: 시연 하나, 행동 8개씩') : o.b ? m.t('mean policy: average of up and down', '평균 정책: 위와 아래의 평균') : m.t('two demonstrations, both good', '좋은 시연 두 개'));
   r1(o.c ? m.t(`sampler: closest to the centre ${near(U, n2).toFixed(2)}: clears`, `표본기: 중심에 가장 가까운 거리 ${near(U, n2).toFixed(2)}: 통과`) : o.b ? '' : m.t('arrows drawn 4x longer', '화살표는 4배로 그렸습니다'));
   r2(o.b ? m.t(`mean: closest to the centre ${near(MP, n).toFixed(2)}` + (near(MP, n) < .3 ? ': hits' : ''), `평균: 중심에 가장 가까운 거리 ${near(MP, n).toFixed(2)}` + (near(MP, n) < .3 ? ': 충돌' : '')) : '');
  };
  const tl = m.timeline({repeatDelay: .3}); fin(tl, g, 12);
  tl.to(o, {a: 1, duration: 3.6, ease: 'none'}, .5).to(o, {b: 1, duration: 3.4, ease: 'none'}, 4.4).to(o, {c: 1, duration: 3.2, ease: 'none'}, 8.2); m.play(tl, {rest: 11.4, draw});
 });
})();
