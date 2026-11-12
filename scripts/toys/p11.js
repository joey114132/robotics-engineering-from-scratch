// 토이: friction-cone (tan(theta) 가 mu 를 넘으면 마찰 원뿔 밖이라 미끄러진다)
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
  // lesson main.py simulate(): penalty normal force + tangential bristle spring clipped at mu*fn, semi-implicit Euler 0.1 ms
  const G = 9.81, DT = 1e-4, K = 1e4, C = 140, KT = 1e4, CT = 200;
  function sim(th, mu) {
    let s = 0, v = 0, n = 0, nv = 0, anchor = 0;
    for (let i = 0; i < 20000; i++) {
      const pen = Math.max(-n, 0), fn = pen > 0 ? Math.max(K * pen - C * nv, 0) : 0;
      let ft = 0;
      if (pen > 0) { ft = -KT * (s - anchor) - CT * v; const cap = mu * fn; if (Math.abs(ft) > cap) { ft = Math.sign(ft) * cap; anchor = s + ft / KT; } } else anchor = s;
      v += (G * Math.sin(th) + ft) * DT; nv += (-G * Math.cos(th) + fn) * DT; s += v * DT; n += nv * DT;
    }
    return v;
  }

  window.TOYS['friction-cone'] = (el, ctx) => {
    ctx.title('Inside the friction cone, or sliding', '마찰 원뿔 안인가, 미끄러지는가');
    const go = soon(ctx, () => draw());
    const { c, g, w, h } = ctx.canvas(360, 210);
    let mu = 0.5, deg = 28, ro;
    function draw() {
      if (!ro) return;   // sliders call draw before the readout exists
      const th = deg * Math.PI / 180, v = sim(th, mu), slides = Math.abs(v) >= 0.05, tn = Math.tan(th);
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), ok = ctx.color('--ok'), bad = ctx.color('--bad'), ln = ctx.color('--line'), card = ctx.color('--card');
      g.clearRect(0, 0, w, h);
      // left: block on the tilted plane
      const x0 = 14, y0 = 150, len = 150;
      L(g, x0, y0, x0 + len * Math.cos(th), y0 - len * Math.sin(th), fg, 2);
      L(g, x0, y0, x0 + len, y0, ln, 1, [4, 4]);
      g.save(); g.translate(x0 + 90 * Math.cos(th), y0 - 90 * Math.sin(th)); g.rotate(-th);
      g.fillStyle = slides ? bad : ok; g.globalAlpha = 0.85; g.fillRect(-20, -32, 40, 32); g.restore(); g.globalAlpha = 1;
      T(g, deg + '°', x0 + 30, y0 - 4, mut);
      // right: forces in (tangential, normal) space; the needed friction must sit inside the cone
      const ox = 262, oy = 190, R = 130, ha = Math.atan(mu);
      g.beginPath(); g.moveTo(ox, oy); g.lineTo(ox - R * Math.sin(ha), oy - R * Math.cos(ha)); g.lineTo(ox + R * Math.sin(ha), oy - R * Math.cos(ha)); g.closePath();
      g.globalAlpha = 0.16; g.fillStyle = ok; g.fill(); g.globalAlpha = 1;
      L(g, ox, oy, ox - R * Math.sin(ha), oy - R * Math.cos(ha), ok, 1.5); L(g, ox, oy, ox + R * Math.sin(ha), oy - R * Math.cos(ha), ok, 1.5);
      const k = 11, px = ox + k * G * Math.sin(th), py = oy - k * G * Math.cos(th);
      L(g, ox, oy, px, py, slides ? bad : acc, 3); g.beginPath(); g.arc(px, py, 5, 0, 7); g.fillStyle = slides ? bad : acc; g.fill();
      T(g, ctx.t('friction cone, μ = ', '마찰 원뿔, μ = ') + mu.toFixed(2), ox, 14, ok, 'center');
      T(g, ctx.t('needed: ft / fn = tan θ', '필요: ft / fn = tan θ'), ox, oy + 16 > h ? h - 2 : oy + 16, mut, 'center');
      ro.textContent = ctx.t(`tan θ ${tn.toFixed(3)} ${tn > mu ? '>' : '≤'} μ ${mu.toFixed(2)} → ${slides ? 'slides' : 'sticks'}, speed after 2 s ${Math.abs(v).toFixed(2)} m/s`,
        `tan θ ${tn.toFixed(3)} ${tn > mu ? '>' : '≤'} μ ${mu.toFixed(2)} → ${slides ? '미끄러짐' : '붙어 있음'}, 2초 뒤 속도 ${Math.abs(v).toFixed(2)} m/s`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    }
    ctx.slider('friction μ', '마찰 계수 μ', 0.1, 1, 0.05, mu, v => { mu = v; go(); });
    ctx.slider('slope angle (°)', '경사각 (°)', 0, 45, 1, deg, v => { deg = v; go(); });
    ro = ctx.readout(); live(ctx, draw, el); draw();
  };
})();
