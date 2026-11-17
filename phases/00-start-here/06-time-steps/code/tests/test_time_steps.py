# 레슨 00/06 테스트: 시간 스텝 반복이 일정한 속도에서는 정확하고, 속도가 변하면 스텝이 작을수록 실제 운동에 가까운지 확인한다
import importlib.util
import pathlib

import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_steps", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_move_adds_speed_times_step_each_time():
    assert m.move(1.0, 2.0, 0.1, 5) == pytest.approx(2.0)


def test_move_with_zero_steps_stays_put():
    assert m.move(3.0, 9.0, 0.1, 0) == 3.0


def test_move_does_not_depend_on_how_the_time_is_cut_up():
    assert m.move(0.0, 2.0, 0.5, 4) == pytest.approx(m.move(0.0, 2.0, 0.05, 40))


def test_exact_fall_after_one_second():
    assert m.exact_distance(9.81, 1.0) == pytest.approx(4.905)


def test_small_steps_stay_close_to_the_exact_fall():
    assert abs(m.positions(9.81, 1.0, 0.01)[-1] - m.exact_distance(9.81, 1.0)) < 0.06


def test_big_steps_drift_further_than_small_steps():
    big = abs(m.positions(9.81, 1.0, 0.5)[-1] - 4.905)
    small = abs(m.positions(9.81, 1.0, 0.1)[-1] - 4.905)
    assert big > 3 * small


def test_halving_the_step_roughly_halves_the_error():
    e1 = abs(m.positions(9.81, 1.0, 0.1)[-1] - 4.905)
    e2 = abs(m.positions(9.81, 1.0, 0.05)[-1] - 4.905)
    assert e1 / e2 == pytest.approx(2.0, rel=0.15)


def test_positions_starts_at_zero_and_has_one_entry_per_step():
    p = m.positions(2.0, 2.0, 0.5)
    assert p[0] == 0.0 and len(p) == 5
