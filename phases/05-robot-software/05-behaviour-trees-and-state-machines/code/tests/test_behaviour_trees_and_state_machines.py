# 레슨 05/05 테스트: Sequence, Fallback, Retry 의 규칙과 running 재개, 간단한 상태 기계
import importlib.util
import pathlib

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_bt", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
S, F, R = m.SUCCESS, m.FAILURE, m.RUNNING


counted = m.scripted  # leaves count their own calls


def test_condition_reports_success_or_failure():
    assert m.condition("ok", lambda: True).tick([]) == S
    assert m.condition("no", lambda: False).tick([]) == F


def test_sequence_stops_at_first_failure():
    a, b, c = counted("a", [S]), counted("b", [F]), counted("c", [S])
    assert m.Sequence("seq", [a, b, c]).tick([]) == F
    assert c.calls == 0


def test_fallback_tries_next_child_only_after_failure():
    a, b, c = counted("a", [F]), counted("b", [S]), counted("c", [S])
    assert m.Fallback("fb", [a, b, c]).tick([]) == S
    assert (a.calls, b.calls, c.calls) == (1, 1, 0)


def test_fallback_fails_when_every_child_fails():
    assert m.Fallback("fb", [counted("a", [F]), counted("b", [F])]).tick([]) == F


def test_running_resumes_without_restarting_finished_siblings():
    a, b = counted("a", [S]), counted("b", [R, R, S])
    seq = m.Sequence("seq", [a, b])
    assert [seq.tick([]) for _ in range(3)] == [R, R, S]
    assert (a.calls, b.calls) == (1, 3)


def test_fallback_keeps_its_running_child_instead_of_retrying_earlier_ones():
    a, b = counted("a", [F]), counted("b", [R, S])
    fb = m.Fallback("fb", [a, b])
    assert [fb.tick([]), fb.tick([])] == [R, S]
    assert a.calls == 1


def test_sequence_starts_over_after_it_finishes():
    a = counted("a", [S])
    seq = m.Sequence("seq", [a])
    seq.tick([])
    seq.tick([])
    assert a.calls == 2


def test_retry_runs_child_until_success():
    g = counted("grasp", [F, F, S])
    r = m.Retry("retry", 3, g)
    assert [r.tick([]) for _ in range(3)] == [R, R, S]
    assert g.calls == 3


def test_retry_gives_up_after_n_failures():
    g = counted("grasp", [F])
    r = m.Retry("retry", 2, g)
    assert [r.tick([]), r.tick([])] == [R, F]
    assert g.calls == 2


def test_fetch_task_recovers_from_failed_grasps_in_six_ticks():
    tree, leaves = m.fetch_task()
    ticks = m.run(tree)
    assert [s for _, s in ticks] == [R, R, R, R, R, S]
    assert leaves["grasp"].calls == 3 and leaves["go_object"].calls == 3


def test_state_machine_moves_on_known_events_and_ignores_others():
    table = {"idle": {"start": "work"}, "work": {"done": "idle", "fault": "idle"}}
    assert m.fsm_step(table, "idle", "start") == "work"
    assert m.fsm_step(table, "work", "bump") == "work"
