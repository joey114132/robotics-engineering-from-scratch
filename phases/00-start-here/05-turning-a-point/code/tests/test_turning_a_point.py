# 레슨 00/05 테스트: 점을 돌리는 식과 2x2 표(회전 행렬)가 같은 답을 주는지 확인한다
import importlib.util
import math
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_turning", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_quarter_turn_takes_across_to_up():
    assert m.rotate((1.0, 0.0), math.pi / 2) == pytest.approx((0.0, 1.0), abs=1e-12)


def test_quarter_turn_takes_up_to_minus_across():
    assert m.rotate((0.0, 1.0), math.pi / 2) == pytest.approx((-1.0, 0.0), abs=1e-12)


def test_no_turn_changes_nothing():
    assert m.rotate((0.7, -0.2), 0.0) == pytest.approx((0.7, -0.2))


def test_distance_from_the_origin_never_changes():
    for deg in range(0, 360, 15):
        assert math.hypot(*m.rotate((0.3, 0.4), math.radians(deg))) == pytest.approx(0.5)


def test_two_turns_equal_one_bigger_turn():
    a, b = math.radians(20), math.radians(55)
    assert m.rotate(m.rotate((1.0, 0.5), a), b) == pytest.approx(m.rotate((1.0, 0.5), a + b))


def test_table_for_a_quarter_turn():
    assert m.rotation_table(math.pi / 2) == pytest.approx(np.array([[0.0, -1.0], [1.0, 0.0]]), abs=1e-12)


def test_table_gives_the_same_answer_as_plain_math():
    for deg in (10, 90, 135, 250):
        a = math.radians(deg)
        assert m.rotate_with_table((0.9, -0.4), a) == pytest.approx(m.rotate((0.9, -0.4), a))
