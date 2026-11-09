# 레슨 09/04 그림: 최적화 전후 경로와 반복마다의 비용(전체, 부드러움, 장애물)을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("opt_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
OBS = [(np.array([3.5, 0.3]), 1.0), (np.array([7.0, -0.5]), 1.0)]
MARGIN = 0.4
OUT = HERE.parent / "assets"


def main():
    OUT.mkdir(exist_ok=True)
    X0 = np.linspace([0.0, 0.0], [10.0, 0.0], 22)
    X0[1:-1, 1] += np.random.default_rng(0).uniform(-0.15, 0.15, 20)
    X, hist = m.optimise(X0, OBS, iters=4000, lr=0.04)
    Y, rows = X0.copy(), []
    for _ in range(4000):  # same descent again, keeping the two cost terms apart
        Y -= 0.04 * m.grad(Y, OBS)
        rows.append(m.cost(Y, OBS))
    rows = np.array(rows)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 5.2), gridspec_kw={"width_ratios": [1.3, 1]})
    for c, r in OBS:
        a1.add_patch(Circle(c, r, color=GREY, alpha=0.4))
        a1.add_patch(Circle(c, r + MARGIN, fill=False, ls="--", ec=GREY))
    a1.plot(X0[:, 0], X0[:, 1], "o-", color=ORANGE, ms=6, lw=2, label="before: jagged, inside obstacles")
    a1.plot(X[:, 0], X[:, 1], "o-", color=BLUE, ms=6, lw=2.8, label="after 4000 steps")
    a1.set_aspect("equal")
    a1.set_xlim(-0.3, 10.3)
    a1.set_ylim(-2.3, 2.3)
    a1.set_xlabel("x (m)")
    a1.set_ylabel("y (m)")
    a1.set_title("Dashed ring: obstacle plus margin", fontsize=15)
    a1.legend(loc="lower left", fontsize=11)

    it = np.arange(1, len(hist) + 1)
    a2.set_xscale("log")
    a2.semilogy(it, rows[:, 0], color=BLUE, label="total")
    a2.semilogy(it, rows[:, 1], "--", color=GREY, label="smoothness")
    a2.semilogy(it, rows[:, 2], ":", color=ORANGE, label="obstacle penalty")
    a2.set_xlabel("iteration (log scale)")
    a2.set_ylabel("cost")
    a2.set_title("Cost falls on every iteration", fontsize=15)
    a2.set_ylim(3e-3, 30)
    a2.legend(loc="center right")
    fig.tight_layout()
    fig.savefig(OUT / "fig-before-after.png", dpi=100)
    print(OUT)


if __name__ == "__main__":
    main()
