# 레슨 08/03 테스트: log-odds 갱신, ray casting, 알려진 자세의 지도와 자세 오차가 번지게 한 지도
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_grid", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

WORLD, TP = m.make_world(), m.loop_poses()
ONE = np.array([0.0])


def test_probability_of_zero_log_odds_is_one_half_and_monotone():
    assert m.prob(0.0) == 0.5
    p = m.prob(np.linspace(-5, 5, 11))
    assert np.all(np.diff(p) > 0) and np.isclose(p[0] + p[-1], 1.0)


def test_ray_range_to_the_right_wall():
    r = m.scan(WORLD, np.array([2.0, 2.0, 0.0]), ONE)
    assert abs(r[0] - (9.75 - 2.0)) < 0.07  # the wall cell starts at x = 9.75


def test_beam_with_no_hit_reports_max_range():
    r = m.scan(m.np.zeros((m.N, m.N), bool), np.array([5.0, 5.0, 0.0]), ONE, max_range=3.0)
    assert r[0] == 3.0


def test_one_beam_marks_end_cell_occupied_and_path_free():
    pose = np.array([2.0, 2.0, 0.0])
    r = m.scan(WORLD, pose, ONE)
    L = m.update(np.zeros((m.N, m.N)), pose, r, ONE)
    end, mid, behind = m.cell([9.8, 2.0]), m.cell([5.0, 2.0]), m.cell([9.8, 3.0])
    assert L[end[1], end[0]] == m.L_OCC
    assert L[mid[1], mid[0]] == -m.L_FREE
    assert L[behind[1], behind[0]] == 0.0


def test_repeated_hits_saturate_at_the_clamp():
    pose = np.array([2.0, 2.0, 0.0])
    r = m.scan(WORLD, pose, ONE)
    L = np.zeros((m.N, m.N))
    for _ in range(50):
        L = m.update(L, pose, r, ONE)
    assert L.max() == m.L_MAX and L.min() == -m.L_MAX


def test_known_poses_give_a_mostly_correct_map_and_hide_the_box_interior():
    L = m.build_map(WORLD, TP, TP)
    assert m.precision(L, WORLD) > 0.8
    assert L[19:21, 19:21].max() == 0.0  # never seen: every beam stopped at the box surface


def test_zero_drift_is_the_identity():
    assert np.allclose(m.drift(TP, 0.0), TP)


def test_drift_keeps_path_length_but_moves_the_end():
    d = m.drift(TP, 0.003)
    length = lambda p: np.linalg.norm(np.diff(p[:, :2], axis=0), axis=1).sum()
    assert np.isclose(length(d), length(TP))
    assert np.linalg.norm(d[-1, :2] - TP[-1, :2]) > 0.5


def test_pose_error_smears_the_map():
    clean = m.build_map(WORLD, TP, TP)
    bad = m.build_map(WORLD, TP, m.drift(TP, 0.003))
    assert m.precision(bad, WORLD) < m.precision(clean, WORLD) - 0.3
    assert (bad > 0).sum() > 1.4 * (clean > 0).sum()
