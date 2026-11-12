# 레슨 01/05 테스트: ZYX Euler 변환 왕복, 두 가지 표기, gimbal lock 에서 각속도 사상의 rank 하락
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_euler", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

D = np.pi / 180


def skew_vec(S):
    return np.array([S[2, 1], S[0, 2], S[1, 0]])


def test_round_trip_for_non_singular_angles():
    rng = np.random.default_rng(0)
    for _ in range(50):
        r, y = rng.uniform(-np.pi, np.pi, 2)
        p = rng.uniform(-80 * D, 80 * D)
        out = m.R_to_euler(m.euler_to_R(r, p, y))
        assert not out[3]
        assert np.allclose(out[:3], [r, p, y], atol=1e-9)


def test_single_axis_matches_hand_rotation():
    R = m.euler_to_R(0.0, 0.0, np.pi / 2)  # yaw 90 deg maps x to y
    assert np.allclose(R @ [1, 0, 0], [0, 1, 0], atol=1e-12)


def test_pitch_past_90_degrees_comes_back_with_roll_and_yaw_flipped_by_180():
    R = m.euler_to_R(0.0, 120 * D, 0.0)
    r, p, y, _ = m.R_to_euler(R)
    assert np.isclose(p, 60 * D)
    assert np.isclose(abs(r), np.pi) and np.isclose(abs(y), np.pi)


def test_every_orientation_has_a_second_spelling():
    a = (0.3, 0.5, -1.0)
    assert np.allclose(m.euler_to_R(*a), m.euler_to_R(*m.other_spelling(*a)), atol=1e-12)


def test_at_gimbal_lock_roll_and_yaw_are_one_angle():
    # yaw and roll both turn the same axis at pitch +90 deg: only yaw - roll matters
    R1 = m.euler_to_R(0.4, 90 * D, 0.9)
    assert np.allclose(R1, m.euler_to_R(0.0, 90 * D, 0.5), atol=1e-12)
    r, p, y, locked = m.R_to_euler(R1)
    assert locked and r == 0.0
    assert np.allclose(m.euler_to_R(r, p, y), R1, atol=1e-12)


def test_rate_map_determinant_is_cos_pitch():
    for p in (0.0, 0.7, -1.2, 1.5):
        assert np.isclose(np.linalg.det(m.rate_map(p, 0.4)), np.cos(p))


def test_rate_map_matches_finite_difference_of_the_rotation():
    q, qd, h = np.array([0.3, 0.6, -0.5]), np.array([0.2, -0.4, 0.7]), 1e-6
    R0, R1 = m.euler_to_R(*q), m.euler_to_R(*(q + h * qd))
    omega = skew_vec((R1 - R0) / h @ R0.T)
    assert np.allclose(omega, m.rate_map(q[1], q[2]) @ qd, atol=1e-5)


def test_rate_map_loses_rank_at_pitch_90():
    E = m.rate_map(90 * D, 0.3)
    assert np.linalg.matrix_rank(E, tol=1e-9) == 2
    with pytest.raises(ValueError, match="gimbal"):
        m.euler_rates([1.0, 0, 0], 90 * D, 0.3)


def test_needed_euler_rates_blow_up_like_one_over_cos_pitch():
    n1 = np.linalg.norm(m.euler_rates([1.0, 0, 0], 80 * D, 0.0))
    n2 = np.linalg.norm(m.euler_rates([1.0, 0, 0], 89 * D, 0.0))
    assert n2 / n1 > 8
