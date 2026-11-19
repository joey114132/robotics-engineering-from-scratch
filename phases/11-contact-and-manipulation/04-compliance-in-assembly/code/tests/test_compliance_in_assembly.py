# 레슨 11/04 테스트: 두 점 접촉 wedge 해석에서 손목 compliance 가 낮으면 jam, 충분히 부드러우면 삽입된다
import importlib.util
import itertools
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


def test_no_contact_ever_pulls_on_the_peg():
    for kx, e, kth in itertools.product((1e5, 1e4, 1e3, 1e2), (0.0, 1e-3, 4e-3), (0.1, 1.0, 10.0)):
        r = m.insert(dict(P, kx=kx, e=e, kth=kth), dz=5e-4)
        assert np.all(r["N1"] >= 0) and np.all(r["N2"] >= 0), (kx, e, kth)


def test_stiff_wrist_does_not_start_with_a_big_side_force():
    # only the tip touches at first, so the peg leans where the wrist wants and the wrist is barely stretched
    assert abs(m.insert(dict(P, kx=1e5))["Fx"][0]) < 1.0


def test_peg_wedges_where_the_hole_allows_less_lean_than_the_wrist_wants():
    for kx in (1e5, 1e4, 1e3):
        p = dict(P, kx=kx)
        r = m.insert(p)
        first_edge_contact = r["zt"][np.argmax(r["N2"] > 0)]
        assert abs(first_edge_contact - 2 * p["h"] / np.tan(m.free_tilt(p))) < 2e-4, kx


def test_wedged_forces_balance_the_wrench_sideways_and_in_twist():
    p = dict(P, kx=1e5)
    r = m.insert(p)
    i = len(r["zt"]) - 1
    _, wr, _, c1, c2 = m.wedge(r["zt"][i], p)
    total = wr + r["N1"][i] * c1 + r["N2"][i] * c2
    assert abs(total[0]) < 1e-9 and abs(total[2]) < 1e-9  # the push is left over: it is what friction must beat
    assert total[1] > 0  # still sliding one step before the jam


def test_friction_at_the_tip_alone_can_hold_the_push():
    p = dict(P, kx=1e5, alpha=np.radians(20), kth=5.0)
    r = m.insert(p)
    assert np.isclose(r["jam"], 2 * p["h"] / np.tan(p["alpha"]), rtol=0, atol=1e-12)  # jammed at the very first depth
    assert len(r["zt"]) == 0


def test_stiffer_wrist_loads_the_walls_harder_before_it_jams():
    soft = m.insert(dict(P, kx=1e3))["N1"].max()
    stiff = m.insert(dict(P, kx=1e4))["N1"].max()
    assert stiff > 1.5 * soft
