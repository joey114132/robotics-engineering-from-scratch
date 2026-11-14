# 레슨 01/03 예시 클립: 손목을 0.1 rad 돌린 것과 0.1 rad 더하기 한 바퀴 돌린 것은 같은 자세다. 앞의 바늘은 quaternion 의 반각이라 한 바퀴 뒤에는 반대쪽(-q)을 가리킨다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, FPS, SC = 5.0, 24, 1.5                 # the wrist is drawn 1.5 times life size
sc = kit.setup(SECONDS)
kit.camera((0.0, -4.2, 3.7), (0.0, -0.4, 0.55), lens=40)


def ease(s):
    s = min(max(s, 0.0), 1.0)
    return s * s * (3 - 2 * s)


def wrist(name, colour, x):
    """A forearm with a flange and a gripper that points along +x and turns about z; a dial in front shows the quaternion's half angle."""
    root = kit.empty(name, (x, 0, 0))
    kit.cyl(name + "-foot", 0.2, 0.04, (0, 0, 0.02), "z", "dark", bevel=0.01, parent=root)
    kit.cyl(name + "-post", 0.07, 0.35, (0, 0, 0.215), "z", "grey", parent=root)
    kit.cyl(name + "-forearm", 0.1, 0.3, (0, 0, 0.54), "z", colour, bevel=0.015, parent=root)
    hand = kit.empty(name + "-hand", (0, 0, 0.73), root)
    kit.cyl(name + "-flange", 0.13, 0.05, (0, 0, 0), "z", "dark", bevel=0.01, parent=hand)
    kit.box(name + "-palm", (0.07, 0.24, 0.07), (0.05, 0, 0.06), "dark", bevel=0.01, parent=hand)
    for y in (0.08, -0.08):
        kit.box(name + "-finger", (0.28, 0.04, 0.05), (0.19, y, 0.06), "grey", bevel=0.008, parent=hand)
    root.scale = (SC,) * 3
    dial = kit.empty(name + "-dial", (x, -0.95, 0.03))
    kit.cyl(name + "-face", 0.38, 0.02, (0, 0, -0.02), "z", "pearl", bevel=0.005, parent=dial)
    for a in (0.0, math.pi):                                                    # the two ends of the line the needle can point along
        kit.box(name + "-tick", (0.05, 0.02, 0.012), (0.36 * math.cos(a), 0.36 * math.sin(a), -0.005), "dark", bevel=0, parent=dial)
    needle = kit.empty(name + "-needle", (0, 0, 0), dial)
    kit.box(name + "-bar", (0.34, 0.04, 0.02), (0.17, 0, 0.01), "amber", bevel=0.008, parent=needle)
    kit.ball(name + "-head", 0.05, (0.34, 0, 0.01), "amber", parent=needle)
    return hand, needle


def unwrap(vals):
    return np.unwrap(np.array(vals))


s_of = lambda f: ease((f / FPS - 0.5) / 3.2)
turns = {"short": (0.1, wrist("short", "blue", -0.9)), "extra": (0.1 + 2 * math.pi, wrist("extra", "green", 0.9))}    # same pose, quaternions q and -q
frames = range(sc.frame_start, sc.frame_end + 1)
for name, (t_end, (hand, needle)) in turns.items():
    yaw, half = [], []
    for f in frames:
        q = m.quat_from_axis_angle([0, 0, 1], t_end * s_of(f))
        R = m.quat_to_R(q)
        yaw.append(math.atan2(R[1, 0], R[0, 0]))                              # the gripper's heading from the rotation matrix
        half.append(math.atan2(q[3], q[0]))                                   # the angle the quaternion itself carries, t / 2
    for f, y, h in zip(frames, unwrap(yaw), unwrap(half)):
        kit.key(hand, f, rot=(0, 0, y))
        kit.key(needle, f, rot=(0, 0, h))
kit.render(__file__)
