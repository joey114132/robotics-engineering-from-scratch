# 레슨 11/01 그림: 마찰 원뿔 안의 힘 궤적과 기울기에 따른 슬립 가속도를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("contact_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

MU = 0.5
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    top = 14.0
    ax1.fill_betweenx([0, top], [0, -MU * top], [0, MU * top], color=GREY, alpha=0.12, label=f"friction cone, mu = {MU}")
    ax1.plot([-MU * top, 0, MU * top], [top, 0, top], color=GREY, lw=1.5)
    for deg, color, dy in ((10, BLUE, 8), (22, BLUE, -18), (35, ORANGE, -16)):
        r = m.simulate(np.radians(deg), MU, T=1.5)
        sl = slice(0, 6000)  # first 0.6 s, includes the normal bounce
        ax1.plot(r["ft"][sl], r["fn"][sl], color=color, lw=2, alpha=0.9)
        ax1.plot(r["ft"][-1], r["fn"][-1], "o", color=color, ms=9)
        ax1.annotate(f"{deg} deg " + ("sticks" if abs(r["v"][-1]) < 0.05 else "slides"), (r["ft"][-1], r["fn"][-1]),
                     xytext=(10, dy), textcoords="offset points", color=color)
    ax1.set_xlim(-7, 7)
    ax1.set_ylim(0, top)
    ax1.set_xlabel("tangential force ft on the block (N)")
    ax1.set_ylabel("normal force fn (N)")
    ax1.set_title("Stick = inside the cone, slip = on its edge", fontsize=12)
    ax1.legend(loc="lower right")
    ax1.grid(alpha=0.3)

    tans = np.arange(0.2, 0.95, 0.05)
    i1, i2 = int(0.5 / m.DT), int(1.5 / m.DT)
    acc = []
    for t in tans:
        r = m.simulate(np.arctan(t), MU, T=1.5)
        acc.append((r["v"][i2 - 1] - r["v"][i1]) / ((i2 - 1 - i1) * m.DT))
    grid = np.linspace(0.2, 0.9, 200)
    ax2.plot(grid, [max(0.0, m.slip_accel(np.arctan(t), MU)) for t in grid], color=GREY, lw=2, label="g (sin t - mu cos t), 0 when sticking")
    ax2.plot(tans, acc, "o", color=BLUE, label="simulation")
    ax2.axvline(MU, color=ORANGE, ls="--", label="tan(theta) = mu")
    ax2.set_xlabel("tan(theta)")
    ax2.set_ylabel("acceleration down the slope (m/s^2)")
    ax2.set_title("Sliding starts exactly at tan(theta) = mu", fontsize=12)
    ax2.legend(loc="upper left")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-stick-slip.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
