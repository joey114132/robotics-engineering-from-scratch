# 레슨 11/03 그림: 닫히는 파지와 안 닫히는 파지의 갤러리, 그리고 offset 에 따른 epsilon 을 PNG 두 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("grasp_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
OUT = HERE.parent / "assets"


def draw(ax, shape, pts, nrm, mu, title):
    pts, nrm = np.asarray(pts, float), np.asarray(nrm, float)
    ax.add_patch(Circle((0, 0), 1, fc="#eeeeee", ec=GREY, lw=2) if shape == "circle" else Rectangle((-1, -1), 2, 2, fc="#eeeeee", ec=GREY, lw=2))
    W = m.contact_wrenches(pts, nrm, mu)
    eps = m.epsilon(W)
    color = BLUE if eps > 0 else ORANGE
    for p, n in zip(pts, nrm):
        n = n / np.linalg.norm(n)
        a = np.arctan(mu)
        L = 0.9
        e1 = p + L * np.array([np.cos(np.arctan2(n[1], n[0]) + a), np.sin(np.arctan2(n[1], n[0]) + a)])
        e2 = p + L * np.array([np.cos(np.arctan2(n[1], n[0]) - a), np.sin(np.arctan2(n[1], n[0]) - a)])
        ax.add_patch(Polygon([p, e1, e2], fc=color, alpha=0.25, ec=color))
        ax.plot(*p, "o", color=color, ms=9)
        ax.annotate("", xy=p + 0.45 * n, xytext=p, arrowprops=dict(arrowstyle="->", color=color, lw=2))
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"{title}\n" + (f"closes, epsilon = {eps:.2f}" if eps > 0 else "no closure, epsilon = 0"), fontsize=11, color=color)


def gallery():
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.6))
    draw(axs[0, 0], "circle", [[1, 0], [-1, 0]], [[-1, 0], [1, 0]], 0.0, "2 contacts, mu = 0")
    draw(axs[0, 1], "circle", [[1, 0], [-1, 0]], [[-1, 0], [1, 0]], 0.3, "2 contacts, mu = 0.3")
    draw(axs[1, 0], "box", [[-1, 0.0], [1, 0.4]], [[1, 0], [-1, 0]], 0.3, "box, jaw offset 0.4 (limit 0.6), mu = 0.3")
    draw(axs[1, 1], "box", [[-1, 0.0], [1, 0.8]], [[1, 0], [-1, 0]], 0.3, "box, jaw offset 0.8 (limit 0.6), mu = 0.3")
    fig.tight_layout()
    fig.savefig(OUT / "fig-grasp-gallery.png", dpi=100)


def sweep():
    fig, ax = plt.subplots(figsize=(8, 5))
    d = np.linspace(0, 1.6, 120)
    for mu, c, ls in ((0.2, ORANGE, "-"), (0.4, BLUE, "-"), (0.6, GREY, "-")):
        ax.plot(d, [m.epsilon(m.contact_wrenches([[-1, 0], [1, x]], [[1, 0], [-1, 0]], mu)) for x in d], ls, color=c, lw=2, label=f"mu = {mu}")
        ax.axvline(2 * mu, color=c, ls=":", lw=1)
    ax.set_xlabel("vertical offset between the two jaws (box width 2)")
    ax.set_ylabel("grasp quality epsilon")
    ax.set_title("Quality drops to zero where offset = 2 mu (dotted)", fontsize=12)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig-epsilon-vs-offset.png", dpi=100)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    gallery()
    sweep()
    print(OUT)
