# 레슨 02/01 그림: 맞는 규약과 틀린 규약이 만든 팔 자세, 그리고 오차가 q 에 따라 자라는 모습을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("dh_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
L1, L2 = 0.4, 0.3




def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.4), gridspec_kw={"width_ratios": [1, 1.1]})
    q = np.array([0.5, 0.8])
    rows, tool = m.planar_craig(L1, L2)
    for conv, color, ls, lab in (("craig", BLUE, "-", "right: Craig routine"), ("standard", ORANGE, "--", "wrong: standard routine")):
        tip = m.fk_dh(rows, q, conv, tool=tool)[:2, 3]
        mid = m.fk_dh(rows, q, conv)[:2, 3]
        xs = [0, mid[0], tip[0]]
        ys = [0, mid[1], tip[1]]
        ax1.plot(xs, ys, ls, color=color, lw=4, solid_capstyle="round", label=lab)
        ax1.plot(xs, ys, "o", color=color, ms=8)
    ax1.set_aspect("equal")
    ax1.set_title("Same table, same q = (0.5, 0.8) rad", fontsize=13)
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.grid(alpha=0.3)
    ax1.set_xlim(-0.05, 0.75)
    ax1.set_ylim(-0.05, 0.85)
    ax1.legend(loc="lower right", fontsize=10)
    t = np.linspace(0, 1.5, 200)
    err = []
    for s in t:
        qq = np.array([s, s])
        a = m.fk_dh(rows, qq, "craig", tool=tool)[:2, 3]
        b = m.fk_dh(rows, qq, "standard", tool=tool)[:2, 3]
        err.append(np.linalg.norm(a - b))
    ax2.plot(t, np.array(err) * 100, color=ORANGE, lw=2.5)
    ax2.plot([0], [0], "o", color=BLUE, ms=11, zorder=3)
    ax2.annotate("zero pose: error 0,\nthe check passes", (0, 0), (0.15, 14), fontsize=11, arrowprops=dict(arrowstyle="->", color=GREY))
    ax2.set_xlabel("both joints at q (rad)")
    ax2.set_ylabel("tip position error (cm)")
    ax2.set_title("The error is invisible exactly where people look", fontsize=13)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-wrong-convention.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
