# 레슨 03/03 테스트: 가상 스프링-댐퍼, 처짐 = F/K, 감쇠비에 따른 overshoot
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_impedance", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

J = 1.0


def run(K, zeta, F=2.0, T=6.0, dt=1e-3):
    D = m.damping_for_zeta(K, J, zeta)
    return m.simulate(J=J, K=K, D=D, f_ext=F, dt=dt, n=int(T / dt))


def test_torque_law_has_spring_damper_and_gravity_terms():
    tau = m.impedance_torque(q=0.1, qd=0.5, q_des=0.3, K=40.0, D=2.0, tau_g=1.5)
    assert np.isclose(tau, 40.0 * 0.2 - 2.0 * 0.5 + 1.5)


def test_steady_deflection_is_force_over_stiffness():
    q = run(K=100.0, zeta=1.0)
    assert np.isclose(q[-1], 2.0 / 100.0, rtol=0.01)


def test_doubling_stiffness_halves_deflection():
    d1 = run(K=100.0, zeta=1.0)[-1]
    d2 = run(K=200.0, zeta=1.0)[-1]
    assert np.isclose(d1 / d2, 2.0, rtol=0.02)


def test_critical_damping_does_not_overshoot():
    q = run(K=100.0, zeta=1.0)
    assert q.max() <= q[-1] * 1.001


def test_underdamped_overshoot_matches_theory():
    zeta = 0.2
    q = run(K=100.0, zeta=zeta)
    overshoot = q.max() / q[-1] - 1.0
    theory = np.exp(-np.pi * zeta / np.sqrt(1 - zeta**2))
    assert np.isclose(overshoot, theory, atol=0.03)


def test_damper_check_alone_does_not_certify_a_spring_and_damper_loop():
    # dt*D/J = 0.1 passes the damper-only check, but the spring term dt^2 K/J = 100 does not
    q = m.simulate(J=1.0, K=10000.0, D=1.0, f_ext=2.0, dt=0.1, n=100)
    assert 0.1 * 1.0 / 1.0 < 1 and np.abs(q).max() > 1e6


def test_full_sampling_limit_matches_the_simulation():
    checked = 0
    for dt in (1e-3, 1e-2, 1e-1):
        for K in (1e2, 1e3, 1e4, 1e5):
            for D in (1.0, 20.0, 200.0):
                lhs = dt * dt * K + 2 * dt * D  # J = 1
                if 0.7 < lhs / 4 < 1.4 or 0.7 < dt * D / 2 < 1.4:
                    continue  # too close to the edge for a finite run to tell
                with np.errstate(all="ignore"):
                    q = m.simulate(J=1.0, K=K, D=D, f_ext=2.0, dt=dt, n=int(30 / dt))
                stable = bool(np.abs(q).max() < 1e3)
                assert stable == (lhs < 4 and dt * D < 2), (dt, K, D)
                checked += 1
    assert checked >= 20
