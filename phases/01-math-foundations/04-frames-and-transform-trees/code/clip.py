# 레슨 01/04 클립: 카메라가 본 컵을 base frame 으로 옮기는 곱의 순서. 순서를 바꾼 곱은 허공을, 맞는 곱은 컵을 가리킨다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, FPS, S, H, L, REACH = 6.0, 24, 0.6, 0.4, 0.3, 0.09     # 1 lesson unit is drawn as 0.6 m; the table top is z = 0.4
sc = kit.setup(SECONDS)
kit.camera((0.2, -2.2, 1.95), (0.2, 0.0, 0.92), lens=40)

# the lesson's numbers: the camera sits at (0.5, 0, 0.4) in the base frame and is yawed 180 degrees; the cup is at (0.2, 0, 0.5) in the camera frame
T_base_cam = m.make_T(m.rot_z(math.pi), [0.5, 0.0, 0.4])
T_cam_cup = m.make_T(np.eye(3), [0.2, 0.0, 0.5])
tree = m.TFTree()
tree.add("cam", "base", T_base_cam)
tree.add("cup", "cam", T_cam_cup)
right = tree.lookup("base", "cup")[:3, 3] * S                    # T_base_cam @ T_cam_cup
wrong = (T_cam_cup @ T_base_cam)[:3, 3] * S                      # the factors swapped

kit.table((1.1, 0.7), H, (0.2, 0))
cam = kit.empty("camera", (T_base_cam[0, 3] * S, 0, H + T_base_cam[2, 3] * S))
kit.cyl("mast", 0.025, T_base_cam[2, 3] * S, (0, 0, -T_base_cam[2, 3] * S / 2), "z", "grey", parent=cam)
body = kit.empty("camera-body", (0, 0, 0), cam)
body.rotation_euler = (0, 0, math.atan2(T_base_cam[1, 0], T_base_cam[0, 0]))      # the yaw comes from the lesson's matrix
kit.box("cam-body", (0.17, 0.13, 0.1), (0, 0, 0), "dark", bevel=0.01, parent=body)
kit.cyl("cam-lens", 0.042, 0.07, (0.11, 0, 0), "x", "sky", bevel=0.006, parent=body)
kit.cyl("cup-stand", 0.012, right[2] - 0.03, (right[0], 0, H + (right[2] - 0.03) / 2), "z", "grey")
kit.box("cup", (0.06, 0.06, 0.06), (right[0], 0, H + right[2]), "amber", bevel=0.01)
kit.ball("empty-air", 0.032, (wrong[0], 0, H + wrong[2]), "red")        # where the swapped product sends the arm
ray = [(cam.location.x - 0.15, 0, cam.location.z), (right[0], 0, H + right[2])]
kit.tube("view-ray", ray, 0.004, "sky")

root, joints = kit.arm("arm", (L, L), "blue", 0.3)
root.location = (0, 0, H)


def reach(p):
    """Joint angles that put the middle of the gripper on p = (x, z) measured from the base frame, elbow up."""
    phi = 0.0
    for _ in range(40):
        wx, wz = p[0] - REACH * math.cos(phi), p[1] - 0.3 - REACH * math.sin(phi)
        c = min(1.0, max(-1.0, (wx * wx + wz * wz - 2 * L * L) / (2 * L * L)))
        q2 = -math.acos(c)
        q1 = math.atan2(wz, wx) - math.atan2(L * math.sin(q2), L + L * math.cos(q2))
        phi = q1 + q2
    return np.array([q1, q2])


rest, q_wrong, q_right = np.array([math.pi / 2, 0.0]), reach((wrong[0], wrong[2])), reach((right[0], right[2]))


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


for f in range(sc.frame_start, sc.frame_end + 1):
    t = f / FPS
    a, b = ease((t - 0.4) / 1.6), ease((t - 2.9) / 1.6)
    kit.pose(joints, f, rest + (q_wrong - rest) * a + (q_right - q_wrong) * b)
kit.render(__file__)
