# 레슨 09/04: waypoint 경로를 부드러움 비용 + 장애물 penalty 의 gradient descent 로 다듬는다 (CHOMP 식 아이디어, 축소판)
import numpy as np


def cost(X, obstacles, ws=1.0, wo=8.0, margin=0.4):
    """Total, smoothness and obstacle cost. Penalty = wo * (r + margin - distance)^2 inside the margin, interior points only."""
    smooth = 0.5 * ws * float(np.sum(np.diff(X, axis=0) ** 2))
    pen = 0.0
    for c, r in obstacles:
        d = np.linalg.norm(X[1:-1] - c, axis=1)
        pen += wo * float(np.sum(np.maximum(0.0, r + margin - d) ** 2))
    return smooth + pen, smooth, pen


def grad(X, obstacles, ws=1.0, wo=8.0, margin=0.4):
    """Analytic gradient, zero on the two fixed endpoints."""
    g = np.zeros_like(X)
    g[1:-1] = ws * (2 * X[1:-1] - X[:-2] - X[2:])
    for c, r in obstacles:
        v = X[1:-1] - c
        d = np.linalg.norm(v, axis=1, keepdims=True)
        g[1:-1] -= 2 * wo * np.maximum(0.0, r + margin - d) * v / np.maximum(d, 1e-9)
    return g


def optimise(X0, obstacles, iters=1000, lr=0.04, **w):
    """Plain gradient descent. Returns the final path and the total cost after every iteration."""
    X, hist = np.array(X0, float), []
    for _ in range(iters):
        X -= lr * grad(X, obstacles, **w)
        hist.append(cost(X, obstacles, **w)[0])
    return X, np.array(hist)


if __name__ == "__main__":
    obs = [(np.array([3.5, 0.3]), 1.0), (np.array([7.0, -0.5]), 1.0)]
    X0 = np.linspace([0.0, 0.0], [10.0, 0.0], 22)
    X, h = optimise(X0, obs, iters=4000)
    print(f"cost {cost(X0, obs)[0]:.2f} -> {h[-1]:.2f}, closest approach {min(np.linalg.norm(x - c) - r for x in X for c, r in obs):.3f} m outside")
