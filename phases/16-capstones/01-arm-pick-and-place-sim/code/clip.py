# 레슨 16/01 클립: 같은 pick-and-place를 두 팔이 한다. 파란 팔은 중력 feedforward 없음, 초록 팔은 있음. 처짐은 6배로 그린다
import pathlib
import sys

import bpy
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
A, B, MAG, BH, GRIP = (0.50, 0.10), (0.15, 0.50), 6.0, 0.45, 0.08     # the lesson's A and B; sag drawn 6x; shoulder height; ball ahead of the wrist
runs = {ff: m.run(A, B, ff) for ff in (1.0, 0.0)}
drawn = {ff: r["q_ref"] + MAG * (r["q"] - r["q_ref"]) for ff, r in runs.items()}   # the plan plus 6x the lesson's tracking error
KP = 1999                                                              # the pick instant, t = 2 s


def ball_at(q, o=(GRIP, 0.0)):                                         # x-z position of a point o in the hand frame, relative to the shoulder
    s = q.sum()
    return m.fk(q) + o[0] * np.array([np.cos(s), np.sin(s)]) + o[1] * np.array([-np.sin(s), np.cos(s)])


sc = kit.setup(5.5)
cradle, goal = ball_at(drawn[1.0][KP]), ball_at(m.ik(B))             # where the ball waits, and where it should end
ghost = kit.ghost("amber", 0.4)
for ff, bx, col in ((0.0, -0.6, "blue"), (1.0, 0.6, "green")):
    root, joints = kit.arm(col + "-arm", (0.4, 0.4), col, base_height=BH)
    bpy.data.objects[col + "-arm-link1"].data.materials[0] = kit.mat(col)    # the forearm in the arm's own colour
    root.location = (bx, 0, 0)
    kit.cyl("tee", 0.022, BH + cradle[1] - 0.035, (bx + cradle[0], 0, (BH + cradle[1] - 0.035) / 2), "z", "grey")
    kit.ball("target", 0.045, (bx + goal[0], 0, BH + goal[1]), ghost)
    ball = kit.ball("payload", 0.035, (0, 0, 0), "amber")
    hand_q = drawn[ff][KP]
    d = cradle - m.fk(hand_q)
    s0 = hand_q.sum()
    off = np.array([d @ [np.cos(s0), np.sin(s0)], d @ [-np.sin(s0), np.cos(s0)]])   # where the ball sits in this arm's hand at the pick
    for f in range(sc.frame_start, sc.frame_end + 1):
        i = min(int((f - 1) / sc.render.fps / m.DT), len(drawn[ff]) - 1)
        kit.pose(joints, f, drawn[ff][i])
        u = min(max((i * m.DT - 2.0) / 0.6, 0.0), 1.0)
        o = np.array([GRIP, 0.0]) + (off - [GRIP, 0.0]) * (1 - u * u * (3 - 2 * u))   # the grip closes the ball into the fingers during the lift
        p = cradle if i < KP else ball_at(drawn[ff][i], o)
        kit.key(ball, f, loc=(bx + p[0], 0, BH + p[1]))
kit.camera((0.2, -3.6, 1.9), (0.2, 0, 0.6), lens=55)
kit.render(__file__)
