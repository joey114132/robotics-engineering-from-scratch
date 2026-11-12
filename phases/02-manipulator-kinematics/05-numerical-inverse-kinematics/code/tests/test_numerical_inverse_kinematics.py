# 레슨 02/05 테스트: 3링크 평면 팔의 damped Newton IK, 관절 한계, 무작위 재시작, 도달 불가 표적
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_numik", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

L = (0.4, 0.3, 0.2)
LO, HI = np.array([-np.pi, -2.5, -2.5]), np.array([np.pi, 2.5, 2.5])


def test_jacobian_matches_finite_difference():
    q, h = np.array([0.3, -0.7, 0.5]), 1e-6
    fd = np.column_stack([(m.fk(q + h * e, L) - m.fk(q - h * e, L)) / (2 * h) for e in np.eye(3)])
    assert np.allclose(m.jacobian(q, L), fd, atol=1e-8)


def test_answer_reaches_the_target_through_fk():
    target = np.array([0.5, 0.3])
    q, ok = m.solve_ik(target, L, [0.2, 0.3, 0.1], LO, HI)
    assert ok and np.linalg.norm(m.fk(q, L) - target) < 1e-6


def test_solution_stays_inside_joint_limits():
    q, _ = m.solve_ik([0.6, -0.2], L, [0.1, 0.1, 0.1], LO, HI)
    assert np.all(q >= LO) and np.all(q <= HI)


def test_starts_from_a_singular_straight_arm():
    q, ok = m.solve_ik([0.5, 0.2], L, [0.0, 0.0, 0.0], LO, HI)
    assert ok and np.linalg.norm(m.fk(q, L) - [0.5, 0.2]) < 1e-6


def test_restarts_find_both_elbow_signs():
    sols = m.ik_restarts([0.5, 0.3], L, LO, HI, n=30, seed=1)
    good = [q for q, ok in sols if ok]
    assert len(good) >= 20
    assert any(q[1] > 0.1 for q in good) and any(q[1] < -0.1 for q in good)
    assert all(np.linalg.norm(m.fk(q, L) - [0.5, 0.3]) < 1e-6 for q in good)


def test_unreachable_target_returns_best_effort_and_a_flag():
    target = np.array([1.5, 0.0])  # reach is 0.9
    q, ok = m.solve_ik(target, L, [0.3, 0.3, 0.3], LO, HI)
    assert not ok
    assert np.isclose(np.linalg.norm(m.fk(q, L) - target), 1.5 - sum(L), atol=0.02)  # creeps toward full stretch: damping slows the last mm


def test_tight_joint_limits_make_a_reachable_point_fail():
    lo, hi = np.array([-0.1, -0.1, -0.1]), np.array([0.1, 0.1, 0.1])
    q, ok = m.solve_ik([0.0, 0.6], L, [0, 0, 0], lo, hi)
    assert not ok and np.all(q >= lo) and np.all(q <= hi)


def test_best_of_restarts_is_never_worse_than_a_single_run():
    target = np.array([0.45, 0.35])
    q0 = np.random.default_rng(3).uniform(LO, HI)
    first, ok = m.solve_ik(target, L, q0, LO, HI)
    first_error = np.linalg.norm(m.fk(first, L) - target)
    assert not ok and first_error > 0.1
    sols = m.ik_restarts(target, L, LO, HI, n=10, seed=3)
    assert np.allclose(sols[0][0], first) and not sols[0][1]
    good = [q for q, converged in sols[1:] if converged]
    assert good
    assert all(np.linalg.norm(m.fk(q, L) - target) < 1e-6 for q in good)
    assert min(np.linalg.norm(m.fk(q, L) - target) for q in good) < first_error


def test_failed_solve_keeps_initial_pose_when_the_step_increases_error():
    q, ok = m.solve_ik([3.0, 0.0], [1.0], [0.1], [-np.pi], [np.pi], iters=1)
    assert not ok and np.allclose(q, [0.1])


def test_failed_solve_keeps_a_better_intermediate_pose():
    q, ok = m.solve_ik([3.0, 0.0], [1.0], [0.2], [-np.pi], [np.pi], iters=2)
    assert not ok and np.allclose(q, [-0.1])


def test_failed_solve_includes_the_final_step_in_its_best_pose():
    q, ok = m.solve_ik([3.0, 0.0], [1.0], [0.2], [-np.pi], [np.pi], iters=1)
    assert not ok and np.allclose(q, [-0.1])


def test_demo_counts_and_figure_convergence_numbers_stay_unchanged():
    sols = m.ik_restarts([0.5, 0.3], L, LO, HI)
    assert sum(ok for _, ok in sols) == 17
    assert {int(np.sign(q[1])) for q, ok in sols if ok} == {-1, 1}
    rng = np.random.default_rng(1)
    steps = []
    for _ in range(4):
        q0 = rng.uniform(LO, HI)
        steps.append(next(k for k in range(40) if m.solve_ik([0.5, 0.3], L, q0, LO, HI, iters=k)[1]))
    assert max(steps) == 16  # The shared figure and EN/KO captions quote about 16 steps.
