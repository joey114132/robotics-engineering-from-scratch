# 레슨 10/03 테스트: 평면 쿼드로터의 호버 추력, 자유낙하, 추력 계단, 토크 계단과 기울임 지연
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_quad", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

M, I, G = 0.5, 0.004, 9.81


def run(state0, T_fn, tau_fn, t_end, dt=1e-3):
    return m.simulate(np.array(state0, float), lambda t, s: (T_fn(t, s), tau_fn(t, s)), M, I, dt, t_end)


def test_hover_thrust_is_weight_and_gives_zero_acceleration():
    T = m.hover_thrust(M)
    assert np.isclose(T, M * G)
    assert np.allclose(m.deriv(np.zeros(6), T, 0.0, M, I), 0.0)


def test_free_fall_matches_half_g_t_squared():
    t, s = run(np.zeros(6), lambda t, s: 0.0, lambda t, s: 0.0, 0.5)
    assert np.isclose(s[-1, 1], -0.5 * G * 0.5**2, rtol=1e-9)
    assert np.isclose(s[-1, 0], 0.0)


def test_thrust_step_moves_only_vertically():
    dT = 0.1 * M * G
    t, s = run(np.zeros(6), lambda t, s: M * G + dT, lambda t, s: 0.0, 0.5)
    assert np.isclose(s[-1, 1], dT / (2 * M) * 0.5**2, rtol=1e-6)
    assert np.allclose(s[:, 0], 0.0) and np.allclose(s[:, 2], 0.0)


def test_torque_step_small_angle_matches_closed_form():
    tau, T_end = 0.001, 0.5
    t, s = run(np.zeros(6), lambda t, s: M * G, lambda t, s: tau, T_end)
    th, x = m.linear_torque_step(T_end, tau, I)
    assert np.isclose(s[-1, 2], th, rtol=1e-6) and abs(th) < 0.1
    assert np.isclose(s[-1, 0], x, rtol=0.02)


def test_pitch_must_tilt_before_the_body_moves_sideways():
    t, s = run(np.zeros(6), lambda t, s: M * G, lambda t, s: 0.002, 1.0)
    t_tilt = t[np.argmax(np.degrees(s[:, 2]) > 1.0)]  # first time pitch passes 1 degree
    t_move = t[np.argmax(s[:, 0] > 0.01)]  # first time x passes 1 cm
    assert 0 < t_tilt < t_move


def test_tilted_at_hover_thrust_loses_height():
    az = m.deriv(np.array([0, 0, 0.3, 0, 0, 0.0]), M * G, 0.0, M, I)[4]
    assert az < 0 and np.isclose(az, G * (np.cos(0.3) - 1))


def test_thrust_over_cos_theta_holds_height_and_accelerates_sideways():
    th = 0.3
    d = m.deriv(np.array([0, 0, th, 0, 0, 0.0]), M * G / np.cos(th), 0.0, M, I)
    assert np.isclose(d[4], 0.0, atol=1e-12) and np.isclose(d[3], G * np.tan(th))


def test_energy_is_conserved_with_zero_inputs_and_no_rotation():
    t, s = run([0, 0, 0, 1.0, 2.0, 0], lambda t, s: 0.0, lambda t, s: 0.0, 0.4)
    e = lambda q: 0.5 * M * (q[3] ** 2 + q[4] ** 2) + M * G * q[1]
    assert np.isclose(e(s[0]), e(s[-1]), rtol=1e-9)


def test_simulation_agrees_with_scipy():
    integrate = pytest.importorskip("scipy.integrate")
    f = lambda t, y: m.deriv(y, 0.9 * M * G, 0.001, M, I)
    r = integrate.solve_ivp(f, (0, 1.0), np.zeros(6), rtol=1e-10, atol=1e-12)
    t, s = run(np.zeros(6), lambda t, s: 0.9 * M * G, lambda t, s: 0.001, 1.0)
    assert np.allclose(s[-1], r.y[:, -1], atol=1e-7)
