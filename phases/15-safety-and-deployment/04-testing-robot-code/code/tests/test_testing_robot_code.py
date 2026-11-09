# 레슨 15/04 테스트: fake clock, mock joint, 녹화 trace replay, 속성 테스트, 그리고 부호 버그를 잡는 테스트
import importlib.util
import json
import pathlib

import numpy as np
import pytest

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lesson_testing", HERE.parent / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
GOLDEN = json.loads((HERE / "golden_trace.json").read_text())


def make(polarity=1):
    clock = m.FakeClock()
    return clock, m.Controller(clock, polarity=polarity)


def check_step_direction(polarity):
    """The test that catches a wrong sign: after 0.3 s of a step to 1.0 the joint must be closer to 1.0."""
    clock, ctrl = make(polarity)
    joint = m.MockJoint()
    m.run(ctrl, joint, clock, q_ref=1.0, T=0.3)
    assert abs(1.0 - joint.q) < 0.7, f"joint moved away from the target: q = {joint.q:.2f}"


def replay(ctrl, clock, trace, dt=0.01):
    for q_meas, q_ref, tau in trace:
        clock.advance(dt)
        assert ctrl.update(q_meas, q_ref) == pytest.approx(tau, abs=1e-9)


def test_fake_clock_moves_only_when_told():
    clock = m.FakeClock()
    assert clock.now() == 0.0
    clock.advance(0.5)
    clock.advance(0.25)
    assert clock.now() == 0.75


def test_a_long_gap_between_updates_gives_zero_torque_without_any_sleeping():
    clock, ctrl = make()
    clock.advance(0.01)
    assert ctrl.update(0.0, 1.0) != 0.0
    clock.advance(0.5)  # ten timeouts pass in zero real time
    assert ctrl.update(0.0, 1.0) == 0.0 and ctrl.stale
    clock.advance(0.01)
    assert ctrl.update(0.0, 1.0) != 0.0 and not ctrl.stale


def test_healthy_controller_passes_the_step_direction_test_and_settles():
    check_step_direction(polarity=1)
    clock, ctrl = make()
    joint = m.MockJoint()
    m.run(ctrl, joint, clock, q_ref=1.0, T=2.0)
    assert abs(joint.q - 1.0) < 0.02


def test_step_direction_test_catches_the_sign_bug():
    with pytest.raises(AssertionError, match="moved away"):
        check_step_direction(polarity=-1)


def test_replaying_the_recorded_trace_reproduces_every_output():
    clock, ctrl = make()
    replay(ctrl, clock, GOLDEN)
    assert len(GOLDEN) == 300


def test_replay_catches_the_sign_bug_on_the_first_loud_sample():
    clock, ctrl = make(polarity=-1)
    with pytest.raises(AssertionError):
        replay(ctrl, clock, GOLDEN)


def test_mock_joint_refuses_a_command_over_its_limit_and_nan():
    joint = m.MockJoint(tau_limit=10.0)
    for bad in (10.5, -11.0, float("nan")):
        with pytest.raises(ValueError):
            joint.step(bad, 0.01)
    assert joint.commands == []


def test_property_torque_never_exceeds_the_limit_for_any_input_including_nan_and_inf():
    rng = np.random.default_rng(0)
    clock, ctrl = make()
    joint = m.MockJoint(tau_limit=ctrl.tau_max)
    specials = [float("nan"), float("inf"), -float("inf"), 1e12, -1e12]
    for _ in range(3000):
        clock.advance(float(rng.choice([0.0, 0.001, 0.01, 0.2])))
        q, r = (specials[rng.integers(5)] if rng.random() < 0.1 else rng.uniform(-1e3, 1e3) for _ in range(2))
        tau = ctrl.update(q, r)
        assert np.isfinite(tau) and abs(tau) <= ctrl.tau_max
        joint.step(tau, 0.001)  # the mock would raise if anything over-limit got through
