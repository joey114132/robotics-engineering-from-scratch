# 레슨 16/02 그림: 성공한 주행의 지도와 경로, 오도메트리 오차를 키웠을 때와 landmark 보정 후의 경로를 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("nav_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
START, GOAL = (1.5, 1.5), (9.0, 8.5)
BAD = dict(scale_err=0.03, w_bias=0.03, sigma=0.02)
GOOD = dict(scale_err=0.002, w_bias=0.001, sigma=0.005)
OUT = HERE.parent / "assets"


def draw_map(ax, world, occ):
    ax.imshow(np.where(occ, 0.8, 1.0), origin="lower", extent=(0, 10, 0, 10), cmap="gray", vmin=0, vmax=1)
    ax.imshow(np.where(world, 0.35, np.nan), origin="lower", extent=(0, 10, 0, 10), cmap="gray", vmin=0, vmax=1)
    ax.plot(*START, "o", color=GREY, ms=9)
    ax.plot(*GOAL, "*", color=GREY, ms=16)
    ax.plot(*m.LANDMARKS.T, "^", color=BLUE, ms=10, mec="white", label="landmarks")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")


def cross_track(traj, path):
    p = np.vstack([a + (b - a) * np.linspace(0, 1, 60)[:, None] for a, b in zip(path[:-1], path[1:])])
    return np.linalg.norm(traj[:, None, :2] - p[None], axis=2).min(axis=1)


def main():
    OUT.mkdir(exist_ok=True)
    world = m.make_world()
    occ = m.inflate(world)
    raw, smooth = m.plan(occ, START, GOAL)
    s = np.array(smooth)

    good, _ = m.drive(smooth, (*START, 0.0), **GOOD)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1, 1.1]})
    draw_map(a1, world, occ)
    r = np.array(raw)
    a1.plot(r[:, 0], r[:, 1], color=GREY, lw=1.5, label="A* path")
    a1.plot(s[:, 0], s[:, 1], "o-", color=BLUE, lw=2, label="after shortcuts")
    a1.plot(good[:, 0], good[:, 1], color=ORANGE, lw=2, label="driven path")
    a1.set_title(f"Start to goal, goal error {np.linalg.norm(good[-1, :2] - GOAL):.2f} m")
    a1.legend(loc="lower right", fontsize=9)
    a2.plot(np.arange(len(good)) * 0.05, cross_track(good, s), color=ORANGE)
    a2.set_xlabel("time (s)")
    a2.set_ylabel("distance from planned path (m)")
    a2.set_title("Distance from the smoothed path")
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig-nav-result.png", dpi=100)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 5), gridspec_kw={"width_ratios": [1, 1, 1.05]})
    runs = {}
    for ax, (label, kw) in zip(axes[:2], (("No fix", {}), ("With landmark fix", dict(landmarks=m.LANDMARKS)))):
        t, e = m.drive(smooth, (*START, 0.0), **BAD, **kw)
        runs[label] = (t, e)
        draw_map(ax, world, occ)
        ax.plot(t[:, 0], t[:, 1], color=ORANGE, lw=2, label="true path")
        ax.plot(e[:, 0], e[:, 1], "--", color=GREY, lw=1.5, label="robot's belief")
        ax.set_title(f"{label}: goal error {np.linalg.norm(t[-1, :2] - GOAL):.2f} m" + (", hits a wall" if m.hits(world, t) else ""), fontsize=11)
        ax.legend(loc="lower right", fontsize=8)
    for label, color in (("No fix", ORANGE), ("With landmark fix", BLUE)):
        t, e = runs[label]
        axes[2].plot(np.arange(len(t)) * 0.05, np.linalg.norm(t[:, :2] - e[:, :2], axis=1), color=color, label=label)
    axes[2].set_xlabel("time (s)")
    axes[2].set_ylabel("belief minus truth (m)")
    axes[2].set_title("Drift grows, the fix resets it", fontsize=11)
    axes[2].legend()
    axes[2].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig-nav-drift.png", dpi=90)
    print(OUT)


if __name__ == "__main__":
    main()
