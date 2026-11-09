# 레슨 13/04 테스트: 학습 정책 안전 래퍼의 clip, 변화율 제한, 오래된 관측 처리, 로그
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_wrapper", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def mk(**kw):
    return m.Wrapper(**{**dict(lo=-1.0, hi=1.0, max_step=0.2, max_age=1, deadline=5), **kw})


def run(w, raws):
    return [w.act(t, 0.0, t, lambda o, v=v: v) for t, v in enumerate(raws)]


def test_value_above_the_limit_is_clipped():
    w = mk(max_step=10.0)
    assert run(w, [5.0, -9.0]) == [1.0, -1.0]
    assert [e["kind"] for e in w.log] == ["clip", "clip"]


def test_command_changes_by_at_most_max_step_per_tick():
    out = run(mk(), [1.0] * 6)
    assert np.allclose(out, [0.2, 0.4, 0.6, 0.8, 1.0, 1.0])


def test_non_finite_output_is_replaced_by_the_fallback_and_logged():
    w = mk(max_step=10.0)
    out = run(w, [0.5, float("nan"), float("inf")])
    assert out == [0.5, 0.0, 0.0]
    assert [e["kind"] for e in w.log] == ["nonfinite", "nonfinite"]


def test_missing_observation_holds_the_last_command_then_falls_back_after_the_deadline():
    w = mk(max_step=10.0, deadline=3)
    w.act(0, 0.0, 0, lambda o: 0.8)
    held = [w.act(t, None, None, lambda o: 99.0) for t in range(1, 4)]
    assert held == [0.8, 0.8, 0.8]
    assert w.act(4, None, None, lambda o: 99.0) == 0.0
    assert [e["kind"] for e in w.log] == ["hold", "hold", "hold", "fallback"]


def test_stale_observation_is_treated_like_a_missing_one():
    w = mk(max_step=10.0)
    w.act(0, 0.0, 0, lambda o: 0.5)
    assert w.act(5, 0.0, 1, lambda o: -1.0) == 0.5  # stamp 1 is 4 ticks old, max_age is 1
    assert w.log[-1]["kind"] == "hold"


def test_policy_is_not_called_without_a_usable_observation():
    w = mk()
    called = []
    w.act(0, None, None, lambda o: called.append(o) or 1.0)
    assert not called


def test_fuzzed_raw_commands_never_leave_limits_or_exceed_the_rate():
    rng = np.random.default_rng(0)
    w = mk()
    prev = 0.0
    for t in range(2000):
        raw = rng.choice([rng.normal(0, 5), float("nan"), float("inf"), -float("inf")])
        obs, stamp = (None, None) if rng.random() < 0.2 else (0.0, t - rng.integers(0, 4))
        out = w.act(t, obs, stamp, lambda o, r=raw: r)
        assert -1.0 <= out <= 1.0 and abs(out - prev) <= 0.2 + 1e-12
        prev = out


def test_well_behaved_policy_passes_through_without_any_log_entry():
    w = mk()
    out = run(w, [0.1, 0.2, 0.15, 0.1])
    assert out == [0.1, 0.2, 0.15, 0.1] and w.log == []


def test_same_inputs_give_identical_outputs_and_logs():
    raws = list(np.random.default_rng(1).normal(0, 2, 50))
    a, b = mk(), mk()
    assert run(a, raws) == run(b, raws) and a.log == b.log


def test_wrapper_contains_a_misbehaving_policy_in_simulation():
    raw_run, wrapped = m.simulate(False), m.simulate(True)
    assert np.abs(raw_run["x"]).max() > 1.5
    assert np.abs(wrapped["x"]).max() <= 1.05
    assert abs(wrapped["x"][-1]) < 0.15
    assert sum(wrapped["counts"].values()) > 10
