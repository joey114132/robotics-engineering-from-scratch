// 인터랙티브 toy 5종: kalman, diff-drive, particle-filter, rrt, pendulum-balance (바닐라 JS, canvas + slider)
(function () {
  const TAU = Math.PI * 2;
  const randn = () => { let u = 0; while (!u) u = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * Math.random()); };
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const wrap = a => Math.atan2(Math.sin(a), Math.cos(a));
  const reduceMq = matchMedia('(prefers-reduced-motion: reduce)');
  const darkMq = matchMedia('(prefers-color-scheme: dark)');
  const FONT = '13px -apple-system, "Pretendard", "Noto Sans KR", system-ui, sans-serif';
  const lab = x => (typeof x === 'function' ? x() : x);

  // ---- shared widgets -------------------------------------------------------------------------
  function bar(el) {
    const d = document.createElement('div');
    Object.assign(d.style, { display: 'flex', flexWrap: 'wrap', gap: '8px', margin: '8px 0 2px' });
    el.appendChild(d);
    return d;
  }
  function btn(box, ctx, en, ko, fn) {
    const b = document.createElement('button');
    b.type = 'button';
    Object.assign(b.style, { font: 'inherit', fontSize: '14px', padding: '6px 14px', border: '1px solid var(--line)', borderRadius: '999px', background: 'var(--card)', color: 'var(--fg)', cursor: 'pointer', touchAction: 'manipulation' });
    const set = () => { b.textContent = ctx.t(lab(en), lab(ko)); };
    set(); ctx.onRedraw(set);
    b.addEventListener('click', () => { fn(); set(); });
    box.appendChild(b);
    return b;
  }
  function txt(g, s, x, y, col, align, font) {
    g.fillStyle = col; g.textAlign = align || 'left'; g.textBaseline = 'alphabetic'; g.font = font || FONT; g.fillText(s, x, y);
  }
  function setText(div, html) { if (div._h !== html) { div._h = html; div.innerHTML = html; } }

  // animation runner: rAF loop that pauses off-screen, honours reduced motion, redraws on theme/language change.
  // o = {step(dt), draw(g, pal), warm, chunk}; returns {redraw, advance, reduced}
  function run(ctx, cv, box, o) {
    const pal = {};
    const refresh = () => { for (const k of ['fg', 'mut', 'acc', 'ok', 'bad', 'line', 'bg']) pal[k] = ctx.color('--' + k); };
    const redraw = () => { refresh(); o.draw(cv.g, pal); };
    let vis = true, last = 0, raf = 0, dead = false;
    const loop = t => {
      raf = 0;
      if (dead || !vis || reduceMq.matches) return;
      o.step(clamp((t - last) / 1000, 0, 0.05)); last = t;
      o.draw(cv.g, pal);
      raf = requestAnimationFrame(loop);
    };
    const start = () => { if (!dead && !raf && vis && !reduceMq.matches) { last = performance.now(); raf = requestAnimationFrame(loop); } };
    const advance = () => { for (let i = 0; i < (o.chunk || 30); i++) o.step(1 / 60); redraw(); };
    const stepBtn = btn(box, ctx, 'Step ▶', '한 걸음 ▶', advance);
    const sync = () => { stepBtn.hidden = !reduceMq.matches; if (reduceMq.matches) { cancelAnimationFrame(raf); raf = 0; redraw(); } else start(); };
    for (let i = 0; i < (reduceMq.matches ? (o.warm || 0) : 0); i++) o.step(1 / 60);
    refresh(); o.draw(cv.g, pal);
    sync();
    reduceMq.addEventListener('change', sync);
    ctx.onRedraw(redraw);
    darkMq.addEventListener('change', redraw);
    const mo = new MutationObserver(redraw);
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'lang', 'class'] });
    let io = null;
    if ('IntersectionObserver' in window) {
      io = new IntersectionObserver(es => { vis = es[es.length - 1].isIntersecting; if (vis) start(); else { cancelAnimationFrame(raf); raf = 0; } });
      io.observe(cv.c);
    }
    // the core calls this when the toy is torn down (lesson removed, or the toy is far from the screen)
    ctx.onDispose(() => { dead = true; cancelAnimationFrame(raf); raf = 0; reduceMq.removeEventListener('change', sync); darkMq.removeEventListener('change', redraw); mo.disconnect(); if (io) io.disconnect(); });
    return { redraw, advance, reduced: () => reduceMq.matches };
  }
  function pointer(cv, fn) {
    cv.c.style.touchAction = 'none';
    const at = e => { const r = cv.c.getBoundingClientRect(); return [(e.clientX - r.left) / r.width * cv.w, (e.clientY - r.top) / r.height * cv.h]; };
    cv.c.addEventListener('pointerdown', e => { cv.c.setPointerCapture(e.pointerId); const p = at(e); fn('down', p[0], p[1]); });
    cv.c.addEventListener('pointermove', e => { if (e.buttons) { const p = at(e); fn('move', p[0], p[1]); } });
  }
  function niceStep(raw) { const p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p; return (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p; }

  // ---- 1. Kalman filter (lesson 07/02): x=[pos, vel], F=[[1,dt],[0,1]], G=[dt^2/2, dt], Q = sa^2 G G^T, H=[1 0] ----
  window.TOYS['kalman'] = (el, ctx) => {
    ctx.title('Kalman filter: how much should it trust the sensor?', '칼만 필터: 센서를 얼마나 믿을까?');
    const cv = ctx.canvas(420, 260), W = cv.w, H = cv.h;
    const out = ctx.readout();
    const DT = 1.0, N = 60, RATE = 5, TRUE_SA = 0.1, TRUE_R = 2.0; // same numbers as lesson 07/02 code/main.py
    let qs = TRUE_SA, rs = TRUE_R, r = null;
    let truth, vel, x, v, P, k0, acc, lo, hi, hist;
    const poke = () => { if (r) r.redraw(); };
    function target() {
      let mn = Infinity, mx = -Infinity;
      for (const h of hist) { mn = Math.min(mn, h.t); mx = Math.max(mx, h.t); }
      const span = Math.max(mx - mn, 8), mid = (mx + mn) / 2;
      return [mid - span * 0.65, mid + span * 0.65];
    }
    function reset() {
      truth = 0; vel = 1; x = truth + 2 * randn(); v = 1; P = [4, 0, 0, 1]; k0 = 0.5; acc = 0; hist = [];
      hist.push({ t: truth, z: truth, x, s: 2 }); [lo, hi] = target();
    }
    function tick() {
      const a = TRUE_SA * randn();
      truth += vel * DT + 0.5 * a * DT * DT; vel += a * DT;
      const z = truth + TRUE_R * randn();
      const g0 = DT * DT / 2, g1 = DT, q = qs * qs;
      x += v * DT; // predict
      const p00 = P[0] + DT * (P[1] + P[2]) + DT * DT * P[3] + q * g0 * g0, p01 = P[1] + DT * P[3] + q * g0 * g1, p11 = P[3] + q * g1 * g1;
      const S = p00 + rs * rs, K0 = p00 / S, K1 = p01 / S, y = z - x; // update
      x += K0 * y; v += K1 * y; k0 = K0;
      P = [(1 - K0) * p00, (1 - K0) * p01, (1 - K0) * p01, p11 - K1 * p01];
      hist.push({ t: truth, z, x, s: Math.sqrt(P[0]) });
      if (hist.length > N) hist.shift();
      const [tl, th] = target(); lo += (tl - lo) * 0.2; hi += (th - hi) * 0.2;
    }
    function draw(g, c) {
      g.clearRect(0, 0, W, H);
      const L = 40, R = W - 10, T = 34, B = H - 26, y = val => B - (val - lo) / (hi - lo) * (B - T), px = i => L + i / (N - 1) * (R - L);
      g.font = FONT; g.lineWidth = 1;
      const st = niceStep((hi - lo) / 4);
      for (let gv = Math.ceil(lo / st) * st; gv < hi; gv += st) {
        g.strokeStyle = c.line; g.beginPath(); g.moveTo(L, y(gv)); g.lineTo(R, y(gv)); g.stroke();
        txt(g, String(Math.round(gv * 10) / 10), L - 5, y(gv) + 4, c.mut, 'right', '12px ' + FONT.slice(5));
      }
      g.save(); g.beginPath(); g.rect(L, T, R - L, B - T); g.clip();
      g.fillStyle = c.acc; g.globalAlpha = 0.2; g.beginPath();
      hist.forEach((h, i) => { const f = i ? g.lineTo : g.moveTo; f.call(g, px(i), y(h.x + 2 * h.s)); });
      for (let i = hist.length - 1; i >= 0; i--) g.lineTo(px(i), y(hist[i].x - 2 * hist[i].s));
      g.closePath(); g.fill(); g.globalAlpha = 1;
      g.fillStyle = c.mut; hist.forEach((h, i) => { g.beginPath(); g.arc(px(i), y(h.z), 2.2, 0, TAU); g.fill(); });
      const path = (key, col, w) => { g.strokeStyle = col; g.lineWidth = w; g.lineJoin = 'round'; g.beginPath(); hist.forEach((h, i) => (i ? g.lineTo : g.moveTo).call(g, px(i), y(h[key]))); g.stroke(); };
      path('t', c.fg, 2); path('x', c.acc, 2.4);
      g.restore();
      // legend
      const items = [[ctx.t('truth', '실제'), c.fg, 'line'], [ctx.t('sensor', '센서'), c.mut, 'dot'], [ctx.t('estimate', '추정값'), c.acc, 'line'], [ctx.t('±2σ band', '±2σ 띠'), c.acc, 'box']];
      let lx = L;
      for (const [s, col, kind] of items) {
        g.fillStyle = col; g.strokeStyle = col; g.lineWidth = 2;
        if (kind === 'line') { g.beginPath(); g.moveTo(lx, 15); g.lineTo(lx + 14, 15); g.stroke(); }
        else if (kind === 'dot') { g.beginPath(); g.arc(lx + 7, 15, 2.6, 0, TAU); g.fill(); }
        else { g.globalAlpha = 0.3; g.fillRect(lx, 9, 14, 12); g.globalAlpha = 1; }
        txt(g, s, lx + 18, 19, c.fg, 'left', '12px ' + FONT.slice(5)); lx += 24 + g.measureText(s).width;
      }
      txt(g, ctx.t('position (m)', '위치 (m)'), L, H - 8, c.mut, 'left', '12px ' + FONT.slice(5));
      txt(g, ctx.t('time →', '시간 →'), R, H - 8, c.mut, 'right', '12px ' + FONT.slice(5));
      const kk = k0.toFixed(2), msg = k0 >= 0.6 ? ctx.t('it mostly trusts the sensor: the estimate chases the dots.', '센서를 주로 믿는 상태라 추정값이 점을 따라갑니다.')
        : k0 <= 0.25 ? ctx.t('it mostly trusts its own model: the estimate is smooth but slow to react.', '자기 모델을 주로 믿는 상태라 추정값이 부드럽지만 반응이 느립니다.')
          : ctx.t('it blends the model and the sensor.', '모델과 센서를 섞어 쓰는 상태입니다.');
      setText(out, ctx.t('Kalman gain K = ', '칼만 이득 K = ') + '<b>' + kk + '</b>: ' + msg + '<br>'
        + ctx.t('Sliders (σ) are what the filter believes. The real sensor noise is ' + TRUE_R.toFixed(1) + ' m and the real push on velocity is ' + TRUE_SA.toFixed(1) + ' m/s².',
          '슬라이더(σ)는 필터가 믿는 값입니다. 실제 센서 잡음은 ' + TRUE_R.toFixed(1) + ' m, 속도에 실제로 가해지는 흔들림은 ' + TRUE_SA.toFixed(1) + ' m/s² 입니다.'));
    }
    ctx.slider('Process noise Q', '프로세스 잡음 Q', 0.01, 3, 0.01, TRUE_SA, a => { qs = a; });
    ctx.slider('Measurement noise R', '측정 잡음 R', 0.1, 6, 0.1, TRUE_R, a => { rs = a; });
    const box = bar(el);
    btn(box, ctx, 'Restart', '다시 시작', () => { reset(); poke(); });
    reset();
    let tacc = 0;
    r = run(ctx, cv, box, { warm: 720, chunk: 90, draw, step(dt) { tacc += dt * RATE; while (tacc >= 1) { tacc--; tick(); } } });
    el.addEventListener('input', poke);
  };

  // ---- 2. Differential drive (lesson 08/01) ---------------------------------------------------------
  window.TOYS['diff-drive'] = (el, ctx) => {
    ctx.title('Differential drive: two wheels make one turn', '차동 구동: 바퀴 두 개로 방향 만들기');
    const cv = ctx.canvas(420, 300), W = cv.w, H = cv.h;
    const out = ctx.readout();
    const TRACK = 0.5, PX = 80, MAXTRAIL = 900;
    let vl = 0.4, vr = 0.7, X = 0, Y = 0, TH = Math.PI / 2, trail = [], cam = { x: 0, y: 0 }, r = null;
    const poke = () => { if (r) r.redraw(); };
    function reset() { X = 0; Y = 0; TH = Math.PI / 2; trail = [[0, 0]]; cam = { x: 0, y: 0 }; }
    function step(dt) {
      const v = (vr + vl) / 2, w = (vr - vl) / TRACK;
      if (Math.abs(w) < 1e-6) { X += v * dt * Math.cos(TH); Y += v * dt * Math.sin(TH); }
      else { X += v / w * (Math.sin(TH + w * dt) - Math.sin(TH)); Y -= v / w * (Math.cos(TH + w * dt) - Math.cos(TH)); TH += w * dt; }
      const l = trail[trail.length - 1];
      if (Math.hypot(X - l[0], Y - l[1]) > 0.03) { trail.push([X, Y]); if (trail.length > MAXTRAIL) trail.shift(); }
      const hx = W / 2 / PX - 0.9, hy = H / 2 / PX - 0.9, k = Math.min(1, dt * 4);
      cam.x += (X - clamp(X - cam.x, -hx, hx) - cam.x) * k; cam.y += (Y - clamp(Y - cam.y, -hy, hy) - cam.y) * k;
    }
    function draw(g, c) {
      g.clearRect(0, 0, W, H);
      const sx = x => W / 2 + (x - cam.x) * PX, sy = y => H / 2 - (y - cam.y) * PX;
      g.fillStyle = c.mut; g.globalAlpha = 0.45;
      for (let gx = Math.floor((cam.x - W / 2 / PX) * 2) / 2; gx < cam.x + W / 2 / PX; gx += 0.5)
        for (let gy = Math.floor((cam.y - H / 2 / PX) * 2) / 2; gy < cam.y + H / 2 / PX; gy += 0.5) g.fillRect(sx(gx) - 1, sy(gy) - 1, 2, 2);
      g.globalAlpha = 1;
      const v = (vr + vl) / 2, w = (vr - vl) / TRACK, R = v / w;
      if (Math.abs(w) > 0.02 && Math.abs(v) > 0.02 && Math.abs(R) < 10) {
        const cx = X - R * Math.sin(TH), cy = Y + R * Math.cos(TH);
        g.strokeStyle = c.mut; g.lineWidth = 1; g.setLineDash([4, 4]);
        g.beginPath(); g.arc(sx(cx), sy(cy), Math.abs(R) * PX, 0, TAU); g.stroke();
        g.beginPath(); g.moveTo(sx(cx), sy(cy)); g.lineTo(sx(X), sy(Y)); g.stroke(); g.setLineDash([]);
        g.fillStyle = c.mut; g.beginPath(); g.arc(sx(cx), sy(cy), 3, 0, TAU); g.fill();
      }
      g.strokeStyle = c.acc; g.lineWidth = 2.5; g.lineJoin = 'round'; g.beginPath();
      trail.forEach((p, i) => (i ? g.lineTo : g.moveTo).call(g, sx(p[0]), sy(p[1]))); g.stroke();
      g.save(); g.translate(sx(X), sy(Y)); g.rotate(-TH);
      const bl = 0.42 * PX / 2, bw = TRACK * PX / 2, wl = 0.2 * PX / 2, ww = 0.09 * PX;
      g.fillStyle = c.bg; g.strokeStyle = c.fg; g.lineWidth = 2;
      g.beginPath(); g.rect(-bl, -bw, 2 * bl, 2 * bw); g.fill(); g.stroke();
      g.fillStyle = c.fg; g.fillRect(-wl, -bw - ww / 2, 2 * wl, ww); g.fillRect(-wl, bw - ww / 2, 2 * wl, ww);
      g.beginPath(); g.moveTo(bl + 8, 0); g.lineTo(bl - 3, -6); g.lineTo(bl - 3, 6); g.closePath(); g.fillStyle = c.acc; g.fill();
      for (const [spd, yy] of [[vl, -bw], [vr, bw]]) { // arrows on each wheel: green forward, red backward
        g.strokeStyle = spd >= 0 ? c.ok : c.bad; g.lineWidth = 3; g.beginPath(); g.moveTo(0, yy); g.lineTo(spd * PX * 0.45, yy); g.stroke();
      }
      g.restore();
      txt(g, ctx.t('left wheel', '왼쪽 바퀴') + ' ' + vl.toFixed(2) + '   ' + ctx.t('right wheel', '오른쪽 바퀴') + ' ' + vr.toFixed(2) + ' m/s', 8, H - 8, c.mut);
      let s;
      if (Math.abs(vl) < 0.02 && Math.abs(vr) < 0.02) s = ctx.t('Stopped.', '멈춰 있습니다.');
      else if (Math.abs(vr - vl) < 0.02) s = ctx.t('Straight line.', '직진입니다.') + ' v = ' + v.toFixed(2) + ' m/s';
      else if (Math.abs(vr + vl) < 0.02) s = ctx.t('Spinning in place: turning radius R = 0.', '제자리 회전입니다. 회전 반지름 R = 0.') + ' ω = ' + w.toFixed(2) + ' rad/s';
      else s = ctx.t('Turning radius R = ', '회전 반지름 R = ') + '<b>' + Math.abs(R).toFixed(2) + ' m</b> (' + (w > 0 ? ctx.t('left turn', '왼쪽으로 회전') : ctx.t('right turn', '오른쪽으로 회전')) + '), v = ' + v.toFixed(2) + ' m/s, ω = ' + w.toFixed(2) + ' rad/s';
      setText(out, s + '<br>' + ctx.t('R = (L/2)(vr+vl)/(vr−vl), with wheel spacing L = ' + TRACK + ' m.', 'R = (L/2)(vr+vl)/(vr−vl), 바퀴 간격 L = ' + TRACK + ' m.'));
    }
    ctx.slider('Left wheel', '왼쪽 바퀴', -1, 1, 0.05, vl, a => { vl = a; });
    ctx.slider('Right wheel', '오른쪽 바퀴', -1, 1, 0.05, vr, a => { vr = a; });
    const box = bar(el);
    btn(box, ctx, 'Reset', '처음으로', () => { reset(); poke(); });
    reset();
    r = run(ctx, cv, box, { chunk: 60, draw, step });
    el.addEventListener('input', poke);
  };

  // ---- 3. Particle filter localisation (lesson 08/02): same predict, weight, resample as code/main.py ----
  window.TOYS['particle-filter'] = (el, ctx) => {
    ctx.title('Particle filter: where am I?', '파티클 필터: 나는 어디에 있나?');
    const cv = ctx.canvas(420, 320), W = cv.w, H = cv.h;
    const out = ctx.readout();
    const LM = [[0, 0], [10, 0], [10, 10], [0, 10]], N = 200, DT = 0.1, V = 1.2, RC = 3, RATE = 12, SV = 0.15, SW = 0.4, S = 29, MX = 65, MY = 15;
    const sx = x => MX + x * S, sy = y => MY + (10 - y) * S;
    let sigma = 0.5, inject = true, r = null, truth, px, py, pt, est, err = 0, neff = N, zs = [0, 0, 0, 0], tacc = 0;
    const poke = () => { if (r) r.redraw(); };
    px = new Float64Array(N); py = new Float64Array(N); pt = new Float64Array(N);
    const scatter = i => { px[i] = Math.random() * 10; py[i] = Math.random() * 10; pt[i] = (Math.random() - 0.5) * TAU; };
    function reset() { truth = [8, 5, Math.PI / 2]; for (let i = 0; i < N; i++) scatter(i); est = [5, 5, 0]; zs = LM.map(l => Math.hypot(truth[0] - l[0], truth[1] - l[1])); err = Math.hypot(est[0] - truth[0], est[1] - truth[1]); neff = N; }
    function command() { // drive a circle of radius RC around the map centre; steer back to it after a kidnap
      const ang = Math.atan2(truth[1] - 5, truth[0] - 5), e = Math.hypot(truth[0] - 5, truth[1] - 5) - RC;
      return [V, clamp(V / RC + 2 * wrap(ang + Math.PI / 2 + clamp(0.8 * e, -1, 1) - truth[2]), -1.5, 1.5)];
    }
    function tick() {
      const [v, w] = command(), th = truth[2] + w * DT / 2;
      truth = [truth[0] + v * DT * Math.cos(th), truth[1] + v * DT * Math.sin(th), truth[2] + w * DT];
      zs = LM.map(l => Math.hypot(truth[0] - l[0], truth[1] - l[1]) + sigma * randn());
      const lw = new Float64Array(N); let mx = -Infinity;
      for (let i = 0; i < N; i++) {
        const vv = v + SV * randn(), ww = w + SW * randn(), t2 = pt[i] + ww * DT / 2;
        px[i] += vv * DT * Math.cos(t2); py[i] += vv * DT * Math.sin(t2); pt[i] += ww * DT;
        let s = 0; for (let j = 0; j < 4; j++) { const d = (Math.hypot(px[i] - LM[j][0], py[i] - LM[j][1]) - zs[j]) / sigma; s += d * d; }
        lw[i] = -0.5 * s; if (lw[i] > mx) mx = lw[i];
      }
      let sum = 0; for (let i = 0; i < N; i++) { lw[i] = Math.exp(lw[i] - mx); sum += lw[i]; } // subtract the max so far-away clouds cannot underflow to all zeros
      let ex = 0, ey = 0, es = 0, ec = 0, s2 = 0;
      for (let i = 0; i < N; i++) { lw[i] /= sum; ex += lw[i] * px[i]; ey += lw[i] * py[i]; es += lw[i] * Math.sin(pt[i]); ec += lw[i] * Math.cos(pt[i]); s2 += lw[i] * lw[i]; }
      est = [ex, ey, Math.atan2(es, ec)]; neff = 1 / s2; err = Math.hypot(ex - truth[0], ey - truth[1]);
      const nx = new Float64Array(N), ny = new Float64Array(N), nt = new Float64Array(N); // systematic resampling
      let cum = lw[0], j = 0; const u0 = Math.random();
      for (let i = 0; i < N; i++) { const u = (u0 + i) / N; while (u > cum && j < N - 1) cum += lw[++j]; nx[i] = px[j]; ny[i] = py[j]; nt[i] = pt[j]; }
      px = nx; py = ny; pt = nt;
      if (inject) for (let i = 0; i < Math.floor(0.05 * N); i++) scatter(i); // a few random guesses keep it able to find a robot that jumped
    }
    function kidnap(x, y) {
      if (x === undefined) { do { x = 0.5 + Math.random() * 9; y = 0.5 + Math.random() * 9; } while (Math.hypot(x - truth[0], y - truth[1]) < 4); }
      truth = [clamp(x, 0.3, 9.7), clamp(y, 0.3, 9.7), (Math.random() - 0.5) * TAU];
    }
    function draw(g, c) {
      g.clearRect(0, 0, W, H);
      g.strokeStyle = c.line; g.lineWidth = 1.5; g.strokeRect(MX, MY, 10 * S, 10 * S);
      g.save(); g.beginPath(); g.rect(MX, MY, 10 * S, 10 * S); g.clip();
      g.strokeStyle = c.mut; g.globalAlpha = 0.45; g.lineWidth = 1;
      LM.forEach((l, j) => { g.beginPath(); g.arc(sx(l[0]), sy(l[1]), Math.max(0, zs[j]) * S, 0, TAU); g.stroke(); });
      g.globalAlpha = 0.65; g.fillStyle = c.acc;
      for (let i = 0; i < N; i++) { g.beginPath(); g.arc(sx(px[i]), sy(py[i]), 1.7, 0, TAU); g.fill(); }
      g.globalAlpha = 1; g.restore();
      g.fillStyle = c.fg;
      for (const l of LM) { g.beginPath(); g.moveTo(sx(l[0]), sy(l[1]) - 7); g.lineTo(sx(l[0]) + 6, sy(l[1])); g.lineTo(sx(l[0]), sy(l[1]) + 7); g.lineTo(sx(l[0]) - 6, sy(l[1])); g.closePath(); g.fill(); }
      g.strokeStyle = c.ok; g.lineWidth = 2.5; const ex = sx(est[0]), ey = sy(est[1]);
      g.beginPath(); g.arc(ex, ey, 8, 0, TAU); g.moveTo(ex - 11, ey); g.lineTo(ex + 11, ey); g.moveTo(ex, ey - 11); g.lineTo(ex, ey + 11); g.stroke();
      g.save(); g.translate(sx(truth[0]), sy(truth[1])); g.rotate(-truth[2]);
      g.fillStyle = c.fg; g.strokeStyle = c.bg; g.lineWidth = 1.5;
      g.beginPath(); g.moveTo(11, 0); g.lineTo(-7, -7); g.lineTo(-4, 0); g.lineTo(-7, 7); g.closePath(); g.fill(); g.stroke(); g.restore();
      const small = '12px ' + FONT.slice(5), rows = [[ctx.t('robot', '로봇'), 'tri'], [ctx.t('estimate', '추정'), 'est'], [ctx.t('particles', '입자'), 'dot'], [ctx.t('landmark', '표지'), 'lm']];
      rows.forEach(([s, k], i) => {
        const y = 34 + i * 20; g.fillStyle = c.fg; g.strokeStyle = c.ok; g.lineWidth = 2;
        if (k === 'tri') { g.beginPath(); g.moveTo(14, y - 5); g.lineTo(5, y - 9); g.lineTo(5, y - 1); g.closePath(); g.fill(); }
        else if (k === 'est') { g.beginPath(); g.arc(10, y - 5, 4.5, 0, TAU); g.stroke(); }
        else if (k === 'dot') { g.fillStyle = c.acc; g.beginPath(); g.arc(10, y - 5, 2.4, 0, TAU); g.fill(); }
        else { g.beginPath(); g.moveTo(10, y - 11); g.lineTo(15, y - 5); g.lineTo(10, y + 1); g.lineTo(5, y - 5); g.closePath(); g.fill(); }
        txt(g, s, 20, y, c.fg, 'left', small);
      });
      setText(out, ctx.t('Position error ', '위치 오차 ') + '<b>' + err.toFixed(2) + ' m</b> · ' + ctx.t('effective particles ', '유효 입자 수 ') + Math.round(neff) + ' / ' + N + ' · ' + ctx.t('random particles ', '무작위 입자 ') + (inject ? ctx.t('on', '켜짐') : ctx.t('off', '꺼짐'))
        + '<br>' + ctx.t('Rings: the measured range to each landmark. Tap the map to teleport the robot.', '고리는 각 표지까지 잰 거리입니다. 지도를 탭하면 로봇을 옮깁니다.'));
    }
    ctx.slider('Sensor noise σ', '센서 잡음 σ', 0.1, 3, 0.05, sigma, a => { sigma = a; });
    const box = bar(el);
    btn(box, ctx, 'Kidnap robot', '로봇 납치', () => { kidnap(); poke(); });
    btn(box, ctx, () => 'Random particles: ' + (inject ? 'on' : 'off'), () => '무작위 입자: ' + (inject ? '켜짐' : '꺼짐'), () => { inject = !inject; });
    btn(box, ctx, 'Restart', '다시 시작', () => { reset(); poke(); });
    pointer(cv, (k, x, y) => { if (k === 'down' && x > MX && x < MX + 10 * S && y > MY && y < MY + 10 * S) { kidnap((x - MX) / S, 10 - (y - MY) / S); poke(); } });
    reset();
    r = run(ctx, cv, box, { warm: 300, chunk: 60, draw, step(dt) { tacc += dt * RATE; while (tacc >= 1) { tacc--; tick(); } } });
    el.addEventListener('input', poke);
  };

  // ---- 4. RRT (lesson 09/02): sample, nearest node, capped step, keep only if the segment is free ----
  window.TOYS['rrt'] = (el, ctx) => {
    ctx.title('RRT: grow a random tree until it finds the goal', 'RRT: 무작위 트리를 키워 목표 찾기');
    const cv = ctx.canvas(420, 300), W = cv.w, H = cv.h;
    const out = ctx.readout();
    const OBS = [[105, 90, 24, 210], [205, 0, 24, 180], [300, 110, 24, 190], [150, 160, 36, 38]], PAD = 4, MAXN = 4000, PER_SEC = 180;
    const START = [30, 262];
    let step = 20, goal = [392, 40], nx = [], ny = [], par = [], path = null, plen = 0, r = null, ready = false, budget = 0, gaveUp = false;
    const poke = () => { if (r) r.redraw(); };
    const inObs = (x, y) => OBS.some(o => x > o[0] - PAD && x < o[0] + o[2] + PAD && y > o[1] - PAD && y < o[1] + o[3] + PAD);
    function segFree(x1, y1, x2, y2) { // Liang-Barsky against each rectangle grown by PAD
      const dx = x2 - x1, dy = y2 - y1;
      for (const o of OBS) {
        let t0 = 0, t1 = 1, hit = true;
        for (const [p, q] of [[-dx, x1 - (o[0] - PAD)], [dx, o[0] + o[2] + PAD - x1], [-dy, y1 - (o[1] - PAD)], [dy, o[1] + o[3] + PAD - y1]]) {
          if (p === 0) { if (q < 0) { hit = false; break; } } else { const t = q / p; if (p < 0) { if (t > t1) { hit = false; break; } if (t > t0) t0 = t; } else { if (t < t0) { hit = false; break; } if (t < t1) t1 = t; } }
        }
        if (hit && t0 < t1) return false;
      }
      return true;
    }
    function restart() { nx = [START[0]]; ny = [START[1]]; par = [-1]; path = null; plen = 0; gaveUp = false; budget = 0; }
    function grow() {
      for (let tries = 0; tries < 80; tries++) {
        const sx = Math.random() < 0.1 ? goal[0] : Math.random() * W, sy = Math.random() < 0.1 ? goal[1] : Math.random() * H;
        let b = 0, bd = Infinity;
        for (let i = 0; i < nx.length; i++) { const d = (nx[i] - sx) ** 2 + (ny[i] - sy) ** 2; if (d < bd) { bd = d; b = i; } }
        const dist = Math.sqrt(bd); if (dist < 1e-6) continue;
        const k = Math.min(step, dist) / dist, x = nx[b] + (sx - nx[b]) * k, y = ny[b] + (sy - ny[b]) * k;
        if (!segFree(nx[b], ny[b], x, y)) continue;
        nx.push(x); ny.push(y); par.push(b);
        if (Math.hypot(x - goal[0], y - goal[1]) <= step && segFree(x, y, goal[0], goal[1])) {
          nx.push(goal[0]); ny.push(goal[1]); par.push(nx.length - 2);
          path = []; for (let i = nx.length - 1; i >= 0; i = par[i]) path.push(i);
          plen = 0; for (let i = 1; i < path.length; i++) plen += Math.hypot(nx[path[i]] - nx[path[i - 1]], ny[path[i]] - ny[path[i - 1]]);
        }
        return;
      }
    }
    function tick(dt) {
      if (path || gaveUp) return;
      budget += dt * PER_SEC;
      while (budget >= 1 && !path) { budget--; grow(); if (nx.length >= MAXN) { gaveUp = true; break; } }
    }
    function draw(g, c) {
      g.clearRect(0, 0, W, H);
      g.fillStyle = c.mut; g.strokeStyle = c.fg; g.lineWidth = 1.5;
      for (const o of OBS) { g.globalAlpha = 0.35; g.fillRect(o[0], o[1], o[2], o[3]); g.globalAlpha = 1; g.strokeRect(o[0], o[1], o[2], o[3]); }
      g.strokeStyle = c.mut; g.globalAlpha = path ? 0.5 : 0.8; g.lineWidth = 1; g.beginPath();
      for (let i = 1; i < nx.length; i++) { g.moveTo(nx[par[i]], ny[par[i]]); g.lineTo(nx[i], ny[i]); }
      g.stroke(); g.globalAlpha = 1;
      if (path) { g.strokeStyle = c.ok; g.lineWidth = 3.5; g.lineJoin = 'round'; g.beginPath(); path.forEach((i, k) => (k ? g.lineTo : g.moveTo).call(g, nx[i], ny[i])); g.stroke(); }
      g.fillStyle = c.acc; g.beginPath(); g.arc(START[0], START[1], 6, 0, TAU); g.fill();
      g.fillStyle = c.bad; g.strokeStyle = c.bg; g.lineWidth = 2; g.beginPath(); g.arc(goal[0], goal[1], 7, 0, TAU); g.fill(); g.stroke();
      txt(g, ctx.t('start', '출발'), START[0] + 10, START[1] + 4, c.fg); txt(g, ctx.t('goal', '목표'), goal[0], goal[1] + 20, c.fg, 'center');
      setText(out, (path ? ctx.t('Path found: ', '경로 발견: ') + '<b>' + Math.round(plen) + ' px</b> ' + ctx.t('long, ', '길이, ') + nx.length + ctx.t(' nodes.', ' 노드.')
        : gaveUp ? ctx.t('No path after ' + MAXN + ' nodes. Try a bigger step or move the goal.', MAXN + '개 노드로도 길을 못 찾았습니다. 보폭을 키우거나 목표를 옮겨 보세요.')
          : ctx.t('Growing: ', '키우는 중: ') + nx.length + ctx.t(' nodes...', ' 노드...'))
        + '<br>' + ctx.t('Tap or drag on the map to move the goal.', '지도를 탭하거나 끌어서 목표를 옮깁니다.'));
    }
    ctx.slider('Step size', '보폭', 5, 60, 1, step, a => { step = a; if (ready) { restart(); poke(); } });
    const box = bar(el);
    btn(box, ctx, 'Restart', '다시 시작', () => { restart(); poke(); });
    pointer(cv, (k, x, y) => { x = clamp(x, 6, W - 6); y = clamp(y, 6, H - 6); if (!inObs(x, y)) { goal = [x, y]; restart(); poke(); } });
    cv.c.tabIndex = 0; cv.c.setAttribute('role', 'application');
    cv.c.setAttribute('aria-label', ctx.t('Goal position. Arrow keys move the goal.', '목표 위치입니다. 화살표 키로 목표를 옮깁니다.'));
    cv.c.addEventListener('keydown', e => {
      const d = { ArrowLeft: [-8, 0], ArrowRight: [8, 0], ArrowUp: [0, -8], ArrowDown: [0, 8] }[e.key]; if (!d) return;
      const x = clamp(goal[0] + d[0], 6, W - 6), y = clamp(goal[1] + d[1], 6, H - 6);
      if (!inObs(x, y)) { goal = [x, y]; restart(); poke(); } e.preventDefault();
    });
    restart(); ready = true;
    r = run(ctx, cv, box, { warm: 60, chunk: 20, draw, step: tick });
  };

  // ---- 5. Inverted pendulum on a cart (lesson 10/01): theta'' = (g sin(th) - a cos(th)) / L, a = PD(theta) ----
  window.TOYS['pendulum-balance'] = (el, ctx) => {
    ctx.title('Balance the pole with a PD controller', 'PD 제어로 막대 세우기');
    const cv = ctx.canvas(420, 280), W = cv.w, H = cv.h;
    const out = ctx.readout();
    const G = 9.81, L = 1, AMAX = 20, FALL = 1.05, PXM = 120, PUSH = 1.0, GROUND = 228, PIVOT = 198;
    let kp = 25, kd = 6, th, w, cx, cvel, fell, t, dir = 1, flash = 0, r = null;
    const poke = () => { if (r) r.redraw(); };
    function reset() { th = 0.03; w = 0; cx = 0; cvel = 0; fell = false; t = 0; flash = 0; }
    function push(d) { if (fell) { reset(); return; } w += d * PUSH; flash = { d, t: 0.5 }; if (r && r.reduced()) r.advance(); }
    function sim(dt) {
      const a = fell ? -4 * cvel : clamp(kp * th + kd * w, -AMAX, AMAX); // no cart friction: an angle-only PD holds the pole but lets the cart drift
      w += ((G / L) * Math.sin(th) - (a / L) * Math.cos(th) - 0.1 * w) * dt; th += w * dt; cvel += a * dt; cx += cvel * dt;
      if (!fell) t += dt;
      if (!fell && Math.abs(th) > FALL) fell = true;
      if (fell && Math.abs(th) >= Math.PI / 2) { th = Math.sign(th) * Math.PI / 2; w = 0; }
    }
    function tick(dt) { const n = Math.max(1, Math.round(dt * 240)); for (let i = 0; i < n; i++) sim(dt / n); if (flash) { flash.t -= dt; if (flash.t <= 0) flash = 0; } }
    function draw(g, c) {
      g.clearRect(0, 0, W, H);
      const mx = W / 2, col = fell ? c.bad : c.acc;
      g.strokeStyle = c.line; g.lineWidth = 2; g.beginPath(); g.moveTo(0, GROUND); g.lineTo(W, GROUND); g.stroke();
      g.strokeStyle = c.mut; g.lineWidth = 1.5; const off = ((cx * PXM) % 30 + 30) % 30;
      for (let x = -off; x < W; x += 30) { g.beginPath(); g.moveTo(x, GROUND); g.lineTo(x - 6, GROUND + 9); g.stroke(); }
      g.fillStyle = c.fg; g.fillRect(mx - 32, PIVOT - 2, 64, 22);
      g.fillStyle = c.bg; g.strokeStyle = c.fg; g.lineWidth = 2;
      for (const dx of [-20, 20]) { g.beginPath(); g.arc(mx + dx, GROUND - 6, 6, 0, TAU); g.fill(); g.stroke(); }
      const tx = mx + Math.sin(th) * L * PXM, ty = PIVOT - Math.cos(th) * L * PXM;
      g.strokeStyle = col; g.lineWidth = 6; g.lineCap = 'round'; g.beginPath(); g.moveTo(mx, PIVOT); g.lineTo(tx, ty); g.stroke(); g.lineCap = 'butt';
      g.fillStyle = col; g.beginPath(); g.arc(tx, ty, 11, 0, TAU); g.fill();
      g.fillStyle = c.bg; g.beginPath(); g.arc(mx, PIVOT, 3, 0, TAU); g.fill();
      if (flash) { // arrow showing the push direction
        const ay = ty - 2; g.strokeStyle = c.bad; g.fillStyle = c.bad; g.lineWidth = 3;
        g.beginPath(); g.moveTo(tx + flash.d * 14, ay - 22); g.lineTo(tx + flash.d * 38, ay - 22); g.stroke();
        g.beginPath(); g.moveTo(tx + flash.d * 44, ay - 22); g.lineTo(tx + flash.d * 34, ay - 28); g.lineTo(tx + flash.d * 34, ay - 16); g.closePath(); g.fill();
      }
      if (fell) txt(g, ctx.t('Fell over', '넘어짐'), mx, 44, c.bad, 'center', 'bold 22px ' + FONT.slice(5));
      txt(g, ctx.t('tap left or right of the pole to push it', '막대 왼쪽/오른쪽을 탭하면 밀어 줍니다'), mx, H - 8, c.mut, 'center', '12px ' + FONT.slice(5));
      const crit = G / L, ok = kp > crit;
      setText(out, ctx.t('Angle θ = ', '각도 θ = ') + '<b>' + (th * 180 / Math.PI).toFixed(1) + '°</b> · ' + ctx.t('upright for ', '버틴 시간 ') + t.toFixed(1) + ' s · ' + ctx.t('cart speed ', '수레 속도 ') + cvel.toFixed(2) + ' m/s'
        + '<br>' + (ok ? ctx.t('kp = ' + kp.toFixed(0) + ' is above g/L = ' + crit.toFixed(2) + ', so the controller can hold the pole; kd sets how fast the wobble dies.', 'kp = ' + kp.toFixed(0) + ' 가 g/L = ' + crit.toFixed(2) + ' 보다 커서 막대를 세울 수 있습니다. kd 는 흔들림이 사라지는 속도를 정합니다.')
          : ctx.t('kp = ' + kp.toFixed(0) + ' is not above g/L = ' + crit.toFixed(2) + ': gravity wins and the pole will fall whatever kd is.', 'kp = ' + kp.toFixed(0) + ' 는 g/L = ' + crit.toFixed(2) + ' 보다 크지 않아서 kd 와 상관없이 중력이 이겨 넘어집니다.')));
    }
    ctx.slider('kp (angle gain)', 'kp (각도 이득)', 0, 40, 1, kp, a => { kp = a; });
    ctx.slider('kd (damping gain)', 'kd (감쇠 이득)', 0, 15, 0.5, kd, a => { kd = a; });
    const box = bar(el);
    btn(box, ctx, 'Push', '밀기', () => { push(dir); dir = -dir; poke(); });
    btn(box, ctx, 'Reset', '처음으로', () => { reset(); poke(); });
    pointer(cv, (k, x) => { if (k === 'down') { push(x < W / 2 ? 1 : -1); poke(); } });
    cv.c.tabIndex = 0; cv.c.setAttribute('role', 'application');
    cv.c.setAttribute('aria-label', ctx.t('Left and right arrow keys push the cart.', '좌우 화살표 키로 카트를 밉니다.'));
    cv.c.addEventListener('keydown', e => { if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { push(e.key === 'ArrowLeft' ? 1 : -1); poke(); e.preventDefault(); } });
    reset();
    r = run(ctx, cv, box, { chunk: 60, draw, step: tick });
    el.addEventListener('input', poke);
  };
})();
