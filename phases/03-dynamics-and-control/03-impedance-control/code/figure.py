# 레슨 03/03 그림: 감쇠비별 push 응답과 강성별 처짐을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("imp_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    J, F, dt = 1.0, 2.0, 1e-3
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    t = np.arange(3000) * dt
    for zeta, c in ((0.2, ORANGE), (0.7, BLUE), (1.0, GREY)):
        q = m.simulate(J, 100.0, m.damping_for_zeta(100.0, J, zeta), F, dt, 3000)
        ax1.plot(t, np.degrees(q), color=c, lw=2, label=f"zeta = {zeta}")
    ax1.axhline(np.degrees(F / 100.0), color="k", ls=":", lw=1)
    ax1.text(1.6, np.degrees(F / 100.0) + 0.12, "F / K", fontsize=10)
    ax1.set_xlabel("time after the push starts (s)")
    ax1.set_ylabel("joint deflection (deg)")
    ax1.set_title("Same K: damping sets the overshoot", fontsize=13)
    ax1.legend(loc="lower right", fontsize=9)
    ax1.grid(alpha=0.3)
    K = np.array([25, 50, 100, 200, 400.0])
    ax2.plot(K, np.degrees(F / K), "o-", color=BLUE, lw=2)
    ax2.set_xlabel("stiffness K (Nm/rad)")
    ax2.set_ylabel("steady deflection under F = 2 Nm (deg)")
    ax2.set_title("Double K, half the deflection", fontsize=13)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-impedance-response.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
