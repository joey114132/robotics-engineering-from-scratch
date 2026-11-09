// 페이즈 12~16 첫 레슨 상단 장면 5종, GSAP timeline: scene-12..scene-16 (sim 쌍둥이, 정책 시도, 군집 대형, 정지, Bolt 마무리 회전)
(()=>{
  const FG = 'var(--fg)', MUT = 'var(--mut)', LN = 'var(--line)', CD = 'var(--card)', PF = 'var(--pf)', PT = 'var(--pt)', BAD = 'var(--bad)', OK = 'var(--ok)', AM = 'var(--oops)';
  const sk = (c, w = 2.5, x = '')=>`fill:none;stroke:${c};stroke-width:${w};stroke-linecap:round;stroke-linejoin:round;${x}`;
  const fl = (c, x = '')=>`fill:${c};stroke:none;${x}`, box = c=>`fill:${CD};stroke:${c};stroke-width:2.5`, ring = (c, w = 2.5)=>`fill:none;stroke:${c};stroke-width:${w}`;
  const R = Math.PI / 180, f1 = v=>v.toFixed(1), at = (e, o)=>{for (const k in o) e.setAttribute(k, o[k]);};
  const kit = m=>{
    const n = (tag, a, p)=>{const {s, ...r} = a; return m.mk(tag, s === undefined ? a : {...r, style: s}, p);};
    const T = (p, x, y, en, ko, z, st, an)=>{const e = n('text', {x, y, 'text-anchor': an || 'start', s: `font-size:${z}px;${st || ''}`}, p), f = ()=>{e.textContent = m.t(en, ko);}; f(); m.onTheme(f); return e;};
    const O = (p, x, y)=>{const e = n('g', {}, p); gsap.set(e, {x, y, svgOrigin: '0 0'}); return e;};
    return {n, T, O, tl: m.timeline({defaults: {ease: 'power2.out'}})};
 };
  const io = (tl, g, P)=>tl.fromTo(g, {autoAlpha: 0}, {autoAlpha: 1, duration: .5, ease: 'power1.out'}, 0).to(g, {autoAlpha: 0, duration: .6, ease: 'power1.in'}, P - .6);
  const swap = (tl, ns, ts)=>ns.forEach((e, i)=>{tl.fromTo(e, {autoAlpha: 0, y: 5}, {autoAlpha: 1, y: 0, duration: .35}, ts[i]); if (i < ns.length - 1) tl.to(e, {autoAlpha: 0, duration: .18, ease: 'power1.in'}, ts[i + 1] - .18);});
  const blip = (tl, e, t, v, from)=>{gsap.set(e, {autoAlpha: 0}); return tl.set(e, {autoAlpha: 1, ...from}, t).to(e, {...v, autoAlpha: 0}, t);};

  function bolt(n, p, x, y, S) {
    const mv = n('g', {}, p), sp = n('g', {}, mv), sq = n('g', {}, sp), g = n('g', {transform: `translate(${-32 * S} ${-61 * S}) scale(${S})`}, sq), bf = box(FG);
    n('path', {d: 'M32 11V5', s: sk(FG, 2.5)}, g);
    n('circle', {cx: 32, cy: 4.5, r: 3, s: `fill:${PF};stroke:${FG};stroke-width:2`}, g);
    const ants = [BAD, OK].map(c=>n('circle', {cx: 32, cy: 4.5, r: 3, s: `fill:${c};stroke:${FG};stroke-width:2;opacity:0`}, g));
    n('rect', {x: 19, y: 46, width: 26, height: 15, rx: 6, s: bf}, g);
    n('circle', {cx: 32, cy: 53.5, r: 2.6, s: fl(PF)}, g);
    n('rect', {x: 4.5, y: 22, width: 6, height: 11, rx: 3, s: bf}, g); n('rect', {x: 53.5, y: 22, width: 6, height: 11, rx: 3, s: bf}, g);
    n('rect', {x: 10, y: 11, width: 44, height: 34, rx: 13, s: bf}, g);
    n('rect', {x: 16, y: 17, width: 32, height: 22, rx: 9, s: 'fill:#0e1a1f'}, g);
    const idle = n('g', {}, g), cheer = n('g', {}, g);
    const gaze = n('g', {}, idle); [26, 38].map(cx=>n('circle', {cx, cy: 27, r: 3.3, s: fl(PF)}, gaze));
    n('path', {d: 'M28.5 33.5q3.5 2.8 7 0', s: sk(PF, 2.6)}, idle);
    n('path', {d: 'M21.5 29q4.5-8 9 0M33.5 29q4.5-8 9 0', s: sk(PF, 2.6)}, cheer); n('path', {d: 'M27 32.5q5 7.5 10 0z', s: fl(PF)}, cheer);
    gsap.set([sp, sq], {svgOrigin: '0 0'}); gsap.set(mv, {x, y, svgOrigin: '0 0'}); gsap.set(cheer, {autoAlpha: 0});
    return {mv, sp, sq, idle, cheer, gaze, ants};
 }

  // scene-12
  MOTION.gs('scene-12', (el, m)=>{
    const P = 10, {svg, g} = m.svg(640, 220, 'A real arm and its simulated twin drift apart, then snap back', '실제 팔과 시뮬 쌍둥이가 어긋났다가 보정으로 다시 맞춰집니다');
    const {n, T, O, tl} = kit(m), L1 = 78, L2 = 66, FY = 190, XR = 150, XS = 490, SY = FY - 24;
    n('line', {x1: 40, y1: FY, x2: 280, y2: FY, s: sk(FG)}, g); n('line', {x1: 360, y1: FY, x2: 600, y2: FY, s: sk(PT, 2.5, 'stroke-dasharray:3 7')}, g);
    n('line', {x1: 320, y1: 44, x2: 320, y2: FY, s: sk(LN, 2, 'stroke-dasharray:2 7')}, g);
    T(g, XR, 34, 'real', '실제', 20, `fill:${FG};font-weight:700`, 'middle'); T(g, XS, 34, 'sim twin', '시뮬 쌍둥이', 20, `fill:${PT};font-weight:700`, 'middle');
    const dust = Array.from({length: 6}, (_, i)=>{const d = O(g, 372 + i * 44, FY - 6); n('circle', {r: 2.2, s: fl(PF)}, d); gsap.set(d, {autoAlpha: 0}); return d;});
    const arm = (x, real)=>{
      const col = real ? FG : PT, a = n('g', {}, g);
      n('rect', {x: x - 20, y: FY - 14, width: 40, height: 14, rx: 6, s: box(col)}, a);
      const d1 = O(a, x, SY), l1 = n('g', {}, d1), d2 = O(l1, L1, 0), l2 = n('g', {}, d2);
      n('rect', {x: -7, y: -8, width: L1 + 14, height: 16, rx: 8, s: box(col)}, l1); n('rect', {x: -7, y: -7, width: L2 + 14, height: 14, rx: 7, s: box(col)}, l2);
      n('circle', {r: 5, s: `fill:${real ? FG : PF};stroke:${col};stroke-width:2.5`}, l1); n('circle', {cx: L2, r: 3.5, s: fl(col)}, l2);
      gsap.set([l1, l2], {svgOrigin: '0 0'});
      return {d1, l1, d2, l2};
   };
    const real = arm(XR, 1), sim = arm(XS, 0);
    const ghost = n('circle', {opacity: 0, r: 12, s: sk(BAD, 3, 'stroke-dasharray:4 4')}, g), gapLine = n('line', {opacity: 0, s: sk(BAD, 2.5)}, g);
    const rg = O(g, XS, FY - 10), rr = n('circle', {r: 10, s: ring(PT, 3)}, rg), ck = O(g, XS + 96, 48);
    n('path', {d: 'M-9 0l6 7l13-15', s: sk(OK, 4)}, ck); gsap.set(ck, {autoAlpha: 0, scale: .3}); gsap.set(rg, {autoAlpha: 0});
    n('rect', {x: 280, y: 200, width: 80, height: 9, rx: 4.5, s: ring(LN, 2)}, g); const bar = n('rect', {x: 280, y: 200, width: 0, height: 9, rx: 4.5, s: fl(BAD)}, g);
    T(g, 270, 210, 'gap', '오차', 20, `fill:${MUT}`, 'end');
    tl.fromTo([real.l1, sim.l1], {rotation: -86}, {rotation: -46, duration: 2.5, ease: 'sine.inOut', repeat: 3, yoyo: true}, 0)
      .fromTo([real.l2, sim.l2], {rotation: 86}, {rotation: 50, duration: 2.5, ease: 'power1.inOut', repeat: 3, yoyo: true}, 0)
      .to(sim.d1, {rotation: 34, duration: 4.2, ease: 'power2.in'}, 1.8).to(sim.d2, {rotation: -20.4, duration: 4.2, ease: 'power2.in'}, 1.8)
      .to([sim.d1, sim.d2], {rotation: 0, duration: 1, ease: 'elastic.out(1,.5)'}, 6)
      .set(rg, {autoAlpha: 1}, 6).to(rr, {attr: {r: 60}, duration: 1}, 6).to(rg, {autoAlpha: 0, duration: 1, ease: 'power1.in'}, 6)
      .to(ck, {autoAlpha: 1, scale: .9, duration: .5, ease: 'back.out(3)'}, 6.8)
      .fromTo(dust, {y: 0}, {y: -150, duration: 2.33, ease: 'none', repeat: 2, stagger: .2}, 0)
      .to(dust, {keyframes: {autoAlpha: [.45, .45, 0]}, duration: 2.33, ease: 'none', repeat: 2, stagger: .2}, 0);
    io(tl, g, P);
    const G = gsap.getProperty, tip = (x, a, b)=>{const A = a * R, B = (a + b) * R; return [x + L1 * Math.cos(A) + L2 * Math.cos(B), SY + L1 * Math.sin(A) + L2 * Math.sin(B)];};
    m.play(tl, {rest: 5.8, draw() {
      const r = tip(XR, G(real.l1, 'rotation'), G(real.l2, 'rotation')), s = tip(XS, G(sim.d1, 'rotation') + G(sim.l1, 'rotation'), G(sim.d2, 'rotation') + G(sim.l2, 'rotation'));
      const gx = XS + r[0] - XR, gap = Math.hypot(s[0] - gx, s[1] - r[1]), on = gap > 3 ? 1 : 0;
      at(ghost, {cx: f1(gx), cy: f1(r[1]), opacity: on}); at(gapLine, {x1: f1(s[0]), y1: f1(s[1]), x2: f1(gx), y2: f1(r[1]), opacity: on}); bar.setAttribute('width', Math.min(80, gap * 2.2).toFixed(1));
   }});
 });

  // scene-13
  MOTION.gs('scene-13', (el, m)=>{
    const P = 11, {svg, g} = m.svg(640, 220, 'Policy attempts fan out, then tighten toward the goal', '정책의 시도가 넓게 퍼졌다가 목표 쪽으로 좁혀집니다');
    const {n, T, O, tl} = kit(m), U = [-.2, .4, -.9, .15, .35, -.5, .9], V = [.8, -.6, .5, -.9, .4, .9, -.5], W = [-.5, .9, -.7, .6, -.9, .3, .8], SP = [100, 60, 14], GX = 570, GY = 110, N = 7;
    const dr = (s, i)=>`M70 115C220 ${(110 + 1.3 * s * V[i]).toFixed(1)} 400 ${(110 + .9 * s * W[i]).toFixed(1)} ${GX} ${(GY + .8 * s * U[i]).toFixed(1)}`, ey = (s, i)=>GY + .8 * s * U[i], hit = (s, i)=>Math.abs(.8 * s * U[i]) < 22;
    n('path', {d: `M70 115L${GX - 20} ${GY - 80}M70 115L${GX - 20} ${GY + 80}`, s: sk(LN, 2, 'stroke-dasharray:4 6')}, g); n('line', {x1: 30, y1: 190, x2: 610, y2: 190, s: sk(LN, 2)}, g);
    n('circle', {cx: GX, cy: GY, r: 22, s: ring(PT, 3)}, g); n('circle', {cx: GX, cy: GY, r: 8, s: fl(PF)}, g);
    const pulse = O(g, GX, GY), pr = n('circle', {r: 22, s: ring(PT, 2)}, pulse);
    const path = U.map((_, i)=>n('path', {d: dr(SP[0], i), pathLength: 1, s: sk(PT, 3, 'stroke-dasharray:1 2;stroke-dashoffset:1.02;opacity:.4')}, g));
    n('circle', {cx: 70, cy: 115, r: 10, s: box(FG)}, g);
    const mkEnd = (st, sc)=>U.map((_, i)=>{const e = O(g, GX, ey(SP[0], i)); n('circle', {r: 6, s: st}, e); gsap.set(e, {autoAlpha: 0, scale: sc}); return e;});
    const ends = mkEnd(`fill:${CD};stroke:${MUT};stroke-width:3`, 1), hits = mkEnd(`fill:${PF};stroke:${PT};stroke-width:3`, .2);
    const dots = [0, 1, 2].map(i=>{n('circle', {cx: 52 + i * 26, cy: 205, r: 5, s: fl(MUT, 'opacity:.35')}, g); const d = O(g, 52 + i * 26, 205); n('circle', {r: 5, s: fl(PT)}, d); gsap.set(d, {autoAlpha: 0, scale: .3}); return d;});
    const txt = [['Early attempts: scattered', '초반 시도: 흩어짐'], ['More practice: tighter', '연습이 늘면: 더 모임'], ['Trained: attempts reach the goal', '학습 후: 시도가 목표에 닿음']];
    swap(tl, txt.map(t=>T(g, 128, 211, t[0], t[1], 20, `fill:${FG}`)), [2.2, 5.4, 8.8]);
    const was = i=>SP.findIndex(s=>hit(s, i)), win = [.4, 4.9, 8.3];
    tl.fromTo(pulse, {autoAlpha: .8}, {autoAlpha: 0, duration: 1.4, ease: 'sine.out', repeat: 6}, 0).fromTo(pr, {attr: {r: 22}}, {attr: {r: 36}, duration: 1.4, ease: 'sine.out', repeat: 6}, 0);
    tl.to(dots[0], {autoAlpha: 1, scale: 1, duration: .4, ease: 'back.out(3)'}, .4).to(dots[1], {autoAlpha: 1, scale: 1, duration: .4, ease: 'back.out(3)'}, 3.6).to(dots[2], {autoAlpha: 1, scale: 1, duration: .4, ease: 'back.out(3)'}, 7);
    tl.to(path, {strokeDashoffset: 0, duration: .85, stagger: .12}, .4);
    U.forEach((_, i)=>{
      const t0 = .4 + i * .12 + .85;
      tl.to(ends[i], {autoAlpha: 1, duration: .15}, t0);
      [[3.6, 1], [7, 2]].forEach(([t, k])=>tl.to([path[i]], {attr: {d: dr(SP[k], i)}, duration: 1.3, ease: 'power3.inOut'}, t + i * .05).to([ends[i], hits[i]], {y: ey(SP[k], i), duration: 1.3, ease: 'power3.inOut'}, t + i * .05));
      const k = was(i), tp = k === 0 ? t0 : win[k] + 0.35 + i * .05;
      tl.to(hits[i], {autoAlpha: 1, scale: 1, duration: .4, ease: 'back.out(3)'}, tp).to(path[i], {opacity: .95, duration: .3}, tp);
   });
    io(tl, g, P); m.play(tl, {rest: 9.6});
 });

  // scene-14
  MOTION.gs('scene-14', (el, m)=>{
    const P = 13, {svg, g} = m.svg(640, 220, 'Two robots meet at a narrow gate, one yields, and the group forms a ring', '좁은 문에서 마주친 로봇 중 한 대가 양보하고 무리가 고리를 만듭니다');
    const {n, O, tl} = kit(m), CX = 540, CY = 110, RD = 44, slot = i=>[CX + RD * Math.cos(i * 60 * R), CY + RD * Math.sin(i * 60 * R)];
    n('rect', {x: 312, y: 14, width: 16, height: 84, rx: 6, s: box(FG)}, g); n('rect', {x: 312, y: 122, width: 16, height: 84, rx: 6, s: box(FG)}, g);
    n('rect', {x: 30, y: 30, width: 200, height: 160, rx: 22, s: sk(LN, 2, 'stroke-dasharray:3 8')}, g);
    const links = Array.from({length: 6}, (_, i)=>{const a = slot(i), b = slot((i + 1) % 6); return n('line', {x1: a[0], y1: a[1], x2: b[0], y2: b[1], s: sk(PT, 3, 'opacity:.8')}, g);});
    const alarm = O(g, 320, 110); n('circle', {r: 10, s: ring(BAD, 3)}, alarm); gsap.set([alarm, ...links], {autoAlpha: 0});
    const P0 = [[70, 60], [130, 150], [175, 85], [95, 112], [185, 160]], fol = P0.map(p=>O(g, p[0], p[1])), jit = fol.map(f=>n('circle', {r: 9, s: `fill:${PF};stroke:${PT};stroke-width:2`}, f));
    const bot = (c, x)=>{const r = O(g, x, 110); n('circle', {r: 10.5, s: `fill:${c};stroke:${FG};stroke-width:2.5`}, r); const h = n('circle', {r: 15, s: ring(BAD, 3)}, r); gsap.set(h, {autoAlpha: 0}); return [r, h];};
    const [Lb, Lh] = bot(PF, 250), [Rb, Rh] = bot(AM, 450), sL = slot(0);
    tl.to(Lb, {x: 306, duration: 1.2}, 1).to(Rb, {x: 334, duration: 1.2}, 1)
      .to([Lb, Rb], {scale: 1.2, duration: .1, yoyo: true, repeat: 1}, 2.2)
      .to([Lh, Rh], {autoAlpha: 1, duration: .15}, 2.4).to([Lh, Rh], {autoAlpha: 0, duration: .3}, 3.6)
      .set(alarm, {autoAlpha: 1}, 2.4).to(alarm, {attr: {r: 34}, autoAlpha: 0, duration: .7, repeat: 1}, 2.4)
      .to(Rb, {x: 342, duration: .2}, 3.6).to(Rb, {x: 402, y: 58, duration: .9, ease: 'power3.inOut'}, 3.8)
      .to(Lb, {x: 430, duration: 1.2, ease: 'power2.inOut'}, 4.4).to(Lb, {x: sL[0], y: sL[1], duration: 1.4, ease: 'back.out(1.1)'}, 5.6)
      .to(Rb, {x: 334, y: 110, duration: .9, ease: 'power2.inOut'}, 9).to(Rb, {x: 205, duration: 1.3, ease: 'power2.inOut'}, 9.9);
    fol.forEach((f, k)=>{
      const a = 5 + .45 * k, s = slot(k + 1), d = .28 + .03 * k;
      tl.to(jit[k], {x: 2.5, y: -2, duration: d, ease: 'sine.inOut', yoyo: true, repeat: 2 * Math.floor(a / (2 * d)) - 1}, 0)
        .to(f, {keyframes: [{x: 290, y: 110, duration: 1.3, ease: 'power1.in'}, {x: 350, y: 110, duration: .6, ease: 'none'}, {x: s[0], y: s[1], duration: 1.5, ease: 'back.out(1.2)'}], ease: 'none'}, a);
   });
    tl.to(links, {autoAlpha: .8, duration: .8, stagger: .08}, 9.4);
    io(tl, g, P); m.play(tl, {rest: 12});
 });

  // scene-15
  MOTION.gs('scene-15', (el, m)=>{
    const P = 10, {svg, g} = m.svg(640, 220, 'A stop signal sweeps out and the robot halts before the guard line', '정지 신호가 퍼지고 로봇이 가드 라인 앞에서 멈춥니다');
    const {n, T, O, tl} = kit(m), RY = 176, S = 1.5, V = 105, A = 140, TS = 4.2, BTX = 300, BTY = 44, tr = TS + .33, td = V / A;
    n('line', {x1: 30, y1: RY, x2: 610, y2: RY, s: sk(FG, 3)}, g);
    const gz = n('g', {}, g);
    n('rect', {x: 540, y: 96, width: 72, height: 80, rx: 8, s: `fill:${AM};fill-opacity:.12;stroke:${AM};stroke-width:2.5;stroke-dasharray:5 5`}, gz);
    for (let i = 0; i < 4; i++) n('line', {x1: 552 + i * 15, y1: 172, x2: 566 + i * 15, y2: 100, s: sk(AM, 2.5, 'opacity:.55')}, gz);
    n('line', {x1: 540, y1: 80, x2: 540, y2: RY, s: sk(AM, 3.5)}, g); n('line', {x1: BTX, y1: BTY + 14, x2: BTX, y2: BTY + 40, s: sk(FG, 3)}, g);
    const btn = O(g, BTX, BTY); n('circle', {r: 15, s: `fill:${BAD};stroke:${FG};stroke-width:2.5`}, btn); n('rect', {x: -6, y: -6, width: 12, height: 12, rx: 2, s: fl('#fff')}, btn);
    const waves = [6, 3].map(w=>{const r = O(g, BTX, BTY); return [r, n('circle', {r: 15, s: ring(BAD, w)}, r)];});
    const b = bolt(n, g, 70, RY, S);
    T(g, 40, 211, 'speed', '속도', 20, `fill:${MUT}`); n('rect', {x: 120, y: 201, width: 110, height: 10, rx: 5, s: ring(LN, 2)}, g);
    const sb = n('rect', {x: 120, y: 201, width: 0, height: 10, rx: 5, s: fl(PF)}, g);
    const done = O(g, 0, 0); n('rect', {x: 300, y: 190, width: 128, height: 28, rx: 14, s: box(OK)}, done); n('path', {d: 'M312 204l5 5l9-11', s: sk(OK, 3)}, done); T(done, 334, 210, 'stopped', '정지', 20, `fill:${OK};font-weight:700`); gsap.set(done, {autoAlpha: 0});
    const x1 = 70 + .5 * V, x2 = x1 + V * (tr - 1.6), x3 = x2 + V * V / (2 * A);
    tl.to(b.mv, {x: x1, duration: 1, ease: 'power1.in'}, .6).to(b.mv, {x: x2, duration: tr - 1.6, ease: 'none'}, 1.6).to(b.mv, {x: x3, duration: td, ease: 'power1.out'}, tr)
      .to(sb, {attr: {width: 110}, duration: 1, ease: 'none'}, .6).to(sb, {attr: {width: 0}, duration: td, ease: 'none'}, tr)
      .to(b.mv, {rotation: 4, duration: td * .6}, tr).to(b.mv, {rotation: 0, duration: .9, ease: 'elastic.out(1,.35)'}, tr + td * .6)
      .to(btn, {scale: .82, duration: .1}, TS).to(btn, {scale: 1, duration: .6, ease: 'elastic.out(1,.4)'}, TS + .1);
    waves.forEach((w, i)=>{blip(tl, w[0], TS + i * .15, {duration: .7, ease: 'none'}); tl.to(w[1], {attr: {r: 435}, duration: .7, ease: 'none'}, TS + i * .15);});
    tl.to(b.gaze, {x: 2, duration: .3}, TS).to(b.gaze, {x: 0, duration: .5}, 6.4)
      .to(b.ants[0], {opacity: 1, duration: .12}, tr).to(b.ants[0], {opacity: 0, duration: .15}, tr + td).to(b.ants[1], {opacity: 1, duration: .3}, tr + td)
      .to(done, {autoAlpha: 1, duration: .4, ease: 'back.out(2.5)'}, tr + td)
      .to(gz, {opacity: .6, duration: 1.2, ease: 'sine.inOut', yoyo: true, repeat: 7}, 0);
    io(tl, g, P); m.play(tl, {rest: 7.4});
 });

  // scene-16
  MOTION.gs('scene-16', (el, m)=>{
    const P = 11, {svg, g} = m.svg(640, 220, 'Bolt has an arm pick and place a cube, then spins in joy', 'Bolt가 팔로 상자를 옮기고 기뻐서 한 바퀴 돕니다');
    const {n, O, tl} = kit(m), FY = 190, SX = 380, SY = 160, L = 80, S = 1.5, BX = 160, oy = FY - 61 * S, A = {x: 420, y: 60, arc: 0, r: 9};
    n('line', {x1: 30, y1: FY, x2: 610, y2: FY, s: sk(FG, 3)}, g); n('rect', {x: 425, y: FY - 6, width: 50, height: 6, rx: 3, s: box(FG)}, g);
    n('rect', {x: 485, y: FY - 6, width: 50, height: 6, rx: 3, s: `fill:${CD};stroke:${PT};stroke-width:2.5;stroke-dasharray:4 4`}, g);
    n('rect', {x: SX - 17, y: SY + 4, width: 34, height: FY - SY - 4, rx: 7, s: box(FG)}, g);
    const cube = O(g, 450, FY - 17); n('rect', {x: -11, y: -11, width: 22, height: 22, rx: 5, s: `fill:${PF};stroke:${FG};stroke-width:2.5`}, cube);
    const ck = O(g, 510, 138); n('circle', {r: 16, s: box(OK)}, ck); n('path', {d: 'M-7 1l5 5l9-11', s: sk(OK, 3.5)}, ck); gsap.set(ck, {autoAlpha: 0, scale: .4});
    const armO = n('polyline', {s: sk(FG, 12)}, g), armI = n('polyline', {s: sk(CD, 6)}, g);
    n('circle', {cx: SX, cy: SY, r: 7, s: `fill:${PF};stroke:${FG};stroke-width:2.5`}, g);
    const grip = n('g', {}, g), clL = n('path', {s: sk(FG, 4)}, grip), clR = n('path', {s: sk(FG, 4)}, grip); n('circle', {r: 5, s: fl(FG)}, grip);
    const sp = Array.from({length: 9}, (_, i)=>{const e = O(g, BX, oy + 10 * S); n('circle', {r: 3.5, s: fl(i % 2 ? PF : AM)}, e); gsap.set(e, {autoAlpha: 0}); return e;});
    const b = bolt(n, g, BX, FY, S), ping = O(g, BX, oy + 4.5 * S), pr = n('circle', {r: 4, s: ring(PT, 3)}, ping);
    const ik = (tx, ty)=>{const dx = tx - SX, dy = ty - SY, h = Math.hypot(dx, dy), d = Math.min(2 * L - 1, h), gm = Math.acos(d / (2 * L)), a = Math.atan2(dy, dx) - gm; return [SX + L * Math.cos(a), SY + L * Math.sin(a), SX + dx * d / h, SY + dy * d / h];};
    tl.to(A, {x: 450, y: 136, duration: 1.2, ease: 'power2.inOut'}, .6).to(A, {y: 163, duration: .6}, 1.8).to(A, {r: 3, duration: .3}, 2.4).to([A, cube], {y: '-=38', duration: .6}, 2.7)
      .to([A, cube], {x: 510, duration: 1.7, ease: 'power2.inOut'}, 3.3).to(A, {arc: -14, duration: .85, ease: 'sine.out'}, 3.3).to(A, {arc: 0, duration: .85, ease: 'sine.in'}, 4.15)
      .to([A, cube], {y: '+=38', duration: .6}, 5).to(A, {r: 9, duration: .3}, 5.6).to(A, {x: 420, y: 60, duration: .9, ease: 'power2.inOut'}, 5.9)
      .to(cube, {y: '-=14', duration: .85, ease: 'sine.out'}, 3.3).to(cube, {y: '+=14', duration: .85, ease: 'sine.in'}, 4.15)
      .to(ck, {autoAlpha: 1, scale: 1, duration: .5, ease: 'back.out(3)'}, 6.5);
    [.6, 5.9].forEach(t=>{blip(tl, ping, t, {duration: .6, ease: 'power2.in'}); tl.set(pr, {attr: {r: 4}}, t).to(pr, {attr: {r: 26}, duration: .6}, t);});
    tl.to(b.gaze, {x: 3, duration: 1.2}, .6).to(b.gaze, {x: 0, duration: 1.2}, 5.6)
      .to(b.sq, {scaleY: .86, duration: .22}, 6.65).to(b.sq, {scaleY: 1.06, duration: .2}, 6.9).to(b.sq, {scaleY: 1, duration: .3, ease: 'power2.inOut'}, 7.1)
      .to(b.mv, {y: FY - 30, duration: .8}, 6.9).to(b.mv, {y: FY, duration: .8, ease: 'power2.in'}, 7.7)
      .to(b.sp, {scaleX: -1, duration: .8, ease: 'sine.inOut'}, 6.9).to(b.sp, {scaleX: 1, duration: .8, ease: 'sine.inOut'}, 7.7)
      .to(b.sq, {scaleY: .88, duration: .12}, 8.5).to(b.sq, {scaleY: 1, duration: .55, ease: 'elastic.out(1,.4)'}, 8.62)
      .to(b.idle, {autoAlpha: 0, duration: .3}, 6.9).to(b.cheer, {autoAlpha: 1, duration: .3}, 6.9).to(b.idle, {autoAlpha: 1, duration: .4}, 9.6).to(b.cheer, {autoAlpha: 0, duration: .4}, 9.6)
      .to(sp, {x: i=>BX + 126 * Math.cos(i / 9 * 2 * Math.PI - Math.PI / 2), y: i=>oy + 10 * S + 76 * Math.sin(i / 9 * 2 * Math.PI - Math.PI / 2), duration: 1.6, stagger: .02}, 7)
      .set(sp, {autoAlpha: 1}, 7).to(sp, {autoAlpha: 0, duration: .7, ease: 'power1.in', stagger: .02}, 7.9);
    io(tl, g, P);
    m.play(tl, {rest: 9, draw() {
      const k = ik(A.x, A.y + A.arc), pts = `${SX},${SY} ${f1(k[0])},${f1(k[1])} ${f1(k[2])},${f1(k[3])}`;
      armO.setAttribute('points', pts); armI.setAttribute('points', pts); grip.setAttribute('transform', `translate(${f1(k[2])} ${f1(k[3])})`);
      clL.setAttribute('d', `M${-A.r} 2v12`); clR.setAttribute('d', `M${A.r} 2v12`);
   }});
 });
})();
