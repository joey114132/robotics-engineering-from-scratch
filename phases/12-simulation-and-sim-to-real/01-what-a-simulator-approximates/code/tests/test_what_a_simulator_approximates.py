# 레슨 12/01 테스트: 마찰·모터 지연·센서 지연이 빠진 시뮬이 같은 명령에서 얼마나 어긋나는지
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_sim_approx", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_same_plant_same_commands_gives_zero_divergence():
    a = m.measured(m.REAL, m.command, 3.0)
    b = m.measured(m.REAL, m.command, 3.0)
    assert np.max(np.abs(a - b)) == 0.0


def test_joint_at_rest_below_the_pivot_stays_at_rest():
    traj = m.simulate(m.REAL, lambda t: 0.0, 1.0)
    assert np.allclose(traj, 0.0, atol=1e-12)


def test_frictionless_joint_conserves_energy_so_the_integrator_is_not_the_error():
    p = {**m.REAL, "b": 0.0, "c": 0.0, "Tm": 0.0}
    traj = m.simulate(p, lambda t: 0.0, 4.0, x0=(1.0, 0.0, 0.0))
    e = m.energy(traj, p)
    assert abs(e[-1] - e[0]) / e[0] < 1e-6


def test_friction_makes_a_swinging_joint_lose_energy():
    traj = m.simulate(m.REAL, lambda t: 0.0, 4.0, x0=(1.0, 0.0, 0.0))
    e = m.energy(traj, m.REAL)
    assert e[-1] < 0.5 * e[0]


def test_sensor_delay_is_an_exact_shift_of_the_true_angle():
    p = {**m.REAL, "delay": 0.02}
    q_true = m.simulate(p, m.command, 2.0)[:, 0]
    q_meas = m.measured(p, m.command, 2.0)
    n = round(0.02 / m.DT)
    assert np.array_equal(q_meas[n:], q_true[:-n])
    assert np.all(q_meas[:n] == q_true[0])


def test_each_missing_effect_changes_the_trajectory():
    costs = m.effect_costs(m.REAL, m.command, 6.0)
    assert all(costs[k] > 1e-4 for k in ("friction", "motor lag", "sensor delay"))


def test_missing_everything_diverges_more_late_than_early():
    sim = {**m.REAL, "b": 0.0, "c": 0.0, "Tm": 0.0, "delay": 0.0}
    d = np.abs(m.measured(m.REAL, m.command, 6.0) - m.measured(sim, m.command, 6.0))
    third = len(d) // 3
    assert d[-third:].mean() > 2 * d[:third].mean()


def test_missing_friction_costs_the_most_for_these_parameters():
    costs = m.effect_costs(m.REAL, m.command, 6.0)
    single = {k: v for k, v in costs.items() if k != "all three"}
    assert max(single, key=single.get) == "friction"
    assert costs["all three"] >= max(single.values()) * 0.8
