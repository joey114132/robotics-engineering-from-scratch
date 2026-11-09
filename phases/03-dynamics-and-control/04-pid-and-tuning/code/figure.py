# 레슨 03/04 그림: P·PD·PID 의 부하 응답, windup 대 anti-windup, 올린 gain 의 명령 떨림을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pid_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY, PINK = "#0072B2", "#D55E00", "#555555", "#CC79A7"
ASSETS = HERE.parent / "assets"
DT = 1e-3


def save(fig, name):
    fig.tight_layout()
    ASSETS.mkdir(exist_ok=True)
    fig.savefig(ASSETS / name, dpi=100)
    plt.close(fig)
    print(ASSETS / name)


def terms():
    fig, axs = plt.subplots(1, 3, figsize=(12, 5), sharey=True)
    t = np.arange(10000) * DT
    for ax, (title, g) in zip(axs, (("P only", (100, 0, 0)), ("P + D", (100, 0, 20)), ("P + I + D", (100, 200, 20)))):
        q, _, _ = m.simulate(1.0, 2.0, *g, DT, 10000, load=20.0, t_load=5.0)
        ax.plot(t, q, color=BLUE, lw=2)
        ax.axhline(1.0, color=GREY, ls=":", lw=1)
        ax.axvline(5.0, color=ORANGE, ls="--", lw=1)
        ax.set_title(title, fontsize=13)
        ax.set_xlabel("time (s)")
        ax.grid(alpha=0.3)
    axs[0].set_ylabel("joint angle (rad), target = 1")
    axs[1].text(5.2, 0.55, "load steps in", color=ORANGE, fontsize=10)
    axs[1].annotate("offset = load / kp", (9.0, 0.8), (6.0, 0.35), arrowprops=dict(arrowstyle="->", color=GREY), fontsize=10)
    fig.suptitle("P alone rings, D calms it, only I removes the offset", fontsize=14)
    save(fig, "fig-pid-terms.png")


def windup():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2))
    t = np.arange(12000) * DT
    for aw, c, lab in ((False, ORANGE, "no anti-windup"), (True, BLUE, "clamped integrator")):
        q, _, I = m.simulate(1.0, 2.0, 100.0, 300.0, 20.0, DT, 12000, q_des=2.0, umax=20.0, anti_windup=aw)
        a1.plot(t, q, color=c, lw=2, label=lab)
        a2.plot(t, I, color=c, lw=2, label=lab)
    a1.axhline(2.0, color=GREY, ls=":", lw=1)
    a1.set_ylabel("joint angle (rad), target = 2")
    a1.set_title("Windup overshoots the target by 1.5 rad", fontsize=13)
    a2.set_ylabel("integral term (Nm)")
    a2.set_title("The integral term piles up while saturated", fontsize=13)
    for a in (a1, a2):
        a.set_xlabel("time (s)")
        a.grid(alpha=0.3)
        a.legend(loc="upper right", fontsize=9)
    save(fig, "fig-windup.png")


def raised():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2))
    for (kp, kd), c, lab in (((40.0, 2.0), BLUE, "before: kp 40, kd 2"), ((400.0, 60.0), ORANGE, "after: kp 400, kd 60")):
        _, u, _ = m.simulate(0.02, 0.1, kp, 0.0, kd, DT, 400, umax=5.0)
        a1.plot(np.arange(360, 400), u[360:], "o-", color=c, lw=1.5, ms=4, label=lab)
    a1.axhline(0, color=GREY, lw=1)
    a1.set_xlabel("control tick (1 ms each), late in the move")
    a1.set_ylabel("torque command (Nm, limit 5)")
    a1.set_title("Late in the move the new gains buzz the command", fontsize=13)
    a1.legend(loc="upper center", ncol=2, fontsize=9)
    a1.set_ylim(-5.5, 7.5)
    kds = np.linspace(0, 80, 161)
    a2.plot(kds, [m.spectral_radius(0.02, 0.1, 400.0, k, DT) for k in kds], color=BLUE, lw=2)
    a2.axhline(1.0, color=ORANGE, ls="--", lw=1.5)
    a2.text(2, 1.03, "above this line the loop grows", color=ORANGE, fontsize=10)
    a2.set_xlabel("derivative gain kd (Nm s/rad)")
    a2.set_ylabel("largest closed-loop eigenvalue magnitude")
    a2.set_title("Closed-loop eigenvalue crosses 1 near kd = 2J/dt", fontsize=13)
    for a in (a1, a2):
        a.grid(alpha=0.3)
    save(fig, "fig-raised-gains.png")


if __name__ == "__main__":
    terms()
    windup()
    raised()
