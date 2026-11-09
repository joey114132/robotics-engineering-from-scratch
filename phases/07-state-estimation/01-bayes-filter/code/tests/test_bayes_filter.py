# 레슨 07/01 테스트: histogram Bayes filter 의 predict/update 대수와 수렴, dead reckoning 의 분산 증가
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_bayes", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def delta(n, i):
    b = np.zeros(n)
    b[i] = 1.0
    return b


def test_predict_conserves_probability_mass():
    rng = np.random.default_rng(0)
    bel = rng.random(20)
    bel /= bel.sum()
    assert np.isclose(m.predict(bel, 2).sum(), 1.0)


def test_predict_turns_a_spike_into_the_motion_kernel():
    out = m.predict(delta(20, 5), 3)
    assert np.allclose(out[[7, 8, 9]], m.KERNEL)
    assert np.isclose(out.sum(), 1.0)


def test_update_on_uniform_prior_scales_doors_by_hit_over_miss():
    doors = np.array([1, 0, 0, 1, 0])
    post = m.update(np.full(5, 0.2), 1, doors)
    assert np.isclose(post[0] / post[1], m.P_HIT / (1 - m.P_HIT))
    assert np.isclose(post.sum(), 1.0)


def test_update_matches_bayes_rule_by_hand():
    # prior 0.5/0.5, cell 0 is a door; reading "door" with p_hit 0.8 -> 0.8*0.5 / (0.8*0.5 + 0.2*0.5) = 0.8
    post = m.update(np.array([0.5, 0.5]), 1, np.array([1, 0]), p_hit=0.8)
    assert np.allclose(post, [0.8, 0.2])


def test_dead_reckoning_variance_grows_by_the_kernel_variance_each_step():
    n, steps = 100, 10
    bel = delta(n, 30)
    for _ in range(steps):
        bel = m.predict(bel, 1)
    cells = np.arange(n)
    mean = (bel * cells).sum()
    var = (bel * (cells - mean) ** 2).sum()
    assert np.isclose(mean, 30 + steps)
    assert np.isclose(var, steps * 0.1)  # kernel variance 0.05 + 0.05


def test_dead_reckoning_entropy_never_decreases():
    bel, h = delta(m.N, 4), []
    for _ in range(40):
        bel = m.predict(bel, 1)
        h.append(m.entropy(bel))
    assert np.all(np.diff(h) >= -1e-12)


def test_filter_sharpens_and_puts_most_mass_near_the_robot():
    mass, steps = [], 30
    for seed in range(30):
        rng = np.random.default_rng(seed)
        truth, zs = m.simulate(m.DOORS, 7, [1] * steps, rng)
        bel = m.run(m.DOORS, zs, [1] * steps)
        assert m.entropy(bel[-1]) < m.entropy(bel[0])
        t = truth[-1]
        mass.append(sum(bel[-1][(t + d) % m.N] for d in (-1, 0, 1)))
    assert np.mean(mass) > 0.8  # a uniform belief would give 3/20 = 0.15
