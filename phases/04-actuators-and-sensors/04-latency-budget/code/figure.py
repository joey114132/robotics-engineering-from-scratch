# 레슨 04/04 그림: kd 에 따른 delay margin 과 지연 예산, 지연에 따른 시뮬레이션 응답을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lat_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

J, KP, KD = 0.05, 100.0, 2.0
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
BUDGET = m.total_latency({"sensor": 0.5e-3, "filter": 2e-3, "bus": 1e-3, "compute": 0.5e-3, "drive": 1e-3}, 1e-3)


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    kds = np.geomspace(0.3, 100, 200)
    dm = np.array([m.delay_margin(KP, k, J) for k in kds]) * 1e3
    ax1.plot(kds, dm, color=BLUE, lw=2.5, label="delay margin of the loop")
    ax1.axhline(BUDGET * 1e3, color=ORANGE, lw=2, ls="--", label=f"loop delay {BUDGET * 1e3:.1f} ms")
    kmax = m.kd_max(BUDGET, KP, J)
    ax1.axvline(kmax, color=GREY, lw=1, ls=":")
    ax1.fill_between(kds, 0, dm, where=dm < BUDGET * 1e3, color=ORANGE, alpha=0.2)
    ax1.annotate(f"kd above {kmax:.0f}\nfails", (kmax * 1.1, 6.2), fontsize=10, color=GREY)
    ax1.annotate("too little kd\nalso fails", (0.32, 3.6), fontsize=10, color=GREY)
    ax1.set_xscale("log")
    ax1.set_xlabel("derivative gain kd (Nm s/rad), kp = 100")
    ax1.set_ylabel("delay margin (ms)")
    ax1.set_title("Delay forces kd down", fontsize=13)
    ax1.legend(fontsize=9, loc="upper right")
    ax1.grid(alpha=0.3, which="both")

    dmk = m.delay_margin(KP, KD, J)
    for f, color, ls in ((0.0, GREY, "-"), (0.6, BLUE, "-"), (1.5, ORANGE, "-")):
        a = m.simulate(KP, KD, J, f * dmk, T=0.8)
        ax2.plot(np.arange(len(a)) * 1e-4, a, ls, color=color, lw=2.2, label=f"delay = {f:.1f} x margin ({f * dmk * 1e3:.1f} ms)")
    ax2.set_ylim(-0.15, 0.15)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("joint error (rad), kd = 2")
    ax2.set_title("Past the margin the error grows (curve leaves the plot)", fontsize=12)
    ax2.legend(fontsize=9, loc="upper right")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-latency-margin.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, kmax)


if __name__ == "__main__":
    main()
