# 레슨 04/04 테스트: 단계별 지연 합, 지연이 phase margin 을 깎는 양, delay margin 공식과 시뮬레이션 일치, 지연에 따른 kd 상한
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_latency", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

J, KP, KD = 0.05, 100.0, 2.0


def loop_gain(w, delay=0.0):
    s = 1j * w
    return (KP + KD * s) * np.exp(-s * delay) / (J * s**2)


def test_total_latency_sums_stages_and_adds_half_a_hold_period():
    stages = {"sensor": 0.5e-3, "filter": 2e-3, "bus": 1e-3}
    assert np.isclose(m.total_latency(stages, period=1e-3), 3.5e-3 + 0.5e-3)


def test_zero_order_hold_lags_a_ramp_by_half_a_period():
    T, slope = 1e-2, 3.0
    t = np.linspace(0, 1, 100_001)
    held = slope * np.floor(t / T) * T
    assert np.isclose((slope * t - held).mean(), slope * T / 2, rtol=0.01)  # finite grid, so not exact


def test_crossover_is_where_the_loop_gain_is_one():
    wc = m.crossover(KP, KD, J)
    assert np.isclose(abs(loop_gain(wc)), 1.0)


def test_phase_margin_matches_a_numeric_bode_reading_and_delay_subtracts_wc_times_delay():
    wc = m.crossover(KP, KD, J)
    pm_numeric = np.pi + np.angle(loop_gain(wc))
    assert np.isclose(m.phase_margin(KP, KD, J), pm_numeric)
    d = 3e-3
    pm_delayed = np.pi + np.unwrap([np.angle(loop_gain(wc, d))])[0]
    assert np.isclose(m.phase_margin(KP, KD, J, d), pm_delayed)


def test_delay_margin_is_the_delay_that_uses_up_the_phase_margin():
    dm = m.delay_margin(KP, KD, J)
    assert dm > 0 and np.isclose(m.phase_margin(KP, KD, J, dm), 0.0, atol=1e-9)


def test_simulation_is_stable_below_the_delay_margin_and_unstable_above_it():
    dm = m.delay_margin(KP, KD, J)
    assert abs(m.simulate(KP, KD, J, 0.6 * dm)[-1]) < 1e-3
    assert abs(m.simulate(KP, KD, J, 1.5 * dm)[-1]) > 1.0


def test_more_delay_forces_a_lower_kd_limit_and_that_limit_sits_on_the_margin():
    k1, k2 = m.kd_max(2e-3, KP, J), m.kd_max(5e-3, KP, J)
    assert k2 < k1
    assert np.isclose(m.delay_margin(KP, k2, J), 5e-3, rtol=0.01)
