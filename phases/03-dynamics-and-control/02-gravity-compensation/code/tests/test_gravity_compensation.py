# 레슨 03/02 테스트: 2링크 중력토크와 정상상태 처짐 = 잔차 / kp
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_gravity", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

P = dict(m1=2.0, m2=1.0, l1=0.4, lc1=0.2, lc2=0.2)
Q_DES = np.array([0.0, 0.0])  # arm stretched out horizontally: worst case for gravity


def test_straight_up_needs_no_gravity_torque():
    tau = m.gravity_torque([np.pi / 2, 0.0], **P)
    assert np.allclose(tau, 0.0, atol=1e-12)


def test_horizontal_pose_matches_hand_calculation():
    g = 9.81
    tau = m.gravity_torque([0.0, 0.0], **P)
    assert np.isclose(tau[1], P["m2"] * P["lc2"] * g)
    assert np.isclose(tau[0], (P["m1"] * P["lc1"] + P["m2"] * P["l1"] + P["m2"] * P["lc2"]) * g)


def test_exact_feedforward_gives_zero_sag():
    sag = m.sag(Q_DES, kp=[50.0, 50.0], ff_scale=1.0, **P)
    assert np.allclose(sag, 0.0, atol=1e-9)


def test_underestimated_model_droops_by_residual_over_kp():
    kp = np.array([200.0, 200.0])
    sag = m.sag(Q_DES, kp=kp, ff_scale=0.8, **P)
    expected = -0.2 * m.gravity_torque(Q_DES, **P) / kp  # first-order
    assert np.all(sag < 0)
    assert np.allclose(sag, expected, rtol=0.15)


def test_overestimated_model_floats_up():
    sag = m.sag(Q_DES, kp=[200.0, 200.0], ff_scale=1.2, **P)
    assert np.all(sag > 0)


def test_kp_too_soft_for_the_gravity_gradient_raises_instead_of_lying():
    with __import__("pytest").raises(ValueError, match="did not converge"):
        m.sag(Q_DES, kp=[1.0, 1.0], ff_scale=0.8, **P)


def test_halving_kp_doubles_the_sag():
    s_hi = m.sag(Q_DES, kp=[200.0, 200.0], ff_scale=0.8, **P)
    s_lo = m.sag(Q_DES, kp=[100.0, 100.0], ff_scale=0.8, **P)
    assert np.allclose(s_lo / s_hi, 2.0, rtol=0.1)
