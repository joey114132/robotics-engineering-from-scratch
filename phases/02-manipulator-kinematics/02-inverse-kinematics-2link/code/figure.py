# 레슨 02/02 그림: 같은 목표에 닿는 두 자세와 도달 범위, 목표가 경계에 다가갈 때 관절각이 변하는 모습을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ik_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
L = (0.5, 0.4)


def draw(ax, q, color, ls, label):
    p1 = L[0] * np.array([np.cos(q[0]), np.sin(q[0])])
    p2 = m.fk(q, L)
    ax.plot([0, p1[0], p2[0]], [0, p1[1], p2[1]], ls, color=color, lw=4, solid_capstyle="round", label=label)
    ax.plot([0, p1[0], p2[0]], [0, p1[1], p2[1]], "o", color=color, ms=8)


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1, 1.1]})
    t = np.linspace(0, 2 * np.pi, 200)
    for r in (abs(L[0] - L[1]), L[0] + L[1]):
        ax1.plot(r * np.cos(t), r * np.sin(t), color=GREY, lw=1, ls=":")
    ax1.text(0.08, 0.95, "outer reach 0.9 m", ha="left", fontsize=10, color=GREY)
    ax1.text(0.0, 0.12, "inner limit 0.1 m", ha="center", fontsize=10, color=GREY)
    p = (0.6, 0.3)
    draw(ax1, m.ik(p, L, "down"), BLUE, "-", "elbow-down")
    draw(ax1, m.ik(p, L, "up"), ORANGE, "--", "elbow-up")
    ax1.plot(*p, "*", color="black", ms=16, zorder=5, label="target")
    ax1.set_aspect("equal")
    ax1.set_xlim(-0.2, 1.0)
    ax1.set_ylim(-0.2, 1.05)
    ax1.set_title("One target, two arms that both reach it", fontsize=13)
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.grid(alpha=0.3)
    ax1.legend(loc="upper right", fontsize=10, framealpha=0.95)
    y = 0.3
    xmax = np.sqrt((L[0] + L[1]) ** 2 - y * y)
    xs = np.linspace(0.0, xmax, 400)
    for e, c in (("down", BLUE), ("up", ORANGE)):
        q = np.array([m.ik((x, y), L, e) for x in xs])
        ax2.plot(xs, np.degrees(q[:, 0]), "-", color=c, lw=2.2, label=f"q1, elbow-{e}")
        ax2.plot(xs, np.degrees(q[:, 1]), "--", color=c, lw=2.2, label=f"q2, elbow-{e}")
    ax2.axvspan(xmax, 1.0, color=GREY, alpha=0.2)
    ax2.text(xmax + 0.012, 100, "unreachable:\nIK refuses", fontsize=11, color=GREY)
    ax2.set_xlim(0, 1.0)
    ax2.set_xlabel("target x at y = 0.3 m (m)")
    ax2.set_ylabel("joint angle (deg)")
    ax2.set_title("Sliding the target outward until the arm is straight", fontsize=13)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), fontsize=9, ncol=4)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-two-elbows.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
