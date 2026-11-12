// 08장 토이 2종: icp-steps (스캔 두 장이 한 반복씩 겹쳐 가는 모습), pose-graph-closure (표류한 정사각형이 루프 폐쇄 edge 로 닫히는 모습)
(() => {
  const root = document.documentElement;
  const wrap = a => ((a + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
  const watch = (ctx, draw) => {  // 언어·테마가 바뀌면 다시 그린다
    ctx.onRedraw(draw);
    const mo = new MutationObserver(draw); mo.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    ctx.onDispose(() => mo.disconnect());
  };
  // 점들이 들어가도록 world->canvas 변환을 만든다 (m 단위, y 는 위가 +). srcs 의 원소는 [x, y] 배열의 목록이거나 x, y 가 번갈아 놓인 Float64Array 다.
  // 돌려주는 f(x, y) 는 같은 배열 하나를 되써서 할당이 없다 (바로 값을 읽어 쓸 것)
  const fit = (srcs, W, H, pad) => {
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    const add = (x, y) => { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); };
    srcs.forEach(P => { if (P.length && P[0].length === undefined) for (let i = 0; i < P.length; i += 2) add(P[i], P[i + 1]); else P.forEach(p => add(p[0], p[1])); });
    const s = Math.min((W - 2 * pad) / (x1 - x0 || 1), (H - 2 * pad) / (y1 - y0 || 1)), ox = pad + (W - 2 * pad - (x1 - x0) * s) / 2, oy = H - pad - (H - 2 * pad - (y1 - y0) * s) / 2, o = [0, 0];
    return (x, y) => { o[0] = ox + (x - x0) * s; o[1] = oy - (y - y0) * s; return o; };
  };
  const dots = (g, P, f, col, r) => { g.fillStyle = col; for (let i = 0; i < P.length; i += 2) { const o = f(P[i], P[i + 1]); g.fillRect(o[0] - r, o[1] - r, 2 * r, 2 * r); } };

  // ---------------------------------------------------------------- icp-steps (main.py 의 room / nearest / kabsch / icp)
  const ROOM = [[0, 0], [6, 0], [6, 2], [4, 2], [4, 4], [0, 4], [0, 0]];
  const room = (sp, phase) => {
    const out = [];
    for (let i = 0; i < 6; i++) {
      const [ax, ay] = ROOM[i], [bx, by] = ROOM[i + 1], n = Math.hypot(bx - ax, by - ay);
      for (let s = phase * sp; s < n; s += sp) out.push([ax + s * (bx - ax) / n, ay + s * (by - ay) / n]);
    }
    return out;
  };
  const flat = pts => Float64Array.from(pts.flat());
  const REF = flat(room(0.05, 0)), CUR = flat(room(0.05, 0.5)), NR = REF.length / 2;
  // REF 로 kd-tree 를 만들어 최근접점을 찾는다 (전수 비교와 같은 답: 같은 거리면 작은 index, 같은 거리 가지도 끝까지 본다)
  const ORD = Array.from({ length: NR }, (_, i) => i);
  (function build(lo, hi, ax) {
    if (hi - lo < 2) return;
    ORD.slice(lo, hi).sort((p, q) => REF[2 * p + ax] - REF[2 * q + ax] || p - q).forEach((v, k) => { ORD[lo + k] = v; });
    const mid = (lo + hi) >> 1; build(lo, mid, 1 - ax); build(mid + 1, hi, 1 - ax);
  })(0, NR, 0);
  let nearD = 0, nearI = -1, qx = 0, qy = 0;  // near() 가 마지막으로 찾은 거리 제곱과 index
  function visit(lo, hi, ax) {
    if (lo >= hi) return;
    const mid = (lo + hi) >> 1, i = ORD[mid], e = (qx - REF[2 * i]) ** 2 + (qy - REF[2 * i + 1]) ** 2;
    if (e < nearD || (e === nearD && i < nearI)) { nearD = e; nearI = i; }
    const diff = (ax ? qy : qx) - REF[2 * i + ax];
    if (diff < 0) { visit(lo, mid, 1 - ax); if (diff * diff <= nearD) visit(mid + 1, hi, 1 - ax); }
    else { visit(mid + 1, hi, 1 - ax); if (diff * diff <= nearD) visit(lo, mid, 1 - ax); }
  }
  function near(px, py, hint) {  // hint: 지난 반복의 짝 index. 실제 점이므로 처음부터 좋은 상한이 되어 가지를 많이 친다
    qx = px; qy = py;
    if (hint >= 0) { nearI = hint; nearD = (px - REF[2 * hint]) ** 2 + (py - REF[2 * hint + 1]) ** 2; } else { nearD = Infinity; nearI = -1; }
    visit(0, NR, 0); return nearI;
  }
  // ICP 를 반복 하나씩 걷는 객체: step() 한 번이 반복 한 번이다. 끝나면 done = true, errs 마지막에 최종 rms 가 붙는다
  function icpRun(src) {
    const n = src.length / 2, M = new Int32Array(n).fill(-1), r = { states: [src], errs: [], done: false, n: 0 };
    let cur = src;
    r.step = () => {
      let s = 0; for (let i = 0; i < n; i++) { M[i] = near(cur[2 * i], cur[2 * i + 1], M[i]); s += nearD; }
      r.errs.push(Math.sqrt(s / n));
      let pcx = 0, pcy = 0, qcx = 0, qcy = 0;
      for (let i = 0; i < n; i++) { pcx += cur[2 * i]; pcy += cur[2 * i + 1]; qcx += REF[2 * M[i]]; qcy += REF[2 * M[i] + 1]; }
      pcx /= n; pcy /= n; qcx /= n; qcy /= n;
      let a = 0, b = 0;
      for (let i = 0; i < n; i++) { const px = cur[2 * i] - pcx, py = cur[2 * i + 1] - pcy, qx = REF[2 * M[i]] - qcx, qy = REF[2 * M[i] + 1] - qcy; a += px * qy - py * qx; b += px * qx + py * qy; }
      const th = Math.atan2(a, b), c = Math.cos(th), sn = Math.sin(th), nx = new Float64Array(2 * n);
      for (let i = 0; i < n; i++) { const x = cur[2 * i] - pcx, y = cur[2 * i + 1] - pcy; nx[2 * i] = c * x - sn * y + qcx; nx[2 * i + 1] = sn * x + c * y + qcy; }  // 2D Kabsch 의 닫힌 형태
      cur = nx; r.states.push(cur);
      const e = r.errs;
      if (r.states.length > 60 || (e.length > 1 && e[e.length - 2] - e[e.length - 1] < 1e-12)) {
        let t = 0; for (let i = 0; i < n; i++) { near(cur[2 * i], cur[2 * i + 1], -1); t += nearD; }
        e.push(Math.sqrt(t / n)); r.done = true;
      }
      r.n = r.states.length - 1;
    };
    return r;
  }

  window.TOYS['icp-steps'] = (el, ctx) => {
    ctx.title('ICP: two scans sliding together', 'ICP: 스캔 두 장이 겹쳐 가는 모습');
    const { c, g, w: W, h: H } = ctx.canvas(320, 260);
    let ang = 1, k = 60, run, f, ro, timer = 0;
    const memo = new Map();  // 시작 회전마다 반복 기록을 한 번만 만들고, 반복 slider 는 그 기록을 index 한다
    const slice = r => { const t0 = performance.now(); do r.step(); while (!r.done && performance.now() - t0 < 4); };  // 한 번에 4 ms 까지만 쓴다
    ctx.onDispose(() => clearTimeout(timer));
    const solve = () => {
      clearTimeout(timer);
      if (!memo.has(ang)) {
        const cs = Math.cos(ang), sn = Math.sin(ang), start = new Float64Array(CUR.length), mine = ang;
        for (let i = 0; i < CUR.length / 2; i++) { const x = CUR[2 * i] - 0.3, y = CUR[2 * i + 1] + 0.2; start[2 * i] = x * cs + y * sn; start[2 * i + 1] = -x * sn + y * cs; }  // (cur - [0.3,-0.2]) @ [[c,-s],[s,c]]
        const r = icpRun(start), seal = () => memo.set(mine, { run: r, f: fit([REF, start, r.states[r.n]], W, H, 14) });
        run = r; f = fit([REF, start], W, H, 14); slice(r);  // 조각으로 나눠 프레임을 막지 않고, 끝나면 숫자를 확정한다 (만들 때도 같다)
        const go = () => { if (mine !== ang) return; slice(r); if (r.done) { seal(); ({ run, f } = memo.get(mine)); } else timer = setTimeout(go, 0); draw(); };
        if (r.done) seal(); else { timer = setTimeout(go, 0); return; }
      }
      ({ run, f } = memo.get(ang));
    };
    const draw = () => {
      const i = Math.min(k, run.done ? run.n : run.errs.length - 1), S = run.states[i];
      g.clearRect(0, 0, W, H);
      g.strokeStyle = ctx.color('--line'); g.lineWidth = 1; g.beginPath();
      for (let j = 0; j < S.length / 2; j += 10) { const q = near(S[2 * j], S[2 * j + 1]), a = f(S[2 * j], S[2 * j + 1]); g.moveTo(a[0], a[1]); const b = f(REF[2 * q], REF[2 * q + 1]); g.lineTo(b[0], b[1]); }
      g.stroke();
      dots(g, REF, f, ctx.color('--mut'), 1.5); dots(g, S, f, ctx.color('--acc'), 1.5);
      ro.textContent = !run.done ? ctx.t(`iteration ${i} · rms ${run.errs[i].toFixed(3)} m · computing…`, `반복 ${i} · rms ${run.errs[i].toFixed(3)} m · 계산 중…`)
        : i < run.n ? ctx.t(`iteration ${i} of ${run.n} · rms ${run.errs[i].toFixed(3)} m`, `반복 ${i} / ${run.n} · rms ${run.errs[i].toFixed(3)} m`)
        : ctx.t(`${run.n} iterations · final rms ${run.errs[i].toFixed(3)} m`, `${run.n}번 반복 · 최종 rms ${run.errs[i].toFixed(3)} m`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    };
    ctx.slider('start rotation (rad)', '시작 회전 (rad)', 0, 3, 0.1, ang, v => { ang = v; if (ro) { solve(); draw(); } });
    ctx.slider('iteration', '반복 횟수', 0, 60, 1, k, v => { k = v; if (ro) draw(); });
    ro = ctx.readout(); solve(); draw(); watch(ctx, draw);
  };

  // ---------------------------------------------------------------- pose-graph-closure (main.py 의 world / residuals / solve)
  const SIDE = 5, NP = 4 * SIDE, SD = [0.02, 0.02, 0.01], WT = [1 / 0.05, 1 / 0.05, 1 / 0.02];
  // main.py 가 default_rng(0) 으로 뽑은 odometry 잡음 20개 + 폐쇄 edge 잡음 1개 (소수 5자리)
  const NOISE = [[0.00251, -0.00264, 0.0064], [0.0021, -0.01071, 0.00362], [0.02608, 0.01894, -0.00704], [-0.02531, -0.01247, 0.00041], [-0.0465, -0.00438, -0.01246], [-0.01465, -0.01089, -0.00316], [0.00823, 0.02085, -0.00129], [0.02733, -0.0133, 0.00352], [0.01807, 0.00188, -0.00743], [-0.01843, -0.00915, 0.0022], [-0.02019, -0.00418, -0.00159], [0.01082, 0.00429, 0.00355], [-0.01308, -0.00259, 0.00784], [0.02987, -0.02518, 0.01514], [0.02692, 0.01563, 0.00264], [-0.00628, 0.02916, 0.0196], [0.03603, 0.0263, 0.00357], [-0.02417, -9e-05, 0.00656], [-0.02577, 0.0079, 0.0043], [0.01392, -0.02368, -0.00662], [-0.00873, -0.0234, 0.01739]];
  const compose = (a, d) => { const c = Math.cos(a[2]), s = Math.sin(a[2]); return [a[0] + c * d[0] - s * d[1], a[1] + s * d[0] + c * d[1], wrap(a[2] + d[2])]; };
  const between = (a, b) => { const c = Math.cos(a[2]), s = Math.sin(a[2]), dx = b[0] - a[0], dy = b[1] - a[1]; return [c * dx + s * dy, -s * dx + c * dy, wrap(b[2] - a[2])]; };
  const walk = ds => { const X = [[0, 0, 0]]; ds.forEach(d => X.push(compose(X[X.length - 1], d))); return X; };
  function gauss(A, b) {  // 가운데 줄이 가장 큰 행을 고르는 소거법
    const n = b.length;
    for (let i = 0; i < n; i++) {
      let p = i; for (let r = i + 1; r < n; r++) if (Math.abs(A[r][i]) > Math.abs(A[p][i])) p = r;
      [A[i], A[p]] = [A[p], A[i]]; [b[i], b[p]] = [b[p], b[i]];
      for (let r = i + 1; r < n; r++) { const m = A[r][i] / A[i][i]; if (m) { for (let q = i; q < n; q++) A[r][q] -= m * A[i][q]; b[r] -= m * b[i]; } }
    }
    for (let i = n - 1; i >= 0; i--) { for (let q = i + 1; q < n; q++) b[i] -= A[i][q] * b[q]; b[i] /= A[i][i]; }
    return b;
  }
  function optimise(X0, E) {  // pose 0 고정, Gauss-Newton. 간선 하나는 두 pose 에만 걸리므로 해석적 Jacobian 의 3x3 블록 둘로 normal equation 을 쌓는다
    let X = X0.map(p => p.slice());
    const nv = 3 * (X.length - 1);
    for (let it = 0; it < 15; it++) {
      const A = Array.from({ length: nv }, () => new Float64Array(nv)), g = new Float64Array(nv);
      for (const [i, j, z] of E) {
        const a = X[i], b = X[j], c = Math.cos(a[2]), s = Math.sin(a[2]), dx = b[0] - a[0], dy = b[1] - a[1];
        const u = c * dx + s * dy, v = -s * dx + c * dy;  // between(a, b) 의 위치 성분
        const r = [WT[0] * (u - z[0]), WT[1] * (v - z[1]), WT[2] * wrap(wrap(b[2] - a[2]) - z[2])];
        const Ja = [[-c, -s, v], [s, -c, -u], [0, 0, -1]], Jb = [[c, s, 0], [-s, c, 0], [0, 0, 1]];  // 열 순서 x, y, theta
        for (const [pose, Jm] of [[i, Ja], [j, Jb]]) {
          if (!pose) continue;
          for (let p = 0; p < 3; p++) {
            const cp = 3 * (pose - 1) + p;
            for (let k = 0; k < 3; k++) g[cp] -= WT[k] * Jm[k][p] * r[k];
            for (const [pose2, Jn] of [[i, Ja], [j, Jb]]) {
              if (!pose2) continue;
              for (let q = 0; q < 3; q++) { const cq = 3 * (pose2 - 1) + q; for (let k = 0; k < 3; k++) A[cp][cq] += WT[k] * Jm[k][p] * WT[k] * Jn[k][q]; }
            }
          }
        }
      }
      for (let k = 0; k < nv; k++) A[k][k] += 1e-9;
      const dxv = gauss(A, g);
      X = X.map((p, i) => i ? p.map((v, k) => k === 2 ? wrap(v + dxv[3 * (i - 1) + k]) : v + dxv[3 * (i - 1) + k]) : p);
      if (Math.max(...dxv.map(Math.abs)) < 1e-9) break;
    }
    return X;
  }
  const ate = (X, T) => Math.sqrt(X.reduce((s, p, i) => s + (p[0] - T[i][0]) ** 2 + (p[1] - T[i][1]) ** 2, 0) / X.length);

  window.TOYS['pose-graph-closure'] = (el, ctx) => {
    ctx.title('Pose graph: close the loop', 'Pose graph: 루프를 닫아 보기');
    const { c, g, w: W, h: H } = ctx.canvas(320, 300);
    let bias = 0.02, closed = true, ro, btn, d;
    const truthSteps = Array.from({ length: NP }, (_, k) => [1, 0, (k + 1) % SIDE ? 0 : Math.PI / 2]), T = walk(truthSteps);
    const memo = new Map();  // bias 값마다 한 번만 푼다 (button 은 다시 풀지 않는다)
    const build = () => {
      if (memo.has(bias)) { d = memo.get(bias); return; }
      const zs = truthSteps.map((s, k) => s.map((v, q) => v + NOISE[k][q] + (q === 2 ? bias : 0)));
      const X0 = walk(zs), E = zs.map((z, k) => [k, k + 1, z]);
      E.push([0, NP, between(T[0], T[NP]).map((v, q) => v + NOISE[NP][q])]);
      d = { X0, X: optimise(X0, E) };
      d.f = fit([T, d.X0, d.X], W, H - 22, 14); memo.set(bias, d);
    };
    const line = (P, col, w, dash) => { g.beginPath(); g.setLineDash(dash || []); g.strokeStyle = col; g.lineWidth = w; P.forEach((p, i) => { const o = d.f(p[0], p[1]), x = o[0], y = o[1]; g[i ? 'lineTo' : 'moveTo'](x, y); }); g.stroke(); g.setLineDash([]); };
    const draw = () => {
      g.clearRect(0, 0, W, H);
      line(T, ctx.color('--mut'), 1.2, [4, 4]);
      line(d.X0, ctx.color('--bad'), closed ? 1.2 : 2.4);
      if (closed) line(d.X, ctx.color('--ok'), 2.4);
      g.font = '12px system-ui,sans-serif'; g.textAlign = 'left'; let lx = 8;
      [['--mut', ctx.t('truth', '정답'), 1], ['--bad', ctx.t('odometry', 'odometry'), 1], ['--ok', ctx.t('optimised', '최적화'), closed]].forEach(([col, name, on]) => {
        if (!on) return; g.fillStyle = ctx.color(col); g.fillRect(lx, H - 14, 14, 3); g.fillText(name, lx + 18, H - 8); lx += 30 + g.measureText(name).width;
      });
      const gap = Math.hypot(d.X0[NP][0], d.X0[NP][1]).toFixed(2);
      ro.textContent = closed ? ctx.t(`end of odometry ${gap} m from the start · rms error ${ate(d.X0, T).toFixed(2)} → ${ate(d.X, T).toFixed(2)} m`, `odometry 끝이 시작에서 ${gap} m · rms 오차 ${ate(d.X0, T).toFixed(2)} → ${ate(d.X, T).toFixed(2)} m`)
        : ctx.t(`end of odometry ${gap} m from the start · rms error ${ate(d.X0, T).toFixed(2)} m`, `odometry 끝이 시작에서 ${gap} m · rms 오차 ${ate(d.X0, T).toFixed(2)} m`);
      btn.textContent = closed ? ctx.t('Remove loop-closure edge', '폐쇄 edge 빼기') : ctx.t('Add loop-closure edge', '폐쇄 edge 더하기');
      btn.setAttribute('aria-pressed', closed);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    };
    ctx.slider('heading bias per step (rad)', '걸음마다 heading 편향 (rad)', 0, 0.06, 0.01, bias, v => { bias = v; if (ro) { build(); draw(); } });
    btn = document.createElement('button'); btn.type = 'button'; btn.onclick = () => { closed = !closed; draw(); }; el.appendChild(btn);
    ro = ctx.readout(); build(); draw(); watch(ctx, draw);
  };
})();
