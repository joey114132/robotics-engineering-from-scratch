# 레슨 09/05 그림: 같은 지도에서 Dijkstra, A*, 과대추정 A* 의 확장 영역과 경로, 가중치에 따른 확장 수와 경로 비용을 PNG 한 장으로 만든다
import importlib.util
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("astar_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
sys.path.insert(0, str(HERE / "tests"))
from test_grid_search_dijkstra_to_astar import TRAP  # noqa: E402

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def panel(ax, grid, s, t, w, title):
    path, exp = m.search(grid, s, t, w)
    img = np.zeros(grid.shape)
    img[grid] = -1
    for c in exp:
        img[c] = 1
    ax.imshow(img, cmap=matplotlib.colors.ListedColormap([GREY, "white", "#9ecae1"]), vmin=-1, vmax=1)
    ax.plot(*zip(*[(c[1], c[0]) for c in path]), color=ORANGE, lw=3)
    ax.plot(s[1], s[0], "o", color=BLUE, ms=9)
    ax.plot(t[1], t[0], "*", color=ORANGE, ms=14)
    ax.set_title(f"{title}: {len(exp)} cells, path {len(path) - 1}", fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(True)


def main():
    grid, s, t = m.parse(TRAP)
    fig, axes = plt.subplots(2, 2, figsize=(12, 6.7))
    panel(axes[0, 0], grid, s, t, 0.0, "Dijkstra (w=0)")
    panel(axes[0, 1], grid, s, t, 1.0, "A* (w=1)")
    panel(axes[1, 0], grid, s, t, 4.0, "Overestimating (w=4)")
    ax = axes[1, 1]
    ws = np.array([0, 0.5, 1, 1.5, 2, 3, 4, 6, 10])
    res = [m.search(grid, s, t, w) for w in ws]
    ax.plot(ws, [len(e) for _, e in res], "o-", color=BLUE)
    ax.set_xlabel("heuristic weight w")
    ax.set_ylabel("cells expanded", color=BLUE)
    ax2 = ax.twinx()
    ax2.plot(ws, [len(p) - 1 for p, _ in res], "s--", color=ORANGE)
    ax2.set_ylabel("path cost (steps)", color=ORANGE)
    ax2.set_ylim(20, 40)
    ax.set_title("Fewer cells, then a longer path")
    ax.grid(alpha=0.3)
    keys = [plt.Rectangle((0, 0), 1, 1, fc="#9ecae1"), plt.Rectangle((0, 0), 1, 1, fc=GREY), plt.Line2D([0], [0], color=ORANGE, lw=3)]
    fig.legend(keys, ["cell expanded", "wall", "path found"], loc="lower center", ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = HERE.parent / "assets" / "fig-astar-expansions.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
