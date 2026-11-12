// phase 14 concept animations (480x270) as GSAP timelines; needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,cl,hd,fin} = K,T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15),N = (m,p,x,y,s,c,an) => T(m,p,x,y,s,s,c,an);
 const D = (p,x,y,cls,an) => {const e = $(p,'text',{x,y,'font-size':15,class:cls || '','text-anchor':an || 'start'}); let l = ''; return s => {if (s !== l) {l = s; e.textContent = s;}};};
 const stage = (m,en,ko) => {const q = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return q;};

 // lesson 01: greedy picks robot by robot; the optimal assignment is the cheapest of all pairings
 R.gs('greedy-trap',(el,m) => {
  const g = stage(m,'Toy layout, distances in grid units. Greedy lets each robot take the nearest free task in turn. Optimal is the cheapest of all pairings.','토이 배치이고 거리는 격자 단위입니다. greedy는 로봇이 차례로 가장 가까운 일을 집고 optimal은 모든 짝짓기 중 가장 쌉니다.');
  const rb = [[120,196],[220,196],[320,196]],tk = [[60,86],[170,86],[270,86]],d = (i,j) => Math.hypot(rb[i][0] - tk[j][0],rb[i][1] - tk[j][1]) / 10;
  const free = [0,1,2],gr = rb.map((_,i) => {const j = free.reduce((a,b) => d(i,b) < d(i,a) ? b :a); free.splice(free.indexOf(j),1); return j;});
  const cost = p => p.reduce((s,j,i) => s + d(i,j),0),op = [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]].reduce((a,b) => cost(b) < cost(a) ? b :a);
  const grow = (l,i,j,p) => A(l,{x2:rb[i][0] + (tk[j][0] - rb[i][0]) * p,y2:rb[i][1] + (tk[j][1] - rb[i][1]) * p});
  const ln = (c,i,j,p) => {const l = $(g,'line',{x1:rb[i][0],y1:rb[i][1],class:'s ' + c}); grow(l,i,j,p || 0); return l;};
  const all = [0,1,2].flatMap(i => [0,1,2].map(j => ln('sm',i,j,1))),gl = rb.map((_,i) => ln('sw w3',i,gr[i])),ol = rb.map((_,i) => ln('sk w4',i,op[i]));
  tk.forEach((c,j) => {RR(g,c[0] - 14,c[1] - 14,28,28,6,'c s sl'); N(m,g,c[0],c[1] + 5,'ABC'[j],'g','middle');});
  rb.forEach((c,i) => {CC(g,c[0],c[1],14,'f'); N(m,g,c[0],c[1] + 5,'' + (i + 1),'b','middle');});
  const h = D(g,16,26,'g'),r1 = D(g,16,262,'x'),r2 = D(g,464,262,'k','end'),o = {g:0,gv:1,a:0,p:0};
  const draw = t => {
   const pg = i => cl(o.g - i),tg = gr.reduce((s,j,i) => s + d(i,j) * pg(i),0);
   gl.forEach((l,i) => {grow(l,i,gr[i],pg(i)); A(l,{opacity:o.gv});}); ol.forEach((l,i) => grow(l,i,op[i],o.p)); all.forEach(l => A(l,{opacity:o.a * .5}));
   h(t < 5.4 ? m.t('Greedy: nearest free task, in turn','greedy: 차례로 가장 가까운 일을 집습니다') :t < 7 ? m.t('Optimal: all pairs at once','optimal: 모든 쌍을 한꺼번에 봅니다') :m.t('Optimal: the smallest total','optimal: 합이 가장 작습니다'));
   r1(tg > 0 ? 'greedy ' + tg.toFixed(1) :''); r2(o.p > 0 ? 'optimal ' + (cost(op) * o.p).toFixed(1) :'');
  };
  const tl = m.timeline({repeatDelay:.4});
  fin(tl,g,11.6);
  tl.to(o,{g:3,duration:4.2,ease:'none'},.8).to(o,{gv:.25,a:1,duration:.6},5.4).to(o,{a:0,duration:.5},7).to(o,{p:1,duration:2.4,ease:'none'},7.2);
  m.play(tl,{rest:10.2,draw});
 });

 // lesson 03: one cell at a time ends in a wait-for loop; reserving the whole route lets disjoint routes run together
 R.gs('deadlock-ring',(el,m) => {
  const g = stage(m,'Each robot needs its own cell and the next. One cell at a time ends in a wait-for loop. Reserving the whole route lets robots 1 and 3 go, then 2 and 4.','로봇마다 자기 칸과 다음 칸이 필요합니다. 한 칸씩 가면 서로 기다리는 고리에 갇히고 경로를 통째로 예약하면 1, 3번이 먼저 가고 2, 4번이 뒤따릅니다.');
  const C = [[170,105],[310,105],[310,195],[170,195]],S = [[110,58],[370,58],[370,236],[110,236]],o = {v:1,w:0};
  for (let i = 0; i < 4; i++) Object.assign(o,{['p' + i]:0,['r' + i]:0});
  C.forEach(c => RR(g,c[0] - 22,c[1] - 22,44,44,8,'c s sm'));
  const hl = C.map(c => RR(g,c[0] - 22,c[1] - 22,44,44,8,'n s sk w4',{opacity:0})),wg = $(g,'g',{});
  C.forEach((c,i) => {const n = C[(i + 1) % 4],dx = n[0] - c[0],dy = n[1] - c[1],l = Math.hypot(dx,dy),ux = dx / l,uy = dy / l; $(wg,'path',{d:hd(c[0] + ux * 28,c[1] + uy * 28,dx - ux * 56,dy - uy * 56),class:'n s sb w3'});});
  const rb = S.map((s,i) => {const q = $(g,'g',{}); return {q,c:CC(q,0,0,13,'f'),t:N(m,q,0,5,'' + (i + 1),'b','middle')};});
  const at = (i,p) => {const a = S[i],b = C[i],c = C[(i + 1) % 4],u = Math.min(p,1),v = cl(p - 1); return p <= 1 ? [a[0] + (b[0] - a[0]) * u,a[1] + (b[1] - a[1]) * u] :[b[0] + (c[0] - b[0]) * v,b[1] + (c[1] - b[1]) * v];};
  const h = D(g,16,26,'g'),dn = D(g,16,262,'m');
  const draw = t => {
   let n = 0;
   rb.forEach((r,i) => {const p = o['p' + i],xy = at(i,p); n += p >= 2; A(r.q,{transform:`translate(${xy[0]} ${xy[1]})`,opacity:p >= 2 ? 0 :o.v}); A(r.c,{class:o.w > .5 ? 'x' :'f'});});
   hl.forEach((q,k) => A(q,{opacity:o['r' + k] > .5 || o['r' + (k + 3) % 4] > .5 ? 1 :0})); A(wg,{opacity:o.w});
   h(t < 2 ? m.t('Enter the next cell if it is free','다음 칸이 비면 들어갑니다') :t < 4.6 ? m.t('A wait-for loop: nobody moves','서로 기다리는 고리: 아무도 못 갑니다') :t < 7.8 ? m.t('Reserve the whole route, or wait','경로를 통째로 예약하거나 기다립니다') :m.t('The rest follow; nobody waits','나머지가 이어서 가고 기다리는 로봇이 없습니다'));
   dn(m.t('passed ','통과 ') + n + ' / 4');
  };
  const tl = m.timeline({repeatDelay:.4});
  fin(tl,g,10.7);
  tl.to(o,{p0:1,p1:1,p2:1,p3:1,duration:1.2},.6).to(o,{w:1,duration:.5},2).to(o,{v:0,w:0,duration:.4},4.2).set(o,{p0:0,p1:0,p2:0,p3:0},4.6).to(o,{v:1,duration:.4},4.7)
   .set(o,{r0:1,r2:1},5.3).to(o,{p0:2,p2:2,duration:2,ease:'none'},5.6).set(o,{r0:0,r2:0,r1:1,r3:1},7.7).to(o,{p1:2,p3:2,duration:2,ease:'none'},8).set(o,{r1:0,r3:0},10.1);
  m.play(tl,{rest:3.6,draw});
 });
})();
