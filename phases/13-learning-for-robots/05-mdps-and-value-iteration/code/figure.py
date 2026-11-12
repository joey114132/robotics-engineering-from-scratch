# 레슨 13/05 그림: 목표에서 퍼져 나가는 value 파문과 sweep 당 gamma 로 줄어드는 오차를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("mdp_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

LAYOUT = ["......G", ".##.##.", "...X...", ".#.##..", "......."]
GAMMA, BLUE, ORANGE, GREY = 0.9, "#0072B2", "#D55E00", "#555555"


def grid(model, V):
    img = np.full((len(LAYOUT), len(LAYOUT[0])), np.nan)
    for (i, j), s in model.idx.items():
        img[i, j] = V[s]
    return img


def main():
    model = m.gridworld(LAYOUT, slip=0.2)
    V, hist, sweeps = m.value_iteration(model, GAMMA)
    pi = m.greedy(model, V, GAMMA)
    fig = plt.figure(figsize=(12, 6.75))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.15, 1])
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("#222222")
    for col, k in enumerate((1, 4, 10, sweeps)):
        ax = fig.add_subplot(gs[0, col])
        ax.imshow(grid(model, hist[k]), cmap=cmap, vmin=-1, vmax=1)
        ax.set_title(f"after sweep {k}" if k < sweeps else f"converged ({sweeps} sweeps)", fontsize=11)
        ax.set_xticks([])
        ax.set_yticks([])
        for (i, j), s in model.idx.items():
            if k == sweeps and not model.term[s]:
                ax.text(j, i, "^v<>"[pi[s]], ha="center", va="center", color="white", fontsize=15, fontweight="bold")
            elif model.term[s]:
                ax.text(j, i, "G" if LAYOUT[i][j] == "G" else "X", ha="center", va="center", color="white", fontsize=13, fontweight="bold")
    ax = fig.add_subplot(gs[1, :])
    err = [np.abs(h - V).max() for h in hist[:-1]]  # the last sweep is V itself, error 0
    ax.semilogy(range(len(err)), np.maximum(err, 1e-12), "o-", color=BLUE, ms=4, label="max error of V after k sweeps")
    ax.semilogy(range(len(err)), GAMMA ** np.arange(len(err)) * np.abs(V).max(), "--", color=GREY, label="bound: gamma^k * max |V*|")
    ax.set_xlabel("sweep k")
    ax.set_ylabel("max error vs converged V")
    ax.set_ylim(1e-8, 2)
    ax.set_title("Value spreads outward from the goal, and the error never beats the bound")
    ax.legend(loc="lower left")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-value-ripple.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
