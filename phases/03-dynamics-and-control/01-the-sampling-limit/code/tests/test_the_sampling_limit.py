# 레슨 03/01 테스트: 홀드된 댐퍼 명령의 안정 한계 dt*kd/J < 2
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_sampling", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

J, DT = 0.02, 0.001  # kg m^2, s  -> boundary kd values: J/DT = 20, 2J/DT = 40


def test_one_step_multiplies_velocity_by_one_minus_ratio():
    assert np.isclose(m.step_damper(2.0, J, 10.0, DT), 2.0 * (1 - DT * 10.0 / J))


def test_below_one_decays_without_sign_change():
    v = m.simulate_damper(1.0, J, 10.0, DT, 50)
    assert all(a > b > 0 for a, b in zip(v, v[1:]))


def test_between_one_and_two_flips_sign_but_decays():
    v = m.simulate_damper(1.0, J, 30.0, DT, 50)  # ratio 1.5
    assert all(a * b < 0 for a, b in zip(v, v[1:]))
    assert abs(v[-1]) < abs(v[0])


def test_above_two_grows_every_step():
    v = m.simulate_damper(1.0, J, 50.0, DT, 20)  # ratio 2.5
    assert all(abs(b) > abs(a) for a, b in zip(v, v[1:]))


def test_limits_are_J_over_dt_and_two_J_over_dt():
    assert np.isclose(m.max_smooth_kd(J, DT), 20.0)
    assert np.isclose(m.max_stable_kd(J, DT), 40.0)


def test_classification_on_both_sides_of_each_boundary():
    assert m.classify(J, 19.0, DT) == "smooth"
    assert m.classify(J, 21.0, DT) == "chatter"
    assert m.classify(J, 39.0, DT) == "chatter"
    assert m.classify(J, 41.0, DT) == "divergent"


def test_low_inertia_joint_crosses_the_line_first():
    kd = 5.0  # one gain, two joints
    assert m.classify(0.5, kd, DT) == "smooth"      # shoulder-like, large J
    assert m.classify(0.001, kd, DT) == "divergent"  # wrist-like, small J


def test_ratio_exactly_one_is_deadbeat_not_chatter():
    assert m.step_damper(1.0, 1.0, 2.0, 0.5) == 0.0  # r = 1: velocity is zero after one tick, no sign flip
    assert m.classify(1.0, 2.0, 0.5) == "smooth"
    assert m.classify(1.0, 4.0, 0.5) == "divergent"  # r = 2: |factor| = 1, rings forever, never decays
