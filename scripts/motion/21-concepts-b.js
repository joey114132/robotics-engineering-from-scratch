// 6 concept loops (480x270) as GSAP timelines; needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,L,TAU,hd,fin} = K,D2R = Math.PI / 180,T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 // D: a text node you set from draw(); .e is the node for tweens
 const D = (p,x,y,cls,an) => {const e = $(p,'text',{x,y,'font-size':15,class:cls || '','text-anchor':an || 'start'}); let l = ''; const f = (s,a) => {if (s !== l) {l = s; e.textContent = s;} if (a) A(e,a);}; f.e = e; return f;};
 const stage = (m,cap,ko) => {const q = K.stage(m,cap,ko,480,270); m.caption(cap,ko); m.replayButton(); return q;};
 const f2 = x => x.toFixed(2),DA = 'stroke-dasharray',DO = 'stroke-dashoffset';

 R.gs('pinhole-rays',(el,m) => {
  const g = stage(m,'A pixel is a ray; depth picks the point on it. A depth error slides the point along the ray, sideways by dz*(u-cx)/fx (example fx = 600 px, cx = 320 px).','픽셀은 광선이고 깊이가 그 위의 점을 고릅니다. 깊이가 틀리면 점이 광선을 따라 밀려 옆으로 dz*(u-cx)/fx만큼 어긋납니다(예: fx = 600, cx = 320 px).');
  const OX = 36,OY = 195,Z = 250,ZP = 136,FX = 600,CX = 320,Z1 = 1,Z2 = 1.15,X = z => OX + z * Z,Y = (z,u) => OY - (u - CX) / FX * z * Z;
  $(g,'line',{x1:OX,y1:OY,x2:460,y2:OY,class:'s sm',[DA]:'3 6'});
  $(g,'line',{x1:X(Z2),y1:60,x2:X(Z2),y2:216,class:'s sm w3',[DA]:'2 7'}); T(m,g,X(Z2),232,'table behind','뒤쪽 탁자','m','middle');
  $(g,'line',{x1:ZP,y1:OY - 44,x2:ZP,y2:OY + 30,class:'s st w3'}); RR(g,12,OY - 15,26,30,7,'f s st');
  const cgo = $(g,'g',{}),cgi = $(cgo,'g',{}); RR(cgi,-11,-28,22,28,6,'f s st');
  const ray = $(g,'line',{class:'s sd',pathLength:1,[DA]:'1 1'}),ly = [$(g,'path',{class:'s n sm',[DA]:'3 4'}),$(g,'path',{class:'s n sk w3',pathLength:1,[DA]:'1 1'})];
  const tp = CC(g,0,0,6,'t'),mk = CC(g,0,0,6,'w'),px = CC(g,ZP,0,5,'t'),sw = [$(g,'path',{d:'M14 245h18',class:'s n sm',[DA]:'3 4'}),$(g,'path',{d:'M14 262h18',class:'s n sk w3'})];
  const lc = D(g,0,0,'m','end'),nt = D(g,16,22,'g'),r1 = D(g,40,249,'g'),r2 = D(g,40,266,'m');
  const o = {u:520,z:.3},MSG = [[.8,'A pixel is a ray.','픽셀은 광선입니다.'],[2.4,'Depth picks one point on the ray.','깊이가 광선 위의 한 점을 고릅니다.'],[5,'A wrong depth slides the point along it.','깊이가 틀리면 점이 광선을 따라 밀립니다.'],[7.4,'Farther from the centre, more sideways error.','중심에서 멀수록 옆 오차가 커집니다.']];
  const draw = t => {
   const u = o.u,sy = x => OY + (Y(1,u) - OY) * (x - OX) / Z,x1 = X(Z1),y1 = Y(Z1,u),x2 = X(Z2),y2 = Y(Z2,u);
   A(ray,{x1:OX,y1:OY,x2:440,y2:sy(440)}); A(px,{cy:sy(ZP)}); lc(m.t('pixel u = ','픽셀 u = ') + Math.round(u),{x:ZP - 8,y:sy(ZP) - 12});
   A(tp,{cx:x1,cy:y1}); A(cgo,{transform:`translate(${x1} ${y1})`}); A(mk,{cx:X(o.z),cy:Y(o.z,u)});
   A(ly[0],{d:`M${x1} ${y1}L${x2} ${y1}`}); A(ly[1],{d:`M${x2} ${y1}L${x2} ${y2}`});
   const n = MSG.filter(s => t >= s[0]).pop() || MSG[0]; nt(m.t(n[1],n[2]));
   r1(m.t('depth error 0.15 m along the ray','깊이 오차 0.15 m (광선 방향)')); r2(`${m.t('sideways', '옆 오차')} = 0.15 x (${Math.round(u)} - 320) / 600 = ${(.15 * (u - CX) / FX * 100).toFixed(1)} cm`);
 };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,12.9).addLabel('ray',.8).addLabel('scan',2.4).addLabel('pick',4.2).addLabel('err',5.6).addLabel('side',7.4);
  MSG.forEach(s => tl.fromTo(nt.e,{autoAlpha:0},{autoAlpha:1,duration:.3},s[0]));
  tl.fromTo(ray,{attr:{[DO]:1}},{attr:{[DO]:0},duration:1.6,ease:'power3.out'},'ray')
   .fromTo(px,{attr:{r:0}},{attr:{r:5},duration:.4,ease:'back.out(3)'},'ray')
   .fromTo(lc.e,{autoAlpha:0},{autoAlpha:1,duration:.4},'ray')
   .fromTo(cgi,{scale:.5,autoAlpha:0,transformOrigin:'50% 100%'},{scale:1,autoAlpha:1,duration:.5,ease:'back.out(2)'},'scan-=.2')
   .fromTo(mk,{autoAlpha:0},{autoAlpha:1,duration:.3},'scan')
   .to(o,{z:1.4,duration:.9,ease:'sine.inOut'},'scan').to(o,{z:.3,duration:.9,ease:'sine.inOut'},'scan+=.9').to(o,{z:1,duration:.8,ease:'power3.out'},'pick')
   .fromTo(tp,{attr:{r:0}},{attr:{r:6},duration:.4,ease:'back.out(3)'},'pick+=.8')
   .to(o,{z:1.15,duration:.8,ease:'power2.inOut'},'err')
   .fromTo([ly[0],sw[0],sw[1],r1.e,r2.e],{autoAlpha:0},{autoAlpha:1,duration:.5,stagger:.1},6.4)
   .fromTo(ly[1],{attr:{[DO]:1}},{attr:{[DO]:0},duration:.7,ease:'power2.out'},6.6)
   .to(o,{u:580,duration:3,ease:'sine.inOut'},'side').to(o,{u:520,duration:1.8,ease:'sine.inOut'},11.4);
  m.play(tl,{rest:10.8,draw});
});

 R.gs('bayes-belief',(el,m) => {
  const g = stage(m,'Predict shifts one cell and blurs (5% short, 90% exact, 5% long). Update multiplies by 0.9 where a cell matches the reading, 0.1 where not, then normalises.','예측은 한 칸 밀며 퍼뜨립니다(5% 짧게, 90% 정확히, 5% 길게). 갱신은 읽은 값과 맞는 칸에 0.9, 아닌 칸에 0.1을 곱하고 합을 1로 맞춥니다.');
  const DR = [1,1,0,1,0,0,0,1,1,1,0,0,1,0,1,0,0,0,0,0],N = 20,K3 = [.05,.9,.05],KS = 9,ST = 1.35;
  const pred = b => b.map((_,i) => K3.reduce((s,p,k) => s + p * b[(i - k + N) % N],0)),upd = (b,z) => {const q = b.map((p,i) => p * (DR[i] === z ? .9 :.1)),s = q.reduce((a,c) => a + c,0); return q.map(p => p / s);};
  const pri = [Array(N).fill(1 / N)],post = [],zs = [];
  for (let k = 0; k < KS; k++) {zs.push(DR[7 + k]); post.push(upd(pri[k],zs[k])); pri.push(pred(post[k]));}
  const cx = i => 20 + i * 22 + 11,BY = 246,H = 135;
  const cells = DR.map((d,i) => RR(g,20 + i * 22 + 1,80,20,22,5,d ? 'f s st' :'c s sm')),bars = DR.map((_,i) => RR(g,cx(i) - 7,BY - H / N,14,H / N,3,'t'));
  const rb = $(g,'g',{}); RR(rb,-11,-27,22,18,7,'f s st'); CC(rb,-4,-19,2,'g'); CC(rb,4,-19,2,'g'); $(rb,'path',{d:'M0 -27V-33M-4 -4L0 0L4 -4',class:'s n st'}); gsap.set(rb,{x:cx(7),y:76});
  const ph = D(g,16,22,'g'),sn = D(g,0,64,'m'),en = D(g,16,266,'m'); RR(g,330,256,14,10,3,'f s st'); T(m,g,350,266,'door','문','m'); RR(g,400,256,14,10,3,'c s sm'); T(m,g,420,266,'wall','벽','m');
  const draw = t => {
   const w = Math.max(0,t - .3) / ST,k = Math.min(KS - 1,Math.floor(w)),u = w - k,rx = gsap.getProperty(rb,'x'); let h = 0;
   let sm = 0; const hp = bars.map(b => b.getAttribute('height') / H); hp.forEach(p => sm += p);   // bars move in a stagger: normalise so the entropy is always of a real distribution
   for (let i = 0; i < N; i++) {const p = hp[i] / (sm || 1); if (p > 1e-9) h -= p * Math.log(p);}
   ph(u < .55 ? m.t('update: keep cells that match','갱신: 읽은 값과 맞는 칸을 키움') :m.t('predict: move, add doubt','예측: 이동, 불확실성 추가'));
   sn(u < .55 ? m.t(zs[k] ? 'sees a door' :'sees a wall',zs[k] ? '문이 보임' :'벽이 보임') :'',{x:rx > 360 ? rx - 18 :rx + 18,y:64,'text-anchor':rx > 360 ? 'end' :'start'});
   en(m.t('entropy ','엔트로피 ') + f2(h) + ' nats');
 };
  const tl = m.timeline({repeatDelay:.3}),hs = b => ({attr:{y:i => BY - b[i] * H,height:i => b[i] * H}});
  fin(tl,g,12.45);
  for (let k = 0; k < KS; k++) {
   const s0 = .3 + k * ST,fr = {amount:.12,from:7 + k};   // the wave starts at the cell the robot sees
   tl.to(cells[7 + k],{scale:1.25,duration:.14,ease:'power2.out',yoyo:true,repeat:1},s0 + .06)
    .to(bars,{...hs(post[k]),duration:.4,ease:'power2.out',stagger:fr},s0 + .08)
    .to(bars,{...hs(pri[k + 1]),duration:.4,ease:'power2.inOut',stagger:fr},s0 + .74)
    .to(rb,{x:cx(8 + k),duration:.45,ease:'power2.inOut'},s0 + .74).to(rb,{y:70,duration:.22,ease:'power2.out',yoyo:true,repeat:1},s0 + .74);
 }
  m.play(tl,{rest:5,draw});
});

 R.gs('lidar-grid',(el,m) => {
  const g = stage(m,'A beam adds 0.85 where it ends and subtracts 0.4 along its path (clamped to +-5). Right: the heading error grows 0.003 rad per scan.','빔은 끝난 칸에 0.85를 더하고 지나온 칸에서 0.4를 뺍니다(±5 제한). 오른쪽은 스캔마다 방향 오차가 0.003 rad 늘어납니다.');
  const NX = 22,NY = 14,NS = 200,NB = 24,E = .003,occ = (i,j) => i < 1 || j < 1 || i > 20 || j > 12 || (i >= 9 && i < 13 && j >= 5 && j < 9);
  const pose = k => {const a = TAU * k / NS; return [11 + 7.3 * Math.cos(a),7 + 3.8 * Math.sin(a),Math.atan2(3.8 * Math.cos(a),-7.3 * Math.sin(a))];};
  const rg = [],P = [pose(0)],Q = [pose(0)],cell = (x,y) => {const i = Math.floor(x),j = Math.floor(y); return i >= 0 && j >= 0 && i < NX && j < NY ? j * NX + i :-1;},cp = (a,b,t) => Math.min(b,Math.max(a,t));
  for (let k = 0; k < NS; k++) {
   const [x,y,th] = pose(k),r = []; for (let b = 0; b < NB; b++) {const a = th + TAU * b / NB; let d = 0; while (d < 9 && !occ(Math.floor(x + Math.cos(a) * d),Math.floor(y + Math.sin(a) * d))) d += .25; r.push(d < 9 ? d :-9);} rg.push(r);
   if (k) {P.push(pose(k)); const q0 = Q[k - 1],a = E * k,c = Math.cos(a),s = Math.sin(a),dx = P[k][0] - P[k - 1][0],dy = P[k][1] - P[k - 1][1]; Q.push([q0[0] + dx * c - dy * s,q0[1] + dx * s + dy * c,P[k][2] + a]);}
 }
  const build = ps => {
   const Lg = new Float32Array(NX * NY),sn = [Lg.slice()],mk = new Uint8Array(NX * NY);
   for (let k = 0; k < NS; k++) {
    mk.fill(0); const [x,y,th] = ps[k];
    rg[k].forEach((d,b) => {const a = th + TAU * b / NB,e = s => cell(x + Math.cos(a) * s,y + Math.sin(a) * s); for (let s = 0; s < (d < 0 ? 9 :d); s += .25) {const c = e(s); if (c >= 0 && !mk[c]) mk[c] = 1;} if (d >= 0 && e(d) >= 0) mk[e(d)] = 2;});
    mk.forEach((v,c) => {if (v) Lg[c] = cp(-5,5,Lg[c] + (v > 1 ? .85 :-.4));}); if (k % 5 === 4) sn.push(Lg.slice());
  }
   return sn;
 };
  const gs = [{ps:P,sn:build(P),x0:10},{ps:Q,sn:build(Q),x0:250}];
  gs.forEach(G => {
   G.g = $(g,'svg',{x:G.x0,y:72,width:220,height:140,viewBox:`${G.x0} 72 220 140`}); G.c = []; G.v = new Int16Array(NX * NY).fill(-99); for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) G.c.push(RR(G.g,G.x0 + i * 10 + .5,72 + j * 10 + .5,9,9,2,'',{opacity:0}));
   G.fr = RR(G.g,G.x0,72,220,140,4,'n s sl'); G.bm = [...Array(NB / 2)].map(() => $(G.g,'line',{class:'s sw',opacity:.6,'stroke-width':1})); G.rb = $(G.g,'path',{d:'M-6 -5L7 0L-6 5Z',class:'t s st'});
 });
  const ti = [T(m,g,10,64,'known poses','알려진 자세','g'),T(m,g,250,64,'drifting heading','틀어지는 방향','g')],c1 = D(g,10,234,'m'),c2 = D(g,250,234,'m'),o = {p:0};
  let ls = -1;
  const draw = () => {
   const s = Math.min(40,Math.floor(41 * o.p)),k = Math.max(0,s * 5 - 1);
   if (s !== ls) {   // the map only changes every 5th scan
    ls = s;
    gs.forEach(G => {
     const sn = G.sn[s]; for (let c = 0; c < sn.length; c++) {const l = sn[c],p = 1 - 1 / (1 + Math.exp(l)),op = l > 0 ? .3 + .7 * p :l < 0 ? Math.min(.55,-l * .35) :0,v = Math.round(op * 20) * (l > 0 ? 1 :-1); if (v !== G.v[c]) {G.v[c] = v; A(G.c[c],{opacity:op,class:l > 0 ? 't' :'f'});}}
     const [x,y,th] = G.ps[k]; G.bm.forEach((b,i) => {const r = rg[k][i * 2],d = r < 0 ? 9 :r,a = th + TAU * i * 2 / NB; A(b,{x1:G.x0 + x * 10,y1:72 + y * 10,x2:G.x0 + (x + Math.cos(a) * d) * 10,y2:72 + (y + Math.sin(a) * d) * 10});});
     A(G.rb,{transform:`translate(${G.x0 + x * 10} ${72 + y * 10}) rotate(${th / D2R})`});
   });
  }
   c1(m.t('scan ','스캔 ') + (k + 1) + ' / 200'); c2(m.t('heading error ','방향 오차 ') + Math.round(E * k / D2R) + '°');   // pose k was built with heading error E*k
 };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,13.2);
  tl.from(ti,{y:-8,autoAlpha:0,duration:.5,ease:'power2.out',stagger:.15},.1)
   .fromTo(gs.map(G => G.g),{autoAlpha:0},{autoAlpha:1,duration:.5,stagger:.15},.2)
   .to(o,{p:1,duration:11,ease:'none'},.8)
   .to(gs[1].fr,{strokeWidth:5,duration:.3,ease:'power2.out',yoyo:true,repeat:1},12.2);
  m.play(tl,{rest:12.5,draw});
});

 R.gs('trapezoid-profile',(el,m) => {
  const g = stage(m,'Same move (d = 1, T = 2 s). A step in acceleration is a jerk spike and the motor feels a torque step. The quintic keeps jerk under 60 d/T^3.','같은 움직임입니다(d = 1, T = 2초). 가속도 계단은 저크 스파이크라 모터에는 토크 계단으로 느껴집니다. 5차는 저크를 60 d/T^3 이하로 둡니다.');
  const Tt = 2,ta = .5,ac = 1 / (ta * (Tt - ta)),vm = 1 / (Tt - ta),px = t => 100 + t * 150,py = a => 100 - a * 38;
  const AC = [t => (6 - 12 * t / Tt) / 4,t => t < ta ? ac :t > Tt - ta ? -ac :0,t => {const s = t / Tt; return (60 * s - 180 * s * s + 120 * s ** 3) / 4;}];
  // the position profiles ARE the easings of the block tween
  const Q = [t => 3 * (t / Tt) ** 2 - 2 * (t / Tt) ** 3,t => t < ta ? .5 * ac * t * t :t > Tt - ta ? 1 - .5 * ac * (Tt - t) ** 2 :vm * (t - ta / 2),t => {const s = t / Tt; return 10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5;}];
  const J = [[0,2],[0,.5,1.5,2],[]],ts = [.6,3.9,7.2],cls = ['s n sm w3','s n sw w3','s n sk w4'],nm = [['cubic','3차'],['trapezoid','사다리꼴'],['quintic','5차']];
  const path = i => {const x = []; for (let t = -.4; t < 2.41; t += .03) x.push(+t.toFixed(3)); x.push(...J[i]); x.sort((a,b) => a - b); return 'M' + x.flatMap(t => J[i].includes(t) ? [[t,a0(i,t - 1e-6)],[t,a0(i,t + 1e-6)]] :[[t,a0(i,t)]]).map(([t,a]) => px(t) + ' ' + py(a)).join('L');};
  const a0 = (i,t) => t < 0 || t > Tt ? 0 :AC[i](t);
  $(g,'line',{x1:30,y1:100,x2:462,y2:100,class:'s sl'}); [0,Tt].forEach(t => $(g,'line',{x1:px(t),y1:36,x2:px(t),y2:167,class:'s sl',[DA]:'3 6'}));
  A(T(m,g,20,100,'acceleration','가속도','m','middle'),{transform:'rotate(-90 20 100)'});
  T(m,g,px(0),181,'t = 0','t = 0','m','middle'); T(m,g,px(Tt),181,'t = 2 s','t = 2초','m','middle');
  const cr = [0,1,2].map(i => {const r = $($(g,'clipPath',{id:'mbt' + i}),'rect',{y:0,height:270,width:px(-.4) - 4}); $(g,'path',{d:path(i),class:cls[i],'clip-path':`url(#mbt${i})`}); return r;});
  nm.forEach((n,i) => {const x = [16,118,250][i]; $(g,'path',{d:`M${x} 18h20`,class:cls[i]}); T(m,g,x + 26,23,n[0],n[1],'m');});
  $(g,'line',{x1:60,y1:214,x2:420,y2:214,class:'s sl w6'});
  const bk = $(g,'g',{}),bs = $(bk,'g',{}); RR(bs,47,203,26,22,7,'f s st'); const kn = T(m,bk,60,198,'knock','덜컥','g','middle'),nt = D(g,16,262,'g');
  gsap.set(kn,{autoAlpha:0});
  const msg = [['cubic: acceleration jumps at the start','3차: 시작할 때 가속도가 점프합니다'],['trapezoid: it jumps too, four times','사다리꼴: 네 번이나 점프합니다'],['quintic: starts at zero, no jump','5차: 0에서 시작해 점프가 없습니다']];
  // Same dt, endpoint padding and finite differences as 09/01 code/main.py.
  const dt = .002,jerk = AC.map(a => {
   const acc = [0,...Array.from({length:Tt / dt + 1},(_,i) => a(i * dt)),0];
   return Math.max(...acc.slice(1).map((v,i) => Math.abs(v - acc[i]) / dt));
  });
  const peaks = D(g,16,242,'m');
  const draw = t => {
   nt(t > 10.4 ? m.t('only the quintic is smooth at both ends','5차만 양 끝에서 매끄럽습니다') :m.t(...msg[t < ts[1] ? 0 :t < ts[2] ? 1 :2]));
   peaks(m.t('peak jerk: ','최대 저크: ') + jerk.map(j => j.toFixed(1)).join(' / '));
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,12.2);
  [.3,ts[1],ts[2],10.4].forEach(t => tl.fromTo(nt.e,{autoAlpha:0},{autoAlpha:1,duration:.3},t));
  ts.forEach((b,i) => {
   tl.fromTo(cr[i],{attr:{width:px(-.4) - 4}},{attr:{width:px(2.4)},duration:2.8,ease:'none'},b)
    .fromTo(bk,{x:0},{x:360,duration:Tt,ease:p => Q[i](p * Tt)},b + .4);
   J[i].forEach(j => tl.to(bs,{x:7,duration:.06,ease:'power1.out'},b + .4 + j).to(bs,{x:0,duration:.5,ease:'elastic.out(1,.3)'},b + .46 + j)
    .to(kn,{autoAlpha:1,duration:.05},b + .4 + j).to(kn,{autoAlpha:0,duration:.5,ease:'power2.in'},b + .45 + j));
   if (i < 2) tl.to(bk,{x:0,duration:.6,ease:'power2.inOut'},b + 2.7);
 });
  m.play(tl,{rest:11.5,draw});
});

 R.gs('quad-thrust',(el,m) => {
  const g = stage(m,'Planar model, m = 0.5 kg, I = 0.004 kg m^2. With T = m g and 0.002 N m for 1 s the body tilts 14 degrees and moves about 0.2 m. Slowed 5x.','평면 모델, m = 0.5 kg, I = 0.004 kg m^2. T = m g에 0.002 N m를 1초 주면 14도 기울고 약 0.2 m 움직입니다. 5배 느립니다.');
  const SC = 300,QX = 100,QY = 196,OX = 385,OY = 150; $(g,'line',{x1:10,y1:236,x2:290,y2:236,class:'s st w3'});
  const qd = $(g,'g',{}),qa = $(qd,'g',{transform:'scale(1.3)'}),qr = $(qa,'g',{});   // qr's bbox is centred on the body so GSAP rotates about it
  CC(qr,0,0,44,'n'); $(qr,'path',{d:'M-20 -6V-18M20 -6V-18',class:'s st w3'}); RR(qr,-28,-7,56,14,7,'f s st'); CC(qr,0,0,2.4,'g'); const ro = [-20,20].map(x => $(qr,'ellipse',{cx:x,cy:-20,rx:18,ry:3,class:'d'}));
  const th = $(qr,'path',{class:'s n sw w3'}); $(qd,'path',{d:'M0 22V50',class:'s n sm w3',[DA]:'2 5'}); gsap.set(qd,{x:QX,y:QY});
  RR(g,298,74,174,179,14,'c s sl'); T(m,g,OX + 8,OY + 62,'mg','mg','m');
  const ax = $(g,'g',{}),pa = [$(ax,'path',{class:'s n sf w4'}),$(ax,'path',{class:'s n sk w4'}),$(ax,'path',{class:'s n sw w4'}),$(ax,'path',{class:'s n sm w3',[DA]:'2 5'})];
  const hl = D(g,16,22,'g'),rd = D(g,16,266,'m'),l1 = D(ax,385,228,'g','middle'),l2 = D(ax,385,246,'g','middle'),o = {s:0,b:0};
  const draw = () => {
   const a = !o.b,s = o.s,ang = a ? 0 :.25 * s * s,Tf = a ? 1.1 :1,ux = Math.sin(ang),uz = Math.cos(ang),pl = 60 * Tf,tn = 34 * Tf;
   A(th,{d:`M0 0V${-tn}M-5 ${-tn + 8}L0 ${-tn}L5 ${-tn + 8}`});
   A(pa[0],{d:hd(OX,OY,0,-pl * uz)}); A(pa[1],{d:hd(OX,OY,pl * ux,0)}); A(pa[2],{d:hd(OX,OY,pl * ux,-pl * uz)}); A(pa[3],{d:`M${OX} ${OY}v60`});
   hl(a ? m.t('10% extra thrust: it only climbs','추력 10% 증가: 위로만 올라갑니다') :m.t('Torque tilts it; the tilt turns thrust sideways','토크로 기울이면 추력이 옆으로 향합니다'));
   rd(`t = ${f2(s)} s   ` + (a ? `z = +${f2(.49 * s * s)} m` :`θ = ${(ang / D2R).toFixed(1)}°   x = ${f2(.2044 * s ** 4)} m`) + m.t('   (5x slow-mo)','   (5배 느리게)'));
   l1(m.t('up ','위 ') + f2(Tf * uz) + ' mg'); l2(m.t('side ','옆 ') + f2(Tf * ux) + ' mg');
 };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,11.4);
  tl.fromTo([qd,ax],{autoAlpha:0},{autoAlpha:1,duration:.4},0).fromTo(hl.e,{autoAlpha:0},{autoAlpha:1,duration:.4},.2)
   .to(o,{s:.6,duration:3,ease:'none'},.6).to(qd,{y:QY - .49 * .36 * SC,duration:3,ease:'power1.in'},.6)   // z = 0.49 s^2 (power1 = t^2)
   .to([qd,ax,hl.e],{autoAlpha:0,duration:.4},4).set(o,{s:0,b:1},4.4).set(qd,{y:QY},4.4)
   .to([qd,ax,hl.e],{autoAlpha:1,duration:.4},4.5)
   .to(o,{s:1,duration:5,ease:'none'},4.9).to(qd,{x:QX + .2044 * SC,duration:5,ease:'power3.in'},4.9)   // x = 0.2044 s^4 (power3 = t^4)
   .to(qr,{rotation:14.32,duration:5,ease:'power1.in'},4.9)   // 0.25 s^2 rad
   .to(qd,{y:QY + .0102 * SC,duration:5,ease:t => t ** 6},4.9)   // z'' = g (cos θ - 1) with θ = 0.25 s^2: z = -0.0102 s^6 m, a 3 px sag
   .fromTo(ro,{attr:{rx:18}},{attr:{rx:14},duration:.06,yoyo:true,repeat:200},0);
  m.play(tl,{rest:10.2,draw});
});

 R.gs('contact-friction',(el,m) => {
  const g = stage(m,'Sticking needs tan(theta) <= mu. With mu = 0.5 the block lets go at 26.6 degrees, then accelerates at g (sin(theta) - mu cos(theta)). Slowed.','붙어 있으려면 tan(theta) <= mu여야 합니다. mu = 0.5이면 26.6도에서 놓이고 g (sin(theta) - mu cos(theta))로 가속합니다. 느리게 보여 줍니다.');
  const MU = .5,PHI = Math.atan(MU),HX = 30,HY = 206,LN = 270,TW = 56,S0 = HX + 220,SM = HX + 40,MAXA = 40 * D2R;
  T(m,g,16,22,'A block sticks while tan θ ≤ μ','tan θ ≤ μ인 동안 블록이 붙어 있습니다','g');
  const pl = $(g,'g',{}); RR(pl,HX - 14,HY,LN + 28,14,7,'f s st');
  const bl = $(pl,'g',{}); RR(bl,-TW / 2,-TW,TW,TW,8,'c s st'); [-9,9].forEach(x => CC(bl,x,-34,2.6,'g')); const cn = $(bl,'polygon',{class:'k',opacity:.3}),ar = $(bl,'path',{class:'s n w4'});
  gsap.set(bl,{x:S0,y:HY});
  RR(g,420,76,28,140,8,'c s st'); const bar = RR(g,424,216,20,0,5,'k'),my = 216 - 140 * MU; $(g,'path',{d:`M414 ${my}H454`,class:'s sw w3',[DA]:'4 4'}); T(m,g,410,my + 5,'μ = 0.5','μ = 0.5','m','end'); T(m,g,434,238,'tan θ','tan θ','g','middle');
  $(g,'polygon',{points:'16,257 40,248 40,266',class:'k',opacity:.4}); T(m,g,46,266,'friction cone','마찰 원뿔','m'); $(g,'path',{d:hd(170,261,28,0),class:'s n sk w4'}); T(m,g,214,266,'force needed to hold','버티는 데 필요한 힘','m');
  const rd = D(g,16,246,'g'); let kc = '',SL = [0];
  const draw = t => {
   if (t < 9.6) gsap.set(bl,{x:S0 - SL[Math.min(SL.length - 1,Math.round(t * 100))]});
   const th = -gsap.getProperty(pl,'rotation') * D2R,tn = Math.tan(th),ok = tn <= MU + 1e-6,c = Math.sin(PHI) * 62,d = Math.cos(PHI) * 62,h = 140 * Math.min(1,tn),k = ok ? 'k' :'x';
   A(cn,{points:`0,0 ${-c},${-d} ${c},${-d}`}); A(ar,{d:hd(0,0,Math.sin(th) * 58,-Math.cos(th) * 58),class:'s n w4 ' + (ok ? 'sk' :'sb')});
   A(bar,{y:216 - h,height:h}); if (k !== kc) A(bar,{class:kc = k});
   rd(`${m.t('tilt ', '기울기 ')}${Math.round(th / D2R)}°   tan θ = ${f2(tn)}   ` + (ok ? m.t('sticks','붙어 있음') :m.t('slides','미끄러짐')));
 };
  // block slides by the lesson's a = g (sin θ - μ cos θ) (zero while it sticks), θ = the tilt on screen; integrated once, scaled (bisection) to reach the lower end at 8.6 s
  const thAt = u => MAXA * (.5 - .5 * Math.cos(Math.PI * Math.min(1,Math.max(0,(u - 1) / 6)))),D0 = S0 - SM,simS = k => {const o = [0]; let v = 0,s = 0; for (let u = 0; u < 10; u += .01) {const th = thAt(u); v += k * Math.max(0,Math.sin(th) - MU * Math.cos(th)) * .01; s = Math.min(D0,s + v * .01); o.push(s);} return o;};
  let lo = 0,hi = 4000; for (let i = 0; i < 40; i++) {const k = (lo + hi) / 2; if (simS(k)[860] >= D0) hi = k; else lo = k;}
  SL = simS(hi);
  const tl = m.timeline({repeatDelay:.3}),so = `${HX} ${HY}`;
  fin(tl,g,11.8);
  tl.to(pl,{rotation:-40,svgOrigin:so,duration:6,ease:'sine.inOut'},1)
   .to(bl,{autoAlpha:0,duration:.4},9.6).set(bl,{x:S0},10).to(bl,{autoAlpha:1,duration:.4},10.4)
   .to(pl,{rotation:0,svgOrigin:so,duration:1.4,ease:'sine.inOut'},10.2);
  m.play(tl,{rest:8.6,draw});
});
 // 03/08: kept with the older concepts so p03.js stays below 20 KB.
 R.gs('replan-loop',(el,m) => {
  const {S} = window.MB;
  const poly = (pts,n,fx,fy) => pts.slice(0,n + 1).map((p,i) => `${i ? 'L' :'M'}${fx(p[0],i).toFixed(1)} ${fy(p[1],i).toFixed(1)}`).join('');
  const g = stage(m,'Double integrator from 4 m, dt = 0.1, |u| <= 0.5. Each tick MPC plans N = 20 steps (2 s) ahead with the limit inside, applies only the first input, then plans again.','이중 적분기가 4 m에서 출발합니다(dt = 0.1, |u| <= 0.5). 매 tick MPC가 한계를 넣고 N = 20 step(2초) 앞을 계획하고 첫 입력만 쓴 뒤 다시 계획합니다.');
  const dt = .1,N = 20,UM = .5,NT = 120,Q = [1,.1],R0 = .1;
  // terminal cost P from the Riccati loop (lesson 03/06); plan = box-constrained quadratic by projected gradient with momentum
  let P = [[1,0],[0,.1]],K; for (let i = 0; i < 2000; i++) {const a = P[0][0],b = P[0][1],c = P[1][1],S = R0 + dt * dt * dt * dt / 4 * a + dt ** 3 * b + dt * dt * c,PB = [a * dt * dt / 2 + b * dt,b * dt * dt / 2 + c * dt];
   const BPA = [PB[0] + 0,0].map((_,j) => j ? dt * PB[0] + PB[1] : PB[0]); K = BPA.map(v => v / S);
   const Ak = [[1 - dt * dt / 2 * K[0],dt - dt * dt / 2 * K[1]],[-dt * K[0],1 - dt * K[1]]],PA = [[a,a * dt + b],[b,b * dt + c]];
   P = [0,1].map(r => [0,1].map(cc => (r === cc ? Q[r] :0) + [0,1].reduce((s,k) => s + (k ? PA[k][r] :PA[0][r]) * Ak[k][cc],0)));}
  // x_i = [pos, vel]; pos_i = x0 + (i+1) dt v0 + sum_j g_pos(i-j) u_j, vel_i = v0 + sum dt u_j
  const gp = k => dt * dt * (k + .5),H = []; for (let a = 0; a < N; a++) {H.push([]); for (let b = 0; b < N; b++) {let h = a === b ? R0 :0; for (let i = Math.max(a,b); i < N; i++) {const w = i === N - 1 ? [P[0][0],P[0][1],P[1][1]] :[Q[0],0,Q[1]]; h += w[0] * gp(i - a) * gp(i - b) + w[1] * (gp(i - a) * dt + dt * gp(i - b)) + w[2] * dt * dt;} H[a].push(h);}}
  const L = (() => {let v = H.map((_,i) => 1 + i % 3 * .1); for (let it = 0; it < 60; it++) {const w = H.map(r => r.reduce((s,x,j) => s + x * v[j],0)),nn = Math.hypot(...w); v = w.map(z => z / nn);} return H.map(r => r.reduce((s,x,j) => s + x * v[j],0)).reduce((s,x,i) => s + x * v[i],0) * 1.05;})();
  const plan = x => {const f = H.map((_,a) => {let s = 0; for (let i = a; i < N; i++) {const w = i === N - 1 ? [P[0][0],P[0][1],P[1][1]] :[Q[0],0,Q[1]],p0 = x[0] + (i + 1) * dt * x[1],v0 = x[1]; s += w[0] * gp(i - a) * p0 + w[1] * (gp(i - a) * v0 + dt * p0) + w[2] * dt * v0;} return s;});
   let U = new Array(N).fill(0),Y = U,t = 1; for (let it = 0; it < 500; it++) {const Un = Y.map((y,a) => Math.max(-UM,Math.min(UM,y - (H[a].reduce((s,h,j) => s + h * Y[j],0) + f[a]) / L))),tn = (1 + Math.sqrt(1 + 4 * t * t)) / 2; Y = Un.map((u,a) => u + (t - 1) / tn * (u - U[a])); U = Un; t = tn;} return U;};
  const X = [[4,0]],PL = [],US = []; for (let k = 0; k < NT; k++) {const x = X[k],U = plan(x); PL.push(U); US.push(U[0]); X.push([x[0] + dt * x[1] + dt * dt / 2 * U[0],x[1] + dt * U[0]]);}
  const fx = k => 40 + k * 3.4,fy = v => 190 - v * 36;
  T(m,g,16,24,'position (m)','위치 (m)','m'); $(g,'path',{d:'M40 44V190H460',class:'s n sm'}); $(g,'path',{d:`M40 ${fy(0)}H460`,class:'s n sm',[DA]:'3 5'});
  const pa = $(g,'path',{class:'s n sf w3',[DA]:'5 4'}),tr = $(g,'path',{class:'s n sk w4'}),dot = CC(g,0,0,5,'g'),ub = RR(g,0,0,0,0,2,'f'),r1 = D(g,16,248,'g'),r2 = D(g,16,266,'m');
  T(m,g,460,208,'u, limit ±0.5','u, 한계 ±0.5','m','end'); $(g,'path',{d:'M40 224H300',class:'s n sm'}); $(g,'path',{d:'M40 214v20M300 214v20',class:'s n sm',[DA]:'2 3'});
  const draw = t => {
   const k = Math.min(NT - 1,Math.round(S(t,.6,9.4) * (NT - 1))),x = X[k],U = PL[k]; let q = x.slice(),pts = [[k,x[0]]]; U.slice(0,NT - k).forEach((u,j) => {q = [q[0] + dt * q[1] + dt * dt / 2 * u,q[1] + dt * u]; pts.push([k + j + 1,q[0]]);});
   A(tr,{d:poly(X.map((v,i) => [i,v[0]]),k,i => fx(i),fy)}); A(pa,{d:poly(pts,pts.length,i => fx(i),fy)}); A(dot,{cx:fx(k),cy:fy(x[0])});
   A(ub,{x:170 + (US[k] < 0 ? US[k] * 260 :0),y:216,width:Math.abs(US[k]) * 260,height:16,class:Math.abs(US[k]) > UM - 1e-6 ? 'x' :'f'});
   r1(`t = ${(k * dt).toFixed(1)} s | position ${x[0].toFixed(2)} m | u = ${US[k].toFixed(2)}`); r2(m.t(`dashed: plan for the next ${N * dt} s, only its first step is used`,`점선: 앞으로 ${N * dt}초 계획, 첫 step만 씁니다`));
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,10.4); m.play(tl,{rest:6,draw});
 });

})();
