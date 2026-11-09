# 레슨 12/02 테스트: explicit Euler 와 semi-implicit Euler 의 에너지 거동, 그리고 time step 에 따라 접촉 결과가 달라지는 지점
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_timestep", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

W = 2.0
LIN = lambda x: -(W**2) * x


def _energy_path(method, dt, n):
    x, v, out = 1.0, 0.3, []
    for _ in range(n):
        out.append((x, v))
        x, v = m.step(method, x, v, LIN, dt)
    return np.array(out)


def test_explicit_euler_multiplies_linear_oscillator_energy_by_one_plus_w2dt2_each_step():
    dt, n = 0.01, 200
    s = _energy_path("euler", dt, n)
    e = 0.5 * s[:, 1] ** 2 + 0.5 * W**2 * s[:, 0] ** 2
    assert np.allclose(e[1:] / e[:-1], 1 + (W * dt) ** 2, rtol=1e-9)


def test_semi_implicit_euler_conserves_a_shadow_energy_exactly():
    dt = 0.05
    s = _energy_path("semi", dt, 400)
    h = 0.5 * s[:, 1] ** 2 + 0.5 * W**2 * s[:, 0] ** 2 - 0.5 * dt * W**2 * s[:, 0] * s[:, 1]
    assert np.ptp(h) < 1e-9


def test_semi_implicit_is_stable_below_two_over_w_and_unstable_above():
    for dt, stable in ((1.9 / W, True), (2.1 / W, False)):
        s = _energy_path("semi", dt, 2000)
        assert (np.abs(s[:, 0]).max() < 10) == stable


def test_pendulum_drift_is_ten_times_smaller_with_semi_implicit_at_the_same_step():
    assert m.pendulum_drift("euler", 0.01) > 10 * m.pendulum_drift("semi", 0.01)


def test_semi_implicit_drift_scales_with_the_step_size():
    ratio = m.pendulum_drift("semi", 0.004) / m.pendulum_drift("semi", 0.002)
    assert 1.8 < ratio < 2.2


def test_tiny_step_rebound_returns_to_the_drop_height():
    assert abs(m.rebound_height("semi", 1e-5) - m.H0) / m.H0 < 0.01


def test_explicit_euler_creates_energy_in_a_stiff_contact():
    assert m.rebound_height("euler", 1e-3) > 1.3 * m.H0


def test_a_step_size_that_looks_fine_changes_the_contact_result_materially():
    assert abs(m.rebound_height("semi", 0.003) - m.H0) / m.H0 < 0.05
    assert m.rebound_height("semi", 0.019) > 3 * m.H0


def test_a_huge_step_throws_the_ball_far_above_where_it_started():
    assert m.rebound_height("euler", 0.1) > 10 * m.H0
