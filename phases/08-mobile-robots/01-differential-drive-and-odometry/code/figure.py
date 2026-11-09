# 레슨 08/01 그림: 같은 바퀴 명령으로 그린 실제 경로와 dead reckoning 경로, 오차 크기별 닫힘 오차
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("dd_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

R, B, DT = 0.05, 0.30, 0.01
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    wl, wr = m.square_wheels(2.0, 0.5, DT, R, B)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1.1, 1]})
    est = m.dead_reckon(wl, wr, DT, R, B)
    true = m.dead_reckon(wl, wr, DT, R, B * 1.02)
    ax1.plot(est[:, 0], est[:, 1], "--", color=GREY, label="odometry estimate: closes the loop")
    ax1.plot(true[:, 0], true[:, 1], color=ORANGE, label="real robot, track width 2% too large")
    ax1.plot(*true[-1, :2], "o", color=ORANGE, ms=11)
    ax1.annotate(f"ends {np.linalg.norm(true[-1, :2]):.2f} m from start", true[-1, :2], (0.45, 0.35), arrowprops=dict(arrowstyle="->", color=ORANGE), color=ORANGE, fontsize=13)
    ax1.plot(0, 0, "s", color=GREY, ms=10)
    ax1.set_aspect("equal")
    ax1.set_xlim(-0.8, 3.0)
    ax1.set_ylim(-0.9, 2.5)
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.set_title("A 2 m square the odometry thinks is closed")
    ax1.legend(loc="upper right", fontsize=11)

    errs = np.linspace(0, 5, 11)
    for name, color, fn in (("track width error", BLUE, lambda e: (R, B * (1 + e / 100))), ("wheel radius error", ORANGE, lambda e: (R * (1 + e / 100), B))):
        ax2.plot(errs, [m.closure_error(wl, wr, DT, *fn(e)) for e in errs], "o-", color=color, label=name)
    ax2.set_xlabel("parameter error (%)")
    ax2.set_ylabel("distance from start after 4 sides (m)")
    ax2.set_title("The gap grows with the error")
    ax2.legend(loc="upper left")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-odometry-drift.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
