# 레슨 06/04 테스트: AX = XB 를 회전 먼저, 이동 나중의 최소제곱으로 풀고 한 축 운동의 한계를 확인한다
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_handeye", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

X = m.make_T(m.rodrigues(np.array([0.3, -0.5, 0.8])), [0.05, 0.03, 0.08])


def errors(spread, noise_deg=0.0, noise_m=0.0, seed=0, n=12):
    As, Bs = m.make_motions(X, n, spread, noise_deg, noise_m, seed)
    Xe, _ = m.solve_hand_eye(As, Bs)
    return m.pose_error(Xe, X)


def test_true_x_satisfies_ax_equals_xb_for_generated_motions():
    As, Bs = m.make_motions(X, 6, 60.0, seed=1)
    assert all(np.allclose(A @ X, X @ B, atol=1e-9) for A, B in zip(As, Bs))


def test_noiseless_motions_about_several_axes_recover_x_exactly():
    rot, trans = errors(60.0)
    assert rot < 1e-9 and trans < 1e-9


def test_rotation_part_is_a_proper_rotation_even_when_the_problem_is_degenerate():
    As, Bs = m.make_motions(X, 8, 0.0, 0.1, 0.001, seed=2)
    R = m.solve_hand_eye(As, Bs)[0][:3, :3]
    assert np.allclose(R @ R.T, np.eye(3), atol=1e-9) and np.isclose(np.linalg.det(R), 1.0)


def test_more_noise_gives_more_error():
    lo = np.median([errors(60.0, 0.1, 0.0005, s)[0] for s in range(20)])
    hi = np.median([errors(60.0, 0.5, 0.0025, s)[0] for s in range(20)])
    assert hi > 2 * lo


def test_single_axis_motions_cannot_see_the_translation_along_that_axis():
    # all rotations about z: the z component of the camera offset (0.08 m) is invisible
    rot, trans = errors(0.0)
    assert trans > 0.07


def test_single_axis_rotation_is_much_worse_than_multi_axis_under_the_same_noise():
    one = np.median([errors(0.0, 0.2, 0.001, s)[0] for s in range(20)])
    many = np.median([errors(60.0, 0.2, 0.001, s)[0] for s in range(20)])
    assert one > 5 * many


def test_observability_ratio_collapses_for_one_axis():
    s_one = m.solve_hand_eye(*m.make_motions(X, 10, 0.0, seed=3))[1]
    s_many = m.solve_hand_eye(*m.make_motions(X, 10, 60.0, seed=3))[1]
    assert s_one[1] / s_one[0] < 1e-6 and s_many[1] / s_many[0] > 0.1


def test_fewer_than_two_motions_is_rejected():
    As, Bs = m.make_motions(X, 1, 60.0, seed=0)
    with pytest.raises(ValueError, match="2 motions"):
        m.solve_hand_eye(As, Bs)


def test_matches_opencv_calibrate_hand_eye_when_available():
    cv2 = pytest.importorskip("cv2")
    As, _ = m.make_motions(X, 9, 60.0, seed=4)
    T_bt = m.make_T(m.rodrigues(np.array([0.1, 0.2, -0.3])), [0.6, 0.1, -0.2])
    grip = [np.eye(4)]
    for A in As:
        grip.append(grip[-1] @ A)
    cam = [np.linalg.inv(X) @ np.linalg.inv(g) @ T_bt for g in grip]  # target in camera frame
    R, t = cv2.calibrateHandEye([g[:3, :3] for g in grip], [g[:3, 3] for g in grip],
                                [c[:3, :3] for c in cam], [c[:3, 3] for c in cam], method=cv2.CALIB_HAND_EYE_TSAI)
    assert m.pose_error(m.make_T(R, t.ravel()), X)[0] < 0.5
