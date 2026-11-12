# 레슨 13/06: 두 갈래 시연에서 평균 회귀와 청크 표본기(겹침 평균)를 비교하는 최소 구현
import numpy as np

GOAL, R_OBST, SIGMA, SIGMA_A, T = np.array([1.0, 0.0]), 0.3, 0.15, 0.01, 40  # obstacle is a disc at the origin


def demos(n_pairs, rng):
    """n_pairs demos over the disc and n_pairs mirrored demos under it. Returns positions (D, T+1, 2) and actions (D, T, 2)."""
    x = np.linspace(-1, 1, T + 1)
    P = []
    for _ in range(n_pairs):
        up = np.column_stack([x, rng.uniform(0.45, 0.65) * (1 - x**2)])
        wobble = rng.normal(0, 0.004, up.shape)
        wobble[[0, -1]] = 0
        up = up + wobble
        P += [up, up * [1, -1]]  # the mirror image goes under
    P = np.array(P)
    return P, np.diff(P, axis=1)


def clear(path):
    return bool((np.linalg.norm(path, axis=1) >= R_OBST).all())


def mean_policy(P, A):
    """Kernel regression: the action is the weighted mean of demo actions at nearby demo states."""
    S, V = P[:, :-1].reshape(-1, 2), A.reshape(-1, 2)

    def policy(x):
        d2 = ((S - x) ** 2).sum(1)
        w = np.exp(-(d2 - d2.min()) / (2 * SIGMA**2))
        return w @ V / w.sum()
    return policy


def rollout_mean(policy, x0, steps=60):
    path = [np.array(x0, float)]
    for _ in range(steps):
        path.append(path[-1] + policy(path[-1]))
    return np.array(path)


def sample_chunk(P, A, x, H, rng, prefix=None):
    """Pick one demo, likelier when it is near x and when its chunk agrees with the actions already committed (prefix)."""
    j = ((P[:, :-1] - x) ** 2).sum(2).argmin(1)
    pad = np.concatenate([A, np.zeros((len(A), H, 2))], 1)
    chunks = np.array([pad[d, j[d]:j[d] + H] for d in range(len(P))])
    logw = -((P[np.arange(len(P)), j] - x) ** 2).sum(1) / (2 * SIGMA**2)
    if prefix is not None:  # a chunk that flips to the other way round would blend into a straight line
        logw -= ((chunks[:, :len(prefix)] - prefix) ** 2).sum((1, 2)) / (2 * SIGMA_A**2)
    w = np.exp(logw - logw.max())
    return chunks[rng.choice(len(P), p=w / w.sum())]


def rollout_chunks(P, A, x0, H, overlap, rng, steps=60):
    """Sample a new chunk every H - overlap steps. While two chunks overlap, blend them with weights that ramp to the new one."""
    x, path, stride, new = np.array(x0, float), [np.array(x0, float)], H - overlap, None
    for t in range(steps):
        if t % stride == 0:
            old, new, t1 = new, sample_chunk(P, A, x, H, rng, None if new is None else new[stride:]), t
        k = t - t1
        w = (k + 1) / (overlap + 1) if old is not None and k < overlap else 1.0
        a = w * new[k] + (1 - w) * old[k + stride] if w < 1 else new[k]
        x = x + a
        path.append(x)
    return np.array(path)


def jitter(path):
    """Mean size of the change in action from one step to the next."""
    return float(np.linalg.norm(np.diff(path, 2, axis=0), axis=1).mean())


if __name__ == "__main__":
    P, A = demos(6, np.random.default_rng(0))
    start = np.array([-1.0, 0.0])
    print("mean policy clear:", clear(rollout_mean(mean_policy(P, A), start)))
    for H, o in ((1, 0), (8, 4)):
        runs = [rollout_chunks(P, A, start, H, o, np.random.default_rng(s)) for s in range(50)]
        print(f"chunk {H} overlap {o}: clear {np.mean([clear(r) for r in runs]):.2f} jitter {np.mean([jitter(r) for r in runs]):.4f}")
