# 레슨 09/04 테스트: 부드러움 비용 + 장애물 penalty 의 gradient, 끝점 고정, 비용 감소, clearance
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_trajopt", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

OBS = [(np.array([3.5, 0.3]), 1.0), (np.array([7.0, -0.5]), 1.0)]


def start_path(n=22, seed=0):
    X = np.linspace([0.0, 0.0], [10.0, 0.0], n)
    X[1:-1, 1] += np.random.default_rng(seed).uniform(-0.15, 0.15, n - 2)
    return X


def clearance(X):
    return min(np.linalg.norm(x - c) - r for x in X for c, r in OBS)


def test_analytic_gradient_matches_finite_differences():
    X = start_path()
    g = m.grad(X, OBS)
    num = np.zeros_like(X)
    for i in range(1, len(X) - 1):
        for k in range(2):
            Xp, Xm = X.copy(), X.copy()
            Xp[i, k] += 1e-6
            Xm[i, k] -= 1e-6
            num[i, k] = (m.cost(Xp, OBS)[0] - m.cost(Xm, OBS)[0]) / 2e-6
    assert np.allclose(g, num, atol=1e-5)


def test_endpoints_never_move():
    X0 = start_path()
    X, _ = m.optimise(X0, OBS, iters=200)
    assert np.array_equal(X[0], X0[0]) and np.array_equal(X[-1], X0[-1])


def test_cost_never_increases_with_a_small_step():
    _, hist = m.optimise(start_path(), OBS, iters=400, lr=0.04)
    assert np.all(np.diff(hist) <= 1e-9)


def test_a_step_that_is_too_large_makes_the_cost_rise():
    _, hist = m.optimise(start_path(), OBS, iters=60, lr=0.5)
    assert np.any(np.diff(hist) > 0)


def test_without_obstacles_the_path_relaxes_to_an_evenly_spaced_straight_line():
    X, _ = m.optimise(start_path(), [], iters=3000, lr=0.2)
    assert np.allclose(X, np.linspace([0.0, 0.0], [10.0, 0.0], len(X)), atol=1e-3)


def test_penalty_is_zero_when_every_waypoint_is_far_from_every_obstacle():
    X = np.linspace([0.0, 5.0], [10.0, 5.0], 12)
    c, smooth, pen = m.cost(X, OBS)
    assert pen == 0.0 and np.isclose(c, smooth)


def test_the_start_path_collides_and_the_result_clears_every_obstacle():
    X0 = start_path()
    assert clearance(X0) < 0
    X, _ = m.optimise(X0, OBS, iters=4000, lr=0.04)
    assert clearance(X) > 0


def test_the_result_is_smoother_than_the_jittered_start():
    X0 = start_path()
    X, _ = m.optimise(X0, OBS, iters=4000, lr=0.04)
    acc = lambda P: np.abs(np.diff(P, 2, axis=0)).max()
    assert acc(X) < acc(X0)


def test_lbfgs_from_scipy_reaches_a_cost_no_worse_than_plain_gradient_descent():
    opt = __import__("pytest").importorskip("scipy.optimize")
    X0 = start_path()
    Xg, hist = m.optimise(X0, OBS, iters=4000, lr=0.04)

    def f(v):
        X = np.vstack([X0[0], v.reshape(-1, 2), X0[-1]])
        return m.cost(X, OBS)[0], m.grad(X, OBS)[1:-1].ravel()

    r = opt.minimize(f, X0[1:-1].ravel(), jac=True, method="L-BFGS-B")
    assert r.fun <= hist[-1] + 1e-3
