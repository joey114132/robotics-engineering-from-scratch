# 레슨 07/02 그림: 추정·측정·2시그마 띠와, 반복 실험의 실제 오차가 sqrt(P) 와 맞는 모습을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("kalman_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    steps, runs = 60, 4000
    truth, zs = m.simulate(steps, runs, np.random.default_rng(7))
    xs, Ps = m.kalman(zs)
    k = np.arange(steps)
    sig = np.sqrt(Ps[:, 0, 0])
    r = 3  # one run to draw
    w = slice(15, 45)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6))
    a1.fill_between(k[w], xs[w, 0, r] - 2 * sig[w], xs[w, 0, r] + 2 * sig[w], color=BLUE, alpha=0.2, label="estimate +/- 2 sigma")
    a1.plot(k[w], zs[w, r], "o", color=ORANGE, ms=5, label="measurement")
    a1.plot(k[w], xs[w, 0, r], color=BLUE, label="estimate")
    a1.plot(k[w], truth[w, 0, r], "--", color="black", lw=1.6, label="truth")
    a1.set_xlabel("time step")
    a1.set_ylabel("position (m)")
    a1.set_title("Estimate hugs the truth, band is honest")
    a1.legend(loc="upper left", framealpha=0.95)
    emp = np.sqrt(np.mean((xs[:, 0] - truth[:, 0]) ** 2, axis=1))
    a2.axhline(2.0, color=ORANGE, lw=2, label="raw measurement noise")
    a2.plot(k, emp, "o", color=BLUE, ms=4, label="actual error, 4000 runs")
    a2.plot(k, sig, color="black", ls="--", label="filter's own sqrt(P)")
    a2.set_xlabel("time step")
    a2.set_ylabel("position error, std (m)")
    a2.set_title("The filter knows how wrong it is")
    a2.set_ylim(0, 2.4)
    a2.legend(loc="lower right", framealpha=0.95)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-kalman-band.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
