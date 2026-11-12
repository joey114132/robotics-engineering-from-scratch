# 레슨 08/06: SE(2) pose graph 와 루프 폐쇄 간선, 수치 Jacobian Gauss-Newton 으로 표류한 궤적을 되감기
import numpy as np


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def compose(a, d):
    """Pose a, then move d = (dx, dy, dth) expressed in a's own frame."""
    c, s = np.cos(a[2]), np.sin(a[2])
    return np.array([a[0] + c * d[0] - s * d[1], a[1] + s * d[0] + c * d[1], wrap(a[2] + d[2])])


def between(a, b):
    """Pose b expressed in a's frame: the quantity an odometry or loop-closure edge measures."""
    c, s = np.cos(a[2]), np.sin(a[2])
    dx, dy = b[:2] - a[:2]
    return np.array([c * dx + s * dy, -s * dx + c * dy, wrap(b[2] - a[2])])


def world(rng, side=5, bias=0.02, odom_std=(0.02, 0.02, 0.01)):
    """Truth for a square loop (21 poses, the last equals the first), edges (i, j, z, weight), drifted initial poses."""
    n = 4 * side
    steps = [np.array([1.0, 0.0, np.pi / 2 if (k + 1) % side == 0 else 0.0]) for k in range(n)]
    truth = [np.zeros(3)]
    for d in steps:
        truth.append(compose(truth[-1], d))
    w_odom, w_loop = 1 / np.array([0.05, 0.05, 0.02]), 1 / np.array([0.05, 0.05, 0.02])
    zs = [d + rng.normal(0, odom_std) + [0, 0, bias] for d in steps]  # a small heading bias every step
    X0 = [np.zeros(3)]
    for z in zs:
        X0.append(compose(X0[-1], z))
    edges = [(k, k + 1, z, w_odom) for k, z in enumerate(zs)]
    edges.append((0, n, between(truth[0], truth[n]) + rng.normal(0, odom_std), w_loop))  # the loop closure
    return np.array(truth), edges, np.array(X0)


def residuals(X, edges):
    out = []
    for i, j, z, w in edges:
        e = between(X[i], X[j]) - z
        e[2] = wrap(e[2])
        out.append(w * e)
    return np.concatenate(out)


def jacobian(X, edges, free, eps=1e-6):
    """Numeric Jacobian of the residuals with respect to the free poses only."""
    cols = []
    for p in free:
        for c in range(3):
            Xp, Xm = X.copy(), X.copy()
            Xp[p, c] += eps
            Xm[p, c] -= eps
            cols.append((residuals(Xp, edges) - residuals(Xm, edges)) / (2 * eps))
    return np.array(cols).T


def solve(X0, edges, iters=15):
    """Gauss-Newton with pose 0 held fixed (the gauge). Returns poses and the cost after every iteration, first entry = start."""
    X, free = X0.copy(), range(1, len(X0))
    costs = [float(residuals(X, edges) @ residuals(X, edges))]
    for _ in range(iters):
        J, r = jacobian(X, edges, free), residuals(X, edges)
        dx = np.linalg.lstsq(J, -r, rcond=None)[0].reshape(-1, 3)
        X[1:] += dx
        X[:, 2] = wrap(X[:, 2])
        costs.append(float(residuals(X, edges) @ residuals(X, edges)))
    return X, np.array(costs)


def ate(X, truth):
    """Root-mean-square position error against the truth."""
    return float(np.sqrt(((X[:, :2] - truth[:, :2]) ** 2).sum(1).mean()))


if __name__ == "__main__":
    truth, edges, X0 = world(np.random.default_rng(0))
    X, costs = solve(X0, edges)
    print(f"end of odometry {np.linalg.norm(X0[-1, :2]):.2f} m from the start, rms error {ate(X0, truth):.2f} -> {ate(X, truth):.2f} m")
