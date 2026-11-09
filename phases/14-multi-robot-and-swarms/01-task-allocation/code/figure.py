# 레슨 14/01 그림: 같은 배치에서 탐욕과 최적 배정의 지도, 그리고 임의 문제 300개의 비용 차이
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("alloc_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
ASSETS = HERE.parent / "assets"


def draw(ax, R, T, C, a, color, title):
    for i, j in enumerate(a):
        ax.plot([R[i, 0], T[j, 0]], [R[i, 1], T[j, 1]], "-", color=color, lw=2)
    ax.plot(*R.T, "o", color=GREY, ms=11, label="robot")
    ax.plot(*T.T, "s", color="black", ms=10, label="task")
    ax.set_title(f"{title}: total {m.total(C, a):.2f} m")
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")


def main():
    rng = np.random.default_rng(3)
    best = None
    for _ in range(200):  # pick a layout where the gap is easy to see
        R, T = rng.random((10, 2)), rng.random((10, 2))
        C = m.cost_matrix(R, T)
        gap = m.total(C, m.greedy(C)) / m.total(C, m.hungarian(C))
        if best is None or gap > best[0]:
            best = (gap, R, T, C)
    _, R, T, C = best
    fig, axs = plt.subplots(1, 2, figsize=(12, 5.8))
    draw(axs[0], R, T, C, m.greedy(C), ORANGE, "Greedy nearest")
    draw(axs[1], R, T, C, m.hungarian(C), BLUE, "Optimal (Hungarian)")
    axs[0].legend(loc="upper center", bbox_to_anchor=(1.1, -0.14), ncol=2)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-assignment-map.png", dpi=100)

    fig, ax = plt.subplots(figsize=(10, 5.6))
    ns, rng = [4, 8, 16, 32], np.random.default_rng(0)
    means = []
    for k, n in enumerate(ns):
        r = []
        for _ in range(300):
            C = m.cost_matrix(rng.random((n, 2)), rng.random((n, 2)))
            r.append(m.total(C, m.greedy(C)) / m.total(C, m.hungarian(C)))
        ax.plot(np.full(len(r), k) + rng.uniform(-0.18, 0.18, len(r)), r, ".", color=BLUE, alpha=0.18, ms=6)
        means.append(np.mean(r))
    ax.plot(range(len(ns)), means, "o-", color=ORANGE, label="mean over 300 instances")
    ax.axhline(1, color=GREY, lw=1)
    ax.set_xticks(range(len(ns)), [str(n) for n in ns])
    ax.set_xlabel("robots = tasks (N)")
    ax.set_ylabel("greedy cost / optimal cost")
    ax.set_title("Greedy never wins, and its gap grows with N")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-cost-gap.png", dpi=100)
    print(ns, [round(x, 3) for x in means])


if __name__ == "__main__":
    main()
