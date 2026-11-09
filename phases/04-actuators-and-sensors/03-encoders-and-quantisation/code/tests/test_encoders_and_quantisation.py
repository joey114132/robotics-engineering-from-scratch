# 레슨 04/03 테스트: encoder 카운트 양자화, 차분 속도의 최소 단계, 저속 노이즈, 필터 창과 지연의 교환
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_encoder", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

CPR, W0 = 4096, 0.1  # slow ramp, rad/s: below one count per millisecond


def ramp(fs, T=10.0, w0=W0, cpr=CPR):
    t = np.arange(int(T * fs) + 1) / fs
    return t, m.counts(w0 * t, cpr)


def test_minimum_velocity_step_is_one_count_per_sample():
    assert np.isclose(m.min_velocity_step(1000, 1e-3), 2 * np.pi)
    assert np.isclose(m.min_velocity_step(4096, 1e-3) / m.min_velocity_step(4096, 1e-2), 10.0)


def test_position_error_is_under_one_count():
    theta = np.linspace(0, 5, 1001)
    err = theta - m.angle_from_counts(m.counts(theta, CPR), CPR)
    assert np.all(err >= 0) and np.all(err < 2 * np.pi / CPR)


def test_difference_velocity_only_takes_multiples_of_the_step():
    _, c = ramp(1000.0)
    v = m.diff_velocity(c, CPR, 1e-3)
    step = m.min_velocity_step(CPR, 1e-3)
    assert np.allclose(v / step, np.round(v / step))
    assert np.isclose(v.max(), step)  # one count per sample is as high as a slow ramp ever reads


def test_slow_ramp_is_unbiased_but_noise_matches_duty_cycle_prediction():
    _, c = ramp(1000.0)
    v = m.diff_velocity(c, CPR, 1e-3)
    step = m.min_velocity_step(CPR, 1e-3)
    d = W0 / step
    assert np.isclose(v.mean(), W0, rtol=0.02)
    assert np.isclose(v.std(), step * np.sqrt(d * (1 - d)), rtol=0.15)


def test_slower_loop_rate_gives_less_noise_on_the_same_slow_ramp():
    _, c_fast = ramp(1000.0)
    _, c_slow = ramp(100.0)
    s_fast = m.diff_velocity(c_fast, CPR, 1e-3).std()
    s_slow = m.diff_velocity(c_slow, CPR, 1e-2).std()
    assert s_slow < s_fast / 3


def test_window_of_n_samples_divides_the_velocity_step_by_n():
    _, c = ramp(1000.0)
    v = m.window_velocity(c, CPR, 1e-3, 8)
    step = m.min_velocity_step(CPR, 1e-3) / 8
    assert np.allclose(v / step, np.round(v / step))


def test_window_estimate_lags_an_accelerating_signal_by_half_the_window():
    fs, a, n = 1000.0, 2.0, 20
    t = np.arange(int(5 * fs) + 1) / fs
    c = m.counts(0.5 * a * t**2, 10_000_000)  # fine encoder: quantisation is negligible
    v = m.window_velocity(c, 10_000_000, 1 / fs, n)
    lag = (a * t[n:] - v) / a
    assert np.isclose(lag.mean(), m.window_lag(n, 1 / fs), rtol=0.02)


def test_longer_window_trades_less_noise_for_more_delay():
    _, c = ramp(1000.0)
    stds = [m.window_velocity(c, CPR, 1e-3, n).std() for n in (1, 5, 20)]
    lags = [m.window_lag(n, 1e-3) for n in (1, 5, 20)]
    assert stds[0] > stds[1] > stds[2] and lags[0] < lags[1] < lags[2]
