# 레슨 09/03 그림: 얇은 장애물을 놓치는 샘플 간격과, 간격에 따른 miss 율과 false alarm 율을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("coll_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
OUT = HERE.parent / "assets"


def samples(a, b, step):
    n = int(np.ceil(np.linalg.norm(b - a) / step))
    return a + np.linspace(0, 1, n + 1)[:, None] * (b - a)


def main():
    OUT.mkdir(exist_ok=True)
    a, b, c, r = np.array([0.0, 0.0]), np.array([6.0, 0.0]), np.array([3.5, 0.0]), 0.25
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.4), gridspec_kw={"width_ratios": [1.1, 1]})
    for step, y, color, mk in ((1.0, 0.55, ORANGE, "x"), (0.25, -0.55, BLUE, "|")):
        p = samples(a, b, step)
        a1.add_patch(Circle(c + [0, y], r, color=GREY, alpha=0.5))
        a1.plot([a[0], b[0]], [y, y], color="black", lw=1.5, zorder=0)
        a1.plot(p[:, 0], np.full(len(p), y), mk, color=color, ms=13, mew=2.5)
        verdict = "catches the obstacle" if m.swept_hits(a, b, c, r, step) else "MISSES the obstacle"
        a1.text(3.0, y + 0.42, f"step {step}: {verdict}", ha="center", color=color, fontsize=13, fontweight="bold")
    a1.annotate("", xy=(c[0] + r, -0.95), xytext=(c[0] - r, -0.95), arrowprops=dict(arrowstyle="<->", color=GREY))
    a1.text(c[0] + 0.4, -1.0, "2r", ha="left", va="center", color=GREY, fontsize=14)
    a1.set_xlim(-0.3, 6.3)
    a1.set_ylim(-1.25, 1.35)
    a1.set_aspect("equal")
    a1.set_title("Same path, two step sizes", fontsize=15)
    a1.set_xlabel("x (m)")
    a1.set_ylabel("y (m)")

    rng = np.random.default_rng(0)
    C, R = np.array([5.0, 5.0]), 0.3
    segs = [(rng.uniform(0, 10, 2), rng.uniform(0, 10, 2)) for _ in range(6000)]
    hit = [(p, q) for p, q in segs if m.seg_hits(p, q, C, R)]
    free = [(p, q) for p, q in segs if not m.seg_hits(p, q, C, R)]
    ratios = np.linspace(0.25, 4, 16)
    miss = [np.mean([not m.swept_hits(p, q, C, R, k * 2 * R) for p, q in hit]) * 100 for k in ratios]
    alarm = [np.mean([m.conservative_hits(p, q, C, R, k * 2 * R) for p, q in free]) * 100 for k in ratios]
    a2.plot(ratios, miss, "o-", color=ORANGE, label="plain samples: real hits missed")
    a2.plot(ratios, alarm, "s--", color=BLUE, label="padded by s/2: false alarms")
    a2.axvline(1.0, color=GREY, ls=":")
    a2.text(1.05, 60, "step = 2r", color=GREY, fontsize=13)
    a2.set_xlabel("step / obstacle width (2r)")
    a2.set_ylabel("share of segments (%)")
    a2.set_title("Bigger step, more misses", fontsize=14)
    a2.legend(loc="upper left", fontsize=12)
    a2.set_ylim(-3, 85)
    fig.tight_layout()
    fig.savefig(OUT / "fig-tunnelling.png", dpi=100)
    print(f"hits {len(hit)} free {len(free)}", [round(x, 1) for x in miss], [round(x, 1) for x in alarm])


if __name__ == "__main__":
    main()
