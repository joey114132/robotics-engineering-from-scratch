# 레슨 14/03 테스트: 격자 교차로의 교착, wait-for graph 탐지, 경로 예약으로 해소
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_traffic", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

ROUND = [((0, 0), (1, 1)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))]  # four robots chasing each other round a 2x2 block


def random_jobs(seed, n=40, size=4):
    rng = np.random.default_rng(seed)
    jobs = []
    while len(jobs) < n:
        a, b = tuple(int(v) for v in rng.integers(0, size, 2)), tuple(int(v) for v in rng.integers(0, size, 2))
        if a != b:
            jobs.append((a, b))
    return jobs


def test_xy_path_is_manhattan_and_steps_by_one():
    p = m.xy_path((0, 0), (2, 3))
    assert len(p) == 6 and p[0] == (0, 0) and p[-1] == (2, 3)
    assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(p, p[1:]))


def test_find_cycle_reports_a_loop_and_none_for_a_chain():
    assert m.find_cycle({0: 1, 1: 2, 2: 0}) is not None
    assert m.find_cycle({0: 1, 1: 2}) is None


def test_naive_policy_deadlocks_on_the_round_block():
    s = m.Sim(ROUND, K=4, policy="naive")
    for _ in range(30):
        s.step()
    cyc = m.find_cycle(s.wait_for())
    assert s.done == 0 and cyc is not None and len(cyc) == 4


def test_two_robots_facing_each_other_form_a_two_cycle():
    s = m.Sim([((0, 0), (1, 0)), ((1, 0), (0, 0))], K=2, policy="naive")
    s.step()
    assert len(m.find_cycle(s.wait_for())) == 2


def test_reservation_clears_the_same_block():
    s = m.Sim(ROUND, K=4, policy="reserve")
    for _ in range(60):
        s.step()
    assert s.done == 4 and not s.at


def test_reservation_never_has_a_waiting_cycle_and_never_double_books():
    s = m.Sim(random_jobs(1), K=10, policy="reserve")
    for _ in range(300):
        s.step()
        assert not s.wait_for() and len(set(s.occ)) == len(s.occ)
    assert s.done == 40


def test_naive_loses_robots_to_deadlock_on_random_traffic():
    done = [m.run(random_jobs(sd), 10, "naive", 400)[-1] for sd in range(6)]
    assert min(done) < 40 and np.mean(done) < 40
