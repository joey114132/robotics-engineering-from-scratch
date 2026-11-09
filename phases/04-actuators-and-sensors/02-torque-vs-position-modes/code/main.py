# 레슨 04/02: 1축 관절을 토크 모드(바깥 임피던스)와 position 모드(드라이브 안쪽 PD)로 돌려 외력에 대한 처짐을 비교
import numpy as np


def run(mode, q_des=0.0, K=20.0, D=None, push=2.0, kp_in=400.0, kd_in=40.0, J=0.1, b=0.05, T=3.0, dt=1e-4, t_push=0.5):
    """Joint J*qdd = tau - b*qd + tau_ext. A constant external torque `push` starts at t_push.

    torque:     the outer loop writes torque directly: tau = K*(q_des - q) - D*qd.
    position:   the drive owns an inner PD with fixed kp_in, kd_in; the outer loop only sets q_des (K is ignored).
    admittance: position mode plus a compliance layer outside: q_cmd = q_des + tau_ext_measured / K.
    """
    D = 1.4 * np.sqrt(K * J) if D is None else D
    n = int(round(T / dt))
    q, qd = 0.0, 0.0
    out = np.zeros(n + 1)
    for k in range(n):
        ext = push if k * dt >= t_push else 0.0
        if mode == "torque":
            tau = K * (q_des - q) - D * qd
        elif mode == "position":
            tau = kp_in * (q_des - q) - kd_in * qd
        elif mode == "admittance":
            tau = kp_in * (q_des + ext / K - q) - kd_in * qd
        else:
            raise ValueError(f"unknown mode {mode!r}")
        qd += dt * (tau - b * qd + ext) / J  # semi-implicit Euler keeps the stiff inner loop stable
        q += dt * qd
        out[k + 1] = q
    return np.arange(n + 1) * dt, out


def felt_stiffness(mode, K, push=2.0, **kw):
    """Torque needed per radian of deflection, measured after the joint settles."""
    _, q = run(mode, K=K, push=push, **kw)
    return push / (q[-1] - 0.0)


if __name__ == "__main__":
    for mode in ("torque", "position", "admittance"):
        print(mode, felt_stiffness(mode, 20.0))
