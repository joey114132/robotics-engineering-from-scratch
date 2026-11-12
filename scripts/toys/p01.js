// 토이: rotation-order (회전 순서가 행렬 곱과 끝점을 바꾼다)
(() => {
  const F = '-apple-system,"Pretendard","Noto Sans KR",system-ui,sans-serif';
  const T = (g, s, x, y, c, a = 'left', w = '') => { g.font = `${w} 12px ${F}`; g.fillStyle = c; g.textAlign = a; g.fillText(s, x, y); };
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
  const rx = a => { const c = Math.cos(a), s = Math.sin(a); return [[1, 0, 0], [0, c, -s], [0, s, c]]; };
  const rz = a => { const c = Math.cos(a), s = Math.sin(a); return [[c, -s, 0], [s, c, 0], [0, 0, 1]]; };
  const mul = (A, B) => A.map(r => [0, 1, 2].map(j => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j]));
  const f2 = v => (Math.abs(v) < 0.005 ? 0 : v).toFixed(2);

  window.TOYS['rotation-order'] = (el, ctx) => {
    ctx.title('Same two turns, two orders', '같은 두 번의 회전, 다른 순서');
    const go = soon(ctx, () => draw());
    const { c, g, w, h } = ctx.canvas(360, 190);
    let a = 90, b = 90, ro;
    function draw() {
      const A = rx(a * Math.PI / 180), B = rz(b * Math.PI / 180), M = [mul(B, A), mul(A, B)];
      const tip = M.map(m => [m[0][0], m[1][0], m[2][0]]);   // M applied to (1,0,0) is the first column
      const gap = Math.hypot(tip[0][0] - tip[1][0], tip[0][1] - tip[1][1], tip[0][2] - tip[1][2]);
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), bad = ctx.color('--bad'), acc = ctx.color('--acc'), ln = ctx.color('--line');
      g.clearRect(0, 0, w, h);
      const names = [ctx.t('x first, then z: Rz·Rx', 'x 먼저, 그다음 z: Rz·Rx'), ctx.t('z first, then x: Rx·Rz', 'z 먼저, 그다음 x: Rx·Rz')];
      M.forEach((m, k) => {
        const x0 = 12 + k * 180;
        T(g, names[k], x0, 18, fg, 'left', '600');
        m.forEach((r, i) => r.forEach((v, j) => {
          const diff = Math.abs(v - M[1 - k][i][j]) > 0.005;
          T(g, f2(v), x0 + 36 + j * 46, 46 + i * 22, diff ? bad : fg, 'right', diff ? '600' : '');
        }));
        g.strokeStyle = ln; g.lineWidth = 1; g.strokeRect(x0 - 2, 30, 148, 74);
        T(g, ctx.t('tip of (1,0,0)', '(1,0,0)의 끝'), x0, 126, mut);
        T(g, '(' + tip[k].map(f2).join(', ') + ')', x0, 146, acc, 'left', '600');
      });
      g.fillStyle = ln; g.fillRect(12, 160, 336, 8); g.fillStyle = gap > 0.005 ? bad : acc; g.fillRect(12, 160, 336 * gap / 2, 8);
      T(g, ctx.t('gap between the two tips: ', '두 끝 사이 거리: ') + gap.toFixed(2), 12, 184, mut);
      if (ro) {
        ro.textContent = ctx.t(`x first: (${tip[0].map(f2)}) · z first: (${tip[1].map(f2)}) · gap ${gap.toFixed(2)}`,
          `x 먼저: (${tip[0].map(f2)}) · z 먼저: (${tip[1].map(f2)}) · 거리 ${gap.toFixed(2)}`);
        c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
      }
    }
    ctx.slider('turn about x (°)', 'x축 회전 (°)', 0, 180, 5, a, v => { a = v; go(); });
    ctx.slider('turn about z (°)', 'z축 회전 (°)', 0, 180, 5, b, v => { b = v; go(); });
    ro = ctx.readout(); live(ctx, draw, el); draw();
  };
})();
