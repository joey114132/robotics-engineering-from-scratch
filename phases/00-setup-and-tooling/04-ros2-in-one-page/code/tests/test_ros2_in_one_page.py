# 레슨 00/04 테스트: 장난감 pub/sub bus 의 queue depth, drop, 지연 시간
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_bus", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_every_subscriber_of_a_topic_gets_its_own_copy():
    bus = m.Bus()
    a, b = bus.subscribe("/q", depth=5), bus.subscribe("/q", depth=5)
    bus.publish("/q", 1)
    assert bus.take(a) == 1 and bus.take(b) == 1 and bus.take(a) is None


def test_other_topics_are_not_delivered():
    bus = m.Bus()
    s = bus.subscribe("/a", depth=5)
    bus.publish("/b", 1)
    assert bus.take(s) is None


def test_queue_never_holds_more_than_depth_and_drops_the_oldest():
    bus = m.Bus()
    s = bus.subscribe("/q", depth=3)
    for i in range(10):
        bus.publish("/q", i)
    assert len(s.q) == 3 and s.dropped == 7
    assert [bus.take(s) for _ in range(3)] == [7, 8, 9]


def test_fast_subscriber_loses_nothing_even_with_depth_one():
    r = m.run(pub_hz=50, sub_hz=100, depth=1, seconds=2.0)
    assert r["dropped"] == 0 and r["delivered"] == r["published"]


def test_slow_subscriber_drops_the_surplus_whatever_the_depth():
    for depth in (1, 10):
        r = m.run(pub_hz=100, sub_hz=40, depth=depth, seconds=10.0)
        assert r["published"] - r["delivered"] == 600  # 60 msg/s surplus over 10 s
        assert r["dropped"] >= 600 - depth  # all of it dropped except what is still queued


def test_deeper_queue_means_older_data_when_the_subscriber_is_slow():
    age = lambda d: m.run(100, 40, d, 10.0)["ages"][-1]
    assert age(1) < 0.02 and age(50) > 0.4


def test_steady_age_is_about_depth_minus_one_publish_periods():
    r = m.run(pub_hz=100, sub_hz=40, depth=10, seconds=10.0)
    assert abs(r["ages"][-1] - 9 / 100) < 0.015


def test_a_burst_fits_only_if_depth_covers_it():
    assert m.burst_drops(burst=10, depth=10) == 0
    assert m.burst_drops(burst=10, depth=3) == 7
