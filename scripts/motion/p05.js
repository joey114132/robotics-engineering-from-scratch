// phase 05 concept loops (480x270) as GSAP timelines on the MB kit from 20-scenes-b.js
(function () {
 const R = window.MOTION,K = window.MB; if (!K) return;
 const {$,A,CC,RR,fin} = K,T = (m,p,x,y,en,ko,c,an) => K.T(m,p,x,y,en,ko,c,an,15);
 // D: a text node you set from draw(); .e is the node for tweens
 const D = (p,x,y,cls,an) => {const e = $(p,'text',{x,y,'font-size':15,class:cls || '','text-anchor':an || 'start'}); let l = ''; const f = s => {if (s !== l) {l = s; e.textContent = s;}}; f.e = e; return f;};
 const stage = (m,en,ko) => {const q = K.stage(m,en,ko,480,270); m.caption(en,ko); m.replayButton(); return q;};

 R.gs('executor-queue',(el,m) => {
  const g = stage(m,'Lesson model: a timer every 10 ms (1 ms of work) and a 60 ms slow callback. One thread: the ticks queue and the first waits 59 ms. Two threads, separate groups: none waits.','레슨 모델입니다. 10 ms마다 도는 타이머(일 1 ms)와 60 ms짜리 느린 callback이 있습니다. thread 하나면 tick이 줄을 서서 첫 tick이 59 ms 기다립니다. group을 나눈 thread 둘이면 기다리지 않습니다.');
  const X = ms => 20 + ms * 4.4,J = [{i:1,r:0,d:60}];
  for (let k = 0; k < 10; k++) J.push({i:0,r:1 + 10 * k,d:1});
  // FIFO schedule of the lesson's model: one thread runs jobs in release order; two threads in separate groups start every job at its release
  const plan = th => {let end = 0; return J.map(j => {const s = th === 1 ? Math.max(j.r,end) :j.r; end = s + j.d; return Object.assign({s,e:end,ln:th === 2 && !j.i ? 1 :0},j);});};
  const logs = [plan(1),plan(2)],W1 = Math.max(...logs[0].filter(j => !j.i).map(j => j.s - j.r));
  const rows = Array.from({length:10},(_,k) => [CC(g,X(1 + 10 * k),39 + k * 9,2.5,'g'),RR(g,X(1 + 10 * k),36.5 + k * 9,0,5,2.5,'x')]);
  const lane = [140,166].map(y => RR(g,X(0),y,440,22,4,'n s sm')),jobs = J.map(() => RR(g,0,0,0,18,2,'t'));
  const cur = $(g,'path',{class:'s n sm'}),hl = D(g,16,20,'g'),r1 = D(g,16,218,'g'),r2 = D(g,16,242,'m'),o = {c:0,n:1};
  const draw = () => {
   const L = logs[o.n - 1],c = Math.round(o.c); let worst = 0;
   L.filter(j => !j.i).forEach((j,k) => {
    const w = Math.min(c,j.s) - j.r; if (c >= j.r) worst = Math.max(worst,w);
    A(rows[k][0],{opacity:c >= j.r ? 1 :.2}); A(rows[k][1],{width:Math.max(0,w) * 4.4,class:c < j.s ? 'x' :'m'});
   });
   L.forEach((j,q) => A(jobs[q],{x:X(j.s),y:142 + 26 * j.ln,width:Math.max(0,Math.min(c,j.e) - j.s) * 4.4,class:j.i ? 'd' :'t'}));
   A(lane[1],{opacity:o.n === 2 ? 1 :.25}); A(cur,{d:`M${X(c)} 30V192`});
   hl(o.n === 1 ? m.t('One thread: the slow callback holds the line','thread 하나: 느린 callback이 줄을 막습니다') :m.t('Two threads, separate groups: no wait','thread 둘, group 분리: 기다리지 않습니다'));
   r1(`t = ${c} ms   ${m.t('timer worst wait = ','타이머 최대 대기 = ')}${worst} ms`);
   r2(o.n === 2 ? m.t('with one thread it was ','thread 하나일 때는 ') + W1 + ' ms' :m.t('each bar: how long a timer tick waited','막대: 타이머 tick이 기다린 시간'));
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,12.4);
  tl.set(o,{n:1,c:0},0).fromTo(o,{c:0},{c:99,duration:4.6,ease:'none'},.6).set(o,{n:2,c:0},6.4).fromTo(o,{c:0},{c:99,duration:3.6,ease:'none'},6.8);
  m.play(tl,{rest:10.9,draw});
 });

 R.gs('jitter-bars',(el,m) => {
  const g = stage(m,'The lesson\'s seeded run, cycles 541 to 580 (1000 us each). The mean jitter stays near zero, yet one wake-up 961 us late misses the next deadline.','레슨의 seed 고정 실행에서 541~580번째 cycle입니다(cycle당 1000 us). 평균 jitter는 0 근처인데 961 us 늦게 깬 cycle 하나가 다음 deadline을 넘깁니다.');
  // lateness of each wake-up in us, from the lesson's simulate(5000, spike_p=0.003); one cycle = 1000 us, 200 us of work
  const U = [4,6,3,6,27,0,4,24,6,18,8,4,99,33,15,38,48,41,2,32,961,161,3,2,1,16,46,18,13,6,30,36,17,37,13,7,0,10,21,15],CYC = 1000,WORK = 200;
  const bars = U.map((u,i) => RR(g,24 + i * 11,190,7,0,1.5,'t')),my = 190 - (CYC - WORK) * .125;
  T(m,g,16,22,'Wake-up lateness of each loop cycle','cycle마다 늦게 깬 정도','g');
  $(g,'path',{d:'M16 190H464',class:'s n sm'}); $(g,'path',{d:`M16 ${my}H464`,class:'s n sw','stroke-dasharray':'4 5'});
  T(m,g,464,my - 7,'a start this late misses','이만큼 늦게 시작하면 놓침','w','end');
  const r1 = D(g,16,222,'g'),r2 = D(g,16,246,'m'),o = {k:0};
  const draw = () => {
   const k = Math.round(o.k); let w = 0,miss = 0;
   U.forEach((u,i) => {
    const h = Math.max(1,u * .125),late = u + WORK > CYC;
    A(bars[i],{y:190 - h,height:i <= k ? h :0,class:late ? 'x' :'t'});
    if (i <= k) {if (i) w = Math.max(w,Math.abs(u - U[i - 1])); if (late) miss++;}
   });
   r1(`${m.t('mean jitter ','평균 jitter ')}${k ? Math.round((U[k] - U[0]) / k) :0} us   ${m.t('worst jitter ','최악 jitter ')}${w} us`);
   r2(`${m.t('cycles shown ','표시한 cycle ')}${k + 1}   ${m.t('missed deadlines ','놓친 deadline ')}${miss}`);
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.6);
  tl.fromTo(o,{k:0},{k:39,duration:7.2,ease:'none'},.6);
  m.play(tl,{rest:9.4,draw});
 });

 R.gs('clock-order',(el,m) => {
  const g = stage(m,'Camera clock 30 ms ahead, sensors 10 ms apart: sorting by stamp mixes up the order. Subtract an offset estimate that is 1 ms off and the order is right again.','카메라 시계가 30 ms 앞서고 센서는 10 ms 간격입니다. stamp로 정렬하면 순서가 뒤섞입니다. 1 ms 오차의 offset 추정치를 빼면 순서가 다시 맞습니다.');
  const EV = [['A',0],['B',10],['A',20],['B',30],['A',40],['B',50]],X = ms => 40 + ms * 5,TRUE = 'ABABAB';
  T(m,g,16,52,'true time (A = IMU, B = camera)','실제 시각(A = IMU, B = 카메라)','m'); T(m,g,16,118,'stamped time (B clock ahead)','stamp 시각(B 시계가 앞섬)','m'); T(m,g,16,178,'order after sorting by stamp','stamp로 정렬한 순서','m');
  [76,142].forEach(y => $(g,'path',{d:`M30 ${y}H460`,class:'s n sm'}));
  const dot = (y,e) => {const q = $(g,'g',{}); CC(q,0,0,11,e[0] === 'A' ? 'f s st' :'d s st'); $(q,'text',{y:5,'font-size':15,'text-anchor':'middle'}).textContent = e[0]; return q;};
  const d1 = EV.map(e => dot(76,e)),d2 = EV.map(e => dot(142,e)),box = TRUE.split('').map((_,i) => RR(g,40 + i * 66 - 26,190,52,34,6,'c s sm')),lt = box.map((b,i) => D(g,40 + i * 66,213,'g','middle'));
  EV.forEach((e,i) => gsap.set(d1[i],{x:X(e[1]),y:76}));
  const hl = D(g,16,22,'g'),rd = D(g,16,252,'g'),o = {s:0,p:0};
  const draw = () => {
   const st = EV.map((e,i) => [e[1] + (e[0] === 'B' ? o.s :0),e[0]]);
   st.forEach((s,i) => gsap.set(d2[i],{x:X(s[0]),y:142}));
   const ord = st.slice().sort((a,b) => a[0] - b[0] || (a[1] < b[1] ? -1 :1)).map(s => s[1]); let bad = 0;
   ord.forEach((c,i) => {const x = c !== TRUE[i]; if (x) bad++; lt[i](c); A(box[i],{class:'c s ' + (x ? 'sb' :'sk')});});
   hl(o.p ? m.t('Subtract the offset estimate from the B stamps','B stamp에서 offset 추정치를 뺍니다') :m.t('The camera clock runs ahead of the IMU clock','카메라 시계가 IMU 시계보다 앞서 갑니다'));
   rd(`${m.t('B stamps are ','B stamp가 ')}${Math.round(o.s)} ms ${m.t('ahead','앞섬')}   ${m.t('order errors ','순서 오류 ')}${bad}`);
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,11.4);
  tl.set(o,{s:0,p:0},0).fromTo(o,{s:0},{s:30,duration:2,ease:'power1.inOut'},.8).set(o,{p:1},4.3).fromTo(o,{s:30},{s:1,duration:3.5,ease:'power1.inOut'},4.5);
  m.play(tl,{rest:9.6,draw});
 });

 R.gs('bt-resume',(el,m) => {
  const g = stage(m,'The lesson\'s fetch task, one tick at a time. The grasp fails twice and the Retry answers running. The Sequence remembers where it was, so go object is ticked 3 times and never again.','레슨의 fetch 작업을 tick 하나씩 봅니다. grasp가 두 번 실패하는 동안 Retry는 running을 답합니다. Sequence가 어디까지 했는지 기억하므로 go object는 3번만 tick되고 그 뒤로는 다시 tick되지 않습니다.');
  // port of the lesson's Sequence / Retry with scripted leaves; S success, F failure, R running
  const sc = a => {let i = 0; return () => a[Math.min(i++,a.length - 1)];},L = {go:sc('RRS'),gr:sc('FFS'),bin:sc('RS'),rel:sc('S')},KEY = ['go','rt','bin','rel'],TK = [];
  let cur = 0,used = 0;
  for (let n = 0; n < 6; n++) {
   const st = {}; let root = 'S',k;
   for (k = cur; k < 4; k++) {
    let s; if (k === 1) {s = st.gr = L.gr(); if (s === 'F') {used++; s = used < 3 ? 'R' :'F';} if (s !== 'R') used = 0;} else s = L[KEY[k]]();
    st[KEY[k]] = s; if (s !== 'S') {root = s; cur = s === 'R' ? k :0; break;}
   }
   if (k === 4) cur = 0; TK.push({st,root,cur});
  }
  const NM = [['go object','go object'],['retry','retry'],['go bin','go bin'],['release','release'],['grasp','grasp']],POS = [[62,118],[182,118],[302,118],[422,118],[182,192]],WORD = {S:['success','성공'],F:['failure','실패'],R:['running','실행 중']};
  const CL = {S:'c s sk w4',F:'c s sb w4',R:'c s sf w4'};
  [0,1,2,3].forEach(i => $(g,'path',{d:`M240 67L${POS[i][0]} 95`,class:'s n sm'})); $(g,'path',{d:'M182 141V169',class:'s n sm'});
  const fr = RR(g,188,21,104,46,8,'c s sm'); T(m,g,240,41,'fetch','fetch','g','middle');
  const rs = D(g,240,59,'m','middle'),nodes = POS.map((p,i) => {
   const b = RR(g,p[0] - 52,p[1] - 23,104,46,8,'c s sm'); T(m,g,p[0],p[1] - 3,NM[i][0],NM[i][1],'g','middle'); return [b,D(g,p[0],p[1] + 15,'m','middle')];
  }),mk = RR(g,0,0,112,54,10,'n s sw',{'stroke-dasharray':'4 4'}),r1 = D(g,16,236,'g'),r2 = D(g,16,258,'m'),r3 = D(g,16,30,'g'),o = {k:0};
  const draw = () => {
   const k = Math.round(o.k),t = TK[k],c = {go:0,gr:0,bin:0,rel:0};
   TK.slice(0,k + 1).forEach(q => ['go','gr','bin','rel'].forEach(x => {if (q.st[x]) c[x]++;}));
   [0,1,2,3,4].forEach(i => {const s = t.st[i === 4 ? 'gr' :KEY[i]]; A(nodes[i][0],{class:s ? CL[s] :'c s sm'}); nodes[i][1](s ? m.t(...WORD[s]) :m.t('not ticked','tick 안 됨'));});
   A(fr,{class:CL[t.root]}); rs(m.t(...WORD[t.root]));
   A(mk,{opacity:t.root === 'R' ? 1 :0,x:POS[t.cur][0] - 56,y:POS[t.cur][1] - 27});
   r3(`tick ${k + 1} / 6`); r1(t.root === 'R' ? `${m.t('next tick resumes at: ','다음 tick은 여기서 재개: ')}${NM[t.cur][0]}` :m.t('the task is done: success','작업 끝: success'));
   r2(`${m.t('ticks so far  go object ','지금까지 tick  go object ')}${c.go}  grasp ${c.gr}  go bin ${c.bin}  release ${c.rel}`);
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,11.8);
  for (let k = 0; k < 6; k++) tl.set(o,{k},.6 + 1.5 * k);
  m.play(tl,{rest:10.4,draw});
 });

 R.gs('tf-lookup',(el,m) => {
  const g = stage(m,'A pose buffer with samples at 0, 1 and 2 s (position 2 t, heading t rad) and 0.1 s of allowed extrapolation. Between samples it interpolates, just past the newest it extrapolates, anything else is refused.','0, 1, 2초에 sample이 있는 pose buffer입니다(위치 2 t, heading t rad). extrapolation은 0.1초까지 허용합니다. sample 사이는 보간하고 가장 새 sample 바로 뒤는 외삽하며 그 밖은 거부합니다.');
  const TX = t => 40 + (t + .4) * 150,PX = p => 40 + p * 100,ZY = 150,TS = [0,1,2];
  const arrow = c => $(g,'polygon',{points:'14,0 -10,-9 -10,9',class:c}); $(g,'path',{d:'M40 100H460',class:'s n sm'});
  TS.forEach(t => {const gh = arrow('n s sm'); A(gh,{transform:`translate(${PX(2 * t)} 100) rotate(${-t * 57.2958})`}); T(m,g,PX(2 * t),76,`t = ${t} s`,`t = ${t}초`,'m','middle');});
  const rb = arrow('f s st w3'); 
  [[0,.4,'x',.3],[.4,2.4,'k',.3],[2.4,2.5,'w',.7],[2.5,2.8,'x',.3]].forEach(([a,b,c,op]) => RR(g,TX(a - .4),ZY,(b - a) * 150,20,0,c,{opacity:op}));
  TS.forEach(t => $(g,'path',{d:`M${TX(t)} ${ZY - 4}V${ZY + 24}`,class:'s n sm'}));
  T(m,g,40,ZY - 8,'refused','거부','m'); T(m,g,TX(1),ZY - 8,'interpolates','보간','m','middle'); T(m,g,462,ZY - 8,'refused','거부','m','end');
  TS.forEach(t => T(m,g,TX(t),ZY + 42,`${t} s`,`${t}초`,'m','middle'));
  RR(g,16,198,14,14,2,'w',{opacity:.7}); T(m,g,38,211,'extrapolates, at most 0.1 s past the newest','가장 새 sample보다 0.1초까지만 외삽','m');
  const q = $(g,'path',{class:'s n w4'}),r1 = D(g,16,238,'g'),r2 = D(g,16,260,'g'),o = {t:-.4};
  const draw = () => {
   const c = Math.round(o.t * 100),t = c / 100,ok = c >= 0 && c <= 210,st = !ok ? 'sb' :c > 200 ? 'sw' :'sk';
   A(q,{d:`M${TX(t)} ${ZY - 6}V${ZY + 28}`,class:`s n w4 ${st}`}); A(rb,{transform:`translate(${PX(2 * t)} 100) rotate(${-t * 57.2958})`,opacity:ok ? 1 :0});
   r1(`t = ${t.toFixed(2)} s   ` + (c < 0 ? m.t('refused','거부') :c <= 200 ? m.t('interpolated','보간') :c <= 210 ? m.t('extrapolated','외삽') :m.t('refused','거부')));
   r2(ok ? `x = ${(2 * t).toFixed(2)} m   ${m.t('heading','heading')} = ${(t * 57.2958).toFixed(0)}°` :m.t(`${Math.abs(c < 0 ? t :t - 2).toFixed(2)} s ${c < 0 ? 'older than the oldest' :'newer than the newest'} sample`,`가장 ${c < 0 ? '오래된' :'새'} sample보다 ${Math.abs(c < 0 ? t :t - 2).toFixed(2)}초 ${c < 0 ? '이전' :'뒤'}`));
  };
  const tl = m.timeline({repeatDelay:.3});
  fin(tl,g,10.6);
  [[-.4,0,1.1,.8],[0,2,4.4,1.9],[2,2.1,1.6,6.3],[2.1,2.4,1.2,7.9]].forEach(([a,b,d,s]) => tl.fromTo(o,{t:a},{t:b,duration:d,ease:'none'},s));
  m.play(tl,{rest:4.2,draw});
 });
})();
