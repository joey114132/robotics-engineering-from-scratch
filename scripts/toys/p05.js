// 05장 토이 2종: bt-ticks (behaviour tree 가 tick 마다 켜지는 모습, 실패 버튼), tf-at-a-time (회전하는 로봇의 스캔을 최신 pose 대 시각 pose 로 놓기)
(() => {
  const root = document.documentElement;
  const watch = (ctx, draw) => {
    ctx.onRedraw(draw);
    const mo = new MutationObserver(draw); mo.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    ctx.onDispose(() => mo.disconnect());
  };

  // ---------------------------------------------------------------- bt-ticks (main.py 의 Sequence / Retry / scripted / run)
  const S = 'success', F = 'failure', R = 'running';
  const leaf = (name, list) => { let n = 0; return { name, tick: log => { const s = list[Math.min(n++, list.length - 1)]; log.push([name, s]); return s; } }; };
  function sequence(name, kids) {
    let i = 0;
    return { name, tick: log => {
      for (let k = i; k < kids.length; k++) {
        const s = kids[k].tick(log);
        if (s === R || s === F) { i = s === R ? k : 0; log.push([name, s]); return s; }
      }
      i = 0; log.push([name, S]); return S;
    } };
  }
  function retry(name, tries, kid) {
    let used = 0;
    return { name, tick: log => {
      let s = kid.tick(log);
      if (s === F) { used++; s = used < tries ? R : F; }
      if (s !== R) used = 0;
      log.push([name, s]); return s;
    } };
  }
  function runTask(graspFails) {
    const grasp = leaf('grasp', graspFails ? [F] : [F, F, S]);
    const tree = sequence('fetch', [leaf('go object', [R, R, S]), retry('retry', 3, grasp), leaf('go bin', [R, S]), leaf('release', [S])]);
    const ticks = [];
    while (ticks.length < 50 && (!ticks.length || ticks[ticks.length - 1].s === R)) { const log = []; ticks.push({ s: tree.tick(log), log }); }
    return ticks;
  }
  const POS = { fetch: [160, 30], 'go object': [40, 105], retry: [120, 105], 'go bin': [200, 105], release: [280, 105], grasp: [120, 180] };
  const EDGES = [['fetch', 'go object'], ['fetch', 'retry'], ['fetch', 'go bin'], ['fetch', 'release'], ['retry', 'grasp']];

  window.TOYS['bt-ticks'] = (el, ctx) => {
    ctx.title('Behaviour tree: one tick at a time', 'Behaviour tree: tick 하나씩 따라가기');
    const { c, g, w: W, h: H } = ctx.canvas(320, 215);
    let tick = 6, fail = false, run = runTask(false), ro, btn;
    const draw = () => {
      const i = Math.min(tick, run.length) - 1, status = Object.fromEntries(run[i].log.map(([n, s]) => [n, s]));
      g.clearRect(0, 0, W, H);
      g.strokeStyle = ctx.color('--line'); g.lineWidth = 1.5;
      EDGES.forEach(([a, b]) => { g.beginPath(); g.moveTo(POS[a][0], POS[a][1] + 14); g.lineTo(POS[b][0], POS[b][1] - 14); g.stroke(); });
      g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = '12px system-ui,sans-serif';
      Object.entries(POS).forEach(([n, [x, y]]) => {
        const s = status[n], col = ctx.color(s === S ? '--ok' : s === F ? '--bad' : s === R ? '--acc' : '--line');
        g.globalAlpha = s ? 0.9 : 0.5; g.fillStyle = col; g.beginPath(); g.roundRect(x - 36, y - 14, 72, 28, 8); g.fill(); g.globalAlpha = 1;
        g.fillStyle = ctx.color('--fg'); g.fillText(n, x, y);
        if (s) { g.fillStyle = ctx.color('--mut'); g.fillText(s, x, y + 23); }
      });
      const last = run[run.length - 1].s;
      ro.textContent = ctx.t(`tick ${i + 1} of ${run.length} · root returns ${run[i].s}` + (i + 1 === run.length ? ` · task ${last === S ? 'done' : 'failed'}` : ''),
        `tick ${i + 1} / ${run.length} · root가 돌려준 값 ${run[i].s}` + (i + 1 === run.length ? ` · 작업 ${last === S ? '성공' : '실패'}` : ''));
      btn.textContent = fail ? ctx.t('Let grasp succeed again', '잡기 다시 성공하게 하기') : ctx.t('Make grasp fail every time', '잡기가 매번 실패하게 하기');
      btn.setAttribute('aria-pressed', fail);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    };
    ctx.slider('tick', 'tick', 1, 8, 1, tick, v => { tick = v; if (ro) draw(); });
    btn = document.createElement('button'); btn.type = 'button';
    btn.onclick = () => { fail = !fail; run = runTask(fail); draw(); }; el.appendChild(btn);
    ro = ctx.readout(); draw(); watch(ctx, draw);
  };

  // ---------------------------------------------------------------- tf-at-a-time (main.py 의 PoseBuffer.lookup 과 to_world)
  // 로봇은 t=0 과 t=1 에 pose 를 보고한다: 위치 (2t, 0), yaw = 회전율 * t. 2D 라서 quaternion slerp 는 yaw 의 선형 보간과 같다.
  window.TOYS['tf-at-a-time'] = (el, ctx) => {
    ctx.title('Placing a scan with the right timestamp', '스캔에 맞는 시각의 pose로 놓기');
    const { c, g, w: W, h: H } = ctx.canvas(320, 230);
    let rate = 1, ro;
    const N = 21, pose = (t, w) => ({ x: 2 * t, th: w * t });  // 두 sample 사이를 보간한 pose (a = t)
    const draw = () => {
      const wall = Array.from({ length: N }, (_, i) => [4, -1 + 2 * i / (N - 1)]);
      const sensor = wall.map(([px, py], i) => { const p = pose(i / (N - 1), rate), dx = px - p.x, dy = py, c = Math.cos(p.th), s = Math.sin(p.th); return [c * dx + s * dy, -s * dx + c * dy]; });  // 그 시각에 센서가 본 점
      const place = at => sensor.map(([x, y], i) => { const p = pose(at(i), rate), c = Math.cos(p.th), s = Math.sin(p.th); return [c * x - s * y + p.x, s * x + c * y]; });
      const stamped = place(i => i / (N - 1)), latest = place(() => 1);
      const bounds = [...wall, ...stamped, ...latest, [pose(0, rate).x, 0], [pose(1, rate).x, 0]];
      const x0 = Math.min(...bounds.map(p => p[0])), x1 = Math.max(...bounds.map(p => p[0])), y0 = Math.min(...bounds.map(p => p[1])), y1 = Math.max(...bounds.map(p => p[1]));
      const pad = 16, bottom = H - 44, sc = Math.min((W - 2 * pad) / (x1 - x0 || 1), (bottom - 2 * pad) / (y1 - y0 || 1));
      const sx = x => W / 2 + (x - (x0 + x1) / 2) * sc, sy = y => bottom / 2 - (y - (y0 + y1) / 2) * sc;
      const err = P => Math.sqrt(P.reduce((s, p, i) => s + (p[0] - wall[i][0]) ** 2 + (p[1] - wall[i][1]) ** 2, 0) / N);
      g.clearRect(0, 0, W, H);
      g.strokeStyle = ctx.color('--mut'); g.lineWidth = 1.5; g.setLineDash([4, 4]); g.beginPath(); g.moveTo(sx(4), sy(-1)); g.lineTo(sx(4), sy(1)); g.stroke(); g.setLineDash([]);
      [0, 1].forEach(t => { const p = pose(t, rate), x = sx(p.x), y = sy(0); g.save(); g.translate(x, y); g.rotate(-p.th); g.fillStyle = ctx.color('--fg'); g.globalAlpha = t ? 1 : 0.4; g.beginPath(); g.moveTo(12, 0); g.lineTo(-8, 7); g.lineTo(-8, -7); g.fill(); g.restore(); });
      const plot = (P, col) => { g.fillStyle = ctx.color(col); P.forEach(([x, y]) => { g.beginPath(); g.arc(sx(x), sy(y), 3, 0, 7); g.fill(); }); };
      plot(latest, '--bad'); plot(stamped, '--ok');
      g.font = '12px system-ui,sans-serif'; g.textAlign = 'left'; g.fillStyle = ctx.color('--bad'); g.fillText(ctx.t('newest pose for every point', '모든 점에 최신 pose'), 8, H - 28);
      g.fillStyle = ctx.color('--ok'); g.fillText(ctx.t('pose at each point’s own stamp', '점마다 자기 시각의 pose'), 8, H - 10);
      ro.textContent = ctx.t(`pose at t=0.5: x=${pose(0.5, rate).x.toFixed(2)} m · wall error: newest ${err(latest).toFixed(3)} m, stamped ${err(stamped).toFixed(3)} m`,
        `t=0.5의 pose: x=${pose(0.5, rate).x.toFixed(2)} m · 벽 오차: 최신 ${err(latest).toFixed(3)} m, 시각 맞춤 ${err(stamped).toFixed(3)} m`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    };
    ctx.slider('turn rate (rad/s)', '회전율 (rad/s)', 0, 3, 0.1, rate, v => { rate = v; if (ro) draw(); });
    ro = ctx.readout(); draw(); watch(ctx, draw);
  };
})();
