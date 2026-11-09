# 레슨 10/01 그림: 같은 밀침에서 발목만 쓰면 넘어지고 capture point 로 한 걸음 내디디면 멈추는 모습을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lipm_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

H, HALF_FOOT, V0 = 0.9, 0.05, 0.4
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    for step, color, label in ((False, ORANGE, "ankle only: falls"), (True, BLUE, "step at 0.1 s: recovers")):
        t, x, v = m.fall_or_recover(V0, H, HALF_FOOT, step, T=1.2)
        ax1.plot(t, x, color=color, label=label)
        ax2.plot(t, m.capture_point(x, v, H), color=color, label=label)
    for ax in (ax1, ax2):
        ax.axhspan(-HALF_FOOT, HALF_FOOT, color=GREY, alpha=0.18, label="foot (ZMP limit)")
        ax.axvline(0.1, color=GREY, ls=":", lw=1.5)
        ax.set_xlabel("time (s)")
        ax.set_ylim(-0.1, 0.6)
    ax1.set_ylabel("CoM position x (m)")
    ax1.set_title("Same push, two outcomes")
    ax1.legend(loc="upper left")
    ax2.set_ylabel("capture point xi (m)")
    ax2.set_title("xi freezes once the foot sits on it")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-fall-and-recovery.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
