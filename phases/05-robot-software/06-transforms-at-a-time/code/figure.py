# 레슨 05/06 그림: 회전하는 로봇의 스캔을 찍힌 시각의 pose 와 최신 pose 로 놓았을 때의 차이를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("tfbuf_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
WALL = np.array([[2.0, y, 0.0] for y in np.linspace(-1, 1, 41)])
STAMPS = np.linspace(0.0, 0.5, 41)  # one beam per stamp, a 0.5 s sweep


def pose(t, w, v=0.5):
    return np.array([v * t, 0.0, 0.0]), np.array([np.cos(w * t / 2), 0, 0, np.sin(w * t / 2)])


def scan(w):
    buf = m.PoseBuffer()
    for t in np.linspace(0, 0.5, 6):
        buf.add(t, *pose(t, w))
    pts = [m.quat_to_R(pose(t, w)[1]).T @ (x - pose(t, w)[0]) for t, x in zip(STAMPS, WALL)]
    return m.to_world(buf, STAMPS, pts), m.to_world(buf, STAMPS, pts, use_stamps=False)


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1, 1.1]})
    good, bad = scan(1.0)
    ax1.plot(good[:, 0], good[:, 1], "o", color=BLUE, ms=5, label="pose at each point's stamp")
    ax1.plot(bad[:, 0], bad[:, 1], "o", color=ORANGE, ms=5, label="newest pose for every point")
    ax1.axvline(2.0, color=GREY, lw=1, ls=":")
    ax1.set_aspect("equal")
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.set_title("Straight wall, robot turning 1 rad/s")
    ax1.set_xlim(1.85, 2.9)
    ax1.set_ylim(-1.1, 1.1)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), fontsize=9)
    ax1.grid(alpha=0.3)
    ws = np.linspace(0, 2, 21)
    err = [np.linalg.norm(scan(w)[1] - WALL, axis=1).max() for w in ws]
    ax2.plot(ws, err, "o-", color=ORANGE, label="newest pose")
    ax2.plot(ws, [np.linalg.norm(scan(w)[0] - WALL, axis=1).max() for w in ws], "o-", color=BLUE, label="stamped pose")
    ax2.set_xlabel("turn rate (rad/s)")
    ax2.set_ylabel("worst point error (m)")
    ax2.set_title("Smear grows with turn rate")
    ax2.legend(loc="upper left")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-scan-smear.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
