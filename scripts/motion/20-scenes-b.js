// scene-06..11 (640x220) as GSAP timelines; exports kit window.MB for 21-concepts-b.js
(function () {
 const R = window.MOTION,NS = 'http://www.w3.org/2000/svg';
 const $ = (p,t,a) => {const e = document.createElementNS(NS,t); for (const k in a) e.setAttribute(k,a[k]); p.appendChild(e); return e;};
 const A = (e,a) => {for (const k in a) e.setAttribute(k,a[k]);};
 const cl = (x,a = 0,b = 1) => x < a ? a :x > b ? b :x;
 const S = (t,a,b) => cl((t - a) / (b - a)),EO = x => 1 - (1 - x) ** 3,EI = x => x < .5 ? 4 * x * x * x :1 - (-2 * x + 2) ** 3 / 2;
 const SN = x => .5 - .5 * Math.cos(Math.PI * x),L = (a,b,t) => a + (b - a) * t,TAU = Math.PI * 2;
 if (!document.getElementById('mbs')) {
  const s = document.createElement('style'); s.id = 'mbs';
  s.textContent = '.mb .f{fill:var(--pf)}.mb .d{fill:var(--pd)}.mb .l{fill:var(--pl)}.mb .b{fill:var(--pb)}.mb .c{fill:var(--card)}.mb .g{fill:var(--fg)}.mb .m{fill:var(--mut)}.mb .t{fill:var(--pt)}.mb .w{fill:var(--oops)}.mb .n{fill:none}' +
   '.mb .s{stroke-width:2;stroke-linecap:round;stroke-linejoin:round}.mb .st{stroke:var(--pt)}.mb .sl{stroke:var(--pl)}.mb .sm{stroke:var(--mut)}.mb .sw{stroke:var(--oops)}.mb .sf{stroke:var(--pf)}.mb .sd{stroke:var(--pd)}' +
   '.mb .k{fill:var(--ok)}.mb .x{fill:var(--bad)}.mb .sk{stroke:var(--ok)}.mb .sb{stroke:var(--bad)}.mb .w3{stroke-width:3}.mb .w4{stroke-width:4}.mb .w6{stroke-width:6}.mb text{fill:var(--fg);font-weight:600}';
  document.head.appendChild(s);
}
 const CC = (p,cx,cy,r,c,e) => $(p,'circle',Object.assign({cx,cy,r,class:c},e)),RR = (p,x,y,width,height,rx,c,e) => $(p,'rect',Object.assign({x,y,width,height,rx,class:c},e));
 const T = (m,p,x,y,en,ko,cls,an,sz) => {const e = $(p,'text',{x,y,'font-size':sz || 20,class:cls || '','text-anchor':an || 'start'}); const set = () => {e.textContent = m.t(en,ko);}; set(); m.onTheme(set); return e;};
 // stage: svg + bg; returns the content group that fades in/out as a whole (invisible loop seam)
 const stage = (m,en,ko,W = 640,H = 220) => {const r = m.svg(W,H,en,ko); r.svg.setAttribute('class','mb'); $(r.g,'rect',{width:W,height:H,class:'b'}); return $(r.g,'g',{});};
 const fin = (tl,q,end) => tl.fromTo(q,{autoAlpha:0},{autoAlpha:1,duration:.4,ease:'power1.out'},0).to(q,{autoAlpha:0,duration:.5,ease:'power1.in'},end);
 const hd = (x,y,dx,dy) => {const l = Math.hypot(dx,dy) || 1,ux = dx / l,uy = dy / l; return `M${x} ${y}l${dx} ${dy}m${-ux * 9 - uy * 6} ${-uy * 9 + ux * 6}l${ux * 9 + uy * 6} ${uy * 9 - ux * 6}l${ux * 9 - uy * 6} ${uy * 9 + ux * 6}`;};
 window.MB = {CC,RR,$,A,cl,S,EO,EI,SN,L,TAU,T,hd,stage,fin};
 const seed = s => () => (s = (s * 9301 + 49297) % 233280) / 233280;

 // scene-06 pinhole
 R.gs('scene-06',(el,m) => {
  const g = stage(m,'A camera turns a cube, then a tilting checkerboard, into sensor dots.','카메라가 큐브와 기울어진 체커보드를 센서 점으로 바꿉니다.');
  const PX = 330,PY = 112,SX = 440,OX = 150,OY = 112;
  RR(g,PX,62,150,100,16,'c s st');
  $(g,'line',{x1:SX,y1:72,x2:SX,y2:152,class:'s st w3'});
  const rays = [0,1,2,3].map(() => $(g,'path',{class:'s sd n',pathLength:1,'stroke-dasharray':'1 1'})),ext = $(g,'line',{class:'s sw','stroke-dasharray':'3 8'});
  const pin = CC(g,PX,PY,5,'c s st'),ob = $(g,'polygon',{class:'f s st w3'}),ax = $(g,'line',{class:'s st','stroke-dasharray':'7 7'});
  const dots = [0,1,2,3].map(() => $(g,'circle',{cx:SX,r:5,class:'t'}));
  RR(g,522,62,86,100,14,'c s st'); $(g,'path',{d:'M486 112h26m-7-6l7 6l-7 6',class:'s n sm w3'});
  const px = [0,1,2,3].map(() => $(g,'rect',{x:559,width:12,height:12,rx:3,class:'t'})),mk = $(g,'circle',{r:7,class:'w'}),mt = T(m,g,0,0,'depth?','깊이?','m','middle');
  T(m,g,336,196,'pinhole','핀홀','','end'); T(m,g,440,196,'sensor','센서','','middle'); T(m,g,565,196,'pixels','픽셀','','middle');
  const C = [-30,-30,30,-30,30,30,-30,30],B = [-4,-45,4,-45,4,45,-4,45],P = [0,0,0,0,0,0,0,0],o = {pop:0,k:0,a:0,w:0};
  const draw = () => {
   const ca = Math.cos(o.a),sa = Math.sin(o.a); let y0 = 0;
   for (let i = 0; i < 4; i++) {const x = L(C[2 * i],B[2 * i],o.k) * o.pop,y = L(C[2 * i + 1],B[2 * i + 1],o.k) * o.pop; P[2 * i] = OX + x * ca - y * sa; P[2 * i + 1] = OY + x * sa + y * ca;}
   A(ob,{points:P.join(' ')}); A(ax,{x1:OX + 45 * sa * o.pop,y1:OY - 45 * ca * o.pop,x2:OX - 45 * sa * o.pop,y2:OY + 45 * ca * o.pop,opacity:o.k * o.pop});
   for (let i = 0; i < 4; i++) {const ox = P[2 * i],oy = P[2 * i + 1],iy = oy + (PY - oy) * (SX - ox) / (PX - ox); if (!i) y0 = iy; A(rays[i],{d:`M${ox} ${oy}L${PX} ${PY}L${SX} ${iy}`}); A(dots[i],{cy:iy}); A(px[i],{y:106 - (iy - 112)});}
   const xm = L(300,70,o.w),ym = y0 + (PY - y0) * (xm - SX) / (PX - SX);
   A(ext,{x1:SX,y1:y0,x2:60,y2:y0 + (PY - y0) * (60 - SX) / (PX - SX)}); A(mk,{cx:xm,cy:ym}); A(mt,{x:xm,y:ym - 14});
 };
  const tl = m.timeline({repeatDelay:.5});
  fin(tl,g,10).addLabel('rays',1.2).addLabel('morph',3.6).addLabel('turn',4.8).addLabel('depth',5.6);
  tl.to(o,{pop:1,duration:.9,ease:'back.out(1.8)'},.2)
   .fromTo(pin,{scale:1},{scale:1.6,duration:.2,ease:'power2.out',yoyo:true,repeat:1},'rays+=.4')
   .fromTo(rays,{attr:{'stroke-dashoffset':1}},{attr:{'stroke-dashoffset':0},duration:1.4,ease:'power2.out',stagger:.12},'rays')
   .fromTo(dots,{attr:{r:0}},{attr:{r:5},duration:.5,ease:'back.out(3)',stagger:.08},2.8)
   .fromTo(px,{autoAlpha:0},{autoAlpha:1,duration:.3,stagger:.08},3)
   .to(o,{k:1,duration:1.2,ease:'power3.inOut'},'morph')
   .to(o,{a:.95,duration:2.2,ease:'sine.inOut'},'turn').to(o,{a:0,duration:2.2,ease:'sine.inOut'},'turn+=2.2')
   .fromTo([ext,mk,mt],{autoAlpha:0},{autoAlpha:1,duration:.6},'depth')
   .fromTo(o,{w:0},{w:1,duration:1.6,ease:'sine.inOut',yoyo:true,repeat:1},'depth+=.2')
   .to([ext,mk,mt],{autoAlpha:0,duration:.4},9);
  m.play(tl,{rest:7,draw});
});

 // scene-07 filter
 R.gs('scene-07',(el,m) => {
  const g = stage(m,'Noisy readings scatter; the estimate tightens around the true path.','잡음 낀 측정값 사이로 추정선이 실제 경로에 조여듭니다.');
  const N = 58,rnd = seed(7),xs = [],ty = [],zs = [],es = [],ws = [];
  let e = 112;
  for (let i = 0; i < N; i++) {const x = 24 + i * 10.4; xs.push(x); ty.push(112 + 28 * Math.sin(x / 120)); zs.push(ty[i] + (rnd() + rnd() - 1) * 36); e += Math.max(.3,1 / (i + 2)) * (zs[i] - e); es.push(e); ws.push(32 * (.2 + .8 * Math.exp(-i / 9)));}
  const cr = $($(g,'clipPath',{id:'mb7c'}),'rect',{x:0,y:0,height:220,width:29}),gl = $(g,'g',{}),c = $(g,'g',{'clip-path':'url(#mb7c)'});
  [60,112,164].forEach(y => $(gl,'line',{x1:14,x2:626,y1:y,y2:y,class:'s sl',opacity:.35}));
  $(g,'path',{d:'M' + xs.map((x,i) => x + ' ' + ty[i].toFixed(1)).join('L'),class:'s n sm','stroke-dasharray':'2 8'});
  $(c,'path',{d:'M' + xs.map((x,i) => x + ' ' + (es[i] - ws[i]).toFixed(1)).join('L') + 'L' + xs.map((x,i) => xs[N - 1 - i] + ' ' + (es[N - 1 - i] + ws[N - 1 - i]).toFixed(1)).join('L') + 'Z',class:'f',opacity:.35});
  const dots = zs.map((z,i) => $(c,'circle',{cx:xs[i],cy:z,r:3.6,class:'m',opacity:.9}));
  const est = $(c,'path',{d:'M' + xs.map((x,i) => x + ' ' + es[i].toFixed(1)).join('L'),class:'s n st w4'});
  const ro = $(g,'g',{}),rb = $(ro,'g',{}); RR(rb,-12,-17,24,16,6,'f s st'); CC(rb,-4,-9,2,'g'); CC(rb,4,-9,2,'g'); $(rb,'path',{d:'M0 -17V-23',class:'s st'});
  const lg = $(g,'g',{}); CC(lg,22,26,4,'m'); T(m,lg,34,32,'noisy readings','잡음 낀 측정','m'); $(lg,'path',{d:'M236 26h22',class:'s n st w4'}); T(m,lg,266,32,'estimate','추정','m'); $(lg,'path',{d:'M388 26h26',class:'s n sm','stroke-dasharray':'2 8'}); T(m,lg,424,32,'true path','실제 경로','m');
  const draw = () => {const cx = +cr.getAttribute('width') - 5; A(ro,{transform:`translate(${cx} ${112 + 28 * Math.sin(cx / 120) - 2})`});};
  const tl = m.timeline({repeatDelay:.4});
  fin(tl,g,9.6);
  tl.fromTo(gl,{autoAlpha:0},{autoAlpha:1,duration:.5},0)
   .fromTo(lg,{autoAlpha:0,y:-6},{autoAlpha:1,y:0,duration:.5,ease:'power2.out'},.2)
   .fromTo(cr,{attr:{width:29}},{attr:{width:xs[N - 1] + 5},duration:8,ease:'none'},.6)
   .fromTo(dots,{attr:{r:0}},{attr:{r:3.6},duration:.3,ease:'back.out(3)',stagger:8 / 57},.5)
   .fromTo(rb,{y:0},{y:-2,duration:.25,ease:'sine.inOut',yoyo:true,repeat:31},.6)
   .fromTo(est,{strokeWidth:4},{strokeWidth:7,duration:.3,ease:'power2.out',yoyo:true,repeat:1},8.8);
  m.play(tl,{rest:9.45,draw});
});

 // scene-08 lidar map
 R.gs('scene-08',(el,m) => {
  const g = stage(m,'A rover drives a room while its lidar paints an occupancy map.','로버가 방을 돌며 라이다로 점유 지도를 칠합니다.');
  const rect = (a,b,c,d) => [[a,b,c,b],[c,b,c,d],[c,d,a,d],[a,d,a,b]],SEG = [...rect(40,28,600,200),...rect(270,96,370,132),...rect(495,100,515,120)];
  const rc = (x,y,dx,dy) => {let b = 1e9; for (const s of SEG) {const ex = s[2] - s[0],ey = s[3] - s[1],de = dx * ey - dy * ex; if (!de) continue; const tt = ((s[0] - x) * ey - (s[1] - y) * ex) / de,uu = ((s[0] - x) * dy - (s[1] - y) * dx) / de; if (tt > 0 && uu >= 0 && uu <= 1 && tt < b) b = tt;} return b;};
  const NB = 14,T0 = .3,T1 = 9.3,pose = u => {const a = TAU * u; return [320 + 245 * Math.cos(a),114 + 60 * Math.sin(a),Math.atan2(60 * Math.cos(a),-245 * Math.sin(a))];};
  const hitT = new Map();
  for (let t = T0; t <= T1; t += 1 / 30) {const p = pose(S(t,T0,T1)); for (let j = 0; j < NB; j++) {const an = p[2] + t * 5 + TAU * j / NB,dx = Math.cos(an),dy = Math.sin(an),d = rc(p[0],p[1],dx,dy); if (d < 1e8) {const k = Math.floor((p[0] + dx * d + dx * .01) / 10) + ',' + Math.floor((p[1] + dy * d + dy * .01) / 10); if (!hitT.has(k)) hitT.set(k,t);}}}
  const hs = [...hitT],mp = $(g,'g',{}),cells = hs.map(([k]) => {const [i,j] = k.split(',').map(Number); return RR(mp,i * 10 + .5,j * 10 + .5,9,9,2,'t');});
  const fb = $(g,'g',{}),fan = $(fb,'polygon',{class:'f',opacity:.22}),bm = [...Array(NB)].map(() => $(fb,'line',{class:'s sd',opacity:.5}));
  const rv = $(g,'g',{}),rvi = $(rv,'g',{}); RR(rvi,-9,-14,18,4,2,'g'); RR(rvi,-9,10,18,4,2,'g'); RR(rvi,-14,-10,28,20,7,'f s st');
  CC(rvi,-3,0,4.5,'d s st'); RR(rvi,4,-7,8,14,3.5,'c'); CC(rvi,8,-2.6,1.5,'g'); CC(rvi,8,2.6,1.5,'g');
  const o = {a:0},pts = [...Array(NB)].fill('0,0');
  const draw = t => {
   const p = pose(o.a),sp = t * 5;
   for (let j = 0; j < NB; j++) {const an = p[2] + sp + TAU * j / NB,dx = Math.cos(an),dy = Math.sin(an),d = Math.min(rc(p[0],p[1],dx,dy),400),x = p[0] + dx * d,y = p[1] + dy * d; pts[j] = x.toFixed(1) + ',' + y.toFixed(1); A(bm[j],{x1:p[0],y1:p[1],x2:x,y2:y});}
   A(fan,{points:pts.join(' ')}); A(rv,{transform:`translate(${p[0]} ${p[1]}) rotate(${p[2] * 180 / Math.PI})`});
 };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.2);
  tl.fromTo(rvi,{scale:.4,autoAlpha:0},{scale:1,autoAlpha:1,duration:.6,ease:'back.out(2)'},.1)
   .fromTo(fb,{autoAlpha:0},{autoAlpha:1,duration:.4},T0)
   .to(o,{a:1,duration:T1 - T0,ease:'none'},T0)
   .fromTo(cells,{autoAlpha:0},{autoAlpha:.9,duration:.3,ease:'power1.out',stagger:i => hs[i][1]},0);
  m.play(tl,{rest:9.8,draw});
});

 // scene-09 tree
 R.gs('scene-09',(el,m) => {
  const g = stage(m,'A tree grows through obstacles to the goal, then the path lights up.','트리가 장애물 사이로 자라 목표에 닿고 경로가 켜집니다.');
  const OB = [[200,62,34],[250,165,36],[372,112,42],[470,54,30],[492,170,32]],rnd = seed(11),G = [600,110];
  const free = (x,y) => x > 14 && x < 626 && y > 14 && y < 206 && OB.every(o => Math.hypot(x - o[0],y - o[1]) > o[2] + 7);
  const N = [[40,110,-1]];
  for (let it = 0; it < 6000; it++) {
   const s = rnd() < .18 ? G :[rnd() * 620 + 10,rnd() * 200 + 10]; let bi = 0,bd = 1e9;
   N.forEach((n,i) => {const d = Math.hypot(n[0] - s[0],n[1] - s[1]); if (d < bd) {bd = d; bi = i;}});
   const n = N[bi],st = Math.min(40,bd),x = n[0] + (s[0] - n[0]) / bd * st,y = n[1] + (s[1] - n[1]) / bd * st; let ok = true;
   for (let q = 1; q <= 8; q++) if (!free(L(n[0],x,q / 8),L(n[1],y,q / 8))) {ok = false; break;}
   if (!ok) continue; N.push([x,y,bi]);
   if (Math.hypot(x - G[0],y - G[1]) < 30) {N.push([G[0],G[1],N.length - 1]); break;}
 }
  const path = []; for (let i = N.length - 1; i >= 0; i = N[i][2]) path.unshift(N[i]);
  const obs = OB.map(o => $(g,'circle',{cx:o[0],cy:o[1],r:o[2],class:'m sm','stroke-width':2,opacity:.3}));
  const edges = N.slice(1).map(n => {const p = N[n[2]]; return $(g,'line',{x1:p[0],y1:p[1],x2:p[0],y2:p[1],class:'s sd','stroke-width':1.5});});
  const pd = 'M' + path.map(p => p[0].toFixed(0) + ' ' + p[1].toFixed(0)).join('L');
  const gl = $(g,'path',{d:pd,class:'s n sf','stroke-width':10,pathLength:1,'stroke-dasharray':'1 1',opacity:.5}),pa = $(g,'path',{d:pd,class:'s n st w4',pathLength:1,'stroke-dasharray':'1 1'});
  const goal = $(g,'g',{}); CC(goal,G[0],G[1],13,'c s st'); CC(goal,G[0],G[1],5,'f');
  const st0 = CC(g,40,110,8,'f s st');
  T(m,g,16,148,'start','시작','m'); T(m,g,626,150,'goal','목표','m','end');
  const bl = $(g,'g',{}),bh = $(bl,'g',{}); $(bh,'circle',{r:9,class:'f s st w3'}); CC(bh,-3,-1,1.6,'g'); CC(bh,3,-1,1.6,'g');
  gsap.set(bl,{x:40,y:110});
  const tl = m.timeline({repeatDelay:.4}),EN = N.length - 2;
  fin(tl,g,10.6);
  tl.from(obs,{attr:{r:0},duration:.6,ease:'back.out(1.6)',stagger:.1},.1)
   .from([st0,goal],{scale:.4,autoAlpha:0,duration:.5,ease:'back.out(2)',stagger:.15},.3)
   .fromTo(edges,{autoAlpha:0},{autoAlpha:1,attr:{x2:i => N[i + 1][0],y2:i => N[i + 1][1]},duration:.18,ease:'power2.out',stagger:i => .6 + 5.6 * i / EN},0)
   .fromTo([gl,pa],{attr:{'stroke-dashoffset':1}},{attr:{'stroke-dashoffset':0},duration:1.4,ease:'power3.inOut'},6.6)
   .fromTo(bl,{autoAlpha:0},{autoAlpha:1,duration:.2},7.9);
  const len = path.map((p,i) => i ? Math.hypot(p[0] - path[i - 1][0],p[1] - path[i - 1][1]) :0),tot = len.reduce((a,b) => a + b,0); let at = 8.1;
  path.slice(1).forEach((p,i) => {const d = 1.8 * len[i + 1] / tot; tl.to(bl,{x:p[0],y:p[1],duration:d,ease:i ? i === path.length - 2 ? 'power1.out' :'none' :'power1.in'},at); at += d;});
  tl.fromTo(bh,{y:0},{y:-4,duration:.15,ease:'sine.out',yoyo:true,repeat:11},8.1)
   .fromTo(goal,{scale:1},{scale:1.35,duration:.25,ease:'back.out(3)',yoyo:true,repeat:1},9.9);
  m.play(tl,{rest:10.2});
});

 // scene-10 biped + quad
 R.gs('scene-10',(el,m) => {
  const g = stage(m,'A biped steps, then a quadrotor tilts to move sideways.','두 발 로봇이 걷고 쿼드로터가 기울어 옆으로 갑니다.');
  const GY = 186,HX = 150,LL = 46,TH = 36;
  $(g,'line',{x1:0,y1:GY + 6,x2:640,y2:GY + 6,class:'s st w3'}); const tk = $(g,'line',{x1:-40,y1:GY + 10,x2:680,y2:GY + 10,class:'s sl','stroke-width':2,'stroke-dasharray':'10 36'});
  const leg = [$(g,'path',{class:'s n sm w6'}),$(g,'path',{class:'s n st w6'})],ft = [$(g,'circle',{r:5,class:'g'}),$(g,'circle',{r:5,class:'g'})];
  const bd = $(g,'g',{}); RR(bd,-15,-36,30,38,12,'f s st'); const hg = $(bd,'g',{}); RR(hg,-13,-66,26,24,10,'c s st'); CC(hg,-4.5,-55,2.4,'g'); CC(hg,4.5,-55,2.4,'g');
  const arm = [$(g,'path',{class:'s n sm w6'}),$(g,'path',{class:'s n st w6'})];
  const qd = $(g,'g',{}),qa = $(qd,'g',{transform:'scale(1.35)'}),qr = $(qa,'g',{}); $(qr,'circle',{r:44,class:'n'}); $(qr,'path',{d:'M-20 -6V-18M20 -6V-18',class:'s st w3'}); RR(qr,-28,-7,56,14,7,'f s st'); $(qr,'circle',{r:2.4,class:'g'});
  const ro = [-20,20].map(x => $(qr,'ellipse',{cx:x,cy:-20,rx:18,ry:3,class:'d'})),th = $(qr,'path',{class:'s n sw w3'}); $(qd,'path',{d:'M0 22V66',class:'s n sm w3','stroke-dasharray':'2 6'});
  T(m,g,HX,214,'step','걸음','m','middle'); const ql = T(m,g,435,214,'tilt, then move','기울이고 나서 이동','m','middle');
  gsap.set(qd,{x:435,y:90});
  const ik = (fx,fy,hy) => {const l = Math.hypot(fx,fy) || 1,d = Math.min(l,2 * TH - .5),h = Math.sqrt(TH * TH - d * d / 4),ux = fx / l,uy = fy / l; return `M${HX} ${hy}L${HX + ux * d / 2 + uy * h} ${hy + uy * d / 2 - ux * h}L${HX + ux * d} ${hy + uy * d}`;};
  const o = {P:0,s:0};
  const draw = () => {
   const P = o.P,j = Math.floor(P),u = P - j,s = o.s,hy = GY - 66 + 2.5 * Math.cos(P * TAU) * (1 - s),e = SN(u);
   for (let i = 0; i < 2; i++) {
    let fx,lift = 0; if (i === (j & 1)) {fx = -LL / 2 - u * LL + 2 * LL * e; lift = 16 * Math.sin(Math.PI * u);} else fx = LL / 2 - u * LL;
    fx = L(fx,i ? 8 :-8,s); lift *= 1 - s; A(leg[i],{d:ik(fx,GY - hy - lift,hy)}); A(ft[i],{cx:HX + fx,cy:GY - lift + 1});
    A(arm[i],{d:`M${HX} ${hy - 26}l${(i ? 1 : -1) * Math.sin(P * Math.PI) * 16 * (1 - s) * (j & 1 ? -1 : 1)} 24`});
  }
   A(bd,{transform:`translate(${HX} ${hy})`}); A(tk,{'stroke-dashoffset':P * LL});
   const tn = 34 / Math.cos(gsap.getProperty(qr,'rotation') * Math.PI / 180); A(th,{d:`M0 0V${-tn}M-5 ${-tn + 8}L0 ${-tn}L5 ${-tn + 8}`});
 };
  const tl = m.timeline({repeatDelay:.3}),sw = (x,a,b) => {tl.to(qr,{rotation:a,duration:.7,ease:'power2.out'},x).to([qd,ql],{x:b,duration:2.1,ease:'power2.inOut'},x + .3).to(qr,{rotation:-a,duration:.7,ease:'power2.inOut'},x + 1.5).to(qr,{rotation:0,duration:.7,ease:'back.out(1.7)'},x + 2.2);};
  fin(tl,g,11.8);
  tl.to(o,{P:3.1,duration:3,ease:'none'},.4).to(o,{P:4,duration:1.74,ease:'power2.out'},3.4).to(o,{s:1,duration:1.2,ease:'sine.inOut'},3.6)
   .fromTo(hg,{y:0},{y:2,duration:.18,ease:'power2.out',yoyo:true,repeat:1},4.9)
   .to(qd,{y:93,duration:.9,ease:'sine.inOut',yoyo:true,repeat:11},.4)
   .fromTo(ro,{attr:{rx:18}},{attr:{rx:14},duration:.06,yoyo:true,repeat:200},0);
  sw(4.6,17,'+=70'); sw(8.3,-17,'-=70');
  m.play(tl,{rest:6.2,draw});
});

 // scene-11 grip
 R.gs('scene-11',(el,m) => {
  const g = stage(m,'A light grip slips; a firm grip keeps the force inside the friction cone.','약하게 쥐면 미끄러지고 세게 쥐면 힘이 마찰 원뿔 안에 듭니다.');
  const MU = .5,PHI = Math.atan(MU),CX = 320,TB = 192,BW = 70,HH = 44;
  $(g,'line',{x1:0,y1:TB,x2:640,y2:TB,class:'s st w3'});
  const gr = $(g,'g',{}); RR(gr,-96,-74,192,22,11,'f s st');
  const fl = RR(gr,-116,-62,16,116,8,'f s st'),fr = RR(gr,100,-62,16,116,8,'f s st');
  const bk = $(g,'g',{}); RR(bk,-BW,-HH,2 * BW,2 * HH,8,'c s st');
  const ey = [-19,19].map(x => CC(bk,x,-28,2.6,'g')),cn = [0,1].map(() => $(bk,'polygon',{class:'k'})),ar = [0,1].map(() => $(bk,'path',{class:'s n w4'})),lg = $(g,'g',{});
  $(lg,'polygon',{points:'14,16 54,6 54,26',class:'k',opacity:.4}); T(m,lg,64,26,'friction cone','마찰 원뿔','m');
  gsap.set(gr,{x:CX,y:112}); gsap.set(bk,{x:CX,y:112});
  const o = {fn:0},cls = ['',''],a0 = 28 - MU * 40,a1 = 28 - MU * 84;
  // Integrate 28 - mu*fn per contact from rest at 1.5 s, including both cubic force ramps.
  const STOP = 3.4 - (a0 * 1.9 + MU * 40 * .1 ** 4 / (4 * .3 ** 3) - MU * 44 * .4) / a1;
  const slip = t => {
   const dt = Math.max(0,t - 1.5),r = Math.max(0,.1 - dt),u = Math.max(0,(t - 2.6) / .8),v = Math.max(0,u - .5),w = Math.max(0,u - 1);
   return .5 * a0 * dt * dt + MU * 40 / (4 * .3 ** 3) * (.1 ** 4 * dt - (.1 ** 5 - r ** 5) / 5) - MU * 44 * .8 ** 2 * ((u ** 5 - w ** 5) / 5 - v ** 4);
  },distance = slip(STOP);   // scale the integrated motion to the existing 24 px slip
  const draw = t => {
   const sl = t > 1.5 && t < STOP,ft = sl ? MU * o.fn :28,v = o.fn > 1 ? 1 :0;
   for (let i = 0; i < 2; i++) {
    const sg = i ? -1 :1,x = -sg * BW,c = Math.cos(PHI) * 62 * sg,s = Math.sin(PHI) * 62,k = 's n w4 ' + (sl ? 'sb' :'sk');
    A(cn[i],{points:`${x},0 ${x + c},${-s} ${x + c},${s}`,opacity:.3 * v}); A(ar[i],{d:hd(x,0,sg * o.fn * .6,-ft * .6),opacity:v}); if (cls[i] !== k) A(ar[i],{class:cls[i] = k});
  }
 };
  const tl = m.timeline({repeatDelay:.4});
  fin(tl,g,9.3);
  tl.fromTo(fl,{attr:{x:-116}},{attr:{x:-85},duration:1.2,ease:'power3.out'},.3).fromTo(fr,{attr:{x:100}},{attr:{x:69},duration:1.2,ease:'power3.out'},.3)
   .to(o,{fn:40,duration:.3,ease:'power2.out'},1.3).to(bk,{y:136,duration:STOP - 1.5,ease:p => slip(1.5 + (STOP - 1.5) * p) / distance},1.5)
   .to(o,{fn:84,duration:.8,ease:'power2.inOut'},2.6).to(fl,{attr:{x:-82.5},duration:.8,ease:'power2.inOut'},2.6).to(fr,{attr:{x:66.5},duration:.8,ease:'power2.inOut'},2.6)
   .fromTo(lg,{autoAlpha:0},{autoAlpha:1,duration:.5},1.4)
   .fromTo(ey,{scaleY:1},{scaleY:.1,duration:.07,yoyo:true,repeat:1},2.2).fromTo(ey,{scaleY:1},{scaleY:.1,duration:.07,yoyo:true,repeat:1,immediateRender:false},6)
   .to(gr,{y:82,duration:1.4,ease:'power2.inOut'},4.2).to(bk,{y:106,duration:1.4,ease:'power2.inOut'},4.2)
   .to(gr,{y:112,duration:.8,ease:'power2.inOut'},6.2).to(bk,{y:136,duration:.8,ease:'power2.inOut'},6.2)
   .to(o,{fn:0,duration:.8,ease:'power2.inOut'},7.2).to(fl,{attr:{x:-122.5},duration:.8,ease:'power2.inOut'},7.2).to(fr,{attr:{x:106.5},duration:.8,ease:'power2.inOut'},7.2)
   .to(bk,{y:TB - HH,duration:.8,ease:'bounce.out'},7.6);
  m.play(tl,{rest:5.2,draw});
});
})();
