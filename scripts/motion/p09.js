// phase 09 concept animations (480x270): rrt-shortcut, tunnel-check, path-relax; needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,cl,hd,fin} = K,DA = 'stroke-dasharray',DO = 'stroke-dashoffset';
 const T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 const D = (p,x,y,cls,an,sz) => {const e = $(p,'text',{x,y,'font-size':sz || 15,class:cls || '','text-anchor':an || 'start'}); let l = ''; const f = s => {if (s !== l) {l = s; e.textContent = s;}}; f.e = e; return f;};
 const stage = (m,en,ko) => {const q = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return q;};
 const dst = (a,b) => Math.hypot(a[0] - b[0],a[1] - b[1]);

 // 09/02: shortcutting the first RRT path (the lesson's seed-0 path and obstacles): pick two nodes, keep the straight link if it is free
 R.gs('rrt-shortcut',(el,m) => {
  const g = stage(m,'Path shortcutting. Pick two nodes at random. If the straight segment between them is free (closest point to each circle), drop every node in between. 200 tries, first 8 shown, later ones sped up.','경로 shortcutting입니다. 노드 두 개를 무작위로 고르고 둘을 잇는 직선이 비어 있으면(각 원까지 가장 가까운 점 기준) 사이의 노드를 모두 버립니다. 200번 시도하며 처음 8번만 천천히 보여 줍니다.');
  const Q = [],S = '1,1,1.38,.87,1.65,1.16,1.99,1.38,2.14,1.75,2.03,2.13,2.31,2.41,2.28,2.81,2.46,3.16,2.76,3.43,3.07,3.67,3.12,4.07,2.97,4.44,2.64,4.66,2.43,5,2.41,5.4,2.13,5.68,2.16,6.08,1.91,6.39,1.51,6.44,1.57,6.83,1.6,7.23,1.53,7.63,1.81,7.91,1.83,8.31,1.9,8.71,2.29,8.79,2.69,8.74,3.09,8.71,3.49,8.73,3.89,8.75,4.27,8.62,4.67,8.65,4.87,8.3,5.22,8.12,5.61,8.21,5.89,7.92,6.28,8,6.66,8.14,7.03,8.28,7.32,8,7.66,8.2,8,8.41,8.35,8.61,8.69,8.82,9,9'.split(',').map(Number);
  for (let i = 0; i < S.length; i += 2) Q.push([S[i],S[i + 1]]);
  const OB = [[5,5,2],[3,7.5,1.2],[7.5,3,1.2]],len = p => p.slice(1).reduce((s,q,i) => s + dst(Q[q],Q[p[i]]),0);
  const free = (a,b) => OB.every(c => {const dx = b[0] - a[0],dy = b[1] - a[1],L2 = dx * dx + dy * dy,t = cl(((c[0] - a[0]) * dx + (c[1] - a[1]) * dy) / L2);
   return Math.hypot(a[0] + t * dx - c[0],a[1] + t * dy - c[1]) > c[2];});
  let sd = 6; const rnd = () => (sd = (sd * 9301 + 49297) % 233280) / 233280;
  const st = [Q.map((_,i) => i)],tr = [];            // st[k]: node indices kept before try k
  for (let k = 0; k < 200; k++) {
   const p = st[k],n = p.length; let i = Math.floor(rnd() * n),j = Math.floor(rnd() * (n - 1)); if (j >= i) j++; if (i > j) [i,j] = [j,i];
   const ok = n > 2 && j - i > 1 && free(Q[p[i]],Q[p[j]]); tr.push({a:Q[p[i]],b:Q[p[j]],ok}); st.push(ok ? p.slice(0,i + 1).concat(p.slice(j)) :p);
  }
  const sx = x => 16 + x * 25,sy = y => 258 - y * 25,pl = p => 'M' + p.map(i => sx(Q[i][0]) + ' ' + sy(Q[i][1])).join('L');
  OB.forEach(c => CC(g,sx(c[0]),sy(c[1]),c[2] * 25,'f s st',{opacity:.35}));
  $(g,'path',{d:pl([0,Q.length - 1]),class:'s n sm',[DA]:'3 6'}); CC(g,sx(1),sy(1),6,'k'); CC(g,sx(9),sy(9),6,'x');
  const path = $(g,'path',{class:'s n st w3'}),cand = $(g,'line',{class:'s w3'}),nd = Q.map(q => CC(g,sx(q[0]),sy(q[1]),2.5,'g'));
  const r1 = D(g,296,60,'g'),r2 = D(g,296,84,'g'),r3 = D(g,296,108,'g'); T(m,g,296,150,'straight line (blocked)','직선(막힘)','m'); const r4 = D(g,296,172,'m');
  const draw = t => {
   let k = 0,c = null;
   if (t >= 1.6) {const kf = (t - 1.6) / .9; if (kf < 8) {k = Math.floor(kf); const ph = kf - k; if (ph > .15) c = tr[k]; if (ph >= .55 && tr[k].ok) k++; k = Math.min(k,200); if (c) c = {...c,cls:ph < .3 ? 'sm' :tr[Math.floor(kf)].ok ? 'sk' :'sb'};}
    else k = 8 + Math.floor(cl((t - 8.8) / 2.2) * 192);}
   const p = st[k],on = new Set(p);
   A(path,{d:pl(p)}); nd.forEach((e,i) => A(e,{opacity:on.has(i) ? 1 :.15}));
   A(cand,{opacity:c ? 1 :0}); if (c) A(cand,{x1:sx(c.a[0]),y1:sy(c.a[1]),x2:sx(c.b[0]),y2:sy(c.b[1]),class:'s w3 ' + c.cls});
   r1(m.t(`path length ${len(p).toFixed(2)} m`,`경로 길이 ${len(p).toFixed(2)} m`)); r2(m.t(`nodes kept ${p.length} of ${Q.length}`,`남은 노드 ${p.length} / ${Q.length}`)); r3(m.t(`tries ${Math.min(k,200)} / 200`,`시도 ${Math.min(k,200)} / 200`));
   r4(dst(Q[0],Q[Q.length - 1]).toFixed(2) + ' m');
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,12.8); m.play(tl,{rest:12,draw});
 });

 // 09/03: a swept check tests samples spaced at most s apart; the post (r = 0.1 m at x = 5.4 m) sits on a 10 m segment
 R.gs('tunnel-check',(el,m) => {
  const g = stage(m,'Swept collision check on a 10 m segment with a post of radius 0.1 m at x = 5.4 m. A step of 1.0 m or 0.4 m skips it, a step of at most 2r = 0.2 m puts a sample on it, and padding by s/2 catches it for any step.','10 m 선분 위 x = 5.4 m에 반지름 0.1 m인 말뚝이 있는 swept 충돌 검사입니다. 간격 1.0 m와 0.4 m는 말뚝을 건너뛰고 2r = 0.2 m 이하면 샘플이 말뚝에 닿으며 s/2만큼 부풀리면 어떤 간격이든 잡습니다.');
  const CX = 5.4,RD = .1,PX = 180,YL = 140,sx = x => 20 + (x - 4.2) * PX,ACT = [[1,0],[.4,0],[.2,0],[.4,.2]];
  const MS = [['Samples fall on both sides of the post.','샘플이 말뚝 양쪽에 떨어집니다.'],['A smaller step still skips it.','간격을 줄여도 건너뜁니다.'],['Step 2r: a sample lands on the post.','간격 2r이면 샘플이 말뚝에 떨어집니다.'],['Pad the post by s/2: every crossing is caught.','말뚝을 s/2 부풀리면 교차를 모두 잡습니다.']];
  $(g,'line',{x1:0,y1:YL,x2:480,y2:YL,class:'s sm w3'});
  const halo = CC(g,sx(CX),YL,0,'n s sw',{[DA]:'4 4'}),post = CC(g,sx(CX),YL,RD * PX,'w s st'),dots = Array.from({length:14},() => CC(g,0,YL,6,'k s st'));
  const mv = CC(g,0,YL - 22,7,'t'),h1 = D(g,16,26,'g'),h2 = D(g,16,50,'m'),v1 = D(g,16,206,'g'),v2 = D(g,16,230,'g'); T(m,g,16,262,'zoom: x = 4.2 to 6.6 m','확대: x = 4.2 ~ 6.6 m','m');
  const draw = t => {
   const a = cl(Math.floor((t - .3) / 3),0,3),u = cl(t - .3 - 3 * a,0,3),s = ACT[a][0],pad = ACT[a][1],n = Math.ceil(10 / s);
   const xs = Array.from({length:n + 1},(_,i) => 10 * i / n),hit = xs.some(x => Math.abs(x - CX) <= RD + pad),vis = xs.filter(x => x >= 4.2 && x <= 6.6);
   h1(m.t(`step s = ${s} m` + (pad ? `, pad s/2 = ${pad} m` :''),`간격 s = ${s} m` + (pad ? `, 패딩 s/2 = ${pad} m` :''))); h2(m.t(MS[a][0],MS[a][1]));
   A(halo,{r:pad ? (RD + pad) * PX :0});
   dots.forEach((e,i) => {const x = vis[i],on = x !== undefined && u > .3 + i * .9 / vis.length,bad = x !== undefined && Math.abs(x - CX) <= RD + pad;
    A(e,{cx:x === undefined ? 0 :sx(x),opacity:on ? 1 :0,class:(bad ? 'x s sb' :'k s st')});});
   const xm = 4.2 + cl((u - 1.7) / .8) * 2.4,touch = u > 1.7 && Math.abs(xm - CX) <= RD;
   A(mv,{cx:sx(xm),opacity:u >= 1.7 ? 1 :0}); A(post,{class:touch ? 'x s sb' :'w s st'});
   v1(u >= 1.4 ? m.t(`checker: ${hit ? 'blocked' :'free'}`,`검사 결과: ${hit ? '충돌' :'통과'}`) :''); A(v1.e,{class:hit ? 'k' :'x'});
   v2(u >= 2.5 ? m.t('real path: touches the post','실제 경로: 말뚝에 닿음') :'');
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,12.2); m.play(tl,{rest:8.9,draw});
 });

 // 09/04: gradient descent on smoothness + obstacle penalty (code/main.py: ws 1, wo 8, margin 0.4, lr 0.04, 22 waypoints)
 R.gs('path-relax',(el,m) => {
  const g = stage(m,'One waypoint in a tug of war: smoothness pulls it toward its neighbours, the obstacle penalty pushes it out, and the path settles where they balance. With a step 7.5x too large (0.3) the cost first goes up instead.','waypoint 하나의 줄다리기입니다. 부드러움은 이웃 쪽으로 당기고 장애물 penalty는 밖으로 밀며 둘이 균형을 이루는 곳에서 경로가 멈춥니다. 스텝이 7.5배 크면(0.3) 비용이 먼저 오히려 올라갑니다.');
  const OB = [[3.5,.3,1],[7,-.5,1]],N = 22,WI = 7,WO = 8,MG = .4;
  const X0 = Array.from({length:N},(_,i) => [10 * i / (N - 1),0]);
  const cost = X => {let s = 0; for (let i = 1; i < N; i++) s += .5 * dst(X[i],X[i - 1]) ** 2;
   OB.forEach(c => {for (let i = 1; i < N - 1; i++) s += WO * Math.max(0,c[2] + MG - dst(X[i],c)) ** 2;}); return s;};
  const grad = (X,i) => {const gs = [0,1].map(k => 2 * X[i][k] - X[i - 1][k] - X[i + 1][k]),go = [0,0];   // smoothness and obstacle parts at waypoint i
   OB.forEach(c => {const d = Math.max(dst(X[i],c),1e-9),f = 2 * WO * Math.max(0,c[2] + MG - d); go[0] -= f * (X[i][0] - c[0]) / d; go[1] -= f * (X[i][1] - c[1]) / d;}); return [gs,go];};
  const snaps = (lr,its) => {let X = X0.map(p => p.slice()); const out = []; for (let n = 0; n <= its[its.length - 1]; n++) {
    if (its.includes(n)) out.push({n,X:X.map(p => p.slice())});
    const G = X.map((_,i) => i && i < N - 1 ? grad(X,i) :null); X = X.map((p,i) => G[i] ? [p[0] - lr * (G[i][0][0] + G[i][1][0]),p[1] - lr * (G[i][0][1] + G[i][1][1])] :p);} return out;};
  const S1 = snaps(.04,Array.from({length:40},(_,j) => j ? Math.round(4000 ** ((j - 1) / 38)) :0)),S2 = snaps(.3,Array.from({length:13},(_,j) => j));
  const sx = x => 20 + x * 44,sy = y => 150 - y * 44;
  OB.forEach(c => {CC(g,sx(c[0]),sy(c[1]),c[2] * 44,'f s st',{opacity:.35}); CC(g,sx(c[0]),sy(c[1]),(c[2] + MG) * 44,'n s sm',{[DA]:'3 5'});});
  const path = $(g,'path',{class:'s n st w3'}),pull = $(g,'path',{class:'s n sf w4'}),push = $(g,'path',{class:'s n sb w4'}),wp = CC(g,0,0,6,'g');
  CC(g,sx(0),sy(0),5,'k'); CC(g,sx(10),sy(0),5,'x');
  const h1 = D(g,16,22,'g'),h2 = D(g,16,44,'m'),l1 = D(g,36,236,'g'),l2 = D(g,36,258,'g');
  $(g,'path',{d:'M12 232h16',class:'s n sf w4'}); $(g,'path',{d:'M12 254h16',class:'s n sb w4'});
  const arrow = (e,x,y,v) => {const l = Math.hypot(v[0],v[1]),s = Math.min(80,4 * l) / (l || 1); A(e,{d:hd(sx(x),sy(y),v[0] * s,-v[1] * s),opacity:l > .05 ? 1 :0});};
  const draw = t => {
   const two = t >= 6.8,S = two ? S2 :S1,p = two ? cl((t - 7.4) / 3) * (S.length - 1) :cl((t - .6) / 5.2) * (S.length - 1),a = Math.min(S.length - 2,Math.floor(p)),f = p - a;
   const X = S[a].X.map((q,i) => [q[0] + (S[a + 1].X[i][0] - q[0]) * f,q[1] + (S[a + 1].X[i][1] - q[1]) * f]),G = grad(X,WI),c = cost(X);
   A(path,{d:'M' + X.map(q => sx(q[0]).toFixed(1) + ' ' + sy(q[1]).toFixed(1)).join('L')}); A(wp,{cx:sx(X[WI][0]),cy:sy(X[WI][1])});
   arrow(pull,X[WI][0],X[WI][1],[-G[0][0],-G[0][1]]); arrow(push,X[WI][0],X[WI][1],[-G[1][0],-G[1][1]]);
   h1(two ? m.t('Step 0.3 instead of 0.04: the cost jumps up.','스텝 0.04 대신 0.3: 비용이 먼저 튀어 오릅니다.') :m.t('Pull and push balance: the path settles.','당김과 밂이 균형을 이루면 경로가 멈춥니다.'));
   const it = Math.round(S[a].n + (S[a + 1].n - S[a].n) * f); h2(m.t(`iteration ${it} · cost ${c.toFixed(1)}`,`반복 ${it} · 비용 ${c.toFixed(1)}`));
   l1(m.t(`pull (smoothness) ${Math.hypot(...G[0]).toFixed(1)}`,`당김(부드러움) ${Math.hypot(...G[0]).toFixed(1)}`)); l2(m.t(`push (obstacle) ${Math.hypot(...G[1]).toFixed(1)}`,`밂(장애물) ${Math.hypot(...G[1]).toFixed(1)}`));
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,11.8); m.play(tl,{rest:6.4,draw});
 });

 // 09/05: the lesson's trap map (17 x 11), 4-connected unit cost, priority g + w * manhattan, heap ties as in search(): w = 1 and w = 4 side by side
 R.gs('astar-weight',(el,m) => {
  const g = stage(m,'The same search on the lesson trap map, with heuristic weight 1 and weight 4. Weight 1 is A*: it goes round the bottom and the path costs 26. Weight 4 over-promises, dives into the near gap in the top wall, then pays a long way back down: 36, within 4 times 26.','레슨의 함정 지도에서 휴리스틱 가중치 1과 4로 같은 탐색을 돌립니다. 가중치 1은 A*로 아래쪽을 돌아가 경로 비용 26입니다. 가중치 4는 과하게 낙관해서 위쪽 벽의 가까운 틈으로 뛰어들고 긴 길을 되돌아 내려와 36을 냅니다(26의 4배 이내).');
  const MAP = ['...........#.....','.....#.....#.....','.....#.....#.....','.....#.....#.....','.....#.....#.....','S....#.....#....G','.....#.....#.....','.....#.....#.....','.....#.....#.....','.....#.....#.....','.................'],NR = 11,NC = 17,S = [5,0],G = [5,16];
  const wall = (r,c) => MAP[r][c] === '#',mh = (a,b) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
  const search = w => {const gc = {'5,0':0},par = {},cl3 = new Set(),ex = []; let hp = [[w * mh(S,G),0,S]];
   while (hp.length) {let bi = 0; hp.forEach((h,i) => {const b = hp[bi]; if (h[0] < b[0] || h[0] === b[0] && (h[1] < b[1] || h[1] === b[1] && (h[2][0] < b[2][0] || h[2][0] === b[2][0] && h[2][1] < b[2][1]))) bi = i;});
    const [,,c] = hp.splice(bi,1)[0],k = c + ''; if (cl3.has(k)) continue; cl3.add(k); ex.push(c);
    if (c[0] === G[0] && c[1] === G[1]) {const pa = []; for (let q = k; q; q = par[q]) pa.push(q.split(',').map(Number)); return {ex,path:pa.reverse()};}
    [[1,0],[-1,0],[0,1],[0,-1]].forEach(d => {const n = [c[0] + d[0],c[1] + d[1]],nk = n + ''; if (n[0] >= 0 && n[0] < NR && n[1] >= 0 && n[1] < NC && !wall(n[0],n[1]) && gc[k] + 1 < (gc[nk] === undefined ? 1e9 :gc[nk])) {gc[nk] = gc[k] + 1; par[nk] = k; hp.push([gc[nk] + w * mh(n,G),-gc[nk],n]);}});}
   return {ex,path:[]};};
  const W = [1,4],RS = W.map(search),CS = 13;
  const pan = RS.map((r,i) => {const ox = 8 + i * 236,oy = 54;
   for (let a = 0; a < NR; a++) for (let b = 0; b < NC; b++) if (wall(a,b)) RR(g,ox + b * CS,oy + a * CS,CS,CS,0,'g');
   const cells = r.ex.map(c => RR(g,ox + c[1] * CS + 1,oy + c[0] * CS + 1,CS - 2,CS - 2,2,'l',{opacity:0})),pa = $(g,'path',{class:'s n sw w4',d:'M' + r.path.map(c => (ox + c[1] * CS + CS / 2) + ' ' + (oy + c[0] * CS + CS / 2)).join('L'),pathLength:1,[DA]:'1 1'});
   CC(g,ox + CS / 2,oy + 5 * CS + CS / 2,5,'k'); CC(g,ox + 16 * CS + CS / 2,oy + 5 * CS + CS / 2,5,'x');
   return {cells,pa,a:D(g,ox,28,'g'),b:D(g,ox,222,'g'),c:D(g,ox,246,'m')};});
  const draw = t => {
   RS.forEach((r,i) => {const P = pan[i],n = r.ex.length,k = Math.min(n,Math.round(cl((t - .8) / 6.2) * n)),pf = cl((t - 7.4) / 1.2);
    P.cells.forEach((e,j) => A(e,{opacity:j < k ? 1 :0})); A(P.pa,{[DO]:1 - pf,opacity:pf > 0 ? 1 :0});
    P.a(m.t(`weight ${W[i]}` + (i ? ' (over-estimates)' :' (A*)'),`가중치 ${W[i]}` + (i ? ' (과대추정)' :' (A*)')));
    P.b(m.t(`cells expanded ${k}`,`확장한 칸 ${k}`)); P.c(pf >= 1 ? m.t(`path cost ${r.path.length - 1}`,`경로 비용 ${r.path.length - 1}`) :'');});
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,12.6); m.play(tl,{rest:11,draw});
 });
})();
