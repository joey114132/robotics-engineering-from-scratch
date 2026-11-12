// phase 01 concept animations (480x270 GSAP timelines); needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,hd,fin} = K,D2R = Math.PI / 180,DA = 'stroke-dasharray',f2 = x => x.toFixed(2);
 const T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 const D = (p,x,y,c,an) => {const e = $(p,'text',{x,y,'font-size':15,class:c || '','text-anchor':an || 'start'}); const f = s => {if (e.textContent !== s) e.textContent = s;}; f.e = e; return f;};
 const stage = (m,en,ko) => {const g = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return g;};

 R.gs('slerp-sign',(el,m) => {
  const g = stage(m,'q1 = -q(0.1 rad) names the same orientation as q(0.1 rad). Without the sign check slerp sweeps 354.3 degrees, with it 5.7 degrees.','q1 = -q(0.1 rad)는 q(0.1 rad)와 같은 자세입니다. 부호 확인이 없으면 slerp는 354.3도, 있으면 5.7도를 돕니다.');
  const N = 300,H = .05,CX = [120,360],CY = 118,RD = 58,o = {u:0};
  // slerp from q0 = (1,0,0,0) to q1 = -(cos H, 0, 0, sin H); the wrist angle is 2 atan2(z, w)
  const seq = fix => {let c = -Math.cos(H),s = -Math.sin(H),d = c; if (fix && d < 0) {c = -c; s = -s; d = -d;}
   const om = Math.acos(Math.min(d,1)); return Array.from({length:N + 1},(_,i) => {const t = i / N,k0 = Math.sin((1 - t) * om) / Math.sin(om),k1 = Math.sin(t * om) / Math.sin(om); return 2 * Math.atan2(k1 * s,k0 + k1 * c);});};
  const AN = [seq(0),seq(1)];
  T(m,g,120,24,'no sign check','부호 확인 없음','g','middle'); T(m,g,360,24,'dot < 0, so negate q1','dot < 0이라 q1 부호 반전','g','middle');
  const dd = `dot(q0, q1) = ${(-Math.cos(H)).toFixed(3)}`; T(m,g,240,256,dd,dd,'m','middle');
  const P = CX.map((cx,k) => {CC(g,cx,CY,RD,'n s sm');
   $(g,'line',{x1:cx + (RD - 7) * Math.cos(.1),y1:CY - (RD - 7) * Math.sin(.1),x2:cx + (RD + 7) * Math.cos(.1),y2:CY - (RD + 7) * Math.sin(.1),class:'s sk w3'});
   return {arc:$(g,'path',{class:'s n w6 ' + (k ? 'sk' :'sw'),opacity:.55}),h:$(g,'line',{x1:cx,y1:CY,class:'s st w4'}),t:CC(g,cx,CY,6,'t'),rd:D(g,cx,212,k ? 'k' :'x','middle')};});
  const draw = () => {
   const i = Math.round(o.u * N);
   CX.forEach((cx,k) => {const a = AN[k][i],ex = cx + RD * Math.cos(a),ey = CY - RD * Math.sin(a);
    A(P[k].h,{x2:ex,y2:ey}); A(P[k].t,{cx:ex,cy:ey});
    A(P[k].arc,{d:Math.abs(a) < .002 ? '' :`M${cx + RD} ${CY}A${RD} ${RD} 0 ${Math.abs(a) > Math.PI ? 1 :0} ${a < 0 ? 1 :0} ${ex.toFixed(2)} ${ey.toFixed(2)}`});
    P[k].rd(m.t('swept ','회전 ') + (Math.abs(a) / D2R).toFixed(1) + '°');});
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.2);
  tl.fromTo(o,{u:0},{u:1,duration:6,ease:'none'},1.4);
  m.play(tl,{rest:8.5,draw});
 });

 R.gs('tf-compose',(el,m) => {
  const g = stage(m,'Camera at (0.5, 0, 0.4) in the base frame, cup at (0.2, 0, 0.5) in the camera frame. T_base_cam @ T_cam_cup follows the camera. Swapped factors are off by up to 0.4 m, a stray inverse by up to 1.3 m.','카메라는 base frame의 (0.5, 0, 0.4)에, 컵은 카메라 frame의 (0.2, 0, 0.5)에 있습니다. T_base_cam @ T_cam_cup은 카메라를 따라갑니다. 곱 순서를 바꾸면 최대 0.4 m, 엉뚱한 inverse는 최대 1.3 m 틀립니다.');
  const OX = 70,OY = 238,S = 200,o = {a:0},p = [.2,0,.5],t = [.5,0,.4],P3 = v => [OX + S * (v[0] + .4 * v[1]),OY - S * (v[2] + .4 * v[1])];
  $(g,'path',{d:hd(OX,OY,45,0) + hd(OX,OY,0,-45),class:'s n sm'}); CC(g,OX,OY,4,'g'); T(m,g,OX + 10,OY + 22,'base','base','m');
  const cam = CC(g,...P3(t),6,'g'),hdg = $(g,'path',{class:'s n sd w3'}),ln = $(g,'line',{class:'s sm',[DA]:'3 4'});
  const rows = [['k','T_base_cam @ T_cam_cup',m => m.t('follows the camera','카메라를 따라감')],['w','T_cam_cup @ T_base_cam'],['x','T_cam_base @ T_cam_cup']].map((r,i) => {const y = 84 + i * 62;
   CC(g,244,y - 5,7,r[0]); T(m,g,258,y,r[1],r[1],'g'); return {mk:CC(g,0,0,7,r[0]),tx:D(g,258,y + 22,'m'),f:r[2]};});
  const hy = D(g,16,24,'g');
  const draw = () => {
   const a = o.a * D2R,c = Math.cos(a),s = Math.sin(a),q = [p[0] - t[0],p[1] - t[1],p[2] - t[2]];
   const V = [[t[0] + c * p[0],t[1] + s * p[0],t[2] + p[2]],[t[0] + p[0],t[1] + p[1],t[2] + p[2]],[c * q[0] + s * q[1],-s * q[0] + c * q[1],q[2]]];
   V.forEach((v,i) => {const [x,y] = P3(v); A(rows[i].mk,{cx:x,cy:y}); rows[i].tx(i ? m.t('error ','오차 ') + f2(Math.hypot(v[0] - V[0][0],v[1] - V[0][1],v[2] - V[0][2])) + ' m' :rows[0].f(m));});
   const [cx,cy] = P3(t),[hx,hy2] = P3([t[0] + .22 * c,t[1] + .22 * s,t[2]]),[rx,ry] = P3(V[0]);
   A(hdg,{d:hd(cx,cy,hx - cx,hy2 - cy)}); A(ln,{x1:cx,y1:cy,x2:rx,y2:ry}); hy(m.t('camera yaw ','카메라 yaw ') + Math.round(o.a) + '°');
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.4);
  tl.fromTo(o,{a:0},{a:180,duration:5,ease:'sine.inOut'},2.4);
  m.play(tl,{rest:8.6,draw});
 });
 R.gs('euler-jump',(el,m) => {
  const g = stage(m,'The tool pitches smoothly from 60 to 120 degrees with roll = yaw = 0 (R = Ry(pitch)). The reader reports pitch up to 90 and back down, while roll and yaw jump by 180 degrees at 90.','도구가 roll = yaw = 0인 채로(R = Ry(pitch)) pitch를 60도에서 120도까지 부드럽게 돌립니다. 읽는 값은 pitch가 90도까지 올랐다가 내려가고 roll과 yaw는 90도에서 180도 점프합니다.');
  const CX = 100,CY = 150,RD = 62,PX = 232,PW = 224,PY0 = 90,PH = 120,o = {p:60};
  // R_to_euler of the lesson for R = Ry(p): pitch = asin(-R20), roll = atan2(R21,R22), yaw = atan2(R10,R00); locked: roll = 0, yaw = atan2(-R01,R11)
  const read = p => {const a = p * D2R,R20 = -Math.sin(a),lock = Math.abs(R20) > 1 - 1e-9;
   return {pitch:Math.asin(Math.max(-1,Math.min(1,-R20))) / D2R,roll:lock ? 0 :Math.atan2(0,Math.cos(a)) / D2R,yaw:lock ? 0 :Math.atan2(0,Math.cos(a)) / D2R,lock};};
  const X = p => PX + PW * (p - 60) / 60,Y = a => PY0 + PH * (1 - a / 180);
  $(g,'path',{d:`M${PX} ${PY0 - 8}V${PY0 + PH}H${PX + PW}`,class:'s n sm'}); T(m,g,PX - 6,Y(180) + 5,'180°','180°','m','end'); T(m,g,PX - 6,Y(0) + 5,'0°','0°','m','end');
  T(m,g,X(90),PY0 + PH + 18,'90°','90°','m','middle'); $(g,'path',{d:`M${X(90)} ${PY0}V${PY0 + PH}`,class:'s sm',[DA]:'3 5'});
  const ln = (c,w,dash) => $(g,'path',{class:`s n ${c} ${w}`,[DA]:dash || ''});
  const tp = ln('sf','w3'),tr = ln('sw','w6'),ty = ln('st','w3','2 5');
  T(m,g,PX,28,'pitch read','읽은 pitch','f'); T(m,g,PX + 84,28,'roll read','읽은 roll','w'); T(m,g,PX + 150,28,'yaw read','읽은 yaw','m');
  CC(g,CX,CY,RD,'n s sm'); $(g,'path',{d:`M${CX} ${CY - RD - 8}V${CY + 6}`,class:'s sm',[DA]:'3 5'});
  const ar = $(g,'line',{x1:CX,y1:CY,class:'s st w6'}),tip = CC(g,CX,CY,7,'t'),cur = $(g,'line',{class:'s sm'});
  const hp = D(g,16,24,'g'),r1 = D(g,16,246,'g'),r2 = D(g,16,264,'m');
  const pts = (k,upto) => {let d = '';for (let p = 60; p <= upto + 1e-9; p += .5) {const v = read(p)[k]; if (p > 60 && Math.abs(v - read(p - .5)[k]) > 90) d += `M${X(p)} ${Y(v)}`; else d += `${p === 60 ? 'M' :'L'}${X(p)} ${Y(v)}`;} return d;};
  const draw = () => {
   const p = o.p,a = p * D2R,r = read(p),tx = CX + RD * Math.cos(a),ty_ = CY - RD * Math.sin(a);
   A(ar,{x2:tx,y2:ty_}); A(tip,{cx:tx,cy:ty_}); A(tp,{d:pts('pitch',p)}); A(tr,{d:pts('roll',p)}); A(ty,{d:pts('yaw',p)}); A(cur,{x1:X(p),y1:PY0,x2:X(p),y2:PY0 + PH});
   hp(m.t('actual pitch ','실제 pitch ') + p.toFixed(0) + '°');
   r1(`roll ${Math.round(r.roll)}°  pitch ${Math.round(r.pitch)}°  yaw ${Math.round(r.yaw)}°`);
   r2(r.lock ? m.t('locked: roll set to 0','잠김: roll을 0으로 둠') :m.t('Euler rate multiplier 1/cos = ','Euler rate 배율 1/cos = ') + (1 / Math.abs(Math.cos(a))).toFixed(1));
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,11.6);
  tl.fromTo(o,{p:60},{p:90,duration:4,ease:'none'},.8).to(o,{p:90,duration:1},4.8).to(o,{p:120,duration:4,ease:'none'},5.8);
  m.play(tl,{rest:9.8,draw});
 });
})();
