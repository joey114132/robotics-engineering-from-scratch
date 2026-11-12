# 레슨 03/08: 이중 적분기의 MPC. 예측 행렬로 비용을 U 의 이차식으로 만들고 투영 경사법(FISTA)으로 입력 한계 안에서 푼다
import numpy as np


def double_integrator(dt):
    return np.array([[1.0, dt], [0.0, 1.0]]), np.array([[dt * dt / 2], [dt]])


def riccati(A, B, Q, R, iters=3000):
    """Infinite-horizon LQR (lesson 06): K and P. P is used as the terminal cost so a short plan still sees the tail."""
    P = Q.copy()
    for _ in range(iters):
        K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
        P = Q + A.T @ P @ (A - B @ K)
    return np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A), P


def prediction(A, B, N):
    """Stacked states X = [x1..xN] = Phi x0 + Gam U for inputs U = [u0..u(N-1)]."""
    n = A.shape[0]
    Phi = np.vstack([np.linalg.matrix_power(A, i + 1) for i in range(N)])
    Gam = np.zeros((n * N, N))
    for i in range(N):
        for j in range(i + 1):
            Gam[n * i:n * i + n, j:j + 1] = np.linalg.matrix_power(A, i - j) @ B
    return Phi, Gam


def plan(x0, A, B, Q, R, Pf, N, umax, iters=800):
    """min over |u| <= umax of sum x'Qx + u'Ru + xN'Pf xN, by accelerated projected gradient. Returns the input plan."""
    Phi, Gam = prediction(A, B, N)
    Qb = np.kron(np.eye(N), Q)
    Qb[-2:, -2:] = Pf
    H = Gam.T @ Qb @ Gam + np.kron(np.eye(N), R)
    f = Gam.T @ Qb @ Phi @ x0
    step = 1.0 / np.linalg.eigvalsh(H).max()
    U = Y = np.zeros(N)
    t = 1.0
    for _ in range(iters):
        U_new = np.clip(Y - step * (H @ Y + f), -umax, umax)
        t_new = (1 + np.sqrt(1 + 4 * t * t)) / 2
        Y = U_new + (t - 1) / t_new * (U_new - U)
        U, t = U_new, t_new
    return U


def simulate(x0, steps, A, B, Q, R, N, umax, plan_log=None):
    """Receding horizon: plan N steps, apply the first, plan again. Returns states, inputs, total cost."""
    _, Pf = riccati(A, B, Q, R)
    x, xs, us, cost = np.array(x0, float), [], [], 0.0
    for _ in range(steps):
        U = plan(x, A, B, Q, R, Pf, N, umax)
        if plan_log is not None:
            plan_log.append((x.copy(), U.copy()))
        u = U[0]
        xs.append(x), us.append(u)
        cost += float(x @ Q @ x + R[0, 0] * u * u)
        x = A @ x + B[:, 0] * u
    return np.array(xs), np.array(us), cost


if __name__ == "__main__":
    A, B = double_integrator(0.1)
    Q, R = np.diag([1.0, 0.1]), np.array([[0.1]])
    print(simulate([4.0, 0.0], 60, A, B, Q, R, 15, 1.0)[2])
