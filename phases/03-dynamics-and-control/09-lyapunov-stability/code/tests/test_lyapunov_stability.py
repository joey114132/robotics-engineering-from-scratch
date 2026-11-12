# 레슨 03/09 테스트: V 의 양정치성, dV/dt = -(c+kd) rate^2, 표본 검사가 반례를 찾는지, 지연이 V 를 키우는지
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_lyap", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

P = m.DEFAULT
BAD = dict(P, kd=-1.0)  # control damping smaller than minus the natural damping
RNG = np.random.default_rng(3)
XS = RNG.uniform(-1, 1, (200, 2)) * np.array([3.0, 8.0])


def test_V_is_zero_at_the_origin_and_positive_elsewhere():
    assert m.V(np.zeros(2), P) == 0.0
    assert all(m.V(x, P) > 0 for x in XS)


def test_vdot_matches_the_hand_derivation():
    for x in XS:
        assert np.isclose(m.vdot(x, P), -(P["c"] + P["kd"]) * x[1] ** 2, atol=1e-5)


def test_stable_gains_never_raise_V_on_any_sample():
    worst, _ = m.check(P, n=5000)
    assert worst <= 1e-5


def test_negative_damping_has_a_counterexample_the_check_finds():
    worst, x = m.check(BAD, n=5000)
    assert worst > 1.0 and abs(x[1]) > 0.1


def test_one_simulation_from_rest_misses_what_the_sweep_finds():
    v = m.simulate(BAD, [0.0, 0.0], T=5.0)
    assert v.max() == 0.0  # sits at the origin forever, looks perfectly stable
    assert m.check(BAD, n=2000)[0] > 1.0


def test_V_never_rises_along_a_stable_run():
    v = m.simulate(P, [2.0, 3.0], T=8.0)
    assert (np.diff(v) <= 1e-9).all() and v[-1] < 0.01 * v[0]


def test_a_delayed_rate_signal_makes_V_grow():
    p = dict(P, kd=5.0)
    assert m.simulate(p, [1.0, 0.0], T=10.0, delay=0.0).max() <= m.V(np.array([1.0, 0.0]), p) + 1e-9
    assert m.simulate(p, [1.0, 0.0], T=10.0, delay=0.3).max() > 100 * m.V(np.array([1.0, 0.0]), p)
