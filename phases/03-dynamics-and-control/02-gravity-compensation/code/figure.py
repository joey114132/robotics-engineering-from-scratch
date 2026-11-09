# 레슨 03/02 그림: kp 에 따른 처짐과 팔 자세 스케치를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("grav_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

P = dict(m1=2.0, m2=1.0, l1=0.4, lc1=0.2, lc2=0.2)
L = (0.4, 0.4)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def arm_xy(q):
    a, b = q[0], q[0] + q[1]
    return [0, L[0] * np.cos(a), L[0] * np.cos(a) + L[1] * np.cos(b)], [0, L[0] * np.sin(a), L[0] * np.sin(a) + L[1] * np.sin(b)]


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1.15, 1]})
    kps = np.array([30, 40, 60, 100, 200, 400.0])
    for scale, color, label in ((0.8, ORANGE, "model 20% too light: arm droops"), (1.2, BLUE, "model 20% too heavy: arm floats up")):
        sag = np.array([m.sag([0, 0], [k, k], scale, **P)[0] for k in kps])
        ax1.plot(kps, np.degrees(sag), "o-", color=color, label=label)
    ax1.axhline(0, color=GREY, lw=1)
    ax1.set_xscale("log")
    ax1.set_xlabel("position gain kp (Nm/rad)")
    ax1.set_ylabel("steady-state error of joint 1 (deg)")
    ax1.set_title("Halve kp, double the error")
    ax1.legend(loc="upper right", framealpha=0.95)
    ax1.grid(alpha=0.3)

    q_des = np.zeros(2)
    q_bad = m.steady_state(q_des, [40.0, 40.0], 0.8, **P)
    for q, color, ls, lab in ((q_des, GREY, "--", "commanded"), (q_bad, ORANGE, "-", "actual at kp=40, model 20% light")):
        x, y = arm_xy(q)
        ax2.plot(x, y, ls, color=color, lw=5, solid_capstyle="round", label=lab)
        ax2.plot(x, y, "o", color=color, ms=9)
    ax2.set_aspect("equal")
    ax2.set_xlim(-0.1, 0.95)
    ax2.set_ylim(-0.25, 0.15)
    ax2.set_title("Same command, soft gain: the arm sags")
    ax2.legend(loc="lower left")
    ax2.set_xlabel("x (m)")
    ax2.set_ylabel("y (m)")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-gravity-sag.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
