# 레슨 03/07: 수평면 2링크 팔의 M(q)와 토크를 운동에너지의 수치 미분(Lagrange)과 Newton-Euler 로 각각 유도한다
import numpy as np

E = 1e-6  # step for numeric partial derivatives


def kinetic(q, qd, p):
    """T = sum of 1/2 m |v_com|^2 + 1/2 I w^2, with COM velocities read off the geometry."""
    perp = lambda a: np.array([-np.sin(a), np.cos(a)])
    v1 = p["lc1"] * qd[0] * perp(q[0])
    v2 = p["l1"] * qd[0] * perp(q[0]) + p["lc2"] * (qd[0] + qd[1]) * perp(q[0] + q[1])
    return 0.5 * (p["m1"] * v1 @ v1 + p["m2"] * v2 @ v2 + p["I1"] * qd[0] ** 2 + p["I2"] * (qd[0] + qd[1]) ** 2)


def mass(q, p):
    """T = 1/2 qd' M qd is exactly quadratic, so unit velocities read M off T (polarisation)."""
    e = np.eye(2)
    T = lambda v: kinetic(q, v, p)
    off = T(e[0] + e[1]) - T(e[0]) - T(e[1])
    return np.array([[2 * T(e[0]), off], [off, 2 * T(e[1])]])


def lagrange_tau(q, qd, qdd, p, h_sign=1):
    """tau = d/dt(dL/dqd) - dL/dq = M qdd + (dM/dq qd) qd - dT/dq."""
    dM = [(mass(q + E * e, p) - mass(q - E * e, p)) / (2 * E) for e in np.eye(2)]  # dM[k] = dM/dq_k
    dMdt = sum(dM[k] * qd[k] for k in range(2))
    dTdq = np.array([(kinetic(q + E * e, qd, p) - kinetic(q - E * e, qd, p)) / (2 * E) for e in np.eye(2)])
    return mass(q, p) @ qdd + h_sign * (dMdt @ qd - dTdq)


def newton_euler(q, qd, qdd, p):
    """Planar recursion: accelerations outward, then forces and moments inward. No energy, no derivatives."""
    perp = lambda v: np.array([-v[1], v[0]])
    cross = lambda a, b: a[0] * b[1] - a[1] * b[0]
    u1, u12 = np.array([np.cos(q[0]), np.sin(q[0])]), np.array([np.cos(q[0] + q[1]), np.sin(q[0] + q[1])])
    w1, w2, al1, al2 = qd[0], qd[0] + qd[1], qdd[0], qdd[0] + qdd[1]
    r1, rj, r2 = p["lc1"] * u1, p["l1"] * u1, p["lc2"] * u12
    a1 = al1 * perp(r1) - w1**2 * r1
    aj = al1 * perp(rj) - w1**2 * rj
    a2 = aj + al2 * perp(r2) - w2**2 * r2
    f2 = p["m2"] * a2                                   # force the link-1 joint puts on link 2
    tau2 = p["I2"] * al2 + cross(r2, f2)
    f1 = p["m1"] * a1 + f2                              # force the base puts on link 1
    tau1 = p["I1"] * al1 + cross(r1, f1) + cross(rj - r1, f2) + tau2
    return np.array([tau1, tau2])


def energy_drift(p, q, qd, T=1.0, dt=1e-3, h_sign=1):
    """Free motion (tau = 0) with RK4. Kinetic energy must not change."""
    def acc(q, qd):
        h = lagrange_tau(q, qd, np.zeros(2), p, h_sign)
        return np.linalg.solve(mass(q, p), -h)
    f = lambda x: np.concatenate([x[2:], acc(x[:2], x[2:])])
    x, e0 = np.concatenate([q, qd]), kinetic(q, qd, p)
    for _ in range(int(T / dt)):
        k1 = f(x); k2 = f(x + dt / 2 * k1); k3 = f(x + dt / 2 * k2); k4 = f(x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return kinetic(x[:2], x[2:], p) - e0
