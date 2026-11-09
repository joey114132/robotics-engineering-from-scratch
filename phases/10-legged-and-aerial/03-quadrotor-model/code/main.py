# 레슨 10/03: 평면 쿼드로터(x, z, pitch)의 운동방정식, 호버 추력, RK4 시뮬레이션
import numpy as np

G = 9.81


def hover_thrust(m, g: float = G):
    """Level and still: the thrust T must cancel weight, T = m g."""
    return m * g


def deriv(s, T, tau, m, I, g: float = G):
    """State s = [x, z, theta, vx, vz, omega]. Thrust T acts along the body axis, tilted by theta from vertical.
    m x'' = T sin(theta), m z'' = T cos(theta) - m g, I theta'' = tau."""
    th = s[2]
    return np.array([s[3], s[4], s[5], T * np.sin(th) / m, T * np.cos(th) / m - g, tau / I])


def simulate(s0, control, m, I, dt, t_end, g: float = G):
    """RK4. control(t, s) returns (T, tau), held constant over each step. Returns (t, states)."""
    n = int(round(t_end / dt))
    t, s = np.arange(n + 1) * dt, np.empty((n + 1, 6))
    s[0] = s0
    for i in range(n):
        T, tau = control(t[i], s[i])
        f = lambda y: deriv(y, T, tau, m, I, g)
        k1 = f(s[i]); k2 = f(s[i] + dt / 2 * k1); k3 = f(s[i] + dt / 2 * k2); k4 = f(s[i] + dt * k3)
        s[i + 1] = s[i] + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, s


def linear_torque_step(t, tau, I, g: float = G):
    """Small angles, T = m g: theta'' = tau/I and x'' = g theta, so theta = tau t^2/(2I) and x = g tau t^4/(24 I)."""
    return tau * t**2 / (2 * I), g * tau * t**4 / (24 * I)


if __name__ == "__main__":
    m, I = 0.5, 0.004
    t, s = simulate(np.zeros(6), lambda t, s: (hover_thrust(m), 0.002), m, I, 1e-3, 1.0)
    print("pitch deg", np.degrees(s[-1, 2]).round(1), "x m", s[-1, 0].round(3), "z m", s[-1, 1].round(3))
