# 레슨 14/03 그림: 교착 해소 전후의 누적 완료 작업 수, 그리고 로봇 수에 따른 처리량
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("traffic_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
N_JOBS, SEEDS = 40, 30


def jobs(seed, size=4):
    rng = np.random.default_rng(seed)
    out = []
    while len(out) < N_JOBS:
        a, b = tuple(int(v) for v in rng.integers(0, size, 2)), tuple(int(v) for v in rng.integers(0, size, 2))
        if a != b:
            out.append((a, b))
    return out


def mean_hist(K, policy, T):
    return np.mean([m.run(jobs(s), K, policy, T) for s in range(SEEDS)], axis=0)


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.6))
    T = 60
    for policy, color, lab in (("naive", ORANGE, "move if next node is free"), ("reserve", BLUE, "reserve whole route")):
        ax1.plot(range(1, T + 1), mean_hist(8, policy, T), color=color, label=lab)
    ax1.axhline(N_JOBS, color=GREY, lw=1, ls="--")
    ax1.set_xlabel("tick")
    ax1.set_ylabel("jobs finished (mean of 30 layouts)")
    ax1.set_title("8 robots: one policy freezes, one finishes")
    ax1.legend(loc="center right")
    Ks = [1, 2, 4, 6, 8, 12, 16]
    for policy, color, lab in (("naive", ORANGE, "move if free"), ("reserve", BLUE, "reserve route")):
        ax2.plot(Ks, [mean_hist(K, policy, 30)[-1] for K in Ks], "o-", color=color, label=lab)
    ax2.set_xlabel("robots on the grid (K)")
    ax2.set_ylabel("jobs finished by tick 30")
    ax2.set_title("More robots help only if they cannot deadlock")
    ax2.legend(loc="center right")
    fig.tight_layout()
    fig.savefig(HERE.parent / "assets" / "fig-throughput.png", dpi=100)
    print([round(mean_hist(8, p, T)[-1], 1) for p in ("naive", "reserve")])


if __name__ == "__main__":
    main()
