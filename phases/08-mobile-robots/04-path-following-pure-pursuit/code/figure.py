# 레슨 08/04 그림: 세 lookahead 거리의 경로, 코너 확대, 첫 직선 구간의 옆 오차
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pp_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
CORNERS = [(0, 0), (10, 0), (10, 10)]
STYLE = {0.4: ("#D55E00", "Ld = 0.4 m"), 1.5: ("#0072B2", "Ld = 1.5 m"), 4.0: ("#009E73", "Ld = 4.0 m")}


def main():
    ref = np.array(CORNERS)
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1, 1, 1.15]})
    for ld, (c, lab) in STYLE.items():
        t = m.follow(CORNERS, ld)
        cut = np.linalg.norm(t[:, :2] - [10, 0], axis=1).min()
        for ax in axs[:2]:
            ax.plot(t[:, 0], t[:, 1], color=c, label=f"{lab}, corner cut {cut:.2f} m")
        leg = t[t[:, 0] < 9.5]
        axs[2].plot(leg[:, 0], leg[:, 1], color=c, label=lab)
    for ax in axs[:2]:
        ax.plot(ref[:, 0], ref[:, 1], "--", color="#555555", lw=1.5, label="path")
        ax.plot(10, 0, "k+", ms=12)
        ax.set_aspect("equal")
        ax.set_xlabel("x (m)")
    axs[0].set_xlim(-0.5, 11)
    axs[0].set_ylim(-1, 11)
    axs[0].set_ylabel("y (m)")
    axs[0].set_title("Whole path")
    axs[0].legend(loc="upper left", fontsize=9)
    axs[1].set_xlim(7, 11)
    axs[1].set_ylim(-0.5, 3.5)
    axs[1].set_title("Zoom on the corner")
    axs[2].axhline(0, color="#555555", ls="--", lw=1.5)
    axs[2].set_ylim(-0.5, 0.8)
    axs[2].set_xlabel("x (m)")
    axs[2].set_ylabel("distance left of the path (m)")
    axs[2].set_title("First straight: wobble or smooth?")
    axs[2].legend(loc="upper right", fontsize=10)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-lookahead-paths.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
