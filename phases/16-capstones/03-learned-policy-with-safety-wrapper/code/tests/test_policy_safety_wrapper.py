# 레슨 16/03 테스트: 모방 정책의 품질, 안전 wrapper 의 clip, 변화율 제한, stale hold, 고장 주입 때의 개입 횟수
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_policy", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

X, Y = m.demos()
POLICY = m.fit(X, Y)
QLIM = 1.3  # joint limit used to judge the dropped-observation run
TARGET = 1.0


def run(safe, **kw):
    return m.rollout(POLICY, TARGET, safety=m.Safety() if safe else None, **kw)


def test_demos_are_saturated_expert_actions():
    assert X.shape[1] == 2 and len(X) == len(Y) > 1000
    assert np.abs(Y).max() <= m.UMAX + 1e-12
    assert np.isclose(Y[0], m.expert(X[0]))


def test_policy_imitates_the_expert_on_fresh_episodes():
    Xt, Yt = m.demos(n_episodes=10, seed=99)  # different starts and targets than the training set
    err = np.abs([POLICY(o) - y for o, y in zip(Xt, Yt)])
    assert err.mean() < 0.1


def test_clean_run_reaches_the_target_with_and_without_the_wrapper():
    for safe in (False, True):
        r = run(safe)
        assert abs(r["q"][-1] - TARGET) < 0.03


def test_wrapper_clips_to_the_torque_limit():
    s = m.Safety(du=100.0)
    assert s(50.0, 0) == m.UMAX and s(-50.0, 0) == -m.UMAX
    assert s.n["clip"] == 2


def test_wrapper_limits_the_rate_of_change():
    s = m.Safety(du=0.4)
    out = [s(3.0, 0) for _ in range(5)] + [s(-3.0, 0)]
    assert np.allclose(np.diff([0.0] + out), [0.4] * 5 + [-0.4])  # one step of 0.4 either way
    assert s.n["rate"] == 6


def test_stale_observation_holds_zero_after_max_age():
    s = m.Safety(du=100.0, max_age=3)
    s(2.0, 0)
    assert s(2.0, 3) == 2.0 and s.n["hold"] == 0  # still trusted: age 3 is not over the limit
    assert s(2.0, 4) == 0.0 and s.n["hold"] == 1


def test_a_policy_spike_is_contained():
    spike = {30: 40.0}
    raw, safe = run(False, glitch=spike), run(True, glitch=spike)
    assert np.abs(raw["u"]).max() > 30
    assert np.abs(safe["u"]).max() <= m.UMAX
    assert safe["n"]["clip"] >= 1 and abs(safe["q"][-1] - TARGET) < 0.05


def test_dropped_observations_overshoot_without_the_wrapper_but_not_with_it():
    drop = range(10, 36)
    raw, safe = run(False, drop=drop), run(True, drop=drop)
    assert raw["q"].max() > QLIM and safe["q"].max() < QLIM
    assert safe["n"]["hold"] > 0 and abs(safe["q"][-1] - TARGET) < 0.05


def test_rollout_is_deterministic():
    assert np.array_equal(run(True, drop=range(10, 20))["q"], run(True, drop=range(10, 20))["q"])


def test_non_finite_action_requests_zero_and_the_wrapper_recovers():
    s = m.Safety()
    out = [s(1.0, 0), s(float("nan"), 0), s(float("inf"), 0), s(1.0, 0)]
    assert all(np.isfinite(out))  # a NaN must not be stored in the rate-limit state
    assert out[2] <= out[1] <= out[0]  # bad actions request zero, so the push eases down
    assert out[3] > out[2] and s.n["hold"] == 2


def test_always_max_torque_is_bounded_in_command_but_not_in_position():
    r = m.rollout(lambda obs: 3.0, TARGET, safety=m.Safety())
    assert np.abs(r["u"]).max() <= m.UMAX  # the wrapper bounds the command ...
    assert abs(r["q"].max() - 8.5) < 0.05  # ... but a bounded command alone does not keep the joint inside its limit
