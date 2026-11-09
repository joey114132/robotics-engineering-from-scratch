# 레슨 03/04: 마찰이 있는 질량에 대한 이산 PID, 부하 외란, 포화 액추에이터와 anti-windup, 폐루프 고유값
import numpy as np


def simulate(J, b, kp, ki, kd, dt, n, q_des=1.0, load=0.0, t_load=0.0, umax=np.inf, anti_windup=True):
    """J*qdd = u - b*qd - load. One command per tick, held for dt. Returns (q, u, I) arrays."""
    q = v = I = 0.0
    out = np.empty((3, n))
    for i in range(n):
        e = q_des - q
        raw = kp * e + I - kd * v  # D acts on measured velocity, so a setpoint step does not kick it
        u = float(np.clip(raw, -umax, umax))
        if not anti_windup or u == raw or e * raw < 0:  # clamp: stop integrating while saturated and pushing deeper
            I += ki * e * dt
        v += dt / J * (u - b * v - (load if i * dt >= t_load else 0.0))
        q += dt * v
        out[:, i] = q, u, I
    return out


def closed_loop_matrix(J, b, kp, kd, dt):
    """State (q, v) of the PD loop above, no integral, no saturation: x+ = A x + (setpoint term)."""
    a = 1.0 - dt * (kd + b) / J
    return np.array([[1.0 - dt * dt * kp / J, dt * a], [-dt * kp / J, a]])


def spectral_radius(J, b, kp, kd, dt):
    return float(np.abs(np.linalg.eigvals(closed_loop_matrix(J, b, kp, kd, dt))).max())


def overshoot(q, q_des=1.0):
    return max(0.0, float(q.max()) - q_des)


if __name__ == "__main__":
    for kd in (2.0, 30.0):
        print(kd, round(spectral_radius(0.02, 0.1, 400.0, kd, 0.001), 3))
