# 레슨 08/05 그림: ICP 반복에 따라 두 스캔이 겹쳐지는 모습과 시작 회전 오차에 따른 성공 범위를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("icp_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
SHIFT = np.array([0.3, -0.2])


def rot(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def make(angle, shift=SHIFT, spacing=0.05):
    ref, cur = m.room(spacing, 0.0), m.room(spacing, 0.5)
    return ref, (cur - shift) @ rot(angle), rot(angle), shift  # moved -> ref is rot(angle) p + shift


def pose_err(R, t, Rt, tt):
    d = R @ Rt.T
    return np.linalg.norm(t - tt) + abs(np.arctan2(d[1, 0], d[0, 0]))


def main():
    fig, axes = plt.subplots(2, 2, figsize=(12, 6.7))
    ref, moved, Rt, tt = make(0.6)
    for ax, k, title in ((axes[0, 0], 0, "Start: scans 0.6 rad apart"), (axes[0, 1], 3, "After 3 iterations"), (axes[1, 0], 40, "Converged")):
        R, t, _ = m.icp(moved, ref, iters=k) if k else (np.eye(2), np.zeros(2), None)
        ax.plot(*ref.T, ".", color=GREY, ms=2.5, label="reference scan")
        ax.plot(*(moved @ R.T + t).T, ".", color=ORANGE, ms=2.5, label="moving scan")
        ax.set_aspect("equal")
        ax.set_title(title)
        ax.grid(alpha=0.3)
        ax.set_xlim(-2.5, 8)
        ax.set_ylim(-5, 6.5)
    axes[0, 0].legend(loc="upper right", markerscale=4, fontsize=9)
    ax = axes[1, 1]
    angles = np.linspace(0, np.pi, 40)
    for shift, color, lab in ((np.zeros(2), BLUE, "no shift"), (np.array([1.0, 0.0]), ORANGE, "1 m shift")):
        errs = []
        for a in angles:
            ref, moved, Rt, tt = make(a, shift)
            errs.append(pose_err(*m.icp(moved, ref)[:2], Rt, tt))
        ax.plot(np.degrees(angles), errs, "o-", ms=3, color=color, label=lab)
    ax.set_yscale("log")
    ax.axhline(0.05, color=GREY, ls="--", lw=1)
    ax.set_xlabel("start rotation offset (deg)")
    ax.set_ylabel("final pose error (m + rad)")
    ax.set_title("Wins up to a point, then a local minimum")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-icp-basin.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
