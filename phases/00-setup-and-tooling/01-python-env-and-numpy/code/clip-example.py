# 레슨 00/01 예시 클립: 손끝 (1, 0, 0)을 z축으로 90도 돌린다. .T 를 쓴 팔(초록)은 표지 기둥에 닿고 .T 를 뺀 팔(파랑)은 반대로 돈다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, HOLD, TURN = 5.0, 0.7, 2.8
REACH, H = 0.8, 0.3                                    # the hand point is 0.8 out along x, drawn as 0.8 m
tip = np.array([[REACH, 0.0, 0.0]])


def smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def yaw(points):                                       # the heading of a rotated hand point
    return math.atan2(points[0][1], points[0][0])


sc = kit.setup(SECONDS)
fps = sc.render.fps
arms = {}
for name, x, colour, sign in (("wrong", -0.6, "blue", -1.0), ("right", 0.9, "green", 1.0)):
    root, joints = kit.arm(name, (0.4, 0.4), colour, base_height=H)
    root.location = (x, 0, 0)                                  # one arm behind the other, so the turn sweeps across the screen
    kit.pose(joints, 1, [0.0, 0.0])
    arms[name] = (root, sign)
for x in (-0.6, 0.9):
    kit.cyl("post", 0.03, H, (x, REACH + 0.2, H / 2), "z", "grey")
    kit.ball("goal", 0.07, (x, REACH + 0.2, H), "amber")                           # just beyond the fingertips after +90 degrees about z
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / fps
    theta = math.pi / 2 * smooth((t - HOLD) / TURN)
    for name, (root, sign) in arms.items():
        pts = m.rotate_z(tip, theta) if sign > 0 else m.rotate_z(tip, -theta)       # `points @ R` equals a turn by -theta (Exercise 3)
        kit.key(root, f, loc=root.location[:], rot=(0, 0, yaw(pts)))
kit.camera((-3.2, 0.0, 3.3), (0.35, 0.0, 0.25), lens=38)
kit.render(__file__)
