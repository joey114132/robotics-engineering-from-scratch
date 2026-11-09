# 레슨 00/02 테스트: numpy 진자 시뮬레이터의 주기, 에너지, 시간 간격 효과와 MuJoCo 교차 확인
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_pendulum", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

T0 = 2 * np.pi * np.sqrt(1.0 / m.G)


def period(theta0, dt=0.001, seconds=20.0, **kw):
    return m.measure_period(m.simulate(theta0, dt, seconds, **kw), dt)


def test_small_angle_period_matches_formula():
    assert np.isclose(period(0.05), T0, rtol=0.005)


def test_large_swing_is_slower_by_the_series_correction():
    assert np.isclose(period(0.5), T0 * (1 + 0.5**2 / 16), rtol=0.01)


def test_period_scales_with_square_root_of_length():
    assert np.isclose(period(0.05, L=4.0) / period(0.05, L=1.0), 2.0, rtol=0.01)


def test_semi_implicit_energy_stays_bounded_but_explicit_blows_up():
    dt = 0.01
    e_semi = m.energy(m.simulate(0.5, dt, 20.0, scheme="semi"), dt)
    e_expl = m.energy(m.simulate(0.5, dt, 20.0, scheme="explicit"), dt)
    assert e_semi.max() / e_semi[0] < 1.05
    assert e_expl[-1] / e_expl[0] > 2.0


def test_smaller_step_gives_a_smaller_period_error():
    exact = T0 * (1 + 0.5**2 / 16 + 11 * 0.5**4 / 3072)  # amplitude series, so the reference is the true period
    err = lambda dt: abs(period(0.5, dt=dt) - exact)
    assert err(0.02) > 4 * err(0.005)


def test_rest_position_stays_at_rest():
    th = m.simulate(0.0, 0.001, 1.0)
    assert np.allclose(th, 0.0)


def test_mujoco_pendulum_period_matches_our_simulator():
    pytest.importorskip("mujoco")
    mj = m.mujoco_period(0.05, 0.001, 20.0)
    assert np.isclose(mj, period(0.05), rtol=0.005)
