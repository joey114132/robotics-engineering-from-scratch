# 레슨 09/05 테스트: A* 와 Dijkstra 의 비용 일치, 확장 수 비교, 과대추정 휴리스틱의 손실과 상한, 도달 불가 처리
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_astar", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def random_map(seed, n=20, p=0.25):
    g = np.random.default_rng(seed).random((n, n)) < p
    g[0, 0] = g[n - 1, n - 1] = False
    return g, (0, 0), (n - 1, n - 1)


def cost(path):
    return None if path is None else len(path) - 1


@pytest.mark.parametrize("start,goal", [((0, 0), (0, 1)), ((0, 1), (0, 0)), ((0, 0), (0, 0))])
def test_blocked_endpoints_are_rejected_even_when_they_are_equal(start, goal):
    with pytest.raises(ValueError, match="start|goal"):
        m.search(np.array([[True, False]]), start, goal)


@pytest.mark.parametrize("bad", [(-1, 0), (0, -1), (1, 0), (0, 2)])
@pytest.mark.parametrize("endpoint", ["start", "goal"])
def test_out_of_bounds_endpoints_are_rejected(bad, endpoint):
    start, goal = (bad, (0, 1)) if endpoint == "start" else ((0, 0), bad)
    with pytest.raises(ValueError, match=endpoint):
        m.search(np.zeros((1, 2), bool), start, goal)


def test_path_is_a_walk_over_free_neighbours():
    g, s, t = random_map(1)
    path, _ = m.search(g, s, t)
    assert path[0] == s and path[-1] == t
    assert all(not g[c] for c in path)
    assert all(m.manhattan(a, b) == 1 for a, b in zip(path[:-1], path[1:]))


def test_astar_matches_dijkstra_cost_on_many_random_maps():
    for seed in range(60):
        g, s, t = random_map(seed)
        assert cost(m.search(g, s, t, 1.0)[0]) == cost(m.search(g, s, t, 0.0)[0])


def test_astar_expands_fewer_cells_than_dijkstra():
    fewer = 0
    for seed in range(40):
        g, s, t = random_map(seed, p=0.2)
        a, d = m.search(g, s, t, 1.0)[1], m.search(g, s, t, 0.0)[1]
        fewer += len(a) <= len(d)
    assert fewer == 40


def test_on_an_empty_map_astar_walks_straight_and_dijkstra_floods():
    g = np.zeros((30, 30), bool)
    path, exp = m.search(g, (0, 0), (29, 29), 1.0)
    assert len(exp) == len(path)  # it never looks at a cell off the final path
    assert len(m.search(g, (0, 0), (29, 29), 0.0)[1]) > 10 * len(path)


def test_no_cell_is_expanded_twice():
    g, s, t = random_map(3)
    for w in (0.0, 1.0, 3.0):
        exp = m.search(g, s, t, w)[1]
        assert len(exp) == len(set(exp))


def test_manhattan_never_overestimates_the_true_distance():
    g, _, t = random_map(5, n=12)
    for i in range(12):
        for j in range(12):
            if not g[i, j] and (p := m.search(g, (i, j), t, 0.0)[0]) is not None:
                assert m.manhattan((i, j), t) <= len(p) - 1


def test_weighted_search_is_never_worse_than_w_times_optimal():
    for seed in range(60):
        g, s, t = random_map(seed)
        opt = cost(m.search(g, s, t, 1.0)[0])
        for w in (1.5, 3.0, 6.0):
            c = cost(m.search(g, s, t, w)[0])
            assert (opt is None) == (c is None)
            assert opt is None or opt <= c <= w * opt


def test_unreachable_goal_returns_none_after_exploring_everything_reachable():
    g = np.zeros((8, 8), bool)
    g[:, 4] = True
    path, exp = m.search(g, (0, 0), (0, 7), 1.0)
    assert path is None and len(exp) == 32


TRAP = [
    "...........#.....",
    ".....#.....#.....",
    ".....#.....#.....",
    ".....#.....#.....",
    ".....#.....#.....",
    "S....#.....#....G",
    ".....#.....#.....",
    ".....#.....#.....",
    ".....#.....#.....",
    ".....#.....#.....",
    ".................",
]


def test_an_overestimating_heuristic_takes_the_tempting_gap_and_pays_for_it():
    g, s, t = m.parse(TRAP)
    assert cost(m.search(g, s, t, 1.0)[0]) == 26  # round the bottom: 5 + 16 + 5
    greedy = cost(m.search(g, s, t, 4.0)[0])
    assert greedy == 36 and greedy <= 4 * 26  # through the near top gap, then all the way down
