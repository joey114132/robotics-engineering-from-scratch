# 레슨 08/02 그림: particle 구름이 실제 자세로 모이는 과정, kidnapped robot 에서 random particle 주입 유무의 오차
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pf_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
OUT = HERE.parent / "assets"


def simulate(inject, sv, sw, steps, kidnap=None, snaps=(), seed=0, n=1000):
    rng, rz = np.random.default_rng(seed), np.random.default_rng(seed + 100)
    truth = np.array([[2.0, 3.0, 0.3]])
    P = np.column_stack([rng.uniform(0, 10, (n, 2)), rng.uniform(-np.pi, np.pi, n)])
    err, shots = [], {0: (P.copy(), truth.copy())}
    for t in range(steps):
        if t == kidnap:
            truth = np.array([[8.0, 7.0, -2.0]])
        truth = m.move(truth, 0.8, 0.15, 0.1)
        z = m.ranges(truth)[0] + rz.normal(0, 0.3, 4)
        P = m.pf_step(P, 0.8, 0.15, 0.1, z, 0.3, rng, sv=sv, sw=sw, inject=inject)
        err.append(np.linalg.norm(m.estimate(P)[:2] - truth[0, :2]))
        if t + 1 in snaps:
            shots[t + 1] = (P.copy(), truth.copy())
    return np.array(err), shots


def main():
    _, shots = simulate(0.0, 0.4, 1.0, 40, snaps=(1, 3, 40))
    fig, axs = plt.subplots(1, 4, figsize=(12.5, 3.9), sharey=True)
    for ax, (k, (P, tr)) in zip(axs, sorted(shots.items())):
        ax.plot(P[:, 0], P[:, 1], ".", color=BLUE, ms=3, alpha=0.5)
        ax.plot(*m.LANDMARKS.T, "s", color=GREY, ms=9)
        ax.plot(*tr[0, :2], "*", color=ORANGE, ms=15, mfc="none", mew=2)
        ax.set_title(f"step {k}", fontsize=15)
        ax.set_xlim(-1, 11)
        ax.set_ylim(-1, 11)
        ax.set_aspect("equal")
        ax.set_xlabel("x (m)")
    axs[0].set_ylabel("y (m)")
    axs[0].plot([], [], ".", color=BLUE, label="particles")
    axs[0].plot([], [], "*", color=ORANGE, mfc="none", mew=2, label="true pose")
    axs[0].plot([], [], "s", color=GREY, label="landmarks")
    axs[0].legend(loc="upper left", fontsize=9, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(OUT / "fig-pf-collapse.png", dpi=100)

    fig, ax = plt.subplots(figsize=(10, 5))
    for inj, color, lab in ((0.0, ORANGE, "plain filter"), (0.05, BLUE, "5% random particles each step")):
        err, _ = simulate(inj, 0.1, 0.3, 100, kidnap=40)
        ax.plot(np.arange(100) * 0.1, err, color=color, label=lab)
    ax.axvline(4.0, color=GREY, ls="--")
    ax.text(4.1, ax.get_ylim()[1] * 0.92, "robot is carried away", color=GREY, fontsize=12)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("position error (m)")
    ax.set_title("After a kidnap the plain filter stays lost")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "fig-pf-kidnap.png", dpi=100)
    print(OUT)


if __name__ == "__main__":
    main()
