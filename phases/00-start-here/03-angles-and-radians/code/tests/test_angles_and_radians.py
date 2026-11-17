# 레슨 00/03 테스트: 도와 라디안 변환, 한 바퀴 안으로 감기, 사분의 일 바퀴
import importlib.util
import math
import pathlib

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_angles", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_a_full_turn_is_360_degrees_or_about_6_28_radians():
    assert abs(m.deg_to_rad(360) - 2 * math.pi) < 1e-12
    assert round(m.deg_to_rad(360), 2) == 6.28


def test_a_quarter_turn_is_about_1_57_radians():
    assert round(m.deg_to_rad(90), 2) == 1.57
    assert abs(m.deg_to_rad(90) - m.QUARTER_TURN) < 1e-12


def test_a_half_turn_is_pi():
    assert abs(m.deg_to_rad(180) - math.pi) < 1e-12


def test_round_trip_gives_back_the_same_angle():
    for degrees in (-270, -45, 0, 30, 90, 359, 720):
        assert abs(m.rad_to_deg(m.deg_to_rad(degrees)) - degrees) < 1e-9


def test_wrap_brings_big_angles_back_into_one_turn():
    assert abs(m.rad_to_deg(m.wrap_turn(m.deg_to_rad(370))) - 10) < 1e-9
    assert abs(m.rad_to_deg(m.wrap_turn(m.deg_to_rad(-90))) - 270) < 1e-9


def test_wrap_leaves_angles_inside_one_turn_alone():
    assert m.wrap_turn(1.0) == 1.0
    assert m.wrap_turn(0.0) == 0.0


def test_wrapped_angle_always_lies_in_zero_to_one_turn():
    for k in range(-40, 40):
        a = m.wrap_turn(k * 0.9)
        assert 0.0 <= a < 2 * math.pi


def test_wrapping_does_not_change_the_direction():
    a = m.deg_to_rad(450)
    assert abs(math.cos(m.wrap_turn(a)) - math.cos(a)) < 1e-9
    assert abs(math.sin(m.wrap_turn(a)) - math.sin(a)) < 1e-9


def test_conversions_agree_with_the_standard_library():
    for degrees in (-90, 30, 180, 450):
        assert abs(m.deg_to_rad(degrees) - math.radians(degrees)) < 1e-12
        assert abs(m.rad_to_deg(math.radians(degrees)) - degrees) < 1e-9


def test_degrees_fed_to_cos_by_mistake_give_the_wrong_answer():
    assert abs(math.cos(m.deg_to_rad(90))) < 1e-12
    assert abs(math.cos(90)) > 0.4
