# 레슨 10/04 그림: 같은 1초 돌풍에서 단일 PD 는 오프셋이 남고 캐스케이드는 0 으로 돌아오는 것을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("cascade_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

I, KP, KD, KI = 0.004, 0.9, 0.084, 0.5
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    gust = lambda t: 0.1 if 0.5 <= t < 1.5 else 0.0
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    for name, ctrl, color in (("single PD", m.pd(KP, KD), ORANGE), ("cascade, rate PI", m.cascade(KP / KD, KD, KI), BLUE)):
        t, th, w, tau = m.simulate(ctrl, I, 1e-3, 3.0, gust, lambda t: 0.0)
        ax1.plot(t, np.degrees(th), color=color, label=name)
        ax2.plot(t, tau * 1000, color=color, label=name)
    for ax in (ax1, ax2):
        ax.axvspan(0.5, 1.5, color=GREY, alpha=0.15, label="gust 0.1 Nm")
        ax.set_xlabel("time (s)")
    ax1.axhline(np.degrees(0.1 / KP), color=ORANGE, ls=":", lw=1.5)
    ax1.text(0.05, np.degrees(0.1 / KP) + 0.25, "d / kp = 6.4 deg", ha="left", color=ORANGE)
    ax1.set_ylabel("pitch error (deg)")
    ax1.set_title("PD holds an offset while the gust lasts")
    ax1.legend(loc="lower left")
    ax2.set_ylabel("torque command (mN m)")
    ax2.set_title("Same torque, no error needed")
    ax2.legend(loc="center right")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-gust-response.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
