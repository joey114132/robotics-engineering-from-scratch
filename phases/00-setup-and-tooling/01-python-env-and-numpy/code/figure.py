# 레슨 00/01 그림: 같은 숫자를 도로 읽을 때와 라디안으로 읽을 때 링크 끝의 x 좌표를 비교한다
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
L = 0.4  # link length in metres


def main():
    q = np.linspace(0, 90, 361)  # sensor values, really degrees
    good = L * np.cos(np.deg2rad(q))
    bad = L * np.cos(q)  # same numbers read as radians
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2))
    a1.plot(q, good * 100, color=BLUE, lw=2.5, label="degrees converted: np.cos(deg2rad(q))")
    a1.plot(q, bad * 100, color=ORANGE, lw=1.5, label="degrees fed as radians: np.cos(q)")
    a1.set_ylim(-62, 46)
    a1.set_xlabel("joint reading (degrees)")
    a1.set_ylabel("link tip x (cm)")
    a1.set_title("Wrong unit, wild answer", fontsize=13)
    a1.legend(loc="lower left", fontsize=9)
    a1.grid(alpha=0.3)
    a2.plot(q, np.abs(bad - good) * 100, color=ORANGE, lw=2)
    a2.axhline(0, color=GREY, lw=1)
    a2.set_xlabel("joint reading (degrees)")
    a2.set_ylabel("position error (cm)")
    a2.set_title("A 0.4 m link ends up almost 80 cm off", fontsize=13)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-degrees-vs-radians.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, "max error cm", round(float(np.abs(bad - good).max() * 100), 1))


if __name__ == "__main__":
    main()
