# 레슨 07/05 테스트: Jacobian 유한차분 검사, NEES 일관성, 큰 초기 heading 오차의 발산
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_ekf", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

X = np.array([1.0, -0.5, 0.7])
U = np.array([1.0, 0.3])
LM = np.array([3.0, 2.0])


def numeric_jac(fun, x, eps=1e-6):
    cols = []
    for i in range(len(x)):
        d = np.zeros(len(x))
        d[i] = eps
        cols.append((fun(x + d) - fun(x - d)) / (2 * eps))
    return np.array(cols).T


def test_motion_jacobian_matches_finite_differences():
    assert np.allclose(m.jac_f(X, U), numeric_jac(lambda x: m.f(x, U), X), atol=1e-6)


def test_measurement_jacobian_matches_finite_differences():
    num = numeric_jac(lambda x: m.h(x, LM), X)
    assert np.allclose(m.jac_h(X, LM), num, atol=1e-6)


def test_bearing_wraps_instead_of_jumping_by_two_pi():
    x = np.array([0.0, 0.0, np.pi - 0.01])
    z = m.h(x, np.array([-1.0, -0.05]))  # landmark almost straight ahead of a robot facing -x
    assert np.isclose(z[1], 0.06, atol=1e-3)  # raw atan2 minus heading would give -6.22


def test_update_never_grows_covariance():
    P = np.diag([0.5, 0.5, 0.2])
    x, P2 = m.update(X, P, m.h(X, LM) + [0.1, 0.02], LM, m.R)
    assert np.all(np.linalg.eigvalsh(P - P2) > -1e-12)


def test_consistent_filter_has_nees_near_state_dimension():
    nees = m.mean_nees(seeds=150, heading_offset=0.0)
    assert 2.4 < nees < 4.2  # the state has 3 dimensions


def test_large_initial_heading_error_makes_the_filter_inconsistent():
    one = m.LMS[:1]  # one landmark gives too little information to pull a bad linearisation back
    good = m.mean_nees(seeds=30, heading_offset=0.0, lms=one)
    bad = m.mean_nees(seeds=30, heading_offset=1.5, lms=one)  # filter claims 0.1 rad std, truth is 1.5 rad away
    assert bad > 20 * good


def test_more_landmarks_rescue_the_same_bad_start():
    assert m.mean_nees(seeds=30, heading_offset=1.0) < 6.0  # four landmarks recover from 1 rad


def test_filter_beats_dead_reckoning_with_a_good_start():
    truth, est, dr, _ = m.run(np.random.default_rng(3), steps=80)
    assert np.linalg.norm(est[-1, :2] - truth[-1, :2]) < 0.5 * np.linalg.norm(dr[-1, :2] - truth[-1, :2])
