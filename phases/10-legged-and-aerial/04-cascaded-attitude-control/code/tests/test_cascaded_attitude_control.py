# 레슨 10/04 테스트: P-P 캐스케이드는 PD 와 같고, 속도 루프의 적분이 돌풍 오프셋을 지운다
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_cascade", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

I, KP, KD, KI = 0.004, 0.9, 0.084, 0.5
K_TH = KP / KD
D = 0.1  # constant gust torque, Nm


def gust(t):
    return D


def run(ctrl, d=gust, t_end=4.0, ref=lambda t: 0.0):
    return m.simulate(ctrl, I, 1e-3, t_end, d, ref)


def test_p_p_cascade_is_exactly_a_pd_loop():
    ref = lambda t: 0.2 if t > 0.5 else 0.0
    a = run(m.pd(KP, KD), d=lambda t: 0.05 * np.sin(5 * t), ref=ref)
    b = run(m.cascade(K_TH, KD, 0.0), d=lambda t: 0.05 * np.sin(5 * t), ref=ref)
    assert np.allclose(a[1], b[1], atol=1e-12) and np.allclose(a[3], b[3], atol=1e-9)


def test_pd_holds_a_constant_gust_with_offset_d_over_kp():
    t, th, w, tau = run(m.pd(KP, KD))
    assert np.isclose(th[-1], D / KP, rtol=0.01)  # the gust pushes the angle positive


def test_cascade_with_rate_integral_removes_the_offset():
    t, th, w, tau = run(m.cascade(K_TH, KD, KI))
    assert abs(th[-1]) < 0.02 * D / KP


def test_cascade_beats_pd_at_the_end_of_a_one_second_gust():
    g = lambda t: D if 0.5 <= t < 1.5 else 0.0
    _, th_pd, _, _ = run(m.pd(KP, KD), d=g, t_end=1.5)
    _, th_c, _, _ = run(m.cascade(K_TH, KD, KI), d=g, t_end=1.5)
    assert abs(th_c[-1]) < 0.3 * abs(th_pd[-1])


def test_closed_loop_poles_are_stable_and_match_the_polynomial():
    poles = m.cascade_poles(I, K_TH, KD, KI)
    assert np.all(poles.real < 0)
    assert np.allclose(np.sort_complex(poles), np.sort_complex(np.roots([I, KD, KD * K_TH + KI, KI * K_TH])))


def test_pd_natural_frequency_is_sqrt_kp_over_i():
    assert np.isclose(np.sqrt(KP / I), 15.0)  # the gains were chosen for wn = 15 rad/s
    assert np.isclose(KD, 2 * 0.7 * 15.0 * I, rtol=1e-9)


def test_both_loops_track_a_step_command_without_a_gust():
    ref = lambda t: 0.2
    for ctrl in (m.pd(KP, KD), m.cascade(K_TH, KD, KI)):
        t, th, w, tau = run(ctrl, d=lambda t: 0.0, ref=ref)
        assert np.isclose(th[-1], 0.2, atol=0.002)


def test_a_weak_rate_gain_with_a_strong_integral_is_unstable_but_the_chosen_gains_are_not():
    assert np.any(m.cascade_poles(I, K_TH, 0.02, 2.0).real > 0)  # k_w < I*k_theta: Routh condition fails
    assert all(np.all(m.cascade_poles(I, K_TH, KD, ki).real < 0) for ki in (0.05, 0.5, 2.0, 8.0))


def test_poles_agree_with_scipy():
    signal = pytest.importorskip("scipy.signal")
    tf = signal.TransferFunction([1.0, 0.0], [I, KD, KD * K_TH + KI, KI * K_TH])  # gust torque to angle
    assert np.allclose(np.sort_complex(tf.poles), np.sort_complex(m.cascade_poles(I, K_TH, KD, KI)))
