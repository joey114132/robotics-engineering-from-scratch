# 레슨 01/03 테스트: Rodrigues, quaternion 이중 덮개, 부호 보정 slerp
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_quat", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

AX = [1.0, 2.0, -0.5]


def test_rodrigues_quarter_turn_about_z():
    assert np.allclose(m.rodrigues([0, 0, 1], np.pi / 2) @ [1, 0, 0], [0, 1, 0], atol=1e-12)


def test_rodrigues_is_a_rotation():
    R = m.rodrigues(AX, 1.3)
    assert np.allclose(R.T @ R, np.eye(3), atol=1e-12) and np.isclose(np.linalg.det(R), 1.0)


def test_quaternion_matches_rodrigues():
    q = m.quat_from_axis_angle(AX, 0.9)
    assert np.isclose(np.linalg.norm(q), 1.0)
    assert np.allclose(m.quat_to_R(q), m.rodrigues(AX, 0.9), atol=1e-12)


def test_q_and_minus_q_are_the_same_rotation():
    q = m.quat_from_axis_angle(AX, 2.0)
    assert np.allclose(m.quat_to_R(q), m.quat_to_R(-q), atol=1e-12)


def test_quat_mul_matches_matrix_product():
    a, b = m.quat_from_axis_angle(AX, 0.7), m.quat_from_axis_angle([0, 1, 0], -1.1)
    assert np.allclose(m.quat_to_R(m.quat_mul(a, b)), m.quat_to_R(a) @ m.quat_to_R(b), atol=1e-12)


def test_matrix_to_quaternion_round_trip_on_all_branches():
    for ax, ang in ((AX, 0.4), ([1, 0, 0], 3.0), ([0, 1, 0], 3.0), ([0, 0, 1], 3.1)):
        R = m.rodrigues(ax, ang)
        assert np.allclose(m.quat_to_R(m.R_to_quat(R)), R, atol=1e-12)


def test_slerp_without_fix_takes_the_long_way():
    q0 = m.quat_from_axis_angle([0, 0, 1], 0.0)
    q1 = -m.quat_from_axis_angle([0, 0, 1], 0.1)  # same rotation as +0.1 rad, opposite sign
    assert np.isclose(m.path_angle(q0, q1, fix=False), 2 * np.pi - 0.1, atol=1e-3)


def test_slerp_with_fix_takes_the_short_way():
    q0 = m.quat_from_axis_angle([0, 0, 1], 0.0)
    q1 = -m.quat_from_axis_angle([0, 0, 1], 0.1)
    assert np.isclose(m.path_angle(q0, q1, fix=True), 0.1, atol=1e-3)


def test_slerp_endpoints_and_midpoint():
    a, b = m.quat_from_axis_angle(AX, 0.2), m.quat_from_axis_angle(AX, 1.0)
    assert np.allclose(m.slerp(a, b, 0.0), a) and np.allclose(m.slerp(a, b, 1.0), b)
    assert np.allclose(m.slerp(a, b, 0.5), m.quat_from_axis_angle(AX, 0.6), atol=1e-12)


def test_matches_scipy_scalar_last_order():
    spatial = pytest.importorskip("scipy.spatial.transform")
    q = m.quat_from_axis_angle(AX, 0.9)
    R = spatial.Rotation.from_quat([q[1], q[2], q[3], q[0]]).as_matrix()  # SciPy is scalar-last
    assert np.allclose(R, m.quat_to_R(q), atol=1e-12)
