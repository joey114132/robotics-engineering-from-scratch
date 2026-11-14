# 레슨 06/04 클립: 손목 카메라가 본 목표를 두 손-눈 보정 결과 X 로 옮겨 팔이 집으러 간다. 파란 팔은 회전축 하나(spread 0), 초록 팔은 spread 60 도
import math
import pathlib
import sys

import numpy as np
from mathutils import Matrix

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
X = m.make_T(m.rodrigues(np.array([0.3, -0.5, 0.8])), [0.05, 0.03, 0.08])      # the true camera-to-gripper transform, as in the lesson
est = {aw: m.solve_hand_eye(*m.make_motions(X, 12, spread, 0.2, 0.001, seed=1))[0] for aw, spread in ((False, 0.0), (True, 60.0))}
SHOULDER, L1, L2, ROLL, Q0 = 0.3, 0.4, 0.5, -0.26, (0.7, -1.6)                  # shoulder above the table, links with 0.1 of hand, wrist roll, picture pose
ry = lambda t: np.array([[math.cos(t), 0, math.sin(t)], [0, 1, 0], [-math.sin(t), 0, math.cos(t)]])
rx = lambda t: np.array([[1, 0, 0], [0, math.cos(t), -math.sin(t)], [0, math.sin(t), math.cos(t)]])
e = lambda a: np.array([math.cos(a), 0, math.sin(a)])
phi = sum(Q0)
tip = np.array([0, 0, SHOULDER]) + L1 * e(Q0[0]) + L2 * e(phi)                  # the gripper pinch point when the picture is taken
RG = ry(-phi) @ rx(ROLL)                                                        # gripper orientation then
p_cam = np.array([0.0, 0.0, 0.3, 1.0])                                          # the cup, 0.3 m in front of the camera

def ik(x, z):
    d = min(math.hypot(x, z), L1 + L2 - 1e-3)
    q1 = -math.acos((d * d - L1 * L1 - L2 * L2) / (2 * L1 * L2))
    return math.atan2(z, x) - math.atan2(L2 * math.sin(q1), L1 + L2 * math.cos(q1)), q1

sc = kit.setup(5)
kit.table((1.2, 1.9), 0.4, (0.45, 0.0))
for aw, colour, y in ((False, "blue", -0.55), (True, "green", 0.55)):
    base = np.array([0.0, y, 0.4])
    cup = base + tip + RG @ (X @ p_cam)[:3]
    goal = base + tip + RG @ (est[aw] @ p_cam)[:3]
    kit.cyl("post", 0.025, cup[2] - 0.4 - 0.035, (cup[0], cup[1], 0.4 + (cup[2] - 0.4 - 0.035) / 2), "z", "grey")
    kit.ball("cup", 0.035, tuple(cup), "amber")
    root, joints = kit.arm("arm-" + colour, colour=colour, base_height=SHOULDER)
    root.location = tuple(base)
    hand = [o for o in root.children_recursive if o.name.startswith("arm-" + colour + "-hand")][0]
    hand.rotation_euler.x = ROLL
    rig = kit.empty("camrig", (0.1, 0, 0), hand)
    rig.matrix_basis = Matrix.Translation((0.1, 0, 0)) @ Matrix(X.tolist())    # the camera sits at X in the gripper frame
    kit.box("cam", (0.08, 0.06, 0.07), (0, 0, 0.02), "dark", bevel=0.01, parent=rig); kit.cyl("lens", 0.026, 0.04, (0, 0, 0.065), "z", "grey", parent=rig)
    kit.tube("sight", [tuple(base + tip + RG @ X[:3, 3]), tuple(cup)], 0.005, "dark")
    d = goal - base - [0, 0, SHOULDER]
    q = ik(math.hypot(d[0], d[1]), d[2])
    for f, pose, yaw in ((1, Q0, 0.0), (22, Q0, 0.0), (86, q, math.atan2(d[1], d[0])), (120, q, math.atan2(d[1], d[0]))):
        kit.pose(joints, f, pose); kit.key(root, f, rot=(0, 0, yaw))
kit.camera((2.5, -0.9, 1.75), (0.45, 0.0, 0.68), lens=44)
kit.render(__file__)
