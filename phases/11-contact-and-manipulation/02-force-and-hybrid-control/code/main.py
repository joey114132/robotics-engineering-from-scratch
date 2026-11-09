# 레슨 11/02: 스프링 표면을 누르는 1-DOF 프로브의 위치 제어 대 적분 힘 제어, 그리고 2-D 하이브리드 위치-힘 제어
import numpy as np

FD, K_EST, X_EST, XS = 10.0, 5000.0, 0.100, 0.1004   # desired force N, assumed stiffness N/m, assumed and true surface m
KI, VMAX, KP = 0.01, 0.01, 20.0                       # force integral gain m/(N s), speed limit m/s, position gain 1/s
VX, T_TOOL, Y0, BUMP, LAM = 0.05, 2.0, 0.100, 0.002, 0.05


def probe(mode, ke, fd=FD, xs=XS, dt=1e-3, T=3.0, vmax=VMAX):
    """Velocity-commanded probe (ideal inner loop) moving down onto a spring surface at xs with stiffness ke."""
    x, n = 0.09, int(T / dt)
    out = {"t": np.arange(n) * dt, "x": np.zeros(n), "f": np.zeros(n)}
    for i in range(n):
        f = ke * max(x - xs, 0.0)                    # true contact force
        if mode == "position":                       # trusts the assumed stiffness and surface position
            v = KP * (X_EST + fd / K_EST - x)
        else:                                        # integral force control: velocity proportional to force error
            v = KI * (fd - f)
        x += np.clip(v, -vmax, vmax) * dt
        out["x"][i], out["f"][i] = x, f
    return out


def tool(S, ke, fd=FD, dt=1e-3):
    """2-D tool. S[k] = 1 force-controls axis k, 0 position-controls it. Axis x slides, axis y presses on a bumpy surface."""
    S, p, n = np.asarray(S, float), np.array([0.0, 0.099]), int(T_TOOL / dt)
    out = {k: np.zeros(n) for k in ("t", "x", "y", "f")}
    for i in range(n):
        t = i * dt
        f = ke * max(p[1] - (Y0 + BUMP * np.sin(2 * np.pi * p[0] / LAM)), 0.0)
        v_pos = KP * (np.array([VX * t, Y0 + fd / K_EST]) - p)        # position law on every axis
        v_frc = np.array([0.0, KI * (fd - f)])                        # force law, only used where S = 1
        lim = np.array([1.0, VMAX if S[1] else 1.0])               # speed limit only on the force axis
        p = p + np.clip((1 - S) * v_pos + S * v_frc, -lim, lim) * dt
        for k, val in zip(out, (t, p[0], p[1], f)):
            out[k][i] = val
    return out


if __name__ == "__main__":
    for ke in (1e3, 5e3, 2.5e4):
        print(ke, "position", round(probe("position", ke)["f"][-1], 1), "force", round(probe("force", ke)["f"][-1], 1))
