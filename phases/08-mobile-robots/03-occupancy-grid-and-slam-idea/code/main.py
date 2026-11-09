# 레슨 08/03: range scan 으로 log-odds occupancy grid 를 만들고, 자세 오차가 지도를 번지게 하는 것을 보인다
import numpy as np

RES, N = 0.25, 40  # cell size (m), cells per side: a 10 m x 10 m room
L_OCC, L_FREE, L_MAX = 0.85, 0.4, 5.0


def make_world():
    w = np.zeros((N, N), bool)
    w[0, :] = w[-1, :] = w[:, 0] = w[:, -1] = True  # walls
    w[16:24, 16:24] = True  # a box in the middle (row = y, column = x)
    return w


def cell(p):
    return np.clip((np.asarray(p) / RES).astype(int), 0, N - 1)


def scan(world, pose, angles, max_range=8.0, sigma=0.0, rng=None):
    """Ray march: range to the first occupied cell along each beam, max_range if none."""
    t = np.arange(0.0, max_range, RES / 4)
    a = pose[2] + angles
    pts = pose[:2] + t[None, :, None] * np.stack([np.cos(a), np.sin(a)], 1)[:, None, :]
    c = cell(pts)
    hit = world[c[..., 1], c[..., 0]] | (pts < 0).any(-1) | (pts >= N * RES).any(-1)
    r = np.where(hit.any(1), t[hit.argmax(1)], max_range)
    return r + (rng.normal(0, sigma, len(r)) if sigma else 0.0)


def update(L, pose, r, angles, max_range=8.0):
    """Log-odds update: cells a beam crossed get less occupied, the cell it ended in gets more."""
    a = pose[2] + angles
    d = np.stack([np.cos(a), np.sin(a)], 1)
    t = np.arange(0.0, max_range, RES / 2)
    free = t[None, :] < (r - RES / 2)[:, None]
    fc = cell(pose[:2] + t[None, :, None] * d[:, None, :])[free]
    oc = cell(pose[:2] + (r * (r < max_range - 1e-6))[:, None] * d)[r < max_range - 1e-6]
    fi, oi = np.unique(fc[:, 1] * N + fc[:, 0]), np.unique(oc[:, 1] * N + oc[:, 0])
    L = L.copy().ravel()
    L[np.setdiff1d(fi, oi)] -= L_FREE
    L[oi] += L_OCC
    return np.clip(L, -L_MAX, L_MAX).reshape(N, N)


def prob(L):
    return 1.0 - 1.0 / (1.0 + np.exp(L))


def loop_poses(k=200, centre=(5.0, 5.0), radius=3.0):
    s = np.linspace(0, 2 * np.pi, k, endpoint=False)
    return np.column_stack([centre[0] + radius * np.cos(s), centre[1] + radius * np.sin(s), s + np.pi / 2])


def drift(poses, yaw_err):
    """Dead-reckoned poses when the heading estimate gains yaw_err rad per step. Step lengths stay exact."""
    k = np.arange(len(poses))
    d = np.diff(poses[:, :2], axis=0)
    way = np.arctan2(d[:, 1], d[:, 0]) + yaw_err * k[1:]  # direction of each step, rotated by the drift so far
    xy = poses[0, :2] + np.cumsum(np.linalg.norm(d, axis=1)[:, None] * np.column_stack([np.cos(way), np.sin(way)]), axis=0)
    return np.column_stack([np.vstack([poses[0, :2], xy]), poses[:, 2] + yaw_err * k])


def build_map(world, true_poses, est_poses, sigma=0.03, seed=0):
    rng, ang = np.random.default_rng(seed), np.linspace(-np.pi, np.pi, 180, endpoint=False)
    L = np.zeros((N, N))
    for tp, ep in zip(true_poses, est_poses):
        L = update(L, ep, scan(world, tp, ang, sigma=sigma, rng=rng), ang)
    return L


def precision(L, world):  # share of cells called occupied that really are occupied
    occ = L > 0
    return float((occ & world).sum() / max(occ.sum(), 1))


if __name__ == "__main__":
    w, tp = make_world(), loop_poses()
    for e in (0.0, 0.001, 0.003):
        L = build_map(w, tp, drift(tp, e) if e else tp)
        print(f"yaw drift {e:.3f} rad/step: occupied cells {(L > 0).sum():4d}, precision {precision(L, w):.2f}")
