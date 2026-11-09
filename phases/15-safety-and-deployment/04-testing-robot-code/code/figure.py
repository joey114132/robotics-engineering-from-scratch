# 레슨 15/04 그림: 부호 버그가 스텝 응답과 녹화 torque 를 어떻게 바꾸는지, 속성 테스트의 토크 분포를 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("test_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
ASSETS = HERE.parent / "assets"


def trace(polarity, T=0.6):
    clock = m.FakeClock()
    return np.array(m.run(m.Controller(clock, polarity=polarity), m.MockJoint(), clock, 1.0, T=T))


def sign_bug():
    good, bad = trace(1), trace(-1)
    t = np.arange(1, len(good) + 1) * 0.01
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.8))
    a1.plot(t, good[:, 0], color=BLUE, lw=2, label="polarity +1")
    a1.plot(t, bad[:, 0], color=ORANGE, lw=2, label="polarity -1 (bug)")
    a1.axhline(1.0, color=GREY, ls=":")
    a1.axvline(0.3, color="k", lw=1)
    a1.text(0.31, -0.35, "test looks here:\nmust be within 0.7 of 1.0", fontsize=9)
    a1.set_xlabel("time (s)")
    a1.set_ylabel("joint angle (rad)")
    a1.set_title("The step test sees the joint run away")
    a1.legend(loc="lower left")
    a2.plot(t, good[:, 2], color=BLUE, lw=2, label="recorded trace")
    clock = m.FakeClock()
    buggy = m.Controller(clock, polarity=-1)
    replayed = []
    for q, r, _ in good:  # feed the recorded inputs to the buggy controller
        clock.advance(0.01)
        replayed.append(buggy.update(q, r))
    a2.plot(t, replayed, color=ORANGE, lw=2, ls="--", label="replayed through the bug")
    a2.set_xlabel("time (s)")
    a2.set_ylabel("commanded torque (Nm)")
    a2.set_title("Replay differs from the recording")
    a2.set_ylim(-12, 17)
    a2.legend(loc="upper right")
    for ax in (a1, a2):
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-sign-bug.png", dpi=100)


def property_plot():
    rng = np.random.default_rng(0)
    clock = m.FakeClock()
    ctrl = m.Controller(clock)
    out = []
    for _ in range(3000):
        clock.advance(float(rng.choice([0.0, 0.001, 0.01, 0.2])))
        q, r = rng.uniform(-1e3, 1e3, 2)
        out.append(ctrl.update(q, r))
    out = np.abs(out)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(out, bins=40, color=BLUE)
    ax.axvline(ctrl.tau_max, color=ORANGE, lw=2)
    ax.text(ctrl.tau_max - 0.2, ax.get_ylim()[1] * 0.6, "limit 10 Nm", color=ORANGE, ha="right")
    ax.set_xlabel("absolute torque for a random input (Nm)")
    ax.set_ylabel("number of inputs")
    ax.set_title("3000 random inputs: none goes past the limit")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-property-torque.png", dpi=100)


if __name__ == "__main__":
    sign_bug()
    property_plot()
