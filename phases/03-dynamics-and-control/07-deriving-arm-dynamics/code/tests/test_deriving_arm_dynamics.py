# 레슨 03/07 테스트: 에너지에서 유도한 M 과 Lagrange 토크가 Newton-Euler, 03/05 의 식과 일치하는지
import importlib.util
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m = load("lesson_derive", HERE / "main.py")
ct = load("lesson_ct", HERE.parents[1] / "05-computed-torque" / "code" / "main.py")
P = dict(m1=1.0, m2=1.5, l1=0.5, lc1=0.2, lc2=0.3, I1=0.03, I2=0.05)
RNG = np.random.default_rng(1)


def states(n=20):
    return [(RNG.uniform(-3, 3, 2), RNG.uniform(-4, 4, 2), RNG.uniform(-5, 5, 2)) for _ in range(n)]


def test_mass_is_symmetric_positive_definite():
    for q, _, _ in states():
        M = m.mass(q, P)
        assert np.allclose(M, M.T, atol=1e-6)
        assert np.linalg.eigvalsh(M).min() > 0


def test_mass_from_energy_matches_the_closed_form_of_lesson_05():
    for q, _, _ in states():
        assert np.allclose(m.mass(q, P), ct.mass(q, P), atol=1e-6)


def test_lagrange_and_newton_euler_give_the_same_torque():
    for q, qd, qdd in states():
        assert np.allclose(m.lagrange_tau(q, qd, qdd, P), m.newton_euler(q, qd, qdd, P), atol=1e-5)


def test_torque_matches_lesson_05_inverse_dynamics():
    for q, qd, qdd in states():
        assert np.allclose(m.lagrange_tau(q, qd, qdd, P), ct.inverse_dynamics(q, qd, qdd, P), atol=1e-5)


def test_torque_is_linear_in_acceleration():
    q, qd, qdd = states(1)[0]
    t0, t1 = m.lagrange_tau(q, qd, 0 * qdd, P), m.lagrange_tau(q, qd, qdd, P)
    assert np.allclose(t1 - t0, m.mass(q, P) @ qdd, atol=1e-6)


def test_energy_is_conserved_with_no_torque():
    drift = m.energy_drift(P, np.array([0.3, 1.0]), np.array([2.0, -1.0]), T=1.0)
    assert abs(drift) < 1e-6


def test_a_flipped_coriolis_sign_is_caught_by_the_energy_test():
    drift = m.energy_drift(P, np.array([0.3, 1.0]), np.array([2.0, -1.0]), T=1.0, h_sign=-1)
    assert abs(drift) > 1e-2
