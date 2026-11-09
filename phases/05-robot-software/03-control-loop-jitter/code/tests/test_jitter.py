# 레슨 05/03 테스트: 고정 주기 loop 의 period jitter, deadline miss, 평균이 최악을 가리는 현상
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_jitter", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

T = 1e-3


def test_without_spikes_nothing_misses_and_jitter_is_small():
    s, d = m.simulate(5000, spike_p=0.0)
    st = m.stats(s, d, T)
    assert st["misses"] == 0 and st["worst"] < 0.2 * T


def test_absolute_deadlines_keep_the_mean_period_at_T_even_with_spikes():
    s, d = m.simulate(5000, spike_p=0.003)
    assert abs(m.stats(s, d, T)["mean_period"] - T) < 0.01 * T


def test_spikes_make_the_worst_case_far_larger_than_the_average_jitter():
    s, d = m.simulate(5000, spike_p=0.003)
    st = m.stats(s, d, T)
    assert abs(st["mean_jitter"]) < 0.01 * T and st["worst"] > 0.5 * T


def test_p99_can_look_fine_while_the_worst_case_does_not():
    s, d = m.simulate(5000, spike_p=0.003)
    st = m.stats(s, d, T)
    assert st["p99"] < 0.2 * T < 0.5 * T < st["worst"]


def test_miss_count_matches_an_independent_count():
    s, d = m.simulate(5000, spike_p=0.003)
    assert m.stats(s, d, T)["misses"] == sum(d[i] > (i + 1) * T for i in range(len(d) - 1))
    assert m.stats(s, d, T)["misses"] > 0


def test_work_longer_than_the_period_misses_every_deadline():
    s, d = m.simulate(200, work=1.5 * T, spike_p=0.0)
    assert m.stats(s, d, T)["misses"] == 199


def test_relative_sleep_drifts_by_work_plus_latency_each_cycle():
    s, d = m.simulate(2000, spike_p=0.0, relative=True)
    assert m.stats(s, d, T)["mean_period"] > T + 1.5e-4


def test_same_seed_gives_the_same_run_and_start_times_increase():
    a, _ = m.simulate(1000, seed=3)
    b, _ = m.simulate(1000, seed=3)
    assert np.array_equal(a, b) and np.all(np.diff(a) > 0)
