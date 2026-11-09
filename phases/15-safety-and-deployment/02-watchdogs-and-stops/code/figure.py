# 레슨 15/02 그림: 토크 차단과 ramp 정지의 궤적, timeout 에 따른 초과 이동 거리를 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("wd_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
ASSETS = HERE.parent / "assets"
LIM = 1.5


def traces():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    for mode, c, lab in (("cut", ORANGE, "torque cut: coasts"), ("ramp", BLUE, "ramped stop, a = 8 rad/s^2")):
        r = m.simulate(mode, timeout=0.05, T=4.0, q_lim=100.0, record=True) if False else None
    for mode, c, lab in (("cut", ORANGE, "torque cut: coasts"), ("ramp", BLUE, "ramped stop (a = 8 rad/s^2)")):
        t, q, v = m.simulate(mode, timeout=0.05, T=4.0, q_lim=100.0)["trace"].T
        a1.plot(t, q, color=c, lw=2, label=lab)
        a2.plot(t, v, color=c, lw=2)
    a1.axhline(LIM, color="k", lw=1.2)
    a1.text(3.9, LIM + 0.12, "joint limit", ha="right")
    a1.set_ylim(0, 6)
    for ax in (a1, a2):
        ax.axvline(0.5, color=GREY, ls=":", lw=1)
        ax.set_xlabel("time (s)")
        ax.grid(alpha=0.3)
    a1.set_ylabel("joint angle (rad)")
    a2.set_ylabel("joint speed (rad/s)")
    a1.set_title("Cut flies past the limit, ramp stops short")
    a2.set_title("Dotted line: the command source dies")
    a1.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-cut-vs-ramp.png", dpi=100)


def timeouts():
    ts = np.linspace(0.02, 0.3, 29)
    over = [m.simulate("ramp", timeout=x, q_lim=100.0, T=4.0)["overrun"] for x in ts]
    room = 0.5
    best = m.max_timeout(room, 2.0, 8.0)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ts, over, color=BLUE, lw=2, label="simulated overrun")
    ax.plot(ts, 2.0 * ts + m.stop_distance(2.0, 8.0), color=GREY, ls="--", label="v T + v^2 / 2a")
    ax.axhline(room, color="k", lw=1.2)
    ax.text(0.15, room + 0.02, "room to the limit (0.5 rad)", fontsize=10)
    ax.axvline(best, color=ORANGE, lw=1.5)
    ax.text(best + 0.005, 0.3, f"max timeout {best:.3f} s", color=ORANGE)
    ax.set_xlabel("watchdog timeout (s)")
    ax.set_ylabel("travel after the source dies (rad)")
    ax.set_title("Every extra 10 ms of timeout costs 0.02 rad of travel")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.85))
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-timeout-budget.png", dpi=100)


if __name__ == "__main__":
    traces()
    timeouts()
