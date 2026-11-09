# 레슨 05/02 테스트: 단일 스레드 executor 에서 느린 callback 이 빠른 timer 를 굶기고, callback group 이 푸는 과정
import importlib.util
import pathlib

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_executors", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

# (name, period ms, duration ms, group, first release ms)
TIMER = ("timer", 10, 1, "fast", 1)
SLOW_SAME = ("slow", 100, 60, "fast", 0)
SLOW_OWN = ("slow", 100, 60, "slow", 0)
H = 1000


def lat(log, name):
    return m.latencies(log, name)


def test_idle_executor_starts_a_timer_on_release():
    log = m.simulate([TIMER], threads=1, horizon=H)
    assert max(lat(log, "timer")) == 0


def test_single_thread_slow_callback_delays_the_timer_by_its_duration():
    log = m.simulate([TIMER, SLOW_OWN], threads=1, horizon=H)
    assert max(lat(log, "timer")) == 59  # released 1 ms after the slow callback starts, which ends 60 ms later


def test_single_thread_misses_whole_timer_periods():
    log = m.simulate([TIMER, SLOW_OWN], threads=1, horizon=H)
    assert m.late_ticks(log, "timer", period=10) >= 40


def test_second_thread_with_its_own_group_removes_the_starvation():
    log = m.simulate([TIMER, SLOW_OWN], threads=2, horizon=H)
    assert max(lat(log, "timer")) == 0


def test_second_thread_in_the_same_mutually_exclusive_group_changes_nothing():
    one = m.simulate([TIMER, SLOW_SAME], threads=1, horizon=H)
    two = m.simulate([TIMER, SLOW_SAME], threads=2, horizon=H)
    assert max(lat(two, "timer")) == max(lat(one, "timer")) == 59


def test_a_mutually_exclusive_group_never_runs_two_callbacks_at_once():
    log = m.simulate([TIMER, SLOW_SAME], threads=4, horizon=H)
    spans = sorted((s, e) for _, _, s, e in log)
    assert all(b[0] >= a[1] for a, b in zip(spans, spans[1:]))


def test_never_more_callbacks_running_than_threads():
    log = m.simulate([TIMER, SLOW_OWN, ("extra", 30, 25, "x", 0)], threads=2, horizon=H)
    for t in range(H):
        assert sum(s <= t < e for _, _, s, e in log) <= 2


def test_slow_callback_itself_is_not_delayed_when_alone_on_its_thread():
    log = m.simulate([TIMER, SLOW_OWN], threads=2, horizon=H)
    assert max(lat(log, "slow")) == 0
