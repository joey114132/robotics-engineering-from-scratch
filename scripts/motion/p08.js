// phase 08 concept animations (480x270): odometry-gap, resample-pointers, lookahead-race; needs window.MB from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,cl,hd,fin,EI} = K,D2R = Math.PI / 180,DA = 'stroke-dasharray';
 const T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 // D: a text node you set from draw(); .e is the node for tweens
 const D = (p,x,y,cls,an,sz) => {const e = $(p,'text',{x,y,'font-size':sz || 15,class:cls || '','text-anchor':an || 'start'}); let l = ''; const f = s => {if (s !== l) {l = s; e.textContent = s;}}; f.e = e; return f;};
 const stage = (m,en,ko) => {const q = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return q;};
 const tri = (p,cls) => $(p,'polygon',{points:'11,0 -8,7 -8,-7',class:cls});
 const put = (e,x,y,th) => A(e,{transform:`translate(${x} ${y}) rotate(${-th / D2R})`});

 // 08/01: the real robot turns 88.2 degrees per corner, the odometry estimate uses the planned width and closes the square
 R.gs('odometry-gap',(el,m) => {
  const g = stage(m,'The real track width is 2% larger than the planner assumed, so each 90 degree corner turns only 88.2 degrees and four sides leave a 0.18 m gap. Odometry reuses the same wrong width, so its square closes.','실제 윤거가 계획보다 2% 크면 직각 코너마다 88.2도만 돌아 네 변이 0.18 m 어긋납니다. 오도메트리는 같은 틀린 윤거를 쓰므로 사각형이 닫힙니다.');
  const KT = 1.02,SD = 2,AR = Math.PI / 2 / KT,AG = Math.PI / 2,U = 2.2,OX = 40,OY = 222,PX = 80;
  const sx = x => OX + x * PX,sy = y => OY - y * PX;
  const V = (k,a) => {let x = 0,y = 0; for (let i = 0; i < k; i++) {x += SD * Math.cos(i * a); y += SD * Math.sin(i * a);} return [x,y];};
  const at = (t,a) => {const k = Math.min(3,t / U | 0),r = t - U * k,v = V(k,a),f = cl(r / 1.5) * SD,h = k * a;
   return {k,x:v[0] + f * Math.cos(h),y:v[1] + f * Math.sin(h),h:h + cl((r - 1.5) / .7) * a};};
  const trail = (p,a) => {let d = `M${sx(0)} ${sy(0)}`; for (let i = 1; i <= p.k; i++) {const v = V(i,a); d += `L${sx(v[0])} ${sy(v[1])}`;} return d + `L${sx(p.x)} ${sy(p.y)}`;};
  RR(g,OX,OY - SD * PX,SD * PX,SD * PX,0,'n s sm',{[DA]:'4 6'});
  const tr = $(g,'path',{class:'s n st w3'});
  const gh = tri(g,'n s sm w3'),rb = tri(g,'f s st'); A(gh,{[DA]:'3 3'}); const gl = $(g,'line',{x1:sx(0),y1:sy(0),class:'s sw w6'});
  const c1 = D(g,250,62,'g'),big = D(g,250,176,'w',0,34),ok = D(g,250,204,'m');
  T(m,g,250,82,'(asked for 90.0°)','(지시한 값 90.0°)','m'); T(m,g,250,126,'Odometry position error','오도메트리 위치 오차','g');
  tri($(g,'g',{transform:'translate(260 236)'}),'f s st'); T(m,g,282,241,'real robot','실제 로봇','m'); A(tri($(g,'g',{transform:'translate(260 258)'}),'n s sm w3'),{[DA]:'3 3'}); T(m,g,282,263,'odometry estimate','오도메트리 추정','m');
  const draw = t => {
   const s = cl(t - .8,0,8.8),pr = at(s,AR),pg = at(s,AG),gap = Math.hypot(pr.x - pg.x,pr.y - pg.y),end = s >= 8.8;
   A(tr,{d:trail(pr,AR)}); put(rb,sx(pr.x),sy(pr.y),pr.h); put(gh,sx(pg.x),sy(pg.y),pg.h);
   A(gl,{x2:sx(pr.x),y2:sy(pr.y),opacity:end ? 1 : 0});
   c1(m.t(`Each corner turns ${(AR / D2R).toFixed(1)}°`,`코너마다 ${(AR / D2R).toFixed(1)}° 회전`)); big(gap.toFixed(2) + ' m');
   ok(end ? m.t('Odometry says: home.','오도메트리는 제자리라 합니다.') :'');
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,12.2); m.play(tl,{rest:11,draw});
 });

 // 08/02: systematic resampling: weights end to end on one strip, N evenly spaced pointers from one offset copy the guesses under them
 R.gs('resample-pointers',(el,m) => {
  const g = stage(m,'Systematic resampling with N = 10 guesses. Weights are laid end to end on a strip, then 10 evenly spaced pointers from one offset copy the guess under each. Heavy guesses are copied, light ones are dropped, and the count stays 10.','N = 10개의 추측으로 보는 systematic resampling입니다. 가중치를 한 줄에 이어 붙이고 한 오프셋에서 시작한 10개의 등간격 포인터가 아래 추측을 복사합니다. 무거운 추측은 여러 번 복사되고 가벼운 추측은 사라지며 개수는 10으로 유지됩니다.');
  const N = 10,E = [1.5,-.5,2.4,.1,-1.7,.4,3,-.2,-1,.9],U0 = .37,X0 = 24,WD = 432;
  const w = E.map(e => Math.exp(-.5 * e * e)),sw = w.reduce((a,b) => a + b),W = w.map(v => v / sw),C = W.map((v,i) => W.slice(0,i + 1).reduce((a,b) => a + b));
  const par = Array.from({length:N},(_,k) => {const q = (U0 + k) / N; return C.findIndex(c => c >= q);}),cnt = W.map((_,i) => par.filter(p => p === i).length);
  const xc = i => 45 + i * 43.3,cls = i => i % 2 ? 'l' :'f';
  const cir = W.map((v,i) => CC(g,xc(i),64,0,cls(i) + ' s st')),lab = W.map((v,i) => D(g,xc(i),108,'m','middle'));
  const seg = W.map((v,i) => RR(g,X0 + WD * (C[i] - v),126,WD * v,20,0,cls(i) + ' s st'));
  const fan = W.map((v,i) => $(g,'line',{x1:xc(i),y1:112,x2:X0 + WD * (C[i] - v / 2),y2:126,class:'s sm'}));
  const pt = par.map((p,k) => $(g,'path',{d:`M0 0l-6 11h12z`,class:'x s sb'})),dots = par.map(p => CC(g,0,0,0,cls(p) + ' s st'));
  const gone = cnt.map((c,i) => c ? null :D(g,xc(i),238,'x','middle'));
  const msg = D(g,16,22,'g'),foot = D(g,16,264,'m');
  const MSG = [[0,'Each guess gets a weight from its range error.','각 추측은 거리 오차로 가중치를 받습니다.'],[2.2,'Lay the weights end to end on one strip.','가중치를 한 줄로 이어 붙입니다.'],[3.4,'10 evenly spaced pointers, one random offset.','오프셋 하나에서 시작하는 포인터 10개입니다.'],[8.6,'Heavy guesses copied, light ones dropped.','무거운 추측은 복사되고 가벼운 추측은 사라집니다.']];
  const draw = t => {
   const gr = cl((t - .4) / 1.2),sp = cl(t - 2.2),m0 = MSG.filter(s => t >= s[0]).pop();
   msg(m.t(m0[1],m0[2]));
   W.forEach((v,i) => {A(cir[i],{r:(4 + 16 * Math.sqrt(v / Math.max(...W))) * gr}); lab[i](gr > .9 ? (v < .005 ? '<1%' :Math.round(v * 100) + '%') :'');
    A(seg[i],{opacity:sp}); A(fan[i],{opacity:sp});});
   par.forEach((p,k) => {const pk = cl((t - 3.4 - k * .5) / .35),j = par.slice(0,k).filter(q => q === p).length,px = X0 + WD * (U0 + k) / N;
    A(pt[k],{transform:`translate(${px} ${150 + (1 - pk) * 14})`,opacity:pk}); A(dots[k],{cx:xc(p),cy:232 - 17 * j,r:7 * pk,opacity:pk});});
   gone.forEach((e,i) => e && e(t > 8.6 ? '×' :''));
   const n = par.filter((_,k) => t >= 3.75 + k * .5).length; foot(t >= 3.4 ? m.t(`guesses before: ${N}, copies so far: ${n}`,`이전 추측: ${N}개, 지금까지 복사: ${n}개`) :'');
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,12.6); m.play(tl,{rest:11,draw});
 });

 // 08/04: pure pursuit on the lesson's path (lag 0.4 s, 1 m/s, start 0.6 m left of the path), three look-ahead distances at once
 R.gs('lookahead-race',(el,m) => {
  const g = stage(m,'Pure pursuit with look-ahead 0.4, 1.5 and 4 m on the lesson path (1 m/s, drive lag 0.4 s, start 0.6 m off the path), played 2.2x fast. Short look-ahead snakes, long look-ahead cuts the corner.','레슨의 경로에서 look-ahead 0.4, 1.5, 4 m로 pure pursuit을 돌린 모습입니다(1 m/s, 구동 지연 0.4초, 경로에서 0.6 m 떨어져 출발). 2.2배 빠르게 재생합니다. 짧으면 구불거리고 길면 코너를 가로지릅니다.');
  const P = [];
  for (let i = 0; i < 500; i++) P.push([i * .02,0]);
  for (let i = 0; i < 500; i++) P.push([10,i * .02]);
  P.push([10,10]);
  const dist = (a,b) => Math.hypot(a[0] - b[0],a[1] - b[1]);
  const follow = ld => {                      // port of follow() in code/main.py
   const p = [0,.6,0],tr = [[...p,0,0]]; let w = 0;
   for (let n = 0; n < 3000; n++) {
    let bi = 0; for (let i = 1; i < P.length; i++) if (dist(P[i],p) < dist(P[bi],p)) bi = i;
    let tg = P[P.length - 1]; for (let i = bi; i < P.length; i++) if (dist(P[i],p) >= ld) {tg = P[i]; break;}
    const dx = tg[0] - p[0],dy = tg[1] - p[1],yy = -Math.sin(p[2]) * dx + Math.cos(p[2]) * dy;
    w += (2 * yy / (dx * dx + dy * dy) - w) * (1 - Math.exp(-.02 / .4));
    p[0] += .02 * Math.cos(p[2]); p[1] += .02 * Math.sin(p[2]); p[2] += .02 * w;
    tr.push([...p,tg[0],tg[1]]); if (dist(p,[10,10]) < .15) break;
   }
   let cs = 0,cm = 1e9,last = 0;               // running line crossings on x < 8 (dead band 0.02) and closest approach to the corner
   return tr.map(q => {cm = Math.min(cm,dist(q,[10,0])); if (q[0] < 8 && Math.abs(q[1]) > .02) {const s = Math.sign(q[1]); if (last && s !== last) cs++; last = s;} return q.concat(cs,cm);});
  };
  const LD = [.4,1.5,4],CL = ['t','k','w'],ST = ['st','sk','sw'],run = LD.map(follow);
  const sx = x => 22 + x * 21,sy = y => 240 - y * 21;
  $(g,'path',{d:`M${sx(0)} ${sy(0)}L${sx(10)} ${sy(0)}L${sx(10)} ${sy(10)}`,class:'s n sm w3'}); CC(g,sx(10),sy(0),4,'g');
  const rows = LD.map((ld,i) => {
   CC(g,262,62 + 56 * i,6,CL[i]);
   return {tr:$(g,'path',{class:`s n ${ST[i]} w3`}),tt:$(g,'line',{class:`s ${ST[i]}`,[DA]:'2 4'}),td:CC(g,0,0,4,CL[i]),rb:tri(g,CL[i] + ' s st'),tx:D(g,276,67 + 56 * i,'g'),ty:D(g,276,88 + 56 * i,'m'),tz:D(g,276,108 + 56 * i,'m')};
  });
  const draw = t => {
   const s = cl((t - .6) * 2.2,0,16);
   rows.forEach((r,i) => {
    const tr = run[i],n = Math.min(tr.length - 1,Math.round(s * 50)),q = tr[n];
    A(r.tr,{d:'M' + tr.slice(0,n + 1).filter((_,k) => k % 5 === 0 || k === n).map(a => sx(a[0]).toFixed(1) + ' ' + sy(a[1]).toFixed(1)).join('L')});
    A(r.tt,{x1:sx(q[0]),y1:sy(q[1]),x2:sx(q[3]),y2:sy(q[4])}); A(r.td,{cx:sx(q[3]),cy:sy(q[4])}); put(r.rb,sx(q[0]),sy(q[1]),q[2]);
    r.tx(`Ld ${LD[i]} m`); r.ty(m.t(`${q[5]} crossing${q[5] === 1 ? '' :'s'}`,`가로지름 ${q[5]}회`));
    r.tz(m.t(`corner ${q[0] >= 7 ? q[6].toFixed(2) + ' m' :'–'}`,`코너 ${q[0] >= 7 ? q[6].toFixed(2) + ' m' :'–'}`));
   });
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,11.4); m.play(tl,{rest:10.5,draw});
 });

 // 08/05: two ICP runs from the lesson (room spacing 0.05 m, start rotation 0.2 and 2.6 rad): nearest-point pairs, fit, repeat
 R.gs('icp-two-starts',(el,m) => {
  const g = stage(m,'ICP on the lesson room, two starts. Each pass pairs every point with its nearest neighbour, fits one rigid move and repeats. From 0.2 rad the pairs are right and the error falls to 0.016 m. From 2.6 rad many pairs are wrong and it locks at 0.538 m.','레슨의 방으로 ICP를 두 번 돌립니다. 매번 각 점을 가장 가까운 점과 짝지어 강체 이동을 하나 맞추고 반복합니다. 0.2 rad에서 시작하면 짝이 맞아 오차가 0.016 m까지 줄고 2.6 rad에서는 틀린 짝이 많아 0.538 m에서 멈춥니다.');
  const RM = [[0,0],[6,0],[6,2],[4,2],[4,4],[0,4],[0,0]],room = ph => {const o = []; for (let e = 0; e < 6; e++) {const a = RM[e],b = RM[e + 1],n = Math.hypot(b[0] - a[0],b[1] - a[1]); for (let s = ph * .05; s < n - 1e-9; s += .05) o.push([a[0] + s * (b[0] - a[0]) / n,a[1] + s * (b[1] - a[1]) / n]);} return o;};
  const ref = room(0),cur = room(.5),nn = (P,Q) => P.map(p => {let b = 0,bd = 1e9; Q.forEach((q,i) => {const d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2; if (d < bd) {bd = d; b = i;}}); return b;});
  const rms = (P,Q,ix) => Math.sqrt(P.reduce((s,p,i) => s + (p[0] - Q[ix[i]][0]) ** 2 + (p[1] - Q[ix[i]][1]) ** 2,0) / P.length);
  const run = ang => {const c = Math.cos(ang),s = Math.sin(ang); let P = cur.map(q => {const x = q[0] - .3,y = q[1] + .2; return [x * c + y * s,-x * s + y * c];}); const st = [P],er = [];
   for (let k = 0; k < 40; k++) {const ix = nn(P,ref),Q = ix.map(i => ref[i]),e = rms(P,ref,ix); er.push(e); if (k && er[k - 1] - e < 1e-12) break;
    const mp = [0,1].map(d => P.reduce((a,p) => a + p[d],0) / P.length),mq = [0,1].map(d => Q.reduce((a,q) => a + q[d],0) / Q.length); let sc = 0,sd = 0;
    P.forEach((p,i) => {const a = [p[0] - mp[0],p[1] - mp[1]],b = [Q[i][0] - mq[0],Q[i][1] - mq[1]]; sd += a[0] * b[0] + a[1] * b[1]; sc += a[0] * b[1] - a[1] * b[0];});
    const th = Math.atan2(sc,sd),c2 = Math.cos(th),s2 = Math.sin(th); P = P.map(p => {const x = p[0] - mp[0],y = p[1] - mp[1]; return [mq[0] + x * c2 - y * s2,mq[1] + x * s2 + y * c2];}); st.push(P);}
   er.push(rms(P,ref,nn(P,ref))); return {st,er,ix:st.map(P => nn(P,ref))};};   // er[k] = rms before pass k; the last entry is the final rms
  const RN = [run(.2),run(2.6)],all = ref.concat(RN[0].st[0],RN[1].st[0]),xs = all.map(p => p[0]),ys = all.map(p => p[1]);
  const x0 = Math.min(...xs),x1 = Math.max(...xs),y0 = Math.min(...ys),y1 = Math.max(...ys),SC = Math.min(222 / (x1 - x0),150 / (y1 - y0));
  const pan = RN.map((r,i) => {const ox = 4 + i * 238,sx = x => ox + (x - x0) * SC,sy = y => 190 - (y - y0) * SC;
   ref.forEach((q,k) => k % 3 === 0 && CC(g,sx(q[0]),sy(q[1]),1.8,'g'));
   return {sx,sy,pr:Array.from({length:40},() => $(g,'line',{class:'s sm'})),dots:Array.from({length:100},() => CC(g,0,0,2.4,i ? 'w' :'k')),a:D(g,ox + 4,230,'g'),b:D(g,ox + 4,254,'m')};});
  const draw = t => {
   const u = Math.max(0,(t - .8) / .42);
   RN.forEach((r,i) => {const n = r.st.length - 1,k = Math.min(n,Math.floor(u)),f = k < n ? cl(u - k) :0,pm = cl(f / .5 - .2),mv = EI(cl((f - .5) / .5)),P = pan[i],A0 = r.st[k],A1 = r.st[Math.min(n,k + 1)];
    P.dots.forEach((e,j) => {const a = A0[j * 4],b = A1[j * 4]; A(e,{cx:P.sx(a[0] + (b[0] - a[0]) * mv),cy:P.sy(a[1] + (b[1] - a[1]) * mv)});});
    P.pr.forEach((e,j) => {const a = A0[j * 10],q = ref[r.ix[k][j * 10]]; A(e,{x1:P.sx(a[0]),y1:P.sy(a[1]),x2:P.sx(q[0]),y2:P.sy(q[1]),opacity:k < n ? (f < .5 ? pm : 0) :0});});
    P.a(m.t(`start ${i ? '2.6' : '0.2'} rad · pass ${k}`,`시작 ${i ? '2.6' : '0.2'} rad · ${k}회째`)); P.b(m.t(`rms ${r.er[k].toFixed(3)} m` + (k >= n ? (i ? ' · stuck' :' · converged') :''),`rms ${r.er[k].toFixed(3)} m` + (k >= n ? (i ? ' · 갇힘' :' · 수렴') :'')));
   });
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,12.6); m.play(tl,{rest:12,draw});
 });

 // 08/06: the lesson's square loop (seed 0, heading bias 0.02 per step): poses solved by Gauss-Newton, shown after 0, 1, 2 and 15 passes
 R.gs('loop-bend',(el,m) => {
  const g = stage(m,'The lesson square loop (5 m, 21 poses, drift from a small heading bias). One late loop-closure edge joins the last pose to the first, and Gauss-Newton moves every pose at once: cost 1246.4, 31.2, then 21.9, and position error 0.70 m down to 0.09 m. Values are the lesson solver output.','레슨의 정사각형 루프입니다(5 m, 포즈 21개, 작은 heading 편향이 만든 표류). 늦게 들어온 루프 폐쇄 간선 하나가 마지막 포즈를 첫 포즈에 잇고 Gauss-Newton이 모든 포즈를 한꺼번에 움직입니다. 비용은 1246.4, 31.2, 21.9, 위치 오차는 0.70 m에서 0.09 m로 줄어듭니다. 값은 레슨 solver의 출력입니다.');
  const Z = s => s.split(',').map(Number),X = [Z('0,0,1,0,2,.01,3.03,.08,4,.13,4.95,.21,4.87,1.19,4.74,2.19,4.63,3.21,4.47,4.22,4.32,5.19,3.36,5.01,2.37,4.8,1.41,4.58,.41,4.35,-.57,4.04,-.24,3.1,.14,2.14,.5,1.23,.89,.34,1.29,-.59'),
   Z('0,0,1,0,2,0,3.02,.04,3.99,.04,4.94,.05,4.96,1.04,4.94,2.06,4.96,3.1,4.97,4.14,4.99,5.14,3.99,5.16,2.94,5.19,1.92,5.22,.85,5.26,-.22,5.24,-.19,4.2,-.13,3.12,-.09,2.09,-.04,1.06,0,-.03'),
   Z('0,0,1,-.01,1.99,-.01,3.01,.02,3.98,.01,4.93,.01,4.93,1,4.9,2,4.9,3.02,4.89,4.04,4.89,5.02,3.9,5.02,2.89,5.01,1.89,5.01,.86,5.02,-.17,4.99,-.14,3.99,-.08,2.95,-.06,1.97,-.02,1,0,-.02'),
   Z('0,0,1,-.01,1.99,-.01,3.01,.02,3.98,.01,4.93,.01,4.93,.99,4.9,2,4.9,3.02,4.89,4.04,4.89,5.01,3.91,5.01,2.89,5.01,1.9,5.01,.86,5.02,-.17,4.99,-.13,3.99,-.08,2.95,-.06,1.97,-.02,1,0,-.02')],
   CO = ['1246.4','31.2','21.9','21.9'],AT = ['0.70','0.16','0.09','0.09'],sx = x => 30 + x * 38,sy = y => 226 - y * 38;
  RR(g,sx(0),sy(5),5 * 38,5 * 38,0,'n s sm',{[DA]:'4 6'});
  const path = $(g,'path',{class:'s n st w3'}),cl2 = $(g,'line',{class:'s sw w4',[DA]:'5 4'}),rb = CC(g,0,0,6,'f s st'),dots = X[0].slice(0,21).map(() => CC(g,0,0,2.5,'g'));
  const a = D(g,262,70,'g'),b = D(g,262,100,'g'),c = D(g,262,150,'g'),d = D(g,262,200,'m');
  const draw = t => {
   const sg = cl((t - .6) / 2.6,0,1) * 20,st = t < 4.2 ? 0 :t < 6 ? 1 :t < 7.8 ? 2 :3,q = t < 4.2 ? 0 :EI(cl((t - [4.2,4.2,6,7.8][st]) / 1.2)),A0 = X[Math.max(0,st - 1)],A1 = X[st],n = 21;
   const P = Array.from({length:n},(_,i) => st ? [0,1].map(k => A0[2 * i + k] + (A1[2 * i + k] - A0[2 * i + k]) * q) :[X[0][2 * i],X[0][2 * i + 1]]);
   const vis = t < 4.2 ? Math.floor(sg) :20;
   let dd = ''; for (let i = 0; i <= vis; i++) dd += (i ? 'L' :'M') + sx(P[i][0]) + ' ' + sy(P[i][1]); A(path,{d:dd});
   dots.forEach((e,i) => A(e,{cx:sx(P[i][0]),cy:sy(P[i][1]),opacity:i <= vis ? 1 :0}));
   A(rb,{cx:sx(P[Math.min(20,vis)][0]),cy:sy(P[Math.min(20,vis)][1])}); A(cl2,{x1:sx(P[20][0]),y1:sy(P[20][1]),x2:sx(P[0][0]),y2:sy(P[0][1]),opacity:t >= 3.4 ? 1 :0});
   a(t < 3.4 ? m.t('Odometry drifts open','odometry가 벌어집니다') :t < 4.2 ? m.t('Loop closure: "back at the start"','루프 폐쇄: "시작점으로 돌아왔다"') :m.t('Every pose moves at once','모든 포즈가 한꺼번에 움직입니다'));
   b(t >= 3.2 ? m.t(`gap ${Math.hypot(...P[20].map((v,k) => v - P[0][k])).toFixed(2)} m`,`간격 ${Math.hypot(...P[20].map((v,k) => v - P[0][k])).toFixed(2)} m`) :'');
   c(t >= 4.2 ? m.t(`pass ${[0,1,2,15][st]} · cost ${CO[st]}`,`${[0,1,2,15][st]}회째 · 비용 ${CO[st]}`) :m.t('cost 1246.4','비용 1246.4')); d(m.t(`position error ${AT[t < 4.2 ? 0 :st]} m (rms)`,`위치 오차 ${AT[t < 4.2 ? 0 :st]} m (rms)`));
  };
  const tl = m.timeline({repeatDelay:.3}); fin(tl,g,12.6); m.play(tl,{rest:11,draw});
 });
})();
