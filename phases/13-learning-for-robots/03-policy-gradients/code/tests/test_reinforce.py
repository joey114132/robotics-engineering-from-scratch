# 레슨 13/03 테스트: Gaussian 정책의 REINFORCE, 기준선의 분산 감소와 불편성
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_reinforce", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

THETA0 = np.array([0.0, 0.0])


def test_score_function_matches_finite_difference_of_log_probability():
    theta, x, a, sig = np.array([-1.3, 0.2]), 0.7, -0.4, 0.5
    logp = lambda th: -0.5 * ((a - (th[0] * x + th[1])) / sig) ** 2
    eps = 1e-6
    fd = [(logp(theta + eps * e) - logp(theta - eps * e)) / (2 * eps) for e in np.eye(2)]
    assert np.allclose(m.score(theta, x, a, sig), fd, atol=1e-6)


def test_reward_to_go_is_the_reverse_cumulative_sum():
    assert np.allclose(m.reward_to_go(np.array([1.0, 2.0, 3.0])), [6.0, 5.0, 3.0])


def test_deadbeat_gain_beats_the_initial_policy():
    rng = np.random.default_rng(0)
    good = np.mean([m.episode(np.array([-4.5, 0.0]), rng)[2].sum() for _ in range(300)])
    bad = np.mean([m.episode(THETA0, rng)[2].sum() for _ in range(300)])
    assert good > bad + 2.0


def test_training_with_a_baseline_raises_the_return():
    curve = m.train(np.random.default_rng(1), iters=60, batch=32, baseline=True)
    assert curve[-10:].mean() > curve[:5].mean() + 2.0


def test_returns_are_large_next_to_their_spread_which_is_what_the_baseline_removes():
    rng = np.random.default_rng(2)
    G = np.array([m.reward_to_go(m.episode(THETA0, rng)[2])[0] for _ in range(300)])
    assert G.mean() > 4 * G.std()


def test_baseline_training_is_steadier_across_seeds():
    end = lambda base: np.array([m.train(np.random.default_rng(s), iters=30, batch=32, baseline=base)[-5:].mean() for s in range(5)])
    assert end(True).std() < end(False).std()


def test_baseline_gradient_has_lower_variance():
    rng = np.random.default_rng(3)
    raw = np.array([m.grad_estimate(THETA0, rng, 16, False)[0] for _ in range(300)])
    base = np.array([m.grad_estimate(THETA0, rng, 16, True)[0] for _ in range(300)])
    assert base.std(0).mean() < 0.5 * raw.std(0).mean()


def test_baseline_does_not_change_the_expected_gradient():
    rng = np.random.default_rng(4)
    raw = np.array([m.grad_estimate(THETA0, rng, 16, False)[0] for _ in range(600)])
    base = np.array([m.grad_estimate(THETA0, rng, 16, True)[0] for _ in range(600)])
    se = np.hypot(raw.std(0), base.std(0)) / np.sqrt(600)
    assert np.all(np.abs(raw.mean(0) - base.mean(0)) < 4 * se)
