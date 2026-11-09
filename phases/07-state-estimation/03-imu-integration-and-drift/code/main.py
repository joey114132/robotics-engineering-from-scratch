# 레슨 07/03: 정지한 IMU 의 gyro/accel 을 적분해 bias 가 각도 선형, 위치 제곱, 중력 누설 세제곱 drift 가 되는 것을 보인다
import numpy as np

G = 9.81  # m/s^2


def gyro_angle(omega_true, bias, sigma, dt, rng, runs=1):
    """Integrate a biased, noisy gyro rate. Returns the estimated angle, shape (steps, runs)."""
    omega_true = np.asarray(omega_true, float)[:, None]
    meas = omega_true + bias + sigma * rng.standard_normal((len(omega_true), runs))
    return np.cumsum(meas, axis=0) * dt


def accel_position(a_true, bias, sigma, dt, rng, runs=1):
    """Double-integrate a biased, noisy accelerometer. Returns estimated velocity and position, each (steps, runs)."""
    a_true = np.asarray(a_true, float)[:, None]
    v = np.cumsum(a_true + bias + sigma * rng.standard_normal((len(a_true), runs)), axis=0) * dt
    return v, np.cumsum(v, axis=0) * dt


def position_drift(accel_error, t):
    """Constant acceleration error integrated twice: 0.5 * a * t^2."""
    return 0.5 * accel_error * t**2


def leaked_position(bias_g, steps, dt):
    """Stationary robot, gyro bias only. The tilt estimate is wrong by bias*t, so g*sin(tilt error) looks like acceleration."""
    t = dt * np.arange(1, steps + 1)
    fake_a = G * np.sin(bias_g * t)
    return np.cumsum(np.cumsum(fake_a) * dt) * dt


if __name__ == "__main__":
    dt, n = 0.01, 1000
    rng = np.random.default_rng(0)
    print("angle error after 10 s (rad):", gyro_angle(np.zeros(n), 0.01, 0.0, dt, rng)[-1, 0])
    print("position error after 10 s (m):", accel_position(np.zeros(n), 0.05, 0.0, dt, rng)[1][-1, 0])
    print("position error from leaked gyro bias (m):", leaked_position(0.01, n, dt)[-1])
