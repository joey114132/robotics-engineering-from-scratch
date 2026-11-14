# 레슨 02/01 예시 클립: 어깨만 돌리면 두 팔의 손이 같은 자리에 있고, 팔꿈치를 굽히는 순간 파란 손만 공에서 벗어난다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, HOLD, SHOULDER, PAUSE, ELBOW = 6.0, 0.6, 1.3, 0.7, 1.6      # still, shoulder turn, pause, elbow bend, hold
Q_END, L1, L2 = np.array([0.5, 0.8]), 0.4, 0.3
rows, tool = m.planar_craig(L1, L2)


def ease(t, t0, dur):
    s = np.clip((t - t0) / dur, 0, 1)
    return s * s * (3 - 2 * s)


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
    arms[conv] = (js, x, kit.ball(conv + "-goal", 0.04, colour="amber"))
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps
    q = np.array([Q_END[0] * ease(t, HOLD, SHOULDER), Q_END[1] * ease(t, HOLD + SHOULDER + PAUSE, ELBOW)])   # the angles are the lesson's (0.5, 0.8) rad
    right = m.fk_dh(rows, q, "craig", tool=tool)[:2, 3]
    d = np.array([np.cos(q.sum()), np.sin(q.sum())])
    for conv, (js, x, ball) in arms.items():
        kit.pose(js, f, joints_of(conv, q))
        kit.key(ball, f, loc=(x + right[0] + 0.085 * d[0], 0, 0.7 + right[1] + 0.085 * d[1]))   # the amber ball rides on the right answer
kit.camera((-0.15, -3.3, 2.2), (-0.15, 0, 0.95), lens=50)
kit.render(__file__)
