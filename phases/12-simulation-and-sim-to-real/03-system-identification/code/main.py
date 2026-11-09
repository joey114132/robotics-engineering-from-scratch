# 레슨 12/03: 기록된 관절 궤적에서 J, b, c, Tm 을 구간 적분 최소제곱과 Tm 격자 탐색으로 맞춘다
import math
import numpy as np

TRUE = dict(J=0.05, b=0.02, c=0.05, Tm=0.03)  # the lesson 12/01 joint; gravity K = m*g*l is known from the model
K, EPS, DT, KV = 0.2, 0.01, 1e-3, 3.0  # gravity (Nm), Coulomb smoothing (rad/s), step (s), speed-loop gain (Nm s/rad)


def run(p, ctrl, T, x0) -> np.ndarray:
    """midpoint rows (t, u, q, w) every DT. ctrl(t, q, w) gives the motor command u."""
    f = lambda x, u: np.array([x[1], (x[2] - p["b"] * x[1] - p["c"] * math.tanh(x[1] / EPS) - K * math.sin(x[0])) / p["J"], (u - x[2]) / p["Tm"]])
    x, rows = np.array(x0, float), []
    for i in range(round(T / DT)):
        u = ctrl(i * DT, x[0], x[1])
        rows.append((i * DT, u, x[0], x[1]))
        x = x + DT * f(x + 0.5 * DT * f(x, u), u)  # midpoint step
    return np.array(rows)


def experiment(a, v0=0.3, T=20.0, p=TRUE) -> np.ndarray:
    """Speed loop around v0 plus a multisine of size a (rad/s). a = 0 is one slow constant-speed run."""
    ref = lambda t: v0 + a * (1.5 * math.sin(0.8 * math.pi * t) + math.sin(2.6 * math.pi * t) + 0.5 * math.sin(6.2 * math.pi * t))
    return run(p, lambda t, q, w: KV * (ref(t) - w) + K * math.sin(q), T, (0.0, v0, p["b"] * v0 + p["c"]))


def record(rows, sw, sq, seed, step=2) -> np.ndarray:
    """Subsample to 500 Hz, add Gaussian noise: sw on speed (rad/s), sq on angle (rad)."""
    d, r = rows[::step].copy(), np.random.default_rng(seed)
    d[:, 3] += r.normal(0, sw, len(d))
    d[:, 2] += r.normal(0, sq, len(d))
    return d


def lag(u, dt, Tm) -> np.ndarray:
    """Motor torque from command u through a first-order lag, from rest (FIR form)."""
    if Tm <= 0:
        return u.copy()
    a = math.exp(-dt / Tm)
    h = np.concatenate([[0.0], (1 - a) * a ** np.arange(int(12 * Tm / dt) + 1)])
    return np.convolve(u, h)[: len(u)]


def design(d, Tm, n=25):
    """Over windows of n samples: dw = (1/J) int(tm - K sin q) - (b/J) int(w) - (c/J) int(tanh(w/EPS)). Returns X, y."""
    t, u, q, w = d.T
    dt = t[1] - t[0]
    cum = lambda y: np.concatenate([[0.0], np.cumsum(0.5 * (y[1:] + y[:-1]) * dt)])
    ig, iw, isg = cum(lag(u, dt, Tm) - K * np.sin(q)), cum(w), cum(np.tanh(w / EPS))
    i = np.arange(0, len(t) - n, n)
    return np.stack([ig[i + n] - ig[i], -(iw[i + n] - iw[i]), -(isg[i + n] - isg[i])], 1), w[i + n] - w[i]


def fit(d, grid=np.linspace(0, 0.1, 51)):
    """Least squares for J, b, c inside a grid search over Tm. Returns (estimate, condition number, residual)."""
    fits = []
    for Tm in grid:
        X, y = design(d, Tm)
        th = np.linalg.lstsq(X, y, rcond=None)[0]
        fits.append((float(np.sum((y - X @ th) ** 2)), Tm, th, np.linalg.cond(X / np.linalg.norm(X, axis=0))))
    res, Tm, th, cond = min(fits, key=lambda z: z[0])
    return dict(J=1 / th[0], b=th[1] / th[0], c=th[2] / th[0], Tm=Tm), cond, res


def predict(est, d):
    """Measured and model-predicted speed change per window, with the fitted parameters."""
    X, y = design(d, est["Tm"])
    return y, X @ np.array([1 / est["J"], est["b"] / est["J"], est["c"] / est["J"]])


def excitation_error(a, sw, sq, seeds) -> dict:
    """Mean relative error of J, b, c over noise seeds for excitation size a."""
    rows = experiment(a)
    ests = [fit(record(rows, sw, sq, s))[0] for s in range(seeds)]
    return {k: float(np.mean([abs(e[k] - TRUE[k]) / TRUE[k] for e in ests])) for k in ("J", "b", "c")}


if __name__ == "__main__":
    for a in (0.0, 1.0):
        est, cond, _ = fit(record(experiment(a), 0.01, 1e-4, 0))
        print(f"a={a}: cond {cond:.0f}", {k: round(v, 4) for k, v in est.items()}, "true", TRUE)
