# 레슨 08/05 클립: 0.6 rad 틀어지고 0.36 m 어긋나게 놓은 두 번째 스캔을 ICP가 반복마다 첫 번째 스캔 위로 맞춘다
import pathlib
import sys

import bpy
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
ANG, SHIFT, ITERS = 0.6, np.array([0.3, -0.2]), 16
rot = lambda a: np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
ref, cur = m.room(0.05, 0.0), m.room(0.05, 0.5)
moved = (cur - SHIFT) @ rot(ANG)                                  # the lesson's test scene: the second scan placed with an error
spot = np.array([3.0, 1.0])                                       # where the scanning rover really is, in the first scan's frame
spot2 = rot(ANG).T @ (spot - SHIFT)                               # the same spot in the second scan's frame (its own pose is part of the guess)
fit = [(np.eye(2), np.zeros(2))] + [m.icp(moved, ref, iters=k)[:2] for k in range(1, ITERS + 1)]
when = [14 + 5 * k for k in range(ITERS + 1)]                    # hold the bad start, then one ICP iteration every 5 frames

sc = kit.setup(when[-1] / 24 + 1.0)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
kit.stripe(-1.0, 7.0, -3.6, 4.8, "road")
for a, b in zip(m.ROOM[:-1], m.ROOM[1:]):                         # the room's floor outline
    kit.stripe(min(a[0], b[0]) - 0.02, max(a[0], b[0]) + 0.02, min(a[1], b[1]) - 0.02, max(a[1], b[1]) + 0.02, "white", z=0.004)
grey, amber = kit.mat("grey"), kit.mat("amber")
for p in ref[::4]:
    kit.ball("ref", 0.045, (p[0], p[1], 0.05), grey)
pts = [kit.ball("scan", 0.045, (0, 0, 0.05), amber) for _ in moved[::4]]
goal = kit.cyl("goal", 0.19, 0.1, (0, 0, 0.11), "z", kit.ghost("green", 0.45))   # where the rover really is
kit.box("goal-nose", (0.05, 0.12, 0.03), (0.17, 0, 0.13), "amber", parent=goal)
root, wheels = kit.rover("moving", "blue")
for ob in (goal, root):
    ob.scale = (1.6,) * 3
kit.key(goal, 1, loc=(*spot, 0), rot=(0, 0, 0))
for f, (R, t) in zip(when, fit):
    for ob, p in zip(pts, moved[::4] @ R.T + t):
        kit.key(ob, f, loc=(p[0], p[1], 0.05))
    kit.key(root, f, loc=(*(R @ spot2 + t), 0), rot=(0, 0, -ANG + np.arctan2(R[1, 0], R[0, 0])))
kit.camera((3.0, -1.2, 9.8), (3.0, 0.55, 0.0), lens=24)
kit.render(__file__)
