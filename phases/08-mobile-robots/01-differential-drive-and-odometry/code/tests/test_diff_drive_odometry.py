# 레슨 08/01 테스트: 차동 구동 운동학, dead reckoning, 바퀴 반지름과 윤거 오차의 효과
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_diffdrive", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

R, B, DT = 0.05, 0.30, 0.01


def test_equal_wheel_speeds_drive_straight():
    v, w = m.wheels_to_twist(10.0, 10.0, R, B)
    assert np.isclose(v, R * 10.0) and np.isclose(w, 0.0)


def test_opposite_wheel_speeds_spin_in_place():
    v, w = m.wheels_to_twist(-4.0, 4.0, R, B)
    assert np.isclose(v, 0.0) and np.isclose(w, 2 * R * 4.0 / B)


def test_twist_to_wheels_round_trip():
    wl, wr = m.twist_to_wheels(0.4, 0.7, R, B)
    assert np.allclose(m.wheels_to_twist(wl, wr, R, B), (0.4, 0.7))


def test_straight_run_distance():
    wl = wr = np.full(200, 8.0)
    x, y, th = m.dead_reckon(wl, wr, DT, R, B)[-1]
    assert np.isclose(x, R * 8.0 * 2.0) and np.isclose(y, 0.0) and np.isclose(th, 0.0)


def test_full_circle_returns_to_start():
    v, w = 0.5, 1.0
    n = int(round(2 * np.pi / w / DT))
    wl, wr = m.twist_to_wheels(v, w * 2 * np.pi / (n * DT), R, B)
    p = m.dead_reckon(np.full(n, wl), np.full(n, wr), DT, R, B)
    assert np.allclose(p[-1, :2], 0.0, atol=1e-9)


def test_radius_error_scales_distance():
    wl = wr = np.full(300, 6.0)
    true = m.dead_reckon(wl, wr, DT, R * 1.02, B)[-1, 0]
    est = m.dead_reckon(wl, wr, DT, R, B)[-1, 0]
    assert np.isclose(true / est, 1.02)


def test_track_error_scales_turn_angle():
    wl, wr = m.square_wheels(2.0, 0.5, DT, R, B)
    true_b = B * 1.01
    th = m.dead_reckon(wl, wr, DT, R, true_b)[:, 2]
    n_side = 400
    n_turn = (len(wl) - 4 * n_side) // 4
    first_turn_end = th[n_side + n_turn]
    assert np.isclose(first_turn_end, (np.pi / 2) * B / true_b, atol=1e-9)


def test_nominal_model_closes_the_square_and_wrong_model_does_not():
    wl, wr = m.square_wheels(2.0, 0.5, DT, R, B)
    assert m.closure_error(wl, wr, DT, R, B) < 1e-9
    assert m.closure_error(wl, wr, DT, R, B * 1.02) > 0.1


def test_closure_error_matches_the_four_corner_formula():
    wl, wr = m.square_wheels(2.0, 0.5, DT, R, B)
    k = 1.02
    alpha = (np.pi / 2) / k
    expect = 2.0 * abs(sum(np.exp(1j * alpha * i) for i in range(4)))
    assert np.isclose(m.closure_error(wl, wr, DT, R, B * k), expect, rtol=1e-6)
