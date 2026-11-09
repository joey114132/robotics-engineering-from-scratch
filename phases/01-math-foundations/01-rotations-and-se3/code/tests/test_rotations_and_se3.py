# 레슨 01/01 테스트: 회전행렬과 SE(3) 합성·역변환
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_rot_se3", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_rot_z_quarter_turn_maps_x_to_y():
    assert np.allclose(m.rot_z(np.pi / 2) @ [1, 0, 0], [0, 1, 0], atol=1e-12)


def test_composed_rotation_is_still_a_rotation():
    R = m.rot_x(0.3) @ m.rot_y(-1.1) @ m.rot_z(2.0)
    assert m.is_rotation(R)


def test_scaled_matrix_is_not_a_rotation():
    assert not m.is_rotation(1.01 * np.eye(3))


def test_rotation_order_matters():
    assert not np.allclose(m.rot_x(0.5) @ m.rot_z(0.7), m.rot_z(0.7) @ m.rot_x(0.5))


def test_invert_T_is_the_inverse():
    T = m.make_T(m.rot_y(0.4) @ m.rot_z(-0.9), [0.3, -0.2, 1.5])
    assert np.allclose(m.invert_T(T) @ T, np.eye(4), atol=1e-12)
    assert np.allclose(m.invert_T(T), np.linalg.inv(T), atol=1e-12)


def test_transform_point_applies_rotation_then_translation():
    T = m.make_T(m.rot_z(np.pi / 2), [1, 2, 3])
    assert np.allclose(m.transform_point(T, [1, 0, 0]), [1, 3, 3], atol=1e-12)


def test_rotation_order_example_from_the_diagram():
    x = np.array([1.0, 0, 0])
    assert np.allclose(m.rot_z(np.pi / 2) @ m.rot_x(np.pi / 2) @ x, [0, 1, 0], atol=1e-12)
    assert np.allclose(m.rot_x(np.pi / 2) @ m.rot_z(np.pi / 2) @ x, [0, 0, 1], atol=1e-12)


def test_reorthonormalize_repairs_drift_and_keeps_the_rotation():
    R = m.rot_y(0.7) @ m.rot_z(-0.2)
    drifted = R + 1e-3 * np.random.default_rng(0).normal(size=(3, 3))
    fixed = m.reorthonormalize(drifted)
    assert not m.is_rotation(drifted) and m.is_rotation(fixed)
    assert np.allclose(fixed, R, atol=5e-3)


def test_matches_scipy_when_available():
    spatial = __import__("pytest").importorskip("scipy.spatial.transform")
    R = spatial.Rotation.from_euler("z", 0.8).as_matrix()
    assert np.allclose(m.rot_z(0.8), R, atol=1e-12)
