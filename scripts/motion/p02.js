// phase 02 concept animations (480x270 GSAP timelines); needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,fin} = K,D2R = Math.PI / 180,DA = 'stroke-dasharray',f2 = x => x.toFixed(2);
 const T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 const D = (p,x,y,c,an) => {const e = $(p,'text',{x,y,'font-size':15,class:c || '','text-anchor':an || 'start'}); const f = s => {if (e.textContent !== s) e.textContent = s;}; f.e = e; return f;};
 const stage = (m,en,ko) => {const g = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return g;};

 R.gs('dh-wrong-convention',(el,m) => {
  const g = stage(m,'One DH table, two routines. At the zero pose the tips agree, so a quick check passes. As q grows the wrong convention drifts away.','같은 DH 표를 루틴 두 개에 넣었습니다. 영점 자세에서는 tip이 같아서 확인을 통과하지만 q가 커지면 틀린 convention이 멀어집니다.');
  const BX = 90,BY = 240,SC = 260,L1 = .4,L2 = .3,Q = [.5,.8],o = {s:0},X = x => BX + SC * x,Y = y => BY - SC * y;
  const tips = s => {const a = Q[0] * s,b = a + Q[1] * s,e = [L1 * Math.cos(a),L1 * Math.sin(a)]; return {e,c:[e[0] + L2 * Math.cos(b),e[1] + L2 * Math.sin(b)],w:[(L1 + L2) * Math.cos(b),(L1 + L2) * Math.sin(b)]};};
  const err = s => {const k = tips(s); return Math.hypot(k.c[0] - k.w[0],k.c[1] - k.w[1]);};
  $(g,'path',{d:`M290 118V230H460`,class:'s n sm'});
  const pts = Array.from({length:61},(_,i) => `${i ? 'L' :'M'}${290 + 170 * i / 60} ${230 - 340 * err(i / 60)}`).join('');
  const tr = $(g,'path',{d:pts,class:'s n sw w3',pathLength:1}),dot = CC(g,290,230,5,'x');
  [['k','Craig routine','Craig 루틴'],['x','other routine, same table','다른 루틴, 같은 표']].forEach((r,i) => {CC(g,258,50 + i * 22,6,r[0]); T(m,g,270,55 + i * 22,r[1],r[2],'g');});
  const wa = $(g,'polyline',{class:'s n sw w4',[DA]:'6 5'}),ca = $(g,'polyline',{class:'s n sk w6'}),gap = $(g,'line',{class:'s sm',[DA]:'3 4'}),ct = CC(g,0,0,7,'k'),wt = CC(g,0,0,7,'x');
  const hq = D(g,16,24,'g'),re = D(g,296,134,'g');
  const draw = () => {
   const s = o.s,k = tips(s),pt = a => `${X(a[0])},${Y(a[1])}`;
   A(ca,{points:`${BX},${BY} ${pt(k.e)} ${pt(k.c)}`}); A(wa,{points:`${BX},${BY} ${pt(k.w)}`});
   A(ct,{cx:X(k.c[0]),cy:Y(k.c[1])}); A(wt,{cx:X(k.w[0]),cy:Y(k.w[1])}); A(gap,{x1:X(k.c[0]),y1:Y(k.c[1]),x2:X(k.w[0]),y2:Y(k.w[1])});
   A(tr,{[DA]:`${s} 2`}); A(dot,{cx:290 + 170 * s,cy:230 - 340 * err(s)});
   hq(`q = (${f2(Q[0] * s)}, ${f2(Q[1] * s)}) rad`);
   re(m.t('error ','오차 ') + f2(err(s)) + ' m');
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.2);
  tl.fromTo(o,{s:0},{s:1,duration:5,ease:'power1.inOut'},1.8);
  m.play(tl,{rest:8.5,draw});
 });

 R.gs('ik-reach-limit',(el,m) => {
  const g = stage(m,'L1 = 0.5 m, L2 = 0.4 m. cos q2 = (r^2 - L1^2 - L2^2) / (2 L1 L2). The two elbows merge at r = 0.9 m, where cos q2 = 1. Past that the solver refuses instead of returning nan.','L1 = 0.5 m, L2 = 0.4 m. cos q2 = (r^2 - L1^2 - L2^2) / (2 L1 L2)입니다. 두 elbow는 r = 0.9 m에서 하나로 합쳐지고 그때 cos q2 = 1입니다. 그 너머에서는 nan을 돌려주는 대신 거부합니다.');
  const BX = 30,BY = 150,SC = 280,L1 = .5,L2 = .4,o = {r:.3},X = x => BX + SC * x,Y = y => BY - SC * y;
  $(g,'line',{x1:BX,y1:BY,x2:X(.95),y2:BY,class:'s sm',[DA]:'3 5'}); $(g,'path',{d:`M${X(.9)} ${BY - 8}v16`,class:'s sw w3'}); T(m,g,X(.9),BY + 30,'L1 + L2','L1 + L2','m','middle');
  T(m,g,330,190,'band 0.10 to 0.90 m','가능 범위 0.10 ~ 0.90 m','m');
  const mk = [1,-1].map(sg => ({ln:$(g,'polyline',{class:'s n w4 ' + (sg > 0 ? 'st' :'sd'),[DA]:sg > 0 ? '' :'6 5'}),jn:CC(g,0,0,6,sg > 0 ? 't' :'d')})),tg = CC(g,0,0,8,'w');
  CC(g,BX,BY,5,'g');
  const l = [60,84,108,132].map(y => D(g,330,y,'g'));
  const draw = () => {
   const r = o.r,c2 = (r * r - L1 * L1 - L2 * L2) / (2 * L1 * L2),ok = c2 <= 1 + 1e-9,cc = Math.min(1,c2),s2 = Math.sqrt(1 - cc * cc),q2 = Math.atan2(s2,cc);
   let err = 0;
   [1,-1].forEach((sg,i) => {const b = -Math.atan2(L2 * sg * s2,L1 + L2 * cc),ex = L1 * Math.cos(b),ey = L1 * Math.sin(b),tx = ex + L2 * Math.cos(b + sg * q2),ty = ey + L2 * Math.sin(b + sg * q2);
    A(mk[i].ln,{points:`${X(0)},${Y(0)} ${X(ex)},${Y(ey)} ${X(tx)},${Y(ty)}`}); A(mk[i].jn,{cx:X(ex),cy:Y(ey)}); err = Math.hypot(tx - r,ty);});
   A(tg,{cx:X(r),cy:Y(0),class:ok ? 'w' :'x'});
   l[0](`|p| = ${f2(r)} m`); l[1](`cos q2 = ${f2(c2)}`);
   l[2](ok ? `q2 = ±${Math.round(q2 / D2R)}°` :m.t('acos: no answer','acos: 해 없음')); l[3](ok ? m.t('FK error ','FK 오차 ') + err.toFixed(3) + ' m' :m.t('refused, not nan','nan 대신 거부')); A(l[3].e,{class:ok ? 'g' :'x'});
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.6);
  tl.fromTo(o,{r:.3},{r:.9,duration:5.6,ease:'none'},1).fromTo(o,{r:.9},{r:.95,duration:1.4,ease:'none'},7);
  m.play(tl,{rest:4.6,draw});
 });

 R.gs('jacobian-ellipse',(el,m) => {
  const g = stage(m,'L1 = 0.5 m, L2 = 0.4 m, q1 = 0.3 rad. Through J, unit joint speeds become this tip-speed ellipse: fat when bent, thin when nearly straight.','단위 joint 속도가 J를 지나면 이 tip 속도 타원이 됩니다. 굽히면 뚱뚱하고 거의 펴면 얇습니다.');
  const L1 = .5,L2 = .4,Q1 = .3,BX = 40,BY = 226,S = 190,CX = 360,CY = 132,KS = 90,Q0 = 1.8,o = {q:Q0,p:0};
  const J = q2 => {const b = Q1 + q2; return [-L1 * Math.sin(Q1) - L2 * Math.sin(b),-L2 * Math.sin(b),L1 * Math.cos(Q1) + L2 * Math.cos(b),L2 * Math.cos(b)];};
  const V = (j,a) => [j[0] * Math.cos(a) + j[1] * Math.sin(a),j[2] * Math.cos(a) + j[3] * Math.sin(a)];
  const ell = q2 => Array.from({length:49},(_,i) => {const [x,y] = V(J(q2),i * Math.PI / 24); return `${i ? 'L' :'M'}${(CX + KS * x).toFixed(1)} ${(CY - KS * y).toFixed(1)}`;}).join('');
  $(g,'path',{d:ell(Q0),class:'s n sm',[DA]:'4 5'});
  const live = $(g,'path',{class:'s n sf w4'}),vec = $(g,'line',{x1:CX,y1:CY,class:'s st w4'}),arm = $(g,'polyline',{class:'s n sl w6'}),tp = CC(g,0,0,7,'t');
  CC(g,BX,BY,5,'g');
  const hq = D(g,16,24,'g'),sg = D(g,464,24,'m','end'),l1 = D(g,236,244,'g'),l2 = D(g,236,262,'m');
  const draw = () => {
   const q2 = o.q,j = J(q2),[vx,vy] = V(j,o.p);
   const t2 = j.reduce((a,b) => a + b * b,0),d = L1 * L2 * Math.sin(q2),r = Math.sqrt(t2 * t2 - 4 * d * d),sM = Math.sqrt((t2 + r) / 2),sm = Math.sqrt((t2 - r) / 2);
   const ex = BX + S * L1 * Math.cos(Q1),ey = BY - S * L1 * Math.sin(Q1),tx = ex + S * L2 * Math.cos(Q1 + q2),ty = ey - S * L2 * Math.sin(Q1 + q2);
   A(arm,{points:`${BX},${BY} ${ex},${ey} ${tx},${ty}`}); A(tp,{cx:tx,cy:ty});
   A(live,{d:ell(q2)}); A(vec,{x2:CX + KS * vx,y2:CY - KS * vy});
   hq(`q2 = ${Math.round(q2 / D2R)}°`); sg(m.t('fast ','빠름 ') + f2(sM) + m.t('  slow ','  느림 ') + f2(sm) + ' m/s');
   l1(`qd = (${f2(Math.cos(o.p))}, ${f2(Math.sin(o.p))}) rad/s`); l2(`v = (${f2(vx)}, ${f2(vy)}) m/s`);
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.6);
  tl.fromTo(o,{q:Q0},{q:.12,duration:8,ease:'sine.inOut'},1).fromTo(o,{p:0},{p:7.2 * Math.PI,duration:9.4,ease:'none'},.6);
  m.play(tl,{rest:9.6,draw});
 });
 R.gs('ik-iterate',(el,m) => {
  const g = stage(m,'Damped Newton steps (lam 0.05, step cap 0.3 rad) on a 3-link arm, L = 0.4, 0.3, 0.2 m. A reachable target falls below 1e-6 m in a few steps. An unreachable one stays flat at its best effort and reports False.','3링크 팔(L = 0.4, 0.3, 0.2 m)에 damped Newton 스텝(lam 0.05, 스텝 상한 0.3 rad)을 적용합니다. 닿는 표적은 몇 스텝 만에 1e-6 m 아래로 내려가고 닿지 않는 표적은 최선의 오차에서 평평하게 남아 False를 돌려줍니다.');
  const L = [.4,.3,.2],LO = [-Math.PI,-2.5,-2.5],HI = [Math.PI,2.5,2.5],BX = 40,BY = 170,SC = 120,PX = 290,PW = 170,PY = 70,PH = 120;
  const fk = q => {let a = 0,x = 0,y = 0; q.forEach((v,i) => {a += v; x += L[i] * Math.cos(a); y += L[i] * Math.sin(a);}); return [x,y];};
  // the lesson's solve_ik, keeping every iterate
  const run = (t,q0) => {const q = q0.slice(),h = [q.slice()];
   for (let n = 0; n < 300; n++) {const p = fk(q),e = [t[0] - p[0],t[1] - p[1]]; if (Math.hypot(e[0],e[1]) < 1e-6) break;
    const a1 = q[0],a2 = a1 + q[1],a3 = a2 + q[2],x3 = -L[2] * Math.sin(a3),x2 = x3 - L[1] * Math.sin(a2),x1 = x2 - L[0] * Math.sin(a1),y3 = L[2] * Math.cos(a3),y2 = y3 + L[1] * Math.cos(a2),y1 = y2 + L[0] * Math.cos(a1);
    const A_ = x1 * x1 + x2 * x2 + x3 * x3 + .0025,B = x1 * y1 + x2 * y2 + x3 * y3,C = y1 * y1 + y2 * y2 + y3 * y3 + .0025,dt = A_ * C - B * B,z0 = (C * e[0] - B * e[1]) / dt,z1 = (-B * e[0] + A_ * e[1]) / dt;
    const d = [x1 * z0 + y1 * z1,x2 * z0 + y2 * z1,x3 * z0 + y3 * z1],s = Math.min(1,.3 / Math.max(...d.map(Math.abs)));
    d.forEach((v,i) => {q[i] = Math.min(HI[i],Math.max(LO[i],q[i] + v * s));}); h.push(q.slice());}
   return h;};
  const Q0 = [.3,.3,.3],ST = [{t:[.5,.3],h:run([.5,.3],Q0)},{t:[1.5,0],h:run([1.5,0],Q0)}];
  const px = p => [BX + SC * p[0],BY - SC * p[1]],err = (k,q) => {const p = fk(q); return Math.hypot(ST[k].t[0] - p[0],ST[k].t[1] - p[1]);};
  const yy = e => PY + PH * Math.min(1,Math.max(0,-Math.log10(Math.max(e,1e-7)) / 7));
  $(g,'path',{d:`M${PX} ${PY - 6}V${PY + PH}H${PX + PW}`,class:'s n sm'}); T(m,g,PX - 6,PY + 5,'1 m','1 m','m','end'); T(m,g,PX - 6,PY + PH + 5,'1e-7','1e-7','m','end');
  $(g,'path',{d:`M${PX} ${yy(1e-6)}H${PX + PW}`,class:'s sk',[DA]:'4 4'}); T(m,g,PX + PW,yy(1e-6) - 5,'tol 1e-6','tol 1e-6','m','end'); T(m,g,PX + PW,PY + PH + 18,'step','스텝','m','end');
  CC(g,BX,BY,5,'g'); const rc = $(g,'path',{d:`M${BX + SC * .9} ${BY}A${SC * .9} ${SC * .9} 0 0 0 ${BX} ${BY - SC * .9}`,class:'s n sm',[DA]:'3 5'});
  const gh = $(g,'polyline',{class:'s n sm',[DA]:'4 4'}),arm = $(g,'polyline',{class:'s n sl w6'}),tg = CC(g,0,0,8,'n s sw'),tp = CC(g,0,0,6,'t'),tr = $(g,'path',{class:'s n sf w3'}),dot = CC(g,PX,PY,5,'f');
  const h1 = D(g,16,24,'g'),h2 = D(g,PX,48,'m'),vd = D(g,16,246,'g'),nt = D(g,16,264,'m'),o = {k:0,s:0};
  const draw = () => {
   const h = ST[o.k].h,i = Math.min(h.length - 1,Math.floor(o.s)),f = i < h.length - 1 ? o.s - i :0,q = h[i].map((v,j) => v + (h[Math.min(h.length - 1,i + 1)][j] - v) * Math.min(1,f)),n = h.length - 1;
   const pts = a => {let a_ = 0,p = [0,0],o_ = [px(p)]; a.forEach((v,j) => {a_ += v; p = [p[0] + L[j] * Math.cos(a_),p[1] + L[j] * Math.sin(a_)]; o_.push(px(p));}); return o_.map(u => u.join(',')).join(' ');};
   A(arm,{points:pts(q)}); A(gh,{points:pts(h[0])}); const [tx,ty] = px(ST[o.k].t),[ex,ey] = px(fk(q)); A(tg,{cx:tx,cy:ty}); A(tp,{cx:ex,cy:ey});
   const X = j => PX + PW * j / Math.max(n,o.k ? 300 :8); let d = ''; for (let j = 0; j <= i; j++) d += `${j ? 'L' :'M'}${X(j)} ${yy(err(o.k,h[j]))}`; d += `L${X(i + Math.min(1,f))} ${yy(err(o.k,q))}`;
   A(tr,{d}); A(dot,{cx:X(i + Math.min(1,f)),cy:yy(err(o.k,q))});
   const e = err(o.k,q),done = o.s >= n - 1;
   h1(o.k ? m.t('target out of reach (1.5, 0)','닿지 않는 표적 (1.5, 0)') :m.t('target (0.5, 0.3)','표적 (0.5, 0.3)')); h2(m.t('error vs step','오차 대 스텝'));
   vd(`${m.t('step','스텝')} ${i}   ${m.t('error','오차')} ${e < 1e-3 ? e.toExponential(1) :e.toFixed(3)} m`);
   nt(done ? (o.k ? m.t('converged: False, best effort kept','converged: False, 최선의 자세 유지') :m.t('converged: True','converged: True')) :m.t('iterating','반복 중')); A(nt.e,{class:done ? (o.k ? 'x' :'k') :'m'});
  };
  const tl = m.timeline({repeatDelay:.3}),n0 = ST[0].h.length - 1,n1 = ST[1].h.length - 1;
  fin(tl,g,11.8);
  tl.set(o,{k:0,s:0},0).fromTo(o,{s:0},{s:n0,duration:4.2,ease:'none'},.8).set(o,{k:1,s:0},6.2).fromTo(o,{s:0},{s:n1,duration:4.6,ease:'power2.out'},6.4);
  m.play(tl,{rest:5.6,draw});
 });
})();
