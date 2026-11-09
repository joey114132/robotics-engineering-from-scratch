# 레슨 04/03 그림: 같은 저속 ramp 를 두 루프 주기로 잰 속도, 그리고 창 길이에 따른 노이즈와 지연을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("enc_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

CPR, W0 = 4096, 0.1
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def ramp(fs, T):
    t = np.arange(int(T * fs) + 1) / fs
    return t, m.counts(W0 * t, CPR)


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    for fs, color, lab in ((1000.0, ORANGE, "1 kHz loop"), (100.0, BLUE, "100 Hz loop")):
        t, c = ramp(fs, 0.3)
        ax1.step(t[1:], m.diff_velocity(c, CPR, 1 / fs), where="post", color=color, lw=1.6, label=lab)
    ax1.axhline(W0, color=GREY, ls="--", lw=1.5, label="true speed 0.1 rad/s")
    ax1.set_ylim(-0.1, 2.1)
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("measured velocity (rad/s)")
    ax1.set_title("Same slow ramp, 1 kHz spikes vs 100 Hz steps", fontsize=13)
    ax1.legend(fontsize=9, loc="upper right")
    ax1.grid(alpha=0.3)

    _, c = ramp(1000.0, 10.0)
    ns = np.arange(1, 41)
    stds = [m.window_velocity(c, CPR, 1e-3, n).std() for n in ns]
    ax2.plot(ns, stds, "o-", color=BLUE, lw=2, ms=4)
    ax2.set_xlabel("window length n (samples at 1 kHz)")
    ax2.set_ylabel("velocity noise, std (rad/s)", color=BLUE)
    ax2.set_title("Longer window: less noise, more delay", fontsize=13)
    ax2.grid(alpha=0.3)
    ax3 = ax2.twinx()
    ax3.plot(ns, [m.window_lag(n, 1e-3) * 1e3 for n in ns], "-", color=ORANGE, lw=2.4)
    ax3.set_ylabel("delay n*dt/2 (ms)", color=ORANGE)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-encoder-velocity.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
