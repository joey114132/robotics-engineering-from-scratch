# 레슨 09/01: 두 점 사이 cubic, quintic, trapezoid 속도 프로파일과 가속도 계단이 만드는 jerk
import numpy as np


def cubic(q0, qf, T):
    """Coefficients a0..a5 of q(t) with zero velocity at both ends (a4 = a5 = 0)."""
    d = qf - q0
    return np.array([q0, 0.0, 3 * d / T**2, -2 * d / T**3, 0.0, 0.0])


def quintic(q0, qf, T):
    """Zero velocity and zero acceleration at both ends: six conditions, six coefficients."""
    d = qf - q0
    return np.array([q0, 0.0, 0.0, 10 * d / T**3, -15 * d / T**4, 6 * d / T**5])


def poly(c, t):
    """Position, velocity, acceleration of sum c[k] t^k."""
    t = np.asarray(t, float)
    p = sum(c[k] * t**k for k in range(6))
    v = sum(k * c[k] * t ** (k - 1) for k in range(1, 6))
    a = sum(k * (k - 1) * c[k] * t ** (k - 2) for k in range(2, 6))
    return p, v, a


def trapezoid(q0, qf, T, ta):
    """Accelerate for ta, cruise at d/(T-ta), decelerate for ta. Needs ta <= T/2."""
    d = qf - q0
    vm = d / (T - ta)
    a = vm / ta

    def f(t):
        t = np.asarray(t, float)
        up, down = t < ta, t > T - ta
        acc = np.where(up, a, np.where(down, -a, 0.0))
        vel = np.where(up, a * t, np.where(down, a * (T - t), vm))
        pos = np.where(up, q0 + 0.5 * a * t**2, np.where(down, qf - 0.5 * a * (T - t) ** 2, q0 + vm * (t - ta / 2)))
        return pos, vel, acc

    return f


def peak_jerk(acc, dt):
    """Largest |finite-difference jerk| when the joint sits at rest (acceleration 0) before and after the move."""
    return float(np.abs(np.diff(np.concatenate([[0.0], acc, [0.0]]))).max() / dt)


if __name__ == "__main__":
    T, dt = 2.0, 0.002
    t = np.arange(0, T + dt / 2, dt)
    for name, acc in (("cubic", poly(cubic(0, 1, T), t)[2]), ("quintic", poly(quintic(0, 1, T), t)[2]), ("trapezoid", trapezoid(0, 1, T, 0.5)(t)[2])):
        print(f"{name:10s} peak accel {np.abs(acc).max():.2f}  peak jerk {peak_jerk(acc, dt):.1f}")
