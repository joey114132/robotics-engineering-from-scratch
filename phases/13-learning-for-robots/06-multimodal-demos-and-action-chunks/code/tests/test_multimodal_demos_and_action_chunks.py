# 레슨 13/06 테스트: 평균 회귀는 장애물에 부딪히고 청크 표본기는 한쪽을 고른다
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_chunks", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

START = np.array([-1.0, 0.0])


def data(seed=0, pairs=6):
    return m.demos(pairs, np.random.default_rng(seed))


def test_demos_split_evenly_and_all_clear_the_obstacle():
    P, A = data()
    assert (P[:, 20, 1] > 0).sum() == (P[:, 20, 1] < 0).sum() == 6
    assert all(m.clear(p) for p in P) and np.allclose(P[:, -1], m.GOAL, atol=1e-9)


def test_mean_regression_drives_straight_into_the_obstacle():
    P, A = data()
    path = m.rollout_mean(m.mean_policy(P, A), START)
    assert not m.clear(path)
    assert abs(path[:, 1]).max() < 0.05  # it averaged "over" and "under" into "straight"


def test_chunk_sampler_never_hits_and_reaches_the_goal():
    P, A = data()
    paths = [m.rollout_chunks(P, A, START, H=8, overlap=4, rng=np.random.default_rng(s)) for s in range(100)]
    assert all(m.clear(p) for p in paths)
    assert all(np.linalg.norm(p[-1] - m.GOAL) < 0.1 for p in paths)


def test_chunk_sampler_keeps_both_ways_around():
    P, A = data()
    side = [np.sign(m.rollout_chunks(P, A, START, 8, 4, np.random.default_rng(s))[:, 1][30]) for s in range(100)]
    assert 30 <= sum(np.array(side) > 0) <= 70


def test_longer_chunks_with_overlap_average_cut_action_jitter():
    P, A = data()
    jit = lambda H, o: np.mean([m.jitter(m.rollout_chunks(P, A, START, H, o, np.random.default_rng(s))) for s in range(40)])
    assert jit(8, 4) < 0.6 * jit(1, 0)


def test_one_demo_is_replayed_exactly_by_any_chunk_length():
    P, A = data(pairs=1)
    one_P, one_A = P[:1], A[:1]
    for H, o in ((1, 0), (8, 4)):
        path = m.rollout_chunks(one_P, one_A, START, H, o, np.random.default_rng(0), steps=40)
        assert np.allclose(path, one_P[0], atol=1e-9)


def test_overlap_of_identical_chunks_changes_nothing():
    P, A = data(pairs=1)
    a = m.rollout_chunks(P[:1], A[:1], START, 8, 0, np.random.default_rng(0), steps=40)
    b = m.rollout_chunks(P[:1], A[:1], START, 8, 4, np.random.default_rng(0), steps=40)
    assert np.allclose(a, b, atol=1e-9)
