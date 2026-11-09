# 레슨 00/03: 표준 라이브러리 xml.etree 로 URDF 를 읽어 kinematic tree 와 link 위치를 계산한다
import xml.etree.ElementTree as ET

import numpy as np

URDF = """<robot name="arm"><link name="base"/><link name="upper"/><link name="fore"/><link name="hand"/><link name="camera"/>
<joint name="shoulder" type="revolute"><parent link="base"/><child link="upper"/><origin xyz="0 0 0.1" rpy="0 0 1.5707963"/>
<axis xyz="0 0 1"/><limit lower="-3.0" upper="3.0" effort="10" velocity="1"/></joint>
<joint name="elbow" type="revolute"><parent link="upper"/><child link="fore"/><origin xyz="0.3 0 0" rpy="0 0 0"/>
<axis xyz="0 0 1"/><limit lower="-1.0" upper="1.0" effort="10" velocity="1"/></joint>
<joint name="wrist" type="fixed"><parent link="fore"/><child link="hand"/><origin xyz="0.2 0 0"/></joint>
<joint name="cam_mount" type="fixed"><parent link="upper"/><child link="camera"/><origin xyz="0 0 0.05"/></joint></robot>"""

def _vec(e, key):
    return np.array([float(v) for v in (e.get(key) if e is not None and e.get(key) else "0 0 0").split()])

def parse_urdf(xml: str):
    root, joints = ET.fromstring(xml), {}
    for e in root.findall("joint"):
        o, ax, lim = e.find("origin"), e.find("axis"), e.find("limit")
        if e.get("type") == "revolute" and ax is None:
            raise ValueError(f"joint {e.get('name')}: revolute joint without axis")
        joints[e.get("name")] = dict(
            name=e.get("name"), type=e.get("type"), parent=e.find("parent").get("link"), child=e.find("child").get("link"),
            xyz=_vec(o, "xyz"), rpy=_vec(o, "rpy"), axis=_vec(ax, "xyz") if ax is not None else None,
            limit=(float(lim.get("lower")), float(lim.get("upper"))) if lim is not None and lim.get("lower") else None)
    return [e.get("name") for e in root.findall("link")], joints

def children(joints):
    out = {}
    for j in joints.values():
        out.setdefault(j["parent"], []).append(j["child"])
    return out

def find_root(links, joints):
    return next(l for l in links if l not in {j["child"] for j in joints.values()})

def chain(joints, root, tip):
    by_child, path = {j["child"]: j for j in joints.values()}, []
    while tip != root:
        if tip not in by_child:
            raise ValueError(f"link {tip} is not reachable from {root}")
        path.insert(0, by_child[tip])
        tip = by_child[tip]["parent"]
    return path

def describe(ch):
    return ch[0]["parent"] + "".join(f" -[{j['name']}]-> {j['child']}" for j in ch)

def check_limit(j, q):
    if j["limit"] and not j["limit"][0] <= q <= j["limit"][1]:
        raise ValueError(f"joint {j['name']}: {q:.3f} outside {j['limit']}")

def _rot(axis, a):  # Rodrigues rotation about an axis
    k = axis / np.linalg.norm(axis)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * K @ K

def link_positions(ch, q):
    """Link origins in the root frame. Each <origin> is a transform from the PARENT link frame to the child."""
    T, pos = np.eye(4), {ch[0]["parent"]: np.zeros(3)}
    for j in ch:
        r, p, y = j["rpy"]  # URDF rpy: fixed axes, roll about x, then pitch about y, then yaw about z
        To = np.eye(4)
        To[:3, :3] = _rot(np.array([0, 0, 1.0]), y) @ _rot(np.array([0, 1.0, 0]), p) @ _rot(np.array([1.0, 0, 0]), r)
        To[:3, 3] = j["xyz"]
        if j["type"] == "revolute":
            check_limit(j, q[j["name"]])
            To[:3, :3] = To[:3, :3] @ _rot(j["axis"], q[j["name"]])
        T = T @ To
        pos[j["child"]] = T[:3, 3].copy()
    return pos

def naive_position(ch):
    return sum(j["xyz"] for j in ch)  # the bug: reads every origin as if it were in the world frame
