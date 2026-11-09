# 레슨 01/02 테스트: 평면과 공간 회전관절 사슬의 순기구학
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_fk", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_straight_arm_reaches_sum_of_lengths():
    x, y, _ = m.fk_planar([1.0, 0.5], [0.0, 0.0])
    assert np.allclose([x, y], [1.5, 0.0])


def test_elbow_up_then_forward():
    x, y, heading = m.fk_planar([1.0, 0.5], [np.pi / 2, -np.pi / 2])
    assert np.allclose([x, y, heading], [0.5, 1.0, 0.0], atol=1e-12)


def test_se3_chain_matches_planar_formula():
    rng = np.random.default_rng(0)
    for _ in range(20):
        q = rng.uniform(-np.pi, np.pi, 3)
        L = [0.4, 0.3, 0.2]
        T = m.fk_chain(q, L)
        x, y, heading = m.fk_planar(L, q)
        assert np.allclose(T[:2, 3], [x, y], atol=1e-12)
        assert np.isclose(np.arctan2(T[1, 0], T[0, 0]), np.arctan2(np.sin(heading), np.cos(heading)))


def test_reach_bounds_equal_links():
    lo, hi = m.reach_bounds([1.0, 1.0])
    assert np.isclose(lo, 0.0) and np.isclose(hi, 2.0)


def test_reach_bounds_long_first_link_leaves_a_hole():
    lo, hi = m.reach_bounds([3.0, 1.0])
    assert np.isclose(lo, 2.0) and np.isclose(hi, 4.0)


def test_random_poses_stay_inside_reach_bounds():
    rng = np.random.default_rng(1)
    L = [0.7, 0.4]
    lo, hi = m.reach_bounds(L)
    for _ in range(200):
        x, y, _ = m.fk_planar(L, rng.uniform(-np.pi, np.pi, 2))
        assert lo - 1e-9 <= np.hypot(x, y) <= hi + 1e-9
