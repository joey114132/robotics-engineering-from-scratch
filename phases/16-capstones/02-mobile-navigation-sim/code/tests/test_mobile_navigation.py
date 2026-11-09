# 레슨 16/02 테스트: A*, 경로 단축, 두 점 자세 보정, 오도메트리 오차 아래의 주행 성공과 실패
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_nav", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

START, GOAL = (1.5, 1.5), (9.0, 8.5)
BAD = dict(scale_err=0.03, w_bias=0.03, sigma=0.02)  # 3% speed error, 0.03 rad/s turn-rate bias


def _plan():
    world = m.make_world()
    occ = m.inflate(world)
    return world, occ, m.plan(occ, START, GOAL)


def test_astar_on_empty_grid_matches_octile_distance():
    occ = np.zeros((20, 20), bool)
    path = m.astar(occ, (2, 3), (12, 9))
    length = sum(np.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(path[:-1], path[1:]))
    assert np.isclose(length, 6 * np.sqrt(2) + 4)  # 6 diagonal steps, then 4 straight


def test_astar_returns_none_when_goal_is_walled_in():
    occ = np.zeros((10, 10), bool)
    occ[4:7, 4:7] = True
    occ[5, 5] = False
    assert m.astar(occ, (0, 0), (5, 5)) is None


def test_astar_never_cuts_a_diagonal_corner():
    occ = np.zeros((6, 6), bool)
    occ[2, 3] = occ[3, 2] = True  # a diagonal gap the robot must not squeeze through
    path = m.astar(occ, (2, 2), (3, 3))
    assert all(not occ[c] for c in path) and len(path) > 2


def test_inflate_grows_obstacles_by_the_robot_radius():
    w = np.zeros((11, 11), bool)
    w[5, 5] = True
    occ = m.inflate(w, 0.4)
    assert occ[5, 6] and occ[6, 6] and not occ[5, 7]  # 0.4 m = 1.6 cells: diagonal in, two cells out


def test_smoothing_shortens_the_path_and_stays_clear():
    _, occ, (raw, smooth) = _plan()
    length = lambda p: sum(np.linalg.norm(np.subtract(a, b)) for a, b in zip(p[:-1], p[1:]))
    assert length(smooth) < length(raw) and len(smooth) < len(raw)
    assert all(m.line_free(occ, a, b) for a, b in zip(smooth[:-1], smooth[1:]))


def test_pose_fix_recovers_pose_without_noise():
    rng = np.random.default_rng(1)
    L = m.LANDMARKS
    pose = np.array([4.0, 5.0, 0.7])
    body = m.sense(pose, L, rng, 0.0)
    assert np.allclose(m.pose_fix(L, body), pose)


def test_good_odometry_reaches_the_goal_without_touching_a_wall():
    world, _, (_, smooth) = _plan()
    true, _ = m.drive(smooth, (*START, 0.0), scale_err=0.002, w_bias=0.001, sigma=0.005)
    assert np.linalg.norm(true[-1, :2] - GOAL) < 0.3 and not m.hits(world, true)


def test_bad_odometry_drifts_off_the_path():
    world, _, (_, smooth) = _plan()
    true, est = m.drive(smooth, (*START, 0.0), **BAD)
    assert np.linalg.norm(true[-1, :2] - GOAL) > 1.0 or m.hits(world, true)
    assert np.linalg.norm(true[-1, :2] - est[-1, :2]) > 0.5  # the robot believes it is somewhere it is not


def test_landmark_fix_brings_the_robot_back():
    world, _, (_, smooth) = _plan()
    lm = m.LANDMARKS
    true, est = m.drive(smooth, (*START, 0.0), landmarks=lm, **BAD)
    assert np.linalg.norm(true[-1, :2] - GOAL) < 0.3 and not m.hits(world, true)


def test_drive_is_reproducible_for_a_seed():
    _, _, (_, smooth) = _plan()
    a, _ = m.drive(smooth, (*START, 0.0), seed=3, **BAD)
    b, _ = m.drive(smooth, (*START, 0.0), seed=3, **BAD)
    assert np.array_equal(a, b)
