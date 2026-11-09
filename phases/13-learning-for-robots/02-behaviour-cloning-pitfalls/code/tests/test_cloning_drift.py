# 레슨 13/02 테스트: 복합 오차(compounding error)와 DAgger 식 복구 시연
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_cloning", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_policy_is_accurate_on_the_demonstrated_states():
    X, A = m.collect(np.random.default_rng(0), 4)
    pi = m.fit_knn(X, A, k=1)
    assert max(np.linalg.norm(pi(x) - m.expert(x)) for x in X[::9]) < 1e-9


def test_noisy_rollout_leaves_the_demonstrated_states():
    rng = np.random.default_rng(1)
    X, A = m.collect(rng, 4)
    err, dist, _ = m.drift_curves(m.fit_knn(X, A), X, rng, n=30)
    assert dist[:30].max() > 3 * m.DT  # the typical learner state is 3+ demo steps from any demo state


def test_action_error_grows_with_the_horizon_for_plain_cloning():
    rng = np.random.default_rng(2)
    X, A = m.collect(rng, 4)
    err, _, _ = m.drift_curves(m.fit_knn(X, A), X, rng, n=40)
    assert err[:3].mean() < 0.5 * err[10:40].mean()


def test_recovery_demonstrations_reduce_late_error():
    rng = np.random.default_rng(3)
    pol_bc, Xb = m.dagger(rng, 4, rounds=0)
    pol_dg, Xd = m.dagger(rng, 4, rounds=4)
    e_bc = m.drift_curves(pol_bc, Xb, np.random.default_rng(9), n=40)[0]
    e_dg = m.drift_curves(pol_dg, Xd, np.random.default_rng(9), n=40)[0]
    assert e_dg[10:].mean() < 0.5 * e_bc[10:].mean()


def test_dagger_labels_come_from_the_expert_not_the_learner():
    rng = np.random.default_rng(4)
    pol, X = m.dagger(rng, 2, rounds=2, labels=True)
    xs, A = X
    assert np.allclose(A, [m.expert(x) for x in xs])


def test_dagger_dataset_grows_each_round():
    rng = np.random.default_rng(5)
    sizes = [len(m.dagger(np.random.default_rng(5), 2, rounds=r)[1]) for r in (0, 1, 2)]
    assert sizes[0] < sizes[1] < sizes[2]


def test_dagger_restores_success_under_noise():
    def rate(rounds):
        return np.mean([m.noisy_success(m.dagger(np.random.default_rng(s), 4, rounds=rounds)[0], np.random.default_rng(50 + s), n=30) for s in range(4)])
    assert rate(4) > rate(0) + 0.15
