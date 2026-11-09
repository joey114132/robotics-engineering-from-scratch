# 레슨 08/04 테스트: lookahead 점, 곡률 공식, 경로 추종, lookahead 거리에 따른 코너 절단과 진동
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_pp", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

CORNERS = [(0, 0), (10, 0), (10, 10)]
PATH = m.dense(CORNERS)


def corner_cut(t):
    return np.linalg.norm(t[:, :2] - [10, 0], axis=1).min()


def leg1_changes(ld, tau=0.4):
    t = m.follow(CORNERS, ld, tau=tau)
    return m.sign_changes(t[t[:, 0] < 8][:, 1])


def test_dense_path_keeps_the_corners_and_spacing():
    assert np.allclose(PATH[0], [0, 0]) and np.allclose(PATH[-1], [10, 10])
    assert np.linalg.norm(np.diff(PATH, axis=0), axis=1).max() < 0.021


def test_lookahead_point_on_a_straight_path_is_ld_ahead():
    p = m.lookahead_point(PATH, np.array([3.0, 0.0]), 1.5)
    assert np.allclose(p, [4.5, 0.0], atol=0.03)


def test_lookahead_point_is_just_beyond_ld_from_an_offset_robot():
    pos = np.array([3.0, 0.5])
    d = np.linalg.norm(m.lookahead_point(PATH, pos, 1.0) - pos)
    assert 1.0 <= d < 1.03


def test_target_straight_ahead_gives_zero_curvature_and_sides_give_signs():
    pose = np.array([0.0, 0.0, 0.0])
    assert m.curvature(pose, np.array([2.0, 0.0])) == 0.0
    assert m.curvature(pose, np.array([2.0, 1.0])) > 0
    assert m.curvature(pose, np.array([2.0, -1.0])) < 0


def test_curvature_is_two_sin_alpha_over_distance():
    a, d = 0.4, 1.7
    k = m.curvature(np.array([1.0, 2.0, 0.3]), np.array([1.0, 2.0]) + d * np.array([np.cos(0.3 + a), np.sin(0.3 + a)]))
    assert np.isclose(k, 2 * np.sin(a) / d)


def test_the_commanded_circle_passes_through_the_target():
    a, d = 0.5, 2.0
    k = 2 * np.sin(a) / d
    s = 2 * a / k  # arc length: the chord turns by 2a
    end = np.array([np.sin(k * s), 1 - np.cos(k * s)]) / k
    assert np.allclose(end, d * np.array([np.cos(a), np.sin(a)]))


def test_follower_reaches_the_end_of_the_path():
    t = m.follow(CORNERS, 1.5)
    assert np.linalg.norm(t[-1, :2] - [10, 10]) < 0.15


def test_bigger_lookahead_cuts_the_corner_more():
    cuts = [corner_cut(m.follow(CORNERS, ld)) for ld in (0.4, 1.5, 4.0)]
    assert cuts[0] < cuts[1] < cuts[2]
    assert cuts[2] > 1.0


def test_short_lookahead_oscillates_when_the_drive_lags_and_not_when_it_does_not():
    assert leg1_changes(0.4) >= 6 and leg1_changes(1.5) <= 2
    assert leg1_changes(0.4, tau=0.01) <= 2
