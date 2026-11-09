# 레슨 12/03 테스트: 기록된 궤적에서 J, b, c, Tm 을 최소제곱으로 맞추고, 느린 궤적 하나로는 b 와 c 를 못 가르는 것을 확인한다
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_sysid", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
rel = lambda est, name: abs(est[name] - m.TRUE[name]) / m.TRUE[name]


def _clean(a):
    return m.record(m.experiment(a), 0.0, 0.0, 0)


def test_lag_step_response_hits_one_minus_exp_minus_one_at_one_time_constant():
    dt, n = 0.002, 15
    tm = m.lag(np.ones(40), dt, n * dt)
    assert np.isclose(tm[n], 1 - np.exp(-1), atol=1e-9)


def test_rich_clean_data_recovers_the_parameters():
    est, _, _ = m.fit(_clean(1.0))
    assert rel(est, "J") < 0.04 and rel(est, "c") < 0.04 and rel(est, "b") < 0.12
    assert abs(est["Tm"] - m.TRUE["Tm"]) < 0.004


def test_fitted_model_predicts_the_speed_change_of_each_window():
    d = m.record(m.experiment(1.0), 0.01, 1e-4, 1)
    y, y_hat = m.predict(m.fit(d)[0], d)
    assert np.corrcoef(y, y_hat)[0, 1] > 0.97 and np.sqrt(np.mean((y - y_hat) ** 2)) < 0.03


def test_one_slow_constant_speed_run_makes_the_regressors_nearly_collinear():
    assert m.fit(_clean(0.0))[1] > 100 * m.fit(_clean(1.0))[1]


def test_one_slow_run_cannot_tell_b_from_c():
    est, _, _ = m.fit(_clean(0.0))
    assert max(rel(est, "b"), rel(est, "c")) > 0.5


def test_swapping_viscous_for_coulomb_friction_hides_on_slow_data_and_shows_on_rich_data():
    w0 = 0.28  # settled speed of the slow run
    alt = {**m.TRUE, "b": 0.0, "c": m.TRUE["c"] + m.TRUE["b"] * w0}
    gap = lambda a: np.sqrt(np.mean((m.record(m.experiment(a, p=alt), 0, 0, 0)[:, 3] - _clean(a)[:, 3]) ** 2))
    assert gap(0.0) < 0.003 and gap(1.0) > 10 * gap(0.0)


def test_more_noise_gives_larger_parameter_error():
    lo, hi = m.excitation_error(1.0, 0.002, 1e-5, 3), m.excitation_error(1.0, 0.05, 1e-3, 3)
    assert sum(hi.values()) > 2 * sum(lo.values())


def test_ignoring_the_motor_lag_leaves_a_larger_residual():
    d = _clean(1.0)
    assert m.fit(d, grid=[0.0])[2] > 3 * m.fit(d)[2]
