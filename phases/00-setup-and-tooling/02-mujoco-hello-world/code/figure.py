# 레슨 00/02 그림: explicit 와 semi-implicit Euler 의 에너지 변화, 시간 간격에 따른 주기 오차를 그린다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pend_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
T0 = 2 * np.pi * np.sqrt(1.0 / m.G)


def main():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2))
    dt = 0.01
    t = np.arange(0, 20.0 + dt / 2, dt)
    for scheme, color, lab in (("explicit", ORANGE, "explicit Euler"), ("semi", BLUE, "semi-implicit Euler")):
        e = m.energy(m.simulate(0.5, dt, 20.0, scheme=scheme), dt)
        a1.plot(t, e / e[0], color=color, lw=2, label=lab)
    a1.set_xlabel("time (s)")
    a1.set_ylabel("energy / initial energy")
    a1.set_title("Explicit Euler pumps energy in", fontsize=13)
    a1.legend(fontsize=10)
    a1.grid(alpha=0.3)
    exact = T0 * (1 + 0.5**2 / 16 + 11 * 0.5**4 / 3072)
    dts = np.array([0.04, 0.02, 0.01, 0.005, 0.0025])
    err = [abs(m.measure_period(m.simulate(0.5, d, 20.0), d) - exact) for d in dts]
    a2.loglog(dts, err, "o-", color=BLUE, lw=2, label="period error")
    a2.loglog(dts, err[0] * (dts / dts[0]) ** 2, "--", color=GREY, label="slope 2 (error ~ dt^2)")
    a2.set_xlabel("time step dt (s)")
    a2.set_ylabel("period error (s)")
    a2.set_title("Halving the step cuts the error about 4x", fontsize=13)
    a2.legend(fontsize=10)
    a2.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-step-size.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, [f"{e:.2e}" for e in err])


if __name__ == "__main__":
    main()
