# 레슨 06/02 테스트: 평면 타깃 homography(DLT)와 선형 최소제곱으로 내부 파라미터를 복원한다
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_calib", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

K = dict(fx=620.0, fy=580.0, cx=330.0, cy=235.0)


def calibrate(n_views, noise, seed):
    views = m.make_views(K, n_views, noise, seed)
    return m.calibrate([m.homography_dlt(xy, uv) for xy, uv in views])


def test_dlt_recovers_the_true_homography_without_noise():
    xy, uv = m.make_views(K, 1, 0.0, 1)[0]
    H = m.homography_dlt(xy, uv)
    proj = H @ np.vstack([xy.T, np.ones(len(xy))])
    assert np.allclose((proj[:2] / proj[2]).T, uv, atol=1e-6)


def test_noiseless_calibration_recovers_all_four_intrinsics():
    est = calibrate(5, 0.0, 2)
    for k, v in K.items():
        assert np.isclose(est[k], v, rtol=1e-6), k


def test_more_noise_gives_more_intrinsics_error():
    def err(s):
        return np.median([abs(calibrate(6, s, i)["fx"] - K["fx"]) for i in range(40)])
    assert err(1.0) > 3 * err(0.1)


def test_more_views_reduce_the_error():
    def err(n):
        return np.median([abs(calibrate(n, 1.0, i)["fx"] - K["fx"]) for i in range(40)])
    assert err(12) < err(3)


def test_views_that_only_translate_are_rejected_as_degenerate():
    views = m.make_views(K, 4, 0.0, 3, tilt=0.0)
    with pytest.raises(ValueError, match="degenerate"):
        m.calibrate([m.homography_dlt(xy, uv) for xy, uv in views])


def test_pixel_error_is_zero_for_the_true_intrinsics_and_grows_with_focal_error():
    assert m.pixel_error(K, K) == 0.0
    off = dict(K, fx=K["fx"] * 1.01)
    assert m.pixel_error(off, K) > 0.5


def test_matches_opencv_calibrate_camera_when_available():
    cv2 = pytest.importorskip("cv2")
    views = m.make_views(K, 6, 0.0, 4)
    obj = [np.hstack([xy, np.zeros((len(xy), 1))]).astype(np.float32) for xy, _ in views]
    img = [uv.astype(np.float32).reshape(-1, 1, 2) for _, uv in views]
    flags = cv2.CALIB_ZERO_TANGENT_DIST | cv2.CALIB_FIX_K1 | cv2.CALIB_FIX_K2 | cv2.CALIB_FIX_K3
    _, Km, *_ = cv2.calibrateCamera(obj, img, (660, 480), None, None, flags=flags)
    assert np.isclose(Km[0, 0], K["fx"], rtol=1e-2) and np.isclose(Km[1, 2], K["cy"], rtol=1e-2)


def test_linear_solution_error_is_several_times_the_pixel_noise_with_few_views():
    errs = []
    for i in range(30):
        try:
            errs.append(m.pixel_error(calibrate(3, 1.0, i), K))
        except ValueError:
            pass
    assert np.median(errs) > 3.0
