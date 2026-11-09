# 레슨 14/01: N 대 N 작업 배정, 탐욕 최근접 배정과 Hungarian 최적 배정
import numpy as np


def cost_matrix(robots, tasks) -> np.ndarray:
    """C[i, j] = straight-line travel distance from robot i to task j."""
    return np.linalg.norm(np.asarray(robots)[:, None] - np.asarray(tasks)[None], axis=2)


def total(C, assign) -> float:
    return float(sum(C[i, j] for i, j in enumerate(assign)))


def greedy(C) -> list:
    """Robots in index order, each takes the nearest task still free."""
    free, out = set(range(len(C))), []
    for row in C:
        j = min(free, key=lambda k: row[k])
        free.remove(j)
        out.append(j)
    return out


def hungarian(C) -> list:
    """Optimal assignment with row/column potentials u, v (O(n^3)). Returns task index per robot."""
    n = len(C)
    u, v = np.zeros(n + 1), np.zeros(n + 1)
    p, way = np.zeros(n + 1, int), np.zeros(n + 1, int)  # p[j] = robot matched to task j (1-based, 0 = none)
    for i in range(1, n + 1):
        p[0], j0 = i, 0
        minv, used = np.full(n + 1, np.inf), np.zeros(n + 1, bool)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], np.inf, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = C[i0 - 1, j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):  # shift potentials so a new zero-reduced-cost edge appears
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:  # flip the augmenting path
            j1 = way[j0]
            p[j0], j0 = p[j1], j1
    out = [0] * n
    for j in range(1, n + 1):
        out[p[j] - 1] = j - 1
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    C = cost_matrix(rng.random((8, 2)), rng.random((8, 2)))
    print(total(C, greedy(C)), total(C, hungarian(C)))
