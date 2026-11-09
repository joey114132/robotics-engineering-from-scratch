# 레슨 16/02: 점유 격자 위의 A*, 경로 단축, 오도메트리 오차가 있는 pure pursuit 주행, 두 landmark 자세 보정
import heapq
from itertools import product

import numpy as np
RES, N = 0.25, 40  # 10 m x 10 m room, 0.25 m cells; arrays are indexed [row = y, col = x]
LANDMARKS = np.array([(0.5, 9.5), (9.5, 0.5)])  # two beacons with a clear view of the whole room (walls do not block them)
rot = lambda th: np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
to_cell = lambda p: (int(p[1] / RES), int(p[0] / RES))
to_xy = lambda c: np.array([(c[1] + 0.5) * RES, (c[0] + 0.5) * RES])
line_free = lambda occ, a, b: not any(occ[to_cell(q)] for q in np.linspace(a, b, int(np.linalg.norm(np.subtract(b, a)) / (RES / 4)) + 2))
hits = lambda world, traj: any(world[to_cell(q)] for q in traj[:, :2])
def make_world():
    w = np.pad(np.zeros((N - 2, N - 2), bool), 1, constant_values=True)  # outer walls
    w[:28, 16:18], w[12:, 28:30] = True, True  # wall 1 has its gap at the top, wall 2 at the bottom
    return w

def inflate(w, r=0.4):  # grow obstacles by the robot radius so it can be planned as a point (lesson 09/03)
    k = int(np.ceil(r / RES))
    out, p = w.copy(), np.pad(w, k)
    for dr, dc in product(range(-k, k + 1), repeat=2):
        if dr * dr + dc * dc <= (r / RES) ** 2:
            out |= p[k + dr:k + dr + w.shape[0], k + dc:k + dc + w.shape[1]]
    return out

def astar(occ, s, g):  # 8-connected; a diagonal step may not squeeze between two blocked cells
    heap, best, parent = [(0.0, 0.0, s)], {s: 0.0}, {}
    while heap:
        _, gc, u = heapq.heappop(heap)
        if u == g:
            path = [u]
            while path[-1] in parent: path.append(parent[path[-1]])
            return path[::-1]
        for dr, dc in product((-1, 0, 1), repeat=2):
            v, c = (u[0] + dr, u[1] + dc), gc + np.hypot(dr, dc)
            if 0 <= v[0] < occ.shape[0] and 0 <= v[1] < occ.shape[1] and not occ[v] and c < best.get(v, 1e9) and not (dr and dc and (occ[u[0] + dr, u[1]] or occ[u[0], u[1] + dc])):
                best[v], parent[v] = c, u
                heapq.heappush(heap, (c + np.hypot(v[0] - g[0], v[1] - g[1]), c, v))

def plan(occ, start, goal):  # A* waypoints, then a greedy shortcut to the farthest point in view
    raw = [np.array(start, float)] + [to_xy(c) for c in astar(occ, to_cell(start), to_cell(goal))[1:-1]] + [np.array(goal, float)]
    out, i = [raw[0]], 0
    while i < len(raw) - 1:
        i = next(j for j in range(len(raw) - 1, i, -1) if j == i + 1 or line_free(occ, raw[i], raw[j]))
        out.append(raw[i])
    return raw, out

def sense(pose, L, rng, sigma):  # landmark positions in the robot frame plus Gaussian noise (m)
    return (L - pose[:2]) @ rot(pose[2]) + rng.normal(0, sigma, L.shape)

def pose_fix(L, body):  # heading from the direction between the landmarks, position from the first
    th = np.arctan2(*(L[1] - L[0])[::-1]) - np.arctan2(*(body[1] - body[0])[::-1])
    return np.array([*(L[0] - rot(th) @ body[0]), th])

def drive(path, start, scale_err=0.0, w_bias=0.0, sigma=0.0, landmarks=None, fix_every=1.0, v=0.6, ld=0.8, seed=0, dt=0.05, t_max=120.0):  # pure pursuit (lesson 08/04) steers from the estimate; the true robot moves as commanded
    rng, c = np.random.default_rng(seed), np.asarray(path, float)
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]
    p = np.c_[[np.interp(np.append(np.arange(0, arc[-1], 0.05), arc[-1]), arc, c[:, k]) for k in (0, 1)]].T
    true, est, T, E = np.array(start, float), np.array(start, float), [], []
    for k in range(int(t_max / dt)):
        i = np.linalg.norm(p - est[:2], axis=1).argmin()
        d = next((q for q in p[i:] if np.linalg.norm(q - est[:2]) >= ld), p[-1]) - est[:2]  # lookahead point
        w = np.clip(v * 2 * (-np.sin(est[2]) * d[0] + np.cos(est[2]) * d[1]) / (d @ d), -1.5, 1.5)  # arc through the lookahead point
        true = true + dt * np.array([v * np.cos(true[2]), v * np.sin(true[2]), w])
        vm, wm = v * (1 + scale_err) + rng.normal(0, sigma), w + w_bias + rng.normal(0, sigma)  # what the wheels report
        est = est + dt * np.array([vm * np.cos(est[2]), vm * np.sin(est[2]), wm])
        if landmarks is not None and k % round(fix_every / dt) == 0:
            est = pose_fix(landmarks, sense(true, landmarks, rng, 0.03))
        T.append(true), E.append(est)
        if np.linalg.norm(est[:2] - p[-1]) < 0.15:
            break
    return np.array(T), np.array(E)


if __name__ == "__main__":
    world, bad = make_world(), dict(scale_err=0.03, w_bias=0.03, sigma=0.02)
    sm = plan(inflate(world), (1.5, 1.5), (9.0, 8.5))[1]
    for name, kw in (("good odometry", dict(scale_err=0.002, w_bias=0.001, sigma=0.005)), ("bad odometry", bad), ("bad + fix", dict(bad, landmarks=LANDMARKS))):
        t = drive(sm, (1.5, 1.5, 0.0), **kw)[0]
        print(f"{name:14s} goal error {np.linalg.norm(t[-1, :2] - (9.0, 8.5)):.2f} m, wall hit: {hits(world, t)}")
