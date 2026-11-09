# 레슨 06/02: 평면 타깃 homography(DLT)에서 선형 대수만으로 fx, fy, cx, cy 를 복원한다 (Zhang 방식, skew 0)
import numpy as np


def rodrigues(w):
    th = np.linalg.norm(w)
    if th < 1e-12:
        return np.eye(3)
    k = w / th
    Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * Kx + (1 - np.cos(th)) * Kx @ Kx


def make_views(K, n=6, noise=0.0, seed=0, tilt=0.5):
    """n views of a 7x5 planar grid (0.06 m pitch, Z=0). Returns [(XY, uv)] with pixel noise sigma `noise`."""
    rng = np.random.default_rng(seed)
    Km = np.array([[K["fx"], 0, K["cx"]], [0, K["fy"], K["cy"]], [0, 0, 1.0]])
    XY = np.array([(0.06 * i, 0.06 * j) for i in range(-3, 4) for j in range(-2, 3)])
    out = []
    for _ in range(n):
        R = rodrigues(rng.uniform(-tilt, tilt, 3))
        t = np.array([*rng.uniform(-0.05, 0.05, 2), rng.uniform(0.5, 0.9)])
        p = Km @ (R[:, :2] @ XY.T + t[:, None])
        out.append((XY, (p[:2] / p[2]).T + rng.normal(0, noise, (len(XY), 2))))
    return out


def _normalise(P):
    c = P.mean(0)
    s = np.sqrt(2) / np.mean(np.linalg.norm(P - c, axis=1))
    return np.array([[s, 0, -s * c[0]], [0, s, -s * c[1]], [0, 0, 1.0]])


def homography_dlt(XY, uv):
    """H with uv ~ H [X, Y, 1]: stack two rows per point, take the smallest singular vector."""
    Tx, Tu = _normalise(XY), _normalise(uv)
    a = (Tx @ np.vstack([XY.T, np.ones(len(XY))]))[:2].T
    b = (Tu @ np.vstack([uv.T, np.ones(len(uv))]))[:2].T
    A = []
    for (X, Y), (u, v) in zip(a, b):
        A += [[-X, -Y, -1, 0, 0, 0, u * X, u * Y, u], [0, 0, 0, -X, -Y, -1, v * X, v * Y, v]]
    H = np.linalg.svd(np.array(A))[2][-1].reshape(3, 3)
    H = np.linalg.inv(Tu) @ H @ Tx
    return H / np.linalg.norm(H)


def _v(H, i, j):
    h, g = H[:, i], H[:, j]
    return np.array([h[0] * g[0], h[1] * g[1], h[2] * g[0] + h[0] * g[2], h[2] * g[1] + h[1] * g[2], h[2] * g[2]])


def calibrate(Hs):
    """B = K^-T K^-1 is symmetric. Each view gives h1'B h2 = 0 and h1'B h1 = h2'B h2, linear in [B11,B22,B13,B23,B33]."""
    A = np.array([r for H in Hs for r in (_v(H, 0, 1), _v(H, 0, 0) - _v(H, 1, 1))])
    _, s, Vt = np.linalg.svd(A)
    if s[-2] < 1e-6 * s[0]:
        raise ValueError("degenerate views: need at least 2 distinct plane orientations")
    b = Vt[-1] * np.sign(Vt[-1][0])
    B11, B22, B13, B23, B33 = b
    cx, cy = -B13 / B11, -B23 / B22
    lam = B33 - B13 ** 2 / B11 - B23 ** 2 / B22
    if min(B11, B22, lam) <= 0:
        raise ValueError("ill-posed: noise too large for the number of views")
    return dict(fx=np.sqrt(lam / B11), fy=np.sqrt(lam / B22), cx=cx, cy=cy)


def pixel_error(est, true, seed=0, n=200):
    """RMS pixel distance between projections of the same random 3D points under the two intrinsics."""
    P = np.random.default_rng(seed).uniform([-0.3, -0.2, 0.5], [0.3, 0.2, 1.5], (n, 3))
    f = lambda k: np.stack([k["fx"] * P[:, 0] / P[:, 2] + k["cx"], k["fy"] * P[:, 1] / P[:, 2] + k["cy"]], 1)
    return float(np.sqrt(np.mean(np.sum((f(est) - f(true)) ** 2, axis=1))))


if __name__ == "__main__":
    K = dict(fx=620.0, fy=580.0, cx=330.0, cy=235.0)
    est = calibrate([homography_dlt(xy, uv) for xy, uv in make_views(K, 6, 0.5, 1)])
    print({k: round(float(v), 1) for k, v in est.items()}, "pixel error", round(pixel_error(est, K), 2))
