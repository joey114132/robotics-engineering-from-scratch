# 레슨 09/02: 원형 장애물이 있는 2D 평면의 RRT 와 무작위 path shortcutting (시드 고정)
import numpy as np


def seg_free(a, b, obstacles):
    """True if segment a-b stays outside every circle (c, r): closest point on the segment, not just the endpoints."""
    d = b - a
    L2 = float(d @ d)
    for c, r in obstacles:
        t = 0.0 if L2 == 0 else float(np.clip((c - a) @ d / L2, 0, 1))
        if np.linalg.norm(a + t * d - c) <= r:
            return False
    return True


def rrt(start, goal, obstacles, bounds, seed=0, step=0.4, iters=3000, goal_bias=0.1):
    """Grow a tree from start. Returns (nodes, parent index per node, path or None)."""
    rng = np.random.default_rng(seed)
    lo, hi = bounds
    buf = np.zeros((iters + 2, 2))  # preallocated so the nearest-node search is one vectorised call
    buf[0], parent = start, [-1]
    n = 1
    for _ in range(iters):
        sample = goal if rng.random() < goal_bias else rng.uniform(lo, hi)
        i = int(np.argmin(np.linalg.norm(buf[:n] - sample, axis=1)))
        d = sample - buf[i]
        dist = np.linalg.norm(d)
        if dist == 0:
            continue
        new = buf[i] + d / dist * min(step, dist)
        if not seg_free(buf[i], new, obstacles):
            continue
        buf[n] = new
        parent.append(i)
        n += 1
        if np.linalg.norm(goal - new) <= step and seg_free(new, goal, obstacles):
            buf[n] = goal
            parent.append(n - 1)
            n += 1
            path, k = [], n - 1
            while k != -1:
                path.append(buf[k].copy())
                k = parent[k]
            return buf[:n].copy(), parent, path[::-1]
    return buf[:n].copy(), parent, None


def shortcut(path, obstacles, seed=0, tries=200):
    """Pick two path points at random; if the straight segment between them is free, drop everything in between."""
    rng = np.random.default_rng(seed)
    p = list(path)
    for _ in range(tries):
        if len(p) < 3:
            break
        i, j = sorted(rng.choice(len(p), 2, replace=False))
        if j - i > 1 and seg_free(p[i], p[j], obstacles):
            p = p[: i + 1] + p[j:]
    return p


def path_length(path):
    return float(sum(np.linalg.norm(b - a) for a, b in zip(path[:-1], path[1:])))


if __name__ == "__main__":
    obs = [(np.array([5.0, 5.0]), 2.0), (np.array([3.0, 7.5]), 1.2), (np.array([7.5, 3.0]), 1.2)]
    nodes, _, path = rrt([1, 1], np.array([9.0, 9.0]), obs, (np.zeros(2), np.full(2, 10.0)))
    short = shortcut(path, obs)
    print(f"nodes {len(nodes)}  raw length {path_length(path):.2f}  shortcut length {path_length(short):.2f}")
