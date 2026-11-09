# 레슨 05/03 그림: period jitter 히스토그램(평균 대 최악)과 jitter 시간선(deadline miss 표시)을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("jitter_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
T = 1e-3


def main():
    s, d = m.simulate(5000, spike_p=0.003)
    st = m.stats(s, d, T)
    jit = (np.diff(s) - T) * 1e6
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6))
    a1.hist(jit, bins=80, color=BLUE)
    a1.set_yscale("log")
    a1.axvline(st["mean_jitter"] * 1e6, color=GREY, ls="--", label=f"mean {abs(st['mean_jitter']) * 1e6:.0f} us")
    a1.axvline(st["p99"] * 1e6, color=GREY, ls=":", label=f"p99 {st['p99'] * 1e6:.0f} us")
    a1.axvline(st["worst"] * 1e6, color=ORANGE, label=f"worst {st['worst'] * 1e6:.0f} us")
    a1.set_xlabel("period minus 1 ms (us)")
    a1.set_ylabel("iterations (log scale)")
    a1.set_title("The mean sits at zero, the tail does not")
    a1.legend(loc="upper right")

    t = s[1:] - s[0]
    a2.plot(t, jit, color=BLUE, lw=0.8)
    miss = np.where(d[:-1] > (np.arange(len(d) - 1) + 1) * T)[0]
    a2.plot(s[miss] - s[0], np.zeros(len(miss)) + jit.max() * 1.05, "v", color=ORANGE, ms=11, label=f"deadline miss ({st['misses']})")
    a2.set_xlabel("time (s)")
    a2.set_ylabel("period minus 1 ms (us)")
    a2.set_title("Rare spikes, the largest miss the deadline")
    a2.set_ylim(-950, 2150)
    a2.legend(loc="upper right")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-jitter.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
