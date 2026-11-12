# 레슨 03/09 그림: V 의 등위선 위에 상태 흐름 화살표를 그려 dV/dt 부호를 보이고, 지연이 V 를 키우는 모습을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lyap_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
OUT = HERE.parent / "assets"


def level_sets():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6), sharey=True)
    th, w = np.linspace(-3, 3, 200), np.linspace(-8, 8, 200)
    TH, W = np.meshgrid(th, w)
    for ax, p, title in ((axes[0], m.DEFAULT, "kd = 2: no arrow points outward"), (axes[1], dict(m.DEFAULT, kd=-1.0), "kd = -1: arrows cross outward")):
        Z = np.array([[m.V(np.array([a, b]), p) for a in th] for b in w])
        ax.contour(TH, W, Z, levels=[2, 6, 12, 20, 30], colors=GREY, linewidths=1)
        gx, gy = np.meshgrid(np.linspace(-2.8, 2.8, 15), np.linspace(-7.5, 7.5, 13))
        for a, b in zip(gx.ravel(), gy.ravel()):
            x = np.array([a, b])
            d = m.f(x, p)
            n = np.hypot(d[0] / 6, d[1] / 16)
            bad = m.vdot(x, p) > 1e-6
            ax.arrow(a, b, 0.22 * d[0] / 6 / n, 0.22 * 2.7 * d[1] / 16 / n, color=ORANGE if bad else BLUE, head_width=0.07, head_length=0.28, lw=0.8)
        ax.set(xlabel="angle (rad)", title=title)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-8, 8)
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("rate (rad/s)")
    fig.tight_layout()
    fig.savefig(OUT / "fig-lyapunov-level-sets.png", dpi=100)


def delay():
    fig, ax = plt.subplots(figsize=(8, 5.2))
    p = dict(m.DEFAULT, kd=5.0)
    t = np.arange(10000) * 1e-3
    for d, color, ls in ((0.0, BLUE, "-"), (0.1, GREY, "--"), (0.3, ORANGE, "-")):
        v = m.simulate(p, [1.0, 0.0], T=10.0, delay=d)
        ax.semilogy(t, np.maximum(v, 1e-6), ls, color=color, lw=2, label=f"rate seen {d * 1000:.0f} ms late")
    ax.set(xlabel="time (s)", ylabel="V (J/kg, log scale)", title="A late rate signal turns a falling V into a rising one")
    ax.set_ylim(1e-6, 1e8)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "fig-lyapunov-delay.png", dpi=100)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    level_sets()
    delay()
    print(OUT)
