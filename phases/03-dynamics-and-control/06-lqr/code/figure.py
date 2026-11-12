# 레슨 03/06 그림: R 을 바꿀 때 위치 응답, 입력, 극점이 어떻게 달라지는지 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lqr_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

DT, Q, X0 = 0.05, np.diag([1.0, 0.1]), np.array([1.0, 0.0])
COLORS = {0.01: "#D55E00", 0.1: "#0072B2", 1.0: "#555555", 10.0: "#009E73"}


def main():
    A, B = m.double_integrator(DT)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    t = np.arange(120) * DT
    for r, c in COLORS.items():
        R = np.array([[r]])
        K, _ = m.dare(A, B, Q, R)
        x, u, _ = m.rollout(A, B, K, X0, 120, Q, R)
        ax1.plot(t, x[:, 0], color=c, lw=2, label=f"R = {r:g}")
        ax2.plot(t, u[:, 0], color=c, lw=2, label=f"R = {r:g}, peak {np.abs(u).max():.1f}")
    ax1.set(xlabel="time (s)", ylabel="position error (m)", title="Cheaper effort, faster settling")
    ax2.set(xlabel="time (s)", ylabel="acceleration command u (m/s^2)", title="...and a bigger first push")
    for ax in (ax1, ax2):
        ax.axhline(0, color="#555555", lw=1)
        ax.grid(alpha=0.3)
        ax.legend(loc="lower right" if ax is ax2 else "upper right")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-lqr-r-sweep.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
