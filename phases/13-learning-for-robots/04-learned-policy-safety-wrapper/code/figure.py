# 레슨 13/04 그림: 정책의 원시 명령과 래퍼 출력, 위치 궤적, 개입 종류별 횟수를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("wrap_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    bare, wrapped = m.simulate(False), m.simulate(True)
    t = np.arange(len(bare["raw"]))
    fig = plt.figure(figsize=(12, 6.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[2.2, 1])
    ax1, ax2, ax3 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0], sharex=None), fig.add_subplot(gs[:, 1])
    ax1.plot(t, wrapped["raw"], color=ORANGE, lw=1.6, label="policy output (raw)")
    ax1.plot(t, wrapped["out"], color=BLUE, lw=2, label="wrapper output")
    ax1.axhspan(-1, 1, color=GREY, alpha=0.1)
    for e in wrapped["log"]:
        if e["kind"] in ("nonfinite", "hold", "fallback"):
            ax1.plot(e["t"], -2.7, "|", color=GREY, ms=9)
    ax1.set(ylim=(-3, 9), ylabel="command u (units)", xlabel="control tick (dt = 0.05 s)", title="Raw versus wrapped command (grey band = limits, ticks = hold/fallback/NaN)")
    ax1.title.set_fontsize(10)
    ax1.legend(loc="upper right")
    ax1.grid(alpha=0.3)
    ax2.plot(t, bare["x"][1:], color=ORANGE, lw=2, label="without wrapper")
    ax2.plot(t, wrapped["x"][1:], color=BLUE, lw=2, label="with wrapper")
    ax2.axhline(1.0, color=GREY, ls="--", lw=1)
    ax2.set(ylabel="position x (m)", xlabel="control tick (dt = 0.05 s)", title="The wrapper never lets x overshoot its start value")
    ax2.title.set_fontsize(10)
    ax2.legend(loc="upper right")
    ax2.grid(alpha=0.3)
    kinds = ["clip", "rate", "nonfinite", "hold", "fallback"]
    ax3.barh(kinds, [wrapped["counts"].get(k, 0) for k in kinds], color=BLUE)
    ax3.invert_yaxis()
    ax3.set(xlabel="interventions in 140 ticks", title="What the log recorded")
    ax3.title.set_fontsize(10)
    ax3.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-wrapper-containment.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, dict(wrapped["counts"]), round(np.abs(bare["x"]).max(), 2), round(np.abs(wrapped["x"]).max(), 2))


if __name__ == "__main__":
    main()
