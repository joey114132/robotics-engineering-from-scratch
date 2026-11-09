# 레슨 02/02 테스트: 2링크 해석적 IK 의 두 가지 해, 도달 불가 거부, FK 로 되짚어 확인
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_ik", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

L = (0.5, 0.4)


def random_targets(n=200, seed=1):
    rng = np.random.default_rng(seed)
    r = rng.uniform(abs(L[0] - L[1]) + 1e-3, L[0] + L[1] - 1e-3, n)
    a = rng.uniform(-np.pi, np.pi, n)
    return np.column_stack([r * np.cos(a), r * np.sin(a)])


@pytest.mark.parametrize("elbow", ["up", "down"])
def test_fk_of_the_answer_returns_the_target(elbow):
    for p in random_targets():
        assert np.allclose(m.fk(m.ik(p, L, elbow), L), p, atol=1e-9)


def test_the_two_branches_are_different_arms_for_the_same_target():
    p = (0.6, 0.3)
    qu, qd = m.ik(p, L, "up"), m.ik(p, L, "down")
    assert not np.allclose(qu, qd)
    assert qu[1] < 0 < qd[1]


def test_known_pose_is_recovered_on_its_own_branch():
    q = np.array([0.4, 0.9])  # q2 > 0 is elbow-down
    assert np.allclose(m.ik(m.fk(q, L), L, "down"), q)
    q = np.array([1.2, -0.7])
    assert np.allclose(m.ik(m.fk(q, L), L, "up"), q)


def test_target_beyond_full_stretch_is_refused():
    with pytest.raises(ValueError, match="unreachable"):
        m.ik((0.91, 0.0), L)


def test_target_inside_the_inner_circle_is_refused():
    with pytest.raises(ValueError, match="unreachable"):
        m.ik((0.05, 0.0), L)  # |l1 - l2| = 0.1 is the closest the tip can come


def test_full_stretch_boundary_gives_one_answer_with_straight_elbow():
    q = m.ik((0.9, 0.0), L)
    assert np.isclose(q[1], 0.0, atol=1e-7) and np.allclose(m.fk(q, L), [0.9, 0.0], atol=1e-9)


def test_rounding_just_outside_the_boundary_is_not_a_false_refusal():
    p = np.array([0.9, 0.0]) * (1 + 1e-12)
    m.ik(p, L)


def test_equal_links_reach_the_base_point():
    q = m.ik((0.0, 0.0), (0.4, 0.4))
    assert np.allclose(m.fk(q, (0.4, 0.4)), 0.0, atol=1e-9)
