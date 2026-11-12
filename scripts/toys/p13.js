// 13장 토이 2종: value-spread (value iteration 이 목표에서 퍼지는 모습), chunk-vs-mean (평균 정책과 청크 표본기)
(() => {
  const root = document.documentElement;
  const watch = (ctx, draw) => {
    ctx.onRedraw(draw);
    const mo = new MutationObserver(draw); mo.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    ctx.onDispose(() => mo.disconnect());
  };

  // ---------------------------------------------------------------- value-spread (main.py 의 gridworld / backup / value_iteration)
  const LAYOUT = ['......G', '.##.##.', '...X...', '.#.##..', '.......'];
  const MOVES = [[-1, 0], [1, 0], [0, -1], [0, 1]], SIDE = [[2, 3], [2, 3], [0, 1], [0, 1]], ARROW = '↑↓←→', GAMMA = 0.9, START = '4,0';
  const rewardOf = ch => (ch === 'G' ? 1 : ch === 'X' ? -1 : 0);

  // 칸마다 행동 a 의 결과 3가지 (그대로, 옆 둘)의 도착 칸과 보상은 slip 과 무관하므로 한 번만 만든다
  const NC = 7, TERM = new Uint8Array(35), TG = new Int32Array(35 * 4 * 3), RW = new Float64Array(35 * 4 * 3);
  LAYOUT.forEach((row, r) => [...row].forEach((chr, c) => {
    TERM[r * NC + c] = chr === 'G' || chr === 'X';
    [0, 1, 2, 3].forEach(a => [a, SIDE[a][0], SIDE[a][1]].forEach((b, k) => {
      let rr = r + MOVES[b][0], cc = c + MOVES[b][1];
      if (!LAYOUT[rr] || !LAYOUT[rr][cc] || LAYOUT[rr][cc] === '#') { rr = r; cc = c; }  // 벽과 가장자리는 제자리
      TG[((r * NC + c) * 4 + a) * 3 + k] = rr * NC + cc; RW[((r * NC + c) * 4 + a) * 3 + k] = rewardOf(LAYOUT[rr][cc]);
    }));
  }));
  const viMemo = new Map();
  function vi(slip) {
    if (viMemo.has(slip)) return viMemo.get(slip);
    const p0 = 1 - slip, p1 = slip / 2;
    // 칸 s 에서 행동 a 의 backup: 도착 칸 세 곳의 (보상 + gamma * value) 를 확률로 가중해 더한다
    const Q = (V, r, c, a) => { const s = r * NC + c; if (TERM[s]) return 0; const o = (s * 4 + a) * 3; return 0 + p0 * (RW[o] + GAMMA * V[TG[o]]) + p1 * (RW[o + 1] + GAMMA * V[TG[o + 1]]) + p1 * (RW[o + 2] + GAMMA * V[TG[o + 2]]); };
    let V = new Float64Array(35), hist = [V];
    for (let it = 0; it < 200; it++) {
      const N = new Float64Array(35); let dmax = 0;
      for (let r = 0; r < 5; r++) for (let c = 0; c < NC; c++) {
        if (LAYOUT[r][c] === '#') continue;
        const v = Math.max(Q(V, r, c, 0), Q(V, r, c, 1), Q(V, r, c, 2), Q(V, r, c, 3));
        N[r * NC + c] = v; dmax = Math.max(dmax, Math.abs(v - V[r * NC + c]));
      }
      hist.push(N); V = N; if (dmax < 1e-6) break;
    }
    const m = { hist, sweeps: hist.length - 1, Q };
    viMemo.set(slip, m); return m;
  }

  window.TOYS['value-spread'] = (el, ctx) => {
    ctx.title('Value iteration spreading from the goal', 'Value iteration이 목표에서 퍼지는 모습');
    const { c, g, w: W, h: H } = ctx.canvas(320, 230);
    let slip = 0.2, k = 60, m, ro;
    const cw = W / 7, ch = H / 5;
    const draw = () => {
      const i = Math.min(k, m.sweeps), V = m.hist[i];
      g.clearRect(0, 0, W, H);
      g.textAlign = 'center'; g.textBaseline = 'middle';
      LAYOUT.forEach((row, r) => [...row].forEach((chr, q) => {
        const x = q * cw, y = r * ch;
        if (chr === '#') { g.fillStyle = ctx.color('--mut'); g.globalAlpha = 0.5; g.fillRect(x + 1, y + 1, cw - 2, ch - 2); g.globalAlpha = 1; return; }
        const v = V[r * NC + q];
        g.fillStyle = ctx.color(v >= 0 ? '--ok' : '--bad'); g.globalAlpha = Math.min(1, Math.abs(v)) * 0.85; g.fillRect(x + 1, y + 1, cw - 2, ch - 2); g.globalAlpha = 1;
        if (r + ',' + q === START) { g.strokeStyle = ctx.color('--fg'); g.lineWidth = 2; g.strokeRect(x + 2, y + 2, cw - 4, ch - 4); }
        g.fillStyle = ctx.color('--fg'); g.font = '12px system-ui,sans-serif';
        if (chr === 'G' || chr === 'X') { g.font = 'bold 14px system-ui,sans-serif'; g.fillText(chr, x + cw / 2, y + ch / 2); return; }
        g.fillText(v.toFixed(2), x + cw / 2, y + ch * 0.36);
        const qs = [0, 1, 2, 3].map(a => m.Q(V, r, q, a)), best = qs.indexOf(Math.max(...qs));
        if (v > 0.005 || v < -0.005) { g.font = 'bold 15px system-ui,sans-serif'; g.fillText(ARROW[best], x + cw / 2, y + ch * 0.74); }
      }));
      const s = V[4 * NC], qs = [0, 1, 2, 3].map(a => m.Q(V, 4, 0, a));
      ro.textContent = ctx.t(`sweep ${i} of ${m.sweeps} · start value ${s.toFixed(3)} · arrow ${ARROW[qs.indexOf(Math.max(...qs))]}`, `sweep ${i} / ${m.sweeps} · 시작 칸 value ${s.toFixed(3)} · 화살표 ${ARROW[qs.indexOf(Math.max(...qs))]}`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    };
    ctx.slider('slip probability', '미끄러질 확률', 0, 0.8, 0.1, slip, v => { slip = v; m = vi(slip); if (ro) draw(); });
    ctx.slider('sweep', 'sweep 횟수', 0, 60, 1, k, v => { k = v; if (ro) draw(); });
    ro = ctx.readout(); draw(); watch(ctx, draw);
  };

  // ---------------------------------------------------------------- chunk-vs-mean (main.py 의 demos / mean_policy / sample_chunk / rollout_chunks)
  const R_OBST = 0.3, SIGMA = 0.15, SIGMA_A = 0.01, T = 40, STEPS = 60, RUNS = 50;
  const rngOf = s => () => { s |= 0; s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const gauss = r => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(6.2831853 * r());
  const clear = path => path.every(p => Math.hypot(p[0], p[1]) >= R_OBST);
  const jitter = path => { let s = 0; for (let i = 2; i < path.length; i++) s += Math.hypot(path[i][0] - 2 * path[i - 1][0] + path[i - 2][0], path[i][1] - 2 * path[i - 1][1] + path[i - 2][1]); return s / (path.length - 2); };
  function demos() {  // 장애물 위로 6개, 아래로 거울상 6개 (잡음은 고정 seed). 계산용 Float64Array 사본도 같이 만든다
    const r = rngOf(8), P = [];
    for (let n = 0; n < 6; n++) {
      const h = 0.45 + 0.2 * r(), up = Array.from({ length: T + 1 }, (_, i) => { const x = -1 + 2 * i / T, e = i && i < T; return [x + (e ? 0.004 * gauss(r) : 0), h * (1 - x * x) + (e ? 0.004 * gauss(r) : 0)]; });
      P.push(up, up.map(p => [p[0], -p[1]]));
    }
    const ND = P.length, Pf = new Float64Array(ND * (T + 1) * 2), Af = new Float64Array(ND * T * 2);
    P.forEach((p, d) => p.forEach((q, i) => { Pf[(d * (T + 1) + i) * 2] = q[0]; Pf[(d * (T + 1) + i) * 2 + 1] = q[1]; if (i) { Af[(d * T + i - 1) * 2] = q[0] - p[i - 1][0]; Af[(d * T + i - 1) * 2 + 1] = q[1] - p[i - 1][1]; } }));
    return { P, Pf, Af, ND };
  }
  const meanRoll = ({ Pf, Af, ND }) => {
    const NS = ND * T, S = new Float64Array(NS * 2), V = new Float64Array(NS * 2), w = new Float64Array(NS);
    for (let d = 0, k = 0; d < ND; d++) for (let i = 0; i < T; i++, k++) { S[2 * k] = Pf[(d * (T + 1) + i) * 2]; S[2 * k + 1] = Pf[(d * (T + 1) + i) * 2 + 1]; V[2 * k] = Af[(d * T + i) * 2]; V[2 * k + 1] = Af[(d * T + i) * 2 + 1]; }
    let x = [-1, 0]; const path = [x];
    for (let t = 0; t < STEPS; t++) {
      let lo = Infinity; for (let k = 0; k < NS; k++) { w[k] = (S[2 * k] - x[0]) ** 2 + (S[2 * k + 1] - x[1]) ** 2; if (w[k] < lo) lo = w[k]; }
      let z = 0, ax = 0, ay = 0; for (let k = 0; k < NS; k++) { w[k] = Math.exp(-(w[k] - lo) / (2 * SIGMA ** 2)); z += w[k]; }
      for (let k = 0; k < NS; k++) { ax += w[k] * V[2 * k]; ay += w[k] * V[2 * k + 1]; }
      x = [x[0] + ax / z, x[1] + ay / z]; path.push(x);
    }
    return path;
  };
  function chunkRoll({ Pf, Af, ND }, H, ov, r) {
    const stride = H - ov, J = new Int32Array(ND), lw = new Float64Array(ND), w = new Float64Array(ND);
    let x = [-1, 0], path = [x], old = null, cur = null, t1 = 0;
    const sample = prefix => {
      for (let d = 0; d < ND; d++) {
        // x 가 증가하는 시연 위에서 가장 가까운 점: x 가 비슷한 칸에서 양쪽으로 퍼지다가 x 거리만으로 이미 진 곳에서 멈춘다 (전수 비교와 같은 답, 같은 거리면 작은 index)
        let j = 0, b = Infinity; const o0 = d * (T + 1) * 2, i0 = Math.max(0, Math.min(T - 1, Math.round((x[0] + 1) * T / 2)));
        for (let i = i0; i < T; i++) { const dx = (Pf[o0 + 2 * i] - x[0]) ** 2; if (dx > b) break; const e = dx + (Pf[o0 + 2 * i + 1] - x[1]) ** 2; if (e < b || (e === b && i < j)) { b = e; j = i; } }
        for (let i = i0 - 1; i >= 0; i--) { const dx = (Pf[o0 + 2 * i] - x[0]) ** 2; if (dx > b) break; const e = dx + (Pf[o0 + 2 * i + 1] - x[1]) ** 2; if (e < b || (e === b && i < j)) { b = e; j = i; } }
        J[d] = j; let ps = 0;
        if (prefix) for (let i = 0; i < prefix.length / 2; i++) { const q = j + i < T ? (d * T + j + i) * 2 : -1; ps += ((q < 0 ? 0 : Af[q]) - prefix[2 * i]) ** 2 + ((q < 0 ? 0 : Af[q + 1]) - prefix[2 * i + 1]) ** 2; }
        lw[d] = -b / (2 * SIGMA ** 2) - (prefix ? ps / (2 * SIGMA_A ** 2) : 0);
      }
      let m = -Infinity; for (let d = 0; d < ND; d++) if (lw[d] > m) m = lw[d];
      let tot = 0; for (let d = 0; d < ND; d++) { w[d] = Math.exp(lw[d] - m); tot += w[d]; }
      let u = r() * tot, i = 0; while (i < ND - 1 && u >= w[i]) u -= w[i++];
      const ch = new Float64Array(2 * H);
      for (let k = 0; k < H && J[i] + k < T; k++) { ch[2 * k] = Af[(i * T + J[i] + k) * 2]; ch[2 * k + 1] = Af[(i * T + J[i] + k) * 2 + 1]; }
      return ch;
    };
    for (let t = 0; t < STEPS; t++) {
      if (t % stride === 0) { const prefix = cur && cur.subarray(2 * stride); old = cur; cur = sample(prefix); t1 = t; }
      const k = t - t1, wt = old && k < ov ? (k + 1) / (ov + 1) : 1;
      const ax = wt < 1 ? wt * cur[2 * k] + (1 - wt) * old[2 * (k + stride)] : cur[2 * k], ay = wt < 1 ? wt * cur[2 * k + 1] + (1 - wt) * old[2 * (k + stride) + 1] : cur[2 * k + 1];
      x = [x[0] + ax, x[1] + ay]; path.push(x);
    }
    return path;
  }

  window.TOYS['chunk-vs-mean'] = (el, ctx) => {
    ctx.title('Mean policy vs sampled action chunks', '평균 정책 대 표본 action chunk');
    const { c, g, w: W, h: H } = ctx.canvas(320, 220);
    let Hc = 8, ov = 4, D, MP, ro; const memo = new Map();
    const sx = x => W * (0.5 + x * 0.3), sy = y => H * (0.5 - y * 0.78), tr = path => { g.beginPath(); path.forEach((p, i) => g[i ? 'lineTo' : 'moveTo'](sx(p[0]), sy(p[1]))); g.stroke(); };
    let timer = 0, cur = null;
    ctx.onDispose(() => clearTimeout(timer));
    // (H, 겹침) 마다 50번 굴린 결과를 한 번만 만든다. slider 를 움직일 때는 4 ms 조각으로 나눠 프레임을 막지 않고, 처음 그릴 때는 끝까지 만든다
    const slice = (job, all) => {
      const t0 = performance.now();
      while (job.runs.length < RUNS && (all || !job.runs.length || performance.now() - t0 < 4)) job.runs.push(chunkRoll(D, job.H, job.o, rngOf(100 + job.runs.length)));
      if (job.runs.length === RUNS && !job.done) { job.done = true; job.ok = job.runs.filter(clear).length / RUNS; job.jit = job.runs.reduce((s, p) => s + jitter(p), 0) / RUNS; }
    };
    const pump = (job, all) => {
      slice(job, all);
      if (job.done) { job.live = false; return; }
      timer = setTimeout(() => { if (cur === job) { pump(job); draw(); } else job.live = false; }, 0);
    };
    const draw = (all) => {
      const o = Math.min(ov, Hc - 1), key = Hc + ',' + o;
      if (!memo.has(key)) memo.set(key, { H: Hc, o, runs: [], done: false, live: false });
      if (cur && cur !== memo.get(key)) { clearTimeout(timer); cur.live = false; }  // 다른 조합으로 옮기면 지난 계산은 멈춘다 (기록은 남아서 이어 간다)
      cur = memo.get(key);
      if (!cur.done && (all || !cur.live)) { cur.live = true; pump(cur, all); }
      const { runs, ok, jit } = cur;
      g.clearRect(0, 0, W, H);
      g.fillStyle = ctx.color('--mut'); g.globalAlpha = 0.5; g.beginPath(); g.arc(sx(0), sy(0), R_OBST * W * 0.3, 0, 7); g.fill(); g.globalAlpha = 1;
      g.save(); g.beginPath(); g.rect(2, 2, W - 4, H - 4); g.clip();
      g.lineWidth = 1; g.strokeStyle = ctx.color('--line'); D.P.forEach(tr);
      g.lineWidth = 2; g.strokeStyle = ctx.color('--acc'); runs.slice(0, 5).forEach(tr);
      g.strokeStyle = ctx.color('--bad'); g.setLineDash([5, 4]); g.lineWidth = 2.4; tr(MP); g.setLineDash([]); g.restore();
      ro.textContent = !cur.done ? ctx.t(`mean policy: ${clear(MP) ? 'clear' : 'hits the disc'} · chunks (${Hc}, overlap ${o}): computing ${runs.length}/${RUNS}…`, `평균 정책: ${clear(MP) ? '통과' : '원판에 부딪힘'} · 청크 (${Hc}, 겹침 ${o}): 계산 중 ${runs.length}/${RUNS}…`)
        : ctx.t(`mean policy: ${clear(MP) ? 'clear' : 'hits the disc'} · chunks (${Hc}, overlap ${o}): clear ${ok.toFixed(2)}, jitter ${jit.toFixed(4)} (toy's own random draws)`,
        `평균 정책: ${clear(MP) ? '통과' : '원판에 부딪힘'} · 청크 (${Hc}, 겹침 ${o}): 통과율 ${ok.toFixed(2)}, jitter ${jit.toFixed(4)} (이 토이의 자체 난수)`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    };
    D = demos(); MP = meanRoll(D);
    ctx.slider('chunk length H', '청크 길이 H', 1, 16, 1, Hc, v => { Hc = v; if (ro) draw(); });
    ctx.slider('overlap (capped at H-1)', '겹침 (최대 H-1)', 0, 8, 1, ov, v => { ov = v; if (ro) draw(); });
    ro = ctx.readout(); draw(true); watch(ctx, () => draw());
  };
})();
