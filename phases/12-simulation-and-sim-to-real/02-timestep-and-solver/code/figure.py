# 레슨 12/02 그림: 진자 에너지 drift 와 stiff 접촉 반발 높이를 time step 에 따라 훑어 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ts_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
CAP = 1.0  # rebound plotted no higher than 10x the drop height


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.4))
    dts = np.logspace(-3.3, -1.3, 14)
    for meth, col, lab in (("euler", ORANGE, "explicit Euler"), ("semi", BLUE, "semi-implicit Euler")):
        ax1.loglog(dts, [m.pendulum_drift(meth, d) for d in dts], "o-", color=col, label=lab)
    ax1.set_xlabel("time step dt (s)")
    ax1.set_ylabel("worst energy drift |E - E0| / E0")
    ax1.set_title("Pendulum, 10 s: semi-implicit stays small")
    ax1.legend(loc="lower right")
    dts2 = np.concatenate([np.logspace(-4, -2.2, 12), [0.012, 0.015, 0.017, 0.019, 0.021]])
    for meth, col, lab in (("euler", ORANGE, "explicit Euler"), ("semi", BLUE, "semi-implicit Euler")):
        ax2.semilogx(dts2, [min(m.rebound_height(meth, d), CAP) for d in dts2], "o-", color=col, label=lab)
    ax2.axhline(m.H0, color=GREY, ls="--", label="correct: drop height 0.1 m")
    ax2.set_ylim(0, CAP * 1.05)
    ax2.set_xlabel("time step dt (s)")
    ax2.set_ylabel("rebound apex (m), clipped at 1 m")
    ax2.set_title("Stiff contact: the answer changes with dt")
    ax2.legend(loc="upper left", fontsize=11)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-dt-sweep.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
