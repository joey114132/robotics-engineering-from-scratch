# 레슨 07/03 테스트: gyro bias 의 각도 drift 는 선형, accel bias 의 위치 drift 는 제곱, 기울기 오차가 새면 세제곱
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_imu", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

DT, N = 0.01, 1000  # 100 Hz for 10 s
RNG = np.random.default_rng(0)


def test_gyro_bias_gives_angle_error_equal_to_bias_times_time():
    err = m.gyro_angle(np.zeros(N), bias=0.02, sigma=0.0, dt=DT, rng=RNG)[:, 0]
    assert np.isclose(err[-1], 0.02 * N * DT)
    assert np.allclose(err, 0.02 * DT * np.arange(1, N + 1))


def test_angle_error_does_not_depend_on_how_the_robot_really_turns():
    omega = 0.5 * np.sin(np.linspace(0, 6, N))
    est = m.gyro_angle(omega, bias=0.02, sigma=0.0, dt=DT, rng=RNG)[:, 0]
    truth = np.cumsum(omega) * DT
    assert np.allclose(est - truth, 0.02 * DT * np.arange(1, N + 1))


def test_accel_bias_gives_position_error_of_half_bias_times_time_squared():
    _, p = m.accel_position(np.zeros(N), bias=0.05, sigma=0.0, dt=DT, rng=RNG)
    exact = 0.05 * DT**2 * N * (N + 1) / 2  # the discrete sum
    assert np.isclose(p[-1, 0], exact)
    assert np.isclose(p[-1, 0], m.position_drift(0.05, N * DT), rtol=1e-3)


def test_doubling_the_time_doubles_angle_error_and_quadruples_position_error():
    a = m.gyro_angle(np.zeros(2 * N), 0.02, 0.0, DT, RNG)[:, 0]
    _, p = m.accel_position(np.zeros(2 * N), 0.05, 0.0, DT, RNG)
    assert np.isclose(a[2 * N - 1] / a[N - 1], 2.0)
    assert np.isclose(p[2 * N - 1, 0] / p[N - 1, 0], 4.0, rtol=0.01)


def test_gyro_noise_alone_gives_a_random_walk_with_std_sigma_sqrt_dt_t():
    err = m.gyro_angle(np.zeros(N), bias=0.0, sigma=0.5, dt=DT, rng=np.random.default_rng(1), runs=4000)
    assert np.isclose(err[-1].std(), 0.5 * np.sqrt(DT * (N * DT)), rtol=0.05)


def test_one_degree_of_tilt_error_fakes_0p17_m_per_s2_and_8p6_m_in_ten_seconds():
    a = m.G * np.sin(np.radians(1.0))
    assert np.isclose(a, 0.171, atol=0.001)
    assert np.isclose(m.position_drift(a, 10.0), 8.56, atol=0.02)


def test_gyro_bias_leaking_through_gravity_grows_with_the_cube_of_time():
    p = m.leaked_position(bias_g=0.001, steps=N, dt=DT)
    exact = m.G * 0.001 * DT**3 * N * (N + 1) * (N + 2) / 6  # small-angle discrete sum
    assert np.isclose(p[-1], exact, rtol=1e-3)
    assert np.isclose(p[-1], m.G * 0.001 * (N * DT) ** 3 / 6, rtol=0.01)
    p2 = m.leaked_position(bias_g=0.001, steps=2 * N, dt=DT)
    assert np.isclose(p2[-1] / p[-1], 8.0, rtol=0.02)
