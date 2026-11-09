# 레슨 01/02 그림: 무작위 관절각으로 찍은 팁 위치가 reach bounds 안에 놓이는 모습과 가운데 구멍을 그린다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lesson_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def save(fig, name):
    out = HERE.parent / "assets" / name
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


def main():
    rng = np.random.default_rng(0)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6))
    th = np.linspace(0, 2 * np.pi, 200)
    for ax, L in zip(axes, ([1.0, 1.0], [3.0, 1.0])):
        pts = np.array([m.fk_planar(L, rng.uniform(-np.pi, np.pi, 2))[:2] for _ in range(3000)])
        lo, hi = m.reach_bounds(L)
        ax.plot(pts[:, 0], pts[:, 1], ".", ms=2, color=BLUE, alpha=0.6)
        for r in (lo, hi):
            ax.plot(r * np.cos(th), r * np.sin(th), "--", color=ORANGE, lw=1.5)
        ax.set_aspect("equal")
        ax.set_title(f"links {L}: reach {lo:g} to {hi:g} m", fontsize=13)
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.grid(alpha=0.3)
    fig.tight_layout()
    save(fig, "fig-workspace.png")


if __name__ == "__main__":
    main()
