# 레슨 07/04 테스트: alpha-tau 관계, 상보 필터 응답, 상수 bias 정상상태 오차 tau*b, 잡음 분산, 최적 tau
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_comp", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

DT = 0.01


def test_alpha_and_time_constant_are_inverses():
    for tau in (0.05, 0.5, 3.0):
        a = m.alpha(tau, DT)
        assert 0 < a < 1
        assert np.isclose(a * DT / (1 - a), tau)


def test_low_pass_and_high_pass_always_add_to_one():
    w = np.logspace(-2, 3, 30)
    lp, hp = m.responses(w, tau=0.5)
    assert np.allclose(lp + hp, 1.0)


def test_crossover_is_where_both_paths_have_equal_magnitude_one_over_sqrt_two():
    tau = 0.5
    lp, hp = m.responses(np.array([1 / tau]), tau)
    assert np.isclose(abs(lp[0]), 1 / np.sqrt(2)) and np.isclose(abs(hp[0]), 1 / np.sqrt(2))
    assert np.isclose(m.crossover_hz(tau), 1 / (2 * np.pi * tau))


def test_initial_error_falls_to_one_over_e_after_one_time_constant():
    tau, n = 1.0, 100  # tau / dt steps
    est = m.complementary(np.zeros((n, 1)), np.ones((n, 1)), DT, tau, theta0=0.0)
    assert np.isclose(1 - est[-1, 0], np.exp(-1), atol=0.01)


def test_constant_gyro_bias_leaves_a_steady_error_of_exactly_tau_times_bias():
    tau, b, n = 0.4, 0.02, 3000
    gyro = np.full((n, 1), b)  # robot is still at tilt 0.3
    acc = np.full((n, 1), 0.3)
    est = m.complementary(gyro, acc, DT, tau, theta0=0.3)
    assert np.isclose(est[-1, 0] - 0.3, tau * b, rtol=1e-6)


def test_white_accel_noise_is_reduced_by_the_low_pass_to_one_minus_a_over_one_plus_a():
    tau, sig, n, runs = 0.4, 0.05, 1500, 2000
    rng = np.random.default_rng(0)
    est = m.complementary(np.zeros((n, runs)), sig * rng.standard_normal((n, runs)), DT, tau)
    a = m.alpha(tau, DT)
    assert np.isclose(est[-1].var(), sig**2 * (1 - a) / (1 + a), rtol=0.08)


def test_fusion_beats_each_sensor_alone_on_a_moving_tilt():
    rng = np.random.default_rng(3)
    t = DT * np.arange(2000)[:, None]
    truth = 0.3 * np.sin(2 * np.pi * 0.3 * t)
    omega = 0.3 * 2 * np.pi * 0.3 * np.cos(2 * np.pi * 0.3 * t)
    gyro, acc = m.sensors(truth, omega, bias=0.01, sig_g=0.02, sig_a=0.05, rng=rng)
    est = m.complementary(gyro, acc, DT, 0.4, theta0=0.0)
    gyro_only = m.integrate(gyro, DT, 0.0)
    rmse = lambda x: np.sqrt(np.mean((x - truth) ** 2))  # noqa: E731
    assert rmse(est) < 0.3 * rmse(acc) and rmse(est) < 0.3 * rmse(gyro_only)


def test_predicted_rmse_matches_simulation_for_a_still_robot():
    tau, b, sa, n, runs = 0.8, 0.01, 0.05, 6000, 200
    rng = np.random.default_rng(5)
    gyro, acc = m.sensors(np.zeros((n, 1)), np.zeros((n, 1)), b, 0.0, sa, rng, runs=runs)
    est = m.complementary(gyro, acc, DT, tau, theta0=0.0)
    sim = np.sqrt(np.mean(est[n // 2 :] ** 2))
    assert np.isclose(sim, m.predicted_rmse(tau, DT, b, sa), rtol=0.08)


def test_best_time_constant_matches_the_closed_form_cube_root():
    b, sa = 0.01, 0.05
    taus = np.linspace(0.05, 3, 600)
    best = taus[np.argmin([m.predicted_rmse(t, DT, b, sa) for t in taus])]
    assert np.isclose(best, m.best_tau(DT, b, sa), rtol=0.05)
    assert 0.2 < best < 1.0
