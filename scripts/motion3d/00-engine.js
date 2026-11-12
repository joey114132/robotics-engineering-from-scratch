// 3D motion engine, no library: Canvas 2D, perspective camera, painter's-algorithm depth sort, flat shading, drag/keys to orbit.
// A widget is MOTION.three(name, spec, frame): frame(s, t, m) queues primitives (s.line, s.path, s.dot, s.box, s.wire, s.label) each frame.
// Colours are CSS variable names ('--pf'), resolved per theme. World axes: x right, y into the screen, z up. Loaded only on pages with a "three" slot.
(() => {
  const M = window.MOTION, PI = Math.PI, sin = Math.sin, cos = Math.cos, clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const rx = a => [[1, 0, 0], [0, cos(a), -sin(a)], [0, sin(a), cos(a)]];
  const ry = a => [[cos(a), 0, sin(a)], [0, 1, 0], [-sin(a), 0, cos(a)]];
  const rz = a => [[cos(a), -sin(a), 0], [sin(a), cos(a), 0], [0, 0, 1]];
  const mv = (R, v) => [0, 1, 2].map(i => R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2]);
  // perspective scale of a point `depth` past the look point, seen from `dist` away. A point at or behind the camera
  // plane is held at a tenth of dist in front of it, so an orbited floor corner runs off the canvas and never mirrors.
  const persp = (dist, depth) => dist / Math.max(dist + depth, .1 * dist);
  const mm = (A, B) => A.map(r => [0, 1, 2].map(j => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j]));
  const LIGHT = [0.35, -0.45, 0.82];   // fixed in the world, so a face visibly changes shade as the body turns
  const CUBE = [[[1, 0, 0], [[1, -1, -1], [1, 1, -1], [1, 1, 1], [1, -1, 1]]], [[-1, 0, 0], [[-1, -1, -1], [-1, -1, 1], [-1, 1, 1], [-1, 1, -1]]],
    [[0, 1, 0], [[-1, 1, -1], [-1, 1, 1], [1, 1, 1], [1, 1, -1]]], [[0, -1, 0], [[-1, -1, -1], [1, -1, -1], [1, -1, 1], [-1, -1, 1]]],
    [[0, 0, 1], [[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]]], [[0, 0, -1], [[-1, -1, -1], [-1, 1, -1], [1, 1, -1], [1, -1, -1]]]];
  const EDGES = [[0, 1], [1, 2], [2, 3], [3, 0], [4, 5], [5, 6], [6, 7], [7, 4], [0, 4], [1, 5], [2, 6], [3, 7]];

  function three(name, spec, frame) {
    M[name] = (el, m) => {
      const W = spec.W || 480, H = spec.H || 300, unit = spec.unit || 100, period = spec.period || 0, rest = spec.rest != null ? spec.rest : 4;
      const canvas = document.createElement('canvas'), ctx = canvas.getContext && canvas.getContext('2d');
      if (!ctx) { el.classList.add('mnote'); el.textContent = m.t('This 3D view needs canvas support.', '이 3D 화면은 canvas 지원이 필요합니다.'); return; }
      el.classList.add('motion-on');
      canvas.style.cssText = `display:block;width:100%;height:auto;aspect-ratio:${W}/${H};touch-action:pan-y;cursor:grab;outline-offset:-3px`;
      canvas.tabIndex = 0; canvas.setAttribute('role', 'img');
      const lab = () => canvas.setAttribute('aria-label', m.t(spec.en, spec.ko) + m.t('. Drag or use the arrow keys to rotate the view.', '. 드래그하거나 방향키로 시점을 돌릴 수 있습니다.'));
      lab(); el.appendChild(canvas);
      const cam = { yaw: 0, pitch: 0 }, base = Object.assign({ yaw: .6, pitch: .42, dist: 7 }, spec.cam), user = { yaw: 0, pitch: 0, on: false };
      let family = '';   // text font, read once (a style read per label was the biggest cost of a frame)
      const colors = {}, probe = document.createElement('i'); probe.style.display = 'none'; el.appendChild(probe);
      const col = v => colors[v] || (colors[v] = (probe.style.color = `var(${v})`, ctx.fillStyle = getComputedStyle(probe).color, ctx.fillStyle));
      let S = 1, T = rest, Rv = null, items = [];
      // world -> screen: spin about z (yaw), tilt about x (pitch), then perspective divide; depth d grows away from the camera
      const L = spec.look || [0, 0, 0];   // spec.look: the world point shown at the centre of the view
      const proj = p => { const q = mv(Rv, [p[0] - L[0], p[1] - L[1], p[2] - L[2]]), k = unit * persp(base.dist, q[1]); return [W / 2 + k * q[0], H / 2 + (spec.oy != null ? spec.oy : 24) - k * q[2], q[1]]; };   // oy: the view centre sits a little low, under the text lines
      const add = (d, fn) => items.push({ d, fn });
      const stroke = (c, w, o) => { ctx.strokeStyle = col(c); ctx.lineWidth = w || 2; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.setLineDash(o && o.dash || []); ctx.globalAlpha = o && o.a != null ? o.a : 1; ctx.stroke(); ctx.globalAlpha = 1; };
      const s = {
        W, H, t: 0, rx, ry, rz, mv, mm, col, cam,
        line(a, b, c, w, o) { const A = proj(a), B = proj(b); add((A[2] + B[2]) / 2 - (o && o.front ? 9 : 0), () => { ctx.beginPath(); ctx.moveTo(A[0], A[1]); ctx.lineTo(B[0], B[1]); stroke(c, w, o); }); },
        // polyline; runs on the near and far side of o.mid (default the origin's depth) are queued separately so a ring can pass behind a solid
        path(pts, c, w, o) {
          const P = pts.map(proj), mid = o && o.mid != null ? o.mid : 0; let run = [];
          const flush = () => { if (run.length > 1) { const r = run, d = r.reduce((x, q) => x + q[2], 0) / r.length; add(d, () => { ctx.beginPath(); r.forEach((q, i) => i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1])); stroke(c, w, o); }); } };
          P.forEach(q => { if (run.length && (q[2] > mid) !== (run[run.length - 1][2] > mid)) { run.push(q); flush(); run = [q]; } else run.push(q); }); flush();
        },
        dot(p, c, r, o) { const A = proj(p); add(A[2] - (o && o.front ? 9 : 0), () => { ctx.beginPath(); ctx.arc(A[0], A[1], r, 0, 2 * PI); ctx.globalAlpha = o && o.a != null ? o.a : 1; ctx.fillStyle = col(c); ctx.fill(); ctx.globalAlpha = 1; if (o && o.ring) { ctx.strokeStyle = col('--card'); ctx.lineWidth = 2; ctx.stroke(); } }); },
        // a convex solid, centre ctr, half-sizes h, orientation R; faces behind the view are dropped, the rest are shaded by the world light
        box(ctr, h, R, c, o) {
          const a = o && o.a != null ? o.a : 1;
          CUBE.forEach(([n, vs]) => {
            const wn = mv(R, n), vn = mv(Rv, wn); if (vn[1] > 0) return;
            const P = vs.map(v => proj(mv(R, [v[0] * h[0], v[1] * h[1], v[2] * h[2]]).map((x, i) => x + ctr[i]))), sh = clamp(.5 + .5 * (wn[0] * LIGHT[0] + wn[1] * LIGHT[1] + wn[2] * LIGHT[2]), 0, 1);
            add(P.reduce((x, q) => x + q[2], 0) / 4, () => { ctx.beginPath(); P.forEach((q, i) => i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1])); ctx.closePath(); ctx.globalAlpha = a; ctx.fillStyle = col(c); ctx.fill();
              ctx.fillStyle = sh < .55 ? col('--fg') : col('--card'); ctx.globalAlpha = a * (sh < .55 ? (.55 - sh) * .9 : (sh - .55) * .55); ctx.fill(); ctx.globalAlpha = a; ctx.strokeStyle = col('--card'); ctx.lineWidth = 1.5; ctx.stroke(); ctx.globalAlpha = 1; });
          });
        },
        wire(ctr, h, R, c, w, o) {
          const V = [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]].map(v => proj(mv(R, [v[0] * h[0], v[1] * h[1], v[2] * h[2]]).map((x, i) => x + ctr[i])));
          add(proj(ctr)[2], () => { ctx.beginPath(); EDGES.forEach(([i, j]) => { ctx.moveTo(V[i][0], V[i][1]); ctx.lineTo(V[j][0], V[j][1]); }); stroke(c, w, o); });
        },
        // filled polygon (a plane patch, a hull face): alpha o.a, outline colour o.edge
        poly(pts, c, o) { const P = pts.map(proj); add(P.reduce((x, q) => x + q[2], 0) / P.length, () => { ctx.beginPath(); P.forEach((q, i) => i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1])); ctx.closePath(); ctx.globalAlpha = o && o.a != null ? o.a : .4; ctx.fillStyle = col(c); ctx.fill(); ctx.globalAlpha = 1; if (o && o.edge) { ctx.beginPath(); P.forEach((q, i) => i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1])); ctx.closePath(); stroke(o.edge, o.w || 1.5, o); } }); },
        // a line with an arrow head at b (head drawn in screen space)
        arrow(a, b, c, w, o) { const A = proj(a), B = proj(b), dx = B[0] - A[0], dy = B[1] - A[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L;
          add((A[2] + B[2]) / 2 - (o && o.front ? 9 : 0), () => { ctx.beginPath(); ctx.moveTo(A[0], A[1]); ctx.lineTo(B[0], B[1]); [.45, -.45].forEach(k => { ctx.moveTo(B[0], B[1]); ctx.lineTo(B[0] - 10 * (ux * Math.cos(k) - uy * Math.sin(k)), B[1] - 10 * (uy * Math.cos(k) + ux * Math.sin(k))); }); stroke(c, w, o); }); },
        // many small squares in one item (a point cloud): drawn in the order given, one depth for the batch
        points(pts, c, r, o) { const P = pts.map(proj); add(P.reduce((x, q) => x + q[2], 0) / (P.length || 1) + (o && o.bias || 0), () => { ctx.fillStyle = col(c); ctx.globalAlpha = o && o.a != null ? o.a : 1; P.forEach(q => ctx.fillRect(q[0] - r, q[1] - r, 2 * r, 2 * r)); ctx.globalAlpha = 1; }); },
        // text drawn last, over the geometry, with a halo in the card colour
        label(p, str, c, size, align, dx, dy) { const A = proj(p); add(-1e9, () => text(str, A[0] + (dx || 0), A[1] + (dy || 0), c, size, align)); },
        text(x, y, str, c, size, align) { add(-1e9, () => text(str, x, y, c, size, align)); },
      };
      const text = (str, x, y, c, size, align) => { ctx.font = `600 ${size || 16}px ${family || (family = getComputedStyle(el).fontFamily)}`; ctx.textAlign = align || 'left'; ctx.lineJoin = 'round'; ctx.lineWidth = 5; ctx.strokeStyle = col('--card'); ctx.strokeText(str, x, y); ctx.fillStyle = col(c || '--fg'); ctx.fillText(str, x, y); };
      function render(t) {
        const t0 = performance.now(); T = t; s.t = t; items = [];
        const sway = m.reduced() || user.on || !period ? 0 : .22 * sin(2 * PI * t / period);
        cam.yaw = base.yaw + user.yaw + sway; cam.pitch = clamp(base.pitch + user.pitch, -1.3, 1.45);
        Rv = mm(rx(cam.pitch), rz(cam.yaw));
        sync(t); frame(s, t, m);
        if (!user.on) s.text(W / 2, H - 10, m.t('Drag to rotate', '드래그해서 돌려 보세요'), '--mut', 15, 'center');
        items.sort((a, b) => b.d - a.d);
        ctx.setTransform(S, 0, 0, S, 0, 0); ctx.clearRect(0, 0, W, H);
        for (const it of items) it.fn();
        M3D.ms[name] = +((M3D.ms[name] || 0) * .9 + (performance.now() - t0) * .1).toFixed(2);   // moving average of the draw time, ms
      }
      // controls: sliders and toggles under the canvas; s.v[id] holds the value. A slider with auto(t) follows it until the reader touches it.
      s.v = {}; const ctls = (spec.controls || []).map(c => {
        const row = document.createElement('label'), txt = document.createElement('span'), inp = document.createElement('input');
        row.style.cssText = 'display:flex;align-items:center;gap:10px;min-height:44px;padding:0 16px;font-size:14px;color:var(--mut)'; txt.style.cssText = 'flex:0 0 46%';
        inp.type = c.toggle ? 'checkbox' : 'range'; inp.style.cssText = c.toggle ? 'width:22px;height:22px;accent-color:var(--pf)' : 'flex:1;min-width:0;accent-color:var(--pf)';
        if (!c.toggle) { inp.min = c.min; inp.max = c.max; inp.step = c.step; }
        row.append(txt, inp); el.insertBefore(row, probe); const k = { c, inp, txt, manual: false, shown: '' };
        inp.addEventListener('input', () => { k.manual = true; user.on = true; render(T); });
        return k;
      });
      const sync = t => ctls.forEach(k => { const c = k.c;
        if (c.toggle) s.v[c.id] = k.inp.checked = k.manual ? k.inp.checked : (c.auto ? c.auto(t) : !!c.val);
        else { if (!k.manual) k.inp.value = c.auto ? c.auto(t) : c.val; s.v[c.id] = +k.inp.value; }
        const str = m.t(c.en, c.ko) + (c.toggle ? '' : ': ' + s.v[c.id].toFixed(c.dec || 0) + (c.unit || '')); if (str !== k.shown) k.txt.textContent = k.shown = str; });
      const size = () => { const dpr = Math.min(devicePixelRatio || 1, 2), w = Math.max(1, Math.round(el.clientWidth * dpr)); if (canvas.width !== w) { canvas.width = w; canvas.height = Math.round(w * H / W); S = w / W; render(T); } };
      const ro = window.ResizeObserver ? new ResizeObserver(size) : null; ro && ro.observe(el); size();
      let drag = null;
      canvas.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY }; user.on = true; canvas.setPointerCapture(e.pointerId); canvas.style.cursor = 'grabbing'; });
      canvas.addEventListener('pointermove', e => { if (!drag) return; user.yaw += (e.clientX - drag.x) * .01; user.pitch += (e.clientY - drag.y) * .01; drag = { x: e.clientX, y: e.clientY }; render(T); });
      const up = () => { drag = null; canvas.style.cursor = 'grab'; }; canvas.addEventListener('pointerup', up); canvas.addEventListener('pointercancel', up);
      canvas.addEventListener('keydown', e => { const k = { ArrowLeft: [-.1, 0], ArrowRight: [.1, 0], ArrowUp: [0, -.1], ArrowDown: [0, .1] }[e.key]; if (!k) return; e.preventDefault(); user.on = true; user.yaw += k[0]; user.pitch += k[1]; render(T); });
      m.onTheme(() => { for (const k in colors) delete colors[k]; family = ''; lab(); });
      m.onDispose(() => { ro && ro.disconnect(); M3D.live--; });
      M3D.live++;
      m.caption(spec.cap[0], spec.cap[1]);
      m.loop((t) => render(m.reduced() ? rest : t), { rest, period });
    };
  }
  // eigen-decomposition of a symmetric 3x3 (Jacobi): {w: eigenvalues descending, v: matching unit vectors}
  const eig3 = S => {
    const A = S.map(r => r.slice()), V = [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
    for (let it = 0; it < 30; it++) {
      let p = 0, q = 1, mx = Math.abs(A[0][1]); if (Math.abs(A[0][2]) > mx) { q = 2; mx = Math.abs(A[0][2]); } if (Math.abs(A[1][2]) > mx) { p = 1; q = 2; mx = Math.abs(A[1][2]); } if (mx < 1e-12) break;
      const th = (A[q][q] - A[p][p]) / (2 * A[p][q]), t = (th < 0 ? -1 : 1) / (Math.abs(th) + Math.sqrt(th * th + 1)), c = 1 / Math.sqrt(t * t + 1), sn = t * c;
      for (let k = 0; k < 3; k++) { const a = A[k][p], b = A[k][q]; A[k][p] = c * a - sn * b; A[k][q] = sn * a + c * b; }
      for (let k = 0; k < 3; k++) { const a = A[p][k], b = A[q][k]; A[p][k] = c * a - sn * b; A[q][k] = sn * a + c * b; }
      for (let k = 0; k < 3; k++) { const a = V[k][p], b = V[k][q]; V[k][p] = c * a - sn * b; V[k][q] = sn * a + c * b; }
    }
    const o = [0, 1, 2].sort((i, j) => A[j][j] - A[i][i]); return { w: o.map(i => A[i][i]), v: o.map(i => [V[0][i], V[1][i], V[2][i]]) };
  };
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2], sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], add3 = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const M3D = window.M3D = { rx, ry, rz, mv, mm, eig3, dot, sub, add: add3, mul, cross, persp, live: 0, ms: {} };
  M.three = three;
})();
