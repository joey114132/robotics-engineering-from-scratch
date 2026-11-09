# 레슨 01/04 테스트: 이름 붙은 frame 트리와 공통 조상을 거치는 transform 조회
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_tf", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def make_tree():
    t = m.TFTree()
    t.add("base", "world", m.make_T(m.rot_z(0.5), [1, 0, 0]))
    t.add("cam", "base", m.make_T(m.rot_y(0.3), [0.2, 0.1, 0.8]))
    t.add("cup", "cam", m.make_T(np.eye(3), [0.2, 0.0, 0.5]))
    t.add("tool", "base", m.make_T(m.rot_x(-0.7), [0.4, 0.0, 0.3]))
    return t


def test_single_edge_is_the_stored_transform():
    t = make_tree()
    assert np.allclose(t.lookup("base", "cam"), m.make_T(m.rot_y(0.3), [0.2, 0.1, 0.8]))


def test_reverse_lookup_is_the_inverse():
    t = make_tree()
    assert np.allclose(t.lookup("cam", "base") @ t.lookup("base", "cam"), np.eye(4), atol=1e-12)


def test_chain_is_the_product_with_inner_names_cancelling():
    t = make_tree()
    assert np.allclose(t.lookup("world", "cup"), t.lookup("world", "base") @ t.lookup("base", "cam") @ t.lookup("cam", "cup"))


def test_siblings_go_through_the_common_ancestor():
    t = make_tree()
    want = m.invert_T(t.lookup("base", "tool")) @ t.lookup("base", "cup")
    assert np.allclose(t.lookup("tool", "cup"), want, atol=1e-12)


def test_lookup_of_a_frame_with_itself_is_identity():
    assert np.allclose(make_tree().lookup("cup", "cup"), np.eye(4))


def test_swapped_product_gives_a_different_valid_pose():
    t = make_tree()
    right = t.lookup("base", "cam") @ t.lookup("cam", "cup")
    wrong = t.lookup("cam", "cup") @ t.lookup("base", "cam")
    assert m.is_rotation(wrong[:3, :3]) and not np.allclose(right[:3, 3], wrong[:3, 3])


def test_unknown_frame_and_disconnected_trees_raise():
    t = make_tree()
    t.add("b", "a", np.eye(4))
    with pytest.raises(KeyError):
        t.lookup("cam", "nowhere")
    with pytest.raises(ValueError):
        t.lookup("cam", "b")


def test_second_parent_and_cycle_are_rejected():
    t = make_tree()
    with pytest.raises(ValueError):
        t.add("cam", "tool", np.eye(4))
    with pytest.raises(ValueError):
        t.add("world", "cup", np.eye(4))


def test_caption_numbers_for_wrong_products():
    cup = m.make_T(np.eye(3), [0.2, 0.0, 0.5])
    err = {}
    for yaw in (0.0, np.pi):
        base_cam = m.make_T(m.rot_z(yaw), [0.5, 0.0, 0.4])
        right = (base_cam @ cup)[:3, 3]
        err[yaw] = (np.linalg.norm((cup @ base_cam)[:3, 3] - right), np.linalg.norm((m.invert_T(base_cam) @ cup)[:3, 3] - right))
    assert np.isclose(err[np.pi][0], 0.4) and np.isclose(err[0.0][1], np.hypot(1.0, 0.8))
