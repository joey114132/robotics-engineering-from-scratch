# 레슨 07/02 테스트: Kalman gain 유도, filter 가 raw 측정보다 낫다, 공분산 P 가 반복 실험의 실제 오차와 맞는다
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_kalman", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

T, RUNS = 60, 4000


@pytest.fixture(scope="module")
def experiment():
    rng = np.random.default_rng(7)
    truth, zs = m.simulate(T, RUNS, rng)
    xs, Ps = m.kalman(zs)
    return truth, zs, xs, Ps


def test_gain_for_one_number_is_prior_variance_over_total_variance():
    K = m.gain(np.array([[4.0]]), np.array([[1.0]]), np.array([[1.0]]))
    assert np.isclose(K[0, 0], 4.0 / (4.0 + 1.0))


def test_gain_minimises_the_joseph_form_posterior_variance():
    F, H, Q, R = m.model()
    P = F @ np.diag([4.0, 1.0]) @ F.T + Q
    K = m.gain(P, H, R)

    def trace(Kx):
        A = np.eye(2) - Kx @ H
        return np.trace(A @ P @ A.T + Kx @ R @ Kx.T)

    for d in ([0.05, 0], [-0.05, 0], [0, 0.05], [0, -0.05]):
        assert trace(K + np.array(d).reshape(2, 1)) > trace(K)


def test_huge_measurement_noise_makes_the_filter_ignore_the_measurement():
    F, H, Q, R = m.model(r=1e6)
    K = m.gain(np.diag([4.0, 1.0]), H, R)
    assert np.all(np.abs(K) < 1e-5)


def test_filter_beats_the_raw_measurement(experiment):
    truth, zs, xs, _ = experiment
    raw = np.sqrt(np.mean((zs[10:] - truth[10:, 0]) ** 2))
    est = np.sqrt(np.mean((xs[10:, 0] - truth[10:, 0]) ** 2))
    assert est < 0.7 * raw


def test_covariance_matches_the_empirical_error_covariance(experiment):
    truth, _, xs, Ps = experiment
    err = xs[T - 1] - truth[T - 1]  # shape (2, runs)
    emp = err @ err.T / RUNS
    assert np.allclose(np.diag(emp), np.diag(Ps[T - 1]), rtol=0.08)
    assert abs(emp[0, 1] - Ps[T - 1][0, 1]) < 0.1 * np.sqrt(Ps[T - 1][0, 0] * Ps[T - 1][1, 1])


def test_two_sigma_band_covers_about_95_percent(experiment):
    truth, _, xs, Ps = experiment
    sig = np.sqrt(Ps[5:, 0, 0])[:, None]
    inside = np.abs(xs[5:, 0] - truth[5:, 0]) < 2 * sig
    assert 0.94 < inside.mean() < 0.965


def test_normalised_error_squared_averages_to_the_state_dimension(experiment):
    truth, _, xs, Ps = experiment
    err = xs[T - 1] - truth[T - 1]
    nees = np.einsum("ir,ij,jr->r", err, np.linalg.inv(Ps[T - 1]), err)
    assert np.isclose(nees.mean(), 2.0, rtol=0.06)


def test_covariance_reaches_a_steady_state_that_does_not_depend_on_the_data():
    _, _, Ps = None, None, m.covariances(300)
    assert np.allclose(Ps[-1], Ps[-2], atol=1e-10)


def test_steady_state_covariance_matches_the_riccati_solution():
    sla = pytest.importorskip("scipy.linalg")
    F, H, Q, R = m.model()
    P_prior = sla.solve_discrete_are(F.T, H.T, Q, R)  # prior covariance (before the update)
    K = m.gain(P_prior, H, R)
    P_post = (np.eye(2) - K @ H) @ P_prior
    assert np.allclose(m.covariances(400)[-1], P_post, atol=1e-8)
