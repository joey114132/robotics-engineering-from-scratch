# 레슨 08/06 테스트: 루프 폐쇄 전후 오차, gauge 고정, Gauss-Newton 단조 감소, 잘못된 폐쇄 간선의 해
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_posegraph", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def build(seed=0):
    truth, edges, X0 = m.world(np.random.default_rng(seed))
    return truth, edges, X0


def test_angle_difference_of_2pi_is_no_error():
    a, b = np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 2 * np.pi])
    assert np.allclose(m.between(a, b), [0, 0, 0], atol=1e-12)


def test_odometry_alone_drifts_far_from_the_start_it_should_return_to():
    truth, _, X0 = build()
    assert np.linalg.norm(X0[-1, :2]) > 0.5  # the loop should end at the origin


def test_a_consistent_graph_is_already_at_its_minimum():
    truth, edges, _ = build()
    perfect = [(i, j, m.between(truth[i], truth[j]), w) for i, j, _, w in edges]
    assert np.abs(m.residuals(truth, perfect)).max() < 1e-12
    X, costs = m.solve(truth, perfect)
    assert np.allclose(X, truth, atol=1e-9)


def test_loop_closure_cuts_the_trajectory_error():
    truth, edges, X0 = build()
    X, _ = m.solve(X0, edges)
    assert m.ate(X, truth) < 0.5 * m.ate(X0, truth)


def test_gauss_newton_cost_never_rises():
    _, edges, X0 = build()
    _, costs = m.solve(X0, edges)
    assert np.all(np.diff(costs) <= 1e-9) and costs[-1] < costs[0]


def test_anchored_pose_does_not_move():
    _, edges, X0 = build()
    X, _ = m.solve(X0, edges)
    assert np.array_equal(X[0], X0[0])


def test_without_an_anchor_three_directions_are_free():
    _, edges, X0 = build()
    J = m.jacobian(X0, edges, free=range(len(X0)))
    assert np.linalg.matrix_rank(J, tol=1e-8) == 3 * len(X0) - 3  # shift x, shift y, rotate whole map
    Ja = m.jacobian(X0, edges, free=range(1, len(X0)))
    assert np.linalg.matrix_rank(Ja, tol=1e-8) == 3 * (len(X0) - 1)


def test_a_wrong_closure_edge_bends_the_map_worse_than_the_right_one():
    truth, edges, X0 = build()
    good, _ = m.solve(X0, edges)
    i, j, z, w = edges[-1]
    bad_edges = edges[:-1] + [(i, j, z + [3.0, -2.0, 0.8], w)]
    bad, _ = m.solve(X0, bad_edges)
    assert m.ate(bad, truth) > m.ate(good, truth)
