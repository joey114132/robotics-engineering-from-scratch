# 레슨 00/02 테스트: 점 이동, 원점 바꾸기, 두 점 사이 거리, 경로 길이, 두 점 사이 한 점
import importlib.util
import math
import pathlib

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_points", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_shift_adds_the_move_to_each_number():
    assert m.shift((2, 1), (3, -1)) == (5, 0)


def test_distance_across_and_up_makes_a_3_4_5_triangle():
    assert m.distance((0, 0), (3, 4)) == 5.0


def test_distance_does_not_care_about_order_and_is_zero_for_the_same_point():
    assert m.distance((1, 2), (4, 6)) == m.distance((4, 6), (1, 2))
    assert m.distance((2, 2), (2, 2)) == 0.0


def test_distance_works_for_three_numbers():
    assert m.distance((0, 0, 0), (1, 2, 2)) == 3.0


def test_new_origin_changes_the_numbers_but_not_the_distance():
    a, b, origin = (4, 5), (7, 9), (1, 1)
    assert m.measured_from(a, origin) == (3, 4)
    assert m.distance(m.measured_from(a, origin), m.measured_from(b, origin)) == m.distance(a, b)


def test_path_through_a_corner_is_longer_than_the_straight_line():
    assert m.path_length(m.ROUTE) == 3.5
    assert m.distance(m.ROUTE[0], m.ROUTE[-1]) == 2.5


def test_lerp_gives_the_start_the_middle_and_the_end():
    assert m.lerp((0, 0), (4, 2), 0.0) == (0, 0)
    assert m.lerp((0, 0), (4, 2), 0.5) == (2, 1)
    assert m.lerp((0, 0), (4, 2), 1.0) == (4, 2)


def test_distance_agrees_with_the_standard_library():
    a, b = (1.5, -2.0), (4.0, 3.5)
    assert abs(m.distance(a, b) - math.dist(a, b)) < 1e-12
