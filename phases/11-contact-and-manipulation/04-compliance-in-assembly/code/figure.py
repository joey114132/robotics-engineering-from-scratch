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
    for kx, color, ls in ((1e3, BLUE, "-"), (1e4, GREY, "-"), (1e5, ORANGE, "-")):
        r = m.insert(dict(m.P0, kx=kx))
        z = r["zt"] * 1e3
        ax1.plot(z, r["N1"], ls, color=color, lw=2, label=f"kx = {kx:g} N/m")
        ax2.plot(z, r["Fx"], ls, color=color, lw=2)
        if r["jam"]:
            for ax, y in ((ax1, r["N1"][-1]), (ax2, r["Fx"][-1])):
                ax.plot(r["jam"] * 1e3, y, "X", color=color, ms=13)
                ax.annotate("jam", (r["jam"] * 1e3, y), xytext=(-40, 10), textcoords="offset points", color=color)
    ax1.set_yscale("log")
    ax2.set_yscale("symlog", linthresh=1.0)
    ax2.axhline(0, color=GREY, lw=1)
    ax1.set_xlabel("tip depth (mm)")
    ax2.set_xlabel("tip depth (mm)")
    ax1.set_ylabel("tip contact normal force N1 (N)")
    ax2.set_ylabel("wrist side force Fx (N, signed)")
    ax1.set_title("Wall force at the tip follows the wrist side force", fontsize=12)
    ax2.set_title("Side force is about kx times the misalignment", fontsize=12)
    ax1.legend(loc="upper left")
    for ax in (ax1, ax2):
        ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "fig-contact-forces.png", dpi=100)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    jam_map()
    forces()
    print(OUT)
