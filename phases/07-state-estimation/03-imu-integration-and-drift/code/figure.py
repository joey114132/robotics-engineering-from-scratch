# 레슨 07/03 그림: 반복 실험의 각도·위치 drift 가 유도식과 겹치는 모습과, 중력 누설이 세제곱으로 커지는 모습을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("imu_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
ASSETS = HERE.parent / "assets"
DT, N = 0.01, 2000  # 100 Hz, 20 s
BG, BA = 0.01, 0.05  # example biases: rad/s and m/s^2


def drift():
    rng = np.random.default_rng(2)
    t = DT * np.arange(1, N + 1)
    ang = np.degrees(m.gyro_angle(np.zeros(N), BG, 0.1, DT, rng, runs=15))
    _, pos = m.accel_position(np.zeros(N), BA, 0.5, DT, rng, runs=15)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6))
    a1.plot(t, ang, color=BLUE, lw=1, alpha=0.5)
    a1.plot(t, np.degrees(BG * t), "--", color="black", lw=2.4, label="derived: b t")
    a1.set_xlabel("time (s)")
    a1.set_ylabel("angle error (deg)")
    a1.set_title("Gyro bias: angle error grows in a line")
    a1.legend(loc="upper left", framealpha=0.95)
    a2.plot(t, pos, color=ORANGE, lw=1, alpha=0.5)
    a2.plot(t, m.position_drift(BA, t), "--", color="black", lw=2.4, label="derived: a t^2 / 2")
    a2.set_xlabel("time (s)")
    a2.set_ylabel("position error (m)")
    a2.set_title("Accel bias: position error grows as t^2")
    a2.legend(loc="upper left", framealpha=0.95)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-imu-drift.png", dpi=100)
    plt.close(fig)


def leak():
    t = DT * np.arange(1, N + 1)
    acc = m.position_drift(BA, t)
    gyr = m.leaked_position(BG, N, DT)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6))
    a1.plot(t, acc, color=ORANGE, label="accel bias 0.05 m/s^2")
    a1.plot(t, gyr, color=BLUE, label="gyro bias 0.01 rad/s (0.57 deg/s)")
    a1.set_xlabel("time (s)")
    a1.set_ylabel("position error (m)")
    a1.set_title("Cubic growth overtakes quadratic")
    a1.legend(loc="upper left", framealpha=0.95)
    a2.loglog(t, acc, color=ORANGE, label="accel bias: slope 2")
    a2.loglog(t, gyr, color=BLUE, label="gyro bias via gravity: slope 3")
    a2.set_xlabel("time (s)")
    a2.set_ylabel("position error (m)")
    a2.set_title("Log-log slope is the order of growth")
    a2.legend(loc="upper left", framealpha=0.95)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-gravity-leak.png", dpi=100)
    plt.close(fig)


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    drift()
    leak()
    print("ok")
