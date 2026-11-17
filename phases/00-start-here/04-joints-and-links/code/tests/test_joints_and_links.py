# 레슨 00/04 테스트: 링크 하나와 두 개의 손 위치가 cos 와 sin 으로 맞게 나오는지 확인한다
import importlib.util
import math
import pathlib

import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_joints", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_link_pointing_straight_across():
    assert m.hand_position(0.4, 0.0) == pytest.approx((0.4, 0.0))


def test_link_pointing_straight_up():
    assert m.hand_position(0.4, math.pi / 2) == pytest.approx((0.0, 0.4), abs=1e-12)


def test_link_at_thirty_degrees():
    across, up = m.hand_position(1.0, math.radians(30))
    assert across == pytest.approx(0.8660254, abs=1e-6)
    assert up == pytest.approx(0.5, abs=1e-9)


def test_hand_stays_one_link_length_from_the_joint():
    for deg in range(0, 360, 20):
        assert math.hypot(*m.hand_position(0.4, math.radians(deg))) == pytest.approx(0.4)


def test_two_straight_links_add_their_lengths():
    assert m.two_link_position(0.4, 0.3, 0.0, 0.0) == pytest.approx((0.7, 0.0))


def test_elbow_bent_a_quarter_turn():
    assert m.two_link_position(0.4, 0.3, 0.0, math.pi / 2) == pytest.approx((0.4, 0.3), abs=1e-12)


def test_elbow_folded_back_subtracts():
    assert m.two_link_position(0.4, 0.3, 0.0, math.pi) == pytest.approx((0.1, 0.0), abs=1e-12)


def test_second_angle_is_measured_from_the_first_link():
    across, up = m.two_link_position(0.4, 0.3, math.pi / 2, -math.pi / 2)
    assert (across, up) == pytest.approx((0.3, 0.4), abs=1e-12)
