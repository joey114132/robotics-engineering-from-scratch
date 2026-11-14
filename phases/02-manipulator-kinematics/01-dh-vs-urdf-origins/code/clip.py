# 레슨 02/01 클립: 같은 DH 표를 Craig 루틴(초록)과 standard 루틴(파랑)에 넣고 두 팔을 같은 q로 굽힌다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, HOLD, BEND = 5.0, 0.7, 3.0          # still at q = 0, bend for 3 s, hold
Q_END, L1, L2 = np.array([0.5, 0.8]), 0.4, 0.3
rows, tool = m.planar_craig(L1, L2)
tip_end = m.fk_dh(rows, Q_END, "craig", tool=tool)[:2, 3]


def joints_of(convention, q):
    """The two joint angles that draw the elbow and tip the given convention computes (lesson plane x, y drawn as x, z)."""
    mid, tip = m.fk_dh(rows, q, convention)[:2, 3], m.fk_dh(rows, q, convention, tool=tool)[:2, 3]
    a1 = np.arctan2(mid[1], mid[0])
    return a1, np.arctan2(*(tip - mid)[::-1]) - a1


sc = kit.setup(SECONDS)
kit.table((2.5, 0.7), 0.4, (-0.15, 0))
arms = {}
for conv, colour, x in (("standard", "blue", -1.0), ("craig", "green", 0.0)):
    root, js = kit.arm(conv, (L1, L2), colour)
    root.location = (x, 0, 0.4)
    arms[conv] = (js, x)
    d = np.array([np.cos(Q_END.sum()), np.sin(Q_END.sum())])
    ball = tip_end + 0.085 * d                                    # the amber ball sits where the right answer puts the fingers
    kit.ball(conv + "-goal", 0.04, (x + ball[0], 0, 0.7 + ball[1]), "amber")
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps
    s = np.clip((t - HOLD) / BEND, 0, 1)
    s = s * s * (3 - 2 * s)                                       # ease in and out; the angles are the lesson's, q = s * (0.5, 0.8) rad
    for conv, (js, x) in arms.items():
        kit.pose(js, f, joints_of(conv, s * Q_END))
kit.camera((-0.15, -3.0, 1.9), (-0.15, 0, 0.92), lens=50)
kit.render(__file__)
