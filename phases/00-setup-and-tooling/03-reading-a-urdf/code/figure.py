# 레슨 00/03 그림: 어깨 yaw 90 도일 때 올바른 link 위치와 origin 을 그냥 더한 위치를 위에서 본 평면도로 비교한다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("urdf_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    links, joints = m.parse_urdf(m.URDF)
    ch = m.chain(joints, m.find_root(links, joints), "hand")
    pos = m.link_positions(ch, {"shoulder": 0.0, "elbow": 0.0})
    naive = np.zeros(3)
    naive_pts = [naive.copy()]
    for j in ch:
        naive = naive + j["xyz"]
        naive_pts.append(naive.copy())
    fig, ax = plt.subplots(figsize=(8, 6.2))
    tp = np.array([pos[n] for n in ["base", "upper", "fore", "hand"]])
    npts = np.array(naive_pts)
    ax.plot(tp[:, 0], tp[:, 1], "o-", color=BLUE, lw=4, ms=10, label="correct: origins in the parent frame")
    ax.plot(npts[:, 0], npts[:, 1], "o--", color=ORANGE, lw=3, ms=8, label="naive: origins added in the world frame")
    for name, p in zip(["base and upper (upper is 0.1 m higher)", "fore", "hand"], tp[[0, 2, 3]]):
        ax.annotate(name, p[:2], textcoords="offset points", xytext=(8, -16 if name.startswith("base") else 6), color=BLUE, fontsize=10)
    ax.annotate("hand (naive)", npts[-1][:2], textcoords="offset points", xytext=(0, 12), color=ORANGE, fontsize=10, ha="center")
    ax.set_aspect("equal")
    ax.set_xlim(-0.15, 0.7)
    ax.set_ylim(-0.1, 0.65)
    ax.set_xlabel("x (m), top view")
    ax.set_ylabel("y (m), top view")
    ax.set_title("Shoulder yaw 90 deg: the naive hand is 0.71 m off", fontsize=13)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-origin-frames.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, np.linalg.norm(npts[-1] - tp[-1]))


if __name__ == "__main__":
    main()
