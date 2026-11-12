// phase 07 concept loops (480x270) as GSAP timelines on the MB kit from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,hd,fin} = K,T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 // D: a text node you set from draw(); .e is the node for tweens
 const D = (p,x,y,cls,an) => {const e = $(p,'text',{x,y,'font-size':15,class:cls || '','text-anchor':an || 'start'}); let l = ''; const f = s => {if (s !== l) {l = s; e.textContent = s;}}; f.e = e; return f;};
 const stage = (m,en,ko) => {const q = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return q;};
 const rng = s => () => (s = (s * 9301 + 49297) % 233280) / 233280;
 const gauss = r => () => Math.sqrt(-2 * Math.log(r() + 1e-9)) * Math.cos(6.2832 * r());

 R.gs('kalman-gain',(el,m) => {
  const g = stage(m,'The lesson\'s model, sensor noise 2.0 m. The gain K starts at 0.5 and settles at 0.27 while sqrt(P00) falls from 1.41 m to 1.04 m, about half of 2.0 m.','레슨의 모델입니다(센서 잡음 2.0 m). gain K는 0.5에서 시작해 0.27로 가라앉고 sqrt(P00)은 1.41 m에서 1.04 m로 줄어 2.0 m의 절반쯤이 됩니다.');
  const N = 60,gs = gauss(rng(3)),S = [];
  let p = 2 * gs(),v = 1 + gs(),x = 0,w = 1,a = 4,b = 0,c = 1;   // truth [p, v], estimate [x, w], P = [[a, b], [b, c]]
  for (let k = 0; k < N; k++) {
   if (k) {const q = .1 * gs(); p += v + q / 2; v += q; x += w; [a,b,c] = [a + 2 * b + c + .0025,b + c + .005,c + .01];}
   const z = p + 2 * gs(),s = a + 4,K0 = a / s,K1 = b / s,e = z - x;
   x += K0 * e; w += K1 * e; [a,b,c] = [a - K0 * a,b - K0 * b,c - K1 * b];
   S.push({zr:z - p,ef:x - p,K:K0,sp:Math.sqrt(a)});
  }
  const X = k => 24 + k * 7.2,Y = e => 96 - e * 10.5;
  T(m,g,16,22,'Error against the truth (m)','참값과의 오차(m)','g'); $(g,'path',{d:'M20 96H462',class:'s n sm','stroke-dasharray':'3 6'});
  const band = $(g,'path',{class:'l',opacity:.35}),line = $(g,'path',{class:'s n st w3'}),dots = S.map(s => CC(g,0,0,2.6,'m'));
  CC(g,24,176,3,'m'); T(m,g,34,181,'sensor','센서','m'); $(g,'path',{d:'M112 176h20',class:'s n st w3'}); T(m,g,138,181,'filter','필터','m'); RR(g,212,170,20,12,2,'l',{opacity:.35}); T(m,g,238,181,'± sqrt(P00)','± sqrt(P00)','m');
  const kb = RR(g,206,192,0,14,3,'k'),pb = RR(g,206,224,0,14,3,'f'),kt = D(g,16,204,'g'),pt = D(g,16,236,'g');
  $(g,'path',{d:'M386 216V246',class:'s n sw','stroke-dasharray':'3 4'}); T(m,g,386,262,'sensor 2.0 m','센서 2.0 m','m','middle');
  const o = {k:0};
  const draw = () => {
   const k = Math.round(o.k),s = S[k]; let up = '',lo = '',ln = '';
   S.forEach((q,i) => {A(dots[i],{cx:X(i),cy:Y(q.zr),opacity:i <= k ? 1 :0}); if (i <= k) {up += `${i ? 'L' :'M'}${X(i)} ${Y(q.sp)}`; lo = `L${X(i)} ${Y(-q.sp)}` + lo; ln += `${i ? 'L' :'M'}${X(i)} ${Y(q.ef)}`;}});
   A(band,{d:up + lo + 'Z'}); A(line,{d:ln}); A(kb,{width:s.K * 240}); A(pb,{width:s.sp * 90});
   kt(`${m.t('sensor weight K = ','센서 가중 K = ')}${s.K.toFixed(2)}`); pt(`sqrt(P00) = ${s.sp.toFixed(2)} m`);
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,12.4);
  tl.fromTo(o,{k:0},{k:N - 1,duration:10.2,ease:'none'},.6);
  m.play(tl,{rest:11.4,draw});
 });

 R.gs('gravity-leak',(el,m) => {
  const g = stage(m,'Robot sitting still, gyro bias 0.01 rad/s. The tilt estimate is off by b t, gravity leaks in as g sin(b t), and the position estimate runs off: 16.4 m after 10 s.','gyro bias 0.01 rad/s인 채 가만히 있는 로봇입니다. 기울기 추정이 b t만큼 틀려 중력이 g sin(b t)로 새고 위치 추정은 10초 뒤 16.4 m까지 달아납니다.');
  const G = 9.81,B = .01,pos = [],fa = [],X = d => 30 + d * 24.6;
  for (let i = 1,v = 0,p = 0; i <= 1000; i++) {const a = G * Math.sin(B * i * .01); v += a * .01; p += v * .01; fa.push(a); pos.push(p);}   // the lesson's leaked_position()
  T(m,g,16,22,'A robot sitting still, gyro bias only','가만히 있는 로봇, gyro bias만 있음','g');
  $(g,'path',{d:'M20 80H140',class:'s n sm'}); T(m,g,24,66,'level','수평','m');
  const tilt = $(g,'path',{d:'M20 80H140',class:'s n sw w3'}),ar = $(g,'path',{class:'s n sw w4'}); T(m,g,250,66,'leftover acceleration','남는 가속도','m');
  const r1 = D(g,16,118,'g'),r2 = D(g,250,118,'g');
  $(g,'path',{d:'M20 170H462',class:'s n sm'}); [0,5,10,15].forEach(d => {$(g,'path',{d:`M${X(d)} 170v6`,class:'s n sm'}); T(m,g,X(d),194,d + (d === 15 ? ' m' :''),d + (d === 15 ? ' m' :''),'m','middle');});
  RR(g,X(0) - 13,152,26,16,4,'f s st'); const gh = RR(g,X(0) - 13,152,26,16,4,'n s sw',{'stroke-dasharray':'4 3'});
  $(g,'path',{d:'M16 218h22',class:'s n st'}); T(m,g,44,223,'robot','로봇','m'); $(g,'path',{d:'M130 218h22','stroke-dasharray':'4 3',class:'s n sw'}); T(m,g,158,223,'estimate','추정','m');
  const rd = D(g,16,250,'g'),o = {t:0};
  const draw = () => {
   const i = Math.max(0,Math.round(o.t * 100) - 1),a = fa[i],deg = B * o.t * 180 / Math.PI;
   A(tilt,{transform:`rotate(${-deg} 80 80)`}); A(ar,{d:hd(250,80,Math.max(1,a * 100),0)}); A(gh,{x:X(pos[i]) - 13});
   r1(`${m.t('tilt error b t = ','기울기 오차 b t = ')}${deg.toFixed(1)}°`); r2(`g sin(b t) = ${a.toFixed(2)} m/s²`);
   rd(`t = ${o.t.toFixed(1)} s   ${m.t('position error = ','위치 오차 = ')}${pos[i].toFixed(1)} m`);
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,11.4);
  tl.fromTo(o,{t:0},{t:10,duration:8.6,ease:'none'},1);
  m.play(tl,{rest:10.4,draw});
 });

 R.gs('tau-lanes',(el,m) => {
  const g = stage(m,'Same noisy gyro (bias 0.01 rad/s) and accelerometer (noise 0.05 rad), three time constants. Small tau lets noise in. Large tau lets the bias creep in: a steady error of tau times bias. The noise is this widget\'s own draw, so its rmse differs from the lesson\'s printed value.','같은 gyro(bias 0.01 rad/s)와 가속도계(잡음 0.05 rad)를 시간상수 세 가지로 걸렀습니다. tau가 작으면 잡음이 들어오고 크면 bias가 스며들어 tau 곱하기 bias만큼 오차가 남습니다. 잡음은 이 위젯이 따로 뽑은 것이라 rmse가 레슨 출력값과 다릅니다.');
  const DT = .01,N = 1500,TAU = [.05,.4,2],gs = gauss(rng(9)),tr = i => .3 * Math.sin(1.9 * i * DT),gy = [],ac = [];
  for (let i = 0; i < N; i++) {gy.push(.57 * Math.cos(1.9 * i * DT) + .01 + .02 * gs()); ac.push(tr(i) + .05 * gs());}
  const ER = TAU.map(tau => {const a = tau / (tau + DT); let th = 0; return gy.map((w,i) => (th = a * (th + w * DT) + (1 - a) * ac[i]) - tr(i));});   // error of the lesson's complementary()
  const LY = [36,114,192],NM = [['tau 0.05 s: noise gets in','tau 0.05 s: 잡음이 들어옴'],['tau 0.40 s: in between','tau 0.40 s: 중간'],['tau 2 s: bias creeps in','tau 2 s: bias가 스며듦']];
  const fr = LY.map((y,l) => {T(m,g,22,y - 8,NM[l][0],NM[l][1],'g'); $(g,'path',{d:`M20 ${y + 26}H460`,class:'s n sm','stroke-dasharray':'3 6'}); return RR(g,20,y,440,52,6,'n s sm');});
  const ln = LY.map(() => $(g,'path',{class:'s n st'})),rm = LY.map((y,l) => D(g,458,y - 8,'m','end')),bt = D(g,16,262,'g'),o = {c:400,h:0};
  const draw = () => {
   const c = Math.round(o.c),i0 = Math.max(0,c - 400),rs = ER.map((e,l) => {
    let d = '',s2 = 0;
    for (let i = i0; i <= c; i++) {s2 += e[i] * e[i]; if (i % 4 === 0) d += `${d ? 'L' :'M'}${(20 + (i - c + 400) * 1.1).toFixed(1)} ${(LY[l] + 26 - Math.max(-24,Math.min(24,e[i] * 650))).toFixed(1)}`;}
    A(ln[l],{d}); return Math.sqrt(s2 / (c - i0 + 1));
   }),best = rs.indexOf(Math.min(...rs));
   rs.forEach((r,l) => {rm[l](m.t('this run, 4 s rmse ','이 실행, 4초 rmse ') + r.toFixed(4)); A(fr[l],{class:'n s ' + (o.h && l === best ? 'sk' :'sm')});});
   bt(o.h ? `${m.t('lowest rmse: tau = ','rmse가 가장 낮은 tau = ')}${TAU[best]} s` :m.t('tilt error (rad), last 4 s','기울기 오차(rad), 최근 4초'));
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,12.4);
  tl.set(o,{h:0},0).fromTo(o,{c:400},{c:N - 1,duration:11,ease:'none'},.6).set(o,{h:1},9.8);
  m.play(tl,{rest:11.6,draw});
 });

 R.gs('ekf-stall',(el,m) => {
  const g = stage(m,'Same start for both runs, heading 1.5 rad off (lesson code, seed 0). With four landmarks the heading error drops into its band. With one it stalls near -0.43 rad while the filter stays sure (sigma 0.05), and NEES ends at 667 where about 3 is expected.','두 실행의 출발은 같고 heading이 1.5 rad 틀려 있습니다(레슨 코드, seed 0). landmark 4개면 heading 오차가 띠 안으로 들어옵니다. 1개면 -0.43 rad 근처에서 멈추는데 필터는 여전히 확신하고(sigma 0.05) NEES는 약 3이어야 할 자리에서 667로 끝납니다.');
  // lesson run, heading error (rad), sqrt(P heading) (rad) and NEES at every second step; four landmarks, then one landmark
  const DAT = [
   {h:[-1.56,0,0,0,-.01,0,0,0,.01,0,.01,.01,.01,.01,.01,.02,.01,0,0,0,0,.01,0,0,.01,.01,0,0,0,-.01,0,0,0,-.01,-.01,0,-.01,0,-.01,0,0],s:[.1,.011,.008,.007,.007,.007,.006,.006,.006,.006,.006,.006,.006,.006,.006,.006,.006,.006,.006,.006,.007,.007,.007,.007,.007,.007,.007,.007,.007,.007,.007,.007,.008,.008,.008,.008,.008,.008,.008,.008,.008],n:[245,1,1,1,3,0,1,1,2,2,3,2,5,4,8,12,15,8,4,1,1,3,2,1,2,1,1,1,1,2,1,3,7,5,5,5,7,3,5,3,6]},
   {h:[-1.56,-.48,-.46,-.46,-.46,-.47,-.48,-.47,-.47,-.48,-.47,-.46,-.46,-.46,-.45,-.46,-.45,-.45,-.45,-.44,-.44,-.46,-.45,-.45,-.45,-.44,-.44,-.44,-.44,-.44,-.44,-.42,-.43,-.43,-.43,-.44,-.43,-.43,-.43,-.43,-.43],s:[.1,.053,.052,.051,.051,.051,.051,.05,.05,.05,.05,.05,.05,.05,.05,.051,.051,.051,.051,.051,.051,.051,.051,.05,.05,.051,.051,.051,.051,.051,.051,.051,.051,.051,.052,.052,.052,.052,.052,.052,.053],n:[245,87,83,95,107,124,144,158,173,177,187,210,214,241,260,295,309,344,363,392,435,484,521,548,573,582,623,641,652,659,661,679,678,677,674,672,674,676,674,665,667]}
  ],CY = [52,152],X = i => 70 + i * 9.5,Y = (c,e) => c - e * 40;
  const rows = DAT.map((d,r) => {
   $(g,'path',{d:`M70 ${CY[r]}H450`,class:'s n sm','stroke-dasharray':'3 6'});
   return {band:$(g,'path',{class:'l',opacity:.5}),line:$(g,'path',{class:'s n w3 ' + (r ? 'sw' :'st')}),lab:D(g,464,CY[r] - 30,'g','end')};
  });
  T(m,g,16,CY[0] + 5,'0','0','m'); T(m,g,16,CY[1] + 5,'0','0','m');
  const r1 = D(g,16,236,'g'),r2 = D(g,16,258,'m'),o = {k:0};
  const draw = () => {
   const k = Math.round(o.k);
   DAT.forEach((d,r) => {
    let up = '',lo = '',ln = '';
    for (let i = 0; i <= k; i++) {up += `${i ? 'L' :'M'}${X(i)} ${Y(CY[r],2 * d.s[i])}`; lo = `L${X(i)} ${Y(CY[r],-2 * d.s[i])}` + lo; ln += `${i ? 'L' :'M'}${X(i)} ${Y(CY[r],d.h[i])}`;}
    A(rows[r].band,{d:up + lo + 'Z'}); A(rows[r].line,{d:ln}); rows[r].lab(`${r ? m.t('1 landmark','landmark 1개') :m.t('4 landmarks','landmark 4개')}   NEES ${d.n[k]}`);
   });
   const d = DAT[1];
   r1(`t = ${(k * .2).toFixed(1)} s   ${m.t('1 landmark: error ','landmark 1개: 오차 ')}${d.h[k].toFixed(2)} rad, 2σ = ±${(2 * d.s[k]).toFixed(2)}`);
   r2(m.t('line = heading error (rad), band = ±2 sigma','선 = heading 오차(rad), 띠 = ±2 sigma'));
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,11);
  tl.fromTo(o,{k:0},{k:40,duration:8.6,ease:'none'},.8);
  m.play(tl,{rest:10,draw});
 });
})();
