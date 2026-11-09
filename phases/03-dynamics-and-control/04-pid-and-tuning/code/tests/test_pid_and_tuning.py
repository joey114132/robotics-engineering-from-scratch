# 레슨 03/04 테스트: P 의 잔류 오차, I 의 제거, D 의 감쇠, windup, 올린 gain 의 떨림과 고유값
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_pid", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

J, B, DT = 1.0, 2.0, 1e-3


def run(kp, ki, kd, n=10000, **kw):
    return m.simulate(J, B, kp, ki, kd, DT, n, **kw)


def test_friction_sets_terminal_speed():
    q, _, _ = m.simulate(J, B, 0.0, 0.0, 0.0, DT, 8000, load=-2.0)  # pushed with 2 Nm, friction 2 Nm s/rad
    assert np.isclose((q[-1] - q[-1000]) / 1.0, 1.0, rtol=0.01)  # speed -> 2/2 = 1 rad/s


def test_p_with_damping_leaves_offset_load_over_kp():
    q, _, _ = run(100.0, 0.0, 20.0, load=20.0, t_load=5.0)
    assert np.isclose(1.0 - q[-1], 20.0 / 100.0, rtol=0.01)


def test_integral_term_removes_the_offset():
    q, _, _ = run(100.0, 200.0, 20.0, load=20.0, t_load=5.0)
    assert abs(1.0 - q[-1]) < 1e-3


def test_derivative_term_cuts_overshoot():
    ring = m.overshoot(run(100.0, 0.0, 0.0)[0])
    calm = m.overshoot(run(100.0, 0.0, 20.0)[0])
    assert ring > 0.5 and calm < 0.01


def test_anti_windup_cuts_overshoot_against_saturation():
    kw = dict(q_des=2.0, umax=20.0, n=12000)
    wound, _, I1 = run(100.0, 300.0, 20.0, anti_windup=False, **kw)
    clamped, _, I2 = run(100.0, 300.0, 20.0, anti_windup=True, **kw)
    assert I1.max() > 4 * I2.max()
    assert m.overshoot(wound, 2.0) > 3 * m.overshoot(clamped, 2.0)


def test_anti_windup_changes_nothing_when_never_saturated():
    a, _, _ = run(100.0, 200.0, 20.0, umax=1e9, anti_windup=True)
    b, _, _ = run(100.0, 200.0, 20.0, umax=1e9, anti_windup=False)
    assert np.allclose(a, b)


def test_eigenvalues_predict_growth_for_both_gain_sets():
    for kd, stable in ((2.0, True), (60.0, False)):
        rho = m.spectral_radius(0.02, 0.1, 400.0, kd, DT)
        q, _, _ = m.simulate(0.02, 0.1, 400.0, 0.0, kd, DT, 300, q_des=1.0)
        grows = abs(q[-1]) > 1e3
        assert (rho < 1.0) == stable and grows == (not stable)


def test_raised_gains_buzz_the_command_every_tick():
    def flips(kp, kd):
        _, u, _ = m.simulate(0.02, 0.1, kp, 0.0, kd, DT, 400, umax=5.0)
        return np.mean(np.sign(u[1:]) != np.sign(u[:-1]))
    assert flips(40.0, 2.0) < 0.05 and flips(400.0, 60.0) > 0.9
