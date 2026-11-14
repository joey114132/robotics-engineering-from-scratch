# 레슨 01/04 예시 클립: 같은 컵을 카메라와 base 와 손(tool)에서 재면 화살표 세 개가 된다. T_tool_cup 은 (0, 0, 0.2)라 팔은 손 바로 위의 컵까지 곧게 올라간다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, FPS, S, H, L, REACH = 5.0, 24, 0.8, 0.4, 0.4, 0.09     # 1 lesson unit is drawn as 0.8 m; the table top is z = 0.4
sc = kit.setup(SECONDS)
kit.camera((0.2, -1.95, 1.4), (0.22, 0.0, 0.8), lens=40)

# the lesson's frames: camera at (0.5, 0, 0.4) yawed 180 degrees, cup at (0.2, 0, 0.5) in the camera frame, hand at (0.3, 0, 0.7), all in the base frame
T_base_cam = m.make_T(m.rot_z(math.pi), [0.5, 0.0, 0.4])
T_cam_cup = m.make_T(np.eye(3), [0.2, 0.0, 0.5])
T_base_tool = m.make_T(np.eye(3), [0.3, 0.0, 0.7])
tree = m.TFTree()
tree.add("cam", "base", T_base_cam)
tree.add("cup", "cam", T_cam_cup)
tree.add("tool", "base", T_base_tool)
cam_pos, tool_pos = T_base_cam[:3, 3] * S, T_base_tool[:3, 3] * S
cup_pos = tree.lookup("base", "cup")[:3, 3] * S                  # (0.3, 0, 0.9) seen from the base
cup_in_tool = tree.lookup("tool", "cup")[:3, 3] * S              # (0, 0, 0.2) seen from the hand

kit.table((1.1, 0.7), H, (0.2, 0))
cam = kit.empty("camera", (cam_pos[0], 0, H + cam_pos[2]))
kit.cyl("mast", 0.025, cam_pos[2], (0, 0, -cam_pos[2] / 2), "z", "grey", parent=cam)
body = kit.empty("camera-body", (0, 0, 0), cam)
body.rotation_euler = (0, 0, math.atan2(T_base_cam[1, 0], T_base_cam[0, 0]))
kit.box("cam-body", (0.17, 0.13, 0.1), (0, 0, 0), "dark", bevel=0.01, parent=body)
kit.cyl("cam-lens", 0.042, 0.07, (0.11, 0, 0), "x", "sky", bevel=0.006, parent=body)
kit.cyl("cup-stand", 0.012, cup_pos[2] - 0.03, (cup_pos[0], 0, H + (cup_pos[2] - 0.03) / 2), "z", "grey")
kit.box("cup", (0.06, 0.06, 0.06), (cup_pos[0], 0, H + cup_pos[2]), "amber", bevel=0.01)
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


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def arrow(name, colour, a, b, shaft=0.014):
    """An arrow from world point a to b (both in the x-z plane), drawn a little toward the camera so it does not hide in the arm."""
    ar = kit.arrow(name, colour, shaft=shaft)
    d = np.array(b) - np.array(a)
    ar.rotation_euler = (0, -math.atan2(d[2], d[0]), 0)
    return ar, float(np.hypot(d[0], d[2])), (a[0], -0.12, a[2])


arrows = [arrow("camera-sees-cup", "sky", (cam_pos[0], 0, H + cam_pos[2]), (cup_pos[0], 0, H + cup_pos[2])) + ((0.4, 1.1),),
          arrow("base-sees-cup", "grey", (0, 0, H), (cup_pos[0], 0, H + cup_pos[2])) + ((1.3, 2.0),),
          arrow("tool-sees-cup", "amber", (tool_pos[0], 0, H + tool_pos[2]), (cup_pos[0], 0, H + cup_pos[2]), shaft=0.022) + ((2.2, 2.9),)]
q_tool, q_cup = reach((tool_pos[0], tool_pos[2])), reach((cup_pos[0], cup_pos[2]))
for f in range(sc.frame_start, sc.frame_end + 1):
    t = f / FPS
    kit.pose(joints, f, q_tool + (q_cup - q_tool) * ease((t - 3.2) / 1.1))      # the hand follows the amber arrow, straight up
    for ar, length, loc, (t0, t1) in arrows:
        ar.scale = (max(length * ease((t - t0) / (t1 - t0)), 1e-4), 1, 1)
        ar.location = loc
        ar.keyframe_insert("scale", frame=f)
        ar.keyframe_insert("location", frame=f)
kit.render(__file__)
