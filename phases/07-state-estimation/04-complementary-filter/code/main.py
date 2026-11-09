# 레슨 07/04: gyro(단기에 좋음)와 가속도계 기울기(장기에 좋음)를 합치는 1차 상보 필터와 시간상수 tau 의 트레이드오프
import numpy as np


def alpha(tau, dt):
    """Weight on the gyro path. tau = alpha * dt / (1 - alpha), so a longer tau trusts the gyro longer."""
    return tau / (tau + dt)


def sensors(truth, omega, bias, sig_g, sig_a, rng, runs=1):
    """Gyro rate = true rate + bias + noise. Accelerometer tilt = true tilt + noise. Both shaped (steps, runs)."""
    shape = (len(truth), runs)
    gyro = omega + bias + sig_g * rng.standard_normal(shape)
    return gyro, truth + sig_a * rng.standard_normal(shape)


def integrate(gyro, dt, theta0=0.0):
    """Gyro only: a running sum of rate * dt. Smooth, but the bias accumulates."""
    return theta0 + np.cumsum(gyro, axis=0) * dt


def complementary(gyro, acc, dt, tau, theta0=0.0):
    """theta = a * (theta + gyro * dt) + (1 - a) * acc: gyro for fast changes, accelerometer for the slow average."""
    a, theta, out = alpha(tau, dt), np.full(gyro.shape[1], theta0, float), []
    for g, z in zip(gyro, acc):
        theta = a * (theta + g * dt) + (1 - a) * z
        out.append(theta)
    return np.array(out)


def responses(w, tau):
    """Continuous-time paths: accelerometer low-pass 1/(1+j w tau) and gyro high-pass j w tau/(1+j w tau)."""
    s = 1j * np.asarray(w) * tau
    return 1 / (1 + s), s / (1 + s)


def crossover_hz(tau):
    """Frequency where both paths have magnitude 1/sqrt(2)."""
    return 1 / (2 * np.pi * tau)


def predicted_rmse(tau, dt, bias, sig_a):
    """Still robot: the gyro bias leaves a steady error tau * bias, the accelerometer noise leaves variance sig_a^2 (1-a)/(1+a)."""
    a = alpha(tau, dt)
    return np.sqrt((tau * bias) ** 2 + sig_a**2 * (1 - a) / (1 + a))


def best_tau(dt, bias, sig_a):
    """Minimise (tau b)^2 + sig_a^2 dt / (2 tau): tau^3 = sig_a^2 dt / (4 b^2)."""
    return (sig_a**2 * dt / (4 * bias**2)) ** (1 / 3)


if __name__ == "__main__":
    dt, b, sa = 0.01, 0.01, 0.05
    t = dt * np.arange(2000)[:, None]
    truth, omega = 0.3 * np.sin(1.9 * t), 0.3 * 1.9 * np.cos(1.9 * t)
    gyro, acc = sensors(truth, omega, b, 0.02, sa, np.random.default_rng(0))
    est = complementary(gyro, acc, dt, best_tau(dt, b, sa))
    for name, x in (("accel", acc), ("gyro", integrate(gyro, dt)), ("fused", est)):
        print(name, "rmse (rad):", np.sqrt(np.mean((x - truth) ** 2)))
