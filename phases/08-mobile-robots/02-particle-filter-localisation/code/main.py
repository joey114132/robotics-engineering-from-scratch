# 레슨 08/02: 알려진 landmark 와 거리 측정으로 2D 자세를 추정하는 particle filter (예측, 가중, resampling)
import numpy as np

LANDMARKS = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]])


def move(P, v, w, dt, rng=None, sv=0.0, sw=0.0):
    """Unicycle step for poses P (N, 3). Noise on v and w makes the particles spread."""
    n = len(P)
    v = v + (rng.normal(0, sv, n) if rng else 0.0)
    w = w + (rng.normal(0, sw, n) if rng else 0.0)
    th = P[:, 2] + w * dt / 2
    return np.column_stack([P[:, 0] + v * dt * np.cos(th), P[:, 1] + v * dt * np.sin(th), P[:, 2] + w * dt])


def ranges(P, lm=LANDMARKS):
    return np.linalg.norm(P[:, None, :2] - lm[None], axis=2)  # (N, landmarks)


def log_weights(P, z, sigma, lm=LANDMARKS):
    """Gaussian log-likelihood of the measured ranges z for every particle."""
    return -0.5 * (((ranges(P, lm) - z) / sigma) ** 2).sum(axis=1)


def systematic_resample(w, rng):
    """One random offset, N evenly spaced pointers into the cumulative weights."""
    n = len(w)
    idx = np.searchsorted(np.cumsum(w), (rng.random() + np.arange(n)) / n)
    return np.minimum(idx, n - 1)


def n_eff(w):
    return 1.0 / np.sum(w ** 2)


def pf_step(P, v, w, dt, z, sigma, rng, sv=0.4, sw=1.0, inject=0.0, box=(0, 10)):
    P = move(P, v, w, dt, rng, sv, sw)
    lw = log_weights(P, z, sigma)
    wt = np.exp(lw - lw.max())  # subtract the max so far-away particles cannot underflow every weight to 0
    P = P[systematic_resample(wt / wt.sum(), rng)]
    k = int(inject * len(P))
    if k:  # a few random particles keep the filter able to find a robot that jumped
        P[:k] = np.column_stack([rng.uniform(*box, (k, 2)), rng.uniform(-np.pi, np.pi, k)])
    return P


def estimate(P):
    return np.array([P[:, 0].mean(), P[:, 1].mean(), np.arctan2(np.sin(P[:, 2]).mean(), np.cos(P[:, 2]).mean())])


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    truth = np.array([[2.0, 3.0, 0.3]])
    P = np.column_stack([rng.uniform(0, 10, (500, 2)), rng.uniform(-np.pi, np.pi, 500)])
    for t in range(40):
        truth = move(truth, 0.8, 0.15, 0.1)
        z = ranges(truth)[0] + rng.normal(0, 0.3, 4)
        P = pf_step(P, 0.8, 0.15, 0.1, z, 0.3, rng)
    print("error (m):", np.linalg.norm(estimate(P)[:2] - truth[0, :2]))
