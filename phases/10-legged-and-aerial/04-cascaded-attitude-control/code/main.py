# 레슨 10/04: 평면 pitch 의 단일 PD 루프와 각도 P + 속도 PI 캐스케이드, 돌풍 토크 아래 비교
import numpy as np


def pd(kp, kd):
    """Single loop: tau = kp (ref - theta) - kd omega."""
    return lambda ref, th, w, dt: kp * (ref - th) - kd * w


def cascade(k_theta, k_w, k_i):
    """Outer angle P gives a rate command, inner rate PI gives the torque. k_i = 0 is a plain P-P cascade."""
    z = [0.0]

    def ctrl(ref, th, w, dt):
        e_w = k_theta * (ref - th) - w
        z[0] += e_w * dt
        return k_w * e_w + k_i * z[0]

    return ctrl


def simulate(ctrl, I, dt, t_end, disturbance, ref):
    """Plant I theta'' = tau + d, semi-implicit Euler. Returns t, theta, omega, tau."""
    n = int(round(t_end / dt))
    t = np.arange(n + 1) * dt
    th, w, tau = np.zeros(n + 1), np.zeros(n + 1), np.zeros(n + 1)
    for i in range(n):
        tau[i] = ctrl(ref(t[i]), th[i], w[i], dt)
        w[i + 1] = w[i] + (tau[i] + disturbance(t[i])) / I * dt
        th[i + 1] = th[i] + w[i + 1] * dt
    tau[n] = tau[n - 1]
    return t, th, w, tau


def cascade_poles(I, k_theta, k_w, k_i):
    """Closed loop of I s^2 theta = -(k_w + k_i/s)(s + k_theta) theta: I s^3 + k_w s^2 + (k_w k_theta + k_i) s + k_i k_theta = 0."""
    return np.roots([I, k_w, k_w * k_theta + k_i, k_i * k_theta])


if __name__ == "__main__":
    I, kp, kd, ki = 0.004, 0.9, 0.084, 0.5
    g = lambda t: 0.1 if 0.5 <= t < 1.5 else 0.0
    for name, c in (("PD", pd(kp, kd)), ("cascade", cascade(kp / kd, kd, ki))):
        t, th, w, tau = simulate(c, I, 1e-3, 3.0, g, lambda t: 0.0)
        print(name, "peak deg", round(np.degrees(np.abs(th).max()), 2), "at 1.5 s", round(np.degrees(th[1500]), 2))
