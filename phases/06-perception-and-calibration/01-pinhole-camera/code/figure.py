# 레슨 06/01 그림: 거리에 따른 위치 오차와 가장자리 픽셀에서 배경 깊이를 읽었을 때의 옆 이동량
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pin_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

K = dict(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    z = np.linspace(0.3, 4.0, 60)
    px = [m.position_error([320.0, 240.0], zi, 0.0, 0.5, **K)["total"] * 1000 for zi in z]
    dep = [m.position_error([320.0, 240.0], zi, 0.01 * zi, 0.0, **K)["total"] * 1000 for zi in z]
    ax1.plot(z, px, color=BLUE, lw=2.5, label="0.5 px pixel error")
    ax1.plot(z, dep, color=ORANGE, lw=2.5, label="1% depth error")
    ax1.set_xlabel("distance z (m)")
    ax1.set_ylabel("3D position error (mm)")
    ax1.set_title("Both errors grow in proportion to distance")
    ax1.legend(loc="upper left")
    ax1.grid(alpha=0.3)

    u = np.linspace(320, 620, 60)
    lat = [m.lateral_from_depth_error(ui, 0.15, K["fx"], K["cx"]) * 1000 for ui in u]
    ax2.plot(u - 320, lat, color=ORANGE, lw=2.5, label="depth read 0.15 m too far (table instead of rim)")
    ax2.axhline(10, color=GREY, ls="--", lw=1)
    ax2.text(5, 12, "10 mm reference line", color=GREY, fontsize=10)
    ax2.set_ylim(-3, 100)
    ax2.set_xlabel("pixel distance from the principal point (px)")
    ax2.set_ylabel("sideways error of the target (mm)")
    ax2.set_title("Off-axis pixels pay more for a wrong depth")
    ax2.legend(loc="upper left")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-pinhole-error.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
