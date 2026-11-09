# 레슨 12/01 그림: 실제와 시뮬의 궤적, 시간에 따른 어긋남, 빠진 효과별 비용을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("sim_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY, GREEN = "#0072B2", "#D55E00", "#555555", "#009E73"
T = 6.0


def main():
    t = np.arange(int(T / m.DT)) * m.DT
    real = m.measured(m.REAL, m.command, T)
    cases = {"friction": dict(b=0.0, c=0.0), "motor lag": dict(Tm=0.0), "sensor delay": dict(delay=0.0)}
    all3 = {k: v for d in cases.values() for k, v in d.items()}
    allsim = m.measured({**m.REAL, **all3}, m.command, T)
    costs = m.effect_costs(m.REAL, m.command, T)

    fig = plt.figure(figsize=(12, 6.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1])
    ax1, ax2, ax3 = fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    ax1.plot(t, real, color=BLUE, label="real plant (friction, lag, delay)")
    ax1.plot(t, allsim, color=ORANGE, label="simulated plant (none of the three)")
    ax1.set_ylabel("measured angle (rad)")
    ax1.set_xlabel("time (s)")
    ax1.set_title("Same open-loop commands, two plants: the trajectories drift apart")
    ax1.set_ylim(-1.8, 2.4)
    ax1.legend(loc="upper left", ncol=2)
    for (name, over), col in zip(cases.items(), (ORANGE, GREEN, GREY)):
        ax2.plot(t, np.abs(m.measured({**m.REAL, **over}, m.command, T) - real), color=col, label=f"only {name} missing")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("|angle error| (rad)")
    ax2.set_title("Error over time")
    ax2.legend(loc="upper left", fontsize=11)
    names = list(costs)
    ax3.bar(names, [costs[n] for n in names], color=[ORANGE, GREEN, GREY, "#999999"])
    ax3.set_ylabel("RMS angle error (rad)")
    ax3.set_title("Friction costs the most here")
    ax3.tick_params(axis="x", labelsize=11)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-divergence.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
