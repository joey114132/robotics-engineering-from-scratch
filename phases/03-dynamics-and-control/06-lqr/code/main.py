# 레슨 03/06: 이산 이중 적분기의 Riccati 반복으로 LQR 게인 K 를 구하고 폐루프를 굴려 비용을 잰다
import numpy as np


def double_integrator(dt):
    """x = (position, velocity), u = acceleration held for dt."""
    return np.array([[1.0, dt], [0.0, 1.0]]), np.array([[dt * dt / 2], [dt]])


def dare(A, B, Q, R, tol=1e-12, max_iter=100000):
    """Backward Riccati recursion until P stops changing. Returns K (u = -K x) and the cost matrix P."""
    P = Q.copy()
    for _ in range(max_iter):
        K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
        P_new = Q + A.T @ P @ (A - B @ K)
        done = np.abs(P_new - P).max() < tol
        P = P_new
        if done:
            break
    return np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A), P


def rollout(A, B, K, x0, n, Q, R, umax=np.inf):
    """Run u = -K x (optionally clipped). Returns states, inputs, and total cost sum(x'Qx + u'Ru)."""
    x, xs, us, cost = np.array(x0, float), [], [], 0.0
    for _ in range(n):
        u = np.clip(-K @ x, -umax, umax)
        xs.append(x), us.append(u)
        cost += float(x @ Q @ x + u @ R @ u)
        x = A @ x + B @ u
    return np.array(xs), np.array(us), cost


if __name__ == "__main__":
    A, B = double_integrator(0.05)
    for r in (0.01, 1.0):
        K, _ = dare(A, B, np.diag([1.0, 0.1]), np.array([[r]]))
        print(r, K)
