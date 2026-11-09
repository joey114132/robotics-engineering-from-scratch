# 레슨 04/02 테스트: 토크 모드와 position 모드에서 외력에 대한 처짐, 모드 동치, admittance 보정
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_modes", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

KP_IN, PUSH = 400.0, 2.0


def deflection(mode, K, **kw):
    t, q = m.run(mode, K=K, push=PUSH, kp_in=KP_IN, **kw)
    return q[-1]


def test_torque_mode_deflection_is_push_over_requested_stiffness():
    for K in (20.0, 50.0):
        assert np.isclose(deflection("torque", K), PUSH / K, rtol=0.02)


def test_position_mode_deflection_is_push_over_inner_gain():
    assert np.isclose(deflection("position", 20.0), PUSH / KP_IN, rtol=0.02)


def test_position_mode_ignores_the_outer_stiffness_request():
    assert np.isclose(deflection("position", 20.0), deflection("position", 5.0), rtol=1e-9)


def test_position_mode_is_a_torque_mode_with_a_fixed_inner_law():
    _, qp = m.run("position", push=PUSH, kp_in=KP_IN, kd_in=40.0)
    _, qt = m.run("torque", K=KP_IN, D=40.0, push=PUSH)
    assert np.allclose(qp, qt, atol=1e-9)


def test_admittance_layer_adds_compliance_from_measured_push():
    K = 20.0
    assert np.isclose(deflection("admittance", K), PUSH * (1 / K + 1 / KP_IN), rtol=0.02)


def test_torque_mode_can_be_stiffer_than_the_inner_gain_but_admittance_cannot():
    stiff = PUSH / deflection("torque", 2000.0)
    assert stiff > KP_IN
    assert PUSH / deflection("admittance", 2000.0) < KP_IN


def test_every_mode_tracks_the_command_when_nothing_pushes():
    for mode in ("torque", "position", "admittance"):
        t, q = m.run(mode, q_des=0.3, push=0.0)
        assert np.isclose(q[-1], 0.3, atol=1e-3)
