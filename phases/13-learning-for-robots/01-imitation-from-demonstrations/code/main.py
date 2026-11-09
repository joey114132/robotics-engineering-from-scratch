# 레슨 13/01: 장애물을 돌아 목표로 가는 점 로봇의 전문가 제어기, 시연 수집, kNN·최소제곱 모방 정책
import numpy as np

GOAL, OBST, R_OBST, DT = np.array([1.0, 0.0]), np.array([0.0, 0.0]), 0.3, 0.05


def expert(x: np.ndarray) -> np.ndarray:
    """Unit-speed pull to the goal plus a swirl around the obstacle that fades out 0.35 m from its edge."""
    d = GOAL - x
    a = d / (np.linalg.norm(d) + 1e-9)
    o = x - OBST
    r = np.linalg.norm(o) + 1e-9
    if r < R_OBST + 0.35:
        side = 1.0 if o[0] * d[1] - o[1] * d[0] >= 0 else -1.0  # pass on the side the point already leans to
        w = 2.5 * (1 - (r - R_OBST) / 0.35)
        a = a + w * side * np.array([-o[1], o[0]]) / r + w * 0.6 * o / r
    return a / max(1.0, np.linalg.norm(a))


def step(x, a, noise=0.0, rng=None):
    a = np.clip(a, -1, 1)
    if noise:
        a = a + noise * rng.standard_normal(2)
    return x + DT * a


def rollout(policy, x0, T=120, noise=0.0, rng=None):
    xs, acts = [np.array(x0, float)], []
    for _ in range(T):
        acts.append(policy(xs[-1]))
        xs.append(step(xs[-1], acts[-1], noise, rng))
    return np.array(xs), np.array(acts)


def success(xs) -> bool:
    hit = (np.linalg.norm(xs - OBST, axis=1) < R_OBST).any()
    return bool(not hit and np.linalg.norm(xs[-1] - GOAL) < 0.1)


def random_starts(rng, n):
    return np.column_stack([rng.uniform(-1.5, -0.8, n), rng.uniform(-0.8, 0.8, n)])


def collect(rng, n_demos, policy=expert):
    """Stack (observation, action) pairs from n_demos expert trajectories."""
    runs = [rollout(policy, x0) for x0 in random_starts(rng, n_demos)]
    return np.vstack([r[0][:-1] for r in runs]), np.vstack([r[1] for r in runs])


def fit_knn(X, A, k=3):
    def policy(x):
        idx = np.argsort(((X - x) ** 2).sum(1))[:k]
        return A[idx].mean(0)
    return policy


def fit_linear(X, A):
    feats = lambda x: np.append(x, 1.0)
    W, *_ = np.linalg.lstsq(np.array([feats(x) for x in X]), A, rcond=None)
    return lambda x: feats(x) @ W


def success_rate(policy, rng, n=60):
    return float(np.mean([success(rollout(policy, x0)[0]) for x0 in random_starts(rng, n)]))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    print("expert", success_rate(expert, rng))
    for n in (1, 3, 10, 30):
        X, A = collect(rng, n)
        print(n, "knn", success_rate(fit_knn(X, A), rng), "linear", success_rate(fit_linear(X, A), rng))
