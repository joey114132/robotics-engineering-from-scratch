// 토이: watchdog-budget (timeout 이 정지 거리 예산 안에 들어가는가)
(() => {
  const F = '-apple-system,"Pretendard","Noto Sans KR",system-ui,sans-serif';
  const T = (g, s, x, y, c, a = 'left', w = '') => { g.font = `${w} 12px ${F}`; g.fillStyle = c; g.textAlign = a; g.fillText(s, x, y); };
  const L = (g, x1, y1, x2, y2, c, w = 1, d = []) => { g.beginPath(); g.setLineDash(d); g.strokeStyle = c; g.lineWidth = w; g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); g.setLineDash([]); };
  // one shared theme observer per file; a toy redraws for theme/language only while on screen, otherwise on its next view
  const subs = new Set(); let mo, mq;
  const onTheme = () => subs.forEach(f => f());
  const live = (ctx, draw, el) => {
    let vis = true, stale = false;
    const f = () => { if (vis) draw(); else stale = true; };
    const io = new IntersectionObserver(es => { vis = es[es.length - 1].isIntersecting; if (vis && stale) { stale = false; draw(); } });
    io.observe(el); ctx.onRedraw(f);
    if (!subs.size) { mo = new MutationObserver(onTheme); mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] }); mq = matchMedia('(prefers-color-scheme: dark)'); mq.addEventListener('change', onTheme); }
    subs.add(f);
    ctx.onDispose(() => { io.disconnect(); subs.delete(f); if (!subs.size) { mo.disconnect(); mq.removeEventListener('change', onTheme); } });
  };
  // slider events only mark the toy dirty; one redraw per frame, latest value wins
  const soon = (ctx, f) => { let q = 0; ctx.onDispose(() => cancelAnimationFrame(q)); return () => { q = q || requestAnimationFrame(() => { q = 0; f(); }); }; };
  // lesson main.py simulate() with q_lim large (so the joint is never clamped); the 1.5 rad limit is judged on q afterwards
  const A = 8, J = 0.5, B = 0.2, KV = 20, DT = 1e-3, QLIM = 1.5;
  const tr = new Float64Array(12000);
  function sim(stop, timeout, v0) {
    const tLoss = 1 / v0, n = 12000;   // tr is one shared buffer: the result is drawn before the next run
    let q = 0, v = v0, last = 0, trip = -1, qLoss = 0, qTrip = 0, done = false;
    for (let i = 0; i < n; i++) {
      const t = i * DT;
      if (t < tLoss && i % 10 === 0) last = t;
      if (!done && t >= tLoss) { qLoss = q; done = true; }
      if (trip < 0 && t - last > timeout) { trip = t; qTrip = q; }
      let tau = KV * (v0 - v);
      if (trip >= 0) tau = stop === 'cut' ? 0 : -Math.sign(v) * Math.min(J * A, J * Math.abs(v) / DT);
      v += (tau - B * v) / J * DT; q += v * DT; tr[i] = q;
    }
    return { tr, tLoss, qLoss, trip, qTrip, qEnd: q };
  }

  window.TOYS['watchdog-budget'] = (el, ctx) => {
    ctx.title('Watchdog timeout against the room to stop', 'Watchdog timeout 과 멈출 수 있는 여유');
    const go = soon(ctx, () => draw());
    const { c, g, w, h } = ctx.canvas(360, 250);
    let ms = 50, v0 = 2, stop = 'ramp', ro;
    const btn = document.createElement('button');
    btn.type = 'button'; btn.style.cssText = 'margin:8px 0 2px;min-height:44px;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:6px 14px;font-size:13px;cursor:pointer';
    btn.onclick = () => { stop = stop === 'ramp' ? 'cut' : 'ramp'; draw(); };
    el.appendChild(btn);
    function draw() {
      if (!ro) return;   // sliders call draw before the readout exists
      const r = sim(stop, ms / 1000, v0), travel = r.qTrip - r.qLoss, brake = r.qEnd - r.qTrip, hit = r.qEnd >= QLIM;
      const brakeNeed = v0 * v0 / (2 * A), maxT = (0.5 - brakeNeed) / v0;
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), ok = ctx.color('--ok'), bad = ctx.color('--bad'), ln = ctx.color('--line');
      g.clearRect(0, 0, w, h);
      // budget bar: room from the loss point to the limit, filled by travel during the timeout then by the stop
      const bx = 12, bw = 336, room = QLIM - r.qLoss, sc = bw / (2 * room), seg = (a, b, col) => { g.fillStyle = col; g.fillRect(bx + Math.min(a * sc, bw), 34, Math.max(0, Math.min(b * sc, bw) - Math.min(a * sc, bw)), 18); };
      T(g, ctx.t('after the commands stop: room, travel during timeout, stop', '명령이 끊긴 뒤: 여유, timeout 동안 이동, 정지'), bx, 16, mut);
      g.fillStyle = ln; g.fillRect(bx, 34, room * sc, 18);
      seg(0, travel, acc); seg(travel, travel + brake, hit ? bad : ok);
      L(g, bx + room * sc, 28, bx + room * sc, 58, fg, 2);
      T(g, ctx.t('limit', '한계'), bx + room * sc, 72, fg, 'center');
      // position after the loss
      const Lm = 40, Rm = 10, Tp = 92, Bt = 26, pw = w - Lm - Rm, ph = h - Tp - Bt, t0 = r.tLoss - 0.25, span = 1.0, ytop = QLIM + 0.4, ybot = r.qLoss - 0.15;
      const X = t => Lm + (t - t0) / span * pw, Y = q => Tp + (ytop - Math.min(ytop, q)) / (ytop - ybot) * ph;
      [ybot + 0.15, 1, QLIM].forEach(t => L(g, Lm, Y(t), Lm + pw, Y(t), ln)); L(g, Lm, Y(QLIM), Lm + pw, Y(QLIM), fg, 1.5, [5, 4]);
      T(g, QLIM, Lm - 4, Y(QLIM) + 4, fg, 'right'); T(g, ctx.t('rad', 'rad'), Lm - 4, Y(1) + 4, mut, 'right');
      g.beginPath(); g.strokeStyle = hit ? bad : acc; g.lineWidth = 2.2;
      for (let i = Math.round(t0 / DT), k = 0; i < Math.round((t0 + span) / DT); i += 4, k++) k ? g.lineTo(X(i * DT), Y(r.tr[i])) : g.moveTo(X(i * DT), Y(r.tr[i])); g.stroke();
      L(g, X(r.tLoss), Tp, X(r.tLoss), Tp + ph, mut, 1, [3, 3]); L(g, X(r.trip), Tp, X(r.trip), Tp + ph, ok, 1, [3, 3]);
      T(g, ctx.t('commands stop', '명령 끊김'), X(r.tLoss) - 3, Tp + 12, mut, 'right'); T(g, ctx.t('trip', 'trip'), X(r.trip) + 3, Tp + 28, ok);
      T(g, ctx.t('joint angle after the loss (1 s)', '끊긴 뒤 관절 각도 (1초)'), w - Rm, h - 8, mut, 'right');
      const mt = maxT > 0 ? ctx.t(`ramped braking only: longest safe timeout ${maxT.toFixed(3)} s`, `ramp 제동에만 적용: 안전한 최대 timeout ${maxT.toFixed(3)} s`) : ctx.t(`ramped braking: no timeout is safe (braking alone needs ${brakeNeed.toFixed(2)} rad of 0.5)`, `ramp 제동: 안전한 timeout 없음 (제동만 ${brakeNeed.toFixed(2)} rad, 여유 0.5)`);
      ro.textContent = mt + ctx.t(` · timeout ${(ms / 1000).toFixed(3)} s → stops after ${(travel + brake).toFixed(2)} rad, ${hit ? 'passes the 1.5 rad limit' : 'stops short of the limit'}`,
        ` · timeout ${(ms / 1000).toFixed(3)} s → ${(travel + brake).toFixed(2)} rad 뒤 정지, ${hit ? '1.5 rad 한계를 넘음' : '한계 앞에서 멈춤'}`);
      btn.textContent = stop === 'ramp' ? ctx.t('stop: ramped brake, tap for torque cut', '정지: ramp 제동, 눌러서 토크 차단') : ctx.t('stop: torque cut, tap for ramped brake', '정지: 토크 차단, 눌러서 ramp 제동');
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    }
    ctx.slider('watchdog timeout (ms)', 'watchdog timeout (ms)', 20, 300, 5, ms, v => { ms = v; go(); });
    ctx.slider('joint speed (rad/s)', '관절 속도 (rad/s)', 1, 4, 0.5, v0, v => { v0 = v; go(); });
    ro = ctx.readout(); live(ctx, draw, el); draw();
  };
})();
