# 레슨 01/05 그림: pitch 가 90도를 지날 때 보고되는 각도의 점프와, 필요한 Euler rate 가 커지는 모습을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("euler_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
D = np.pi / 180


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    true = np.linspace(60, 120, 241)
    ang = np.array([m.R_to_euler(m.euler_to_R(0.0, t * D, 0.0))[:3] for t in true]) / D
    ax1.plot(true, ang[:, 1], color=GREY, lw=2, label="pitch")
    ax1.plot(true, ang[:, 0], color=ORANGE, lw=2, label="roll")
    ax1.plot(true, ang[:, 2], color=BLUE, lw=2, ls="--", label="yaw")
    ax1.axvline(90, color=GREY, lw=1, ls=":")
    ax1.set_xlabel("true pitch of the tool (deg)")
    ax1.set_ylabel("reported angle (deg)")
    ax1.set_title("One smooth turn, a 180 deg jump")
    ax1.legend(loc="center left")
    ax1.grid(alpha=0.3)

    p = np.linspace(0, 89.9, 400)
    need = [np.linalg.norm(m.euler_rates([1.0, 0, 0], t * D, 0.0)) for t in p]
    ax2.semilogy(p, need, color=ORANGE, lw=2, label="|Euler rates| for 1 rad/s")
    ax2.semilogy(p, 1 / np.cos(p * D), color=GREY, lw=1.5, ls="--", label="1 / cos(pitch)")
    ax2.set_xlabel("pitch (deg)")
    ax2.set_ylabel("Euler rate norm (rad/s)")
    ax2.set_title("Same spin, rates blow up near 90 deg")
    ax2.legend(loc="upper left")
    ax2.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-gimbal-lock.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
