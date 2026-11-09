# 레슨 13/03: 1차원 도달 과제에서 Gaussian 정책의 REINFORCE, 배치 기준선(leave-one-out)의 분산 감소
import numpy as np

DT, T, SIGMA, BONUS = 0.2, 15, 0.5, 3.0


def episode(theta, rng, sigma=SIGMA):
    """Policy a ~ N(w*x + b, sigma^2). State x, x' = x + DT*a, reward BONUS - x'^2 - 0.01 a^2 (BONUS: a per-step alive bonus)."""
    x, xs, acts, rs = rng.uniform(-1, 1), [], [], []
    for _ in range(T):
        a = theta[0] * x + theta[1] + sigma * rng.standard_normal()
        xs.append(x), acts.append(a)
        x = x + DT * a
        rs.append(BONUS - x * x - 0.01 * a * a)
    return np.array(xs), np.array(acts), np.array(rs)


def score(theta, x, a, sigma=SIGMA):
    """Gradient of log N(a; w*x + b, sigma^2) with respect to (w, b)."""
    return (a - (theta[0] * x + theta[1])) / sigma**2 * np.array([x, 1.0])


def reward_to_go(r):
    return np.cumsum(r[::-1])[::-1]


def grad_estimate(theta, rng, batch, baseline):
    """Mean over episodes of sum_t score_t * (G_t - b_t). Baseline b_t = mean G_t of the OTHER episodes, so it stays unbiased."""
    eps = [episode(theta, rng) for _ in range(batch)]
    G = np.array([reward_to_go(r) for _, _, r in eps])
    b = (G.sum(0) - G) / (batch - 1) if baseline else np.zeros_like(G)
    g = np.zeros(2)
    for i, (xs, acts, _) in enumerate(eps):
        g += sum(score(theta, x, a) * (G[i, t] - b[i, t]) for t, (x, a) in enumerate(zip(xs, acts)))
    return g / batch, G[:, 0].mean()


def train(rng, iters=60, batch=32, baseline=True, lr=0.006):
    """Plain gradient ascent; returns the mean episode return per iteration."""
    theta, curve = np.zeros(2), []
    for _ in range(iters):
        g, ret = grad_estimate(theta, rng, batch, baseline)
        theta = theta + lr * g
        curve.append(ret)
    return np.array(curve)


if __name__ == "__main__":
    for base in (False, True):
        print(base, train(np.random.default_rng(0), baseline=base)[[0, 20, 40, 59]].round(2))
