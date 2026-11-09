# 레슨 09/01 테스트: cubic, quintic, trapezoid 프로파일의 경계 조건과 가속도 계단이 만드는 jerk
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_traj", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

Q0, QF, T = 0.2, 1.4, 2.0


def ends(c):
    return m.poly(c, 0.0), m.poly(c, T)


def test_cubic_hits_position_and_zero_velocity_at_both_ends():
    (p0, v0, _), (p1, v1, _) = ends(m.cubic(Q0, QF, T))
    assert np.allclose([p0, p1, v0, v1], [Q0, QF, 0, 0], atol=1e-12)


def test_quintic_hits_position_velocity_and_acceleration_at_both_ends():
    (p0, v0, a0), (p1, v1, a1) = ends(m.quintic(Q0, QF, T))
    assert np.allclose([p0, p1, v0, v1, a0, a1], [Q0, QF, 0, 0, 0, 0], atol=1e-12)


def test_quintic_coefficients_match_a_generic_linear_solve():
    from math import factorial
    rows = [[factorial(k) / factorial(k - d) * t ** (k - d) if k >= d else 0.0 for k in range(6)] for d in range(3) for t in (0.0, T)]
    rhs = [Q0, QF, 0, 0, 0, 0]
    assert np.allclose(np.linalg.solve(rows, rhs), m.quintic(Q0, QF, T), atol=1e-9)


def test_cubic_starts_with_an_acceleration_jump_and_quintic_does_not():
    assert abs(m.poly(m.cubic(Q0, QF, T), 0.0)[2]) > 1.0
    assert abs(m.poly(m.quintic(Q0, QF, T), 0.0)[2]) < 1e-12


def test_trapezoid_reaches_the_target_and_covers_the_distance():
    f = m.trapezoid(Q0, QF, T, 0.5)
    t = np.linspace(0, T, 4001)
    p, v, _ = f(t)
    assert np.isclose(p[0], Q0) and np.isclose(p[-1], QF)
    assert np.isclose(np.sum((v[:-1] + v[1:]) / 2 * np.diff(t)), QF - Q0, atol=1e-4)
    assert np.isclose(v.max(), (QF - Q0) / (T - 0.5))


def test_discrete_jerk_of_cubic_grows_as_sampling_gets_finer_but_quintic_does_not():
    def jerk(c, dt):
        return m.peak_jerk(m.poly(c, np.arange(0, T + dt / 2, dt))[2], dt)
    cu, qu = m.cubic(Q0, QF, T), m.quintic(Q0, QF, T)
    assert jerk(cu, 0.001) > 8 * jerk(cu, 0.01)
    assert np.isclose(jerk(qu, 0.001), jerk(qu, 0.01), rtol=0.1)


def test_quintic_peak_jerk_matches_the_closed_form():
    assert np.isclose(m.peak_jerk(m.poly(m.quintic(Q0, QF, T), np.linspace(0, T, 20001))[2], T / 20000), 60 * (QF - Q0) / T**3, rtol=1e-3)


def test_quintic_matches_scipy_bernstein_polynomial_with_the_same_end_derivatives():
    interp = __import__("pytest").importorskip("scipy.interpolate")
    b = interp.BPoly.from_derivatives([0.0, T], [[Q0, 0, 0], [QF, 0, 0]])
    t = np.linspace(0, T, 50)
    assert np.allclose(b(t), m.poly(m.quintic(Q0, QF, T), t)[0], atol=1e-9)
