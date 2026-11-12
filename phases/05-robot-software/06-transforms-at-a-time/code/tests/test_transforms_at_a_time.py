# 레슨 05/06 테스트: 시간표가 붙은 pose buffer 의 보간, 외삽 제한, 늦게 도착한 sample, 스캔 번짐
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_tfbuf", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def yaw_q(a):
    return np.array([np.cos(a / 2), 0, 0, np.sin(a / 2)])


def pose(t, v=0.5, w=1.0):
    """Ground truth: drives along x at v and turns at w."""
    return np.array([v * t, 0.0, 0.0]), yaw_q(w * t)


def filled(step=0.1, n=6, **kw):
    buf = m.PoseBuffer(**kw)
    for i in range(n):
        buf.add(i * step, *pose(i * step))
    return buf


def test_exact_at_a_stored_sample():
    p, q = filled().lookup(0.3)
    assert np.allclose(p, pose(0.3)[0]) and np.allclose(q, pose(0.3)[1])


def test_inserted_arrays_are_snapshots_even_when_the_caller_reuses_them():
    buf = m.PoseBuffer()
    p, q = np.zeros(3), yaw_q(0.0)
    buf.add(0.0, p, q)
    p[:] = [2.0, 0.0, 0.0]
    q[:] = yaw_q(1.0)
    buf.add(1.0, p, q)
    assert np.allclose(buf.lookup(0.0)[0], [0.0, 0.0, 0.0])
    assert np.allclose(buf.lookup(0.0)[1], yaw_q(0.0))
    assert np.allclose(buf.lookup(0.5)[0], [1.0, 0.0, 0.0])
    assert np.allclose(buf.lookup(0.5)[1], yaw_q(0.5))


@pytest.mark.parametrize("samples", [1, 2])
def test_lookup_arrays_cannot_mutate_history_including_constant_rotation(samples):
    buf = m.PoseBuffer()
    for t in range(samples):
        buf.add(float(t), [float(t), 0.0, 0.0], yaw_q(0.0))
    p, q = buf.lookup(0.0)
    p[:] = 42.0
    q[:] = 42.0
    assert np.allclose(buf.lookup(0.0)[0], [0.0, 0.0, 0.0])
    assert np.allclose(buf.lookup(0.0)[1], yaw_q(0.0))


def test_midpoint_is_halfway_in_position_and_in_angle():
    buf = m.PoseBuffer()
    buf.add(0.0, [0, 0, 0], yaw_q(0.0))
    buf.add(1.0, [2, 0, 0], yaw_q(1.0))
    p, q = buf.lookup(0.5)
    assert np.allclose(p, [1, 0, 0]) and np.allclose(q, yaw_q(0.5))


def test_interpolation_takes_the_short_arc_when_a_quaternion_sign_flips():
    buf = m.PoseBuffer()
    buf.add(0.0, [0, 0, 0], yaw_q(0.0))
    buf.add(1.0, [0, 0, 0], -yaw_q(0.2))  # same rotation as yaw_q(0.2)
    assert np.allclose(np.abs(buf.lookup(0.5)[1]), yaw_q(0.1))


def test_query_older_than_the_oldest_sample_raises():
    with pytest.raises(LookupError, match="older"):
        filled().lookup(-0.01)


def test_query_past_the_newest_sample_raises_instead_of_guessing():
    with pytest.raises(LookupError, match="newer"):
        filled().lookup(0.51)


def test_extrapolation_limit_allows_a_short_constant_velocity_guess():
    buf = filled(max_extrapolation=0.1)
    p, q = buf.lookup(0.55)
    assert np.allclose(p, pose(0.55)[0]) and np.allclose(q, pose(0.55)[1])
    with pytest.raises(LookupError):
        buf.lookup(0.61)


def test_samples_that_arrive_late_are_stored_in_time_order():
    buf = m.PoseBuffer()
    for i in (0, 2, 1, 3):
        buf.add(i * 0.1, *pose(i * 0.1))
    assert np.allclose(buf.lookup(0.15)[0], pose(0.15)[0])


def test_old_samples_fall_out_of_the_window():
    buf = m.PoseBuffer(window=0.25)
    for i in range(6):
        buf.add(i * 0.1, *pose(i * 0.1))
    with pytest.raises(LookupError, match="older"):
        buf.lookup(0.1)
    assert np.allclose(buf.lookup(0.4)[0], pose(0.4)[0])


def test_stamped_scan_is_straight_and_latest_pose_scan_is_smeared():
    buf = filled(step=0.1, n=6)  # samples cover 0 to 0.5 s
    wall = np.array([[2.0, y, 0.0] for y in np.linspace(-1, 1, 21)])
    stamps = np.linspace(0.0, 0.5, 21)  # one beam per stamp while the robot turns 0.5 rad
    pts = []
    for t, w in zip(stamps, wall):
        p, q = pose(t)
        pts.append(m.quat_to_R(q).T @ (w - p))  # what the sensor saw at that instant
    good = m.to_world(buf, stamps, pts)
    bad = m.to_world(buf, stamps, pts, use_stamps=False)
    assert np.abs(good - wall).max() < 1e-9
    assert np.abs(bad - wall).max() > 0.3
