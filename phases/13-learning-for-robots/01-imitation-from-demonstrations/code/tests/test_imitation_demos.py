# 레슨 13/01 테스트: 전문가, 시연 수집, kNN·선형 모방 정책
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_imitation", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_expert_reaches_goal_from_every_start_without_touching_the_obstacle():
    rng = np.random.default_rng(1)
    assert m.success_rate(m.expert, rng, n=40) == 1.0


def test_expert_passes_the_obstacle_when_started_dead_on_the_axis():
    xs, _ = m.rollout(m.expert, [-1.2, 0.0])
    assert m.success(xs)
    assert np.abs(xs[:, 1]).max() > 0.2  # it had to swing around


def test_expert_action_is_capped_at_unit_speed():
    rng = np.random.default_rng(2)
    for x in rng.uniform(-1.5, 1.5, (200, 2)):
        assert np.linalg.norm(m.expert(x)) <= 1.0 + 1e-9


def test_collect_returns_matching_observation_and_action_arrays():
    X, A = m.collect(np.random.default_rng(3), 4)
    assert X.shape == A.shape == (4 * 120, 2)


def test_knn_with_k1_reproduces_every_demonstrated_action():
    X, A = m.collect(np.random.default_rng(4), 3)
    pi = m.fit_knn(X, A, k=1)
    assert all(np.allclose(pi(x), a) for x, a in zip(X[::17], A[::17]))


def test_linear_fit_recovers_an_exactly_linear_expert():
    rng = np.random.default_rng(5)
    X = rng.uniform(-1, 1, (50, 2))
    A = X @ np.array([[0.5, 0.1], [-0.2, 0.3]]) + 0.05
    pi = m.fit_linear(X, A)
    assert np.allclose([pi(x) for x in X], A, atol=1e-9)


def test_more_demonstrations_help_a_nearest_neighbour_policy():
    def rate(n):
        return np.mean([m.success_rate(m.fit_knn(*m.collect(np.random.default_rng(s), n)), np.random.default_rng(100 + s), n=30) for s in range(4)])
    assert rate(10) > rate(1) + 0.3


def test_a_linear_policy_cannot_swerve_around_the_obstacle():
    X, A = m.collect(np.random.default_rng(6), 30)
    assert m.success_rate(m.fit_linear(X, A), np.random.default_rng(7), n=40) < 0.5


def test_knn_matches_scipy_kdtree_neighbours():
    spatial = pytest.importorskip("scipy.spatial")
    X, A = m.collect(np.random.default_rng(8), 3)
    x = np.array([-0.5, 0.1])
    _, idx = spatial.cKDTree(X).query(x, k=3)
    assert np.allclose(m.fit_knn(X, A, k=3)(x), A[idx].mean(0))
