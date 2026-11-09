# 레슨 10/03 그림: 추력 계단은 높이만 바꾸고 토크 계단은 기울인 뒤에야 옆으로 움직인다는 것을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("quad_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

M, I, TAU = 0.5, 0.004, 0.002
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    hover = m.hover_thrust(M)
    t, s = m.simulate(np.zeros(6), lambda t, s: (1.1 * hover, 0.0), M, I, 1e-3, 1.0)
    ax1.plot(t, s[:, 1] * 100, color=BLUE, label="height z")
    ax1.plot(t, s[:, 0] * 100, color=ORANGE, label="sideways x")
    ax1.set_title("10% more thrust: it only climbs")
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("position (cm)")
    ax1.legend(loc="upper left")

    t, s = m.simulate(np.zeros(6), lambda t, s: (hover, TAU), M, I, 1e-3, 1.0)
    deg, x = np.degrees(s[:, 2]), s[:, 0] * 100
    ax2.plot(t, deg, color=BLUE, label="pitch (deg, left axis)")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("pitch (deg)")
    ax3 = ax2.twinx()
    ax3.plot(t, x, color=ORANGE, label="sideways x (cm, right axis)")
    ax3.set_ylabel("sideways x (cm)")
    ax3.spines["right"].set_visible(True)
    ax3.grid(False)
    t_tilt, t_move = t[np.argmax(deg > 1.0)], t[np.argmax(x > 1.0)]
    ax2.axvline(t_tilt, color=BLUE, ls=":", lw=1.5, label=f"pitch passes 1 deg at {t_tilt:.2f} s")
    ax2.axvline(t_move, color=ORANGE, ls=":", lw=1.5, label=f"x passes 1 cm at {t_move:.2f} s")
    h1, l1 = ax2.get_legend_handles_labels()
    h2, l2 = ax3.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=11)
    ax2.set_title("A torque step: tilt first, then travel")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-tilt-then-move.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, t_tilt, t_move)


if __name__ == "__main__":
    main()
