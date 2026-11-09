# 레슨 01/03 그림: 부호 보정이 없으면 slerp 가 얼마나 돌아가는지 경로 위 누적 각도로 보여 준다
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
    q0 = m.quat_from_axis_angle([0, 0, 1], 0.0)
    q1 = -m.quat_from_axis_angle([0, 0, 1], 0.1)  # the 0.1 rad target, delivered with the opposite sign
    ts = np.linspace(0, 1, 200)
    fig, ax = plt.subplots(figsize=(10, 5.6))
    for fix, color, label in ((False, ORANGE, "no sign fix"), (True, BLUE, "negate when dot < 0")):
        ang = [np.degrees(2 * np.arctan2(np.linalg.norm(q[1:]), q[0])) for q in (m.slerp(q0, q1, t, fix) for t in ts)]
        ax.plot(ts, ang, color=color, lw=2.5, label=f"{label}: swept {np.degrees(m.path_angle(q0, q1, fix)):.1f} deg")
    ax.set_xlabel("interpolation parameter t")
    ax.set_ylabel("wrist angle about z (deg)")
    ax.set_title("A 5.7 deg correction becomes a near-full turn without the fix", fontsize=13)
    ax.legend(fontsize=10, loc="center left")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save(fig, "fig-slerp-long-way.png")


if __name__ == "__main__":
    main()
