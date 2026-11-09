# 레슨 07/01: 고리 복도 1차원 histogram Bayes filter (predict = 모션 번짐, update = 센서 가능도)
import numpy as np

DOORS = np.array([1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0])  # 1 = door, 0 = wall
N = len(DOORS)
KERNEL = (0.05, 0.9, 0.05)  # P(robot moves one cell short, exact, one cell long)
P_HIT = 0.9  # P(sensor reports the true cell type)


def predict(bel, move, kernel=KERNEL):
    """Motion step: shift by `move` cells, blurred by the kernel (a convolution on the ring)."""
    return sum(p * np.roll(bel, move + k) for k, p in zip((-1, 0, 1), kernel))


def update(bel, z, doors=DOORS, p_hit=P_HIT):
    """Sensor step: multiply by the likelihood of reading z in each cell, then renormalise."""
    post = bel * np.where(doors == z, p_hit, 1 - p_hit)
    return post / post.sum()


def entropy(bel):
    """Shannon entropy in nats: 0 for a spike, ln(N) for a uniform belief."""
    p = bel[bel > 0]
    return float(-(p * np.log(p)).sum())


def simulate(doors, start, moves, rng, p_hit=P_HIT, kernel=KERNEL):
    """Ground truth: noisy motion, noisy door/wall readings. Returns (positions, readings)."""
    pos, truth, zs = start, [], []
    for mv in moves:
        pos = (pos + mv + rng.choice((-1, 0, 1), p=kernel)) % len(doors)
        z = doors[pos] if rng.random() < p_hit else 1 - doors[pos]
        truth.append(pos)
        zs.append(int(z))
    return truth, zs


def run(doors, zs, moves, use_update=True, bel0=None):
    """Filter over a whole run. Returns beliefs, shape (steps + 1, N); row 0 is the prior."""
    bel = np.full(len(doors), 1 / len(doors)) if bel0 is None else bel0
    out = [bel]
    for mv, z in zip(moves, zs):
        bel = predict(bel, mv)
        if use_update:
            bel = update(bel, z, doors)
        out.append(bel)
    return np.array(out)


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    moves = [1] * 25
    truth, zs = simulate(DOORS, 7, moves, rng)
    bel = run(DOORS, zs, moves)
    print("true cell", truth[-1], "best guess", bel[-1].argmax(), "entropy", entropy(bel[0]), "->", entropy(bel[-1]))
