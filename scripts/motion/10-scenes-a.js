// phase scenes 00-05 (GSAP timelines) + helpers MOTION.__h for 11-concepts-a.js
(()=>{
const A=window.MOTION,NS='http://www.w3.org/2000/svg',PI=Math.PI,sin=Math.sin,cos=Math.cos;
const E=(p,t,a,s)=>{const x=document.createElementNS(NS,t);for(const k in a)x.setAttribute(k,a[k]);if(s)x.setAttribute('style',s);p.appendChild(x);return x};
const SK='fill:none;stroke:var(--fg);stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round',BXS='fill:var(--card);stroke:var(--fg);stroke-width:2.5';
const f1=v=>v.toFixed(1);
const TF=(e,x,y,r,s)=>e.setAttribute('transform','translate('+f1(x)+' '+f1(y)+')'+(r?' rotate('+f1(r)+')':'')+(s!=null&&s!==1?' scale('+s.toFixed(3)+')':''));
const G=(p,x,y,r)=>{const g=E(p,'g',{});gsap.set(g,{x:x||0,y:y||0,rotation:r||0,transformOrigin:'0 0'});return g};
const BX=(p,x,y,w,h,r,s)=>E(p,'rect',{x,y,width:w,height:h,rx:r==null?12:r},s||BXS);
const LB=m=>({add(p,x,y,en,ko,s,z,a){const e=E(p,'text',{x,y,'font-size':z||20,'text-anchor':a||'start'},'fill:var(--mut);font-weight:600;'+(s||''));const f=()=>{e.textContent=m.t(en,ko)};f();m.onTheme(f);return e}});
const LK=(p,w)=>{const a=E(p,'line',{},'stroke:var(--fg);stroke-width:'+(w+5)+';stroke-linecap:round'),b=E(p,'line',{},'stroke:var(--card);stroke-width:'+w+';stroke-linecap:round');return(x1,y1,x2,y2)=>{for(const e of[a,b]){e.setAttribute('x1',f1(x1));e.setAttribute('y1',f1(y1));e.setAttribute('x2',f1(x2));e.setAttribute('y2',f1(y2))}}};
const LL=(p,x,y,w)=>[E(p,'line',{x2:x,y2:y},'stroke:var(--fg);stroke-width:'+(w+5)+';stroke-linecap:round'),E(p,'line',{x2:x,y2:y},'stroke:var(--card);stroke-width:'+w+';stroke-linecap:round')];
const PL=(p,d,s)=>{const e=E(p,'path',{d,pathLength:1},s+';stroke-dasharray:1');gsap.set(e,{strokeDashoffset:1,autoAlpha:0});return e};
const DR=(tl,e,t,d,ez)=>tl.set(e,{autoAlpha:1},t).to(e,{strokeDashoffset:0,duration:d,ease:ez||'power2.inOut'},t);
const PATH=(tl,e,pts,t0,T)=>{const L=pts.slice(1).map((q,i)=>Math.hypot(q[0]-pts[i][0],q[1]-pts[i][1])),S=L.reduce((a,b)=>a+b);let t=t0;L.forEach((l,i)=>{const d=T*l/S;tl.to(e,{x:pts[i+1][0],y:pts[i+1][1],duration:d,ease:L.length==1?'power1.inOut':i?i==L.length-1?'power1.out':'none':'power1.in'},t);t+=d})};
// ambient motes (wrap by modifier, sine opacity)
const AM=(tl,p,n,W,H,P)=>{for(let i=0;i<n;i++){const k=1+i%2,u0=i/n,x0=(i*97.3)%W,c=E(p,'circle',{r:2+i%3*.8},'fill:var(--pl)');gsap.set(c,{x:x0,y:H-u0*H,opacity:0});
 tl.to(c,{y:H-(u0+k)*H,x:x0+9*k,duration:P,ease:'none',modifiers:{y:v=>{v=parseFloat(v);return H-(((H-v)%H)+H)%H}}},0).to(c,{opacity:.55,duration:P,ease:q=>sin(((u0+k*q)%1)*PI)},0)}};
const BO=p=>{const g=G(p),s=G(g),k=E(s,'g',{transform:'translate(-32 -61)'});E(k,'path',{d:'M32 11V4'},SK);E(k,'circle',{cx:32,cy:4,r:3},'fill:var(--pf);stroke:var(--fg);stroke-width:2');E(k,'rect',{x:4.5,y:22,width:6,height:11,rx:3},BXS);E(k,'rect',{x:53.5,y:22,width:6,height:11,rx:3},BXS);BX(k,19,46,26,15,6);BX(k,10,11,44,34,13);E(k,'rect',{x:16,y:17,width:32,height:22,rx:9},'fill:var(--ink0)');const ey=G(k);[26,38].forEach(x=>E(ey,'circle',{cx:x,cy:27,r:3.4},'fill:var(--pf)'));E(k,'path',{d:'M28.5 33.5q3.5 2.8 7 0'},'fill:none;stroke:var(--pf);stroke-width:2.6;stroke-linecap:round');return{g,s,ey}};
A.__h={E,SK,BXS,f1,TF,G,BX,LB,LK,LL,PL,DR,PATH};
// scene shell; build(m,root,labels,tl) adds the story to tl and may return draw(t)
const SC=(n,en,ko,P,rest,build)=>A.gs('scene-0'+n,(el,m)=>{const{g}=m.svg(640,220,en,ko),lb=LB(m),tl=m.timeline();
 E(g,'rect',{x:0,y:192,width:640,height:28},'fill:var(--pb)');const r=E(g,'g',{});AM(tl,r,8,640,200,P);
 const d=build(m,r,lb,tl);tl.fromTo(r,{opacity:0},{opacity:1,duration:.3,ease:'none'},0).to(r,{opacity:0,duration:.5,ease:'none'},P-.5);m.play(tl,{rest,draw:d})});

SC(0,'A toolbox opens, a Python line runs, and a robot arm wakes up','도구 상자가 열리고 파이썬 한 줄이 실행되며 로봇 팔이 깨어납니다',10,9,(m,r,lb,tl)=>{
BX(r,40,140,90,50,10);E(r,'rect',{x:52,y:160,width:66,height:8,rx:4},'fill:var(--pf)');
const IP=[[92,88],[130,64],[168,88]],ic=IP.map((q,i)=>{const g=G(r,85,140);
 if(i==0){E(g,'circle',{r:9},'fill:var(--card);stroke:var(--pf);stroke-width:6;stroke-dasharray:5.7 5.7');E(g,'circle',{r:3},'fill:var(--fg)')}
 else if(i==1)E(g,'rect',{x:-10,y:-10,width:20,height:20,rx:5},'fill:var(--card);stroke:var(--pd);stroke-width:3.5');
 else E(g,'path',{d:'M-10 0L-5-9H5L10 0L5 9H-5Z'},'fill:var(--card);stroke:var(--fg);stroke-width:3.5;stroke-linejoin:round');return g});
const lid=G(r,40,140);BX(lid,0,-20,90,20,7);E(lid,'rect',{x:10,y:-12,width:70,height:5,rx:2.5},'fill:var(--pf)');
BX(r,215,34,235,120,14,'fill:var(--ink0)');[0,1,2].forEach(i=>E(r,'circle',{cx:232+i*14,cy:50,r:4},'fill:var(--mut);opacity:.7'));
const TT=(y,s,id)=>{const k=E(E(r,'clipPath',{id}),'rect',{x:229,y:y-20,width:0,height:28});E(r,'text',{x:231,y,'font-size':20,'clip-path':'url(#'+id+')'},'fill:#e8eff2;font-family:var(--mono);font-weight:600').textContent=s;return k};
const k1=TT(92,'$ python3','c00a'),k2=TT(124,'>>> import numpy','c00b'),cu=G(r,231,75),cr=E(cu,'rect',{width:10,height:20},'fill:var(--pf)'),ck=G(r,438,115),cp=PL(ck,'M-8 0l5 6 11-12','fill:none;stroke:var(--pf);stroke-width:4;stroke-linecap:round;stroke-linejoin:round');
gsap.set(cu,{autoAlpha:0});
const bx=540,by=186,L1=64,L2=52;E(r,'rect',{x:bx-24,y:by-6,width:48,height:10,rx:5},BXS);
const a1=G(r,bx,by,62);LL(a1,0,-L1,9);const a2=G(a1,0,-L1,95);LL(a2,0,-L2,8);E(a1,'circle',{r:7},'fill:var(--pf)');E(a2,'circle',{r:6},'fill:var(--pf)');
const led=E(a2,'circle',{cy:-L2,r:7},'fill:var(--line);stroke:var(--fg);stroke-width:2.5'),gl=E(a2,'circle',{cy:-L2,r:7},'fill:var(--pf)'),rg=E(a2,'circle',{cy:-L2,r:8},'fill:none;stroke:var(--pf);stroke-width:3'),z=E(r,'text',{x:600,y:186,'font-size':22,'font-weight':700},'fill:var(--mut)');z.textContent='z z';
gsap.set([gl,rg],{autoAlpha:0});
tl.fromTo(z,{y:0,autoAlpha:.9},{y:-14,autoAlpha:0,duration:1.4,ease:'sine.out',repeat:3},0)
 .to(lid,{rotation:-100,duration:.9,ease:'back.out(1.4)'},.3)
 .fromTo(ic,{x:85,y:140,scale:.4,autoAlpha:0},{x:i=>IP[i][0],y:i=>IP[i][1],scale:1.5,autoAlpha:1,duration:.9,ease:'back.out(1.7)',stagger:.3},1)
 .to(ic[0],{rotation:360,duration:8.5,ease:'none'},1.2).to(ic[1],{rotation:10,duration:1.4,ease:'sine.inOut',yoyo:true,repeat:4},1.9).to(ic[2],{rotation:-10,duration:1.4,ease:'sine.inOut',yoyo:true,repeat:4},2.1)

ic.forEach((g,i)=>tl.to(g,{y:'-=4',duration:1.2,ease:'sine.inOut',yoyo:true,repeat:5},2.2+i*.25));tl
 .set(cu,{autoAlpha:1},2).to(cu,{x:339,duration:.8,ease:'steps(9)'},2).to(k1,{attr:{width:109},duration:.8,ease:'steps(9)'},2)
 .set(cu,{x:231,y:107},3.2).to(cu,{x:423,duration:1.4,ease:'steps(16)'},3.3).to(k2,{attr:{width:193},duration:1.4,ease:'steps(16)'},3.3)
 .to(cr,{autoAlpha:.15,duration:.3,ease:'sine.inOut',yoyo:true,repeat:9},2).to(cu,{autoAlpha:0,duration:.2},5.2)
 .fromTo(ck,{scale:.6},{scale:1,duration:.5,ease:'back.out(2.5)'},4.9);DR(tl,cp,4.9,.4,'power2.out');
tl.to([a1,a2],{rotation:'+=5',duration:.25,ease:'power2.out'},4.9)
 .to(a1,{rotation:-12,duration:1.2,ease:'back.out(1.5)'},5.2).to(a2,{rotation:50,duration:2.2,ease:'elastic.out(1,.35)'},5.2)
 .to(gl,{autoAlpha:1,duration:1,ease:'power2.out'},5.2).set(rg,{autoAlpha:1},5.4).to(rg,{attr:{r:30},autoAlpha:0,duration:1.2,ease:'power2.out'},5.4);
});

SC(1,'Two coordinate frames: the camera sees a cup, and its position is handed over to the base frame','두 좌표계: 카메라가 본 컵의 위치를 베이스 좌표계로 넘깁니다',10,9,(m,r,lb,tl)=>{
const FR=(x,y,l)=>{const g=G(r,x,y);E(g,'line',{x2:l},'stroke:var(--pf);stroke-width:4;stroke-linecap:round');E(g,'line',{y2:-l},'stroke:var(--pd);stroke-width:4;stroke-linecap:round');E(g,'path',{d:'M'+l+' 0l-10-6v12zM0 -'+l+'l-6 10h12z'},'fill:var(--fg)');E(g,'circle',{r:5},'fill:var(--card);stroke:var(--fg);stroke-width:2.5');return g};
const bs=FR(90,170,70),cm=FR(340,150,56),cp=G(r,401.2,63.1);
const leg=E(r,'line',{x1:90,y1:170,x2:340,y2:150},'stroke:var(--mut);stroke-width:3;stroke-dasharray:6 6;stroke-linecap:round'),
 lg2=PL(cm,'M0 0H100V-36','fill:none;stroke:var(--pd);stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round'),
 arr=PL(r,'M90 170L380 70','fill:none;stroke:var(--fg);stroke-width:4;stroke-linecap:round'),hd=G(r,384,68.8,-19);E(hd,'path',{d:'M-10-6L2 0L-10 6z'},'fill:var(--fg)');
E(cp,'path',{d:'M-10 -11h20l-3 22h-14z'},BXS+';stroke-linejoin:round');E(cp,'path',{d:'M10 -5q9 1 8 6q-1 5-9 5'},SK);
const dot=G(r,90,170);E(dot,'circle',{r:7},'fill:var(--pf);stroke:var(--card);stroke-width:2.5');gsap.set([dot,leg,hd],{autoAlpha:0});
const bl=lb.add(r,90,212,'base','베이스',null,20,'middle'),cl=lb.add(r,340,180,'camera','카메라',null,20,'middle'),pl=lb.add(r,401,34,'cup','컵',null,20,'middle');
const s1=lb.add(r,620,212,'cup in camera frame','카메라 기준 컵 위치','fill:var(--pt)',20,'end'),s2=lb.add(r,620,212,'cup in base frame','베이스 기준 컵 위치','fill:var(--fg)',20,'end');
const up=(e,t)=>tl.fromTo(e,{autoAlpha:0,y:8},{autoAlpha:1,y:0,duration:.5,ease:'power3.out'},t);
tl.fromTo(bs,{scale:.5,autoAlpha:0},{scale:1,autoAlpha:1,duration:.9,ease:'back.out(1.7)'},.2);up(bl,.5);
tl.fromTo(cm,{scale:.5,autoAlpha:0},{scale:1,autoAlpha:1,duration:.9,ease:'back.out(1.7)'},1.2).to(cm,{rotation:-35,duration:1.4,ease:'power3.out'},1.2);up(cl,1.6);
tl.to(leg,{autoAlpha:1,duration:.8,ease:'power2.out'},1.6)
 .fromTo(cp,{autoAlpha:0,scale:.5,y:49},{autoAlpha:1,scale:1,y:63.1,duration:.7,ease:'back.out(2)'},3);up(pl,3.2);
DR(tl,lg2,3.6,1.4);up(s1,3.4);tl.to(s1,{autoAlpha:0,y:-6,duration:.3,ease:'power2.in'},5.3);
tl.set(dot,{autoAlpha:1},5.2);PATH(tl,dot,[[90,170],[340,150],[401.2,63.1]],5.2,1.6);tl.to(dot,{autoAlpha:0,scale:.5,duration:.2},6.8);
DR(tl,arr,6.4,1.2,'power2.out');tl.fromTo(hd,{scale:.3,autoAlpha:0},{scale:1,autoAlpha:1,duration:.35,ease:'back.out(3)'},7.3);up(s2,5.6);
});

SC(2,'A two-link arm reaches a target, flips its elbow at full stretch, and folds when the target comes close','2링크 팔이 목표를 향해 뻗고 완전히 펴진 지점에서 팔꿈치를 뒤집고 목표가 가까워지면 접힙니다',11.5,7.8,(m,r,lb,tl)=>{
const bx=330,by=190,L1=85,L2=70,th=62*PI/180,R=L1+L2,pr={D:110,s:1,sw:0};
const wc=E(r,'circle',{cx:bx,cy:by,r:R},'fill:none;stroke:var(--line);stroke-width:2.5;stroke-dasharray:3 9;stroke-linecap:round');
const gh=E(r,'polyline',{},'fill:none;stroke:var(--pl);stroke-width:5;stroke-dasharray:2 9;stroke-linecap:round;stroke-linejoin:round');
BX(r,bx-26,by-8,52,14,7);
const k1=LK(r,10),k2=LK(r,9),tg=E(r,'g',{}),ti=G(tg);E(ti,'circle',{r:15},'fill:none;stroke:var(--pf);stroke-width:3.5');E(ti,'circle',{r:4},'fill:var(--pf)');
const j0=E(r,'circle',{r:8},'fill:var(--pf)'),j1=E(r,'circle',{r:7},'fill:var(--pf)'),tp=E(r,'circle',{r:6},'fill:var(--pd);stroke:var(--card);stroke-width:2');
const st=[['elbow up','팔꿈치 위'],['stretched: elbow flips','쭉 폄: 팔꿈치 뒤집힘'],['elbow down','팔꿈치 아래'],['folded: near the inner limit','접힘: 안쪽 한계 근처']].map(q=>lb.add(r,24,44,q[0],q[1],'fill:var(--fg)',20));
tl.to(wc,{strokeDashoffset:-48,duration:11.5,ease:'none'},0).to(ti,{scale:1.12,duration:.5,ease:'sine.inOut',yoyo:true,repeat:21},0)
 .to(pr,{keyframes:{sw:[0,.1,0,-.1,0,.1,0,-.1,0],easeEach:'sine.inOut'},duration:11.5,ease:'none'},0)
 .to(pr,{D:103,duration:.35,ease:'power2.out'},.5).to(pr,{D:155,duration:1.15,ease:'power3.inOut'},.85).set(pr,{s:-1},2.3)
 .to(pr,{D:110,duration:2,ease:'power2.inOut'},2.6).to(pr,{D:24,duration:2.4,ease:'power3.inOut'},5).to(pr,{D:110,duration:1.8,ease:'power2.inOut'},8.6);
const e=[0,0],g=[0,0];
return()=>{const D=pr.D,s=pr.s,ang=th+pr.sw,tx=bx+D*cos(ang),ty=by-D*sin(ang),al=Math.acos(Math.max(-1,Math.min(1,(L1*L1+D*D-L2*L2)/(2*L1*D))));
 const pose=(q,o)=>{const a=ang+q*al;o[0]=bx+L1*cos(a);o[1]=by-L1*sin(a)};pose(s,e);pose(-s,g);
 k1(bx,by,e[0],e[1]);k2(e[0],e[1],tx,ty);gh.setAttribute('points',bx+','+by+' '+f1(g[0])+','+f1(g[1])+' '+f1(tx)+','+f1(ty));
 for(const[q,x,y]of[[j0,bx,by],[j1,e[0],e[1]],[tp,tx,ty]]){q.setAttribute('cx',f1(x));q.setAttribute('cy',f1(y))}
 TF(tg,tx,ty);const k=D>=R-3?1:D<=45?3:s>0?0:2;st.forEach((q,i)=>q.setAttribute('opacity',i===k?1:0))}});

SC(3,'An arm swings a payload after a push and settles like a spring and damper','팔이 밀린 뒤 페이로드를 흔들다가 스프링과 댐퍼처럼 가라앉습니다',10.5,8.5,(m,r,lb,tl)=>{
const sx=170,sy=44,L=110,A0=.66,sig=.99,wd=4.38,y0=112,PX=336,PW=275,pr={a:0,u:0};
BX(r,110,26,120,12,6);
const th=u=>A0*Math.exp(-sig*u)*(cos(wd*u)+sig/wd*sin(wd*u));
let c='';for(let i=0;i<=64;i++){const u=i/64*6.4;c+=(i?'L':'M')+f1(PX+4+u/6.4*PW)+' '+f1(y0-th(u)/A0*52)}
E(r,'path',{d:'M'+PX+' 56V176M'+PX+' '+y0+'H'+(PX+PW+14)},'fill:none;stroke:var(--line);stroke-width:2.5;stroke-linecap:round');
const tc=q=>'M'+(PX+4)+' '+(y0+q)+'C'+(PX+60)+' '+(y0+q)+' '+(PX+PW*.5)+' '+y0+' '+(PX+PW+4)+' '+y0,tol=E(r,'path',{d:tc(-52)+tc(52)},'fill:none;stroke:var(--pl);stroke-width:2.5;stroke-dasharray:3 6;stroke-linecap:round');
const ck=E(E(r,'clipPath',{id:'c03'}),'rect',{x:PX,y:40,width:0,height:150});
const cv=E(r,'path',{d:c,'clip-path':'url(#c03)'},'fill:none;stroke:var(--pt);stroke-width:4;stroke-linecap:round;stroke-linejoin:round'),hd=E(r,'circle',{r:6},'fill:var(--pt);stroke:var(--card);stroke-width:2');gsap.set(hd,{autoAlpha:0});
const sp=E(r,'polyline',{},'fill:none;stroke:var(--pd);stroke-width:3;stroke-linejoin:round;stroke-linecap:round'),dm=E(r,'g',{});E(dm,'path',{d:'M0 0H40'},'fill:none;stroke:var(--fg);stroke-width:2.5');BX(dm,40,-8,44,16,4);const rod=E(dm,'path',{},SK);
E(r,'rect',{x:22,y:60,width:8,height:104,rx:4},'fill:var(--fg)');
const ln=LK(r,9);E(r,'circle',{cx:sx,cy:sy,r:8},'fill:var(--pf)');const pl=E(r,'circle',{r:16},'fill:var(--pf);stroke:var(--fg);stroke-width:2.5'),ph=E(r,'g',{}),pi=G(ph);E(pi,'path',{d:'M-34 0H-6M-14 -8L-5 0L-14 8'},'fill:none;stroke:var(--pd);stroke-width:4;stroke-linecap:round;stroke-linejoin:round');gsap.set(pi,{autoAlpha:0});
lb.add(r,PX+PW+10,y0-10,'target','목표',null,20,'end');lb.add(r,PX+PW+10,y0+30,'time','시간',null,20,'end');lb.add(r,PX+6,50,'angle','각도',null,20);
tl.to(tol,{strokeDashoffset:-72,duration:10.5,ease:'none'},0)
 .to(pr,{a:-.07,duration:.3,ease:'power2.out'},.45).to(pr,{a:A0,duration:.8,ease:'power3.inOut'},.8)
 .fromTo(pi,{autoAlpha:0,x:-10},{autoAlpha:1,x:0,duration:.3,ease:'power3.out'},.4).to(pi,{autoAlpha:0,x:6,duration:.25,ease:'power2.in'},1.45)
 .to(pr,{u:6.4,duration:6.4,ease:'none'},1.6).to(ck,{attr:{width:PW+16},duration:6.4,ease:'none'},1.6).set(hd,{autoAlpha:1},1.6);
return()=>{const u=pr.u,a=u>0?th(u):pr.a,px=sx+L*sin(a),py=sy+L*cos(a);ln(sx,sy,px,py);pl.setAttribute('cx',f1(px));pl.setAttribute('cy',f1(py));TF(ph,px-6,py);
 let s='30,'+f1(py-14);const x1=px-20;for(let i=1;i<=9;i++)s+=' '+f1(30+(x1-30)*i/10)+','+f1(py-14+(i%2?-8:8));sp.setAttribute('points',s+' '+f1(x1)+','+f1(py-14));
 TF(dm,30,py+14);rod.setAttribute('d','M50 -8V8M50 0H'+f1(px-50));
 const hu=Math.max(0,Math.min(6.4,u));hd.setAttribute('cx',f1(PX+4+hu/6.4*PW));hd.setAttribute('cy',f1(y0-th(hu)/A0*52))}});

SC(4,'A motor turns a gearbox, and an encoder disc turns slots into a train of pulses','모터가 감속기를 돌리고 엔코더 디스크가 슬롯을 펄스 신호로 바꿉니다',10,6,(m,r,lb,tl)=>{
const ea=m.ease,pw=12,CW=24,pr={s:0};
const om=t=>12*ea.inOut(ea.seg(t,.8,2.6))*(1-ea.inOut(ea.seg(t,7.2,9))),tab=[0];for(let i=0;i<600;i++)tab.push(tab[i]+om(i/60)/60);
const E4=p=>{const x=Math.min(1,Math.max(0,p))*600,i=Math.min(599,Math.floor(x));return(tab[i]+(tab[i+1]-tab[i])*(x-i))/tab[600]};
const D1=tab[600]*180/PI,D2=-D1*20/42,S=-D2/360*24*CW;
const gM=E(r,'g',{}),gG=E(r,'g',{}),gE=E(r,'g',{});
E(E(gE,'clipPath',{id:'c04a'}),'rect',{x:400,y:40,width:230,height:110});
BX(gM,22,78,78,64,12);E(gM,'rect',{x:96,y:104,width:34,height:12,rx:3},'fill:var(--fg)');const mled=E(gM,'circle',{cx:42,cy:96,r:6,opacity:.35},'fill:var(--pf)');E(gM,'path',{d:'M52 108h38M52 120h38'},'stroke:var(--line);stroke-width:3;stroke-linecap:round');
const GR=(cx,cy,rr,n)=>{const g=G(gG,cx,cy),q=6.283*(rr+2)/(2*n);E(g,'circle',{r:rr+2},'fill:none;stroke:var(--fg);stroke-width:6;stroke-dasharray:'+f1(q)+' '+f1(q));E(g,'circle',{r:rr-2},BXS);E(g,'circle',{cx:rr*.55,r:4},'fill:var(--pf)');return g};
const g1=GR(150,110,18,8),g2=GR(212,110,40,22);E(gG,'path',{d:'M252 110H330'},SK);
const dsc=G(gE,330,110);E(dsc,'circle',{r:34},BXS);E(dsc,'circle',{r:26},'fill:none;stroke:var(--pd);stroke-width:12;stroke-dasharray:'+f1(6.283*26/48)+' '+f1(6.283*26/48));E(dsc,'circle',{cx:12,r:4},'fill:var(--pf)');
BX(gE,321,58,18,12,3);const rd=E(gE,'rect',{x:323,y:60,width:14,height:8,rx:2},'fill:var(--line)');
const mw=(y,x0)=>{let d='M'+(-CW)+' '+(y+22);for(let k=-1;k<11;k++){const x=k*CW;d+='V'+y+'H'+(x+pw)+'V'+(y+22)+'H'+(x+CW)}const e=E(E(gE,'g',{'clip-path':'url(#c04a)'}),'path',{d},'fill:none;stroke:var(--pt);stroke-width:3.5;stroke-linejoin:round');gsap.set(e,{x:x0});return e};
const wa=mw(50,400),wb=mw(104,400+pw/2);wb.style.stroke='var(--fg)';
const wire=E(gE,'path',{d:'M339 64C370 64 380 72 400 72'},'fill:none;stroke:var(--line);stroke-width:2.5;stroke-dasharray:3 6;stroke-linecap:round');
lb.add(gM,60,212,'motor','모터',null,20,'middle');lb.add(gG,190,212,'gearbox','감속기',null,20,'middle');lb.add(gE,330,212,'encoder','엔코더',null,20,'middle');lb.add(gE,515,212,'pulses','펄스',null,20,'middle');lb.add(gE,392,78,'A','A','fill:var(--pt)',20,'end');lb.add(gE,392,132,'B','B','fill:var(--fg)',20,'end');
const wrap=b=>v=>b+(((parseFloat(v)-b)%CW)+CW)%CW;
tl.fromTo([gM,gG,gE],{y:14,autoAlpha:0},{y:0,autoAlpha:1,duration:.7,ease:'power3.out',stagger:.2},.2)
 .to(wire,{strokeDashoffset:-90,duration:10,ease:'none'},0)
 .to(g1,{rotation:D1,duration:10,ease:E4},0).to([g2,dsc],{rotation:D2,duration:10,ease:E4},0)
 .to(wa,{x:400+S,duration:10,ease:E4,modifiers:{x:wrap(400)}},0).to(wb,{x:400+pw/2+S,duration:10,ease:E4,modifiers:{x:wrap(400)}},0).to(pr,{s:S,duration:10,ease:E4},0)
 .to(mled,{opacity:1,duration:1.8,ease:'power2.inOut'},.8).to(mled,{opacity:.35,duration:1.8,ease:'power2.inOut'},7.2);
return()=>{rd.setAttribute('style','fill:'+((((-pr.s)%CW)+CW)%CW<pw?'var(--pf)':'var(--line)'))}});

SC(5,'A camera node publishes messages; the planner receives them, but messages for the viewer fall through a broken link','카메라 노드가 메시지를 발행합니다. 플래너는 받지만 뷰어로 가는 메시지는 끊긴 연결에서 떨어집니다',10,3.55,(m,r,lb,tl)=>{
const EM=[[.9,0],[2.2,1],[3.6,0],[5,1],[6.4,0],[7.8,1]],P1=[[134,110],[230,110],[230,140],[450,140]],P2=[[134,110],[230,110],[230,52],[350,52]];
const W='fill:none;stroke:var(--fg);stroke-width:3;stroke-linecap:round;stroke-linejoin:round';
E(r,'path',{d:'M134 110H230V140H450M230 110V52H350'},W);E(r,'path',{d:'M410 52H450'},W+';stroke-dasharray:3 7');
BX(r,14,85,120,50,12);BX(r,450,112,140,56,12);const pf=BX(r,450,112,140,56,12,'fill:var(--pf);stroke:none');BX(r,450,24,140,56,12,BXS+';stroke-dasharray:7 6');
lb.add(r,74,117,'camera','카메라',null,20,'middle');lb.add(r,520,146,'planner','플래너',null,20,'middle');lb.add(r,520,58,'viewer','뷰어',null,20,'middle');lb.add(r,140,98,'/image','/image','font-family:var(--mono)',20);
const ms=EM.map(()=>{const e=E(r,'rect',{x:-11,y:-8,width:22,height:16,rx:5},'fill:var(--pd);stroke:var(--card);stroke-width:2');gsap.set(e,{x:134,y:110,autoAlpha:0,scale:.6,transformOrigin:'0 0'});return e}),bo=BO(r),pu=BX(r,14,85,120,50,12,'fill:var(--pf)');
gsap.set([pf,pu],{autoAlpha:0});gsap.set(bo.g,{x:392,y:208,scale:.9});gsap.set(bo.ey,{x:2});
tl.to(bo.g,{y:'-=3',duration:1.3,ease:'sine.inOut',yoyo:true,repeat:5},0);
EM.forEach(([t0,pl],i)=>{const e=ms[i];
 tl.to(e,{autoAlpha:1,scale:1,duration:.15,ease:'back.out(2.5)'},t0).set(pu,{autoAlpha:.5},t0).to(pu,{autoAlpha:0,duration:.35,ease:'power2.out'},t0);
 if(!pl){PATH(tl,e,P1,t0,1.5);tl.to(e,{autoAlpha:0,scale:.6,duration:.15,ease:'power2.in'},t0+1.45).set(pf,{autoAlpha:.6},t0+1.5).to(pf,{autoAlpha:0,duration:.4,ease:'power2.out'},t0+1.5)}
 else{PATH(tl,e,P2,t0,1.1);const a=t0+1.1;
  tl.to(e,{x:'+=36',rotation:128,duration:.8,ease:'none'},a).to(e,{y:'+=110',duration:.8,ease:'power2.in'},a).set(e,{autoAlpha:0},a+.8)
   .to(bo.s,{scaleY:1.07,duration:.12,ease:'power2.out',yoyo:true,repeat:1},a+.58).to(bo.ey,{x:0,y:-2,duration:.15,ease:'power2.out'},a+.55).to(bo.ey,{x:2,y:0,duration:.2,ease:'power2.inOut'},a+.75)}});
});
})();
