# 레슨 06/03: depth 이미지를 점군으로 바꾸고 voxel 다운샘플, 최소제곱 평면, RANSAC 평면으로 바닥을 찾는다
import numpy as np

TABLE_N = np.array([0.0, 0.5, np.sqrt(0.75)])  # unit normal of the table; the plane is n . X = 1 m


def make_scene(seed=0, box=True, noise=0.003, flyers=0.02, K=(150.0, 150.0, 80.0, 60.0), shape=(120, 160)):
    """Depth image of a tilted table with a box on it, Gaussian depth noise and random flyer pixels.
    Returns (depth, true plane normal)."""
    rng = np.random.default_rng(seed)
    fx, fy, cx, cy = K
    v, u = np.mgrid[0:shape[0], 0:shape[1]]
    ray = np.stack([(u - cx) / fx, (v - cy) / fy, np.ones(shape)], axis=-1)
    z = 1.0 / (ray @ TABLE_N)
    if box:
        z[40:80, 60:110] -= 0.2  # box top: 0.2 m nearer to the camera than the table behind it
    z = z + rng.normal(0, noise, shape)
    bad = rng.random(shape) < flyers
    z[bad] = rng.uniform(0.3, 3.0, bad.sum())
    return z, TABLE_N


def depth_to_points(depth, fx, fy, cx, cy) -> np.ndarray:
    """Every valid pixel (finite, z > 0) becomes a 3D point in the camera frame."""
    v, u = np.nonzero(np.isfinite(depth) & (depth > 0))
    z = depth[v, u]
    return np.stack([(u - cx) * z / fx, (v - cy) * z / fy, z], axis=1)


def voxel_downsample(P, size) -> np.ndarray:
    """One averaged point per occupied voxel of edge `size`."""
    key = np.floor(P / size).astype(np.int64)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    out = np.zeros((len(cnt), 3))
    np.add.at(out, inv.reshape(-1), P)
    return out / cnt[:, None]


def fit_plane(P):
    """Least squares plane n . X = d, n unit, d >= 0: the smallest singular vector of the centred points."""
    c = P.mean(0)
    n = np.linalg.svd(P - c, full_matrices=False)[2][-1]
    d = float(n @ c)
    return (n, d) if d >= 0 else (-n, -d)


def ransac_iters(inlier_frac, p_success=0.99, k=3) -> int:
    """Samples needed so that with probability p_success at least one has k inliers: log(1-p)/log(1-w^k)."""
    return int(np.ceil(np.log(1 - p_success) / np.log(1 - inlier_frac ** k)))


def ransac_plane(P, thr, iters, seed=0):
    """Fit planes to random point triples, keep the one with most points within `thr`, refit on those inliers."""
    if len(P) < 3:
        raise ValueError("need at least 3 points")
    rng, best = np.random.default_rng(seed), None
    for _ in range(iters):
        a, b, c = P[rng.choice(len(P), 3, replace=False)]
        n = np.cross(b - a, c - a)
        if np.linalg.norm(n) < 1e-9:  # collinear sample
            continue
        n = n / np.linalg.norm(n)
        inl = np.abs((P - a) @ n) < thr
        if best is None or inl.sum() > best.sum():
            best = inl
    if best is None:
        raise ValueError("no valid plane sample found")
    n, d = fit_plane(P[best])
    return n, d, np.abs(P @ n - d) < thr


if __name__ == "__main__":
    depth, truth = make_scene(1)
    P = depth_to_points(depth, 150.0, 150.0, 80.0, 60.0)
    deg = lambda n: np.degrees(np.arccos(abs(n @ truth)))
    print(len(P), "points; least squares off by", round(deg(fit_plane(P)[0]), 1), "deg; RANSAC off by",
          round(deg(ransac_plane(P, 0.012, 150)[0]), 2), "deg")
