# 레슨 15/03 테스트: 계층별 한계가 서로 어긋나면 가장 빡빡한 것이 조용히 이기고, 시작 점검이 전부 보고한다
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_limits", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_aligned_stack_has_no_mismatch():
    assert m.check_limits(m.ALIGNED) == []


def test_mismatched_stack_reports_every_mismatch_not_just_the_first():
    found = {(q, up, down) for q, up, down, *_ in m.check_limits(m.MISMATCHED)}
    assert found == {("pos", "planner", "controller"), ("vel", "controller", "drive"), ("tau", "controller", "drive")}


def test_equal_limits_are_not_a_mismatch():
    L = {k: dict(v, vel=1.0) for k, v in m.ALIGNED.items()}
    assert not [r for r in m.check_limits(L) if r[0] == "vel"]


def test_a_layer_with_no_limit_is_skipped_and_the_next_pair_is_compared():
    L = {k: dict(v) for k, v in m.ALIGNED.items()}
    L["controller"]["pos"] = None
    L["planner"]["pos"] = 2.5  # looser than the drive, two layers away
    assert [(r[0], r[1], r[2]) for r in m.check_limits(L)] == [("pos", "planner", "drive")]


def test_effective_limit_is_the_tightest_layer_and_names_it():
    assert m.effective(m.MISMATCHED, "vel") == (1.5, "drive")
    assert m.effective(m.MISMATCHED, "pos") == (1.8, "controller")
    assert m.effective(m.ALIGNED, "vel") == (1.0, "planner")


def test_require_nested_raises_with_all_messages_and_passes_when_aligned():
    m.require_nested(m.ALIGNED)
    with pytest.raises(ValueError) as e:
        m.require_nested(m.MISMATCHED)
    assert str(e.value).count("wins silently") == 3


def test_joint_speed_is_held_to_the_tightest_layer_while_the_planner_thinks_it_is_faster():
    run = m.simulate(m.MISMATCHED)
    assert run["max_speed"] <= 1.5 + 0.02 and run["planner_speed"] == 3.0


def test_mismatch_makes_the_joint_lag_far_behind_its_reference():
    bad, good = m.simulate(m.MISMATCHED), m.simulate(m.ALIGNED)
    assert bad["peak_err"] > 5 * good["peak_err"]
    assert bad["peak_err"] > 0.5 and good["peak_err"] < 0.15
