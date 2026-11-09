# 레슨 08/02 테스트: resampling, 가중치 수치 안정성, 수렴, kidnapped robot 에서 random particle 주입의 효과
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_pf", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def run(seed, inject=0.0, n=1000, steps=100, kidnap=None, sv=0.4, sw=1.0):
    rng, rz = np.random.default_rng(seed), np.random.default_rng(seed + 100)
    truth = np.array([[2.0, 3.0, 0.3]])
    P = np.column_stack([rng.uniform(0, 10, (n, 2)), rng.uniform(-np.pi, np.pi, n)])
    err = []
    for t in range(steps):
        if t == kidnap:
            truth = np.array([[8.0, 7.0, -2.0]])
        truth = m.move(truth, 0.8, 0.15, 0.1)
        z = m.ranges(truth)[0] + rz.normal(0, 0.3, 4)
        P = m.pf_step(P, 0.8, 0.15, 0.1, z, 0.3, rng, sv=sv, sw=sw, inject=inject)
        err.append(np.linalg.norm(m.estimate(P)[:2] - truth[0, :2]))
    return np.array(err), P


def test_resample_copies_the_only_heavy_particle():
    idx = m.systematic_resample(np.array([0.0, 0.0, 1.0, 0.0]), np.random.default_rng(1))
    assert np.all(idx == 2)


def test_systematic_resample_counts_follow_the_weights():
    w = np.array([0.5, 0.25, 0.125, 0.125])
    idx = m.systematic_resample(w, np.random.default_rng(3))
    c = np.bincount(idx, minlength=4)  # expected 4 * w = [2, 1, 0.5, 0.5]: whole parts are exact
    assert c[0] == 2 and c[1] == 1 and c[2] + c[3] == 1


def test_effective_sample_size_extremes():
    assert np.isclose(m.n_eff(np.full(50, 1 / 50)), 50)
    assert np.isclose(m.n_eff(np.eye(5)[0]), 1)


def test_true_pose_has_the_highest_log_weight():
    truth = np.array([[3.0, 4.0, 0.0]])
    z = m.ranges(truth)[0]
    cand = np.vstack([truth, truth + [0.5, 0, 0], truth + [0, -1.0, 0], [[8.0, 8.0, 0.0]]])
    lw = m.log_weights(cand, z, 0.3)
    assert lw.argmax() == 0 and np.isclose(lw[0], 0.0)


def test_huge_residuals_do_not_produce_nan():
    P = np.column_stack([np.random.default_rng(0).uniform(0, 10, (200, 2)), np.zeros(200)])
    out = m.pf_step(P, 0.5, 0.0, 0.1, np.full(4, 1e4), 0.3, np.random.default_rng(1))
    assert np.isfinite(out).all()


def test_noise_free_move_is_a_straight_line():
    P = m.move(np.array([[1.0, 1.0, 0.0]]), 2.0, 0.0, 0.5)
    assert np.allclose(P, [[2.0, 1.0, 0.0]])


def test_filter_converges_from_a_uniform_start_and_spread_collapses():
    err, P = run(0, steps=40)
    assert err[-1] < 0.3
    assert P[:, :2].std(axis=0).max() < 0.5


def test_kidnapped_filter_stays_lost_unless_random_particles_are_injected():
    plain, _ = run(0, kidnap=40, sv=0.1, sw=0.3)
    inj, _ = run(0, inject=0.05, kidnap=40, sv=0.1, sw=0.3)
    assert plain[39] < 0.3 and plain[40:].min() > 1.4
    assert inj[40:].max() < 1.2
