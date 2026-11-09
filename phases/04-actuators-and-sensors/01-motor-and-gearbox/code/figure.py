# 레슨 04/01 그림: 모터와 출력축의 토크-속도 직선, 감속비별 속도 응답(부하 유무)을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("motor_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

M = dict(kt=0.05, R=1.0, V=24.0)
JR, JL = 2e-5, 2e-3
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    w = np.linspace(0, m.no_load_speed(**M), 50)
    tau = m.motor_torque(w, **M)
    ax1.plot(w, tau, color=BLUE, lw=2.5, label="motor shaft")
    N = 10.0
    ax1.plot(w / N, tau * N, color=ORANGE, lw=2.5, label="output shaft, N = 10")
    ax1.set_xlabel("speed (rad/s)")
    ax1.set_ylabel("torque (Nm)")
    ax1.set_title("Gearbox: torque x N, speed / N", fontsize=13)
    ax1.legend(fontsize=10)
    ax1.grid(alpha=0.3)

    for n, color in ((10.0, ORANGE), (100.0, BLUE)):
        for jl, ls, lab in ((0.0, "--", "no load"), (JL, "-", "with load")):
            t, wm = m.spin_up(n, JR, jl, 0.0, T=0.06, dt=1e-5, **M)
            ax2.plot(t * 1e3, wm / m.no_load_speed(**M), ls, color=color, lw=2.2, label=f"N = {n:.0f}, {lab}")
    ax2.set_xlabel("time (ms)")
    ax2.set_ylabel("motor speed / no-load speed")
    ax2.set_title("At N = 100 the two curves almost coincide", fontsize=13)
    ax2.legend(fontsize=9, loc="lower right")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-motor-gearbox.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
