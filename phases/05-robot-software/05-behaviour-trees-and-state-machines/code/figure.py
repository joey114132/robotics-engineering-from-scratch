# 레슨 05/05 그림: fetch 작업이 tick 마다 어느 노드를 어떤 상태로 돌리는지 격자로 그린다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("bt_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

COLORS = {m.SUCCESS: "#009E73", m.FAILURE: "#D55E00", m.RUNNING: "#E69F00"}
ROWS = ["fetch", "go object", "retry", "grasp", "go bin", "release"]


def main():
    ticks = m.run(m.fetch_task()[0])
    fig, ax = plt.subplots(figsize=(10, 5))
    for t, (log, _) in enumerate(ticks):
        for name, status in log:
            ax.add_patch(plt.Rectangle((t, ROWS.index(name)), 0.9, 0.8, color=COLORS[status]))
    ax.set_xlim(0, len(ticks))
    ax.set_ylim(len(ROWS), 0)
    ax.set_xticks([t + 0.45 for t in range(len(ticks))], [str(t + 1) for t in range(len(ticks))])
    ax.set_yticks([i + 0.4 for i in range(len(ROWS))], ROWS)
    ax.set_xlabel("tick")
    ax.set_title("Two failed grasps are retried; finished nodes are not ticked again")
    ax.legend(handles=[Patch(color=c, label=k) for k, c in COLORS.items()], loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-fetch-ticks.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
