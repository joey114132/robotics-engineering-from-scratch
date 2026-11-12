// phase 15 concept animations (480x270) as GSAP timelines; needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,fin} = K,T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15),N = (m,p,x,y,s,c,an) => T(m,p,x,y,s,s,c,an);
 const D = (p,x,y,cls,an) => {const e = $(p,'text',{x,y,'font-size':15,class:cls || '','text-anchor':an || 'start'}); let l = ''; return s => {if (s !== l) {l = s; e.textContent = s;}};};
 const stage = (m,en,ko) => {const q = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return q;};
 const f2 = x => x.toFixed(2),clamp = (x,a) => Math.max(-a,Math.min(a,x));

 // lesson 01: simulate('stuck') at 1 ms: the reading freezes, the true joint runs on, the cheap alarm fires long before the stop
 R.gs('stuck-sensor',(el,m) => {
  const g = stage(m,'Lesson model: kp = 40, kd = 4, target 1 rad, hard stops at ±2 rad. The sensor freezes at 0.30 s. Shown 5x slower.','레슨 모델입니다. kp = 40, kd = 4, 목표 1 rad, ±2 rad에 hard stop이 있습니다. 센서는 0.30초에 얼어붙습니다. 5배 느립니다.');
  const X = q => 240 + q * 95,Y = 130,rows = [];
  let q = 0,v = 0,held = null,prev = null,ch = 0,al = null,lm = null;
  for (let i = 0; i < 1600; i++) {
   let qm = q,vm = v; if (i >= 300) {held = held || [q,v]; qm = held[0]; vm = held[1];}
   if (qm !== prev) {prev = qm; ch = i;}
   const u = clamp(40 * (1 - qm) - 4 * vm,10);
   if (al === null && i - ch >= 50 && Math.abs(u) > .5) al = i / 1000;   // reading flat for 50 ms while torque is applied
   v += (u - .2 * v) / .5 * .001; q += v * .001; if (Math.abs(q) >= 2) {q = 2; v = 0; lm = lm || i / 1000;}
   rows.push([q,qm,u]);
  }
  [-2,2].forEach(w => {RR(g,X(w) - 4,Y - 34,8,68,2,'x'); N(m,g,X(w),Y + 56,'stop ' + w,'m','middle');}); $(g,'line',{x1:X(-2),y1:Y,x2:X(2),y2:Y,class:'s sm w3'});
  $(g,'line',{x1:X(1),y1:Y - 12,x2:X(1),y2:Y + 12,class:'s sm w3'}); T(m,g,X(1),Y + 36,'target','목표','m','middle');
  const ax = X(rows[Math.round(al * 1000)][0]),af = $(g,'g',{opacity:0}); $(af,'line',{x1:ax,y1:Y - 30,x2:ax,y2:Y + 16,class:'s sb w3'}); N(m,af,ax,Y - 36,'alarm','x','middle');
  const ring = CC(g,X(0),Y,18,'n s st w3'),dot = CC(g,X(0),Y,10,'f');
  CC(g,24,56,8,'f'); T(m,g,40,61,'joint (true)','관절(실제)','g'); CC(g,200,56,8,'n s st w3'); T(m,g,216,61,'reading the controller uses','컨트롤러가 쓰는 센서값','g');
  const h = D(g,16,26,'g'),r1 = D(g,16,216,'g'),r2 = D(g,16,236,'g'),r3 = D(g,16,258,'k'),o = {s:0};
  const draw = () => {
   const r = rows[Math.min(1599,Math.round(o.s * 1000))],hit = o.s >= lm;
   A(dot,{cx:X(r[0])}); A(ring,{cx:X(r[1])}); A(af,{opacity:o.s >= al ? 1 :0});
   h(hit ? m.t('The joint hits the stop at ' + f2(lm) + ' s','관절이 ' + f2(lm) + '초에 stop에 닿습니다') :o.s >= al ? m.t('Alarm at ' + f2(al) + ' s: reading flat, torque on','alarm ' + f2(al) + '초: 토크는 주는데 값이 그대로') :o.s >= .3 ? m.t('The sensor freezes at 0.30 s','센서가 0.30초에 얼어붙습니다') :m.t('Healthy: the reading follows the joint','정상: 센서값이 관절을 따라갑니다'));
   r1('t = ' + f2(o.s) + ' s   ' + m.t('torque ','토크 ') + r[2].toFixed(1) + ' Nm'); r2(m.t('joint ','관절 ') + f2(r[0]) + ' rad   ' + m.t('reading ','센서값 ') + f2(r[1]) + ' rad');
   r3(hit ? m.t('Warned ' + f2(lm - al) + ' s before the stop','stop보다 ' + f2(lm - al) + '초 먼저 경고했습니다') :'');
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.4);
  tl.to(o,{s:1.5,duration:7.5,ease:'none'},.6);   // 5x slow-motion
  m.play(tl,{rest:9,draw});
 });

 // lesson 03: simulate(MISMATCHED): the planner asks 3.0 rad/s, the drive allows 1.5, and nothing says so
 R.gs('silent-clamp',(el,m) => {
  const g = stage(m,'Lesson setup: speed limits 3.0, 3.0 and 1.5 rad/s, goal 1.4 rad. The tightest layer wins and logs nothing. Shown 4x slower.','레슨 설정입니다. 속도 한계는 3.0, 3.0, 1.5 rad/s이고 목표는 1.4 rad입니다. 가장 빡빡한 층이 이기고 기록은 남기지 않습니다. 4배 느립니다.');
  const rows = [],X = q => 40 + q * 200;
  let q = 0,v = 0,ref = 0;
  for (let i = 0; i < 1700; i++) {
   ref += clamp(1.4 - ref,.003);   // planner rate limit 3.0 rad/s
   let u = clamp(clamp(60 * (clamp(ref,1.8) - q) - 6 * v,10),6);   // controller, then drive torque clamps
   if (v >= 1.5) u = Math.min(u,0);   // drive refuses to push past its speed limit
   v += (u - .2 * v) / .5 * .001; q += v * .001; rows.push([ref,q,v]);
  }
  [['planner',3],['controller',3],['drive',1.5]].forEach((l,i) => {const y = 44 + i * 24; N(m,g,16,y + 12,l[0],'g'); RR(g,110,y,l[1] * 60,14,3,i < 2 ? 'l' :'x'); N(m,g,116 + l[1] * 60,y + 12,l[1].toFixed(1),'m');});
  T(m,g,16,140,'joint','관절','g'); const sp = RR(g,110,128,0,14,3,'f'),sv = D(g,300,140,'g');
  $(g,'line',{x1:200,y1:38,x2:200,y2:148,class:'s sb w3'}); T(m,g,236,104,'clamped, nothing logged','잘렸지만 기록은 없습니다','x');
  $(g,'line',{x1:40,y1:210,x2:X(1.4),y2:210,class:'s sm w3'}); $(g,'line',{x1:X(1.4),y1:196,x2:X(1.4),y2:224,class:'s sm w3'}); T(m,g,X(1.4),244,'goal 1.4','목표 1.4','m','middle');
  const lag = $(g,'line',{x1:40,y1:210,x2:40,y2:210,class:'s sb w4'}),rf = CC(g,40,210,13,'n s st w3'),jt = CC(g,40,210,8,'f');
  const h = D(g,16,26,'g'),rd = D(g,16,184,'g'),o = {s:0};
  const draw = () => {
   const r = rows[Math.round(o.s * 1000)],gap = Math.abs(r[0] - r[1]),sd = Math.abs(r[2]);
   A(sp,{width:sd * 60}); sv(f2(sd) + ' rad/s'); A(rf,{cx:X(r[0])}); A(jt,{cx:X(r[1])}); A(lag,{x1:X(r[1]),x2:X(r[0])});
   h(o.s < 1.4 / 3 ? m.t('The planner asks for 3.0 rad/s','planner는 3.0 rad/s를 요청합니다') :gap > .02 ? m.t('The planner is done; the joint is behind','planner는 끝났고 관절은 뒤에 있습니다') :m.t('The joint has caught up','관절이 따라잡았습니다'));
   rd('t = ' + f2(o.s) + ' s   ' + m.t('lag ','지연 ') + f2(gap) + ' rad');
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.6);
  tl.to(o,{s:1.6,duration:6.4,ease:'none'},.6);   // 4x slow-motion
  m.play(tl,{rest:2.6,draw});
 });

 // lesson 04: the same closed loop on a fake clock the test advances and on a real clock that has to sleep
 R.gs('fake-clock',(el,m) => {
  const g = stage(m,'PD kp = 40, kd = 4, 300 steps of 0.01 s. The test owns the clock, so 3.00 s of robot time needs no sleeping. A gap over the 0.05 s timeout gives zero torque.','PD kp = 40, kd = 4, 0.01초씩 300 step입니다. 테스트가 시계를 쥐고 있어 로봇 시간 3.00초가 기다림 없이 지나갑니다. 갱신 간격이 timeout 0.05초를 넘으면 토크가 0입니다.');
  const ct = {t:null,q:0},upd = (now,qm) => {   // Controller.update from the lesson
   const stale = ct.t !== null && now - ct.t > .05,dq = ct.t !== null && now > ct.t ? (qm - ct.q) / (now - ct.t) : 0; ct.t = now; ct.q = qm;
   return stale ? 0 :clamp(40 * (1 - qm) - 4 * dq,10);
  };
  let q = 0,v = 0; const Q = [0]; for (let k = 1; k <= 300; k++) {const u = upd(k * .01,q); v += (u - .2 * v) / .5 * .01; q += v * .01; Q.push(q);}
  const late = upd(3.06,Q[300]),o = {f:0,r:0,b:0};
  const row = (y,name,call) => {
   N(m,g,16,y + 22,name + ' clock','g'); RR(g,120,y,336,60,4,'c s sm'); $(g,'line',{x1:120,y1:y + 12,x2:456,y2:y + 12,class:'s sm','stroke-dasharray':'3 4'});
   const p = $(g,'path',{class:'s n sf w3'}),rd = D(g,16,y + 80,'g'),dn = D(g,464,y + 80,'k','end');
   return t => {const n = Math.floor(t * 100 + 1e-6); A(p,{d:'M' + Q.slice(0,n + 1).map((c,i) => (120 + i * 1.12).toFixed(1) + ' ' + (y + 60 - c / 1.25 * 60).toFixed(1)).join('L')}); rd(call + '(0.01) x 300   t = ' + f2(t) + ' s'); dn(t >= 3 ? m.t('passed','통과') :'');};
  };
  const a = row(40,'fake','advance'),b = row(140,'real','sleep'),h = D(g,16,26,'g'),ex = D(g,16,262,'k');
  const draw = () => {
   a(o.f); b(o.r);
   h(o.f < 3 ? m.t('The test advances the clock itself','테스트가 시계를 직접 넘깁니다') :o.r < 3 ? m.t('Fake clock done; real clock sleeping','fake clock은 끝났고 real clock은 잡니다') :m.t('Same trace; only one of them waited','같은 trace이고 한쪽만 기다렸습니다'));
   ex(o.b ? m.t('advance(0.06) > timeout 0.05 s: torque = ' + f2(late) + ' Nm','advance(0.06) > timeout 0.05초: 토크 = ' + f2(late) + ' Nm') :'');
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,9);
  tl.to(o,{f:3,duration:1,ease:'power2.out'},.6).to(o,{r:3,duration:3,ease:'none'},.6).set(o,{b:1},5);
  m.play(tl,{rest:7.5,draw});
 });
})();
