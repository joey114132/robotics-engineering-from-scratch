# 레슨 16/01 그림: 성공한 pick-and-place 경로와 오차, 중력 feedforward 를 뺐을 때의 처짐을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pp_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
A, B = (0.50, 0.10), (0.15, 0.50)
OUT = HERE.parent / "assets"


def arm_xy(q):
    return ([0, m.L[0] * np.cos(q[0]), m.fk(q)[0]], [0, m.L[0] * np.sin(q[0]), m.fk(q)[1]])


def scene(ax, r, color, label):
    ax.plot(r["tip"][:, 0], r["tip"][:, 1], color=color, lw=2, label=label)
    for k in (2000, len(r["t"]) - 1):
        x, y = arm_xy(r["q"][k])
        ax.plot(x, y, "-o", color=color, lw=4, ms=7, alpha=0.5)
    ax.plot(*A, "s", color=GREY, ms=11)
    ax.plot(*B, "*", color=GREY, ms=16)
    ax.annotate("A (pick)", A, (A[0] + 0.03, A[1] - 0.06))
    ax.annotate("B (place)", B, (B[0] - 0.12, B[1] + 0.12))
    ax.set_aspect("equal")
    ax.set_xlim(-0.1, 0.85)
    ax.set_ylim(-0.5, 0.75)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.grid(alpha=0.3)


def tracking_mm(r):
    return 1000 * np.linalg.norm(r["tip"] - np.array([m.fk(q) for q in r["q_ref"]]), axis=1)


def main():
    OUT.mkdir(exist_ok=True)
    good, bad = m.run(A, B, 1.0), m.run(A, B, 0.0)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6))
    scene(a1, good, BLUE, "tip path")
    a1.set_title(f"Pick at A, place at B: error {good['place_err'] * 1000:.2f} mm")
    a1.legend(loc="upper right")
    a2.plot(good["t"], tracking_mm(good), color=BLUE)
    a2.axhline(m.TOL * 1000, color=GREY, ls="--", label="place limit 5 mm (checked at the end)")
    a2.set_xlabel("time (s)")
    a2.set_ylabel("tip distance from planned tip (mm)")
    a2.set_title("Tracking lags in motion and settles to zero at B")
    a2.legend()
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig-pick-place-result.png", dpi=100)
    plt.close(fig)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6))
    scene(a1, good, BLUE, "with gravity ff")
    scene(a1, bad, ORANGE, "without gravity ff")
    a1.set_title("Sag pulls the tip off A and B")
    a1.legend(loc="lower right")
    a2.plot(good["t"], tracking_mm(good), color=BLUE, label="with gravity ff")
    a2.plot(bad["t"], tracking_mm(bad), color=ORANGE, label=f"without ff: place error {bad['place_err'] * 1000:.0f} mm, FAIL")
    a2.axhline(m.TOL * 1000, color=GREY, ls="--", label="pass limit 5 mm")
    a2.set_xlabel("time (s)")
    a2.set_ylabel("tip distance from planned tip (mm)")
    a2.set_title("Without ff: 14 to 37 mm off after the start")
    a2.legend(loc="upper right")
    a2.set_ylim(-2, 52)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig-pick-place-sag.png", dpi=100)
    print(OUT)


if __name__ == "__main__":
    main()
