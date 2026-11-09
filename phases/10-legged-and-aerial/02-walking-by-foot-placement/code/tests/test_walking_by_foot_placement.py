# 레슨 10/02 테스트: deadbeat 발 위치로 목표 속도에 도달하고, 짧은 걸음은 속도를 키운다
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_walk", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

H, T, VT = 0.9, 0.4, 0.6


def test_next_foot_gives_exact_target_speed_one_step_later():
    x, v, p = 0.1, 0.3, 0.0
    q = m.next_foot(x, v, VT, T, H)
    _, v2 = m.lipm_state(x, v, q, T, H)
    assert np.isclose(v2, VT)


def test_walker_reaches_target_speed_within_two_steps_from_rest():
    r = m.walk(6, T, H, VT)
    assert np.allclose(r["v_end"][1:], VT, atol=1e-9)


def test_steady_step_length_matches_closed_form():
    r = m.walk(8, T, H, VT)
    tc = np.sqrt(H / 9.81)
    # at steady state the CoM is symmetric about the support foot: x_rel = -Tc*v*tanh(T/2Tc) at touchdown
    expected = 2 * tc * VT * np.tanh(T / (2 * tc))
    assert np.isclose(np.diff(r["feet"])[-1], expected, rtol=1e-6)


def test_steps_scaled_too_short_make_the_speed_run_away():
    r = m.walk(8, T, H, VT, step_scale=0.6, x0=-0.05, v0=0.3)
    assert r["v_end"][-1] > 2 * VT and np.all(np.diff(r["v_end"][1:]) > 0)


def test_steps_scaled_too_long_make_the_walker_stall_and_reverse():
    r = m.walk(8, T, H, VT, step_scale=1.5, x0=-0.05, v0=0.3)
    assert np.any(r["v_end"] < 0)  # the CoM never gets over the foot and rolls backward


def test_a_walker_that_is_already_moving_converges_in_one_step():
    r = m.walk(6, T, H, VT, x0=-0.05, v0=0.3)
    assert np.allclose(r["v_end"][1:], VT, atol=1e-9) and np.all(np.diff(r["feet"])[1:] > 0)


def test_zero_target_speed_from_rest_does_not_move():
    r = m.walk(4, T, H, 0.0)
    assert np.allclose(r["x"], 0.0, atol=1e-12)


def test_trajectory_is_continuous_across_foot_switches():
    r = m.walk(5, T, H, VT)
    assert np.max(np.abs(np.diff(r["x"]))) < 0.02


def test_walk_matches_scipy_integration_of_the_first_step():
    integrate = pytest.importorskip("scipy.integrate")
    r = m.walk(3, T, H, VT)
    s = integrate.solve_ivp(lambda t, y: [y[1], 9.81 / H * (y[0] - 0.0)], (0, T), [0.0, 0.0], rtol=1e-10, atol=1e-12)
    assert np.isclose(r["x_end"][0], s.y[0, -1], atol=1e-8)
