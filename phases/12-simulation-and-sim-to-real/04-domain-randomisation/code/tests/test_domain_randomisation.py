# 레슨 12/04 테스트: 고정 controller 를 무작위 plant 에서 평가하고, 범위에 맞춘 튜닝과 너무 넓은 튜닝의 차이를 확인한다
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_domrand", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
SMALL = (np.geomspace(2, 200, 10), np.geomspace(0.1, 4, 10))  # coarse gain grid keeps the tests fast


def test_zero_width_gives_exactly_the_nominal_plant():
    P = m.sample(0.0, 5, np.random.default_rng(0))
    assert all(np.all(P[k] == v) for k, v in m.NOM.items())


def test_samples_stay_inside_the_width_and_centre_on_nominal():
    P = m.sample(0.3, 4000, np.random.default_rng(1))
    for k, v in m.NOM.items():
        assert P[k].min() >= 0.7 * v and P[k].max() <= 1.3 * v
        assert abs(P[k].mean() / v - 1) < 0.02


def test_one_plant_simulated_alone_equals_the_same_plant_inside_a_batch():
    P = m.sample(0.3, 6, np.random.default_rng(2))
    batch = m.simulate(P, np.full(6, 6.0), np.full(6, 1.0))
    alone = m.simulate({k: v[3:4] for k, v in P.items()}, np.array([6.0]), np.array([1.0]))
    assert np.allclose(batch[:, 3], alone[:, 0], atol=1e-12)


def test_score_reads_settle_time_and_overshoot_from_a_known_curve():
    t = np.arange(round(m.T / m.DT)) * m.DT
    clean = np.where(t < 0.5, t / 0.5 * 0.9, 1.0)[:, None]
    ok, settle = m.score(clean)
    assert ok[0] and abs(settle[0] - 0.5) < 0.01  # the curve jumps into the 5% band at t = 0.5 s
    assert not m.score(np.where(t < 0.5, 1.2, 1.0)[:, None])[0][0]


def test_aggressive_gains_fail_on_the_nominal_plant_and_gentle_ones_pass():
    P = m.sample(0.0, 2, np.random.default_rng(0))
    ok_hi, _ = m.score(m.simulate(P, np.full(2, 200.0), np.full(2, 0.1)))
    ok_lo, _ = m.score(m.simulate(P, np.full(2, 5.9), np.full(2, 1.09)))
    assert not ok_hi.any() and ok_lo.all()


def test_gains_tuned_on_the_nominal_plant_lose_success_as_the_plant_spreads():
    kp, kd = m.tune(0.0, 1, 0)
    rates = [m.evaluate(kp, kd, w, 200, 7)[0] for w in (0.0, 0.1, 0.3, 0.6)]
    assert rates[0] == 1.0 and rates[2] < 0.8 and rates[3] <= rates[1]


def test_gains_tuned_across_the_range_beat_nominal_gains_on_that_range():
    nom, rng_ = m.tune(0.0, 1, 0), m.tune(0.3, 30, 1, *SMALL)
    assert m.evaluate(*rng_, 0.3, 200, 7)[0] > m.evaluate(*nom, 0.3, 200, 7)[0] + 0.15


def test_a_range_much_wider_than_the_real_uncertainty_costs_performance():
    right, wide = m.tune(0.3, 30, 1, *SMALL), m.tune(0.6, 30, 1, *SMALL)
    assert m.evaluate(*wide, 0.3, 300, 7)[1] > 1.05 * m.evaluate(*right, 0.3, 300, 7)[1]
