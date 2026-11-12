# 레슨 07/05 그림: 지도 위의 추정 경로와 공분산 타원, 초기 heading 오차에 따른 NEES 를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ekf_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def ellipse(ax, mean, cov, color):
    w, v = np.linalg.eigh(cov[:2, :2])
    a = np.linspace(0, 2 * np.pi, 60)
    pts = mean[:2, None] + v @ (2 * np.sqrt(w)[:, None] * np.vstack([np.cos(a), np.sin(a)]))
    ax.plot(*pts, color=color, lw=1, alpha=0.8)


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    t, e, d, Ps = m.run(np.random.default_rng(3), 80, lms=m.LMS[:2])
    ax1.plot(*t[:, :2].T, color=GREY, lw=6, alpha=0.5, label="truth")
    ax1.plot(*d[:, :2].T, "--", color=ORANGE, lw=2, label="dead reckoning")
    ax1.plot(*e[:, :2].T, color=BLUE, lw=1.5, label="EKF")
    for k in range(0, 81, 10):
        ellipse(ax1, e[k], Ps[k], BLUE)
    ax1.plot(*m.LMS[:2].T, "k^", ms=10, label="landmark")
    ax1.set_aspect("equal")
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.set_title("2-sigma ellipses tighten as landmarks are seen")
    ax1.set_xlim(-6, 5)
    ax1.legend(loc="center left")
    ax1.grid(alpha=0.3)

    offs = np.array([0, 0.3, 0.6, 1.0, 1.5])
    for n, color in ((1, ORANGE), (4, BLUE)):
        ax2.plot(offs, [m.mean_nees(20, o, lms=m.LMS[:n]) for o in offs], "o-", color=color, label=f"{n} landmark" + ("s" if n > 1 else ""))
    ax2.axhline(3, color=GREY, ls="--", lw=1)
    ax2.text(0.02, 3.8, "consistent filter = 3", color=GREY)
    ax2.set_yscale("log")
    ax2.set_xlabel("initial heading error (rad)")
    ax2.set_ylabel("mean NEES (log scale)")
    ax2.set_title("One landmark cannot rescue a bad start")
    ax2.legend(loc="upper left")
    ax2.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-ekf-run.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
