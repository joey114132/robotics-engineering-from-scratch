# 레슨 00/03 테스트: URDF 파싱, kinematic tree, joint origin 의 프레임 해석과 limit 검사
import importlib.util
import pathlib

import numpy as np
import pytest

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_urdf", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

links, joints = m.parse_urdf(m.URDF)


def test_parse_finds_links_and_joints_in_file_order():
    assert links == ["base", "upper", "fore", "hand", "camera"]
    assert list(joints) == ["shoulder", "elbow", "wrist", "cam_mount"]


def test_root_and_branching_tree():
    assert m.find_root(links, joints) == "base"
    kids = m.children(joints)
    assert sorted(kids["upper"]) == ["camera", "fore"]


def test_chain_prints_from_root_to_tip():
    chain = m.chain(joints, "base", "hand")
    assert [j["name"] for j in chain] == ["shoulder", "elbow", "wrist"]
    assert m.describe(chain) == "base -[shoulder]-> upper -[elbow]-> fore -[wrist]-> hand"


def test_limits_are_parsed_and_enforced():
    assert joints["shoulder"]["limit"] == (-3.0, 3.0)
    assert joints["wrist"]["limit"] is None
    with pytest.raises(ValueError, match="elbow"):
        m.check_limit(joints["elbow"], 2.0)
    m.check_limit(joints["elbow"], 0.5)


def test_origin_is_in_the_parent_frame_not_the_world():
    pos = m.link_positions(m.chain(joints, "base", "hand"), {"shoulder": 0.0, "elbow": 0.0})
    assert np.allclose(pos["hand"], [0.0, 0.5, 0.1], atol=1e-6)


def test_naive_sum_of_origins_is_the_wrong_answer():
    ch = m.chain(joints, "base", "hand")
    naive = m.naive_position(ch)
    true = m.link_positions(ch, {"shoulder": 0.0, "elbow": 0.0})["hand"]
    assert np.allclose(naive, [0.5, 0.0, 0.1])
    assert np.linalg.norm(naive - true) > 0.5


def test_joint_angle_rotates_everything_after_the_joint():
    pos = m.link_positions(m.chain(joints, "base", "hand"), {"shoulder": np.pi / 2, "elbow": 0.0})
    assert np.allclose(pos["hand"], [-0.5, 0.0, 0.1], atol=1e-6)


def test_unknown_tip_and_missing_axis_raise():
    with pytest.raises(ValueError):
        m.chain(joints, "base", "nowhere")
    with pytest.raises(ValueError, match="axis"):
        m.parse_urdf('<robot name="r"><link name="a"/><link name="b"/><joint name="j" type="revolute">'
                     '<parent link="a"/><child link="b"/><limit lower="0" upper="1" effort="1" velocity="1"/></joint></robot>')
