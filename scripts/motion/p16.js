// phase 16 concept animations (480x270) as GSAP timelines; needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,cl,fin} = K,T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15),N = (m,p,x,y,s,c,an) => T(m,p,x,y,s,s,c,an);
 const D = (p,x,y,cls,an) => {const e = $(p,'text',{x,y,'font-size':15,class:cls || '','text-anchor':an || 'start'}); let l = ''; return s => {if (s !== l) {l = s; e.textContent = s;}};};
 const stage = (m,en,ko) => {const q = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return q;};
 const f1 = x => x.toFixed(1),f2 = x => x.toFixed(2),ip = (P,ts,s) => {let i = 0; while (i < ts.length - 2 && s > ts[i + 1]) i++; const u = cl((s - ts[i]) / (ts[i + 1] - ts[i])); return [P[i][0] + (P[i + 1][0] - P[i][0]) * u,P[i][1] + (P[i + 1][1] - P[i][1]) * u];};

 // lesson 01: static equilibrium of the lesson's arm at B while the gravity feedforward is turned down: kp (qd - q) = g(q) - ff g(qd)
 R.gs('ff-sag-knob',(el,m) => {
  const g = stage(m,'Lesson arm, kp = 150, place point B = (0.15, 0.50) m. The arm settles where kp (qd - q) = g(q) - ff g(qd). Pass line: 5 mm.','레슨의 팔입니다. kp = 150, 놓는 점 B = (0.15, 0.50) m입니다. 팔은 kp (qd - q) = g(q) - ff g(qd)인 곳에서 멈춥니다. 합격선은 5 mm입니다.');
  const G = 9.81,fk = q => [.4 * (Math.cos(q[0]) + Math.cos(q[0] + q[1])),.4 * (Math.sin(q[0]) + Math.sin(q[0] + q[1]))];
  const grav = q => {const t2 = .2 * G * Math.cos(q[0] + q[1]); return [.8 * G * Math.cos(q[0]) + t2,t2];};
  const B = [.15,.5],c2 = (B[0] ** 2 + B[1] ** 2 - .32) / .32,s2 = Math.sqrt(1 - c2 * c2),qd = [Math.atan2(B[1],B[0]) - Math.atan2(.4 * s2,.4 + .4 * c2),Math.atan2(s2,c2)];
  const settle = ff => {let q = qd; for (let i = 0; i < 60; i++) {const a = grav(q),b = grav(qd); q = [qd[0] - (a[0] - ff * b[0]) / 150,qd[1] - (a[1] - ff * b[1]) / 150];} return q;};
  const P = p => [40 + p[0] * 230,206 - p[1] * 230],pl = q => 'M' + [[0,0],[.4 * Math.cos(q[0]),.4 * Math.sin(q[0])],fk(q)].map(p => P(p).join(' ')).join('L');
  CC(g,40,206,6,'g'); N(m,g,P(B)[0] - 18,P(B)[1] - 6,'B','g'); const ghost = $(g,'path',{class:'s n sm w3','stroke-dasharray':'3 5'}),live = $(g,'path',{class:'s n sf w6'});
  const bx = 300,by = 44,cx = bx + 80,cy = by + 80; RR(g,bx,by,160,160,10,'c s sl'); $(g,'path',{d:`M${cx - 10} ${cy}h20M${cx} ${cy - 10}v20`,class:'s sm'}); CC(g,cx,cy,15,'n s sk w3'); N(m,g,cx,by + 150,'ring = 5 mm','m','middle');
  const dot = CC(g,cx,cy,6,'f'),lead = $(g,'line',{class:'s sm'}),kn = CC(g,40,250,9,'f'); $(g,'line',{x1:40,y1:250,x2:440,y2:250,class:'s sm w3'}); N(m,g,40,268,'ff 1','m','middle'); N(m,g,440,268,'ff 0','m','middle');
  const h = D(g,16,26,'g'),r1 = D(g,16,228,'g'),ok = D(g,464,228,'k','end'),no = D(g,464,228,'x','end'),o = {f:1};
  const draw = () => {
   const q = settle(o.f),t = fk(q),dx = (t[0] - B[0]) * 3000,dy = (t[1] - B[1]) * 3000,e = Math.hypot(dx,dy) / 3,tp = P(t);
   A(live,{d:pl(q)}); A(ghost,{d:pl(qd)}); A(dot,{cx:cx + dx,cy:cy - dy,class:e < 5 ? 'k' :'x'}); A(lead,{x1:tp[0],y1:tp[1],x2:bx,y2:cy}); A(kn,{cx:40 + (1 - o.f) * 400});
   h(m.t('Turn the gravity feedforward down','gravity feedforward를 줄여 봅니다')); r1('ff ' + f2(o.f) + m.t('   place error ','   놓는 오차 ') + f1(e) + ' mm');
   ok(e < 5 ? 'PASS' :''); no(e < 5 ? '' :'FAIL');
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,9.6);
  tl.to(o,{f:0,duration:5.5,ease:'power1.inOut'},1.6);
  m.play(tl,{rest:8.4,draw});
 });

 // lesson 02: the same route and wheel error with and without a landmark fix (data: the lesson's drive(), one sample every 3 s)
 R.gs('odometry-drift',(el,m) => {
  const g = stage(m,'Wheel speed error 3%, turn bias 0.03 rad/s. Ring: where the robot believes it is. Dot: where it is. Shown 4x faster.','바퀴 속도 오차 3%, 회전 편향 0.03 rad/s입니다. 고리는 로봇이 믿는 위치이고 점은 실제 위치입니다. 4배 빠릅니다.');
  const tN = [0,3,6,9,12,15,18,21,24,27,30,31.4],tF = [0,3,6,9,12,15,18,21,24,27,30,32.15],tT = [0,3,6,9];
  const NE = [[1.53,1.5],[2.15,3.08],[2.67,4.84],[3.32,6.57],[4.73,7.35],[5.55,5.74],[6.14,3.98],[7.21,2.61],[8.21,3.89],[8.45,5.72],[8.8,7.54],[8.96,8.36]],NT = [[1.53,1.5],[2.22,3.01],[2.98,4.64],[3.98,6.13]];
  const FE = [[1.52,1.5],[2.15,3.01],[2.68,4.76],[3.32,6.41],[4.56,7.38],[5.48,5.95],[6.03,4.22],[6.95,2.71],[8.12,3.63],[8.4,5.34],[8.73,7.06],[8.93,8.39]],FT = [[1.53,1.5],[2.14,3.02],[2.67,4.73],[3.3,6.42],[4.58,7.39],[5.48,5.92],[6.02,4.2],[6.91,2.7],[8.17,3.56],[8.43,5.34],[8.73,7.12],[8.96,8.36]];
  const route = [[1.5,1.5],[3.62,7.38],[4.88,7.38],[6.62,2.62],[7.88,2.62],[9,8.5]],o = {s:0};
  const panel = (ox,en,ko,E,eT,T2,tT2,crash) => {
   const X = p => [ox + p[0] * 21,254 - p[1] * 21],gp = X([9,8.5]); RR(g,ox,44,210,210,6,'c s sm');
   [[4,0],[7,3]].forEach(w => {const a = X([w[0],w[1] + 7]); RR(g,a[0],a[1],10.5,147,0,'m');});   // walls: 0.5 m wide, 7 m long
   $(g,'path',{d:'M' + route.map(p => X(p).join(' ')).join('L'),class:'s n sl','stroke-dasharray':'3 4'}); RR(g,gp[0] - 5,gp[1] - 5,10,10,2,'k');
   T(m,g,ox + 105,38,en,ko,'g','middle'); const gap = $(g,'line',{class:'s sb w3'}),ring = CC(g,0,0,9,'n s st w3'),dot = CC(g,0,0,5,'f'),rd = D(g,ox + 4,268,'g');
   return () => {
    const b = X(ip(E,eT,o.s)),t = X(ip(T2,tT2,o.s)),err = Math.hypot(b[0] - t[0],b[1] - t[1]) / 21,hit = crash && o.s >= crash,end = !crash && o.s >= 32,ge = Math.hypot(t[0] - gp[0],t[1] - gp[1]) / 21;
    A(ring,{cx:b[0],cy:b[1]}); A(dot,{cx:t[0],cy:t[1],class:hit ? 'x' :'f'}); A(gap,{x1:b[0],y1:b[1],x2:t[0],y2:t[1]});
    rd(hit ? m.t('wall, belief off ' + f1(err) + ' m','충돌, 믿음과 ' + f1(err) + ' m 차이') :end ? m.t('goal error ' + f2(ge) + ' m','목표 오차 ' + f2(ge) + ' m') :m.t('belief error ' + f2(err) + ' m','믿음 오차 ' + f2(err) + ' m'));
   };
  };
  const a = panel(8,'no fix','보정 없음',NE,tN,NT,tT,9),b = panel(262,'fix every 1 s','1초마다 보정',FE,tF,FT,tF,0),h = D(g,16,20,'g');
  const draw = () => {a(); b(); h(o.s < 9 ? m.t('Both steer by what they believe','둘 다 믿는 위치로 조향합니다') :m.t('Left hit a wall; its display says on the path','왼쪽은 벽에 닿았는데 화면은 경로 위입니다'));};
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,9.4);
  tl.to(o,{s:32.15,duration:8,ease:'none'},.6);
  m.play(tl,{rest:8.6,draw});
 });

 // lesson 03: the wrapper clips a 40 Nm spike to 3 Nm (data: the lesson's rollout() with glitch {30: 40}, every 3rd step = 0.06 s)
 R.gs('spike-wrapper',(el,m) => {
  const g = stage(m,'One +40 Nm spike on the policy action at 0.6 s. Torque limit 3 Nm, joint limit 1.3 rad, target 1.0 rad. Shown 4x slower.','0.6초에 정책 action에 +40 Nm 스파이크가 한 번 들어갑니다. 토크 한계 3 Nm, 관절 한계 1.3 rad, 목표 1.0 rad입니다. 4배 느립니다.');
  const Q = [[0,.01,.03,.06,.1,.16,.21,.28,.35,.41,.5,.61,.71,.8,.88,.96,1.03,1.09,1.14,1.19,1.23,1.26,1.29,1.32,1.34,1.35,1.36,1.35,1.34,1.32,1.3,1.27,1.24,1.22],[0,0,.02,.04,.07,.11,.17,.23,.29,.36,.43,.5,.56,.62,.67,.72,.77,.8,.84,.87,.9,.92,.94,.95,.97,.98,.99,.99,1,1,1.01,1.01,1.01,1.01]];
  const X = q => 40 + q * 260,o = {s:0},U = [39.9,3];
  const lane = (k,y,en,ko) => {
   T(m,g,16,y,en,ko,'g'); $(g,'line',{x1:X(0),y1:y + 32,x2:X(1.5),y2:y + 32,class:'s sm w3'}); RR(g,X(1.3) - 3,y + 14,6,36,2,'x'); T(m,g,X(1.3),y + 68,'limit 1.3','한계 1.3','m','middle');
   $(g,'line',{x1:X(1),y1:y + 24,x2:X(1),y2:y + 40,class:'s sm w3'}); T(m,g,X(1),y + 68,'target','목표','m','middle');
   const dot = CC(g,X(0),y + 32,9,'f'),pk = D(g,464,y,'g','end'),sp = D(g,16,y + 68,k ? 'k' :'x');
   return () => {
    const i = o.s / .06,j = Math.min(Math.floor(i),32),q = Q[k][j] + (Q[k][j + 1] - Q[k][j]) * (i - j),mx = Math.max(...Q[k].slice(0,j + 1),q);
    A(dot,{cx:X(q),class:q > 1.3 ? 'x' :'f'}); pk(m.t('peak ','최대 ') + f2(mx) + ' rad');
    sp(o.s < .6 ? '' :k ? m.t('spike clipped to ' + f1(U[1]) + ' Nm, 1 clip','스파이크를 ' + f1(U[1]) + ' Nm로 clip') :m.t('spike torque ' + f1(U[0]) + ' Nm','스파이크 토크 ' + f1(U[0]) + ' Nm'));
   };
  };
  const a = lane(0,64,'no wrapper','wrapper 없음'),b = lane(1,166,'with wrapper','wrapper 있음'),h = D(g,16,26,'g'),rd = D(g,464,26,'m','end');
  const draw = () => {a(); b(); h(o.s < .6 ? m.t('The policy reaches for 1.0 rad','정책이 1.0 rad로 갑니다') :m.t('A bad output arrives at 0.6 s','0.6초에 나쁜 출력이 들어옵니다')); rd('t = ' + f2(o.s) + ' s');};
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,9.6);
  tl.to(o,{s:1.98,duration:8,ease:'none'},.6);
  m.play(tl,{rest:8.4,draw});
 });
})();
