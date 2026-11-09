# 레슨 02/03 그림: 유한 차분 오차가 step 크기에 따라 어떻게 변하는지와 자세별 tip 속도 타원을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("jac_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
L = (0.5, 0.4)


def arm(ax, q, color):
    p1 = L[0] * np.array([np.cos(q[0]), np.sin(q[0])])
    p2 = m.fk(q, L)
    ax.plot([0, p1[0], p2[0]], [0, p1[1], p2[1]], "-", color=color, lw=4, solid_capstyle="round")
    ax.plot([0, p1[0], p2[0]], [0, p1[1], p2[1]], "o", color=color, ms=7)
    return p2


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.4), gridspec_kw={"width_ratios": [1, 1.05]})
    q = np.array([0.3, 0.8])
    eps = np.logspace(-12, 0, 60)
    err = [np.abs(m.jacobian_fd(q, L, e) - m.jacobian(q, L)).max() for e in eps]
    ax1.loglog(eps, err, color=BLUE, lw=2.5)
    ax1.axvline(1e-6, color=GREY, ls="--", lw=1)
    ax1.text(0.5, 0.45, "default step 1e-6 ", color=GREY, fontsize=11, ha="right", transform=ax1.transAxes)
    ax1.text(0.03, 0.8, "too small:\nrounding noise", fontsize=11, color=ORANGE, transform=ax1.transAxes)
    ax1.text(0.97, 0.3, "too large:\ncurvature", fontsize=11, color=ORANGE, ha="right", transform=ax1.transAxes)
    ax1.set_xlabel("finite-difference step eps (rad)")
    ax1.set_ylabel("max |J_fd - J_analytic| (m)")
    ax1.set_title("A step that is too small or too large is wrong", fontsize=13)
    ax1.grid(alpha=0.3, which="both")
    t = np.linspace(0, 2 * np.pi, 200)
    circle = np.vstack([np.cos(t), np.sin(t)])
    for qq, c, lab in (([0.3, 1.5], BLUE, "bent, q2 = 1.5"), ([0.3, 0.35], ORANGE, "nearly straight, q2 = 0.35")):
        tip = arm(ax2, qq, c)
        ax2.plot([], [], color=c, lw=4, label=lab)
        e = m.J_times(m.jacobian(qq, L), circle) * 0.2 + tip[:, None]
        ax2.plot(e[0], e[1], color=c, lw=2, ls="--")
    ax2.set_aspect("equal")
    ax2.set_xlim(-0.15, 1.05)
    ax2.set_ylim(-0.15, 0.95)
    ax2.set_xlabel("x (m)")
    ax2.set_ylabel("y (m)")
    ax2.set_title("Dashed: tip speeds from unit joint speeds", fontsize=13)
    ax2.legend(loc="lower right", fontsize=10)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-jacobian.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
