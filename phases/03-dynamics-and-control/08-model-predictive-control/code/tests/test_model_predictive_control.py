# 레슨 03/08 테스트: 예측 행렬, 입력 한계 준수, 한계가 비활성일 때 LQR 과 일치, 긴 horizon 의 이득
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_mpc", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

A, B = m.double_integrator(0.1)
Q, R = np.diag([1.0, 0.1]), np.array([[0.1]])
K, P = m.riccati(A, B, Q, R)
X0 = np.array([4.0, 0.0])


def test_prediction_matrices_reproduce_a_rollout():
    N, U = 6, np.array([0.3, -1.0, 0.5, 0.0, 2.0, -0.7])
    Phi, Gam = m.prediction(A, B, N)
    x, xs = np.array([1.0, -0.5]), []
    for u in U:
        x = A @ x + B[:, 0] * u
        xs.append(x)
    assert np.allclose(Phi @ np.array([1.0, -0.5]) + Gam @ U, np.concatenate(xs))


def test_plan_never_exceeds_the_input_bound_and_does_hit_it():
    U = m.plan(X0, A, B, Q, R, P, 20, 0.5)
    assert np.abs(U).max() <= 0.5 + 1e-12
    assert np.isclose(np.abs(U).max(), 0.5)


def test_applied_inputs_obey_the_bound_at_every_step():
    _, us, _ = m.simulate(X0, 60, A, B, Q, R, 10, 0.5)
    assert np.abs(us).max() <= 0.5 + 1e-12


def test_matches_lqr_when_the_bound_is_inactive():
    x0 = np.array([1.0, 0.5])
    u0 = m.plan(x0, A, B, Q, R, P, 15, 1e6)[0]
    assert np.isclose(u0, -(K @ x0)[0], atol=1e-3)


def test_whole_run_matches_lqr_when_the_bound_is_inactive():
    x, ref = np.array([1.0, 0.5]), []
    for _ in range(40):
        ref.append(x)
        x = A @ x - B @ K @ x
    xs, _, _ = m.simulate([1.0, 0.5], 40, A, B, Q, R, 15, 1e6)
    assert np.allclose(xs, np.array(ref), atol=1e-2)


def test_longer_horizon_does_not_raise_cost():
    costs = [m.simulate(X0, 150, A, B, Q, R, N, 0.5)[2] for N in (2, 5, 20)]
    assert costs[0] >= costs[1] >= costs[2]
    assert costs[0] - costs[2] > 10.0


def test_mpc_overshoots_less_than_clipped_lqr():
    x, lo = X0.copy(), 0.0
    for _ in range(150):
        x = A @ x + B[:, 0] * np.clip(-(K @ x)[0], -0.5, 0.5)
        lo = min(lo, x[0])
    xs, _, _ = m.simulate(X0, 150, A, B, Q, R, 20, 0.5)
    assert xs[:, 0].min() > lo + 0.5
