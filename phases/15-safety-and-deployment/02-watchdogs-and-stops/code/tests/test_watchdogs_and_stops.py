# 레슨 15/02 테스트: 하트비트 watchdog, 정지 거리 v^2/(2a), 토크 차단과 ramp 정지, timeout 상한
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_watchdog", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_watchdog_trips_only_after_silence_longer_than_the_timeout():
    wd = m.Watchdog(0.05)
    wd.beat(1.0)
    assert not wd.tripped(1.049) and wd.tripped(1.051)


def test_a_timeout_shorter_than_a_late_beat_trips_falsely():
    for timeout, expect_trip in ((0.02, True), (0.03, False)):
        wd = m.Watchdog(timeout)
        for t in (0.0, 0.01, 0.02):
            wd.beat(t)
        assert wd.tripped(0.044) is expect_trip  # next beat is 25 ms late


def test_stop_distance_formula_matches_a_frictionless_ramped_stop():
    r = m.simulate("ramp", b=0.0, q_lim=100.0, v0=2.0, a=8.0)
    assert r["stop_dist"] == pytest.approx(m.stop_distance(2.0, 8.0), rel=0.01)
    assert r["stop_time"] == pytest.approx(2.0 / 8.0, abs=0.005)


def test_ramped_stop_with_friction_never_goes_farther_than_the_formula():
    r = m.simulate("ramp", q_lim=100.0)
    assert r["stop_dist"] <= m.stop_distance(r["v_trip"], 8.0) + 1e-6


def test_torque_cut_is_a_coast_not_a_stop():
    r = m.simulate("cut", q_lim=100.0)
    assert r["stop_dist"] == pytest.approx(0.5 * r["v_trip"] / 0.2, rel=0.03)  # J v / b
    assert r["stop_dist"] > 10 * m.simulate("ramp", q_lim=100.0)["stop_dist"]


def test_cut_hits_the_limit_where_ramp_stops_short_with_the_same_timeout():
    assert m.simulate("cut", timeout=0.05)["hit"]
    assert not m.simulate("ramp", timeout=0.05)["hit"]


def test_overrun_never_exceeds_travel_during_timeout_plus_braking_distance():
    for timeout in (0.02, 0.05, 0.1, 0.2):
        r = m.simulate("ramp", timeout=timeout, q_lim=100.0)
        assert r["overrun"] <= r["v_loss"] * timeout + m.stop_distance(r["v_loss"], 8.0) + 1e-6


def test_max_timeout_matches_hand_calculation_and_separates_safe_from_unsafe():
    assert m.max_timeout(0.5, 2.0, 8.0) == pytest.approx(0.125)
    assert not m.simulate("ramp", timeout=0.10)["hit"]
    assert m.simulate("ramp", timeout=0.16)["hit"]


def test_max_timeout_raises_when_braking_alone_does_not_fit():
    with pytest.raises(ValueError):
        m.max_timeout(0.2, 2.0, 8.0)
