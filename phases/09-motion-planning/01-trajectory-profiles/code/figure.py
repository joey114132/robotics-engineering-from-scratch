# 레슨 09/01 그림: 세 프로파일의 위치, 속도, 가속도와 샘플 간격에 따른 최대 jerk 를 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("traj_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
Q0, QF, T = 0.0, 1.0, 2.0
OUT = HERE.parent / "assets"


def profiles(t):
    return {"cubic": m.poly(m.cubic(Q0, QF, T), t), "quintic": m.poly(m.quintic(Q0, QF, T), t), "trapezoid": m.trapezoid(Q0, QF, T, 0.5)(t)}


def main():
    OUT.mkdir(exist_ok=True)
    t = np.linspace(0, T, 801)
    style = {"cubic": (ORANGE, "-"), "quintic": (BLUE, "-"), "trapezoid": (GREY, "--")}
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.8))
    for k, (ax, name, unit) in enumerate(zip(axes, ("position", "velocity", "acceleration"), ("rad", "rad/s", "rad/s$^2$"))):
        for label, data in profiles(t).items():
            ax.plot(t, data[k], color=style[label][0], ls=style[label][1], label=label)
        ax.set_xlabel("time (s)")
        ax.set_ylabel(f"{name} ({unit})")
    axes[2].set_title("Cubic and trapezoid\njump at the start", fontsize=15)
    axes[1].set_title("All three: rest to rest", fontsize=15)
    axes[0].set_title("All three reach 1 rad", fontsize=15)
    axes[0].legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "fig-profiles.png", dpi=100)

    fig, ax = plt.subplots(figsize=(8, 5.6))
    dts = np.logspace(-3.3, -1.3, 12)
    for label in ("cubic", "trapezoid", "quintic"):
        j = []
        for dt in dts:
            tt = np.arange(0, T + dt / 2, dt)
            j.append(m.peak_jerk(profiles(tt)[label][2], dt))
        ax.loglog(dts * 1000, j, "o-", color=style[label][0], ls=style[label][1], label=label)
    ax.set_xlabel("sample period dt (ms)")
    ax.set_ylabel("peak finite-difference jerk (rad/s$^3$)")
    ax.set_title("Cubic jerk grows as 1/dt, quintic stays flat")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "fig-jerk-vs-dt.png", dpi=100)
    print(OUT)


if __name__ == "__main__":
    main()
