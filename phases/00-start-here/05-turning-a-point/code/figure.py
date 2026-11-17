# 레슨 00/05 그림: 점 (1, 0)을 여러 각도로 돌린 자리(원 위)와, 돌려도 원점에서의 거리가 그대로임을 보인다
import importlib.util
import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lesson_turning_fig", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.4))
    t = np.linspace(0, 2 * math.pi, 200)
    a1.plot(np.cos(t), np.sin(t), color=GREY, lw=1, ls="--")
    for deg in range(0, 360, 45):
        x, y = m.rotate((1.0, 0.0), math.radians(deg))
        a1.plot(x, y, "o", color=ORANGE if deg else BLUE, ms=9)
        a1.annotate(f"{deg}°", (x, y), textcoords="offset points", xytext=(8, 6), fontsize=10)
    a1.set_aspect("equal")
    a1.set_xlim(-1.4, 1.5)
    a1.set_xlabel("how far across")
    a1.set_ylabel("how far up")
    a1.set_title("The point swings around a circle", fontsize=13)
    a1.grid(alpha=0.3)
    deg = np.arange(0, 361, 5)
    dist = [math.hypot(*m.rotate((1.0, 0.0), math.radians(d))) for d in deg]
    a2.plot(deg, dist, color=BLUE, lw=2.5)
    a2.set_ylim(0, 1.3)
    a2.set_xlabel("turn angle (degrees)")
    a2.set_ylabel("distance from the origin")
    a2.set_title("Turning never changes the distance", fontsize=13)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-turn-circle.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, "distance min/max", round(min(dist), 6), round(max(dist), 6))


if __name__ == "__main__":
    main()
