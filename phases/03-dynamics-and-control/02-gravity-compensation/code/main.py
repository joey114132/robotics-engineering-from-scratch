# 레슨 03/02: 2링크 평면 팔의 중력토크와 PD+feedforward 의 정상상태 처짐
import numpy as np

G = 9.81


def gravity_torque(q, m1, m2, l1, lc1, lc2, g: float = G) -> np.ndarray:
    """Joint torques that hold the arm still. Angles from the horizontal, gravity points down."""
    q1, q2 = q
    c1, c12 = np.cos(q1), np.cos(q1 + q2)
    t2 = m2 * lc2 * g * c12
    t1 = (m1 * lc1 + m2 * l1) * g * c1 + t2
    return np.array([t1, t2])


def steady_state(q_des, kp, ff_scale, iters: int = 500, **params) -> np.ndarray:
    """Solve kp*(q_des - q) + ff = tau_g(q) by damped fixed-point iteration. ff = ff_scale * tau_g(q_des)."""
    q_des, kp = np.asarray(q_des, float), np.asarray(kp, float)
    ff = ff_scale * gravity_torque(q_des, **params)
    q = q_des.copy()
    for _ in range(iters):
        q = 0.5 * q + 0.5 * (q_des + (ff - gravity_torque(q, **params)) / kp)
    residual = np.abs(kp * (q_des - q) + ff - gravity_torque(q, **params)).max()
    if not residual < 1e-6:  # kp below the gravity gradient has no stable equilibrium to find
        raise ValueError(f"steady state did not converge (residual {residual:.3g} Nm); kp too soft")
    return q


def sag(q_des, kp, ff_scale, **params) -> np.ndarray:
    """Negative = the arm droops below the command; positive = it floats up."""
    return steady_state(q_des, kp, ff_scale, **params) - np.asarray(q_des, float)


if __name__ == "__main__":
    P = dict(m1=2.0, m2=1.0, l1=0.4, lc1=0.2, lc2=0.2)
    for kp in (200.0, 100.0, 50.0):
        print(kp, sag([0.0, 0.0], [kp, kp], 0.8, **P))
