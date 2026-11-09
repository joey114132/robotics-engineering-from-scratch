# 레슨 05/01 테스트: QoS 호환 검사와 keep-last 큐의 유실 계산
import importlib.util
import pathlib

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_qos", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

REL, BE = m.Qos("reliable"), m.Qos("best_effort")


def test_reliable_publisher_matches_best_effort_subscriber():
    ok, _ = m.compatible(REL, BE)
    assert ok


def test_best_effort_publisher_does_not_match_reliable_subscriber():
    ok, why = m.compatible(BE, REL)
    assert not ok and "reliability" in why


def test_volatile_publisher_does_not_match_transient_local_subscriber():
    ok, why = m.compatible(m.Qos("reliable", "volatile"), m.Qos("reliable", "transient_local"))
    assert not ok and "durability" in why


def test_every_reliability_pair_matches_the_documented_table():
    table = {("best_effort", "best_effort"): True, ("best_effort", "reliable"): False,
             ("reliable", "best_effort"): True, ("reliable", "reliable"): True}
    for (p, s), want in table.items():
        assert m.compatible(m.Qos(p), m.Qos(s))[0] is want


def test_mismatch_delivers_nothing_but_publishes_everything():
    r = m.run(BE, REL, [1] * 50)
    assert not r["connected"] and r["delivered"] == 0 and r["published"] == 50


def test_nothing_is_created_or_lost_without_accounting():
    r = m.run(REL, m.Qos("best_effort", depth=2), [3, 0, 5, 1] * 10, link_loss=0.3, seed=4)
    assert r["delivered"] + r["dropped"] + r["lost"] == r["published"]


def test_depth_absorbs_a_burst_but_not_a_sustained_overload():
    burst = [8] + [0] * 19
    assert m.run(REL, m.Qos("reliable", depth=1), burst)["dropped"] == 7
    assert m.run(REL, m.Qos("reliable", depth=8), burst)["dropped"] == 0
    overload = [2] * 200
    shallow = m.run(REL, m.Qos("reliable", depth=2), overload)["dropped"]
    deep = m.run(REL, m.Qos("reliable", depth=50), overload)["dropped"]
    assert shallow > 80 and deep > 80


def test_keep_last_drops_the_oldest_message():
    q = m.Queue(2)
    for i in range(4):
        q.push(i)
    assert q.items == [2, 3] and q.dropped == 2


def test_best_effort_link_loses_messages_but_reliable_does_not():
    assert m.run(BE, BE, [1] * 400, link_loss=0.2, seed=1)["lost"] > 0
    assert m.run(REL, REL, [1] * 400, link_loss=0.2, seed=1)["lost"] == 0
