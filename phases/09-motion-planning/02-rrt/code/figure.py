# 레슨 09/02 그림: RRT 트리와 경로, shortcut 뒤의 경로, 시드 20개에 걸친 경로 길이를 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("rrt_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
START, GOAL = np.array([1.0, 1.0]), np.array([9.0, 9.0])
BOUNDS = (np.zeros(2), np.full(2, 10.0))
OBS = [(np.array([5.0, 5.0]), 2.0), (np.array([3.0, 7.5]), 1.2), (np.array([7.5, 3.0]), 1.2)]
OUT = HERE.parent / "assets"


def world(ax, title):
    for c, r in OBS:
        ax.add_patch(Circle(c, r, color=GREY, alpha=0.35))
    ax.plot(*START, "s", color="black", ms=11)
    ax.plot(*GOAL, "*", color="black", ms=17)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=15)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")


def main():
    OUT.mkdir(exist_ok=True)
    nodes, parent, path = m.rrt(START, GOAL, OBS, BOUNDS, seed=0)
    short = m.shortcut(path, OBS, seed=0)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.8))
    world(a1, f"RRT: {len(nodes)} nodes, path {m.path_length(path):.1f} m")
    for i in range(1, len(nodes)):
        a1.plot(*zip(nodes[i], nodes[parent[i]]), color="#999999", lw=1)
    P = np.array(path)
    a1.plot(P[:, 0], P[:, 1], color=BLUE, lw=3.2)
    world(a2, f"After shortcutting: {m.path_length(short):.1f} m")
    a2.plot(P[:, 0], P[:, 1], color=BLUE, lw=2, alpha=0.4, label="raw path")
    S = np.array(short)
    a2.plot(S[:, 0], S[:, 1], "o-", color=ORANGE, lw=3.2, label="shortcut path")
    a2.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "fig-rrt-tree-path.png", dpi=100)

    raw, sh = [], []
    for s in range(20):
        _, _, p = m.rrt(START, GOAL, OBS, BOUNDS, seed=s)
        raw.append(m.path_length(p))
        sh.append(m.path_length(m.shortcut(p, OBS, seed=s)))
    fig, ax = plt.subplots(figsize=(8, 5.6))
    ax.plot(range(20), raw, "o", color=BLUE, label="raw RRT path")
    ax.plot(range(20), sh, "s", color=ORANGE, label="after shortcutting")
    ax.axhline(np.linalg.norm(GOAL - START), color=GREY, ls="--", label="straight line (blocked)")
    ax.set_xlabel("random seed")
    ax.set_ylabel("path length (m)")
    ax.set_title("Shortcutting trims every seed")
    ax.set_xticks(range(0, 20, 2))
    ax.set_ylim(10.5, 23)
    ax.legend(loc="upper right", ncol=1)
    fig.tight_layout()
    fig.savefig(OUT / "fig-rrt-lengths.png", dpi=100)
    print(OUT)


if __name__ == "__main__":
    main()
