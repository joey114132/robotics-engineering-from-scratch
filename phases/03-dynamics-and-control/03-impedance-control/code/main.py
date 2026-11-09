# 레슨 03/03: 1자유도 가상 스프링-댐퍼(임피던스) 제어와 외력에 대한 처짐
import numpy as np


def impedance_torque(q, qd, q_des, K, D, tau_g):
    """Spring toward q_des, damper on velocity, plus gravity feedforward."""
    return K * (q_des - q) - D * qd + tau_g


def damping_for_zeta(K: float, J: float, zeta: float) -> float:
    return 2.0 * zeta * np.sqrt(K * J)


def simulate(J: float, K: float, D: float, f_ext: float, dt: float, n: int) -> np.ndarray:
    """Gravity is cancelled exactly; a constant external torque pushes the joint. Semi-implicit Euler."""
    q = qd = 0.0
    out = np.empty(n)
    for i in range(n):
        tau = impedance_torque(q, qd, 0.0, K, D, tau_g=0.0)
        qd += dt * (tau + f_ext) / J
        q += dt * qd
        out[i] = q
    return out


if __name__ == "__main__":
    q = simulate(1.0, 100.0, damping_for_zeta(100.0, 1.0, 0.2), 2.0, 1e-3, 6000)
    print("steady", q[-1], "peak", q.max())
