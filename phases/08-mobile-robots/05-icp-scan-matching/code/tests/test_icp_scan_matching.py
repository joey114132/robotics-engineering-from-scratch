# 레슨 08/05 테스트: Kabsch 정확 복원, ICP 수렴과 단조 감소, 큰 초기 오차와 직선 벽에서의 예측 가능한 실패
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_icp", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def rot(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


def pose_error(R, t, R_true, t_true):
    return np.linalg.norm(t - t_true) + abs(np.arctan2((R @ R_true.T)[1, 0], (R @ R_true.T)[0, 0]))


def scene(angle, shift, spacing=0.05, phase=0.5):
    """Reference scan, and the same room seen from a pose offset by (angle, shift) with different sample points."""
    ref = m.room(spacing, 0.0)
    cur = m.room(spacing, phase)
    R_true = rot(angle)
    t_true = np.asarray(shift, float)
    moved = (cur - t_true) @ R_true  # the inverse motion: ICP must map moved back onto ref
    return ref, moved, R_true, t_true  # the map moved -> ref is R_true @ p + t_true


def test_kabsch_recovers_exact_transform_from_known_pairs():
    P = np.random.default_rng(0).uniform(-1, 1, (30, 2))
    R_true, t_true = rot(0.7), np.array([0.4, -1.2])
    R, t = m.kabsch(P, P @ R_true.T + t_true)
    assert np.allclose(R, R_true, atol=1e-12) and np.allclose(t, t_true, atol=1e-12)


def test_kabsch_returns_a_rotation_not_a_reflection():
    P = np.random.default_rng(1).uniform(-1, 1, (3, 2))
    Q = P * [1, -1]  # a mirror image: best orthogonal fit is a reflection
    R, _ = m.kabsch(P, Q)
    assert np.isclose(np.linalg.det(R), 1.0) and np.allclose(R @ R.T, np.eye(2))


def test_icp_is_exact_when_every_point_still_sits_closest_to_its_twin():
    ref, moved, R_true, t_true = scene(0.002, [0.01, -0.01], phase=0.0)  # every point moves under half the 0.05 m spacing
    R, t, errs = m.icp(moved, ref)
    assert pose_error(R, t, R_true, t_true) < 1e-6 and errs[-1] < 1e-9


def test_once_the_offset_exceeds_the_spacing_matches_go_wrong_and_exactness_is_lost():
    ref, moved, R_true, t_true = scene(0.2, [0.3, -0.2], phase=0.0)  # offset 6 spacings, identical sample points
    err = pose_error(*m.icp(moved, ref)[:2], R_true, t_true)
    assert 1e-3 < err < 0.1  # close, never exact


def test_icp_with_different_sample_points_is_accurate_to_about_the_point_spacing():
    ref, moved, R_true, t_true = scene(0.2, [0.3, -0.2])  # spacing 0.05 m
    R, t, errs = m.icp(moved, ref)
    assert pose_error(R, t, R_true, t_true) < 0.05


def test_icp_error_never_rises():
    ref, moved, *_ = scene(0.3, [0.2, 0.1])
    errs = m.icp(moved, ref)[2]
    assert np.all(np.diff(errs) <= 1e-12) and errs[-1] < 0.5 * errs[0]


def test_icp_fails_from_a_large_rotation_and_reports_a_bad_fit():
    ref, moved, R_true, t_true = scene(2.6, [0.0, 0.0])
    R, t, errs = m.icp(moved, ref)
    assert pose_error(R, t, R_true, t_true) > 0.5  # a local minimum, not the answer


def test_basin_is_wide_for_small_rotations_and_closes_for_large_ones():
    ok = [pose_error(*m.icp(scene(a, [0, 0])[1], scene(a, [0, 0])[0])[:2], *scene(a, [0, 0])[2:]) < 0.05 for a in (0.1, 0.4)]
    assert all(ok)


def test_a_single_straight_wall_cannot_fix_sliding_along_it():
    wall = np.column_stack([np.linspace(0, 5, 200), np.zeros(200)])
    moved = wall + [0.8, 0.3]  # 0.8 along the wall, 0.3 across it
    R, t, _ = m.icp(moved, wall)
    fixed = moved @ R.T + t
    assert abs(fixed[:, 1].mean()) < 1e-6   # across the wall: solved
    assert abs(fixed[:, 0].mean() - wall[:, 0].mean()) > 0.1  # along the wall: left unsolved
