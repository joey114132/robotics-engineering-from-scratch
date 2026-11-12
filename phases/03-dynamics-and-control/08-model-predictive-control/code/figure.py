# 레슨 03/08 그림: 한계를 자른 LQR 과 MPC 의 위치 응답, 그리고 MPC 가 한 시점에서 내다본 예측 경로를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("mpc_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

DT, UMAX, STEPS = 0.1, 0.5, 120
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    A, B = m.double_integrator(DT)
    Q, R = np.diag([1.0, 0.1]), np.array([[0.1]])
    K, _ = m.riccati(A, B, Q, R)
    x0 = np.array([4.0, 0.0])
    x, clip = x0.copy(), []
    for _ in range(STEPS):
        clip.append(x[0])
        x = A @ x + B[:, 0] * np.clip(-(K @ x)[0], -UMAX, UMAX)
    log = []
    xs, _, _ = m.simulate(x0, STEPS, A, B, Q, R, 20, UMAX, plan_log=log)
    t = np.arange(STEPS) * DT
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    ax1.plot(t, clip, color=ORANGE, lw=2, label=f"LQR clipped at {UMAX} m/s^2 (min {min(clip):.2f} m)")
    ax1.plot(t, xs[:, 0], color=BLUE, lw=2, label=f"MPC, N = 20 (min {xs[:, 0].min():.2f} m)")
    ax1.axhline(0, color=GREY, lw=1)
    ax1.set(xlabel="time (s)", ylabel="position (m)", title="Knowing the limit removes the overshoot")
    ax1.legend(loc="upper right", fontsize=9)
    ax1.grid(alpha=0.3)
    k = 40
    xk, U = log[k]
    Phi, Gam = m.prediction(A, B, 20)
    pred = (Phi @ xk + Gam @ U)[0::2]
    ax2.plot(t, xs[:, 0], color=BLUE, lw=2, label="actual MPC path")
    ax2.plot(t[k] + DT * np.arange(1, 21), pred, "o--", color=ORANGE, ms=4, label=f"plan made at t = {t[k]:.1f} s")
    ax2.plot(t[k], xk[0], "ks", ms=8)
    ax2.set(xlabel="time (s)", ylabel="position (m)", title="Plan ahead, use only step one")
    ax2.legend(loc="upper right", fontsize=9)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-mpc-vs-clip.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
