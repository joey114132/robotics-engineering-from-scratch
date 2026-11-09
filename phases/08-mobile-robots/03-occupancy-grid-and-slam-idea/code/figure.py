# 레슨 08/03 그림: 참 지도, 알려진 자세로 만든 지도, 자세 drift 로 번진 지도, drift 크기별 정밀도
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("grid_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
OUT = HERE.parent / "assets"
EXT = (0, m.N * m.RES, 0, m.N * m.RES)


def show(ax, img, title, path=None, est=None):
    ax.imshow(img, origin="lower", extent=EXT, cmap="Greys", vmin=0, vmax=1)
    if path is not None:
        ax.plot(path[:, 0], path[:, 1], color=BLUE, lw=1.5)
    if est is not None:
        ax.plot(est[:, 0], est[:, 1], color=ORANGE, lw=1.5)
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("x (m)")
    ax.grid(False)


def main():
    w, tp = m.make_world(), m.loop_poses()
    dr = m.drift(tp, 0.003)
    clean, bad = m.build_map(w, tp, tp), m.build_map(w, tp, dr)
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 4.4), sharey=True)
    show(axs[0], w.astype(float), "True room and robot path", tp)
    show(axs[1], m.prob(clean), f"Known poses: precision {m.precision(clean, w):.2f}")
    show(axs[2], m.prob(bad), f"Drifted poses: precision {m.precision(bad, w):.2f}", tp, dr)
    axs[0].set_ylabel("y (m)")
    axs[2].plot([], [], color=BLUE, label="true path")
    axs[2].plot([], [], color=ORANGE, label="believed path")
    axs[2].legend(loc="lower left", fontsize=10, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(OUT / "fig-grid-maps.png", dpi=100)

    fig, ax = plt.subplots(figsize=(9, 4.8))
    e = np.array([0, 0.0005, 0.001, 0.0015, 0.002, 0.003])
    prec, cnt = [], []
    for v in e:
        L = m.build_map(w, tp, m.drift(tp, v))
        prec.append(m.precision(L, w))
        cnt.append((L > 0).sum())
    ax.plot(np.degrees(e) * len(tp), prec, "o-", color=BLUE)
    ax.set_xlabel("heading error accumulated over the loop (deg)")
    ax.set_ylabel("share of occupied cells that are real")
    ax.set_ylim(0, 1)
    ax.set_title("A few degrees of heading error ruin the walls")
    fig.tight_layout()
    fig.savefig(OUT / "fig-smear-curve.png", dpi=100)
    print(list(zip(np.degrees(e) * len(tp), np.round(prec, 2), cnt)))


if __name__ == "__main__":
    main()
