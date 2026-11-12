// phase 10 concept animations (480x270): capture-step, step-vs-speed, gust-integral; needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,cl,hd,fin} = K;
 const T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 const D = (p,x,y,cls,an,sz) => {const e = $(p,'text',{x,y,'font-size':sz || 15,class:cls || '','text-anchor':an || 'start'}); let l = ''; const f = s => {if (s !== l) {l = s; e.textContent = s;}}; f.e = e; return f;};
 const stage = (m,en,ko) => {const q = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return q;};
 const TC = Math.sqrt(.9 / 9.81);                       // h = 0.9 m, Tc = sqrt(h/g)
 const lipm = (x,v,p,t) => {const a = x - p,c = Math.cosh(t / TC),s = Math.sinh(t / TC); return [p + a * c + TC * v * s,a * s / TC + v * c];};

 // 10/01: same 0.4 m/s push, ankle only vs a step onto the capture point at 0.1 s (RK4 of x'' = (g/h)(x - p), as in code/main.py)
 R.gs('capture-step',(el,m) => {
  const g = stage(m,'The same 0.4 m/s push twice. The ankle can only move the force point inside the foot (half-length 0.05 m), and the capture point is already outside it. A step onto the capture point at 0.1 s freezes it and the body stops over the new foot. Body heights are not to scale.','같은 0.4 m/s 밀림을 두 번 보여 줍니다. 발목은 힘의 작용점을 발 안(반길이 0.05 m)에서만 옮길 수 있는데 capture point는 이미 그 밖입니다. 0.1초에 capture point로 발을 내디디면 capture point가 멈추고 몸이 새 발 위에서 멈춥니다. 몸 높이는 축척이 아닙니다.');
  const sim = step => {let x = 0,v = .4,p0 = null; const out = [[x,v,0,x + v * TC]];
   for (let i = 0; i < 1000; i++) {const xi = x + v * TC; let p = cl(xi,-.05,.05);
    if (step && i >= 100) {if (p0 === null) p0 = xi; p = p0;}
    const f = s => [s[1],9.81 / .9 * (s[0] - p)],a = [x,v],k1 = f(a),k2 = f([a[0] + .0005 * k1[0],a[1] + .0005 * k1[1]]),k3 = f([a[0] + .0005 * k2[0],a[1] + .0005 * k2[1]]),k4 = f([a[0] + .001 * k3[0],a[1] + .001 * k3[1]]);
    x += .001 / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); v += .001 / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); out.push([x,v,p,x + v * TC]);} return {samples:out,step:p0};};
  const PX = 200,sx = x => 36 + x * PX,BH = 62,GY = [118,238],SIM = [sim(0),sim(1)];
  const lane = (y,i) => {
   $(g,'line',{x1:0,y1:y,x2:480,y2:y,class:'s sm w3'}); RR(g,sx(-.05),y - 3,.1 * PX,6,2,'f s st');
   return {nf:RR(g,0,y - 3,.1 * PX,6,2,'k s sk'),leg:$(g,'line',{class:'s st w4'}),zm:CC(g,0,y,5,'g'),xi:$(g,'path',{d:'M0 -9L8 0L0 9L-8 0Z',class:'k s sk'}),body:CC(g,0,y - BH,9,'f s st'),
    a:D(g,16,y - 96,'g'),b:D(g,16,y - 76,'m')};};
  const L = GY.map(lane),push = $(g,'path',{class:'s n sw w6'});
  const draw = t => {
   const ts = cl((t - 1.4) * .45,0,1),i = Math.round(ts * 1000);
   A(push,{d:hd(4,GY[0] - BH,28,0) + hd(4,GY[1] - BH,28,0),opacity:t < 1.4 ? cl(t / .5) :0});
   L.forEach((l,k) => {
    const [x,v,p,xi] = SIM[k].samples[i],on = k && i >= 100,support = on ? SIM[k].step :p,inside = Math.abs(xi - (on ? SIM[k].step :0)) <= .05;
    A(l.body,{cx:sx(x)}); A(l.leg,{x1:sx(x),y1:GY[k] - BH,x2:sx(support),y2:GY[k]}); A(l.zm,{cx:sx(support)}); A(l.xi,{transform:`translate(${sx(xi)} ${GY[k] - 14})`,class:(inside ? 'k s sk' :'x s sb')});
    A(l.nf,{x:sx(SIM[k].step) - .05 * PX,opacity:on ? 1 :0});
    l.a(k ? m.t('Step onto ξ at 0.1 s','0.1초에 ξ로 발을 내디딤') :m.t('Ankle only','발목만 사용'));
    l.b(k ? (on ? m.t(`x = ${x.toFixed(2)} m, speed ${v.toFixed(2)} m/s`,`x = ${x.toFixed(2)} m, 속도 ${v.toFixed(2)} m/s`) :m.t(`ξ = ${xi.toFixed(2)} m, foot ±0.05 m`,`ξ = ${xi.toFixed(2)} m, 발 ±0.05 m`))
     :(inside ? m.t(`ξ = ${xi.toFixed(2)} m: inside the foot`,`ξ = ${xi.toFixed(2)} m: 발 안`) :m.t(`ξ = ${xi.toFixed(2)} m: outside the foot, x = ${x.toFixed(2)} m`,`ξ = ${xi.toFixed(2)} m: 발 밖, x = ${x.toFixed(2)} m`)));
   });
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,9); m.play(tl,{rest:8,draw});
 });

 // 10/02: deadbeat foot placement vs steps scaled to 60% (walk() in code/main.py: T 0.4 s, h 0.9 m, target 0.6 m/s, start x -0.05 m, 0.3 m/s)
 R.gs('step-vs-speed',(el,m) => {
  const g = stage(m,'Same start, same 0.6 m/s target, six stances of 0.4 s, played 2.7x slow. Deadbeat steps (the solved foot) lock the speed at 0.6 m/s from the second step. Steps scaled to 60% let the body run ahead of its feet, faster every step.','같은 출발과 0.6 m/s 목표로 0.4초짜리 stance 여섯 번을 2.7배 느리게 보여 줍니다. deadbeat 발(풀어서 구한 발 위치)은 두 번째 걸음부터 속도를 0.6 m/s로 고정합니다. 걸음을 60%로 줄이면 몸이 발보다 앞서 달려 걸음마다 빨라집니다.');
  const T0 = .4,walk = sc => {let foot = 0,x = -.05,v = .3; const out = [];
   for (let k = 0; k < 6; k++) {out.push({x,v,foot}); [x,v] = lipm(x,v,foot,T0); foot += sc * ((x - (.6 - v * Math.cosh(T0 / TC)) * TC / Math.sinh(T0 / TC)) - foot);} return out;};
  const W = [walk(1),walk(.6)],sx = x => 24 + x * 100,GY = [112,232],BH = 52;
  const lane = y => {$(g,'line',{x1:0,y1:y,x2:480,y2:y,class:'s sm w3'});
   return {ft:W[0].map(() => RR(g,0,y - 3,10,6,2,'f s st')),leg:$(g,'line',{class:'s st w4'}),body:CC(g,0,y - BH,9,'f s st'),a:D(g,16,y - 90,'g'),b:D(g,16,y - 70,'m')};};
  const L = GY.map(lane);
  const draw = t => {
   const u = cl((t - 1) * .37,0,2.4),k = Math.min(5,Math.floor(u / T0)),tau = u - k * T0;
   L.forEach((l,i) => {
    const w = W[i][k],[x,v] = lipm(w.x,w.v,w.foot,tau),step = k ? w.foot - W[i][k - 1].foot :null;
    W[i].forEach((q,j) => A(l.ft[j],{x:sx(q.foot) - 5,opacity:j <= k ? 1 :0,class:(j === k ? 'k s sk' :'f s st')}));
    A(l.body,{cx:sx(x)}); A(l.leg,{x1:sx(x),y1:GY[i] - BH,x2:sx(w.foot),y2:GY[i]});
    l.a(i ? m.t('Steps scaled to 60%','걸음을 60%로 줄임') :m.t('Deadbeat steps','deadbeat 걸음'));
    l.b(m.t(`speed ${v.toFixed(2)} m/s · step ${step === null ? '–' :step.toFixed(2) + ' m'}`,`속도 ${v.toFixed(2)} m/s · 걸음 ${step === null ? '–' :step.toFixed(2) + ' m'}`));
   });
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,9.8); m.play(tl,{rest:8.5,draw});
 });

 // 10/04: one-second gust (0.1 N m) on a planar pitch loop, PD vs angle P + rate PI cascade (I 0.004, kp 0.9, kd 0.084, ki 0.5; tilt drawn 3x)
 R.gs('gust-integral',(el,m) => {
  const g = stage(m,'A 1 s gust of 0.1 N m on a pitch loop, played 2x slow with tilt drawn 3x. PD holds a steady tilt until the gust ends. The cascade stores the gust in its integral, so the tilt returns to zero while the gust is still on, then swings the other way when the gust stops.','피치 루프에 0.1 N m 돌풍이 1초 불 때입니다. 2배 느리게 보여 주고 기울기는 3배로 그렸습니다. PD는 돌풍이 끝날 때까지 일정하게 기운 채 버팁니다. cascade는 돌풍을 integral에 저장해서 돌풍 중에 기울기가 0으로 돌아오고 돌풍이 멈추면 반대로 흔들립니다.');
  const I = .004,KP = .9,KD = .084,KI = .5,gust = t => t >= .5 && t < 1.5 ? .1 :0;
  const sim = cas => {let th = 0,w = 0,z = 0; const out = [[0,0]];
   for (let i = 0; i < 3000; i++) {const t = i * .001; let tau;
    if (cas) {const e = KP / KD * (0 - th) - w; z += e * .001; tau = KD * e + KI * z;} else tau = KP * (0 - th) - KD * w;
    w += (tau + gust(t)) / I * .001; th += w * .001; out.push([th / Math.PI * 180,cas ? KI * z :0]);} return out;};
  const S = [sim(0),sim(1)],CX = [120,360],DY = 96;
  const lane = (cx,i) => {
   const d = $(g,'g',{}); RR(d,-60,-4,120,8,4,'f s st'); [-50,50].forEach(x => $(d,'ellipse',{cx:x,cy:-14,rx:16,ry:3,class:'d'})); CC(d,0,0,3,'g');
   const ga = $(g,'path',{class:'s n sw w6'}); A(ga,{d:hd(cx + 52,DY - 52,0,36)});
   if (i) {RR(g,cx - 80,160,160,12,3,'n s sm'); T(m,g,cx,152,'stored integral','저장된 integral','m','middle');} else T(m,g,cx,152,'no integral term','integral 항 없음','m','middle');
   return {d,ga,bar:RR(g,cx - 80,160,0,12,3,'k'),tilt:D(g,cx,208,'g','middle',30),a:D(g,cx,22,'g','middle')};};
  const L = CX.map(lane);
  RR(g,20,240,440,18,4,'n s sm'); const gw = RR(g,20 + 440 * .5 / 3,240,440 / 3,18,4,'l'),cur = $(g,'line',{y1:236,y2:262,class:'s sw w4'}); T(m,g,20 + 440 * 1 / 3,254,'gust','돌풍','g','middle');
  const draw = t => {
   const ts = cl((t - .6) * .5,0,3),i = Math.round(ts * 1000),on = ts >= .5 && ts < 1.5;
   A(cur,{x1:20 + 440 * ts / 3,x2:20 + 440 * ts / 3});
   L.forEach((l,k) => {const [deg,it] = S[k][i];
    A(l.d,{transform:`translate(${CX[k]} ${DY}) rotate(${3 * deg})`}); A(l.ga,{opacity:on ? 1 :0}); A(l.bar,{width:cl(Math.abs(it) / .1) * 160});
    l.tilt(`${(Math.abs(deg) < .05 ? 0 :deg).toFixed(1)}°`); l.a(k ? m.t('Cascade with integral','integral이 있는 cascade') :m.t('PD loop','PD 루프'));});
  };
  // Last sample before the gust ends: PD 6.366°, cascade 0.048°, integral still stored.
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,10.5); m.play(tl,{rest:.6 + 2 * 1.499,draw});
 });
})();
