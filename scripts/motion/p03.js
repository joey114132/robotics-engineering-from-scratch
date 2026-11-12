// phase 03 concept loops (480x270) as GSAP timelines; needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,S,SN,hd,fin} = K,D2R = Math.PI / 180,DA = 'stroke-dasharray',f2 = x => x.toFixed(2);
 const T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 // D: a text node you set from draw()
 const D = (p,x,y,cls,an) => {const e = $(p,'text',{x,y,'font-size':15,class:cls || '','text-anchor':an || 'start'}); let l = ''; return s => {if (s !== l) e.textContent = l = s;};};
 const stage = (m,en,ko) => {const g = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return g;};
 // a timeline of length E; its time t drives draw(t) (everything on screen is computed from t)
 const play = (m,g,E,rest,draw) => {const tl = m.timeline({repeatDelay:.3}); fin(tl,g,E); m.play(tl,{rest,draw});};

 R.gs('held-torque',(el,m) => {
  const g = stage(m,'One tick: the torque is held and set by the velocity at the tick start, so v+ = v (1 - r) with r = dt kd / J. Here J = 0.02 and dt = 0.001.','한 tick 동안 torque는 tick 시작 때의 속도로 정해져 유지됩니다. 그래서 v+ = v (1 - r)이고 r = dt kd / J입니다. 여기서는 J = 0.02, dt = 0.001입니다.');
  const X0 = 36,W = 68,Y0 = 142,SC = 30,N = 6,CASE = 3.6,KD = [10,30,44],J = .02,DT = .001;
  $(g,'path',{d:`M${X0} ${Y0}h${N * W}`,class:'s n sm'});
  for (let j = 0; j <= N; j++) $(g,'path',{d:`M${X0 + j * W} 66v166`,class:'s n sm',[DA]:'2 6'});
  T(m,g,X0 + N * W,58,'ticks','tick','m','end'); T(m,g,16,Y0 + 5,'v','v','m');
  const hl = D(g,16,24,'g'),ln = $(g,'path',{class:'s n w4'}),zc = CC(g,0,0,6,'x'),r1 = D(g,16,248,'g'),r2 = D(g,16,266,'m');
  const dots = Array.from({length:N + 1},() => CC(g,0,0,4,'g')),MSG = [['smooth: v shrinks','smooth: v가 줄어듭니다'],['chatter: v flips sign','chatter: v의 부호가 뒤집힙니다'],['divergent: |v| grows','divergent: |v|가 커집니다']];
  const draw = t => {
   const c = Math.min(2,Math.floor(t / CASE)),r = KD[c] * DT / J,f = 1 - r,p = Math.min(1,(t - c * CASE) / 3) * N,k = Math.min(N - 1,Math.floor(p)),s = p - k;
   const P = (x,v) => `${(X0 + x * W).toFixed(1)} ${(Y0 - v * SC).toFixed(1)}`,zx = 1 / r,cross = r > 1 && (k > 0 || s >= zx);
   let d = 'M' + P(0,1); for (let j = 1; j <= k; j++) d += 'L' + P(j,f ** j); d += 'L' + P(k + s,f ** k * (1 - r * s));
   A(ln,{d,class:'s n w4 ' + ['sk','sw','sb'][r <= 1 ? 0 :r < 2 ? 1 :2]});
   dots.forEach((e,j) => A(e,{cx:X0 + j * W,cy:Y0 - SC * f ** j,opacity:j <= p ? 1 :0}));
   A(zc,{cx:X0 + zx * W,cy:Y0,opacity:cross ? 1 :0});
   hl(m.t(MSG[c][0],MSG[c][1]));
   r1(`r = ${f2(r)} | kd = ${KD[c]} | v(tick ${k}) = ${f2(f ** k)}`);
   r2(c === 1 && cross ? m.t('v hits 0 mid-tick, the held torque keeps pushing','v가 중간에 0이 돼도 torque는 계속 밉니다') :c === 2 ? m.t(`|1 - r| = ${f2(-f)} > 1, so |v| grows`,`|1 - r| = ${f2(-f)} > 1이라 |v|가 커집니다`) :m.t(`every tick v+ = ${f2(f)} v`,`tick마다 v+ = ${f2(f)} v`));
  };
  play(m,g,3 * CASE,6.9,draw);
 });

 R.gs('sag-halves',(el,m) => {
  const g = stage(m,'The feedforward is 0.8 of the gravity torque, so the residual is the missing 20%. The sag is about residual / kp: halve kp and the sag roughly doubles.','feedforward가 중력 torque의 0.8이라 residual은 모자란 20%입니다. 처짐은 대략 residual / kp이므로 kp를 반으로 줄이면 처짐이 대략 두 배가 됩니다.');
  const M1 = 2,M2 = 1,L1 = .4,LC = .2,G = 9.81,BX = 48,BY = 118,L = 108,tg = q => {const t2 = M2 * LC * G * Math.cos(q[0] + q[1]); return [(M1 * LC + M2 * L1) * G * Math.cos(q[0]) + t2,t2];};
  const t0 = tg([0,0]),ff = t0.map(x => .8 * x),res = t0[0] - ff[0];
  const sag = kp => {let q = [0,0]; for (let i = 0; i < 200; i++) {const w = tg(q); q = q.map((x,j) => .5 * x + .5 * (ff[j] - w[j]) / kp);} return q;};
  T(m,g,16,24,`Model 20% light: residual ${f2(res)} Nm`,`모델이 20% 가벼워서 residual은 ${f2(res)} Nm`,'g');
  RR(g,BX - 18,BY - 30,14,60,3,'f s st'); $(g,'path',{d:`M${BX} ${BY}h${2 * L}`,class:'s n sm',[DA]:'3 6'});
  const arm = $(g,'path',{class:'s n sd w6'}),gap = $(g,'path',{class:'s n sw w3'}),dots = [0,1,2].map(() => CC(g,0,0,5,'g'));
  $(g,'path',{d:`M360 232h100`,class:'s n sm'}); const bk = RR(g,364,232,28,0,3,'k'),bs = RR(g,424,232,28,0,3,'x');
  T(m,g,378,248,'kp','kp','m','middle'); T(m,g,438,248,'sag','처짐','m','middle');
  const r1 = D(g,16,248,'g'),r2 = D(g,16,266,'m');
  const draw = t => {
   const kp = 24 / 2 ** (SN(S(t,2.4,3.4)) + SN(S(t,6,7))),q = sag(kp),a = q[0] + q[1],x1 = BX + L * Math.cos(q[0]),y1 = BY - L * Math.sin(q[0]),x2 = x1 + L * Math.cos(a),y2 = y1 - L * Math.sin(a);
   A(arm,{d:`M${BX} ${BY}L${x1} ${y1}L${x2} ${y2}`}); A(gap,{d:`M${x2} ${BY}V${y2}`});
   [[BX,BY],[x1,y1],[x2,y2]].forEach((p,i) => A(dots[i],{cx:p[0],cy:p[1]}));
   A(bk,{y:232 - kp * 3,height:kp * 3}); A(bs,{y:232 + q[0] / D2R * 5.5,height:-q[0] / D2R * 5.5});
   r1(`kp = ${kp.toFixed(0)} | sag of joint 1 = ${(q[0] / D2R).toFixed(1)}°`.replace('sag of joint 1',m.t('sag of joint 1','관절 1 처짐')));
   r2(m.t(`residual / kp = ${(-res / kp / D2R).toFixed(1)}° (first order)`,`residual / kp = ${(-res / kp / D2R).toFixed(1)}° (1차 근사)`));
  };
  play(m,g,10.8,10.2,draw);
 });

 R.gs('push-and-settle',(el,m) => {
  const g = stage(m,'Same push F = 2 on K = 100, J = 1, 3x slow. Both settle at F / K = 0.020 rad; only zeta changes the overshoot: 0.53 at 0.2, none at 1.','같은 push F = 2, K = 100, J = 1(3배 느리게)입니다. 둘 다 F / K = 0.020 rad에서 멈추고 overshoot만 zeta로 달라집니다. 0.2는 0.53, 1은 없습니다.');
  const KK = 100,F = 2,W0 = 10,ST = F / KK,X0 = 150,SC = 8500,xs = q => X0 + q * SC,RUN = [[.8,.2],[7,1]];
  T(m,g,16,24,'A spring and a damper meet a push','스프링과 댐퍼가 push를 받습니다','g');
  RR(g,22,70,14,110,3,'f s st'); $(g,'path',{d:'M36 120H460',class:'s n sm',[DA]:'3 6'});
  $(g,'path',{d:'M36 207H460',class:'s n sm'}); [0,.01,.02,.03].forEach(q => {$(g,'path',{d:`M${xs(q)} 202v10`,class:'s n sm'}); T(m,g,xs(q),230,q ? q.toFixed(2) :'0',q ? q.toFixed(2) :'0','m','middle');});
  $(g,'path',{d:`M${xs(ST)} 66V207`,class:'s n sk w3',[DA]:'4 4'}); T(m,g,xs(ST) + 8,196,'F / K','F / K','m');
  const pk = $(g,'path',{class:'s n sw w3'}),sp = $(g,'path',{class:'s n sd w3'}),rod = $(g,'path',{class:'s n sm w3'});
  RR(g,40,133,66,18,3,'c s st'); const bl = $(g,'g',{}); RR(bl,0,96,36,60,6,'f s st'); $(bl,'path',{d:hd(2,80,30,0),class:'s n sf w4'}); T(m,bl,40,86,'F = 2','F = 2','g');
  const r1 = D(g,16,248,'g'),r2 = D(g,16,266,'m');
  const draw = t => {
   const run = t >= RUN[1][0] ? 1 :0,z = RUN[run][1],tau = Math.max(0,(t - RUN[run][0]) / 3),wd = W0 * Math.sqrt(1 - Math.min(z,.999) ** 2),sx = Math.sqrt(1 - z * z);
   const x = (a) => ST * (z < 1 ? 1 - Math.exp(-z * W0 * a) * (Math.cos(wd * a) + z / sx * Math.sin(wd * a)) :1 - (1 + W0 * a) * Math.exp(-W0 * a)),q = x(tau),qp = x(z < 1 ? Math.min(tau,Math.PI / wd) :tau),bx = xs(q);
   gsap.set(bl,{x:bx}); let d = 'M36 100H50'; for (let i = 0; i < 8; i++) d += `L${50 + (bx - 64) * (i + .5) / 8} ${i % 2 ? 90 :110}`; A(sp,{d: d + `H${bx}`}); A(rod,{d:`M106 142H${bx}`});
   A(pk,{d:`M${xs(qp)} 80V207`,opacity:qp > ST * 1.002 ? 1 :0});
   r1(`K = ${KK} | D = ${(2 * z * Math.sqrt(KK)).toFixed(0)} | ζ = ${z}`);
   r2(m.t(`peak ${qp.toFixed(3)} | overshoot ${f2(Math.max(0,qp / ST - 1))}`,`peak ${qp.toFixed(3)} | overshoot ${f2(Math.max(0,qp / ST - 1))}`));
  };
  play(m,g,11,6.8,draw);
 });

 R.gs('windup-race',(el,m) => {
  const g = stage(m,'Same gains (kp 100, ki 300, kd 20) and torque limit 20, target 2 rad, shown 2x slow. Without a clamp the integral winds up while the torque is saturated and the joint overshoots by about 1.5 rad.','같은 gain(kp 100, ki 300, kd 20)과 torque 한계 20, 목표 2 rad이며 2배 느리게 보여 줍니다. clamp가 없으면 torque가 포화된 동안 적분항이 쌓여서 약 1.5 rad overshoot가 납니다.');
  const sim = aw => {let q = 0,v = 0,I = 0,mx = 0,o = []; for (let i = 0; i <= 3600; i++) {if (i % 20 === 0) o.push([q,I,mx]); const e = 2 - q,raw = 100 * e + I - 20 * v,u = Math.max(-20,Math.min(20,raw)); if (!aw || u === raw || e * raw < 0) I += .3 * e; v += (u - 2 * v) / 1000; q += v / 1000; mx = Math.max(mx,q);} return o;};
  const RUNS = [sim(false),sim(true)],CL = ['sw','sk'],X0 = 40,PX = 117,qy = q => 130 - q * 28,iy = i => 205 - i * .28;
  $(g,'path',{d:`M${X0} ${qy(2)}H460`,class:'s n sm',[DA]:'3 6'}); $(g,'path',{d:`M${X0} 205H460`,class:'s n sm'}); T(m,g,460,qy(2) - 6,'target','목표','m','end');
  T(m,g,460,44,'q (rad)','q (rad)','m','end'); T(m,g,460,172,'integral term I','적분항 I','m','end');
  const qs = CL.map(c => $(g,'path',{class:'s n w4 ' + c})),is = CL.map(c => $(g,'path',{class:'s n w3 ' + c}));
  const r1 = D(g,16,248,'w'),r2 = D(g,16,266,'k');
  const draw = t => {
   const n = Math.round(Math.min(3.6,Math.max(0,(t - .8) / 2)) / .02),row = [r1,r2];
   RUNS.forEach((o,k) => {
    let a = 'M',b = 'M'; for (let i = 0; i <= n; i += 2) {const x = X0 + i * .02 * PX; a += `${x} ${qy(o[i][0])}L`; b += `${x} ${iy(o[i][1])}L`;}
    A(qs[k],{d:a.slice(0,-1)}); A(is[k],{d:b.slice(0,-1)});
    row[k](m.t(k ? 'clamped integrator' :'no anti-windup',k ? '적분 clamp' :'anti-windup 없음') + ` | I = ${Math.round(o[n][1]) || 0} | ` + 'overshoot ' + f2(Math.max(0,o[n][2] - 2)) + ' rad');
   });
  };
  play(m,g,10,8,draw);
 });

 R.gs('tracking-arms',(el,m) => {
  const g = stage(m,'The same 1 s swing, 3x slow. Joint PD lags; computed torque cancels M(q) and Coriolis and stays on the reference.','같은 1초 swing(3배 느리게)입니다. joint PD는 늦고 computed torque는 M(q)와 Coriolis를 상쇄해 reference에 붙습니다.');
  // midpoint step (the lesson uses RK4); lesson arm: m = 1 kg, l1 = 0.5 m, lc = 0.25 m, I = 0.02 kg m^2 per link, so m2 l1 lc = 0.125 and the 0.415 and 0.0825 follow
  const OM = 20,AMP = [1.2,1.5],W = 2 * Math.PI,mass = q => [.415 + .25 * Math.cos(q[1]),.0825 + .125 * Math.cos(q[1]),.0825],cor = x => {const h = .125 * Math.sin(x[1]); return [-h * (2 * x[2] * x[3] + x[3] ** 2),h * x[2] ** 2];};
  const ref = t => {const c = Math.cos(W * t),s = Math.sin(W * t); return [AMP.map(a => a * (1 - c) / 2),AMP.map(a => a * W * s / 2),AMP.map(a => a * W * W * c / 2)];};
  const acc = (x,u) => {const M = mass(x),h = cor(x),b = [u[0] - h[0],u[1] - h[1]],d = M[0] * M[2] - M[1] ** 2; return [x[2],x[3],(M[2] * b[0] - M[1] * b[1]) / d,(M[0] * b[1] - M[1] * b[0]) / d];};
  const ctl = ct => (x,r) => {
   const e = [0,1].map(i => r[0][i] - x[i]),ed = [0,1].map(i => r[1][i] - x[i + 2]),M = ct ? mass(x) :mass([.6,.75]),a = [0,1].map(i => (ct ? r[2][i] :0) + 2 * OM * ed[i] + OM * OM * e[i]);
   if (!ct) return [M[0] * a[0],M[2] * a[1]]; const h = cor(x); return [M[0] * a[0] + M[1] * a[1] + h[0],M[1] * a[0] + M[2] * a[1] + h[1]];
  };
  const sim = c => {let x = [0,0,0,0],mx = 0,o = []; for (let i = 0; i <= 2000; i++) {const r = ref(i / 1000); mx = Math.max(mx,Math.hypot(r[0][0] - x[0],r[0][1] - x[1])); if (i % 10 === 0) o.push([x[0],x[1],mx]);
   const u = c(x,r),h = .001,k = acc(x,u),y = acc(x.map((z,j) => z + h / 2 * k[j]),u); x = x.map((z,j) => z + h * y[j]);} return o;};
  const RUNS = [sim(ctl(0)),sim(ctl(1))],BY = 215,L = 84,BX = [56,296];
  const path = (bx,q) => {const x = bx + L * Math.cos(q[0]),y = BY - L * Math.sin(q[0]),a = q[0] + q[1]; return `M${bx} ${BY}L${x} ${y}L${x + L * Math.cos(a)} ${y - L * Math.sin(a)}`;};
  T(m,g,16,24,'PD per joint','joint별 PD','g'); T(m,g,256,24,'computed torque','computed torque','g'); $(g,'path',{d:'M240 40V270',class:'s n sm',[DA]:'2 6'});
  const rf = BX.map(() => $(g,'path',{class:'s n sm w3',[DA]:'4 5'})),ar = BX.map((b,k) => $(g,'path',{class:'s n w6 ' + ['sw','sk'][k]})),rd = [D(g,16,248,'w'),D(g,256,248,'k')],r2 = D(g,16,266,'m');
  const draw = t => {
   const s = Math.min(2,Math.max(0,(t - .8) / 3)),n = Math.round(s / .01),q = ref(s)[0],e = RUNS.map(o => o[n][2]);
   BX.forEach((bx,k) => {A(rf[k],{d:path(bx,q)}); A(ar[k],{d:path(bx,RUNS[k][n])}); rd[k]('max |e| ' + e[k].toFixed(e[k] < .01 ? 4 :3) + ' rad');});
   r2(m.t('dashed: ref','점선: ref') + (s > .5 ? ` | PD ÷ CT = ${(e[0] / e[1]).toFixed(0)}x` :''));
  };
  play(m,g,9.6,3.2,draw);
 });

 // path through pts[0..n] with maps fx, fy
 const poly = (pts,n,fx,fy) => pts.slice(0,n + 1).map((p,i) => `${i ? 'L' :'M'}${fx(p[0],i).toFixed(1)} ${fy(p[1],i).toFixed(1)}`).join('');

 R.gs('riccati-converge',(el,m) => {
  const g = stage(m,'Riccati loop for a double integrator (dt = 0.05, Q = diag(1, 0.1), R = 0.1): each pass refines K until P stops changing. Then u = -Kx brings a 1 m error to zero.','dt = 0.05, Q = diag(1, 0.1), R = 0.1인 이중 적분기에 Riccati 반복을 돌립니다. P가 더 변하지 않을 때까지 K가 다듬어지고 u = -Kx가 1 m 오차를 0으로 만듭니다.');
  const dt = .05,Am = [[1,dt],[0,1]],B = [dt * dt / 2,dt],Q = [[1,0],[0,.1]],R0 = .1,NI = 60,KS = [];
  const mm = (X,Y) => X.map((r,i) => Y[0].map((_,j) => r.reduce((s,_k,k) => s + X[i][k] * Y[k][j],0)));
  let P = Q.map(r => r.slice());
  for (let i = 0; i < NI; i++) {
   const PB = [P[0][0] * B[0] + P[0][1] * B[1],P[1][0] * B[0] + P[1][1] * B[1]],S = R0 + B[0] * PB[0] + B[1] * PB[1],PA = mm(P,Am),K = [0,1].map(j => (B[0] * PA[0][j] + B[1] * PA[1][j]) / S); KS.push(K);
   const AK = Am.map((r,a) => r.map((v,j) => v - B[a] * K[j])),Nx = mm([[1,0],[dt,1]],mm(P,AK)); P = Q.map((r,a) => r.map((v,j) => v + Nx[a][j]));
  }
  const KF = KS[NI - 1],X = [[1,0]]; for (let i = 0; i < 100; i++) {const x = X[i],u = -(KF[0] * x[0] + KF[1] * x[1]); X.push([x[0] + dt * x[1] + dt * dt / 2 * u,x[1] + dt * u]);}
  T(m,g,16,24,'K per Riccati pass','Riccati 반복마다의 K','g'); T(m,g,250,36,'K1','K1','k'); T(m,g,250,92,'K2','K2','w');
  $(g,'path',{d:'M40 130H460M40 44V130',class:'s n sm'}); $(g,'path',{d:'M40 220H460M40 150V220',class:'s n sm'}); T(m,g,460,172,'position (m)','위치 (m)','m','end');
  const k1 = $(g,'path',{class:'s n sk w4'}),k2 = $(g,'path',{class:'s n sw w4'}),xp = $(g,'path',{class:'s n sf w4'}),dot = CC(g,0,0,5,'g'),r1 = D(g,16,248,'g'),r2 = D(g,16,266,'m');
  const draw = t => {
   const i = Math.round(S(t,.5,4.5) * (NI - 1)),n = Math.round(S(t,5.2,9.2) * 100),ky = v => 130 - v * 28;
   A(k1,{d:poly(KS.map(k => [0,k[0]]),i,(_,j) => 40 + j * 7,ky)}); A(k2,{d:poly(KS.map(k => [0,k[1]]),i,(_,j) => 40 + j * 7,ky)});
   A(xp,{d:t < 5.2 ? '' :poly(X.map(x => [0,x[0]]),n,(_,j) => 40 + j * 4.2,v => 220 - v * 60)}); A(dot,{cx:40 + n * 4.2,cy:220 - X[n][0] * 60,opacity:t < 5.2 ? 0 :1});
   r1(`pass ${i + 1} | K = [${KS[i][0].toFixed(2)}, ${KS[i][1].toFixed(2)}]`); r2(t < 5.2 ? m.t('K stops changing: the cheapest feedback','K가 멈추면 가장 싼 feedback입니다') :m.t(`u = -Kx | position ${X[n][0].toFixed(2)} m`,`u = -Kx | 위치 ${X[n][0].toFixed(2)} m`));
  };
  play(m,g,10.4,9.4,draw);
 });

 R.gs('free-motion-energy',(el,m) => {
  const g = stage(m,'Free motion (tau = 0) of the lesson arm with RK4, q = (0.3, 1.0), qd = (2, -1). With the correct h the kinetic energy stays put; with the Coriolis sign flipped it drifts, slowed 6x.','수업의 팔을 tau = 0으로 RK4 적분합니다(q = (0.3, 1.0), qd = (2, -1)). h가 맞으면 운동에너지가 그대로이고 Coriolis 부호가 뒤집히면 흘러갑니다(6배 느리게).');
  const p = {m1:1,m2:1.5,l1:.5,lc1:.2,lc2:.3,I1:.03,I2:.05},h2 = p.m2 * p.l1 * p.lc2,m22 = p.I2 + p.m2 * p.lc2 ** 2;
  const Mq = q => {const c = Math.cos(q[1]); return [p.I1 + p.m1 * p.lc1 ** 2 + p.m2 * (p.l1 ** 2 + p.lc2 ** 2 + 2 * p.l1 * p.lc2 * c) + p.I2,m22 + h2 * c,m22];};
  const Ek = x => {const M = Mq(x); return .5 * (M[0] * x[2] ** 2 + 2 * M[1] * x[2] * x[3] + M[2] * x[3] ** 2);};
  const run = sg => {
   const f = x => {const M = Mq(x),s2 = h2 * Math.sin(x[1]),b = [sg * s2 * (2 * x[2] * x[3] + x[3] ** 2),-sg * s2 * x[2] ** 2],d = M[0] * M[2] - M[1] ** 2; return [x[2],x[3],(M[2] * b[0] - M[1] * b[1]) / d,(M[0] * b[1] - M[1] * b[0]) / d];};
   const st = (x,k,h) => x.map((z,j) => z + h * k[j]); let x = [.3,1,2,-1],o = [[x.slice(),0]],e0 = Ek(x);
   for (let i = 1; i <= 500; i++) {const h = .002,k1 = f(x),k2 = f(st(x,k1,h / 2)),k3 = f(st(x,k2,h / 2)),k4 = f(st(x,k3,h)); x = x.map((z,j) => z + h / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])); if (i % 5 === 0) o.push([x.slice(),Ek(x) - e0]);} return o;
  };
  const RN = [run(1),run(-1)],CL = ['sk','sw'],BX = 80,BY = 175,SC = 110,PX = 230,ZY = 150,YS = 40 / Math.max(...RN[1].map(o => Math.abs(o[1])));
  T(m,g,16,24,'same arm, same start','같은 팔, 같은 시작','g'); $(g,'path',{d:`M${PX} ${ZY}H460M${PX} 50V230`,class:'s n sm'}); T(m,g,PX + 8,64,'change in kinetic energy (J)','운동에너지 변화 (J)','m');
  const arms = CL.map(c => $(g,'path',{class:'s n w4 ' + c})),cv = CL.map(c => $(g,'path',{class:'s n w4 ' + c})),r1 = D(g,16,248,'k'),r2 = D(g,16,266,'w');
  const draw = t => {
   const i = Math.round(S(t,.6,6.6) * 100);
   RN.forEach((o,k) => {const x = o[i][0],a = x[0] + x[1],x1 = BX + SC * p.l1 * Math.cos(x[0]),y1 = BY - SC * p.l1 * Math.sin(x[0]);
    A(arms[k],{d:`M${BX} ${BY}L${x1} ${y1}L${x1 + SC * p.lc2 * Math.cos(a)} ${y1 - SC * p.lc2 * Math.sin(a)}`,opacity:k ? .8 :1}); A(cv[k],{d:poly(o.map((v,j) => [j,v[1]]),i,j => PX + j * 2.3,v => ZY - v * YS)});});
   r1(m.t('correct h: ΔT = ','맞는 h: ΔT = ') + RN[0][i][1].toExponential(1) + ' J'); r2(m.t('sign flipped: ΔT = ','부호 뒤집음: ΔT = ') + RN[1][i][1].toFixed(2) + ' J');
  };
  play(m,g,10.4,9.5,draw);
 });

 R.gs('energy-falls',(el,m) => {
  const g = stage(m,'PD pendulum, V = kinetic + gravity + spring energy (c = 0.1, kp = 10). Along the motion dV/dt = -(c + kd) w^2, so V falls for kd = 2 and climbs for kd = -1.','PD 진자에서 V는 운동, 중력, 스프링 에너지의 합입니다(c = 0.1, kp = 10). 운동을 따라 dV/dt = -(c + kd) w^2이므로 kd = 2이면 V가 줄고 kd = -1이면 늘어납니다.');
  const GL = 9.81,KP = 10,CS = [[2,2],[-1,.5]],run = (kd,q0) => {let q = q0,w = 0,o = []; for (let i = 0; i <= 5000; i++) {if (i % 20 === 0) o.push([.5 * w * w,GL * (1 - Math.cos(q)),.5 * KP * q * q]); const a = -GL * Math.sin(q) - .1 * w - KP * q - kd * w; w += 1e-3 * a; q += 1e-3 * w;} return o;};
  const RN = CS.map(c => run(c[0],c[1])),Y0 = [112,212],ln = [0,1].map(() => [0,1,2].map(j => $(g,'path',{class:'s n w3 ' + ['sk','sf','sl'][j]})));
  const tot = [0,1].map(k => $(g,'path',{class:'s n w4 ' + ['sk','sb'][k]})),r1 = D(g,16,248,'g'),r2 = D(g,16,266,'m');
  [0,1].forEach(k => {$(g,'path',{d:`M40 ${Y0[k]}H460M40 ${Y0[k] - 74}V${Y0[k]}`,class:'s n sm'}); T(m,g,56,Y0[k] - 60,k ? 'kd = -1: dV/dt = +0.9 w²' :'kd = 2: dV/dt = -2.1 w²',k ? 'kd = -1: dV/dt = +0.9 w²' :'kd = 2: dV/dt = -2.1 w²','g');});
  const MX = RN.map(o => Math.max(...o.map(r => r[0] + r[1] + r[2]))),draw = t => {
   const e = [S(t,.4,4.6),S(t,5.2,9.4)],ni = e.map(v => Math.round(v * 250));
   RN.forEach((o,k) => {const f = r => 60 / MX[k] * r; tot[k].setAttribute('d',poly(o.map((r,j) => [j,r[0] + r[1] + r[2]]),ni[k],j => 40 + j * 1.68,v => Y0[k] - f(v)));
    [0,1,2].forEach(j => ln[k][j].setAttribute('d',poly(o.map((r,i) => [i,r[j]]),ni[k],i => 40 + i * 1.68,v => Y0[k] - f(v))));});
   const i = ni[1] > 0 ? ni[1] :ni[0],k = ni[1] > 0 ? 1 :0,r = RN[k][i],V = r[0] + r[1] + r[2];
   r1(`V = ${V.toFixed(2)} ≈ ${r[0].toFixed(2)} + ${r[1].toFixed(2)} + ${r[2].toFixed(2)}`); r2(m.t('thin: kinetic, gravity, spring. thick: V','가는 선: 운동, 중력, 스프링. 굵은 선: V'));
  };
  play(m,g,10.4,9.6,draw);
 });
})();
