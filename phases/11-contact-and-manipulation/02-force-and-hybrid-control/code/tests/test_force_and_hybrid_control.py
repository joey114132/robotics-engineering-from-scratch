# 레슨 11/02 테스트: 위치 제어는 강성 오차를 힘 오차로 바꾸고 적분 힘 제어는 강성과 무관하게 수렴한다
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_force", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

FD = 10.0


def test_position_control_force_is_ke_times_command_error():
    r = m.probe("position", ke=5000.0)
    expected = 5000.0 * (m.X_EST + FD / m.K_EST - m.XS)
    assert np.isclose(r["f"][-1], expected, rtol=0.01)


def test_position_control_is_right_only_when_model_is_exact():
    ok = m.probe("position", ke=m.K_EST, xs=m.X_EST)["f"][-1]
    stiff = m.probe("position", ke=5 * m.K_EST, xs=m.X_EST)["f"][-1]
    assert np.isclose(ok, FD, rtol=0.01)
    assert np.isclose(stiff, 5 * FD, rtol=0.01)  # 5x stiffer surface, 5x the force


def test_force_control_reaches_fd_for_any_stiffness():
    for ke in (1e3, 5e3, 2.5e4):
        assert np.isclose(m.probe("force", ke=ke)["f"][-1], FD, rtol=0.02), ke


def test_force_control_does_not_slam_on_first_contact():
    for ke in (1e3, 2.5e4):
        assert m.probe("force", ke=ke)["f"].max() < 1.05 * FD


def test_stiffer_surface_settles_faster_under_integral_control():
    def t_settle(ke):
        r = m.probe("force", ke=ke)
        touch = r["t"][np.argmax(r["f"] > 0)]
        return r["t"][np.argmax(np.abs(r["f"] - FD) < 0.05 * FD)] - touch
    assert t_settle(1e3) > 5 * t_settle(2.5e4)


def test_integral_gain_has_a_discrete_stability_limit_ke_ki_dt_below_2():
    ok = m.probe("force", ke=1e4, dt=0.015, T=3.0, vmax=10.0)["f"][-50:]   # ke ki dt = 1.5
    bad = m.probe("force", ke=1e4, dt=0.025, T=3.0, vmax=10.0)["f"][-50:]  # ke ki dt = 2.5
    assert np.allclose(ok, FD, rtol=0.02)
    assert np.abs(bad - FD).max() > 0.2 * FD


def test_hybrid_holds_force_on_a_bumpy_surface_where_position_control_does_not():
    h = m.tool(np.array([0, 1]), ke=5000.0)
    p = m.tool(np.array([0, 0]), ke=5000.0)
    err = lambda r: np.sqrt(np.mean((r["f"][500:] - FD) ** 2))
    assert err(h) < 0.3 * err(p)


def test_selection_matrix_keeps_the_free_axis_position_controlled():
    h = m.tool(np.array([0, 1]), ke=5000.0)
    assert abs(h["x"][-1] - m.VX * m.T_TOOL) < 1.2 * m.VX / m.KP  # ramp lag of the position law
