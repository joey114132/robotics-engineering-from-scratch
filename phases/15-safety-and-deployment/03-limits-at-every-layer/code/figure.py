# 레슨 15/03 그림: 두 구성의 계층별 한계 막대와 기준 궤적 대비 관절 궤적을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lim_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
ASSETS = HERE.parent / "assets"


def stack():
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.6))
    units = dict(pos="position limit (rad)", vel="speed limit (rad/s)", tau="torque limit (Nm)")
    x = np.arange(3)
    for ax, q in zip(axs, m.QUANTITIES):
        for off, L, c, lab in ((-0.2, m.ALIGNED, BLUE, "aligned"), (0.2, m.MISMATCHED, ORANGE, "mismatched")):
            vals = [L[n][q] if L[n][q] is not None else np.nan for n in m.LAYERS]
            ax.bar(x + off, vals, 0.38, color=c, label=lab)
        ax.set_xticks(x, m.LAYERS)
        ax.set_ylabel(units[q])
        ax.grid(alpha=0.3, axis="y")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2)
    axs[1].set_title("Orange: controller allows 3.0, drive only 1.5")
    axs[2].text(0, 0.4, "planner sets\nno torque limit", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(ASSETS / "fig-limit-stack.png", dpi=100)


def lag():
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    t = np.arange(2500) * 1e-3
    for ax, (name, L, c) in zip(axs, (("aligned", m.ALIGNED, BLUE), ("mismatched", m.MISMATCHED, ORANGE))):
        r = m.simulate(L)
        ax.plot(t, r["trace"][:, 0], color=GREY, ls="--", lw=1.8, label="planner reference")
        ax.plot(t, r["trace"][:, 1], color=c, lw=2.2, label="joint")
        ax.set_title(f"{name}: peak lag {r['peak_err']:.2f} rad")
        ax.set_xlabel("time (s)")
        ax.grid(alpha=0.3)
        ax.legend(loc="lower right")
    axs[0].set_ylabel("joint angle (rad)")
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-limit-lag.png", dpi=100)


if __name__ == "__main__":
    stack()
    lag()
