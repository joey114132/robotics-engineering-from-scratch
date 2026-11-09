# 레슨 05/04 테스트: NTP 식 offset 추정, 보정 안 된 시계가 센서 순서를 깨는 과정, trace 에서 첫 불일치 찾기
import importlib.util
import json
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_time", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

A = [0.02 * i for i in range(50)]  # sensor A fires at 0, 20, 40 ms ...
B = [0.02 * i + 0.01 for i in range(50)]  # sensor B fires halfway between


def test_symmetric_delay_recovers_the_offset_exactly():
    off, delay = m.estimate(*m.exchange(0.123, 0.010, 0.010))
    assert np.isclose(off, 0.123) and np.isclose(delay, 0.020)


def test_asymmetric_delay_gives_error_of_half_the_difference_within_half_the_round_trip():
    f, b = 0.030, 0.010
    off, delay = m.estimate(*m.exchange(0.5, f, b))
    assert np.isclose(off - 0.5, (f - b) / 2) and abs(off - 0.5) <= delay / 2


def test_the_lowest_delay_exchange_is_the_one_to_trust():
    samples = [m.exchange(0.2, 0.05, 0.01), m.exchange(0.2, 0.004, 0.004), m.exchange(0.2, 0.02, 0.09)]
    assert np.isclose(m.best_offset(samples), 0.2)


def test_equal_clocks_keep_the_true_order():
    assert m.order_errors(A, B, 0.0) == 0


def test_offset_below_half_the_sensor_gap_keeps_order_and_above_breaks_it():
    assert m.order_errors(A, B, 0.009) == 0
    assert m.order_errors(A, B, 0.011) > 0


def test_correcting_with_the_estimated_offset_restores_the_order():
    off = m.best_offset([m.exchange(0.03, 0.004, 0.004)])
    assert m.order_errors(A, B, 0.03) > 0
    assert m.order_errors(A, B, 0.03, correction=off) == 0


def test_trace_line_is_one_json_object_with_a_pre_and_post_pair():
    rec = json.loads(m.trace_line(3, "move_to", [0.0, 0.0], [0.5, 0.1]))
    assert rec["step"] == 3 and rec["pre"] == [0.0, 0.0] and rec["post"] == [0.5, 0.1]


def _run(posts):
    intents = [{"step": i, "primitive": "move_to", "target": [float(i + 1), 0.0]} for i in range(len(posts))]
    lines = [m.trace_line(i, "move_to", [float(i), 0.0], p) for i, p in enumerate(posts) if p is not None]
    return intents, lines


def test_a_run_that_matches_its_intent_has_no_mismatch():
    assert m.first_mismatch(*_run([[1.0, 0.0], [2.0, 0.0], [3.0, 0.0]])) is None


def test_missing_record_is_reported_as_not_executed():
    assert m.first_mismatch(*_run([[1.0, 0.0], None, [3.0, 0.0]])) == {"step": 1, "kind": "not_executed"}


def test_unchanged_state_is_reported_as_no_motion():
    assert m.first_mismatch(*_run([[1.0, 0.0], [1.0, 0.0]])) == {"step": 1, "kind": "no_motion"}


def test_motion_to_the_wrong_place_is_reported_as_wrong_motion():
    assert m.first_mismatch(*_run([[1.0, 0.0], [2.0, 0.4]])) == {"step": 1, "kind": "wrong_motion"}


def test_only_the_first_mismatch_is_returned():
    assert m.first_mismatch(*_run([[1.0, 0.0], [1.0, 0.0], None]))["step"] == 1


def test_picking_the_lowest_delay_of_eight_beats_a_single_exchange():
    rng = np.random.default_rng(0)
    one, best = [], []
    for _ in range(300):
        s = [m.exchange(0.05, 0.005 + rng.exponential(0.005), 0.005 + rng.exponential(0.005)) for _ in range(8)]
        one.append(abs(m.estimate(*s[0])[0] - 0.05))
        best.append(abs(m.best_offset(s) - 0.05))
    assert np.median(best) < np.median(one)
