# 레슨 07/05: 유니사이클 운동 모델과 range-bearing 랜드마크 측정을 쓰는 EKF (해석적 Jacobian)
import numpy as np

DT, SV, SW = 0.1, 0.05, 0.03             # step (s), control noise std: speed (m/s), turn rate (rad/s)
R = np.diag([0.2**2, 0.03**2])           # range (m) and bearing (rad) noise
P0 = np.diag([0.3**2, 0.3**2, 0.1**2])   # what the filter believes about its start
LMS = np.array([[4.0, 1.0], [0.0, 5.5], [-4.0, 1.0], [0.0, -2.0]])
U = np.array([1.0, 0.3])                 # commanded speed and turn rate: a circle of radius 3.3 m


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def f(x, u, dt=DT):
    return np.array([x[0] + u[0] * dt * np.cos(x[2]), x[1] + u[0] * dt * np.sin(x[2]), wrap(x[2] + u[1] * dt)])


def jac_f(x, u, dt=DT):
    return np.array([[1, 0, -u[0] * dt * np.sin(x[2])], [0, 1, u[0] * dt * np.cos(x[2])], [0, 0, 1.0]])


def h(x, lm):
    d = lm - x[:2]
    return np.array([np.hypot(*d), wrap(np.arctan2(d[1], d[0]) - x[2])])


def jac_h(x, lm):
    dx, dy = lm - x[:2]
    q = dx * dx + dy * dy
    r = np.sqrt(q)
    return np.array([[-dx / r, -dy / r, 0.0], [dy / q, -dx / q, -1.0]])


def predict(x, P, u, dt=DT):
    G = np.array([[dt * np.cos(x[2]), 0], [dt * np.sin(x[2]), 0], [0, dt]])  # how control noise enters
    F = jac_f(x, u, dt)
    return f(x, u, dt), F @ P @ F.T + G @ np.diag([SV**2, SW**2]) @ G.T


def update(x, P, z, lm, R=R):
    H = jac_h(x, lm)                                    # linearised at the current estimate
    K = P @ H.T @ np.linalg.inv(H @ P @ H.T + R)
    y = z - h(x, lm)
    y[1] = wrap(y[1])                                   # an angle difference must wrap
    I_KH = np.eye(3) - K @ H
    return x + K @ y, I_KH @ P @ I_KH.T + K @ R @ K.T   # Joseph form keeps P symmetric


def run(rng, steps=80, heading_offset=0.0, lms=LMS, max_range=8.0):
    """Truth, estimate, dead reckoning and covariances. The filter starts at the origin with P0."""
    x_est = np.zeros(3)
    x = x_est + np.linalg.cholesky(P0) @ rng.standard_normal(3) + [0, 0, heading_offset]
    est, P, dr = x_est.copy(), P0, x_est.copy()
    out = [(x, est, dr, P)]
    for _ in range(steps):
        x = f(x, U + [SV, SW] * rng.standard_normal(2))
        dr = f(dr, U)
        est, P = predict(est, P, U)
        for lm in lms:
            z = h(x, lm)
            if z[0] < max_range:
                z = z + np.sqrt(np.diag(R)) * rng.standard_normal(2)
                est, P = update(est, P, z, lm)
        out.append((x, est, dr, P))
    t, e, d, Ps = zip(*out)
    return np.array(t), np.array(e), np.array(d), np.array(Ps)


def mean_nees(seeds, heading_offset=0.0, steps=60, lms=LMS):
    """Average of e^T P^-1 e over seeds and time. A consistent filter gives the state dimension, 3."""
    vals = []
    for s in range(seeds):
        t, e, _, Ps = run(np.random.default_rng(s), steps, heading_offset, lms)
        err = e - t
        err[:, 2] = wrap(err[:, 2])
        vals += [er @ np.linalg.solve(P, er) for er, P in zip(err[10:], Ps[10:])]
    return float(np.mean(vals))


if __name__ == "__main__":
    for n in (1, 4):
        for off in (0.0, 0.6, 1.5):
            print(f"{n} landmark(s), heading offset {off} rad: mean NEES {mean_nees(30, off, lms=LMS[:n]):.1f}")
