// 단계 02 토이: ik-seeds (레슨 02/05). 표적을 끌면 서로 다른 시작 자세 8개의 IK 해가 유령 팔로 나온다. 00-core.js 의 ctx 사용
(() => {
  const FONT = '-apple-system,"Pretendard","Noto Sans KR","Apple SD Gothic Neo",system-ui,sans-serif';
  const root = document.documentElement;
  const L = [0.4, 0.3, 0.2];
  function live(ctx, draw) {
    ctx.onRedraw(draw);
    const mq = matchMedia('(prefers-color-scheme: dark)'), mo = new MutationObserver(draw);
    mq.addEventListener('change', draw); mo.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    ctx.onDispose(() => { mq.removeEventListener('change', draw); mo.disconnect(); });
  }
  // 레슨의 solve_ik (lam 0.05, 300 회, tol 1e-6, 한 걸음 최대 0.3 rad). 할당 없이 스칼라로 푼다
  function solve(t, q0, lo, hi) {
    const q = [0, 1, 2].map(i => Math.min(hi[i], Math.max(lo[i], q0[i])));
    let ok = false;
    for (let n = 0; n <= 300; n++) {
      const a1 = q[0], a2 = a1 + q[1], a3 = a2 + q[2], c1 = Math.cos(a1), c2 = Math.cos(a2), c3 = Math.cos(a3), s1 = Math.sin(a1), s2 = Math.sin(a2), s3 = Math.sin(a3);
      const e0 = t[0] - (L[0] * c1 + L[1] * c2 + L[2] * c3), e1 = t[1] - (L[0] * s1 + L[1] * s2 + L[2] * s3);
      if (Math.hypot(e0, e1) < 1e-6) { ok = true; break; }
      if (n === 300) break;
      const x3 = -L[2] * s3, x2 = x3 - L[1] * s2, x1 = x2 - L[0] * s1, y3 = L[2] * c3, y2 = y3 + L[1] * c2, y1 = y2 + L[0] * c1;   // J 의 세 열 (x1,y1) (x2,y2) (x3,y3)
      const a = x1 * x1 + x2 * x2 + x3 * x3 + 0.0025, b = x1 * y1 + x2 * y2 + x3 * y3, d = y1 * y1 + y2 * y2 + y3 * y3 + 0.0025, det = a * d - b * b;
      const z0 = (d * e0 - b * e1) / det, z1 = (-b * e0 + a * e1) / det;   // (J J' + lam² I)^-1 e
      const d0 = x1 * z0 + y1 * z1, d1 = x2 * z0 + y2 * z1, d2 = x3 * z0 + y3 * z1, s = Math.min(1, 0.3 / (Math.max(Math.abs(d0), Math.abs(d1), Math.abs(d2)) || 1));
      q[0] = Math.min(hi[0], Math.max(lo[0], q[0] + d0 * s)); q[1] = Math.min(hi[1], Math.max(lo[1], q[1] + d1 * s)); q[2] = Math.min(hi[2], Math.max(lo[2], q[2] + d2 * s));
    }
    return { q, ok };
  }
  window.TOYS['ik-seeds'] = (el, ctx) => {
    ctx.title('One target, eight starting poses', '표적 하나, 시작 자세 여덟 개');
    const { c, g, w, h } = ctx.canvas(360, 240);
    const S = 125, bx = 110, by = 120, LIM = Math.PI;
    let tgt = [0.5, 0.3], lim = 2.5, ro;
    let s = 7; const rnd = () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    const at = (u, l) => u.map((v, i) => (i ? -l : -LIM) + v * 2 * (i ? l : LIM)), seeds = [];   // 기본 한계에서 수렴하는 seed 8개를 고른다 (레슨 그림과 같은 방식)
    while (seeds.length < 8) { const u = [rnd(), rnd(), rnd()]; if (solve([0.5, 0.3], at(u, 2.5), at(u, 2.5).map(() => 0).map((_, i) => (i ? -2.5 : -LIM)), [LIM, 2.5, 2.5]).ok) seeds.push(u); }
    const px = p => [bx + S * p[0], by - S * p[1]];
    const pose = (q, col, wd, dash) => {
      let a = 0, p = [0, 0]; g.beginPath(); g.setLineDash(dash || []); g.strokeStyle = col; g.lineWidth = wd; g.lineCap = 'round'; g.lineJoin = 'round'; g.moveTo(...px(p));
      q.forEach((v, i) => { a += v; p = [p[0] + L[i] * Math.cos(a), p[1] + L[i] * Math.sin(a)]; g.lineTo(...px(p)); }); g.stroke(); g.setLineDash([]);
    };
    function draw() {
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), bad = ctx.color('--bad'), ok = ctx.color('--ok');
      const lo = [-LIM, -lim, -lim], hi = [LIM, lim, lim];
      g.clearRect(0, 0, w, h);
      g.beginPath(); g.arc(bx, by, S * 0.9, 0, 6.3); g.setLineDash([3, 4]); g.strokeStyle = ctx.color('--line'); g.lineWidth = 1; g.stroke(); g.setLineDash([]);
      let up = 0, down = 0, fail = 0;
      seeds.forEach(sd => {
        const r = solve(tgt, sd.map((u, i) => lo[i] + u * (hi[i] - lo[i])), lo, hi);
        if (r.ok) { r.q[1] > 0 ? up++ : down++; g.globalAlpha = 0.5; pose(r.q, r.q[1] > 0 ? acc : ok, 4); g.globalAlpha = 1; }
        else { fail++; g.globalAlpha = 0.6; pose(r.q, bad, 2, [4, 4]); g.globalAlpha = 1; }
      });
      const t = px(tgt); g.strokeStyle = fg; g.lineWidth = 2; g.beginPath(); g.arc(t[0], t[1], 8, 0, 6.3); g.moveTo(t[0] - 12, t[1]); g.lineTo(t[0] + 12, t[1]); g.moveTo(t[0], t[1] - 12); g.lineTo(t[0], t[1] + 12); g.stroke();
      g.beginPath(); g.arc(bx, by, 5, 0, 6.3); g.fillStyle = fg; g.fill();
      g.font = '12.5px ' + FONT; g.fillStyle = mut; g.textAlign = 'right';
      g.fillText(ctx.t('drag the target (or arrow keys)', '표적을 끌기 (또는 화살표 키)'), w - 8, 18);
      g.fillStyle = acc; g.fillText(ctx.t('elbow q2 > 0', '팔꿈치 q2 > 0'), w - 8, 36); g.fillStyle = ok; g.fillText(ctx.t('elbow q2 < 0', '팔꿈치 q2 < 0'), w - 8, 54); g.fillStyle = bad; g.fillText(ctx.t('failed: best effort', '실패: 최선의 자세'), w - 8, 72);
      ro.textContent = ctx.t(`${up + down} of 8 seeds converge (elbow one way ${up}, other way ${down}) · ${fail} failed · target (${tgt[0].toFixed(2)}, ${tgt[1].toFixed(2)}) m · the toy's own random starts`,
        `seed 8개 중 ${up + down}개 수렴 (팔꿈치 한쪽 ${up}, 반대쪽 ${down}) · 실패 ${fail} · 표적 (${tgt[0].toFixed(2)}, ${tgt[1].toFixed(2)}) m · 이 토이의 무작위 시작 자세`);
    }
    let fr; const soon = () => { cancelAnimationFrame(fr); fr = requestAnimationFrame(draw); }; ctx.onDispose(() => cancelAnimationFrame(fr));
    const set = (x, y) => { tgt = [Math.max(-0.9, Math.min(1.4, x)), Math.max(-0.9, Math.min(0.9, y))]; soon(); };
    const move = e => { const r = c.getBoundingClientRect(); set(((e.clientX - r.left) / r.width * w - bx) / S, (by - (e.clientY - r.top) / r.height * h) / S); };
    c.style.touchAction = 'none'; c.tabIndex = 0; c.setAttribute('role', 'application');
    const lab = () => c.setAttribute('aria-label', ctx.t('Target position; arrow keys move it', '표적 위치. 화살표 키로 움직입니다'));
    lab(); ctx.onRedraw(lab);
    c.addEventListener('pointerdown', e => { c.setPointerCapture(e.pointerId); move(e); c.onpointermove = move; });
    c.addEventListener('pointerup', () => { c.onpointermove = null; });
    c.addEventListener('keydown', e => {
      const d = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key];
      if (d) { e.preventDefault(); set(tgt[0] + d[0] * 0.02, tgt[1] + d[1] * 0.02); }
    });
    ctx.slider('elbow/wrist joint limit ± (rad)', '팔꿈치·손목 관절 한계 ± (rad)', 0.5, 2.5, 0.25, lim, v => { lim = v; ro && soon(); });
    ro = ctx.readout(); live(ctx, draw); soon();
  };
})();
