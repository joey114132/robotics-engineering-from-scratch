// 토이 4종: pd-step, ik-2link, grav-sag, sampling-limit (00-core.js 의 ctx 사용, 라이브러리 없음)
(() => {
  const FONT = '-apple-system,"Pretendard","Noto Sans KR","Apple SD Gothic Neo",system-ui,sans-serif';
  const root = document.documentElement;
  const isDark = () => root.dataset.theme === 'dark' || (root.dataset.theme !== 'light' && matchMedia('(prefers-color-scheme: dark)').matches);
  const amber = () => (isDark() ? '#f0b240' : '#c77c00');
  const deg = r => r * 180 / Math.PI;
  const sgn = (x, d) => (x < 0 ? '−' : '') + Math.abs(x).toFixed(d);

  // 테마(OS 설정, 토글 버튼)와 언어 변경 때 다시 그린다
  function live(ctx, draw) {
    ctx.onRedraw(draw);
    const mq = matchMedia('(prefers-color-scheme: dark)'), mo = new MutationObserver(draw);
    mq.addEventListener('change', draw);
    mo.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    ctx.onDispose(() => { mq.removeEventListener('change', draw); mo.disconnect(); });
  }
  const text = (g, s, x, y, col, align = 'left', size = 11, weight = '') => {
    g.font = `${weight} ${size}px ${FONT}`; g.fillStyle = col; g.textAlign = align; g.fillText(s, x, y);
  };
  const line = (g, x1, y1, x2, y2, col, w = 1, dash = null) => {
    g.beginPath(); g.setLineDash(dash || []); g.strokeStyle = col; g.lineWidth = w; g.moveTo(x1, y1); g.lineTo(x2, y2); g.stroke(); g.setLineDash([]);
  };
  const dot = (g, x, y, r, fill, stroke) => {
    g.beginPath(); g.arc(x, y, r, 0, 2 * Math.PI); if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = 2; g.stroke(); }
  };

  // ---------------------------------------------------------------- 1. pd-step
  window.TOYS['pd-step'] = (el, ctx) => {
    ctx.title('PD step response', 'PD 계단 응답');
    const { c, g, w, h } = ctx.canvas(360, 230);
    const DT = 0.002, T = 3, N = Math.round(T / DT), B = 0.2; // 단위 관성 J=1, 약한 마찰 B
    let kp = 30, kd = 4, ro;

    function draw() {
      // J*q'' = kp*(1-q) - (kd+B)*q'
      const y = new Float32Array(N + 1);
      let q = 0, v = 0, peak = 0, ipk = 0, lo = 0, last = -1;
      for (let i = 1; i <= N; i++) {
        v += (kp * (1 - q) - (kd + B) * v) * DT; q += v * DT; y[i] = q;
        if (q > peak) { peak = q; ipk = i; }
        if (q < lo) lo = q;
        if (Math.abs(q - 1) > 0.02) last = i;
      }
      const over = Math.max(0, peak - 1) * 100, settled = last < N, ts = (last + 1) * DT;

      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), ok = ctx.color('--ok'), ln = ctx.color('--line');
      const L = 34, R = 12, Tp = 14, Bt = 28, pw = w - L - R, ph = h - Tp - Bt;
      const ymax = Math.max(1.5, peak * 1.08), ymin = Math.min(0, lo - 0.05);
      const X = t => L + t / T * pw, Y = v => Tp + (ymax - v) / (ymax - ymin) * ph;
      g.clearRect(0, 0, w, h);
      // 2% 띠
      g.globalAlpha = 0.14; g.fillStyle = ok; g.fillRect(L, Y(1.02), pw, Y(0.98) - Y(1.02)); g.globalAlpha = 1;
      for (let t = 0; t <= T; t++) { line(g, X(t), Tp, X(t), Tp + ph, ln); text(g, t + ' s', X(t), h - 10, mut, 'center'); }
      line(g, L, Y(0), L + pw, Y(0), ln);
      line(g, L, Y(1), L + pw, Y(1), mut, 1.2, [5, 4]);
      text(g, '1', L - 6, Y(1) + 4, mut, 'right'); text(g, '0', L - 6, Y(0) + 4, mut, 'right');
      if (settled && ts > 0 && ts < T) {
        line(g, X(ts), Tp, X(ts), Tp + ph, ok, 1.2, [3, 3]);
        text(g, 't_s', X(ts) + 3, Tp + 10, ok);
      }
      g.beginPath(); g.strokeStyle = acc; g.lineWidth = 2.2; g.lineJoin = 'round';
      for (let i = 0; i <= N; i += 2) { const px = X(i * DT), py = Y(y[i]); i ? g.lineTo(px, py) : g.moveTo(px, py); }
      g.stroke();
      if (over > 0.5) {
        const px = X(ipk * DT), py = Y(peak);
        dot(g, px, py, 3.5, ctx.color('--bad'));
        text(g, '+' + over.toFixed(0) + '%', px + 6, py - 4, ctx.color('--bad'), 'left', 11, '600');
      }
      if (ro) ro.textContent = ctx.t(
        `overshoot ${over.toFixed(1)}% · settle (2%) ${settled ? ts.toFixed(2) + ' s' : 'not within ' + T + ' s'}`,
        `오버슈트 ${over.toFixed(1)}% · 정착(2%) ${settled ? ts.toFixed(2) + ' s' : T + ' s 안에 못 함'}`);
    }
    ctx.slider('kp (stiffness)', 'kp (강성)', 1, 100, 1, kp, v => { kp = v; draw(); });
    ctx.slider('kd (damping)', 'kd (댐핑)', 0, 15, 0.5, kd, v => { kd = v; draw(); });
    ro = ctx.readout(); live(ctx, draw); draw();
  };

  // ---------------------------------------------------------------- 2. ik-2link
  window.TOYS['ik-2link'] = (el, ctx) => {
    ctx.title('2-link inverse kinematics: drag the dot', '2링크 역기구학: 점을 끌어 보세요');
    const { c, g, w, h } = ctx.canvas(360, 300);
    const L1 = 1, L2 = 0.8, S = 76, bx = w / 2, by = h / 2; // 도달 반경 1.8 -> 137 px
    let tx = 1.0, ty = 0.9, elbowUp = false, ro;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.style.cssText = 'margin:8px 0 2px;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:6px 14px;font-size:13px;cursor:pointer';
    btn.onclick = () => { elbowUp = !elbowUp; draw(); };

    function solve() {
      const d = Math.hypot(tx, ty), ang = Math.atan2(ty, tx), lo = Math.abs(L1 - L2), hi = L1 + L2, s = elbowUp ? -1 : 1;
      if (d > hi) return { q1: ang, q2: 0, out: true };
      if (d < lo) return { q1: ang, q2: s * Math.PI, out: true };
      const c2 = Math.max(-1, Math.min(1, (d * d - L1 * L1 - L2 * L2) / (2 * L1 * L2)));
      const q2 = s * Math.acos(c2);
      return { q1: ang - Math.atan2(L2 * Math.sin(q2), L1 + L2 * Math.cos(q2)), q2, out: false };
    }

    function draw() {
      const { q1, q2, out } = solve();
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), ok = ctx.color('--ok'), bad = ctx.color('--bad'), ln = ctx.color('--line');
      const P = (x, y) => [bx + x * S, by - y * S];
      const ex = L1 * Math.cos(q1), ey = L1 * Math.sin(q1), px = ex + L2 * Math.cos(q1 + q2), py = ey + L2 * Math.sin(q1 + q2);
      g.clearRect(0, 0, w, h);
      // 도달 영역(바깥/안쪽 원)
      g.beginPath(); g.setLineDash([4, 4]); g.strokeStyle = ln; g.lineWidth = 1.2; g.arc(bx, by, (L1 + L2) * S, 0, 7); g.stroke();
      g.beginPath(); g.arc(bx, by, Math.abs(L1 - L2) * S, 0, 7); g.stroke(); g.setLineDash([]);
      const [ax, ay] = P(ex, ey), [tipx, tipy] = P(px, py), [dx, dy] = P(tx, ty);
      g.lineCap = 'round';
      line(g, bx, by, ax, ay, acc, 8); line(g, ax, ay, tipx, tipy, acc, 5.5);
      g.globalAlpha = 0.35; line(g, bx, by, ax, ay, fg, 1); line(g, ax, ay, tipx, tipy, fg, 1); g.globalAlpha = 1;
      if (out) line(g, tipx, tipy, dx, dy, bad, 1.4, [3, 3]);
      dot(g, bx, by, 6, fg); dot(g, ax, ay, 5, ctx.color('--card'), fg); dot(g, tipx, tipy, 4, fg);
      dot(g, dx, dy, 9, out ? bad : ok, ctx.color('--card'));
      if (out) text(g, ctx.t('out of reach', '닿지 않음'), Math.max(45, Math.min(w - 45, dx)), dy - 15 < 14 ? dy + 26 : dy - 15, bad, 'center', 12, '600');
      if (ro) ro.textContent = `θ₁ = ${sgn(deg(q1), 1)}°   θ₂ = ${sgn(deg(q2), 1)}°   ` +
        ctx.t(`target (${tx.toFixed(2)}, ${ty.toFixed(2)})`, `목표 (${tx.toFixed(2)}, ${ty.toFixed(2)})`);
      btn.textContent = elbowUp ? ctx.t('elbow up (θ₂ < 0), tap to flip', '팔꿈치 위 (θ₂ < 0), 눌러서 바꾸기')
                                : ctx.t('elbow down (θ₂ > 0), tap to flip', '팔꿈치 아래 (θ₂ > 0), 눌러서 바꾸기');
    }
    const set = e => {
      const r = c.getBoundingClientRect(), k = w / r.width;
      tx = ((e.clientX - r.left) * k - bx) / S; ty = (by - (e.clientY - r.top) * k) / S;
      const lim = 2.3, m = Math.max(Math.abs(tx), Math.abs(ty) * 1.2) > lim; // 화면 밖으로 안 나가게
      if (m) { const f = lim / Math.max(Math.abs(tx), Math.abs(ty) * 1.2); tx *= f; ty *= f; }
      draw();
    };
    let down = false;
    c.style.touchAction = 'none'; c.style.cursor = 'crosshair';
    c.addEventListener('pointerdown', e => { down = true; c.setPointerCapture(e.pointerId); set(e); e.preventDefault(); });
    c.addEventListener('pointermove', e => { if (down) set(e); });
    const up = () => { down = false; }; c.addEventListener('pointerup', up); c.addEventListener('pointercancel', up);
    c.tabIndex = 0; c.setAttribute('role', 'application');
    c.setAttribute('aria-label', ctx.t('Target position. Arrow keys move the target.', '목표 위치입니다. 화살표 키로 목표를 옮깁니다.'));
    c.addEventListener('keydown', e => {
      const d = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key]; if (!d) return;
      tx += d[0] * 0.05; ty += d[1] * 0.05;
      const lim = 2.3, f = lim / Math.max(Math.abs(tx), Math.abs(ty) * 1.2); if (f < 1) { tx *= f; ty *= f; }
      draw(); e.preventDefault();
    });
    el.appendChild(btn); ro = ctx.readout(); live(ctx, draw); draw();
  };

  // ---------------------------------------------------------------- 3. grav-sag
  window.TOYS['grav-sag'] = (el, ctx) => {
    ctx.title('Gravity sag under PD + feedforward', 'PD + feedforward 아래의 중력 처짐');
    const { c, g, w, h } = ctx.canvas(360, 230);
    // 레슨 03/02 와 같은 모델: 각도는 수평 기준, 중력은 아래로
    const M1 = 2, M2 = 1, L1 = 0.4, LC1 = 0.2, LC2 = 0.2, G = 9.81, L2 = 0.4;
    const QD = [0.15, 0.1];
    let kp = 20, err = -25, ro;
    const tauG = q => {
      const t2 = M2 * LC2 * G * Math.cos(q[0] + q[1]);
      return [(M1 * LC1 + M2 * L1) * G * Math.cos(q[0]) + t2, t2];
    };
    // kp*(qd - q) + ff = tau_g(q) 를 감쇠 고정점 반복으로 푼다
    function settle() {
      const ffq = tauG(QD), ff = ffq.map(t => t * (1 + err / 100));
      let q = QD.slice();
      for (let i = 0; i < 500; i++) { const tg = tauG(q); q = q.map((qi, j) => 0.5 * qi + 0.5 * (QD[j] + (ff[j] - tg[j]) / kp)); }
      const tg = tauG(q), res = Math.max(...q.map((qi, j) => Math.abs(kp * (QD[j] - qi) + ff[j] - tg[j])));
      return { q, ok: res < 1e-6 && isFinite(res) };
    }
    const S = 300, bx = 34, by = 125;
    const tip = q => [bx + S * (L1 * Math.cos(q[0]) + L2 * Math.cos(q[0] + q[1])), by - S * (L1 * Math.sin(q[0]) + L2 * Math.sin(q[0] + q[1]))];

    function drawArm(q, col, wd, dash) {
      const e = [bx + S * L1 * Math.cos(q[0]), by - S * L1 * Math.sin(q[0])], t = tip(q);
      g.lineCap = 'round';
      line(g, bx, by, e[0], e[1], col, wd, dash); line(g, e[0], e[1], t[0], t[1], col, wd * 0.75, dash);
      return e;
    }
    function draw() {
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), acc = ctx.color('--acc'), bad = ctx.color('--bad'), ok = ctx.color('--ok'), ln = ctx.color('--line');
      const { q, ok: conv } = settle();
      g.clearRect(0, 0, w, h);
      // 벽과 수평 기준선, 중력 화살표
      line(g, bx - 10, 30, bx - 10, h - 30, fg, 3);
      for (let y = 40; y < h - 30; y += 12) line(g, bx - 10, y, bx - 20, y + 8, mut, 1);
      line(g, bx, by, bx + S * 0.8 + 20, by, ln, 1, [3, 4]);
      line(g, w - 24, 60, w - 24, 100, mut, 2); g.beginPath(); g.fillStyle = mut; g.moveTo(w - 24, 108); g.lineTo(w - 29, 98); g.lineTo(w - 19, 98); g.fill();
      text(g, 'g', w - 24, 122, mut, 'center', 12, '600');
      g.globalAlpha = 0.45; const dq = drawArm(QD, mut, 7); g.globalAlpha = 1; // 명령 자세(유령)
      const pq = conv ? q : QD;
      drawArm(pq, acc, 7);
      const td = tip(QD), ta = tip(pq);
      dot(g, bx, by, 6, fg); dot(g, dq[0], dq[1], 3, mut); dot(g, ta[0], ta[1], 4, fg);
      const dyCm = (td[1] - ta[1]) / S * 100; // 위가 +
      if (conv && Math.abs(dyCm) > 0.4) {
        line(g, td[0], td[1], ta[0], ta[1], dyCm < 0 ? bad : ok, 2);
        text(g, `${dyCm < 0 ? '−' : '+'}${Math.abs(dyCm).toFixed(1)} cm`, ta[0] - 6, ta[1] + (dyCm < 0 ? 16 : -10), dyCm < 0 ? bad : ok, 'right', 12, '600');
      }
      text(g, ctx.t('dashed = commanded pose', '점선 = 명령 자세'), 14, h - 8, mut);
      text(g, ctx.t('solid = where it settles', '실선 = 실제로 멈추는 자세'), w - 10, h - 8, acc, 'right');
      if (!ro) return;
      if (!conv) { ro.textContent = ctx.t('kp too soft: no stable equilibrium', 'kp 가 너무 작아서 안정한 평형이 없음'); return; }
      const s1 = deg(q[0] - QD[0]), s2 = deg(q[1] - QD[1]);
      const word = dyCm < -0.4 ? ctx.t('droops', '처짐') : dyCm > 0.4 ? ctx.t('floats up', '뜸') : ctx.t('holds', '유지');
      ro.textContent = ctx.t(`sag: joint 1 ${sgn(s1, 1)}°, joint 2 ${sgn(s2, 1)}° · tip ${sgn(dyCm, 1)} cm · ${word}`,
        `처짐: 관절 1 ${sgn(s1, 1)}°, 관절 2 ${sgn(s2, 1)}° · 끝점 ${sgn(dyCm, 1)} cm · ${word}`);
    }
    ctx.slider('kp (Nm/rad)', 'kp (Nm/rad)', 12, 150, 1, kp, v => { kp = v; draw(); });
    ctx.slider('gravity model error % (+ = model too heavy)', '중력 모델 오차 % (+ = 모델이 더 무거움)', -30, 30, 1, err, v => { err = v; draw(); });
    ro = ctx.readout(); live(ctx, draw); draw();
  };

  // ---------------------------------------------------------------- 4. sampling-limit
  window.TOYS['sampling-limit'] = (el, ctx) => {
    ctx.title('The sampling limit: r = dt·kd/J', '샘플링 한계: r = dt·kd/J');
    const { c, g, w, h } = ctx.canvas(360, 250);
    const N = 40, RMAX = 2.5, YM = 1.5;
    let r = 0.6, ro;
    function draw() {
      const fg = ctx.color('--fg'), mut = ctx.color('--mut'), ln = ctx.color('--line'), ok = ctx.color('--ok'), bad = ctx.color('--bad'), am = amber();
      const col = r <= 1 + 1e-9 ? ok : r < 2 - 1e-9 ? am : bad;
      const L = 34, R = 12, Tp = 12, ph = 170, pw = w - L - R;
      const X = k => L + k / N * pw, Y = v => Tp + (YM - v) / (2 * YM) * ph;
      g.clearRect(0, 0, w, h);
      for (const v of [-1, 0, 1]) { line(g, L, Y(v), L + pw, Y(v), v ? ln : mut, v ? 1 : 1.2); text(g, String(v), L - 6, Y(v) + 4, mut, 'right'); }
      text(g, ctx.t('step', '스텝'), L + pw, Tp + ph + 14, mut, 'right');
      text(g, 'v', L - 20, Tp + 4, mut, 'right', 11, '600');
      g.save(); g.beginPath(); g.rect(L, Tp, pw, ph); g.clip();
      const f = 1 - r; let v = 1; g.beginPath(); g.strokeStyle = col; g.lineWidth = 1.5; g.globalAlpha = 0.55;
      const vs = []; let off = -1;
      for (let k = 0; k <= N && off < 0; k++) { if (Math.abs(v) > YM) off = k; else { vs.push(v); k ? g.lineTo(X(k), Y(v)) : g.moveTo(X(k), Y(v)); } v *= f; }
      g.stroke(); g.globalAlpha = 1;
      vs.forEach((u, k) => { line(g, X(k), Y(0), X(k), Y(u), col, 1.2); dot(g, X(k), Y(u), 2.8, col); });
      g.restore();
      if (off >= 0) text(g, ctx.t('off scale ▲', '범위 밖 ▲'), Math.min(X(off) + 4, L + pw), Tp + 12, bad, X(off) + 4 > L + pw - 60 ? 'right' : 'left', 11, '600');
      // r 구간 막대: 초록 [0,1], 주황 [1,2], 빨강 [2,2.5]
      const by = Tp + ph + 30, bh = 10, Rx = x => L + x / RMAX * pw;
      g.fillStyle = ok; g.fillRect(Rx(0), by, Rx(1) - Rx(0), bh); g.fillStyle = am; g.fillRect(Rx(1), by, Rx(2) - Rx(1), bh); g.fillStyle = bad; g.fillRect(Rx(2), by, Rx(RMAX) - Rx(2), bh);
      text(g, '0', Rx(0), by + bh + 12, mut, 'center'); text(g, '1', Rx(1), by + bh + 12, mut, 'center'); text(g, '2', Rx(2), by + bh + 12, mut, 'center'); text(g, 'r', Rx(RMAX) + 2, by + bh + 12, mut, 'right');
      g.beginPath(); g.fillStyle = fg; g.moveTo(Rx(r), by - 1); g.lineTo(Rx(r) - 5, by - 9); g.lineTo(Rx(r) + 5, by - 9); g.fill();
      if (!ro) return;
      const mag = Math.pow(Math.abs(f), N);
      const msg = r <= 1 + 1e-9
        ? ctx.t(Math.abs(r - 1) < 1e-9 ? 'smooth: deadbeat, velocity hits 0 in one step' : 'smooth: velocity shrinks every step', Math.abs(r - 1) < 1e-9 ? '부드러움: 한 스텝 만에 속도 0 (deadbeat)' : '부드러움: 속도가 매 스텝 줄어듦')
        : r < 2 - 1e-9 ? ctx.t('chatter: sign flips every step but it still shrinks', '떨림(chatter): 매 스텝 부호가 뒤집히지만 줄어들긴 함')
        : ctx.t(`diverges: never decays (|v| after ${N} steps = ${mag > 1e3 ? mag.toExponential(1) : mag.toFixed(2)})`, `발산: 줄지 않음 (${N} 스텝 뒤 |v| = ${mag > 1e3 ? mag.toExponential(1) : mag.toFixed(2)})`);
      ro.textContent = `r = ${r.toFixed(2)}, 1−r = ${sgn(f, 2)} · ${msg}`;
      ro.style.color = col;
    }
    ctx.slider('r = dt·kd/J', 'r = dt·kd/J', 0.1, RMAX, 0.05, r, v => { r = v; draw(); });
    ro = ctx.readout(); ro.style.fontWeight = '600'; live(ctx, draw); draw();
  };
})();
