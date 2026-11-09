// 개념 애니메이션 4종, GSAP timeline (수치는 각 레슨 code/main.py 기준)
(()=>{
 const FG = 'var(--fg)', MUT = 'var(--mut)', LN = 'var(--line)', CD = 'var(--card)', PF = 'var(--pf)', PB = 'var(--pb)', PT = 'var(--pt)', BAD = 'var(--bad)', OK = 'var(--ok)', AM = 'var(--oops)';
 const sk = (c, w = 2.5, x = '') => `fill:none;stroke:${c};stroke-width:${w};stroke-linecap:round;stroke-linejoin:round;${x}`;
 const fl = (c, x = '') => `fill:${c};stroke:none;${x}`, box = (c, w = 2.5, f = CD) => `fill:${f};stroke:${c};stroke-width:${w}`, mut = fl(MUT), bold = fl(FG, 'font-weight:700');
 const f1 = v => v.toFixed(1), at = (e, o) => { for (const k in o) e.setAttribute(k, o[k]); };
 const poly = (xs, ys) => { let d = 'M'; for (let i = 0; i < xs.length; i++) d += (i ? 'L' : '') + f1(xs[i]) + ' ' + f1(ys[i]); return d; };
 const PT2 = s => { const a = s.split(',').map(Number), o = []; for (let i = 0; i < a.length; i += 2) o.push([a[i], a[i + 1]]); return o; };

 const kit=m=>{
  const n=(t,a,p)=>{const{s,...r}=a;return m.mk(t,s===undefined?a:{...r,style:s},p)};
  const T=(p,x,y,en,ko,z,st,an)=>{const e=n('text',{x,y,'text-anchor':an||'start',s:`font-size:${z}px;${st||''}`},p),f=()=>{e.textContent=m.t(en,ko)};f();m.onTheme(f);return e};
  const O=(p,x,y)=>{const e=n('g',{},p);gsap.set(e,{x,y,svgOrigin:'0 0'});return e};
  return{n,T,O,Tn:(p,x,y,v,z,st,an)=>T(p,x,y,v,v,z,st,an),L:(p,a,b,c,d,s)=>n('line',{x1:a,y1:b,x2:c,y2:d,s},p),Rc:(p,x,y,w,h,r,s)=>n('rect',{x,y,width:w,height:h,rx:r,s},p),
   C:(p,x,y,r,s)=>n('circle',{cx:x,cy:y,r,s},p),Pa:(p,d,s,a)=>n('path',{d,s,...a},p),tl:m.timeline({defaults:{ease:'power2.out'}})};
 };
 const io=(tl,g,P)=>tl.fromTo(g,{autoAlpha:0},{autoAlpha:1,duration:.5,ease:'power1.out'},0).to(g,{autoAlpha:0,duration:.6,ease:'power1.in'},P-.6);
 const swap=(tl,ns,ts)=>ns.forEach((e,i)=>{tl.fromTo(e,{autoAlpha:0,y:5},{autoAlpha:1,y:0,duration:.35},ts[i]);if(i<ns.length-1)tl.to(e,{autoAlpha:0,duration:.18,ease:'power1.in'},ts[i+1]-.18)});
 const DASH='stroke-dasharray:1 2;stroke-dashoffset:1.02';   // draw-in: tween strokeDashoffset 1.02 to 0 on a pathLength=1 path
 const NOM = { J: .05, b: .02, c: .05, k: .2, Tm: .03, dl: .02 }, DT = .002, NS = 1500, NK = Object.keys(NOM);
 const U = [[-.7, -.1, .4, .9, -.7, -1], [-.5, .3, -.2, .5, -.4, .2], [-.5, -.4, -.4, 0, -.9, -.5], [-.9, -.3, .8, -.9, -.2, .4], [-.4, .1, .8, .4, .5, -.4], [.1, 1, -.7, 0, .5, -.9], [.8, -.4, .5, -.1, -.8, -.9], [-.6, 0, -.2, .6, .6, .8], [.2, .4, .9, 0, -.2, .7], [-.4, -.4, .1, -.3, .5, .3], [-.7, .2, -.3, -.6, .7, .8], [.8, .8, .9, .9, .6, .2], [0, -.2, -1, -.6, .9, -.3], [.8, .3, -.8, 1, .4, 1]];
 const GAIN = [[4.51, .705], [7.75, 1.352], [4.51, .876]]; // 공칭, 폭 0.3, 폭 0.6에서 tune()이 고른 kp, kd
 function sim(u, kp, kd) {
  const p = {}; NK.forEach((k, i) => p[k] = NOM[k] * (1 + .3 * u[i]));
  const d = Math.round(p.dl / DT), q = new Float32Array(NS), w = new Float32Array(NS);
  const f = (x, v, m, c) => [v, (m - p.b * v - p.c * Math.tanh(v / .01) - p.k * Math.sin(x)) / p.J, (c - m) / p.Tm];
  let y = [0, 0, 0];
  for (let i = 0; i < NS; i++) {
   q[i] = y[0]; w[i] = y[1]; const j = Math.max(i - d, 0), c = Math.max(-1, Math.min(1, kp * (1 - q[j]) - kd * w[j] + NOM.k * Math.sin(q[j])));
   const a = f(...y, c), b = f(...y.map((v, k) => v + DT / 2 * a[k]), c), e = f(...y.map((v, k) => v + DT / 2 * b[k]), c), h = f(...y.map((v, k) => v + DT * e[k]), c);
   y = y.map((v, k) => v + DT / 6 * (a[k] + 2 * b[k] + 2 * e[k] + h[k]));
  }
  let last = 0, mx = 0; for (let i = 0; i < NS; i++) { if (Math.abs(q[i] - 1) > .05) last = i + 1; mx = Math.max(mx, q[i]); }
  return { q: Float32Array.from({ length: 42 }, (_, j) => q[j * 17]), ok: last * DT <= .8 && mx < 1.05 ? 1 : 0 };
 }

 MOTION.gs('domain-rand',(el,m)=>{
  const P=13,{svg,g}=m.svg(480,270,'One controller on 14 random joints, tuned three ways','무작위 관절 14개에 같은 controller, 세 가지 튜닝');
  const RS=GAIN.map(k=>U.map(u=>sim(u,k[0],k[1]))),DR=RS.map(r=>r.map(x=>x.q)),DOK=RS.map(r=>r.map(x=>x.ok));
  const{n,T,Tn,L,Rc,C,Pa,tl}=kit(m),X0=40,W=420,Y0=205,K=240,NP=42,N=14,cid='dr'+Math.random().toString(36).slice(2,7);
  const X=j=>X0+j/(NP-1)*W,Y=v=>Y0-(v-.6)*K,XT=X0+.8/1.4*W,xs=Array.from({length:NP},(_,j)=>X(j)),path=q=>poly(xs,Array.from(q,Y));
  Rc(n('clipPath',{id:cid},n('defs',{},svg)),X0-2,50,W+4,Y0-48,0,'');
  const cg=n('g',{'clip-path':`url(#${cid})`},g);
  Rc(g,XT,Y(1.05),W*.6/1.4,.1*K,0,fl(PF,'opacity:.4'));
  const lim=L(g,X0,Y(1.05),X0+W,Y(1.05),sk(BAD,2,'stroke-dasharray:2 5'));L(g,X0,Y(1),X0+W,Y(1),sk(MUT,1.5,'stroke-dasharray:4 5'));
  L(g,XT,80,XT,Y0,sk(LN,2,'stroke-dasharray:3 5'));L(g,X0,Y0,X0+W,Y0,sk(FG,2));
  T(g,X0+W,Y(1.05)-7,'limit 1.05','한계 1.05',15,fl(BAD),'end');Tn(g,X0-6,Y(.8)+5,'0.8',15,mut,'end');Tn(g,X0-6,Y(1)+5,'1',15,mut,'end');
  Tn(g,X0,223,'0',15,mut,'middle');T(g,XT,223,'0.8 s','0.8초',15,mut,'middle');
  const gh=[];for(let i=8;i<N;i++)gh.push(Pa(cg,path(DR[0][i]),sk(BAD,2,'stroke-dasharray:3 4')));gsap.set(gh,{autoAlpha:0});
  const cv=DR[0].map(q=>Pa(cg,path(q),sk(PT,2.5,DASH),{pathLength:1}));
  const big=n('text',{x:456,y:160,'text-anchor':'end',s:'font-size:30px;'+bold}, g),sub=T(g,456,180,'of random joints succeed','무작위 관절 중 성공',15,mut,'end');gsap.set([big,sub],{autoAlpha:0});
  swap(tl,[['a failed run costs 2 s','실패하면 2초로 계산'],['mean cost 0.532 s','평균 비용 0.532초'],['mean cost 0.586 s (10% slower)','평균 비용 0.586초 (10% 느림)']].map(t=>T(g,456,198,t[0],t[1],15,mut,'end')),[1.7,4.4,7.4]);
  swap(tl,[['Gains tuned on one nominal joint','공칭 관절 하나로 튜닝한 gain'],['Tuned across the real ±30% spread','실제 ±30% 범위로 튜닝'],['Tuned across ±60%: safer, slower','±60%로 튜닝: 더 안전, 더 느림']].map(t=>T(g,16,34,t[0],t[1],15,bold)),[0,4.4,7.4]);
  T(g,14,252,'tuned on','튜닝 범위',15,mut);
  const pills=[['nominal','공칭'],['±30%','±30%'],['±60%','±60%']].map((p,i)=>Rc(g,86+i*128,234,120,26,13,sk(LN,2))),hl=Rc(g,86,234,120,26,13,`fill:${PB};stroke:${PT};stroke-width:2.5`);
  [['nominal','공칭'],['±30%','±30%'],['±60%','±60%']].forEach((p,i)=>T(g,146+i*128,252,p[0],p[1],15,fl(FG),'middle'));
  m.caption('Same controller, 14 of 300 random joints (parameters within 30%). Percentages cover all 300.','같은 controller, 무작위 관절 300개 중 14개(파라미터 ±30%). 퍼센트는 300개 전체 결과입니다.');
  m.replayButton();
  // primary: the 14 step responses draw in, then morph to the response under the next tuning (d tween, staggered); secondary: success rate counts up, the highlight slides between pills
  const NV={v:0};
  tl.to(lim,{strokeDashoffset:-70,duration:P,ease:'none'},0)
   .to(cv,{strokeDashoffset:0,duration:.8,stagger:.06},.6).to([big,sub],{autoAlpha:1,duration:.4},1.7)
   .to(NV,{v:57,duration:1},1.8).to(NV,{v:99,duration:.8,ease:'power2.inOut'},4.9).to(NV,{v:100,duration:.8,ease:'power2.inOut'},7.9)
   .to(gh,{autoAlpha:.35,duration:.4,stagger:.05},4.4).to(hl,{x:128,duration:.5,ease:'back.out(1.5)'},4.4).to(hl,{x:256,duration:.5,ease:'back.out(1.5)'},7.4);
  [4.4,7.4].forEach((t,k)=>cv.forEach((c,i)=>tl.to(c,{attr:{d:path(DR[k+1][i])},duration:.9,ease:'power2.inOut'},t+i*.02)));
  io(tl,g,P);
  let pv=-1,sh=-1;
  m.play(tl,{rest:6.5,draw(t){
   const pc=Math.round(NV.v);if(pc!==pv){pv=pc;big.textContent=pc+'%'}
   const s=t<5.3?0:t<8.3?1:2;if(s!==sh){sh=s;cv.forEach((c,i)=>c.style.stroke=DOK[s][i]?PT:BAD)}
  }});
 });

 const BD = ['-89,35,-69,31,-50,29,-33,39,-15,48,5,52,25,49,43,42,60,31,76,19,91,7,99,1', '-130,66,-111,61,-91,55,-72,50,-53,44,-34,44,-15,50,5,53,25,50,43,42,60,31,75,19,91,7,99,1'].map(PT2);
 const R0 = PT2('-130,15,-117,12,-105,12,-95,8,-90,3,-75,8,-63,13,-52,15,-46,21,-32,28,-30,26,-20,31,-4,39,13,47,25,46,32,39,43,34,49,22,53,18,67,9,76,-5,88,-20,87,-19,77,-5,73,-17,73,-34,75,-41,66,-42,66,-38,65,-47,70,-48'), R4 = PT2('-130,15,-117,14,-105,14,-95,11,-89,8,-74,14,-62,20,-51,22,-46,31,-32,39,-29,36,-20,42,-4,50,13,57,25,55,32,48,42,43,49,31,54,29,68,20,77,6,91,-4,99,2,95,8,90,0,92,-9,100,-8,99,-5,98,-1,100,-3,105,-4');
 const C0 = [.114, .135, .271, .331, .424, .453, .424, .409, .42, .465, .548, .655, .748, .805, .813, .87], C4 = [.021, .021, .042, .057, .072, .074, .059, .047, .038, .04, .036, .044, .036, .037, .036, .032];

 MOTION.gs('bc-drift',(el,m)=>{
  const P=13,{svg,g}=m.svg(480,236,'A cloned policy drifts off; DAgger keeps it on track','복제 정책은 벗어나지만 DAgger를 쓰면 경로를 지킵니다');
  const{n,T,Tn,L,Rc,C,Pa,O,tl}=kit(m),AX=12,AY=60,mx=p=>AX+p[0]+140,my=p=>AY+88-p[1],path=a=>poly(a.map(mx),a.map(my));
  Rc(g,AX,AY,250,160,12,sk(LN,2));C(g,AX+140,AY+88,30,box(MUT,2.5,LN));
  const GX=AX+240,GY=AY+88,pulse=O(g,GX,GY);C(g,GX,GY,11,sk(PT,3));C(g,GX,GY,4,fl(PT));n('circle',{r:11,s:sk(PT,2)},pulse);
  const demo=BD.map(d=>Pa(g,path(d),sk(MUT,3,'stroke-dasharray:0.1 7;opacity:.8')));
  const trail=(a,c)=>Pa(g,path(a),sk(c,3.5,DASH),{pathLength:1}),t0=trail(R0,BAD),t4=trail(R4,OK),dem=BD.flat(),ticks=[];
  for(let i=3;i<31;i+=3){
   const p=R0[i],b=dem.reduce((a,q)=>(q[0]-p[0])**2+(q[1]-p[1])**2<(a[0]-p[0])**2+(a[1]-p[1])**2?q:a),L2=Math.hypot(b[0]-p[0],b[1]-p[1])||1;
   const tg=n('g',{},g);L(tg,mx(p),my(p),mx(p)+(b[0]-p[0])/L2*14,my(p)-(b[1]-p[1])/L2*14,sk(PT,2.5));C(tg,mx(p),my(p),4.5,box(PT,2,PF));gsap.set(tg,{autoAlpha:0,scale:.3,svgOrigin:`${mx(p)} ${my(p)}`});ticks.push(tg);
  }
  const hd=c=>{const h=C(g,0,0,7,box(c,3));return h},h0=hd(FG),h4=hd(OK);gsap.set(h4,{autoAlpha:0});
  const PX=300,PW=166,ex=i=>PX+i/15*PW,ey=v=>190-v*85,ln2=(a,c)=>Pa(g,poly(a.map((_,i)=>ex(i)),a.map(ey)),sk(c,3.5,DASH),{pathLength:1});
  L(g,PX,190,PX+PW,190,sk(FG,2));L(g,PX,190,PX,98,sk(FG,2));
  T(g,PX,93,'action error','행동 오차',15,mut);Tn(g,PX,208,'0',15,mut,'middle');T(g,PX+PW,208,'60 steps','60스텝',15,mut,'end');
  const e0=ln2(C0,BAD),e4=ln2(C4,OK),lab=(x,y,en,ko,z,c)=>{const e=T(g,x,y,en,ko,z,fl(c,'font-weight:700'),'end');gsap.set(e,{autoAlpha:0,scale:.5,svgOrigin:`${x} ${y}`});return e};
  const l0=lab(PX+PW-4,ey(.87)-8,'7×','7배',17,BAD),l4=lab(PX+PW-4,ey(.03)-10,'near 0','거의 0',15,OK);
  swap(tl,[['Plain cloning: errors pile up','단순 복제: 오차가 쌓임'],['DAgger: expert labels visited states','DAgger: 방문한 상태를 전문가가 라벨링'],['After 4 DAgger rounds: stays on track','DAgger 4라운드 후: 경로를 지킴']].map(t=>T(g,16,34,t[0],t[1],15,bold)),[0,5.2,8]);
  m.caption('Top view, goal behind an obstacle. Dotted: demonstrations. Red: cloned policy. Green: after 4 DAgger rounds (round 1 labels shown). Error: mean of 6 seeds.','위에서 본 과제입니다. 점선은 시연, 빨강은 복제 정책, 초록은 DAgger 4라운드 뒤입니다(1라운드 라벨 표시). 오차는 6 seed 평균입니다.');
  m.replayButton();
  // primary: the cloned run and the DAgger run each progress along their path (U0/U4 drive the head; the trail and the error curve use the same tween); secondary: label arrows pop one by one
  const U0={u:0},U4={u:0},run=(U,tr,e,at0,d)=>tl.to(U,{u:1,duration:d,ease:'power3.inOut'},at0).to([tr,e],{strokeDashoffset:0,duration:d,ease:'power3.inOut'},at0);
  run(U0,t0,e0,.6,4);run(U4,t4,e4,8.2,3);
  tl.to(l0,{autoAlpha:1,scale:1,duration:.4,ease:'back.out(3)'},4.6).to(ticks,{autoAlpha:1,scale:1,duration:.3,ease:'back.out(2)',stagger:.16},5.4)
   .to(t0,{opacity:.3,duration:.4},8).to(h0,{autoAlpha:0,duration:.2},7.9).to(h4,{autoAlpha:1,duration:.2},8.1).to(l4,{autoAlpha:1,scale:1,duration:.4,ease:'back.out(3)'},11.2)
   .to(demo,{strokeDashoffset:-71,duration:P,ease:'none'},0).fromTo(pulse,{autoAlpha:.8},{autoAlpha:0,duration:1.8,ease:'sine.out',repeat:6},0);
  tl.fromTo(pulse.firstChild,{attr:{r:11}},{attr:{r:19},duration:1.8,ease:'sine.out',repeat:6},0);
  io(tl,g,P);
  m.play(tl,{rest:11.8,draw(){[[t0,U0,h0],[t4,U4,h4]].forEach(([p,U,h])=>{const q=p.getPointAtLength(U.u*p.getTotalLength());at(h,{cx:f1(q.x),cy:f1(q.y)})})}});
 });

 MOTION.gs('consensus-converge',(el,m)=>{
  const P=14,{svg,g}=m.svg(480,240,'Eight robots average with neighbours on three graphs','로봇 8대가 세 가지 그래프에서 이웃과 평균을 맞춥니다');
  const{n,T,Tn,L,C,Pa,tl}=kit(m),NN=8,ST=60,X0=[4,-1,2,7,0,3,-5,1],EPS=.05;
  const adj=[(i,j)=>(j-i+NN)%NN===1||(i-j+NN)%NN===1,()=>true,(i,j)=>(i<4)===(j<4)];
  const traj=adj.map(f=>{const A=X0.map((_,i)=>X0.map((_,j)=>i!==j&&f(i,j)?1:0)),out=[X0];for(let s=0;s<ST;s++){const x=out[s];out.push(x.map((xi,i)=>xi+EPS*A[i].reduce((a,w,j)=>a+w*(x[j]-xi),0)))}return out});
  const pos=X0.map((_,i)=>[112+56*Math.cos(i*Math.PI/4-Math.PI/2),152+56*Math.sin(i*Math.PI/4-Math.PI/2)]);
  const edges=[];for(let i=0;i<NN;i++)for(let j=i+1;j<NN;j++)edges.push([i,j,L(g,pos[i][0],pos[i][1],pos[j][0],pos[j][1],sk(PT,2.5))]);
  const ea=[0,1,2].map(k=>edges.map(e=>adj[k](e[0],e[1])?.75:0));edges.forEach((e,i)=>gsap.set(e[2],{autoAlpha:ea[0][i]}));
  const nodes=pos.map(p=>{C(g,p[0],p[1],13,box(PT));return C(g,p[0],p[1],5,fl(PT))});
  const PX=232,PW=232,vy=v=>206-(v+5.5)*8.6,avg=11/8;
  L(g,PX,206,PX+PW,206,sk(FG,2));const al=L(g,PX,vy(avg),PX+PW,vy(avg),sk(FG,2,'stroke-dasharray:5 5'));
  Tn(g,PX,224,'0',15,mut,'middle');T(g,PX+PW,224,'60 steps','60스텝',15,mut,'end');
  const tr=traj.map(tj=>X0.map((_,i)=>Pa(g,poly(tj.map((_,s)=>PX+s/ST*PW),tj.map(r=>vy(r[i]))),sk(PT,2.5,DASH+';opacity:.85'),{pathLength:1})));
  swap(tl,[['Ring, λ2 = 0.59: slow','고리, λ2 = 0.59: 느림'],['Complete, λ2 = 8: about 10 steps','완전, λ2 = 8: 약 10스텝'],['Two groups, λ2 = 0: never agree','두 무리, λ2 = 0: 합의 못 함']].map(t=>T(g,16,34,t[0],t[1],15,bold)),[0,4.8,8.4]);
  m.caption('Each step a robot moves toward its neighbours\' average. Node size is its value, the dashed line is the average.','한 스텝마다 각 로봇은 이웃의 평균 쪽으로 움직입니다. 원의 크기가 값이고 점선이 평균입니다.');
  m.replayButton();
  // primary: one iteration run per graph (SG[k].v is the step number, the trajectories draw with it); secondary: edges fade between graphs, earlier trajectories dim
  const win=[[1,4.6],[5.4,7.8],[9,11.4]],SG=[{v:0},{v:0},{v:0}];
  win.forEach((w,k)=>tl.to(SG[k],{v:ST,duration:w[1]-w[0],ease:'none'},w[0]).to(tr[k],{strokeDashoffset:0,duration:w[1]-w[0],ease:'none'},w[0]));
  [4.8,8.4].forEach((t,k)=>{edges.forEach((e,i)=>{if(ea[k+1][i]!==ea[k][i])tl.to(e[2],{autoAlpha:ea[k+1][i],duration:.6,ease:'power2.inOut'},t+i*.012)});tl.to(tr[k],{opacity:.18,duration:.4},t)});
  tl.to(al,{strokeDashoffset:-100,duration:P,ease:'none'},0);
  io(tl,g,P);
  m.play(tl,{rest:7.9,draw(t){
   const st=t<4.8?0:t<8.4?1:2,s=SG[st].v,i=Math.min(ST-1,Math.floor(s)),f=s-i,A=traj[st][i],B=traj[st][i+1];
   nodes.forEach((nd,k)=>nd.setAttribute('r',f1(3+9*m.clamp((A[k]+(B[k]-A[k])*f+5)/12))));
  }});
 });

 MOTION.gs('watchdog-stop',(el,m)=>{
  const P=12,{svg,g}=m.svg(480,270,'After the source dies, a torque cut hits the limit and a ramped stop halts 0.15 rad short','소스가 죽으면 토크 차단은 한계에 부딪히고 ramp 정지는 0.15 rad 앞에서 멈춥니다');
  const{n,T,Tn,L,Rc,C,Pa,O,tl}=kit(m),QX=q=>40+(q-.5)*380,YA=150,YB=200,QL=1.5,X1=QX(QL);
  const joint=(y,c)=>{const j=O(g,QX(.5)-26,y-10);Rc(j,0,0,26,20,6,box(FG,3));const r=Rc(j,0,0,26,20,6,box(c,3));gsap.set(r,{autoAlpha:0});return[j,r]};
  const chip=(x,w,en,ko)=>{const r=Rc(g,x,52,w,28,14,box(FG)),b=Rc(g,x,52,w,28,14,box(BAD));gsap.set(b,{autoAlpha:0});T(g,x+w/2,71,en,ko,15,fl(FG),'middle');return b},csR=chip(16,104,'source','소스'),cwR=chip(230,104,'watchdog','워치독');
  L(g,120,66,230,66,sk(LN,3));
  const pulses=Array.from({length:7},()=>{const p=O(g,120,66);C(p,0,0,5,fl(PT));gsap.set(p,{autoAlpha:0});return p});
  const x1=O(g,105.5,65.5);Pa(x1,'M-5.5 -5.5l11 11M5.5 -5.5l-11 11',sk(BAD,3.5));gsap.set(x1,{autoAlpha:0,scale:.3});
  Rc(g,230,90,104,8,4,sk(LN,2));const tb=Rc(g,230,90,0,8,4,fl(BAD)),tl2=T(g,232,114,'timeout 0.05 s','timeout 0.05초',15,mut);gsap.set(tl2,{autoAlpha:0});
  const wall=Rc(g,X1,120,24,92,4,`fill:${BAD};fill-opacity:.12;stroke:${BAD};stroke-width:2.5`),fx=Rc(g,X1,120,24,92,4,fl(BAD,'fill-opacity:.4'));
  for(let i=0;i<3;i++)L(g,X1+2,150+i*24,X1+22,130+i*24,sk(BAD,2,'opacity:.6'));
  [YA,YB].forEach(y=>L(g,40,y,X1,y,sk(LN,3)));
  const[jA,jAr]=joint(YA,BAD),[jB]=joint(YB,OK);
  const lbl=(y,a,b,c)=>[T(g,40,y-24,a[0],a[1],15,bold),T(g,40,y-24,b[0],b[1],15,fl(c,'font-weight:700'))];
  swap(tl,lbl(YA,['torque cut: coasts','토크 차단: 계속 미끄러짐'],['torque cut: hits the limit','토크 차단: 한계에 부딪힘'],BAD),[0,6]);
  swap(tl,lbl(YB,['ramped stop: brakes at 8 rad/s²','ramp 정지: 8 rad/s²로 제동'],['ramped stop: 0.15 rad short','ramp 정지: 한계 0.15 rad 앞'],OK),[0,6.5]);
  const bud=n('g',{},g),segs=[];gsap.set(bud,{autoAlpha:0});
  [[1,1.1,AM,'wait','대기','0.1'],[1.1,1.35,PF,'brake','제동','0.25'],[1.35,1.5,OK,'spare','여유','0.15']].forEach(s=>{const c=(QX(s[0])+QX(s[1]))/2,sg=O(bud,QX(s[0]),224);Rc(sg,0,0,QX(s[1])-QX(s[0]),16,0,fl(s[2],'fill-opacity:.55'));gsap.set(sg,{scaleX:0});segs.push(sg);T(bud,c,237,s[3],s[4],15,fl(FG),'middle');Tn(bud,c,258,s[5],15,mut,'middle')});
  Rc(bud,QX(1),224,QX(1.5)-QX(1),16,0,sk(FG,2));T(bud,QX(1)-8,237,'room 0.5 rad','여유 공간 0.5 rad',15,mut,'end');
  T(g,16,264,'10× slow motion','10배 느리게',15,mut);
  swap(tl,[['Source sends commands and heartbeat','소스가 명령과 heartbeat를 보냄'],['Source dies: cut torque vs ramped stop','소스 소멸: 토크 차단과 ramp 정지'],['Ramp stops 0.15 rad short of the limit','ramp는 한계 0.15 rad 앞에서 정지'],['Longest safe timeout = 0.125 s','허용되는 최대 timeout = 0.125초']].map(t=>T(g,16,34,t[0],t[1],15,bold)),[0,3.5,6.5,8.7]);
  m.caption('Lesson values: 2 rad/s, brake 8 rad/s², limit 1.5 rad, timeout 0.05 s. Longest timeout = (0.5 - 0.25) / 2 = 0.125 s.','레슨의 값입니다. 2 rad/s, 제동 8 rad/s², 한계 1.5 rad, timeout 0.05초. 최대 timeout = (0.5 - 0.25) / 2 = 0.125초.');
  m.replayButton();
  // 10x slow motion. primary: both joints slide at 2 rad/s (linear); the ramped one brakes at 8 rad/s² (power1.out = t^2 curve = constant deceleration; 0.25 rad in 2.5 s from 0.2 rad/s); the cut one hits the wall and recoils.
  // secondary: heartbeats stop, the timeout bar fills, chips turn red; the budget bar builds up
  const xa=q=>QX(q)-26;
  tl.to(pulses,{autoAlpha:1,duration:.01,stagger:.4},1).to(pulses,{x:230,duration:1,ease:'none',stagger:.4},1).to(pulses,{autoAlpha:0,duration:.01,stagger:.4},2)
   .to(x1,{autoAlpha:1,scale:1,duration:.4,ease:'back.out(3)'},3.5).to(csR,{autoAlpha:1,duration:.15},3.5).to(tl2,{autoAlpha:1,duration:.3},3.5).to(tb,{attr:{width:104},duration:.5,ease:'none'},3.5).to(cwR,{autoAlpha:1,duration:.15},4)
   .to([jA,jB],{x:xa(1.1),duration:3,ease:'none'},1).to(jA,{x:xa(QL),duration:2,ease:'none'},4).to(jB,{x:xa(1.35),duration:2.5,ease:'power1.out'},4)
   .to(jA,{x:'-=10',duration:.12},6).to(jA,{x:'+=10',duration:.5,ease:'elastic.out(1,.4)'},6.12).to(jAr,{autoAlpha:1,duration:.15},6)
   .set(fx,{autoAlpha:1},6).to(fx,{autoAlpha:0,duration:.5,ease:'power2.in'},6)
   .to(bud,{autoAlpha:1,duration:.4},6.7).to(segs,{scaleX:1,duration:.5,stagger:.15},6.7);
  gsap.set(fx,{autoAlpha:0});
  io(tl,g,P);m.play(tl,{rest:9.5});
 });
})();
