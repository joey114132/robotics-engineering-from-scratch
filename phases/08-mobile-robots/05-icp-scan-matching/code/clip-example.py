# 레슨 08/05 예시 클립: 같은 방을 맞추는 두 스캔. 초록은 0.2 rad 틀어져 시작해 방에 붙고 파랑은 2.6 rad 틀어져 시작해 틀린 자리에 갇힌다
import pathlib
import sys

import numpy as np
from bpy_extras import anim_utils

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SHIFT, ITERS, EVERY, DOT = np.array([0.3, -0.2]), 26, 3, 0.09
rot = lambda a: np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
ref, cur = m.room(0.05, 0.0), m.room(0.05, 0.5)
spot = np.array([3.0, 1.0])                                        # where the scanning rover really is, in the first scan's frame
starts = {"far": (2.6, "blue"), "near": (0.2, "green")}            # the lesson's demo loop: start rotation in rad
runs = {}
for k, (ang, _) in starts.items():
    moved = (cur - SHIFT) @ rot(ang)                               # the second scan, placed with an error
    runs[k] = (moved, [(np.eye(2), np.zeros(2))] + [m.icp(moved, ref, iters=i)[:2] for i in range(1, ITERS + 1)], rot(ang).T @ (spot - SHIFT))
when = [18 + EVERY * i for i in range(ITERS + 1)]                  # hold the bad start, then one ICP iteration every 3 frames

sc = kit.setup(when[-1] / 24 + 1.0)
kit.stripe(-6.0, 7.5, -6.5, 5.5, "road")
for a, b in zip(m.ROOM[:-1], m.ROOM[1:]):                          # the room's floor outline
    kit.stripe(min(a[0], b[0]) - 0.03, max(a[0], b[0]) + 0.03, min(a[1], b[1]) - 0.03, max(a[1], b[1]) + 0.03, "white", z=0.004)
for p in ref[::4]:
    kit.ball("ref", DOT, (p[0], p[1], 0.05), "grey")
goal = kit.cyl("goal", 0.19, 0.1, (0, 0, 0.11), "z", kit.ghost("amber", 0.5))   # where the rover really is
kit.box("goal-nose", (0.05, 0.12, 0.03), (0.17, 0, 0.13), "amber", parent=goal)
goal.scale = (1.7,) * 3
goal.location = (*spot, 0)
parts = {}
for k, (ang, colour) in starts.items():
    moved = runs[k][0][::4]
    root, wheels = kit.rover("rover-" + k, colour)
    root.scale = (1.7,) * 3
    pairs = [kit.cyl("pair", 0.012, 1.0, (0, 0, 0), "x", colour, segments=6) for _ in moved[::5]]   # the nearest-point guess of every fifth dot
    parts[k] = ([kit.ball("scan-" + k, DOT, (0, 0, 0.06), colour) for _ in moved], root, pairs)
for k, (dots, root, pairs) in parts.items():
    moved, fit, spot2 = runs[k]
    for it, (f, (R, t)) in enumerate(zip(when, fit)):
        pts = moved[::4] @ R.T + t
        for ob, p in zip(dots, pts):
            kit.key(ob, f, loc=(p[0], p[1], 0.06))
        kit.key(root, f, loc=(*(R @ spot2 + t), 0), rot=(0, 0, -starts[k][0] + np.arctan2(R[1, 0], R[0, 0])))
        for ln, p in zip(pairs, pts[::5]):                         # pair lines for the first three iterations, then they vanish
            q = ref[m.nearest(p[None], ref)[0]]
            v = q - p
            ln.location, ln.rotation_euler = (*(p + v / 2), 0.05), (0, 0, float(np.arctan2(v[1], v[0])))
            ln.scale = (float(np.hypot(*v)) if it < 3 else 0.0, 1, 1)
            for prop in ("location", "rotation_euler", "scale"):
                ln.keyframe_insert(prop, frame=f)
for k, (dots, root, pairs) in parts.items():
    for ob in (*dots, root):                                       # dots and rovers glide from fit to fit
        for fcu in anim_utils.action_get_channelbag_for_slot(ob.animation_data.action, ob.animation_data.action_slot).fcurves:
            for kp in fcu.keyframe_points:
                kp.interpolation = "LINEAR"
    for ob in pairs:                                               # pair lines blink, they do not glide
        for fcu in anim_utils.action_get_channelbag_for_slot(ob.animation_data.action, ob.animation_data.action_slot).fcurves:
            for kp in fcu.keyframe_points:
                kp.interpolation = "CONSTANT"
kit.camera((1.2, -2.3, 15.3), (1.2, -1.2, 0.0), lens=27)
kit.render(__file__)
