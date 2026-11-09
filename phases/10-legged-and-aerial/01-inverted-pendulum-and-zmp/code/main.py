# 레슨 10/01: 선형 도립진자(LIPM)의 닫힌 해, ZMP, capture point (평면)
import numpy as np

G = 9.81


def time_constant(h, g: float = G):
    """Tc = sqrt(h/g). From x'' = (g/h)(x - p) the growing and shrinking modes are exp(+-t/Tc)."""
    return np.sqrt(h / g)


def lipm_state(x0, v0, p, t, h, g: float = G):
    """Closed form with the foot fixed at p. Returns (x, v) after t seconds."""
    tc, a = time_constant(h, g), x0 - p
    c, s = np.cosh(t / tc), np.sinh(t / tc)
    return p + a * c + tc * v0 * s, a * s / tc + v0 * c


def simulate(x0, v0, foot_fn, h, dt, T, g: float = G):
    """RK4 of x'' = (g/h)(x - p). foot_fn(t, x, v) gives p, held constant over each step."""
    w2, n = g / h, int(round(T / dt))
    t, x, v = np.arange(n + 1) * dt, np.empty(n + 1), np.empty(n + 1)
    x[0], v[0] = x0, v0
    for i in range(n):
        p = foot_fn(t[i], x[i], v[i])
        f = lambda s: np.array([s[1], w2 * (s[0] - p)])
        s0 = np.array([x[i], v[i]])
        k1 = f(s0); k2 = f(s0 + dt / 2 * k1); k3 = f(s0 + dt / 2 * k2); k4 = f(s0 + dt * k3)
        x[i + 1], v[i + 1] = s0 + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, x, v


def zmp(x, acc, h, g: float = G):
    """Zero-moment point: where the ground reaction must act to give this CoM acceleration."""
    return x - h * acc / g


def capture_point(x, v, h, g: float = G):
    """xi = x + v*Tc. It obeys xi' = (xi - p)/Tc, so a foot placed on xi freezes it."""
    return x + v * time_constant(h, g)


def fall_or_recover(v0, h, half_foot, step, t_step=0.1, T=2.0, dt=1e-3):
    """A push gives the CoM speed v0 over the ankle. The ankle puts the ZMP on the capture point, limited to the foot."""
    state = {}

    def foot(t, x, v):
        xi = capture_point(x, v, h)
        if step and t >= t_step:
            state.setdefault("p", xi)  # foot lands on the capture point and stays
            return state["p"]
        return float(np.clip(xi, -half_foot, half_foot))

    return simulate(0.0, v0, foot, h, dt, T)


if __name__ == "__main__":
    for step in (False, True):
        t, x, v = fall_or_recover(0.4, 0.9, 0.05, step)
        print("step" if step else "ankle only", round(x[-1], 3), round(v[-1], 3))
