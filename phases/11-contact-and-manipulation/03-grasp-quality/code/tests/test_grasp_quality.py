# 레슨 11/03 테스트: 마찰 원뿔 가장자리 wrench 의 볼록 껍질이 원점을 품으면 force closure 이다
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_grasp", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def antipodal(mu):
    return m.contact_wrenches([[1, 0], [-1, 0]], [[-1, 0], [1, 0]], mu)


def offset_jaws(d, mu):
    """Two jaws on opposite faces of a box 2 wide, the right contact d higher than the left."""
    return m.contact_wrenches([[-1, 0], [1, d]], [[1, 0], [-1, 0]], mu)


def three_on_circle(mu):
    ang = np.radians([90, 210, 330])
    pts = np.c_[np.cos(ang), np.sin(ang)]
    return m.contact_wrenches(pts, -pts, mu)


def test_wrench_of_a_normal_force_through_the_origin_has_no_torque():
    W = m.contact_wrenches([[1, 0]], [[-1, 0]], 0.0)
    assert np.allclose(W[0], [-1, 0, 0])


def test_two_frictionless_antipodal_contacts_do_not_close():
    assert not m.closes(antipodal(0.0))


def test_two_antipodal_contacts_with_friction_close():
    assert m.closes(antipodal(0.3))


def test_offset_jaws_close_exactly_while_the_joining_line_is_inside_the_cone():
    mu = 0.4
    assert m.closes(offset_jaws(2 * mu * 0.9, mu))
    assert not m.closes(offset_jaws(2 * mu * 1.1, mu))


def test_three_contacts_need_friction_on_a_circle():
    assert not m.closes(three_on_circle(0.0))
    assert m.closes(three_on_circle(0.2))


def test_quality_grows_with_friction_and_is_zero_when_open():
    q = [m.epsilon(antipodal(mu)) for mu in (0.0, 0.2, 0.4, 0.8)]
    assert q[0] == 0.0 and q[1] > 0 and q == sorted(q)


def test_one_contact_never_closes():
    assert not m.closes(m.contact_wrenches([[1, 0]], [[-1, 0]], 5.0))


def test_closure_does_not_depend_on_the_torque_length_scale():
    for rho in (0.1, 1.0, 10.0):
        assert m.closes(m.contact_wrenches([[1, 0], [-1, 0]], [[-1, 0], [1, 0]], 0.3, rho))


def test_agrees_with_a_linear_program_on_random_grasps():
    linprog = pytest.importorskip("scipy.optimize").linprog
    rng = np.random.default_rng(3)
    for _ in range(40):
        ang = rng.uniform(0, 2 * np.pi, 3)
        pts = np.c_[np.cos(ang), np.sin(ang)]
        W = m.contact_wrenches(pts, -pts, rng.uniform(0, 0.5))
        # exists lam >= t > 0 with W^T lam = 0 and sum lam = 1  <=>  origin strictly inside the hull (rank 3 assumed)
        n = len(W)
        res = linprog(c=np.r_[np.zeros(n), -1.0], A_ub=np.c_[-np.eye(n), np.ones(n)], b_ub=np.zeros(n),
                      A_eq=np.r_[np.c_[W.T, np.zeros(3)], [np.r_[np.ones(n), 0.0]]], b_eq=[0, 0, 0, 1],
                      bounds=[(0, None)] * n + [(None, None)])
        lp_closed = res.status == 0 and -res.fun > 1e-7 and np.linalg.matrix_rank(W) == 3
        assert lp_closed == m.closes(W)
