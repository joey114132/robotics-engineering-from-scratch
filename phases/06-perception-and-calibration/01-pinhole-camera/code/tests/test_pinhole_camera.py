# 레슨 06/01 테스트: 핀홀 투영과 역투영, 깊이·픽셀 오차가 3D 위치 오차로 바뀌는 크기
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_pinhole", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

K = dict(fx=600.0, fy=600.0, cx=320.0, cy=240.0)


def test_point_on_optical_axis_lands_on_principal_point():
    assert np.allclose(m.project([[0, 0, 2.0]], **K), [[320, 240]])


def test_projection_matches_hand_calculation():
    uv = m.project([[0.1, -0.05, 1.0]], **K)
    assert np.allclose(uv, [[380.0, 210.0]])


def test_unproject_inverts_project():
    P = np.array([[0.3, -0.2, 1.5], [-0.1, 0.4, 0.8]])
    assert np.allclose(m.unproject(m.project(P, **K), P[:, 2], **K), P)


def test_doubling_distance_halves_the_pixel_offset():
    near, far = m.project([[0.2, 0, 1.0]], **K)[0, 0], m.project([[0.2, 0, 2.0]], **K)[0, 0]
    assert np.isclose((near - 320) / (far - 320), 2.0)


def test_depth_error_off_axis_shifts_the_point_sideways_by_dz_times_ray_slope():
    # pixel 200 px right of the principal point, depth 0.10 m too large: 0.10 * 200/600 m sideways
    err = m.position_error([520.0, 240.0], 1.0, dz=0.10, du=0.0, **K)
    assert np.isclose(err["lateral"], 0.10 * 200 / 600)
    assert np.isclose(err["total"], 0.10 * np.sqrt(1 + (200 / 600) ** 2))


def test_depth_error_on_the_optical_axis_is_purely_along_the_ray():
    err = m.position_error([320.0, 240.0], 1.0, dz=0.10, du=0.0, **K)
    assert np.isclose(err["lateral"], 0.0) and np.isclose(err["total"], 0.10)


def test_pixel_error_grows_linearly_with_distance():
    e1 = m.position_error([320.0, 240.0], 1.0, dz=0.0, du=1.0, **K)["total"]
    e3 = m.position_error([320.0, 240.0], 3.0, dz=0.0, du=1.0, **K)["total"]
    assert np.isclose(e3 / e1, 3.0) and np.isclose(e1, 1.0 / 600)


def test_point_behind_the_camera_is_rejected():
    import pytest
    with pytest.raises(ValueError, match="behind"):
        m.project([[0, 0, -1.0]], **K)


def test_matches_opencv_project_points_when_available():
    cv2 = __import__("pytest").importorskip("cv2")
    P = np.array([[0.3, -0.2, 1.5], [-0.1, 0.4, 0.8]])
    Km = np.array([[600.0, 0, 320], [0, 600, 240], [0, 0, 1]])
    ref, _ = cv2.projectPoints(P, np.zeros(3), np.zeros(3), Km, None)
    assert np.allclose(m.project(P, **K), ref.reshape(-1, 2))
