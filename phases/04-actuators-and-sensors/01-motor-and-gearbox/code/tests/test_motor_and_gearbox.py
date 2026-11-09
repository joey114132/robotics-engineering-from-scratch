# 레슨 04/01 테스트: DC 모터 토크-속도 직선, 기어 반사 관성 N^2, 높은 감속비가 부하 변화를 가리는 정도
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_motor", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

M = dict(kt=0.05, R=1.0, V=24.0)  # illustrative motor, not a datasheet
JR, JL = 2e-5, 2e-3


def test_stall_torque_and_no_load_speed():
    assert np.isclose(m.stall_torque(**M), 0.05 * 24.0 / 1.0)
    assert np.isclose(m.no_load_speed(**M), 24.0 / 0.05)


def test_torque_speed_is_a_straight_line_through_both_ends():
    w = np.linspace(0, m.no_load_speed(**M), 5)
    tau = m.motor_torque(w, **M)
    assert np.isclose(tau[0], m.stall_torque(**M)) and np.isclose(tau[-1], 0.0, atol=1e-12)
    assert np.allclose(np.diff(tau), np.diff(tau)[0])


def test_torque_constant_equals_back_emf_constant_as_power():
    w, i = 100.0, 3.0
    assert np.isclose(M["kt"] * i * w, M["kt"] * w * i)  # mechanical power = back-EMF power
    assert np.isclose(m.motor_torque(w, **M), M["kt"] * (M["V"] - M["kt"] * w) / M["R"])


def test_reflected_inertia_grows_with_n_squared_and_conserves_energy():
    assert np.isclose(m.rotor_at_output(JR, 10.0), 100 * JR)
    wm, N = 50.0, 10.0
    assert np.isclose(0.5 * JR * wm**2, 0.5 * m.rotor_at_output(JR, N) * (wm / N) ** 2)
    assert np.isclose(m.load_at_motor(JL, N), JL / 100)


def test_gearbox_trades_speed_for_torque():
    tau_o, w_o = m.gear_output(0.2, 300.0, 20.0)
    assert np.isclose(tau_o, 4.0) and np.isclose(w_o, 15.0)


def test_simulation_reaches_analytic_terminal_speed_with_load_torque():
    N, tau_l = 10.0, 0.5
    t, w = m.spin_up(N, JR, JL, tau_l, T=0.5, dt=1e-5, **M)
    expected = (M["V"] - M["R"] * tau_l / (N * M["kt"])) / M["kt"]
    assert np.isclose(w[-1], expected, rtol=1e-3)


def test_speed_reaches_63_percent_at_one_time_constant():
    N = 1.0
    t, w = m.spin_up(N, JR, 0.0, 0.0, T=0.2, dt=1e-6, **M)
    tau_m = m.time_constant(N, JR, 0.0, **M)
    k = int(round(tau_m / 1e-6))
    assert np.isclose(w[k] / w[-1], 1 - np.exp(-1), atol=2e-3)


def test_high_ratio_hides_the_load_from_the_motor():
    s1, s10, s100 = (m.inertia_sensitivity(JR, JL, n) for n in (1.0, 10.0, 100.0))
    assert s1 > 50 and 1.5 < s10 < 3 and s100 < 1.05
