# 레슨 09/02 테스트: 원형 장애물이 있는 2D 평면의 RRT, 시드 고정 결정성, path shortcutting
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_rrt", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

START, GOAL = np.array([1.0, 1.0]), np.array([9.0, 9.0])
BOUNDS = (np.zeros(2), np.full(2, 10.0))
OBS = [(np.array([5.0, 5.0]), 2.0), (np.array([3.0, 7.5]), 1.2), (np.array([7.5, 3.0]), 1.2)]


def plan(seed=0, **kw):
    return m.rrt(START, GOAL, OBS, BOUNDS, seed=seed, **kw)


def test_the_straight_line_is_blocked_so_planning_is_needed():
    assert not m.seg_free(START, GOAL, OBS)


def test_path_runs_from_start_to_goal_and_every_segment_is_free():
    _, _, path = plan()
    assert path is not None and np.allclose(path[0], START) and np.allclose(path[-1], GOAL)
    assert all(m.seg_free(a, b, OBS) for a, b in zip(path[:-1], path[1:]))


def test_same_seed_gives_the_same_tree_and_a_different_seed_does_not():
    n1, _, _ = plan(seed=3)
    n2, _, _ = plan(seed=3)
    n3, _, _ = plan(seed=4)
    assert np.array_equal(n1, n2) and (len(n1) != len(n3) or not np.array_equal(n1, n3))


def test_every_tree_edge_is_free_inside_bounds_and_no_longer_than_the_step():
    nodes, parent, _ = plan(step=0.5)
    for i in range(1, len(nodes)):
        assert np.linalg.norm(nodes[i] - nodes[parent[i]]) <= 0.5 + 1e-9
        assert m.seg_free(nodes[parent[i]], nodes[i], OBS)
    assert (nodes >= BOUNDS[0] - 1e-9).all() and (nodes <= BOUNDS[1] + 1e-9).all()


def test_a_goal_sealed_inside_a_ring_of_circles_is_reported_as_no_path():
    c = np.array([5.0, 5.0])
    ring = [(c + 1.5 * np.array([np.cos(a), np.sin(a)]), 0.9) for a in np.linspace(0, 2 * np.pi, 12, endpoint=False)]
    _, _, path = m.rrt(START, c, ring, BOUNDS, seed=0, iters=1500)
    assert path is None


def test_shortcut_keeps_the_endpoints_stays_free_and_is_never_longer():
    _, _, path = plan()
    short = m.shortcut(path, OBS, seed=0)
    assert np.allclose(short[0], START) and np.allclose(short[-1], GOAL)
    assert all(m.seg_free(a, b, OBS) for a, b in zip(short[:-1], short[1:]))
    assert m.path_length(short) <= m.path_length(path) + 1e-12


def test_shortcut_shortens_most_paths_and_never_beats_the_straight_line():
    gains = []
    for s in range(10):
        _, _, path = plan(seed=s)
        short = m.shortcut(path, OBS, seed=s)
        assert m.path_length(short) >= np.linalg.norm(GOAL - START) - 1e-9
        gains.append(m.path_length(path) - m.path_length(short))
    assert sum(g > 0.1 for g in gains) >= 8


def test_kdtree_nearest_neighbour_agrees_with_the_brute_force_search_used_here():
    spatial = __import__("pytest").importorskip("scipy.spatial")
    nodes, _, _ = plan()
    q = np.array([[2.2, 7.7], [8.1, 1.4]])
    brute = [int(np.argmin(np.linalg.norm(nodes - p, axis=1))) for p in q]
    assert list(spatial.cKDTree(nodes).query(q)[1]) == brute
