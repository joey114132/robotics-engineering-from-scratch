# 레슨 08/06 그림: 표류한 궤적과 루프 폐쇄 뒤 궤적, 포즈별 위치 오차 변화를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pg_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    truth, edges, X0 = m.world(np.random.default_rng(0))
    X, costs = m.solve(X0, edges)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    ax1.plot(*truth[:, :2].T, color=GREY, lw=5, alpha=0.4, label="truth")
    ax1.plot(*X0[:, :2].T, "o--", color=ORANGE, ms=4, label="odometry only")
    ax1.plot(*X[:, :2].T, "o-", color=BLUE, ms=4, label="after loop closure")
    ax1.plot(*X0[-1, :2], "s", color=ORANGE, ms=10)
    ax1.annotate("end of odometry", X0[-1, :2], (2.0, -1.0), color=ORANGE, arrowprops=dict(arrowstyle="->", color=ORANGE))
    ax1.set_aspect("equal")
    ax1.set_ylim(-1.4, 5.5)
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.set_title("The open loop snaps shut")
    ax1.legend(loc="center")
    ax1.grid(alpha=0.3)
    k = np.arange(len(truth))
    for P, color, lab in ((X0, ORANGE, f"odometry only (rms {m.ate(X0, truth):.2f} m)"), (X, BLUE, f"after closure (rms {m.ate(X, truth):.2f} m)")):
        ax2.plot(k, np.linalg.norm(P[:, :2] - truth[:, :2], axis=1), "o-", ms=4, color=color, label=lab)
    ax2.set_xlabel("pose index along the loop")
    ax2.set_ylabel("position error (m)")
    ax2.set_title("The correction reaches old poses too")
    ax2.legend(loc="upper left")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-posegraph-loop.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
