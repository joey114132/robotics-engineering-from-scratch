# 레슨 00/03 그림: 도와 라디안의 대응 점들, 큰 각도를 한 바퀴 안으로 감은 톱니 모양을 그린다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("angles_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2))
    deg = np.linspace(0, 360, 361)
    a1.plot(deg, [m.deg_to_rad(d) for d in deg], color=BLUE, lw=2.5)
    for d, name in ((90, "quarter"), (180, "half"), (360, "full")):
        r = m.deg_to_rad(d)
        a1.plot([d], [r], "o", color=ORANGE, ms=9)
        a1.annotate(f"{name} turn: {d} deg = {r:.2f} rad", (d, r), textcoords="offset points", xytext=(-175 if d == 360 else 10, -4 if d == 360 else -16), fontsize=10)
    a1.set_xlabel("angle (degrees)")
    a1.set_ylabel("angle (radians)")
    a1.set_title("A full turn is 360 degrees or 6.28 radians", fontsize=13)
    a1.grid(alpha=0.3)
    big = np.linspace(-360, 900, 1261)
    a2.plot(big, [m.rad_to_deg(m.wrap_turn(m.deg_to_rad(d))) for d in big], color=BLUE, lw=2)
    a2.plot([450], [90], "o", color=ORANGE, ms=9)
    a2.annotate("450 wraps to 90", (450, 90), textcoords="offset points", xytext=(10, -22), fontsize=11)
    a2.axhline(360, color=GREY, ls="--", lw=1)
    a2.set_xlabel("angle you gave (degrees)")
    a2.set_ylabel("wrapped angle (degrees)")
    a2.set_title("Wrapping keeps every angle within one turn", fontsize=13)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-conversion-and-wrap.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, "full turn rad", round(m.deg_to_rad(360), 2))


if __name__ == "__main__":
    main()
