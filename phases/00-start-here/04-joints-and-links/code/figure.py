# 레슨 00/04 그림: 두 링크의 관절 각도를 모두 돌렸을 때 손이 닿을 수 있는 자리(고리 모양)를 그린다
import importlib.util
import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lesson_joints_fig", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
L1, L2 = 0.4, 0.3


def main():
    pts = np.array([m.two_link_position(L1, L2, a, b) for a in np.linspace(0, 2 * math.pi, 120) for b in np.linspace(0, 2 * math.pi, 120)])
    fig, ax = plt.subplots(figsize=(7, 6.4))
    ax.scatter(pts[:, 0], pts[:, 1], s=2, color=BLUE, alpha=0.25, label="places the hand can reach")
    q1, q2 = math.radians(30), math.radians(60)
    elbow = m.hand_position(L1, q1)
    hand = m.two_link_position(L1, L2, q1, q2)
    ax.plot([0, elbow[0], hand[0]], [0, elbow[1], hand[1]], color=ORANGE, lw=4, marker="o", label="one pose: 30 and 60 degrees")
    ax.set_aspect("equal")
    ax.set_xlabel("how far across (m)")
    ax.set_ylabel("how far up (m)")
    ax.set_title("Two links reach a ring, not a square", fontsize=13)
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-reach-ring.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    r = np.hypot(pts[:, 0], pts[:, 1])
    print(out, "reach from", round(float(r.min()), 3), "to", round(float(r.max()), 3), "m")


if __name__ == "__main__":
    main()
