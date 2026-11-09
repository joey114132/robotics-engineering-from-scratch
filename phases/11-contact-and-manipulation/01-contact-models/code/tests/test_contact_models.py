# 레슨 11/01 테스트: 페널티 법선력과 쿨롱 마찰이 tan(theta) 대 mu 로 stick/slip 을 가르는지 확인한다
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_contact", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

MU = 0.5


def test_resting_normal_force_is_m_g_cos_theta():
    th = np.radians(20)
    r = m.simulate(th, MU)
    assert np.isclose(r["fn"][-1], m.M * m.G * np.cos(th), rtol=0.01)


def test_below_critical_angle_the_block_sticks():
    th = np.arctan(0.8 * MU)
    r = m.simulate(th, MU)
    assert abs(r["s"][-1]) < 0.005 and abs(r["v"][-1]) < 1e-3


def test_above_critical_angle_the_block_slides_with_analytic_acceleration():
    th = np.arctan(1.2 * MU)
    r = m.simulate(th, MU, T=2.0)
    i1, i2 = int(0.5 / m.DT), int(1.5 / m.DT)
    a = (r["v"][i2] - r["v"][i1]) / ((i2 - i1) * m.DT)
    assert np.isclose(a, m.slip_accel(th, MU), rtol=0.03)


def test_stick_slip_boundary_matches_tan_theta_equals_mu_on_a_sweep():
    for mu in (0.3, 0.8):
        for ratio in (0.7, 0.9, 1.1, 1.4):
            th = np.arctan(ratio * mu)
            r = m.simulate(th, mu, T=1.5)
            slid = abs(r["v"][-1]) > 0.05
            assert slid == m.slides(th, mu), (mu, ratio)


def test_friction_force_never_leaves_the_cone():
    r = m.simulate(np.radians(35), MU)
    ok = r["fn"] > 1e-6
    assert np.all(np.abs(r["ft"][ok]) <= MU * r["fn"][ok] + 1e-9)


def test_sticking_friction_ratio_equals_tan_theta():
    th = np.radians(15)
    r = m.simulate(th, MU)
    assert np.isclose(abs(r["ft"][-1]) / r["fn"][-1], np.tan(th), rtol=0.02)


def test_critical_angle_helper_and_zero_friction():
    assert np.isclose(m.critical_angle(MU), np.arctan(MU))
    assert m.slides(np.radians(1), 0.0)  # frictionless: any tilt slides
