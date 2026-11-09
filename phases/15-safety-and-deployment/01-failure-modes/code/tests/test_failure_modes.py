# 레슨 15/01 테스트: 관절 제어 루프에 결함 다섯 가지를 넣고 영향과 감지 가능성을 확인한다
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_failure_modes", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def stats(fault, **kw):
    run = m.simulate(fault, **kw)
    return run, m.metrics(run), m.alarm_time(run)


def test_healthy_loop_settles_without_hitting_a_limit_or_an_alarm():
    _, s, alarm = stats("none")
    assert s["final_err"] < 0.01 and not s["hit"] and alarm is None


def test_wrong_sign_runs_away_to_the_limit_and_is_flagged_before_it_arrives():
    _, s, alarm = stats("wrong_sign")
    assert s["hit"] and s["final_err"] > 2.9
    assert alarm is not None and alarm < s["t_limit"]


def test_stuck_sensor_freezes_the_reading_while_the_joint_hits_the_limit():
    run, s, alarm = stats("stuck")
    after = run[:, 0] >= 0.3
    assert np.ptp(run[after, 4]) == 0.0  # the controller sees a calm, constant joint
    assert s["hit"] and s["final_err"] > 2.9
    assert 0.3 < alarm < 0.4  # only the frozen-reading check can see it


def test_dropout_to_zero_overdrives_the_joint_but_loop_recovers_after_the_gap():
    _, s, alarm = stats("dropout")
    assert s["hit"] and s["final_err"] < 0.01
    assert abs(alarm - 0.3) < 0.002  # the reading jumps in one tick


def test_delay_is_harmless_when_short_and_unstable_when_long():
    short = m.metrics(m.simulate("delay", delay=0.02))
    long_ = m.metrics(m.simulate("delay", delay=0.1))
    assert short["final_err"] < 0.01 and long_["final_err"] > 0.3


def test_saturation_never_hits_the_limit_but_only_a_late_check_notices():
    _, s, alarm = stats("saturation")
    assert not s["hit"] and s["final_err"] > 0.05
    assert alarm is not None and alarm >= 2.0


def test_ranking_puts_the_two_runaway_faults_first_and_the_healthy_loop_last():
    rows = m.ranked()
    assert {r["fault"] for r in rows[:2]} == {"wrong_sign", "stuck"}
    assert rows[-1]["fault"] == "none"
