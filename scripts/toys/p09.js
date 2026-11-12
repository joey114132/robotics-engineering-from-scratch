// 09장 토이: 격자 탐색에서 휴리스틱 가중치 w 를 올리면 확장하는 칸이 줄고 경로가 길어지는 것을 보여 준다 (astar-flood)
(() => {
  // lesson 09/05 의 40x40 격자(numpy default_rng(0), 벽 25%): 한 줄이 40비트, 1 = 벽
  const ROWS = ['30150c0080', '0295362400', '0088840945', '0580012285', '0004064248', '512a071028', '8080411480', '0050820212', '1216286121', '0d488d0014', 'b080050802', '4040263360', '000008a021', '3003204040', '3d4a021800', '82c86240e2', 'c104c49074', '4c30045001', '8900219220', '4241750088', '24240070ea', '08210900c0', '0010801001', '4c01830504', '0a1001104a', '80b6c23000', 'e0882c0242', '40030b6c38', '00814c0919', '0200444295', '00c2180105', '02f5000548', '221b00c803', 'fbb00cc590', '1088180008', '0082040165', '6614398084', '11080b9000', '3352294856', '3800081c00'];
  const N = 40;
  const wall = ROWS.map(h => h.split('').map(c => parseInt(c, 16).toString(2).padStart(4, '0')).join('').split('').map(b => b === '1'));
  wall[0][0] = wall[N - 1][N - 1] = false;
  const free = wall.flat().filter(x => !x).length;
  const man = (r, c) => Math.abs(r - (N - 1)) + Math.abs(c - (N - 1));

  // main.py 의 search(): 우선순위 (f, -g, 칸) 순서까지 같게 한다. 이진 힙과 Int32Array 로 칸당 비용을 줄였고 w 별로 결과를 기억한다
  const PX = 8, cache = new Map();  // PX: 칸 하나의 canvas 픽셀 (40 * 8 = 320)
  const wallPath = new Path2D(); wall.forEach((row, r) => row.forEach((x, k) => x && wallPath.rect(k * PX, r * PX, PX, PX)));
  function search(w) {
    if (cache.has(w)) return cache.get(w);
    const g = new Int32Array(N * N).fill(1 << 30), par = new Int32Array(N * N).fill(-1), closed = new Uint8Array(N * N), exp = [], heap = [];
    const less = (a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2];
    const push = it => { let i = heap.push(it) - 1; while (i) { const p = (i - 1) >> 1; if (less(heap[p], it) <= 0) break; heap[i] = heap[p]; i = p; } heap[i] = it; };
    const pop = () => {
      const top = heap[0], last = heap.pop();
      if (heap.length) { let i = 0; for (;;) { let c = 2 * i + 1; if (c >= heap.length) break; if (c + 1 < heap.length && less(heap[c + 1], heap[c]) < 0) c++; if (less(last, heap[c]) <= 0) break; heap[i] = heap[c]; i = c; } heap[i] = last; }
      return top;
    };
    g[0] = 0; push([w * man(0, 0), 0, 0]);
    let res = { path: null, exp };
    while (heap.length) {
      const id = pop()[2];
      if (closed[id]) continue;
      closed[id] = 1; exp.push(id);
      if (id === N * N - 1) { const path = []; for (let k = id; k >= 0; k = par[k]) path.push(k); res = { path, exp }; break; }
      const r = Math.floor(id / N), c = id % N;
      for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const rr = r + dr, cc = c + dc, n = rr * N + cc;
        if (rr < 0 || cc < 0 || rr >= N || cc >= N || wall[rr][cc] || g[id] + 1 >= g[n]) continue;
        g[n] = g[id] + 1; par[n] = id;
        push([g[n] + w * man(rr, cc), -g[n], n]);
      }
    }
    res.pathObj = new Path2D(); res.exp.forEach(id => res.pathObj.rect((id % N) * PX, Math.floor(id / N) * PX, PX, PX));
    cache.set(w, res);
    return res;
  }

  window.TOYS['astar-flood'] = (el, ctx) => {
    ctx.title('Heuristic weight: Dijkstra to A* to greedy', '휴리스틱 가중치: Dijkstra에서 A*, 탐욕까지');
    const { c, g, w: W, h: H } = ctx.canvas(N * PX, N * PX);
    const S = PX; let w = 1, ro;
    const draw = () => {
      const { path, exp, pathObj } = search(w);
      g.clearRect(0, 0, W, H);
      g.fillStyle = ctx.color('--mut'); g.globalAlpha = 0.55;
      g.fill(wallPath);
      g.fillStyle = ctx.color('--acc'); g.globalAlpha = 0.28;
      g.fill(pathObj);
      g.globalAlpha = 1;
      if (path) {
        g.beginPath(); g.strokeStyle = ctx.color('--ok'); g.lineWidth = 2.5; g.lineJoin = 'round';
        path.forEach((id, i) => g[i ? 'lineTo' : 'moveTo']((id % N + 0.5) * S, (Math.floor(id / N) + 0.5) * S)); g.stroke();
      }
      g.fillStyle = ctx.color('--fg'); g.font = 'bold 12px system-ui,sans-serif'; g.textAlign = 'left';
      g.fillText('S', 1, 11); g.textAlign = 'right'; g.fillText('G', W - 1, H - 2);
      const cost = path ? path.length - 1 : '-';
      ro.textContent = ctx.t(`w=${w} · expanded ${exp.length} of ${free} free cells · path cost ${cost}`, `w=${w} · 확장 ${exp.length}칸 (빈 칸 ${free}칸 중) · 경로 비용 ${cost}`);
      c.setAttribute('role', 'img'); c.setAttribute('aria-label', ro.textContent);
    };
    ctx.slider('weight w (0 = Dijkstra, 1 = A*)', '가중치 w (0 = Dijkstra, 1 = A*)', 0, 6, 0.5, w, v => { w = v; ro && draw(); });
    ro = ctx.readout(); draw();
    ctx.onRedraw(draw);
    const mo = new MutationObserver(draw); mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    ctx.onDispose(() => mo.disconnect());
  };
})();
