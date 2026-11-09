# 레슨 14/02 테스트: 평균 합의, Laplacian 두 번째 고유값과 수렴 속도, 끊어진 그래프
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_consensus", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

X0 = np.array([4.0, -1.0, 2.0, 7.0, 0.0, 3.0, -5.0, 1.0])


def test_laplacian_is_symmetric_with_zero_row_sums():
    L = m.laplacian(m.ring(8))
    assert np.allclose(L, L.T) and np.allclose(L.sum(axis=1), 0)


def test_lambda2_matches_closed_forms():
    assert np.isclose(m.lambda2(m.laplacian(m.ring(8))), 2 - 2 * np.cos(2 * np.pi / 8))
    assert np.isclose(m.lambda2(m.laplacian(m.complete(8))), 8.0)


def test_average_is_preserved_every_step():
    traj = m.run(X0, m.ring(8), eps=0.2, steps=50)
    assert np.allclose(traj.mean(axis=1), X0.mean())


def test_ring_converges_to_the_initial_average():
    traj = m.run(X0, m.ring(8), eps=0.2, steps=400)
    assert np.allclose(traj[-1], X0.mean(), atol=1e-6)


def test_contraction_per_step_is_one_minus_eps_lambda2():
    eps = 0.1
    A = m.ring(8)
    traj = m.run(X0, A, eps, steps=300)
    d = np.linalg.norm(traj - traj.mean(axis=1, keepdims=True), axis=1)
    assert np.isclose(d[201] / d[200], 1 - eps * m.lambda2(m.laplacian(A)), rtol=1e-3)


def test_complete_graph_agrees_faster_than_ring():
    eps = 0.05
    r = [m.steps_to_agree(X0, A, eps) for A in (m.ring(8), m.complete(8))]
    assert r[1] < r[0] / 5


def test_disconnected_graph_never_agrees_but_each_part_does():
    A = np.zeros((8, 8))
    A[:4, :4], A[4:, 4:] = m.complete(4), m.complete(4)
    assert np.isclose(m.lambda2(m.laplacian(A)), 0, atol=1e-12)
    x = m.run(X0, A, 0.2, 500)[-1]
    assert np.allclose(x[:4], X0[:4].mean()) and np.allclose(x[4:], X0[4:].mean())
    assert abs(x[0] - x[7]) > 0.1


def test_step_size_above_two_over_lambda_max_diverges():
    A = m.ring(8)
    lmax = np.linalg.eigvalsh(m.laplacian(A))[-1]
    d = np.ptp(m.run(X0, A, 2.2 / lmax, 200)[-1])
    assert d > 100
