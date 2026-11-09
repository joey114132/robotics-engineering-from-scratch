# 레슨 02/04 테스트: det(J) = l1 l2 sin q2, 특이점에서 잃는 방향, 역행렬의 속도 폭주와 damped least squares 의 상한
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_sing", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

L = (0.5, 0.4)
V = np.array([0.1, 0.0])  # 0.1 m/s radially outward when q1 = 0


def test_determinant_is_l1_l2_sin_q2_at_any_q1():
    for q in np.random.default_rng(5).uniform(-3, 3, (30, 2)):
        assert np.isclose(np.linalg.det(m.jacobian(q, L)), L[0] * L[1] * np.sin(q[1]))


def test_stretched_arm_has_rank_one_and_cannot_move_the_tip_radially():
    J = m.jacobian([0.0, 0.0], L)
    assert np.linalg.matrix_rank(J) == 1
    for qd in np.random.default_rng(6).normal(size=(10, 2)):
        assert abs((J @ qd)[0]) < 1e-12  # tip x velocity is zero for every joint speed


def test_folded_arm_is_singular_too():
    assert abs(np.linalg.det(m.jacobian([0.3, np.pi], L))) < 1e-12


def test_manipulability_peaks_at_a_right_angle_elbow():
    q2 = np.linspace(0.01, np.pi - 0.01, 2001)
    w = [m.manipulability(m.jacobian([0.0, a], L)) for a in q2]
    assert abs(q2[int(np.argmax(w))] - np.pi / 2) < 0.01


def test_plain_inverse_joint_speed_grows_like_one_over_sin_q2():
    s = lambda a: np.linalg.norm(m.solve(m.jacobian([0.0, a], L), V, lam=0.0))
    assert np.isclose(s(0.01) / s(0.02), 2.0, rtol=0.05)


def test_damped_solution_obeys_the_speed_bound():
    lam = 0.05
    for a in np.linspace(1e-4, np.pi / 2, 200):
        qd = m.solve(m.jacobian([0.0, a], L), V, lam)
        assert np.linalg.norm(qd) <= np.linalg.norm(V) / (2 * lam) + 1e-12


def test_damping_far_from_a_singularity_changes_almost_nothing():
    J = m.jacobian([0.0, 1.5], L)
    assert np.allclose(m.solve(J, V, 1e-3), m.solve(J, V, 0.0), rtol=1e-3, atol=1e-6)


def test_damping_costs_tip_accuracy_near_the_singularity_but_not_the_whole_command():
    J = m.jacobian([0.0, 0.02], L)
    err = np.linalg.norm(J @ m.solve(J, V, 0.05) - V)
    assert 0.5 * np.linalg.norm(V) < err < np.linalg.norm(V)
