# 레슨 03/06 테스트: Riccati 게인의 안정성, 비용 최적성, R 이 피크 입력에 주는 영향
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_lqr", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

A, B = m.double_integrator(0.05)
Q = np.diag([1.0, 0.1])
X0 = np.array([1.0, 0.0])


def test_closed_loop_eigenvalues_inside_unit_circle():
    K, _ = m.dare(A, B, Q, np.array([[0.1]]))
    assert np.abs(np.linalg.eigvals(A - B @ K)).max() < 1.0


def test_gain_satisfies_the_fixed_point_equation():
    R = np.array([[0.1]])
    K, P = m.dare(A, B, Q, R)
    assert np.allclose(K, np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A))
    assert np.allclose(P, Q + A.T @ P @ (A - B @ K), atol=1e-9)


def test_simulated_cost_equals_x0_P_x0():
    R = np.array([[0.1]])
    K, P = m.dare(A, B, Q, R)
    _, _, cost = m.rollout(A, B, K, X0, 2000, Q, R)
    assert np.isclose(cost, X0 @ P @ X0, rtol=1e-6)


def test_lqr_beats_a_hand_tuned_pd():
    R = np.array([[0.1]])
    K, _ = m.dare(A, B, Q, R)
    pd = np.array([[4.0, 3.0]])  # a plausible hand pick, stable but not optimal
    assert np.abs(np.linalg.eigvals(A - B @ pd)).max() < 1.0
    assert m.rollout(A, B, K, X0, 2000, Q, R)[2] < m.rollout(A, B, pd, X0, 2000, Q, R)[2]


def test_larger_R_gives_smaller_peak_input():
    peaks = []
    for r in (0.01, 0.1, 1.0, 10.0):
        R = np.array([[r]])
        K, _ = m.dare(A, B, Q, R)
        peaks.append(np.abs(m.rollout(A, B, K, X0, 400, Q, R)[1]).max())
    assert all(a > b for a, b in zip(peaks, peaks[1:]))


def test_larger_R_settles_slower():
    t = []
    for r in (0.01, 1.0):
        R = np.array([[r]])
        K, _ = m.dare(A, B, Q, R)
        x = m.rollout(A, B, K, X0, 800, Q, R)[0]
        t.append(int(np.where(np.abs(x[:, 0]) > 0.02)[0].max()))  # last tick outside the 2% band
    assert t[0] < t[1]


def test_matches_scipy_riccati_solution():
    import pytest

    linalg = pytest.importorskip("scipy.linalg")
    R = np.array([[0.1]])
    assert np.allclose(m.dare(A, B, Q, R)[1], linalg.solve_discrete_are(A, B, Q, R), atol=1e-8)
