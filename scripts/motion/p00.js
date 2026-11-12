// phase 00 concept animations (480x270 GSAP timelines); needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,hd,fin} = K,D2R = Math.PI / 180,DA = 'stroke-dasharray',f2 = x => x.toFixed(2);
 const T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 const D = (p,x,y,c,an) => {const e = $(p,'text',{x,y,'font-size':15,class:c || '','text-anchor':an || 'start'}); const f = s => {if (e.textContent !== s) e.textContent = s;}; f.e = e; return f;};
 const stage = (m,en,ko) => {const g = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return g;};

 R.gs('degrees-guard',(el,m) => {
  const g = stage(m,'The sensor says 90 degrees but np.cos reads 90 radians, so cos is -0.45 instead of 0. The guard refuses any reading above 2 pi.','센서는 90도인데 np.cos가 90 rad로 읽어서 cos가 0이 아니라 -0.45가 됩니다. 가드는 2 pi를 넘는 값을 거부합니다.');
  const PX = [120,360],PY = 130,LN = 62,o = {q:0,g:0},hd1 = D(g,240,24,'g','middle'),rd = D(g,240,50,'m','middle'),gd = D(g,360,258,'g','middle');
  const P = PX.map(x => {
   CC(g,x,PY,LN,'n s sm'); $(g,'path',{d:`M${x - LN} ${PY}H${x + LN}`,class:'s sm',[DA]:'3 5'});
   return {dr:$(g,'line',{class:'s sw w3',[DA]:'3 4'}),ar:$(g,'line',{x1:x,y1:PY,class:'s st w4'}),tp:CC(g,x,PY,6,'t'),cs:D(g,x,236,'g','middle')};
  });
  T(m,g,120,214,'read as degrees','도로 읽기','m','middle'); T(m,g,360,214,'np.cos: read as radians','np.cos: rad로 읽기','m','middle');
  const draw = () => {
   const q = o.q,trip = o.g && q > 2 * Math.PI,a = [q * D2R,o.g ? Math.min(q,2 * Math.PI) :q];
   a.forEach((v,i) => {const tx = PX[i] + LN * Math.cos(v),ty = PY - LN * Math.sin(v);
    A(P[i].ar,{x2:tx,y2:ty}); A(P[i].tp,{cx:tx,cy:ty}); A(P[i].dr,{x1:tx,y1:ty,x2:tx,y2:PY});});
   hd1(o.g ? m.t('Guard on: a reading above 2π is refused','가드 켬: 2π 넘는 값은 거부') :m.t('No guard: np.cos reads the 90 as radians','가드 없음: 90을 rad로 읽음'));
   rd(m.t('sensor reading q = ','센서 값 q = ') + Math.round(q));
   P[0].cs('cos = ' + f2(Math.cos(a[0]))); P[1].cs(trip ? m.t('refused','거부됨') :'cos = ' + f2(Math.cos(a[1])));
   gd(o.g ? (trip ? `ValueError: ${Math.round(q)} > 2π` :m.t('guard: ok','가드: 통과')) :''); A(gd.e,{class:trip ? 'x' :'g'});
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,11.8);
  tl.fromTo(o,{q:0},{q:90,duration:4.4,ease:'none'},.6).set(o,{g:1},6.4).fromTo(o,{q:0},{q:90,duration:4.4,ease:'none'},6.4);
  m.play(tl,{rest:5.4,draw});
 });

 R.gs('euler-energy',(el,m) => {
  const g = stage(m,'One pendulum (L = 1 m), theta0 = 0.3 rad, step dt = 0.02 s, large so the drift shows. Moving the angle with the old omega adds energy every swing; the new omega does not.','진자 하나(L = 1 m), theta0 = 0.3 rad, 스텝 dt = 0.02초로 드리프트가 보이게 크게 잡았습니다. 옛 omega로 각도를 옮기면 매 스윙마다 에너지가 늘고 새 omega는 늘지 않습니다.');
  const N = 600,DT = .02,TH0 = .3,G = 9.81,E0 = G * (1 - Math.cos(TH0)),RL = 58,SX = [120,360],o = {i:0};
  const run = semi => {const th = [TH0]; let t = TH0,w = 0; for (let i = 0; i < N; i++) {const wn = w - DT * G * Math.sin(t); t += DT * (semi ? wn :w); w = wn; th.push(t);} return th;};
  const TH = [run(1),run(0)],E = TH.map(th => th.map((t,i) => {const a = Math.max(0,i - 1),b = Math.min(N,i + 1),w = (th[b] - th[a]) / (DT * (b - a)); return (.5 * w * w + G * (1 - Math.cos(t))) / E0;}));
  T(m,g,240,22,'Swap two lines and the energy drifts','두 줄 순서만 바꿨는데 에너지가 늘어납니다','g','middle');
  T(m,g,120,128,'semi-implicit: new ω','반암시적: 새 ω','m','middle'); T(m,g,360,128,'explicit Euler: old ω','명시적 Euler: 옛 ω','m','middle');
  $(g,'line',{x1:30,y1:252,x2:450,y2:252,class:'s sm',[DA]:'3 5'}); T(m,g,466,246,'E0','E0','m','end');
  const ps = SX.map((x,i) => {CC(g,x,40,4,'g'); return {rod:$(g,'line',{x1:x,y1:40,class:'s st w3'}),bob:CC(g,x,40,9,i ? 'w' :'k'),rd:D(g,x,148,'g','middle'),
   tr:$(g,'path',{d:E[i].map((r,j) => `${j ? 'L' :'M'}${(30 + j * 420 / N).toFixed(1)} ${(262 - Math.min(r,10.3) * 10).toFixed(1)}`).join(''),class:'s n w3 ' + (i ? 'sw' :'sk'),pathLength:1})};});
  const draw = () => {
   const i = Math.min(N,Math.round(o.i));
   ps.forEach((p,k) => {const th = TH[k][i],bx = SX[k] + RL * Math.sin(th),by = 40 + RL * Math.cos(th);
    A(p.rod,{x2:bx,y2:by}); A(p.bob,{cx:bx,cy:by}); A(p.tr,{[DA]:`${i / N} 2`}); p.rd(`E = ${f2(E[k][i])} E0`);});
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,13.4);
  tl.fromTo(o,{i:0},{i:N,duration:12,ease:'none'},.6);
  m.play(tl,{rest:12.4,draw});
 });

 R.gs('origin-frames',(el,m) => {
  const g = stage(m,'Each origin is read in its parent frame. After the shoulder yaw of 90 degrees the offsets point along y: the hand is at (0, 0.5), 0.71 m from the plain sum (0.5, 0).','각 origin은 부모 frame에서 읽습니다. shoulder yaw가 90도가 되면 offset이 y 방향을 향해 hand는 (0, 0.5)에 있고 단순 합 (0.5, 0)과 0.71 m 떨어집니다.');
  const BX = 90,BY = 222,SC = 250,o = {p:0},X = x => BX + SC * x,Y = y => BY - SC * y,pn = (x,y) => `${X(x)},${Y(y)} `;
  $(g,'path',{d:`M${BX} ${BY}H${BX + 150}M${BX} ${BY}V${BY - 150}`,class:'s n sm',[DA]:'2 5'}); T(m,g,BX + 154,BY + 5,'x','x','m'); T(m,g,BX,BY - 158,'y','y','m','middle');
  const nv = $(g,'g',{}); $(nv,'polyline',{points:pn(0,0) + pn(.3,0) + pn(.5,0),class:'s n sw w3',[DA]:'5 5'}); CC(nv,X(.5),Y(0),8,'n s sw');
  $(nv,'path',{d:'M250 80h26',class:'s n sw w3',[DA]:'5 5'}); const nl = D(nv,284,85,'g');
  const fr = $(g,'path',{d:hd(BX,BY,62,0) + hd(BX,BY,0,-62),class:'s n sd w3'}),fx = T(m,g,0,0,"x'","x'",'m'),fy = T(m,g,0,0,"y'","y'",'m'),arm = $(g,'polyline',{class:'s n sk w6'}),hn = CC(g,0,0,7,'k');
  $(g,'path',{d:'M250 56h26',class:'s n sk w6'}); const rl = D(g,284,61,'g'),ya = D(g,250,30,'m'),gp = $(g,'g',{}),gl = $(gp,'line',{class:'s sm',[DA]:'3 4'}),gt = D(gp,250,112,'g');
  const draw = () => {
   const s = o.p * D2R,c = Math.cos(s),n = Math.sin(s),ex = .3 * c,ey = .3 * n,hx = ex + .2 * c,hy = ey + .2 * n;
   A(arm,{points:pn(0,0) + pn(ex,ey) + pn(hx,hy)}); A(hn,{cx:X(hx),cy:Y(hy)});
   A(fr,{transform:`rotate(${-o.p} ${BX} ${BY})`}); A(fx,{x:BX + 70 * c,y:BY - 70 * n + 5}); A(fy,{x:BX - 70 * n - 5,y:BY - 70 * c}); A(gl,{x1:X(hx),y1:Y(hy),x2:X(.5),y2:Y(0)});
   ya('origin yaw ' + Math.round(o.p) + '°'); rl(`hand (${f2(hx)}, ${f2(hy)})`); nl(m.t('plain sum ','단순 합 ') + '(0.50, 0.00)'); gt(m.t('gap ','차이 ') + f2(Math.hypot(hx - .5,hy)) + ' m');
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.6);
  tl.fromTo(nv,{autoAlpha:0},{autoAlpha:1,duration:.5},.8).fromTo(o,{p:0},{p:90,duration:3.6,ease:'power2.inOut'},2.2).fromTo(gp,{autoAlpha:0},{autoAlpha:1,duration:.5},5.9);
  m.play(tl,{rest:8.5,draw});
 });

 R.gs('queue-depth',(el,m) => {
  const g = stage(m,'Publisher 100 Hz, subscriber 40 Hz, shown 5x slower. Each queue keeps the last depth messages and a full queue drops the oldest. What the subscriber reads is 5, 95 and 495 ms old.','publisher 100 Hz, subscriber 40 Hz를 5배 느리게 보여 줍니다. 각 queue는 마지막 depth개만 보관하고 가득 차면 가장 오래된 것을 버립니다. subscriber가 읽는 메시지는 5, 95, 495 ms 지난 것입니다.');
  const DS = [1,10,50],CW = 6.4,NS = 1475,o = {s:0};
  const sim = d => {const q = [],r = {len:[],dr:[],age:[]}; let dr = 0,age = 0; for (let t = 0; t <= NS; t++) {if (t % 10 === 0) {if (q.length === d) {q.shift(); dr++;} q.push(t);} if (t % 25 === 0 && q.length) age = t - q.shift(); r.len.push(q.length); r.dr.push(dr); r.age.push(age);} return r;};
  const S = DS.map(sim);
  T(m,g,16,22,'Publisher 100 Hz, subscriber 40 Hz','publisher 100 Hz, subscriber 40 Hz','g'); T(m,g,464,22,'5x slow motion','5배 느리게','m','end');
  T(m,g,16,258,'A full queue drops its oldest message','가득 찬 queue는 가장 오래된 메시지를 버립니다','m');
  const rows = DS.map((d,r) => {const y = 52 + r * 72;
   const cells = Array.from({length:d},(_,i) => RR(g,16 + i * CW,y + 8,CW - 1,14,1,'c')); RR(g,15,y + 7,d * CW + 1,16,2,'n s sm');
   return {cells,n:-1,tx:D(g,16,y,'g'),bar:RR(g,16,y + 30,1,8,3,'t')};});
  const draw = () => {
   const s = Math.min(NS,Math.round(o.s));
   rows.forEach((r,k) => {const n = S[k].len[s],age = S[k].age[s];
    if (n !== r.n) {r.n = n; r.cells.forEach((c,i) => A(c,{class:i < n ? (i ? 'f' :'t') :'c'}));}
    A(r.bar,{width:Math.max(1,age * .64)});
    r.tx(`depth ${DS[k]} · ${m.t("dropped","버림")} ${S[k].dr[s]} · ${m.t("age","나이")} ${age} ms`);});
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,9.4);
  tl.fromTo(o,{s:0},{s:NS,duration:7.4,ease:'none'},.6);
  m.play(tl,{rest:8.4,draw});
 });
})();
