# 레슨 03/05: 수평면 2링크 팔의 M·Coriolis, computed torque 와 PD 의 빠른 궤적 추종 오차 비교
import numpy as np

PARAMS = dict(m1=1.0, m2=1.0, l1=0.5, lc1=0.25, lc2=0.25, I1=0.02, I2=0.02)
OMEGA, DT, AMP, W_TRAJ = 20.0, 1e-3, np.array([1.2, 1.5]), 2 * np.pi  # 1 s period, horizontal plane: no gravity


def mass(q, p):
    c2 = np.cos(q[1])
    a = p["m2"] * p["l1"] * p["lc2"] * c2
    m22 = p["I2"] + p["m2"] * p["lc2"] ** 2
    m11 = p["I1"] + p["m1"] * p["lc1"] ** 2 + p["m2"] * (p["l1"] ** 2 + p["lc2"] ** 2) + p["I2"] + 2 * a
    return np.array([[m11, m22 + a], [m22 + a, m22]])


def coriolis(q, qd, p):
    h = p["m2"] * p["l1"] * p["lc2"] * np.sin(q[1])
    return np.array([-h * (2 * qd[0] * qd[1] + qd[1] ** 2), h * qd[0] ** 2])


def inverse_dynamics(q, qd, qdd, p):
    return mass(q, p) @ qdd + coriolis(q, qd, p)


def forward_dynamics(q, qd, tau, p):
    return np.linalg.solve(mass(q, p), tau - coriolis(q, qd, p))


def rk4_step(q, qd, tau, dt, p):
    f = lambda x: np.concatenate([x[2:], forward_dynamics(x[:2], x[2:], tau, p)])
    x = np.concatenate([q, qd])
    k1 = f(x); k2 = f(x + dt / 2 * k1); k3 = f(x + dt / 2 * k2); k4 = f(x + dt * k3)
    x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return x[:2], x[2:]


def trajectory(t):
    c, s = np.cos(W_TRAJ * t), np.sin(W_TRAJ * t)
    return AMP * (1 - c) / 2, AMP * W_TRAJ * s / 2, AMP * W_TRAJ**2 * c / 2


def computed_torque(q, qd, ref, model):
    """tau = M (qdd_d + kd*ed + kp*e) + h : the model turns the arm into two decoupled double integrators."""
    (qr, vr, ar), e, ed = ref, ref[0] - q, ref[1] - qd
    return mass(q, model) @ (ar + 2 * OMEGA * ed + OMEGA**2 * e) + coriolis(q, qd, model)


def pd_control(q, qd, ref, model):
    """Joint PD tuned for the same bandwidth at one mean pose: gains = M_ii(mean pose) * (omega^2, 2*omega)."""
    Md = np.diag(mass(np.array([0.6, 0.75]), model))
    return Md * (OMEGA**2 * (ref[0] - q) + 2 * OMEGA * (ref[1] - qd))


def tracking_error(ctrl, model, plant, T=2.0, q0_offset=np.zeros(2), norm=True):
    """Controller sees `model`, the arm is `plant`; returns |e| per tick (or e itself with norm=False)."""
    q, qd = trajectory(0.0)[0] + q0_offset, np.zeros(2)
    err = []
    for i in range(int(T / DT)):
        ref = trajectory(i * DT)
        err.append(ref[0] - q)
        q, qd = rk4_step(q, qd, ctrl(q, qd, ref, model), DT, plant)
    err = np.array(err)
    return np.linalg.norm(err, axis=1) if norm else err


if __name__ == "__main__":
    for c in (pd_control, computed_torque):
        print(c.__name__, tracking_error(c, PARAMS, PARAMS).max())
