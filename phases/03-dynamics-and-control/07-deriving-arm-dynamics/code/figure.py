# 레슨 03/07 그림: 팔꿈치 각도에 따른 M 성분과 Coriolis 부호를 뒤집었을 때의 에너지 드리프트를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("derive_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

P = dict(m1=1.0, m2=1.5, l1=0.5, lc1=0.2, lc2=0.3, I1=0.03, I2=0.05)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    q2 = np.linspace(-np.pi, np.pi, 61)
    heavy = dict(P, m2=3.0)
    for p, ls, tag in ((P, "-", "m2 = 1.5"), (heavy, "--", "m2 = 3.0")):
        M = np.array([m.mass(np.array([0.0, a]), p) for a in q2])
        ax1.plot(np.degrees(q2), M[:, 0, 0], ls, color=BLUE, lw=2, label=f"M11, {tag}")
        ax1.plot(np.degrees(q2), M[:, 0, 1], ls, color=ORANGE, lw=2, label=f"M12, {tag}")
    ax1.set(xlabel="elbow angle q2 (deg)", ylabel="inertia entry (kg m^2)", title="M(q) changes with the elbow")
    ax1.grid(alpha=0.3)
    ax1.legend(loc="lower center", ncol=2, fontsize=9)
    Ts = np.linspace(0.0, 1.0, 6)
    q0, v0 = np.array([0.3, 1.0]), np.array([2.0, -1.0])
    for sign, color, lab in ((1, BLUE, "correct h"), (-1, ORANGE, "Coriolis sign flipped")):
        d = [m.energy_drift(P, q0, v0, T=T, dt=2e-3, h_sign=sign) if T > 0 else 0.0 for T in Ts]
        ax2.plot(Ts, d, "o-", color=color, lw=2, label=lab)
    ax2.axhline(0, color=GREY, lw=1)
    ax2.set(xlabel="time (s)", ylabel="kinetic energy change (J)", title="Free motion must not gain energy")
    ax2.grid(alpha=0.3)
    ax2.legend(loc="center left")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-inertia-and-energy.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
