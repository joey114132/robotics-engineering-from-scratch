# 레슨 10/01 테스트: LIPM 닫힌 해, 시상수, ZMP, capture point
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_lipm", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

H = 0.9
TC = np.sqrt(H / 9.81)
HALF_FOOT = 0.05


def test_time_constant_is_sqrt_h_over_g():
    assert np.isclose(m.time_constant(H), TC)
    assert np.isclose(m.time_constant(4 * H), 2 * TC)  # four times the height, twice as slow


def test_closed_form_matches_numerical_integration():
    t, x, v = m.simulate(0.02, 0.3, lambda t, x, v: 0.01, H, 1e-4, 0.8)
    xc, vc = m.lipm_state(0.02, 0.3, 0.01, t, H)
    assert np.allclose(x, xc, atol=1e-7) and np.allclose(v, vc, atol=1e-6)


def test_divergent_mode_grows_as_exp_t_over_tc():
    x, v = m.lipm_state(1.0, 1.0 / TC, 0.0, 2 * TC, H)  # v0 = x0 / Tc, foot at the origin
    assert np.isclose(x, np.exp(2.0)) and np.isclose(v, np.exp(2.0) / TC)


def test_zmp_of_the_motion_is_the_foot_position():
    x, v = m.lipm_state(0.0, 0.2, 0.03, 0.1, H)
    acc = (9.81 / H) * (x - 0.03)
    assert np.isclose(m.zmp(x, acc, H), 0.03)


def test_capture_point_is_constant_when_the_foot_is_on_it():
    xi0 = m.capture_point(0.0, 0.4, H)
    x, v = m.lipm_state(0.0, 0.4, xi0, 1.5, H)
    assert np.isclose(m.capture_point(x, v, H), xi0)
    assert abs(v) < 1e-2 and np.isclose(x, xi0, atol=5e-3)  # comes to rest over the foot


def test_ankle_only_cannot_recover_when_capture_point_is_outside_the_foot():
    assert m.capture_point(0.0, 0.4, H) > HALF_FOOT
    t, x, v = m.fall_or_recover(0.4, H, HALF_FOOT, step=False)
    assert x[-1] > 0.5 and v[-1] > 0


def test_stepping_onto_the_capture_point_recovers():
    t, x, v = m.fall_or_recover(0.4, H, HALF_FOOT, step=True)
    assert abs(v[-1]) < 5e-2 and x[-1] < 0.2


def test_ankle_only_recovers_a_small_push():
    t, x, v = m.fall_or_recover(0.1, H, HALF_FOOT, step=False)  # capture point 0.03 m, inside the foot
    assert abs(v[-1]) < 5e-2


def test_closed_form_agrees_with_scipy():
    integrate = pytest.importorskip("scipy.integrate")
    w2 = 9.81 / H
    s = integrate.solve_ivp(lambda t, y: [y[1], w2 * (y[0] - 0.01)], (0, 0.8), [0.02, 0.3], rtol=1e-10, atol=1e-12)
    xc, vc = m.lipm_state(0.02, 0.3, 0.01, 0.8, H)
    assert np.isclose(s.y[0, -1], xc, atol=1e-8) and np.isclose(s.y[1, -1], vc, atol=1e-7)
