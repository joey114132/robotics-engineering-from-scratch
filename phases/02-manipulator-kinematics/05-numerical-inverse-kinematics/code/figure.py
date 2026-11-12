# 레슨 02/05 그림: 같은 표적에 닿는 여러 seed 의 팔 자세와 반복마다 줄어드는 오차를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("numik_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

L = (0.4, 0.3, 0.2)
LO, HI = np.array([-np.pi, -2.5, -2.5]), np.array([np.pi, 2.5, 2.5])
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def points(q):
    a = np.cumsum(q)
    return np.cumsum(np.r_[0, L * np.cos(a)]), np.cumsum(np.r_[0, L * np.sin(a)])


def history(target, q0, n=40):
    return [np.linalg.norm(target - m.fk(m.solve_ik(target, L, q0, LO, HI, iters=k)[0], L)) for k in range(n)]


def main():
    target = np.array([0.5, 0.3])
    sols = [q for q, ok in m.ik_restarts(target, L, LO, HI, n=12, seed=1) if ok]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    for q in sols[:8]:
        x, y = points(q)
        c = BLUE if q[1] > 0 else ORANGE
        ax1.plot(x, y, "-o", color=c, alpha=0.45, lw=3, ms=5)
    ax1.plot(*target, "*", color="k", ms=18, zorder=5)
    ax1.plot([], [], color=BLUE, lw=3, label="elbow bends one way (q2 > 0)")
    ax1.plot([], [], color=ORANGE, lw=3, label="elbow bends the other (q2 < 0)")
    ax1.set_aspect("equal")
    ax1.set_xlim(-0.35, 0.95)
    ax1.set_ylim(-0.7, 0.8)
    ax1.set_title("Eight seeds, one target (star)")
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.legend(loc="lower left", fontsize=9)
    ax1.grid(alpha=0.3)
    rng = np.random.default_rng(1)
    for i in range(4):
        ax2.semilogy(history(target, rng.uniform(LO, HI)), color=BLUE, alpha=0.7, label="reachable target" if i == 0 else None)
    ax2.semilogy(history(np.array([1.5, 0.0]), np.array([0.3, 0.3, 0.3])), color=ORANGE, lw=2, label="unreachable target (best effort)")
    ax2.axhline(1e-6, color=GREY, ls=":", lw=1)
    ax2.set_ylim(1e-8, 2)
    ax2.set_xlabel("iteration")
    ax2.set_ylabel("tip error (m)")
    ax2.set_title("Converges fast, or plateaus honestly")
    ax2.legend(loc="lower left", fontsize=9)
    ax2.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-numerical-ik.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
