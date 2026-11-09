# 레슨 03/01 그림: r 값별 틱당 속도 변화와 인자 1-r 의 구간을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("samp_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY, RED = "#0072B2", "#D55E00", "#555555", "#CC79A7"


def main():
    J, dt = 0.02, 0.001
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    for r, c, ls in ((0.5, BLUE, "-"), (1.0, GREY, "--"), (1.5, ORANGE, "-"), (1.9, RED, "-")):
        v = m.simulate_damper(1.0, J, r * J / dt, dt, 12)
        ax1.plot(v, "o" + ls, color=c, lw=2, label=f"r = {r}")
    ax1.axhline(0, color=GREY, lw=1)
    ax1.set_xlabel("control tick")
    ax1.set_ylabel("velocity (rad/s, starts at 1)")
    ax1.set_title("r = 1 stops at once, r > 1 flips sign", fontsize=13)
    ax1.legend(loc="upper right", fontsize=9)
    ax1.grid(alpha=0.3)
    r = np.linspace(0, 3, 301)
    ax2.plot(r, 1 - r, color=BLUE, lw=2)
    ax2.axhspan(-1, 1, color=BLUE, alpha=0.08)
    for x, lab in ((1, "r = 1"), (2, "r = 2")):
        ax2.axvline(x, color=GREY, ls=":")
        ax2.text(x + 0.03, 1.1, lab, fontsize=10)
    ax2.set_ylim(-2.2, 1.3)
    ax2.set_xlabel("r = dt*kd/J (dimensionless)")
    ax2.set_ylabel("velocity factor per tick, 1 - r")
    ax2.set_title("Shaded band: |factor| < 1, velocity shrinks", fontsize=13)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-r-response.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
