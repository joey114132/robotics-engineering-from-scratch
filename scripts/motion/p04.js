// phase 04 concept loops (480x270) as GSAP timelines; needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,S,SN,hd,fin} = K,DA = 'stroke-dasharray',f2 = x => x.toFixed(2);
 const T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 // D: a text node you set from draw()
 const D = (p,x,y,cls,an) => {const e = $(p,'text',{x,y,'font-size':15,class:cls || '','text-anchor':an || 'start'}); let l = ''; return s => {if (s !== l) e.textContent = l = s;};};
 const stage = (m,en,ko) => {const g = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return g;};
 // a timeline of length E; its time t drives draw(t) (everything on screen is computed from t)
 const play = (m,g,E,rest,draw) => {const tl = m.timeline({repeatDelay:.3}); fin(tl,g,E); m.play(tl,{rest,draw});};

 R.gs('reflected-load',(el,m) => {
  const g = stage(m,'Seen from the motor, the load inertia is J_L / N². The orange disc is that inertia (area = inertia), the green disc is the rotor. With J_R = 2e-5 and J_L = 2e-3 it hides inside the rotor at N = 100.','motor에서 본 부하 관성은 J_L / N²입니다. 주황 원이 그 관성(면적 = 관성)이고 초록 원이 rotor입니다. J_R = 2e-5, J_L = 2e-3이면 N = 100에서 rotor 안에 숨습니다.');
  const JR = 2e-5,JL = 2e-3,CY = 112,RR0 = 44 / Math.sqrt(JL / JR);
  T(m,g,16,24,'The motor feels the load divided by N²','motor는 부하를 N²으로 나눈 값으로 느낍니다','g');
  CC(g,370,CY,44,'f s st'); $(g,'path',{d:hd(314,CY,-52,0),class:'s n sm w3'}); T(m,g,294,CY - 12,'÷ N²','÷ N²','m','middle');
  const seen = CC(g,120,CY,44,'w'),rot = CC(g,120,CY,RR0,'k s st'),inside = CC(g,120,CY,0,'w');
  // Keep the true area scale; a leader identifies the tiny orange disc at N = 100.
  $(g,'path',{d:`M120 ${CY}V62H40`,class:'s n sw'}); CC(g,32,62,4,'w');
  T(m,g,46,57,'orange: J_L / N²','주황: J_L / N²','m');
  T(m,g,120,186,'as the motor feels it','motor가 느끼는 부하','m','middle'); T(m,g,370,186,'real load J_L','실제 부하 J_L','m','middle');
  const r1 = D(g,16,248,'g'),r2 = D(g,16,266,'m');
  const draw = t => {
   const p = SN(S(t,1,3.5)) * .5 + SN(S(t,5,8)) * .5,N = 10 ** (2 * p),jl = JL / N ** 2;
   A(seen,{r:44 / N}); A(rot,{r:RR0}); A(inside,{r:44 / N < RR0 ? 44 / N :0});
   r1(`N = ${N < 10 ? N.toFixed(1) :N.toFixed(0)} | J_L / N² = ${jl.toExponential(1)}`);
   r2(m.t(`(J_R + J_L/N²) / J_R = ${f2((JR + jl) / JR)}`,`(J_R + J_L/N²) / J_R = ${f2((JR + jl) / JR)}`));
  };
  play(m,g,10.6,9.5,draw);
 });

 R.gs('push-modes',(el,m) => {
  const g = stage(m,'The same 2 push on two joints that were both asked for K = 20 (then K = 100). Torque mode gives way by tau_ext / K. Position mode uses the drive inner kp = 400, so it gives way by tau_ext / 400 whatever K says.','같은 2 push를 K = 20(그다음 K = 100)을 요청한 두 관절에 줍니다. torque mode는 tau_ext / K만큼 밀리고 position mode는 drive 안쪽 kp = 400을 쓰므로 K와 상관없이 tau_ext / 400만큼 밀립니다.');
  const J = .1,B = .05,PUSH = 2,KI = 400,KDI = 40;
  const run = (pos,K) => {let q = 0,v = 0,o = [],D_ = 1.4 * Math.sqrt(K * J); for (let i = 0; i < 3000; i++) {const e = i >= 500 ? PUSH :0,tau = pos ? -KI * q - KDI * v :-K * q - D_ * v; v += (tau - B * v + e) / J / 1000; q += v / 1000; if (i % 10 === 0) o.push(q);} return o;};
  const RUNS = [[run(0,20),run(1,20)],[run(0,100),run(1,100)]],PX = [30,270],PY = 130,L = 160,DEG = 180 / Math.PI;
  T(m,g,16,24,'torque mode','torque mode','g'); T(m,g,256,24,'position mode','position mode','g'); $(g,'path',{d:'M240 40V232',class:'s n sm',[DA]:'2 6'});
  T(m,g,462,46,'angle drawn 10x','각도를 10배로 그림','m','end'); const k0 = D(g,16,46,'m'),ar = [0,1].map(i => $(g,'path',{class:'s n w6 ' + ['sw','sk'][i]})),tp = [0,1].map(i => CC(g,0,0,6,'g'));
  PX.forEach(x => {$(g,'path',{d:`M${x} ${PY}h${L}`,class:'s n sm',[DA]:'3 6'}); CC(g,x,PY,7,'g');});
  const pa = PX.map(x => $(g,'path',{class:'s n sf w4'})),rd = [D(g,16,248,'w'),D(g,256,248,'k')],rf = [D(g,16,266,'m'),D(g,256,266,'m')];
  const draw = t => {
   const b = t >= 5 ? 1 :0,s = Math.min(2.99,Math.max(0,t - (b ? 5 :.8))),n = Math.round(s / .01);
   k0(m.t(`K asked for: ${b ? 100 :20}`,`요청한 K: ${b ? 100 :20}`));
   PX.forEach((x,i) => {
    const q = RUNS[b][i][n],ex = x + L * Math.cos(10 * q),ey = PY + L * Math.sin(10 * q);
    A(ar[i],{d:`M${x} ${PY}L${ex} ${ey}`}); A(tp[i],{cx:ex,cy:ey}); A(pa[i],{d:hd(ex,ey + 6,0,36),opacity:s >= .5 ? 1 :0});
    rd[i]((q * DEG).toFixed(2) + m.t('° deflection','° 밀림')); rf[i](s >= 2.2 ? m.t(`feels like ${(PUSH / q).toFixed(0)}`,`${(PUSH / q).toFixed(0)}처럼 느껴짐`) :'');
   });
  };
  play(m,g,10.4,9,draw);
 });

 R.gs('encoder-window',(el,m) => {
  const g = stage(m,'A slow joint (0.1, then 0.3 rad/s) on a 4096-count encoder at 1 kHz. One-sample differences spike by 2 pi / (CPR dt) = 1.53 rad/s. A 20-sample window is smooth but n dt / 2 = 10 ms late.','느린 관절(0.1, 그다음 0.3 rad/s)을 4096 count, 1 kHz로 읽습니다. 한 sample 차분은 2 pi / (CPR dt) = 1.53 rad/s씩 튀고 20 sample window는 매끄럽지만 n dt / 2 = 10 ms 늦습니다.');
  const CPR = 4096,DT = .001,TC = .12,NS = 300,X0 = 40,PX = 1400,Y0 = 200,VY = 80,TW = 2 * Math.PI;
  const th = s => s < TC ? .1 * s :.1 * TC + .3 * (s - TC),c = Array.from({length:NS + 21},(_,i) => Math.floor(th(i * DT) / TW * CPR));
  const est = n => Array.from({length:NS - n + 1},(_,i) => (c[i + n] - c[i]) * TW / CPR / (n * DT)),x = i => X0 + i * DT * PX,y = v => Y0 - v * VY;
  const E1 = est(1),E20 = est(20);
  $(g,'path',{d:`M${X0} ${Y0}h${NS * DT * PX}`,class:'s n sm'}); [0,.1,.2,.3].forEach(s => {$(g,'path',{d:`M${X0 + s * PX} ${Y0}v6`,class:'s n sm'}); T(m,g,X0 + s * PX,Y0 + 24,s ? s + ' s' :'0',s ? s + ' s' :'0','m','middle');});
  $(g,'path',{d:`M${x(0)} ${y(.1)}H${x(TC / DT)}V${y(.3)}H${x(NS)}`,class:'s n sm w3',[DA]:'4 4'}); T(m,g,462,60,'dashed: true speed','점선: 실제 속도','m','end');
  const p1 = $(g,'path',{class:'s n sw w3'}),p2 = $(g,'path',{class:'s n sk w4'}),lg = $(g,'path',{d:hd(x(TC / DT),y(.2) - 8,x(14) - x(0),0),class:'s n sf w4'});
  const hl = D(g,16,24,'g'),r1 = D(g,16,248,'w'),r2 = D(g,16,266,'k');
  const draw = t => {
   const a = Math.round(S(t,.8,3.6) * (NS - 1)),b = Math.round(S(t,4,7.2) * (NS - 20)),P = (E,n,k) => E.slice(0,k + 1).map((v,i) => `${i ? 'L' :'M'}${x(i + n)} ${y(v)}`).join('');
   A(p1,{d:t < .8 ? '' :P(E1,1,a)}); A(p2,{d:t < 4 ? '' :P(E20,20,b)}); A(lg,{opacity:t > 7.2 ? 1 :0});
   hl(t < 4 ? m.t('Whole counts, so the speed jumps','count가 정수라서 속도가 튑니다') :m.t('A longer window: smooth, but late','window가 길수록 매끄럽지만 늦습니다'));
   r1(`n = 1 | step ${(TW / CPR / DT).toFixed(2)} rad/s`); r2(t < 4 ? '' :`n = 20 | step ${(TW / CPR / DT / 20).toFixed(3)} rad/s | lag ${20 * DT / 2 * 1000} ms`);
  };
  play(m,g,9.6,8.5,draw);
 });

 R.gs('delay-budget',(el,m) => {
  const g = stage(m,'J = 0.05, kp = 100. Stage delays add up to the lesson budget of 5.5 ms. The loop is stable only while the total stays under the delay margin, which depends on kd.','J = 0.05, kp = 100입니다. 단계별 지연이 합쳐져 레슨의 budget 5.5 ms가 됩니다. 합이 kd로 정해지는 delay margin 안에 있어야 안정합니다.');
  const KP = 100,J = .05,ST = [['sensor',.5],['filter',2],['bus',1],['compute',.5],['drive',1],['hold',.5]],MS = 40,X0 = 40,BY = 190;
  const dm = kd => {const w = Math.sqrt((kd * kd + Math.sqrt(kd ** 4 + 4 * J * J * KP * KP)) / (2 * J * J)); return Math.atan(kd * w / KP) / w * 1000;};
  const sim = (kd,d) => {const n = 4000,lag = Math.round(d * 10),q = new Float64Array(n + 1).fill(.1),v = new Float64Array(n + 1); for (let k = 0; k < n; k++) {const j = Math.max(k - lag,0); v[k + 1] = v[k] + 1e-4 * (-KP * q[j] - kd * v[j]) / J; q[k + 1] = q[k] + 1e-4 * v[k + 1];} return q;};
  const cum = ST.map((s,i) => ST.slice(0,i + 1).reduce((a,b) => a + b[1],0)),SIM = [[20,0],...cum.map(c => [20,c])].map(a => sim(a[0],a[1])),S8 = sim(8,5.5);
  $(g,'path',{d:`M${X0} 95H460`,class:'s n sm'}); T(m,g,462,60,'q after a kick','킥 뒤의 q','m','end');
  const cv = $(g,'path',{class:'s n w3'}),segs = ST.map(() => RR(g,X0,BY,0,22,3,'k s sm')),mk = $(g,'path',{class:'s n sb w4'});
  const ml = D(g,X0,BY - 12,'m'),r1 = D(g,16,248,'g'),r2 = D(g,16,266,'m');
  const draw = t => {
   const hi = t >= 7.2,kd = hi ? 8 :20,mx = dm(20) + (dm(8) - dm(20)) * SN(S(t,7.2,8)),done = hi ? 6 :ST.filter((s,i) => t >= 1.5 + i).length,tot = done ? cum[done - 1] :0,q = hi ? S8 :SIM[done];
   ST.forEach((s,i) => A(segs[i],{x:X0 + (cum[i] - s[1]) * MS,width:s[1] * MS * (hi ? 1 :S(t,1 + i,1.5 + i)),class:(cum[i] > mx ? 'x' :'k') + ' s sm'}));
   A(mk,{d:`M${X0 + mx * MS} ${BY - 8}V${BY + 30}`}); ml(`delay margin ${mx.toFixed(1)} ms`);
   A(cv,{d:Array.from({length:130},(_,i) => `${i ? 'L' :'M'}${X0 + i * 3.2} ${Math.max(40,Math.min(150,95 - q[i * 30] * 275))}`).join(''),class:'s n w3 ' + (tot > mx ? 'sb' :'sk')});
   r1(`kd = ${kd}` + (done && !hi ? ` | + ${ST[done - 1][0]} ${ST[done - 1][1]} ms` :''));
   r2(m.t(`loop delay ${tot.toFixed(1)} ms ` + (tot > mx ? '> margin: it grows' :'< margin: it settles'),`loop delay ${tot.toFixed(1)} ms ` + (tot > mx ? '> margin: 커집니다' :'< margin: 가라앉습니다')));
  };
  play(m,g,10.4,9.5,draw);
 });
})();
