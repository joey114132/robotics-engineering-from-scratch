// phase 06 concept loops (480x270) as GSAP timelines on the MB kit from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,hd,fin} = K,T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 // D: a text node you set from draw(); .e is the node for tweens
 const D = (p,x,y,cls,an) => {const e = $(p,'text',{x,y,'font-size':15,class:cls || '','text-anchor':an || 'start'}); let l = ''; const f = s => {if (s !== l) {l = s; e.textContent = s;}}; f.e = e; return f;};
 const stage = (m,en,ko) => {const q = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return q;};
 const rng = s => () => (s = (s * 9301 + 49297) % 233280) / 233280;

 R.gs('calib-views',(el,m) => {
  const g = stage(m,'Lesson run, 0.5 px noise, tilted views added one by one. Pixel error falls from 3.88 px (2 views) to 2.24 px (6), with a bump at 5. Brackets: true values.','레슨 실행(잡음 0.5 px)에 기울인 view를 하나씩 더합니다. 픽셀 오차는 2장의 3.88 px에서 6장의 2.24 px로 줄고 5장에서 한 번 튑니다. 괄호는 참값입니다.');
  // estimates [fx, fy, cx, cy, pixel error] from the first 2..6 views of make_views(K, 6, 0.5, 1)
  const E = [[614.3,575.1,333.2,233.2,3.88],[614.7,575.9,332.0,233.1,2.95],[616.0,577.0,331.8,233.7,2.39],[616.2,577.1,331.9,233.3,2.64],[617.8,578.2,332.0,234.0,2.24]],TR = [620,580,330,235],NM = ['fx','fy','cx','cy'];
  const Q = [[4,3,-6,0,-6,0,4,-3],[0,6,-4,-2,-6,2,6,-2],[6,0,0,5,-4,-5,2,0],[-4,-3,2,6,4,-6,0,3],[2,-5,-6,4,0,3,8,-5]];
  const grid = V => {   // a 7x5 grid seen from a tilted view: bilinear map of the unit square onto a quad
   const c = [[0,0],[60,0],[60,44],[0,44]].map((p,i) => [p[0] + V[2 * i],p[1] + V[2 * i + 1]]),P = (u,v) => [0,1].map(a => (1 - v) * ((1 - u) * c[0][a] + u * c[1][a]) + v * ((1 - u) * c[3][a] + u * c[2][a]));
   let d = ''; for (let j = 0; j <= 4; j++) d += `M${P(0,j / 4)}L${P(1,j / 4)}`; for (let i = 0; i <= 6; i++) d += `M${P(i / 6,0)}L${P(i / 6,1)}`;
   return d;
  };
  const th = Q.map((V,i) => $(g,'path',{d:grid(V),transform:`translate(${24 + i * 90} 34)`,class:'n st'}));
  const ys = [118,146,174,202],dots = NM.map((n,j) => {
   T(m,g,16,ys[j] + 5,n,n,'g'); $(g,'path',{d:`M100 ${ys[j]}H340`,class:'s n sm'}); $(g,'path',{d:`M220 ${ys[j] - 9}V${ys[j] + 9}`,class:'s n sk w3'});
   return [CC(g,220,ys[j],6,'t'),D(g,350,ys[j] + 5,'g')];
  });
  T(m,g,16,241,'error','오차','g'); const bar = RR(g,100,229,0,14,3,'w'),ev = D(g,350,241,'g'),hl = D(g,16,22,'g'),o = {v:0};
  const draw = () => {
   const ri = Math.round(o.v),a = Math.min(3,Math.floor(o.v)),u = o.v - a,e = E[a].map((x,j) => x + (E[a + 1] ? (E[a + 1][j] - x) * u :0));
   dots.forEach(([c,t],j) => {A(c,{cx:220 + Math.max(-8,Math.min(8,e[j] - TR[j])) * 15}); t(`${E[ri][j].toFixed(1)} (${TR[j]})`);});
   A(bar,{width:e[4] * 60}); ev(E[ri][4].toFixed(2) + ' px'); hl(`${ri + 2}${m.t(' views','장')}`);
   th.forEach((p,i) => A(p,{opacity:i < 2 ? 1 :Math.max(.05,Math.min(1,o.v - i + 2))}));
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.8);
  tl.set(o,{v:0},0); [1,2,3,4].forEach(i => tl.fromTo(o,{v:i - 1},{v:i,duration:.8,ease:'power2.inOut'},1.2 + i * 1.8));
  m.play(tl,{rest:9.8,draw});
 });

 R.gs('ransac-rounds',(el,m) => {
  const g = stage(m,'Side view of a depth cloud. Least squares leans toward the box. Each RANSAC round fits a plane to 3 random points and counts the points near it. The best plane is refit on its inliers.','깊이 점군의 옆면입니다. 최소제곱은 상자 쪽으로 기웁니다. RANSAC은 매 round 무작위 점 3개로 평면을 만들어 가까운 점을 세고 가장 좋은 평면을 inlier로 다시 맞춥니다.');
  const r = rng(11),tab = x => 175 - .1 * (x - 20),P = [],RN = 8,pt = (n,f) => {for (let i = 0; i < n; i++) P.push(f(r()));};
  pt(60,u => {const x = 20 + 420 * u; return [x,tab(x) + (r() - .5) * 8];}); pt(22,u => {const x = 170 + 90 * u; return [x,tab(x) - 38 + (r() - .5) * 8];}); pt(10,u => [20 + 420 * u,60 + 130 * r()]);
  const sum = (S,f) => S.reduce((s,p) => s + f(p),0),fit = S => {   // least-squares line y = a + b x
   const n = S.length,mx = sum(S,p => p[0]) / n,my = sum(S,p => p[1]) / n,b = sum(S,p => (p[0] - mx) * (p[1] - my)) / sum(S,p => (p[0] - mx) ** 2);
   return [my - b * mx,b];
  },near = ([a,b]) => P.map(p => Math.abs(p[1] - a - b * p[0]) / Math.hypot(1,b) < 6),ls = fit(P),rounds = [],bst = [];   // bst[k]: best round among the first k + 1
  for (let k = 0; k < RN; k++) {
   const pk = []; while (pk.length < 3) {const i = Math.floor(r() * P.length); if (!pk.includes(i)) pk.push(i);}
   const l = fit(pk.map(i => P[i])),inl = near(l); rounds.push({pk,l,inl,n:inl.filter(Boolean).length}); bst.push(rounds.reduce((b,q,i) => q.n > rounds[b].n ? i :b,0));
  }
  const fl = fit(P.filter((p,i) => rounds[bst[RN - 1]].inl[i])),fv = near(fl);
  const clip = $(g,'clipPath',{id:'rc-clip'}),ln = c => $(g,'path',{class:'s n ' + c,'clip-path':'url(#rc-clip)'}),dots = P.map(p => CC(g,p[0],p[1],3,'m')),bl = ln('sk w4'),cl = ln('st'),ll = ln('sw w3');
  RR(clip,16,40,448,180,0,'n'); A(ll,{d:`M20 ${ls[0] + ls[1] * 20}L460 ${ls[0] + ls[1] * 460}`});
  const line = (e,l) => A(e,{d:`M20 ${l[0] + l[1] * 20}L460 ${l[0] + l[1] * 460}`});
  $(g,'path',{d:'M16 22h24',class:'s n sw w3'}); T(m,g,46,28,'least squares','최소제곱','m'); $(g,'path',{d:'M180 22h24',class:'s n sk w4'}); T(m,g,210,28,'RANSAC','RANSAC','m');
  const r1 = D(g,16,236,'g'),r2 = D(g,16,258,'m'),o = {r:0};
  const draw = () => {
   const done = o.r >= RN,k = Math.min(RN - 1,Math.floor(o.r)),f = o.r - k,q = rounds[k],b = done ? RN :k + (f > .7 ? 1 :0),B = rounds[bst[Math.max(0,b - 1)]];
   dots.forEach((d,i) => A(d,{r:!done && f > .05 && q.pk.includes(i) ? 5 :3,class:done ? (fv[i] ? 'k' :'m') :(f > .7 && q.inl[i] ? 'k' :q.pk.includes(i) && f > .05 ? 't' :'m')}));
   A(cl,{opacity:!done && f > .3 ? 1 :0}); line(cl,q.l); A(bl,{opacity:b ? 1 :0}); line(bl,done ? fl :B.l);
   r1(done ? m.t('Refit on the best plane\'s inliers','가장 좋은 평면의 inlier로 다시 맞춤') :`${m.t('round ','round ')}${k + 1} / ${RN}   ${m.t('points near this plane: ','이 평면에 가까운 점: ')}${f > .7 ? q.n :'…'}`);
   r2(`${m.t('best so far: ','지금까지 최고: ')}${b ? B.n :0} / ${P.length}`);
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,12.6);
  tl.fromTo(o,{r:0},{r:RN,duration:8.8,ease:'none'},1.2);
  m.play(tl,{rest:11.6,draw});
 });

 R.gs('handeye-spread',(el,m) => {
  const g = stage(m,'Hand-eye solve, 12 motions, 0.2 degrees and 1 mm of noise, as the rotation axes spread around z. One axis: 135.76 degrees of rotation error. 60 degrees of spread: 0.33. The dashed frame is turned by that error.','hand-eye 해입니다(motion 12개, 잡음 0.2도와 1 mm). 회전축이 z 둘레로 퍼집니다. 축 하나면 회전 오차가 135.76도이고 60도로 퍼지면 0.33도입니다. 점선 frame이 그만큼 돌아가 있습니다.');
  const S = [0,2,5,15,60],ER = [135.76,9.36,3.78,1.26,0.33],MM = [121.1,74.6,18.4,4.9,1.3],r = rng(5),AX = Array.from({length:12},() => [r(),r() * 6.2832]),CX = 350,CY = 125,so = `${CX} ${CY}`;
  T(m,g,16,22,'rotation axes of the 12 motions','motion 12개의 회전축','g'); $(g,'path',{d:'M120 200V70',class:'s n sm','stroke-dasharray':'3 6'}); T(m,g,126,78,'z','z','m');
  const fan = $(g,'path',{class:'s n sl'}); CC(g,CX,CY,62,'n s sm',{});
  const frame = c => {const q = $(g,'g',{}); $(q,'path',{d:hd(CX,CY,50,0) + hd(CX,CY,0,-50),class:'s n w3 ' + c}); return q;};
  frame('sf'); const gh = frame('sw'); gh.firstChild.setAttribute('stroke-dasharray','5 4');
  $(g,'path',{d:'M242 212h22',class:'s n sf w3'}); T(m,g,270,217,'true','참값','m'); $(g,'path',{d:'M330 212h22','stroke-dasharray':'5 4',class:'s n sw w3'}); T(m,g,358,217,'solved','추정','m');
  const r1 = D(g,16,240,'g'),r2 = D(g,16,260,'g'),o = {k:0,s:0};
  const draw = () => {
   let d = ''; AX.forEach(([u,ph]) => {const p = o.s * u * Math.PI / 180; d += `M120 200L${120 + 115 * Math.sin(p) * Math.cos(ph)} ${200 - 115 * Math.cos(p)}`;}); A(fan,{d});
   r1(`${m.t('axes within ','축이 z에서 ')}${S[o.k]}${m.t(' degrees of z',' 도 이내')}`);
   r2(`${m.t('rotation error ','회전 오차 ')}${ER[o.k]} ${m.t('deg','도')}   ${m.t('translation error ','이동 오차 ')}${MM[o.k]} mm`);
  };
  const tl = m.timeline({repeatDelay:.3}),at = i => 1.2 + i * 1.9;
  fin(tl,g,11.6);
  tl.set(o,{k:0,s:0},0).set(gh,{rotation:ER[0],svgOrigin:so},0);
  for (let i = 1; i < 5; i++) tl.set(o,{k:i},at(i)).fromTo(o,{s:S[i - 1]},{s:S[i],duration:1,ease:'power2.inOut'},at(i)).fromTo(gh,{rotation:ER[i - 1],svgOrigin:so},{rotation:ER[i],svgOrigin:so,duration:.9,ease:'power2.inOut'},at(i));
  m.play(tl,{rest:10.4,draw});
 });
})();
