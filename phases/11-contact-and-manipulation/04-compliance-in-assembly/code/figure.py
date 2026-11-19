# 레슨 11/04 그림: 손목 강성 x 횡 오프셋 jam 지도와 삽입 깊이에 따른 접촉력을 PNG 두 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("assembly_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
OUT = HERE.parent / "assets"


def jam_map():
    kx = np.logspace(1, 5.5, 28)
    e = np.linspace(0, 3e-3, 25)
    grid = np.array([[m.insert(dict(m.P0, kx=k, e=x), dz=2e-4)["jam"] is not None for k in kx] for x in e])
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.pcolormesh(kx, e * 1e3, grid, cmap=ListedColormap([BLUE, ORANGE]), shading="nearest", alpha=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("wrist lateral stiffness kx (N/m)")
    ax.set_ylabel("lateral offset e (mm)")
    ax.set_title("Orange = jams, blue = inserts (mu = 0.4, tilt 3 deg)", fontsize=12)
    ax.text(15, 2.6, "soft wrist gives way", color="white", fontsize=12, fontweight="bold")
    ax.text(1.2e4, 2.6, "stiff + offset: jam", color="white", fontsize=12, fontweight="bold")
    ax.text(15, 0.3, "small offset inserts even with a stiff wrist", color="white", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "fig-jam-map.png", dpi=100)


def forces():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))
    for kx, color in ((1e3, BLUE), (1e4, GREY), (1e5, ORANGE)):
        r = m.insert(dict(m.P0, kx=kx))
        z = r["zt"] * 1e3
        wall = np.maximum(r["N1"], r["N2"])
        ax1.plot(z, wall, color=color, lw=2, label=f"kx = {kx:g} N/m")
        ax2.plot(z, r["Fx"], color=color, lw=2)
        if r["jam"]:
            for ax, y in ((ax1, wall[-1]), (ax2, r["Fx"][-1])):
                ax.plot(r["jam"] * 1e3, y, "X", color=color, ms=13)
                ax.annotate("jam", (r["jam"] * 1e3, y), xytext=(-48, -4), textcoords="offset points", color=color)
    ax2.axhline(0, color=GREY, lw=1)
    ax1.set_xlabel("tip depth (mm)")
    ax2.set_xlabel("tip depth (mm)")
    ax1.set_ylabel("largest wall force (N)")
    ax2.set_ylabel("wrist side force Fx (N, signed)")
    ax1.set_title("Wall force grows once the edge catches the peg", fontsize=12)
    ax2.set_title("A stiff wrist's side force climbs as the hole narrows", fontsize=12)
    ax1.legend(loc="upper left")
    for ax in (ax1, ax2):
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig-contact-forces.png", dpi=100)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    jam_map()
    forces()
    print(OUT)
