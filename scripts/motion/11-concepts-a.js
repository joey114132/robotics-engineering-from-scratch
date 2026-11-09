// concept animations as GSAP timelines: rotation-frames, fk-chain, singularity-fold, pubsub-flow (helpers come from 10-scenes-a.js)
(()=>{
const A=window.MOTION,Hh=A.__h;if(!Hh)return;
const{E,f1,TF,G,BX,LB,LK,LL,PL,DR,PATH,BXS}=Hh,PI=Math.PI,sin=Math.sin,cos=Math.cos;
const CP=(name,en,ko,P,rest,ce,ck,rp,build)=>A.gs(name,(el,m)=>{const{g}=m.svg(480,270,en,ko),lb=LB(m),r=E(g,'g',{}),tl=m.timeline(),d=build(m,r,lb,tl);m.caption(ce,ck);
 if(rp){m.replayButton();const b=el.lastChild;b.style.position='static';b.style.margin='0 16px 14px'}
 tl.fromTo(r,{opacity:0},{opacity:1,duration:.3,ease:'none'},0).to(r,{opacity:0,duration:.5,ease:'none'},P-.5);m.play(tl,{rest,draw:d})});
const TX=(lb,r,x,y,en,ko,s,z,a)=>lb.add(r,x,y,en,ko,s,z||16,a);
const MO='font-family:var(--mono);fill:var(--fg)',UP=(tl,e,t)=>tl.fromTo(e,{autoAlpha:0,y:6},{autoAlpha:1,y:0,duration:.35,ease:'power3.out'},t),DN=(tl,e,t)=>tl.to(e,{autoAlpha:0,y:-6,duration:.2,ease:'power2.in'},t);

CP('rotation-frames','Two turns of 90 degrees, about x then z and about z then x, end in different places','90도 회전 두 번을 x 다음 z 순서와 z 다음 x 순서로 하면 끝나는 자리가 다릅니다',13,10.5,
'The same two quarter turns in a different order: x then z sends (1, 0, 0) to (0, 1, 0), z then x sends it to (0, 0, 1). The thick cyan arrow is the body x axis.','같은 90도 회전 두 번도 순서가 다르면 결과가 다릅니다. x 다음 z는 (1, 0, 0)을 (0, 1, 0)으로, z 다음 x는 (0, 0, 1)로 보냅니다. 굵은 화살표가 몸체 x 축입니다.',true,(m,r,lb,tl)=>{
const u=64,c3=.866,oy=165,col=['var(--pf)','var(--pd)','var(--mut)'],wd=[6,4,4],rd=[8,5,5],pr={a1:0,a2:0};
const pj=(v,cx,o)=>{o[0]=cx+(v[0]-v[1])*c3*u;o[1]=oy+(v[0]+v[1])*.5*u-v[2]*u},ap=(ax,a,v,o)=>{const c=cos(a),s=sin(a);if(ax===0){o[0]=v[0];o[1]=v[1]*c-v[2]*s;o[2]=v[1]*s+v[2]*c}else{o[0]=v[0]*c-v[1]*s;o[1]=v[0]*s+v[1]*c;o[2]=v[2]}};
const V=[[1,0,0],[0,1,0],[0,0,1]],t1=[0,0,0],t2=[0,0,0],pp=[0,0];
const PN=(cx,x1,x2,tE,tK,s1E,s1K,s2E,s2K,rsE,rsK)=>{
 const wl=[],hl=[],fx=[];
 V.forEach((v,i)=>{pj([v[0]*1.3,v[1]*1.3,v[2]*1.3],cx,pp);const ln=c=>E(r,'line',{x1:cx,y1:oy,x2:pp[0],y2:pp[1]},'stroke:'+c+';stroke-width:3;stroke-linecap:round');wl.push(ln('var(--line)'));hl.push(ln('var(--pd)'));fx.push(TX(lb,r,pp[0]+[8,-8,0][i],pp[1]+[16,16,-8][i],'xyz'[i],'xyz'[i],null,15,['start','end','middle'][i]))});
 pj(V[0],cx,pp);const gh=E(r,'circle',{cx:pp[0],cy:pp[1],r:8},'fill:none;stroke:var(--mut);stroke-width:2;stroke-dasharray:3 3');
 const gb=E(r,'g',{}),B=[1,2,0].map(i=>({i,l:E(gb,'line',{x1:cx,y1:oy},'stroke:'+col[i]+';stroke-width:'+wd[i]+';stroke-linecap:round'),c:E(gb,'circle',{r:rd[i]},'fill:'+col[i]+';stroke:var(--card);stroke-width:2.5')}));
 const ring=E(r,'circle',{r:10},'fill:none;stroke:var(--fg);stroke-width:2.5'),tt=TX(lb,r,cx,34,tE,tK,'fill:var(--fg)',17,'middle'),a=TX(lb,r,cx,236,s1E,s1K,null,16,'middle'),b=TX(lb,r,cx,236,s2E,s2K,null,16,'middle'),rs=TX(lb,r,cx,258,rsE,rsK,'fill:var(--fg)',16,'middle');
 gsap.set(hl,{autoAlpha:0});gsap.set([gb,ring,a,b,rs],{autoAlpha:0});
 tl.fromTo([tt,...wl,...fx,gh],{autoAlpha:0},{autoAlpha:1,duration:.5,ease:'power2.out',stagger:.04},.1).to(gb,{autoAlpha:1,duration:.5},.6)   // setup
  .to(hl[x1],{autoAlpha:1,duration:.25},1.3).to(hl[x1],{autoAlpha:0,duration:.25},3.4).to(hl[x2],{autoAlpha:1,duration:.25},4.5).to(hl[x2],{autoAlpha:0,duration:.25},6.6);   // the wall of the turn lights up
 UP(tl,a,1);DN(tl,a,4.2);UP(tl,b,4.4);UP(tl,rs,7);
 tl.set(ring,{autoAlpha:1},6.6).to(ring,{attr:{r:18},duration:.4,ease:'sine.inOut',yoyo:true,repeat:1},6.6);   // resolution: the tip is ringed
 return(a1,a2)=>{for(const q of B){ap(x1,a1,V[q.i],t1);ap(x2,a2,t1,t2);pj(t2,cx,pp);q.l.setAttribute('x2',f1(pp[0]));q.l.setAttribute('y2',f1(pp[1]));q.c.setAttribute('cx',f1(pp[0]));q.c.setAttribute('cy',f1(pp[1]));if(q.i===0){ring.setAttribute('cx',f1(pp[0]));ring.setAttribute('cy',f1(pp[1]))}}}};
const L=PN(120,0,2,'x first, then z','x 먼저, 다음 z','1. turn about x','1. x축 기준 회전','2. turn about z','2. z축 기준 회전','tip (0, 1, 0)','끝점 (0, 1, 0)'),R=PN(360,2,0,'z first, then x','z 먼저, 다음 x','1. turn about z','1. z축 기준 회전','2. turn about x','2. x축 기준 회전','tip (0, 0, 1)','끝점 (0, 0, 1)');
const ne=G(r,240,150);TX(lb,ne,0,0,'≠','≠','fill:var(--fg)',40,'middle');
tl.to(pr,{a1:PI/2,duration:2,ease:'power3.inOut'},1.4).to(pr,{a2:PI/2,duration:2,ease:'power3.inOut'},4.6).fromTo(ne,{autoAlpha:0,scale:.5},{autoAlpha:1,scale:1,duration:.5,ease:'back.out(2.5)'},7.4);
return()=>{L(pr.a1,pr.a2);R(pr.a1,pr.a2)}});

CP('fk-chain','Forward kinematics walks the chain: turn at each joint, step along each link','순기구학은 체인을 따라 걷습니다. 관절마다 회전하고 링크마다 전진합니다',13,11.5,
'Each joint contributes Rz(q) and each link Tx(l). The tip pose is their ordered product, here for q = 40, 35, -50 degrees and l = 1, 1, 0.6.','관절마다 Rz(q), 링크마다 Tx(l)이 곱해집니다. 끝 자세는 순서대로 곱한 결과이며 여기서는 q = 40, 35, -50도, l = 1, 1, 0.6입니다.',true,(m,r,lb,tl)=>{
const u=76,bx=46,by=224,Ls=[1,1,.6],Q=[40,35,-50],Hs=[0],J=[[bx,by]],pr={h:0,x:bx,y:by},T0=.8,SD=1.5,Z='power3.inOut';
for(let i=0;i<3;i++){Hs.push(Hs[i]+Q[i]);const h=Hs[i+1]*PI/180;J.push([J[i][0]+Ls[i]*u*cos(h),J[i][1]-Ls[i]*u*sin(h)])}
E(r,'path',{d:'M'+(bx+2.6*u)+' '+by+'A'+2.6*u+' '+2.6*u+' 0 0 0 '+bx+' '+(by-2.6*u)},'fill:none;stroke:var(--line);stroke-width:2.5;stroke-dasharray:3 8;stroke-linecap:round');
const st=[['turn q1 = 40°','q1 = 40° 회전'],['step l1 = 1.0','l1 = 1.0 전진'],['turn q2 = 35°','q2 = 35° 회전'],['step l2 = 1.0','l2 = 1.0 전진'],['turn q3 = -50°','q3 = -50° 회전'],['step l3 = 0.6','l3 = 0.6 전진']].map(q=>TX(lb,r,262,46,q[0],q[1],'fill:var(--fg)',18,'start'));
const glyph=p=>{const g=G(p);E(g,'line',{x2:34},'stroke:var(--pd);stroke-width:4;stroke-linecap:round');E(g,'line',{y2:-26},'stroke:var(--fg);stroke-width:4;stroke-linecap:round;opacity:.55');E(g,'path',{d:'M38 0l-9-5v10z'},'fill:var(--pd)');return g};
let par=r,gl0;
for(let j=0;j<3;j++){   // the chain is real nesting: each joint group turns inside the previous one
 const q=Q[j]*PI/180,len=Ls[j]*u,s=T0+SD*2*j,s2=s+SD,pos=G(par,j?Ls[j-1]*u:bx,j?0:by),arc=PL(pos,'M34 0A34 34 0 0 '+(q>0?0:1)+' '+f1(34*cos(q))+' '+f1(-34*sin(q)),'fill:none;stroke:var(--pl);stroke-width:7;stroke-linecap:round'),rot=G(pos),lk=LL(rot,0,0,[9,8,7][j]),jd=E(rot,'circle',{r:6},'fill:var(--pf);stroke:var(--fg);stroke-width:2.5'),gl=glyph(rot);
 gsap.set(lk,{autoAlpha:0});gsap.set(jd,{autoAlpha:0});if(j){gsap.set(gl,{autoAlpha:0})}else gl0=gl;
 tl.fromTo(jd,{autoAlpha:0,scale:.5},{autoAlpha:1,scale:1,duration:.3,ease:'back.out(2.5)'},s);
 if(j)tl.set(par.glyph,{autoAlpha:0},s).set(gl,{autoAlpha:1},s);
 DR(tl,arc,s,SD,Z);tl.to(arc,{autoAlpha:0,duration:.3},s+SD)
  .to(rot,{rotation:-Q[j],duration:SD,ease:Z},s).to(pr,{h:Hs[j+1],duration:SD,ease:Z},s)   // turn
  .set(lk,{autoAlpha:1},s2).to(lk,{attr:{x2:len},duration:SD,ease:Z},s2).to(gl,{x:len,duration:SD,ease:Z},s2).to(pr,{x:J[j+1][0],y:J[j+1][1],duration:SD,ease:Z},s2);   // step
 UP(tl,st[2*j],s);DN(tl,st[2*j],s+1.3);UP(tl,st[2*j+1],s2);DN(tl,st[2*j+1],s2+1.3);
 rot.glyph=gl;par=rot}
const jt=E(par,'circle',{cx:Ls[2]*u,r:6},'fill:var(--pf);stroke:var(--fg);stroke-width:2.5');gsap.set(jt,{autoAlpha:0});
tl.fromTo(gl0,{autoAlpha:0},{autoAlpha:1,duration:.4},.2).fromTo(jt,{autoAlpha:0},{autoAlpha:1,duration:.3},T0+SD*6);
const row=(y,en,ko)=>{TX(lb,r,262,y,en,ko,null,16);return E(r,'text',{x:468,y,'font-size':16,'text-anchor':'end'},MO)};
const nh=row(86,'heading','방향'),nx=row(112,'tip x','끝 x'),ny=row(138,'tip y','끝 y'),nd=row(176,'distance','거리'),pt=E(r,'text',{x:24,y:256,'font-size':16},MO),TK=['Rz(q1)','Tx(l1)','Rz(q2)','Tx(l2)','Rz(q3)','Tx(l3)'];let pc=-1;
nd.textContent=(Math.hypot(J[3][0]-bx,by-J[3][1])/u).toFixed(2)+' ≤ 2.6';
const ring=G(r,J[3][0],J[3][1]);E(ring,'circle',{r:12},'fill:none;stroke:var(--pd);stroke-width:3');
tl.fromTo(ring,{autoAlpha:0,scale:.5},{autoAlpha:1,scale:1,duration:.4,ease:'back.out(2.5)'},T0+SD*6).to(ring,{scale:1.2,duration:.4,ease:'sine.inOut',yoyo:true,repeat:1},T0+SD*6+.5).fromTo(nd,{autoAlpha:0},{autoAlpha:1,duration:.4},T0+SD*6);   // resolution
return t=>{nh.textContent=Math.round(pr.h)+'°';nx.textContent=((pr.x-bx)/u).toFixed(2);ny.textContent=((by-pr.y)/u).toFixed(2);
 const c=Math.max(0,Math.min(6,Math.floor((t-T0)/SD)+1));if(c!==pc){pc=c;pt.textContent=c?'T = '+TK.slice(0,c).join(' '):''}}});

CP('singularity-fold','Near full stretch the tip needs a huge joint speed from the plain inverse, while damped least squares stays bounded','완전히 펴지는 자세 근처에서 기본 역행렬은 관절 속도가 폭주하고 감쇠 최소제곱은 상한 안에 머뭅니다',13,7,
'Tip moving outward at 0.1 m/s with both links 1 long: det J = sin q2 shrinks to 0, the plain inverse blows up like 1 / q2, and damped least squares (lam = 0.1) stays below 0.5 rad/s.','양쪽 링크 길이 1인 팔의 끝이 0.1 m/s로 바깥으로 갈 때 det J = sin q2가 0으로 줄고 기본 역행렬은 1 / q2처럼 폭주합니다. 감쇠 최소제곱(lam = 0.1)은 0.5 rad/s 아래에 머뭅니다.',false,(m,r,lb,tl)=>{
const u=72,bx=48,by=150,vv=.1,lm=.01,X0=276,PW=186,Y0=46,PH=124,YM=6,pr={th:90},x0=2*cos(PI/4),dx=2*cos(1.5*PI/360)-x0;
const sol=(h,d)=>{const a=0,b=sin(h),c=2*cos(h),e=cos(h);if(!d)return vv/b*Math.hypot(1,.5);const m0=a*a+b*b+lm,m1=a*c+b*e,m3=c*c+e*e+lm,dt=m0*m3-m1*m1,y0=m3*vv/dt,y1=-m1*vv/dt;return Math.hypot(a*y0+c*y1,b*y0+e*y1)};
const xp=th=>X0+(90-th)/90*PW,yp=v=>Y0+PH-Math.min(v,YM)/YM*PH;
let dP='',dD='';for(let i=0;i<=80;i++){const th=90-89.6*i/80,h=th*PI/360;dP+=(i?'L':'M')+f1(xp(th))+' '+f1(yp(sol(h,0)));dD+=(i?'L':'M')+f1(xp(th))+' '+f1(yp(sol(h,1)))}
E(r,'path',{d:'M'+X0+' '+Y0+'V'+(Y0+PH)+'H'+(X0+PW+6)},'fill:none;stroke:var(--line);stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round');
E(r,'path',{d:'M'+X0+' '+f1(yp(.5))+'H'+(X0+PW)},'fill:none;stroke:var(--pl);stroke-width:2.5;stroke-dasharray:4 6');
const cP=PL(r,dP,'fill:none;stroke:var(--fg);stroke-width:3.5;stroke-linejoin:round'),cD=PL(r,dD,'fill:none;stroke:var(--pt);stroke-width:3.5;stroke-linejoin:round');
const mk=c=>{const o=E(r,'g',{}),i=G(o);E(i,'circle',{r:7},'fill:'+c+';stroke:var(--card);stroke-width:2.5');return[o,i]},[dpo,dpi]=mk('var(--fg)'),[ddo]=mk('var(--pt)');
BX(r,bx-24,by+4,48,12,6);const k1=LK(r,9),k2=LK(r,8),jn=[E(r,'circle',{r:7},'fill:var(--pf)'),E(r,'circle',{r:7},'fill:var(--pf)')],tp=E(r,'circle',{r:7},'fill:var(--pd);stroke:var(--card);stroke-width:2');
const ao=E(r,'g',{}),ai=G(ao);E(ai,'path',{d:'M0 0H26M26 0l-8-6M26 0l-8 6'},'fill:none;stroke:var(--pt);stroke-width:4;stroke-linecap:round;stroke-linejoin:round');
TX(lb,r,X0,32,'joint speed (rad/s)','관절 속도 (rad/s)');TX(lb,r,X0+PW+6,192,'elbow angle 90° to 0°','팔꿈치 각도 90° → 0°',null,15,'end');TX(lb,r,X0-6,Y0+8,'6','6',null,15,'end');TX(lb,r,X0-6,Y0+PH+4,'0','0',null,15,'end');
const row=(x,y,en,ko,c)=>{TX(lb,r,x,y,en,ko,c);return E(r,'text',{x:x+(x<100?170:190),y,'font-size':16,'text-anchor':'end'},MO)};
const e1=row(24,214,'elbow q2','팔꿈치 q2'),e2=row(24,236,'det J','det J'),e3=row(24,258,'tip speed','끝 속도'),p1=row(X0-2,214,'plain inverse','기본 역행렬','fill:var(--fg)'),p2=row(X0-2,236,'damped','감쇠','fill:var(--pt)'),p3=row(X0-2,258,'damped limit','감쇠 상한');
e3.textContent='0.1 m/s';p3.textContent='0.5';
DR(tl,cP,.2,1.2,'power2.out');DR(tl,cD,.5,1.2,'power2.out');   // setup: the two curves are drawn
tl.to(ai,{x:5,duration:.6,ease:'sine.inOut',yoyo:true,repeat:19},0)   // ambient: the tip keeps pushing outward
 .to(pr,{th:1.5,duration:dx/vv,ease:p=>(90-360/PI*Math.acos((x0+dx*p)/2))/88.5},1).to(dpi,{scale:1.5,duration:.3,ease:'sine.inOut',yoyo:true,repeat:5},5.4).to(pr,{th:90,duration:4,ease:'power3.inOut'},8.2);   // x = 2 cos(q2/2) advances at vv; the arm then relaxes
return()=>{const th=pr.th,h=th*PI/360,x1=bx+u*cos(h),y1=by-u*sin(h),tx=bx+2*u*cos(h);k1(bx,by,x1,y1);k2(x1,y1,tx,by);
 for(const[c,x,y]of[[jn[0],bx,by],[jn[1],x1,y1],[tp,tx,by]]){c.setAttribute('cx',f1(x));c.setAttribute('cy',f1(y))}
 TF(ao,tx+14,by);const sp=sol(h,0),sd=sol(h,1);TF(dpo,xp(th),yp(sp));TF(ddo,xp(th),yp(sd));
 e1.textContent=th.toFixed(1)+'°';e2.textContent=sin(th*PI/180).toFixed(3);p1.textContent=Math.min(99.9,sp).toFixed(1);p2.textContent=sd.toFixed(2)}});

CP('pubsub-flow','A reliable subscriber cannot match a best effort publisher, so it receives nothing and no error appears until it asks for best effort','reliable 구독자는 best effort 발행자와 맞지 않아 아무것도 받지 못하고 오류도 없습니다. best effort로 바꾸면 연결됩니다',14,12.6,
'The camera offers best effort. The logger asks for best effort and matches. The viewer asks for reliable, never matches, and gets nothing and no error. Ask for best effort and it matches.','카메라는 best effort를 제공합니다. 로거는 best effort를 요청해 연결됩니다. 뷰어는 reliable을 요청해 연결되지 않고 오류도 없습니다. best effort로 바꾸면 연결됩니다.',true,(m,r,lb,tl)=>{
const wv=[[144,130],[237,130],[237,54],[330,54]],wl=[[144,130],[237,130],[237,180],[330,180]],rev=a=>a.slice().reverse();
const bw=E(r,'path',{d:'M144 130H237V54H330M237 130V180H330'},'fill:none;stroke:var(--line);stroke-width:3;stroke-dasharray:6 7;stroke-linecap:round;stroke-linejoin:round');
const so=d=>PL(r,d,'fill:none;stroke:var(--pd);stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round'),sl=so('M144 130H237V180H330'),sv=so('M144 130H237V54H330');
BX(r,24,100,120,60,12);TX(lb,r,84,136,'camera','카메라','fill:var(--fg)',18,'middle');
const chip=(cx,y,w)=>E(r,'rect',{x:cx-w/2,y,width:w,height:24,rx:12},'fill:var(--pb);stroke:var(--line);stroke-width:2');
chip(84,168,160);TX(lb,r,84,185,'offers best effort','제공: best effort','fill:var(--fg)',15,'middle');
BX(r,330,24,130,60,12,BXS+';stroke-dasharray:7 6');const vs=BX(r,330,24,130,60,12);BX(r,330,150,130,60,12);gsap.set(vs,{autoAlpha:0});
TX(lb,r,342,46,'viewer','뷰어','fill:var(--fg)',18);TX(lb,r,342,172,'logger','로거','fill:var(--fg)',18);TX(lb,r,342,72,'received','받은 수',null,15);TX(lb,r,342,198,'received','받은 수',null,15);
const cn=(x,y)=>{const g=G(r,x,y),t=E(g,'text',{'font-size':16,'text-anchor':'end'},MO);t.textContent='0';return[g,t]},[cv,nv]=cn(448,72),[cl,nl]=cn(448,198);
const cg=G(r,395,100);E(cg,'rect',{x:-80,y:-12,width:160,height:24,rx:12},'fill:var(--pb);stroke:var(--line);stroke-width:2');
const ca=TX(lb,cg,0,5,'asks reliable','요청: reliable','fill:var(--fg)',15,'middle'),cb=TX(lb,cg,0,5,'asks best effort','요청: best effort','fill:var(--fg)',15,'middle');
chip(395,214,160);TX(lb,r,395,231,'asks best effort','요청: best effort','fill:var(--fg)',15,'middle');
const an=TX(lb,r,150,34,'no match, no error','매칭 안 됨, 오류 없음','fill:var(--mut)',16);
const mkc=()=>{const g=G(r);E(g,'circle',{r:12},'fill:var(--card);stroke:var(--fg);stroke-width:2.5');return g},ok=mkc(),no=mkc(),okv=mkc();gsap.set(ok,{x:300,y:180});gsap.set([no,okv],{x:300,y:54});
for(const g of[ok,okv])E(g,'path',{d:'M-6 0l4 5 8-10'},'fill:none;stroke:var(--pd);stroke-width:4;stroke-linecap:round;stroke-linejoin:round');E(no,'path',{d:'M-5-5l10 10M5-5l-10 10'},'fill:none;stroke:var(--fg);stroke-width:4;stroke-linecap:round');
const pb=['var(--pd)','var(--fg)'].map(c=>{const g=G(r,330,0);E(g,'circle',{r:6},'fill:'+c+';stroke:var(--card);stroke-width:2');gsap.set(g,{autoAlpha:0});return g});
gsap.set(cb,{autoAlpha:0});gsap.set([ok,no,okv,an],{autoAlpha:0});
const pop=(e,t)=>tl.fromTo(e,{autoAlpha:0,scale:.4},{autoAlpha:1,scale:1,duration:.5,ease:'back.out(2.5)'},t);
tl.to(bw,{strokeDashoffset:-130,duration:14,ease:'none'},0)   // ambient: the discovery wires keep probing
 .fromTo(an,{autoAlpha:0,y:6},{autoAlpha:1,y:0,duration:.4,ease:'power3.out'},3.4).to(an,{autoAlpha:0,duration:.3},6.3);
tl.set(pb[0],{x:330,y:180,autoAlpha:1},1.2);PATH(tl,pb[0],rev(wl),1.2,1);tl.to(pb[0],{autoAlpha:0,duration:.1},2.2);   // the logger asks best effort and matches
DR(tl,sl,2.4,.5);pop(ok,2.4);pop(no,2.4);   // the viewer asks reliable and does not
tl.to(cg,{scaleY:0,duration:.4,ease:'power2.in'},6.4).set(ca,{autoAlpha:0},6.8).set(cb,{autoAlpha:1},6.8).to(cg,{scaleY:1,duration:.4,ease:'power2.out'},6.8);   // the viewer's request flips to best effort
tl.set(pb[1],{x:330,y:54,autoAlpha:1},7.4);PATH(tl,pb[1],rev(wv),7.4,.9);tl.to(pb[1],{autoAlpha:0,duration:.1},8.3);
tl.to(no,{autoAlpha:0,scale:.6,duration:.2},8.4);pop(okv,8.4);DR(tl,sv,8.4,.5);tl.to(vs,{autoAlpha:1,duration:.3},8.4);   // match: the viewer link is solid
const MS=[[3,1],[3.9,1],[4.8,1],[5.7,1],[9.2,1],[10.2,1],[11.2,1],[9.2,0],[10.2,0],[11.2,0]];
MS.forEach(([t0,lg])=>{const e=E(r,'rect',{x:-9,y:-6.5,width:18,height:13,rx:4},'fill:var(--pd);stroke:var(--card);stroke-width:2');gsap.set(e,{x:144,y:130,autoAlpha:0,scale:.6,transformOrigin:'0 0'});
 tl.to(e,{autoAlpha:1,scale:1,duration:.12,ease:'back.out(2)'},t0);PATH(tl,e,lg?wl:wv,t0,1);tl.to(e,{autoAlpha:0,scale:.6,duration:.12,ease:'power2.in'},t0+.88);
 const c=lg?cl:cv;tl.set(c,{scale:1.35},t0+1).to(c,{scale:1,duration:.3,ease:'back.out(2)'},t0+1)});
return t=>{let a=0,b=0;MS.forEach(q=>{if(t>=q[0]+1){if(q[1])a++;else b++}});nl.textContent=a;nv.textContent=b}});
})();
