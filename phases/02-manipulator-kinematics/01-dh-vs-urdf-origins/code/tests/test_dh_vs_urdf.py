# 레슨 02/01 테스트: 같은 팔의 DH(Craig) 표, DH(standard) 표, URDF origin 이 같은 FK 를 내는지, 규약을 틀리면 조용히 틀리는지
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_dh", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

L1, L2 = 0.4, 0.3
Q = np.array([0.5, 0.8])


def closed_form(q):
    return np.array([L1 * np.cos(q[0]) + L2 * np.cos(q[0] + q[1]), L1 * np.sin(q[0]) + L2 * np.sin(q[0] + q[1])])


def spatial_rows(offsets=True):
    rng = np.random.default_rng(3)
    rows = np.column_stack([rng.uniform(0.1, 0.5, 3), rng.uniform(-np.pi / 2, np.pi / 2, 3), rng.uniform(0.0, 0.3, 3), rng.uniform(-1, 1, 3) * offsets])
    return rows, m.tr(0.2, 0.0, 0.1)


def test_craig_table_matches_closed_form_planar_fk():
    rows, tool = m.planar_craig(L1, L2)
    T = m.fk_dh(rows, Q, "craig", tool=tool)
    assert np.allclose(T[:2, 3], closed_form(Q))


def test_urdf_origins_match_closed_form_planar_fk():
    joints, tool = m.planar_urdf(L1, L2)
    T = m.fk_urdf(joints, Q, tool)
    assert np.allclose(T[:2, 3], closed_form(Q))


def test_craig_and_urdf_agree_on_a_spatial_arm():
    rows, tool = spatial_rows(offsets=False)
    q = np.array([0.3, -0.7, 1.1])
    a = m.fk_dh(rows, q, "craig", tool=tool)
    b = m.fk_urdf(m.craig_to_urdf(rows), q, tool)
    assert np.allclose(a, b, atol=1e-12)


def test_converted_standard_table_agrees_with_craig_table():
    rows, tool = spatial_rows()
    q = np.array([-0.4, 0.9, 0.2])
    std_rows, base = m.craig_to_standard(rows)
    a = m.fk_dh(rows, q, "craig", tool=tool)
    b = m.fk_dh(std_rows, q, "standard", base=base, tool=tool)
    assert np.allclose(a, b, atol=1e-12)


def test_wrong_convention_runs_without_error_and_gives_a_wrong_pose():
    rows, tool = m.planar_craig(L1, L2)
    wrong = m.fk_dh(rows, Q, "standard", tool=tool)  # Craig table fed to the standard routine
    right = m.fk_dh(rows, Q, "craig", tool=tool)
    assert np.linalg.norm(wrong[:3, 3] - right[:3, 3]) > 0.1


def test_wrong_convention_still_passes_the_zero_pose_check():
    rows, tool = m.planar_craig(L1, L2)
    wrong = m.fk_dh(rows, np.zeros(2), "standard", tool=tool)
    right = m.fk_dh(rows, np.zeros(2), "craig", tool=tool)
    assert np.allclose(wrong, right)  # this is why the mistake survives a casual check


def test_urdf_origin_is_a_position_and_an_orientation_not_four_symbols():
    joints = m.craig_to_urdf(np.array([[0.0, np.pi / 2, 0.1, 0.0]]))
    xyz, rpy = joints[0]
    assert np.allclose(xyz, [0.0, -0.1, 0.0], atol=1e-12) and np.allclose(rpy, [np.pi / 2, 0, 0])


def test_urdf_conversion_refuses_a_theta_offset_instead_of_dropping_it():
    import pytest
    rows, _ = spatial_rows()
    with pytest.raises(ValueError):
        m.craig_to_urdf(rows)
