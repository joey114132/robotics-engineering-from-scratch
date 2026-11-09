# 레슨 02/03 테스트: 해석적 Jacobian 과 유한 차분 Jacobian 의 일치, 속도 사상, tau = J^T F
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_jac", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

L = (0.5, 0.4)


def random_q(n=50, seed=2):
    return np.random.default_rng(seed).uniform(-np.pi, np.pi, (n, 2))


def test_analytic_and_finite_difference_jacobians_agree():
    for q in random_q():
        assert np.allclose(m.jacobian(q, L), m.jacobian_fd(q, L), atol=1e-8)


def test_hand_computed_jacobian_at_the_stretched_pose():
    J = m.jacobian([0.0, 0.0], L)
    assert np.allclose(J, [[0.0, 0.0], [0.9, 0.4]])


def test_joint_speed_maps_to_tip_speed_like_a_small_fk_step():
    q, qd, dt = np.array([0.3, 0.8]), np.array([0.5, -0.2]), 1e-6
    step = (m.fk(q + qd * dt, L) - m.fk(q, L)) / dt
    assert np.allclose(m.J_times(m.jacobian(q, L), qd), step, atol=1e-5)


def test_tip_force_maps_to_joint_torque_by_hand():
    tau = m.joint_torque(m.jacobian([0.0, 0.0], L), [0.0, -10.0])  # push straight down on a stretched arm
    assert np.allclose(tau, [-9.0, -4.0])


def test_power_in_joint_space_equals_power_at_the_tip():
    for q in random_q():
        J, qd, F = m.jacobian(q, L), np.array([0.7, -1.1]), np.array([3.0, -2.0])
        assert np.isclose(m.joint_torque(J, F) @ qd, F @ (J @ qd))


def test_holding_a_tip_weight_matches_the_gravity_torque_of_a_point_mass():
    q, mass, g = np.array([0.4, 0.9]), 2.0, 9.81
    tau = m.joint_torque(m.jacobian(q, L), [0.0, mass * g])  # torque that cancels the weight
    t2 = mass * g * L[1] * np.cos(q[0] + q[1])
    t1 = mass * g * (L[0] * np.cos(q[0]) + L[1] * np.cos(q[0] + q[1]))
    assert np.allclose(tau, [t1, t2])


def test_finite_difference_step_too_large_is_visibly_wrong_and_default_is_fine():
    q = np.array([0.3, 0.8])
    assert np.abs(m.jacobian_fd(q, L, eps=1e-1) - m.jacobian(q, L)).max() > 1e-4
    assert np.abs(m.jacobian_fd(q, L) - m.jacobian(q, L)).max() < 1e-8
