# 레슨 07/02: 등속 모델 [위치, 속도] 와 위치 측정만 쓰는 선형 Kalman filter (gain 유도는 문서, 검증은 테스트)
import numpy as np

DT, SA, R_STD = 1.0, 0.1, 2.0  # step (s), accel noise std (m/s^2), position measurement noise std (m)
X0, P0 = np.array([0.0, 1.0]), np.diag([4.0, 1.0])  # prior mean and covariance of [position, velocity]


def model(dt=DT, sa=SA, r=R_STD):
    """x' = F x + G a with a ~ N(0, sa^2), so Q = sa^2 G G^T. Returns F, H, Q, R."""
    F = np.array([[1.0, dt], [0.0, 1.0]])
    G = np.array([[dt**2 / 2], [dt]])
    return F, np.array([[1.0, 0.0]]), sa**2 * G @ G.T, np.array([[r**2]])


def gain(P, H, R):
    """K = P H^T (H P H^T + R)^-1: the K that minimises the posterior variance."""
    return P @ H.T @ np.linalg.inv(H @ P @ H.T + R)


def simulate(steps, runs, rng, **kw):
    """Truth (steps, 2, runs) and noisy position readings (steps, runs); every run starts from a draw of the prior."""
    F, H, Q, R = model(**kw)
    dt, sa = kw.get("dt", DT), kw.get("sa", SA)
    G = sa * np.array([[dt**2 / 2], [dt]])  # how one accel sample enters [position, velocity]
    x = X0[:, None] + np.linalg.cholesky(P0) @ rng.standard_normal((2, runs))
    truth = [x]
    for _ in range(steps - 1):
        x = F @ x + G * rng.standard_normal((1, runs))
        truth.append(x)
    truth = np.array(truth)
    return truth, truth[:, 0] + np.sqrt(R[0, 0]) * rng.standard_normal((steps, runs))


def kalman(zs, **kw):
    """Run the filter over readings zs (steps, runs). Returns estimates (steps, 2, runs) and covariances (steps, 2, 2)."""
    F, H, Q, R = model(**kw)
    x, P = np.tile(X0[:, None], (1, zs.shape[1])), P0
    xs, Ps = [], []
    for k, z in enumerate(zs):
        if k:
            x, P = F @ x, F @ P @ F.T + Q  # predict
        K = gain(P, H, R)
        x = x + K @ (z[None, :] - H @ x)  # update
        P = (np.eye(2) - K @ H) @ P
        xs.append(x)
        Ps.append(P)
    return np.array(xs), np.array(Ps)


def covariances(steps, **kw):
    """P depends only on the model, not on the data, so it can be computed without any readings."""
    return kalman(np.zeros((steps, 1)), **kw)[1]


if __name__ == "__main__":
    truth, zs = simulate(60, 2000, np.random.default_rng(0))
    xs, Ps = kalman(zs)
    print("raw rmse", np.sqrt(np.mean((zs[10:] - truth[10:, 0]) ** 2)), "filter rmse", np.sqrt(np.mean((xs[10:, 0] - truth[10:, 0]) ** 2)))
    print("sqrt(P00) at the end", np.sqrt(Ps[-1, 0, 0]))
