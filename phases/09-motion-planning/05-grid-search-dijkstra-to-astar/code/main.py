# 레슨 09/05: 힙 기반 Dijkstra 에 휴리스틱(맨해튼 거리 x 가중치)을 더한 A*, 확장한 칸 수 세기
import heapq

import numpy as np


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def search(grid, start, goal, w=1.0):
    """4-connected unit-cost search on a bool grid (True = wall). Priority f = g + w * manhattan.
    w = 0 is Dijkstra, w = 1 is A*, w > 1 overestimates. Returns (path or None, expanded cells in order).
    Raises ValueError if either endpoint is blocked or outside the grid."""
    for name, cell in (("start", start), ("goal", goal)):
        if not (0 <= cell[0] < grid.shape[0] and 0 <= cell[1] < grid.shape[1]) or grid[cell]:
            raise ValueError(f"{name} must be a free cell inside the grid")
    g, parent, closed, expanded = {start: 0}, {start: None}, set(), []
    heap = [(w * manhattan(start, goal), 0, start)]  # (f, -g so ties go deeper, cell)
    while heap:
        _, _, cell = heapq.heappop(heap)
        if cell in closed:
            continue  # a stale entry: this cell was already expanded with a smaller g
        closed.add(cell)
        expanded.append(cell)
        if cell == goal:
            path = []
            while cell is not None:
                path.append(cell)
                cell = parent[cell]
            return path[::-1], expanded
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cell[0] + d[0], cell[1] + d[1])
            if 0 <= n[0] < grid.shape[0] and 0 <= n[1] < grid.shape[1] and not grid[n] and g[cell] + 1 < g.get(n, 1e9):
                g[n], parent[n] = g[cell] + 1, cell
                heapq.heappush(heap, (g[n] + w * manhattan(n, goal), -g[n], n))
    return None, expanded


def parse(rows):
    """Turn rows of text ('#' wall, 'S' start, 'G' goal) into (grid, start, goal)."""
    grid = np.array([[c == "#" for c in r] for r in rows])
    find = lambda ch: next((i, r.index(ch)) for i, r in enumerate(rows) if ch in r)
    return grid, find("S"), find("G")


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    grid = rng.random((40, 40)) < 0.25
    grid[0, 0] = grid[39, 39] = False
    for w in (0, 1, 3, 6):
        path, exp = search(grid, (0, 0), (39, 39), w)
        print(f"w={w}: path cost {len(path) - 1 if path else None}, expanded {len(exp)} of {(~grid).sum()} free cells")
