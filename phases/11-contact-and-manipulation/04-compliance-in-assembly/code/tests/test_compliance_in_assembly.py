# 레슨 11/04 테스트: 두 점 접촉 wedge 해석에서 손목 compliance 가 낮으면 jam, 충분히 부드러우면 삽입된다
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_assembly", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

P = m.P0


def test_wedge_geometry_puts_the_peg_line_through_the_mouth_edge():
    zt = 0.02
    th = m.wedge(zt, P)[0]
    T, u = np.array([-P["h"], zt]), np.array([np.sin(th), -np.cos(th)])
    s = zt / np.cos(th)  # distance along the peg from the tip to height z = 0
    assert np.allclose(T + s * u, [P["h"], 0.0], atol=1e-12)


def test_stiff_wrist_with_lateral_offset_jams():
    assert m.insert(dict(P, kx=1e5))["jam"] is not None


def test_soft_wrist_with_the_same_offset_inserts():
    assert m.insert(dict(P, kx=1e3))["jam"] is None


def test_aligned_stiff_wrist_still_inserts():
    assert m.insert(dict(P, kx=1e5, e=0.0))["jam"] is None


def test_more_friction_never_makes_a_jam_go_away():
    jam = [m.insert(dict(P, kx=1e4, e=2e-3, mu=mu))["jam"] is not None for mu in (0.1, 0.2, 0.3, 0.4, 0.6)]
    assert jam == sorted(jam)  # False ... False True ... True


def test_softer_wrist_never_makes_a_success_into_a_jam():
    jam = [m.insert(dict(P, kx=kx))["jam"] is not None for kx in (1e5, 3e4, 1e4, 3e3, 1e3, 1e2)]
    assert jam == sorted(jam, reverse=True)


def test_frictionless_contact_never_jams():
    for e in (0.0, 1e-3, 3e-3):
        assert m.insert(dict(P, kx=1e5, mu=0.0, e=e))["jam"] is None


def test_sliding_contact_forces_balance_the_wrench_and_stay_positive():
    r = m.insert(dict(P, kx=1e4))
    assert r["jam"] is None and np.all(r["N1"] > 0) and np.all(r["N2"] > 0)
    zt = r["zt"][100]
    _, wr, _, c1, c2, tau = m.wedge(zt, dict(P, kx=1e4))
    q = np.linalg.solve(np.c_[c1, c2, -tau], -wr)[2]
    assert np.allclose(wr + r["N1"][100] * c1 + r["N2"][100] * c2, q * tau)


def test_stiffer_wrist_loads_the_walls_harder_before_it_jams():
    soft = m.insert(dict(P, kx=1e3))["N1"].max()
    stiff = m.insert(dict(P, kx=1e4))["N1"].max()
    assert stiff > 1.5 * soft
