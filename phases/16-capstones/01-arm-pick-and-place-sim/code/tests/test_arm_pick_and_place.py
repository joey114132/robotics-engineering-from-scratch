# 레슨 16/01 테스트: 동역학 모델 검증, IK 웨이포인트, 궤적 연속성, 중력 feedforward 유무에 따른 pass/fail
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_pickplace", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

A, B = (0.50, 0.10), (0.15, 0.50)


def test_ik_waypoints_reach_every_target():
    for p in (A, B, (0.5, 0.3), (0.15, 0.6)):
        assert np.allclose(m.fk(m.ik(p)), p, atol=1e-9)


def test_inertia_is_symmetric_positive_definite():
    rng = np.random.default_rng(0)
    for q in rng.uniform(-3, 3, (20, 2)):
        M = m.inertia(q)
        assert np.allclose(M, M.T)
        assert np.linalg.eigvalsh(M).min() > 0


def test_free_swing_conserves_energy():
    """No torque, no damping: kinetic + potential energy must stay put. This checks the Coriolis terms."""
    q, v, dt = np.array([0.3, -0.6]), np.array([1.0, 2.0]), 1e-4

    def energy(q, v):
        pe = m.G * (m.P["m1"] * m.P["lc1"] * np.sin(q[0]) + m.P["m2"] * (m.P["l1"] * np.sin(q[0]) + m.P["lc2"] * np.sin(q[0] + q[1])))
        return 0.5 * v @ m.inertia(q) @ v + pe

    e0 = energy(q, v)
    for _ in range(20000):
        q, v = m.step(q, v, np.zeros(2), dt)
    assert abs(energy(q, v) - e0) < 0.02 * (abs(e0) + 1)


def test_trajectory_is_smooth_and_hits_waypoints():
    wp = [np.array([0.0, 0.5]), np.array([0.4, 1.0]), np.array([1.0, 0.2])]
    ref = m.reference(wp, 1.0)
    for k, t in enumerate((0.0, 1.0, 2.0)):
        q, v, a = ref(t)
        assert np.allclose(q, wp[k], atol=1e-9)
        assert np.allclose(v, 0, atol=1e-9) and np.allclose(a, 0, atol=1e-9)
    assert np.allclose(ref(0.999)[0], ref(1.001)[0], atol=1e-3)  # no jump at the join


def test_gravity_feedforward_places_within_tolerance():
    r = m.run(A, B, ff=1.0)
    assert r["place_err"] < 0.002 and r["pick_err"] < 0.002 and r["passed"]


def test_without_feedforward_the_arm_sags_and_fails():
    good, bad = m.run(A, B, ff=1.0), m.run(A, B, ff=0.0)
    assert not bad["passed"] and bad["place_err"] > 0.02
    assert bad["place_err"] > 20 * good["place_err"]


def test_sag_matches_residual_over_kp():
    """Lesson 03/02: with ff = 0 the first-order error is tau_g / kp, and q1 sits below the command."""
    r = m.run(A, B, ff=0.0)
    q_des = r["q_ref"][-1]
    expected = -m.gravity(q_des) / m.KP
    assert (r["q"][-1] - q_des)[0] < 0  # joint 2 can rise: its gravity torque changes sign past 90 degrees of absolute angle
    assert np.allclose(r["q"][-1] - q_des, expected, rtol=0.25)
