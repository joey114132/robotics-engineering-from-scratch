# 레슨 09/03 테스트: 점-원, 선분-원, 간격을 둔 swept 검사와 얇은 장애물 터널링
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_collision", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

C, R = np.array([5.0, 0.0]), 0.3
A, B = np.array([0.0, 0.0]), np.array([10.0, 0.0])


def random_segments(n, seed):
    rng = np.random.default_rng(seed)
    return [(rng.uniform(0, 10, 2), rng.uniform(0, 10, 2)) for _ in range(n)]


def test_point_in_circle_includes_the_boundary_and_excludes_outside():
    assert m.in_circle(np.array([5.3, 0.0]), C, R) and not m.in_circle(np.array([5.31, 0.0]), C, R)


def test_exact_segment_test_catches_a_chord_whose_endpoints_are_both_outside():
    assert not m.in_circle(A, C, R) and not m.in_circle(B, C, R)
    assert m.seg_hits(A, B, C, R)


def test_exact_segment_test_separates_a_graze_from_a_near_miss():
    assert m.seg_hits(A + [0, 0.29], B + [0, 0.29], C, R) and not m.seg_hits(A + [0, 0.31], B + [0, 0.31], C, R)


def test_a_coarse_step_tunnels_through_a_thin_obstacle_that_the_exact_test_sees():
    c = np.array([5.5, 0.0])
    assert m.seg_hits(A, B, c, R / 3) and not m.swept_hits(A, B, c, R / 3, step=1.0)


def test_a_step_up_to_the_obstacle_width_catches_every_dead_centre_crossing():
    xs = np.linspace(1, 9, 400)
    assert all(m.swept_hits(A, B, np.array([x, 0.0]), R, step=2 * R) for x in xs)
    assert not all(m.swept_hits(A, B, np.array([x, 0.0]), R, step=6 * R) for x in xs)


def test_padding_by_half_a_step_never_misses_a_real_collision():
    for step in (0.2, 1.0, 3.0):
        for a, b in random_segments(1500, 1):
            if m.seg_hits(a, b, C, R):
                assert m.conservative_hits(a, b, C, R, step)


def test_unpadded_swept_check_never_raises_a_false_alarm():
    for a, b in random_segments(1500, 2):
        if m.swept_hits(a, b, C, R, 0.5):
            assert m.seg_hits(a, b, C, R)


def test_miss_rate_falls_as_the_step_shrinks():
    hits = [(a, b) for a, b in random_segments(3000, 3) if m.seg_hits(a, b, C, R)]
    rate = lambda s: np.mean([not m.swept_hits(a, b, C, R, s) for a, b in hits])
    assert rate(4 * R) > rate(R) > rate(R / 4) and rate(R / 4) < 0.1


def test_exact_closest_point_agrees_with_a_numerical_minimiser():
    opt = __import__("pytest").importorskip("scipy.optimize")
    for a, b in random_segments(50, 4):
        t = opt.minimize_scalar(lambda t: np.linalg.norm(a + t * (b - a) - C), bounds=(0, 1), method="bounded", options={"xatol": 1e-10}).fun
        assert np.isclose(m.seg_hits(a, b, C, R), t <= R) or abs(t - R) < 1e-6
