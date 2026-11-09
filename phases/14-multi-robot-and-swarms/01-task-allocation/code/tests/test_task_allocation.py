# 레슨 14/01 테스트: 탐욕 배정, Hungarian 최적 배정, brute force 대조
import importlib.util
import itertools
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_alloc", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def rand_instance(n, seed):
    rng = np.random.default_rng(seed)
    return m.cost_matrix(rng.random((n, 2)), rng.random((n, 2)))


def brute(C):
    n = len(C)
    return min(sum(C[i, p[i]] for i in range(n)) for p in itertools.permutations(range(n)))


def test_cost_matrix_is_euclidean_distance():
    C = m.cost_matrix(np.array([[0.0, 0.0]]), np.array([[3.0, 4.0]]))
    assert C.shape == (1, 1) and np.isclose(C[0, 0], 5.0)


def test_hungarian_matches_brute_force_on_small_instances():
    for seed in range(60):
        C = rand_instance(2 + seed % 5, seed)
        assert np.isclose(m.total(C, m.hungarian(C)), brute(C))


def test_assignments_are_permutations():
    C = rand_instance(8, 1)
    for a in (m.greedy(C), m.hungarian(C)):
        assert sorted(a) == list(range(8))


def test_greedy_is_never_better_than_optimal():
    for seed in range(40):
        C = rand_instance(9, seed)
        assert m.total(C, m.greedy(C)) >= m.total(C, m.hungarian(C)) - 1e-9


def test_greedy_loses_on_a_hand_built_trap():
    C = np.array([[1.0, 2.0], [1.1, 10.0]])  # robot 0 grabs task 0 and strands robot 1
    assert np.isclose(m.total(C, m.greedy(C)), 11.0)
    assert np.isclose(m.total(C, m.hungarian(C)), 3.1)


def test_hungarian_handles_negative_and_equal_costs():
    C = np.array([[0.0, 0.0], [0.0, 0.0]])
    assert m.total(C, m.hungarian(C)) == 0.0
    C = rand_instance(5, 3) - 0.7
    assert np.isclose(m.total(C, m.hungarian(C)), brute(C))


def test_matches_scipy_on_larger_instances():
    lsa = pytest.importorskip("scipy.optimize").linear_sum_assignment
    for seed in range(10):
        C = rand_instance(30, seed)
        r, c = lsa(C)
        assert np.isclose(m.total(C, m.hungarian(C)), C[r, c].sum())
