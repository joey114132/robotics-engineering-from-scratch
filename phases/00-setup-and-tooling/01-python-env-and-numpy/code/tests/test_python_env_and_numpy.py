# 레슨 00/01 테스트: shape 검사, 단위 가드, 도와 라디안을 섞었을 때의 오류
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_env", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_check_shape_accepts_matching_and_wildcard():
    assert m.check_shape(np.zeros((5, 3)), (None, 3), "pts").shape == (5, 3)
    assert m.check_shape([0.0, 1.0, 2.0], (3,), "q").shape == (3,)


def test_check_shape_names_the_argument_in_the_error():
    with pytest.raises(ValueError, match="pts.*expected.*3.*got.*3, 5"):
        m.check_shape(np.zeros((3, 5)), (None, 3), "pts")


def test_check_shape_catches_the_column_vector_broadcast_trap():
    a, b = np.zeros(3), np.zeros((3, 1))
    assert (a - b).shape == (3, 3)  # numpy silently builds a 3x3
    with pytest.raises(ValueError):
        m.check_shape(b, (3,), "b")


def test_degree_radian_round_trip():
    q = np.array([-180.0, 0.0, 90.0, 359.0])
    assert np.allclose(m.rad2deg(m.deg2rad(q)), q)
    assert np.isclose(m.deg2rad(180.0), np.pi)


def test_unit_guard_flags_degrees_but_not_radians():
    assert m.looks_like_degrees([0.0, 90.0, -45.0])
    assert not m.looks_like_degrees([0.0, 1.57, -0.8])
    with pytest.raises(ValueError, match="degrees"):
        m.joint_angles([0.0, 90.0])


def test_cos_of_degrees_is_the_wrong_answer():
    assert abs(np.cos(m.deg2rad(90.0))) < 1e-12
    assert abs(np.cos(90.0) - 0.0) > 0.4  # cos(90 rad) = -0.448


def test_rotate_points_matches_hand_calculation_and_checks_shape():
    out = m.rotate_z(np.array([[1.0, 0.0, 0.0]]), np.pi / 2)
    assert np.allclose(out, [[0.0, 1.0, 0.0]], atol=1e-12)
    with pytest.raises(ValueError):
        m.rotate_z(np.zeros((3, 5)), 0.1)


def test_rotation_preserves_length():
    pts = np.random.default_rng(0).normal(size=(20, 3))
    out = m.rotate_z(pts, 0.7)
    assert np.allclose(np.linalg.norm(out, axis=1), np.linalg.norm(pts, axis=1))
