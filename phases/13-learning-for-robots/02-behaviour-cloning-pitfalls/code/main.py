# 레슨 13/02: 노이즈 아래의 행동 복제 드리프트와 DAgger 식 재라벨링으로 복구하는 최소 구현
import numpy as np

GOAL, OBST, R_OBST, DT, NOISE = np.array([1.0, 0.0]), np.zeros(2), 0.3, 0.05, 0.8


def expert(x):
    d = GOAL - x
    a = d / (np.linalg.norm(d) + 1e-9)
    o = x - OBST
    r = np.linalg.norm(o) + 1e-9
    if r < R_OBST + 0.35:
        side = 1.0 if o[0] * d[1] - o[1] * d[0] >= 0 else -1.0
        w = 2.5 * (1 - (r - R_OBST) / 0.35)
        a = a + w * side * np.array([-o[1], o[0]]) / r + w * 0.6 * o / r
    return a / max(1.0, np.linalg.norm(a))


def rollout(policy, x0, rng, noise=NOISE, T=120):
    """Execution noise is added to the commanded velocity, so the learner is pushed off the demo states."""
    xs = [np.array(x0, float)]
    for _ in range(T):
        xs.append(xs[-1] + DT * (np.clip(policy(xs[-1]), -1, 1) + noise * rng.standard_normal(2)))
    return np.array(xs)


def starts(rng, n):
    return np.column_stack([rng.uniform(-1.5, -0.8, n), rng.uniform(-0.8, 0.8, n)])


def fit_knn(X, A, k=3):
    return lambda x: A[np.argsort(((X - x) ** 2).sum(1))[:k]].mean(0)


def collect(rng, n):
    xs = [rollout(expert, x0, rng, noise=0.0)[:-1] for x0 in starts(rng, n)]
    X = np.vstack(xs)
    return X, np.array([expert(x) for x in X])


def dagger(rng, n_demos, rounds, per_round=5, labels=False):
    """Round 0 is plain cloning. Each later round rolls the learner out, asks the expert to label the visited states, refits."""
    X, A = collect(rng, n_demos)
    pol = fit_knn(X, A)
    for _ in range(rounds):
        V = np.vstack([rollout(pol, x0, rng)[:-1] for x0 in starts(rng, per_round)])
        X, A = np.vstack([X, V]), np.vstack([A, [expert(x) for x in V]])
        pol = fit_knn(X, A)
    return pol, ((X, A) if labels else X)


def drift_curves(pol, X, rng, n=40):
    """Per time step: action error vs the expert, distance to the nearest data state, and success of each rollout."""
    paths = [rollout(pol, x0, rng)[:-1] for x0 in starts(rng, n)]
    err = np.mean([[np.linalg.norm(pol(x) - expert(x)) for x in p] for p in paths], 0)
    dist = np.mean([[np.sqrt(((X - x) ** 2).sum(1).min()) for x in p] for p in paths], 0)
    return err, dist, paths


def noisy_success(pol, rng, n=40):
    ok = lambda p: (np.linalg.norm(p - OBST, axis=1) >= R_OBST).all() and np.linalg.norm(p[-1] - GOAL) < 0.15
    return float(np.mean([ok(rollout(pol, x0, rng)) for x0 in starts(rng, n)]))


if __name__ == "__main__":
    for r in (0, 2, 4):
        print(r, np.mean([noisy_success(dagger(np.random.default_rng(s), 4, r)[0], np.random.default_rng(9 + s)) for s in range(3)]))
