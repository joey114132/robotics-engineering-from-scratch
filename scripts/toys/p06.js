// 토이: pinhole-depth (픽셀 하나는 광선이고, 깊이 오차는 점을 광선 위로 민다)
(() => {
  const F = '-apple-system,"Pretendard","Noto Sans KR",system-ui,sans-serif';
  const T = (g, s, x, y, c, a = 'left', w = '') => { g.font = `${w} 12px ${F}`; g.fillStyle = c; g.textAlign = a; g.fillText(s, x, y); };
  const L = (g, x1, y1, x2, y2, c, w = 1, d = []) => { g.beginPath(); g.setLineDash(d); g.strokeStyle = c; g.lineWidth = w; g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); g.setLineDash([]); };
  const dot = (g, x, y, r, c) => { g.beginPath(); g.arc(x, y, r, 0, 7); g.fillStyle = c; g.fill(); };
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

  window.TOYS['pinhole-depth'] = (el, ctx) => {
    ctx.title('One pixel, one ray: a wrong depth slides the point', '픽셀 하나는 광선 하나: 틀린 깊이는 점을 밀어냅니다');
    const go = soon(ctx, () => draw());
    const { c, g, w, h } = ctx.canvas(360, 230);
    const FX = 600, CX = 320, U = 520, DU = 0.5, S = 36, bx = 150, by = h - 16;   // lesson numbers: fx 600, cx 320, pixel (520, 240), 0.5 px
    let z = 2, pct = 1, ro;
    const unproject = (u, d) => [(u - CX) * d / FX, d];   // the y row is the principal row, so y = 0
    function draw() {
      if (!ro) return;   // sliders call draw before the readout exists
      const dz = z * pct / 100, good = unproject(U, z), bad = unproject(U + DU, z + dz);
      const tot = Math.hypot(bad[0] - good[0], bad[1] - good[1]) * 1000;
      const fromPx = z * DU / FX * 1000, fromDepth = dz * Math.hypot(1, (U - CX) / FX) * 1000;
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), ok = ctx.color('--ok'), bd = ctx.color('--bad'), ln = ctx.color('--line');
      const P = p => [bx + p[0] * S, by - p[1] * S];
      g.clearRect(0, 0, w, h);
      for (let m = 1; m <= 5; m++) { L(g, bx - 8, by - m * S, bx + 8, by - m * S, ln); T(g, m + ' m', bx - 12, by - m * S + 4, mut, 'right'); }
      L(g, bx, by, bx, 6, ln, 1, [4, 4]);
      const far = unproject(U, 5.5); L(g, bx, by, ...P(far), acc, 1.5);
      const [gx, gy] = P(good), [ex, ey] = P(bad);
      L(g, gx, gy, ex, ey, bd, 3);
      dot(g, gx, gy, 6, ok); dot(g, ex, ey, 5, bd); dot(g, bx, by, 6, fg);
      T(g, ctx.t('camera', '카메라'), bx + 10, by - 2, fg);
      T(g, ctx.t('the pixel\'s ray', '픽셀의 광선'), Math.min(w - 8, P(unproject(U, 4.4))[0] + 10), P(unproject(U, 4.4))[1], acc);
      const apart = Math.hypot(ex - gx, ey - gy) > 14;   // at small errors the two dots coincide, so one label
      T(g, apart ? ctx.t('real cup', '실제 컵') : ctx.t('overlap at this scale', '이 축척에서는 겹칩니다'), gx + 10, gy + 4, ok);
      if (apart) T(g, ctx.t('grabbed', '집는 곳'), ex + 10, ey + 4, bd);
      ro.textContent = ctx.t(`pixel ${DU} px: ${fromPx.toFixed(1)} mm sideways · depth ${pct}%: ${fromDepth.toFixed(1)} mm along the ray · total ${tot.toFixed(1)} mm`,
        `픽셀 ${DU} px: 옆으로 ${fromPx.toFixed(1)} mm · 깊이 ${pct}%: 광선 따라 ${fromDepth.toFixed(1)} mm · 합계 ${tot.toFixed(1)} mm`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    }
    ctx.slider('distance z (m)', '거리 z (m)', 0.5, 4, 0.1, z, v => { z = v; go(); });
    ctx.slider('depth error (%)', '깊이 오차 (%)', 0, 30, 1, pct, v => { pct = v; go(); });
    ro = ctx.readout(); live(ctx, draw, el); draw();
  };
})();
