# 레슨 10/02 그림: deadbeat 걸음과 60% 로 짧아진 걸음의 무게중심 궤적과 걸음 끝 속도를 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("walk_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

T, H, VT, N = 0.4, 0.9, 0.6, 6
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    for scale, color, label in ((1.0, BLUE, "deadbeat step"), (0.6, ORANGE, "steps 40% too short")):
        r = m.walk(N, T, H, VT, step_scale=scale, x0=-0.05, v0=0.3)
        ax1.plot(r["t"], r["x"], color=color, label=label)
        ax1.plot(np.arange(N) * T, r["feet"][:-1], "s", color=color, ms=8)
        ax2.plot(np.arange(1, N + 1), r["v_end"], "o-", color=color, label=label)
    ax2.axhline(VT, color=GREY, ls="--", lw=1.5, label="target 0.6 m/s")
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("CoM position x (m), squares = foot")
    ax1.set_title("Short steps let the body outrun its feet")
    ax1.legend(loc="upper left")
    ax2.set_xlabel("step number")
    ax2.set_ylabel("speed at end of step (m/s)")
    ax2.set_title("Speed locks on target or runs away")
    ax2.legend(loc="upper left")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-com-over-steps.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
