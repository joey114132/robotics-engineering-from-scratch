# 레슨 11/02 그림: 강성별 위치 대 힘 제어의 접촉력과 범프 표면 위 하이브리드 제어를 PNG 두 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("force_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
OUT = HERE.parent / "assets"


def stiffness():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1.3, 1]})
    for ke, ls in ((1e3, ":"), (5e3, "--"), (2.5e4, "-")):
        for mode, color in (("position", ORANGE), ("force", BLUE)):
            r = m.probe(mode, ke)
            ax1.plot(r["t"], r["f"], ls, color=color, lw=2, label=f"{mode}, ke={ke:g}" if ke == 2.5e4 else None)
    ax1.axhline(m.FD, color=GREY, lw=1)
    ax1.plot([], [], ":", color=GREY, label="ke = 1e3 N/m")
    ax1.plot([], [], "--", color=GREY, label="ke = 5e3 N/m")
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("contact force (N)")
    ax1.set_title("Force control lands on 10 N for every surface", fontsize=12)
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(alpha=0.3)
    kes = np.array([1e3, 2e3, 5e3, 1e4, 2.5e4])
    for mode, color in (("position", ORANGE), ("force", BLUE)):
        ax2.plot(kes, [m.probe(mode, k)["f"][-1] for k in kes], "o-", color=color, label=mode + " control")
    ax2.axhline(m.FD, color=GREY, lw=1)
    ax2.set_xscale("log")
    ax2.set_xlabel("true surface stiffness ke (N/m)")
    ax2.set_ylabel("final contact force (N)")
    ax2.set_title("Position control: force scales with ke", fontsize=12)
    ax2.legend(loc="upper left")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig-force-vs-stiffness.png", dpi=100)


def hybrid():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    h, p = m.tool(np.array([0, 1]), 5000.0), m.tool(np.array([0, 0]), 5000.0)
    xs = np.linspace(0, 0.1, 400)
    ax1.plot(xs * 1000, (m.Y0 + m.BUMP * np.sin(2 * np.pi * xs / m.LAM)) * 1000, color=GREY, lw=3, label="surface")
    ax1.plot(p["x"] * 1000, p["y"] * 1000, "--", color=ORANGE, lw=2, label="position only: flat path")
    ax1.plot(h["x"] * 1000, h["y"] * 1000, color=BLUE, lw=2, label="hybrid: path follows the bumps")
    ax1.set_ylim(105, 97)  # y points into the surface, so draw it downward
    ax1.set_xlim(0, 100)
    ax1.set_xlabel("x along the surface (mm)")
    ax1.set_ylabel("y into the surface (mm, down)")
    ax1.set_title("Tool path over a bumpy surface", fontsize=12)
    ax1.legend(loc="lower left", fontsize=9)
    ax1.grid(alpha=0.3)
    ax2.plot(p["t"][500:], p["f"][500:], color=ORANGE, lw=2, label="position only")
    ax2.plot(h["t"][500:], h["f"][500:], color=BLUE, lw=2, label="hybrid, S = diag(0, 1)")
    ax2.axhline(m.FD, color=GREY, lw=1)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("normal force (N)")
    ax2.set_title("Force along y: held near 10 N vs swinging 0 to 20 N", fontsize=12)
    ax2.legend(loc="upper right", fontsize=9)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig-hybrid-bumpy.png", dpi=100)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    stiffness()
    hybrid()
    print(OUT)
