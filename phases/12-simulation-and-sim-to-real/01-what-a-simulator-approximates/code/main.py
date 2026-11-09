# 레슨 12/01: 마찰·모터 지연·센서 지연이 있는 "실제" 관절과 빠진 "시뮬" 관절을 같은 명령으로 돌려 어긋남을 잰다
import math

import numpy as np

DT, EPS = 1e-3, 0.01  # RK4 step (s), width of the smoothed Coulomb sign (rad/s)
REAL = dict(J=0.05, b=0.02, c=0.05, k=0.2, Tm=0.03, delay=0.02)  # inertia, viscous, Coulomb, m*g*l, motor lag (s), sensor delay (s)


def command(t: float) -> float:
    """Open-loop torque (Nm): two sines, the same list of numbers is replayed on every plant."""
    return 0.35 * math.sin(2 * math.pi * 0.7 * t) + 0.15 * math.sin(2 * math.pi * 1.9 * t)


def rhs(x, u, p):
    q, w, tm = x
    dw = (tm - p["b"] * w - p["c"] * math.tanh(w / EPS) - p["k"] * math.sin(q)) / p["J"]
    return (w, dw, (u - tm) / p["Tm"] if p["Tm"] > 0 else 0.0)


def simulate(p, u_fn, T, x0=(0.0, 0.0, 0.0)) -> np.ndarray:
    """RK4 trajectory (n, 3) of [angle, speed, motor torque]. Tm = 0 means the torque follows the command at once."""
    x, out = list(x0), []
    for i in range(int(round(T / DT))):
        out.append(tuple(x))
        u = u_fn(i * DT)
        if p["Tm"] == 0:
            x[2] = u
        k1 = rhs(x, u, p)
        k2 = rhs([a + 0.5 * DT * b for a, b in zip(x, k1)], u, p)
        k3 = rhs([a + 0.5 * DT * b for a, b in zip(x, k2)], u, p)
        k4 = rhs([a + DT * b for a, b in zip(x, k3)], u, p)
        x = [a + DT / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(x, k1, k2, k3, k4)]
    return np.array(out)


def measured(p, u_fn, T) -> np.ndarray:
    """What the encoder reports: the true angle shifted by the sensor delay."""
    q, n = simulate(p, u_fn, T)[:, 0], round(p["delay"] / DT)
    return np.concatenate([np.full(n, q[0]), q[: len(q) - n]]) if n else q


def energy(traj, p) -> np.ndarray:
    return 0.5 * p["J"] * traj[:, 1] ** 2 + p["k"] * (1 - np.cos(traj[:, 0]))


def effect_costs(real, u_fn, T) -> dict:
    """RMS angle error (rad) of a sim that lacks one effect, or all three, replaying the real plant's commands."""
    ref = measured(real, u_fn, T)
    off = {"friction": dict(b=0.0, c=0.0), "motor lag": dict(Tm=0.0), "sensor delay": dict(delay=0.0)}
    off["all three"] = {k: v for d in list(off.values()) for k, v in d.items()}
    return {n: float(np.sqrt(np.mean((measured({**real, **o}, u_fn, T) - ref) ** 2))) for n, o in off.items()}


if __name__ == "__main__":
    for name, rms in effect_costs(REAL, command, 6.0).items():
        print(f"{name:13s} rms error {rms:.3f} rad")
