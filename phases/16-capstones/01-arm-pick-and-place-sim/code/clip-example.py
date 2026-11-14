# 레슨 16/01 예시 클립: 표시 위에서 공을 든 채 가만히 선 두 팔. 파란 팔의 feedforward 를 끄면 팔이 처졌다가 멈춘다. 처짐은 6배로 그린다
import pathlib
import sys

import bpy
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
B, MAG, BH, GRIP, SLOW, T_OFF, SECONDS = (0.15, 0.50), 6.0, 0.45, 0.08, 0.25, 0.25, 5.0   # the lesson's B; sag drawn 6x; slow motion 0.25x; switched off at 0.25 s (1 s of clip)
qB = m.ik(B)
DT = m.DT


def hold(ff_off):
    """Hold the pose at B from rest; the blue arm loses its feedforward at T_OFF. Returns the joint angles every step."""
    q, v, out = qB.copy(), np.zeros(2), []
    for k in range(int(SECONDS * SLOW / DT) + 1):
        ff = 0.0 if ff_off and k * DT >= T_OFF else 1.0
        q, v = m.step(q, v, ff * m.gravity(qB) + m.KP * (qB - q) + m.KD * (0 - v))
        out.append(qB + MAG * (q - qB))
    return out


def ball_at(q):                                                        # x-z position of the ball held in the fingers, relative to the shoulder
    s = q.sum()
    return m.fk(q) + GRIP * np.array([np.cos(s), np.sin(s)])


runs = {False: hold(False), True: hold(True)}
sc = kit.setup(SECONDS)
goal = ball_at(qB)
for off, bx, col in ((True, -0.6, "blue"), (False, 0.6, "green")):
    root, joints = kit.arm(col + "-arm", (0.4, 0.4), col, base_height=BH)
    bpy.data.objects[col + "-arm-link1"].data.materials[0] = kit.mat(col)
    root.location = (bx, 0, 0)
    kit.ball("target", 0.05, (bx + goal[0], 0, BH + goal[1]), kit.ghost("amber", 0.4))
    ball = kit.ball("payload", 0.035, (0, 0, 0), "amber")
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = min(int((f - 1) / sc.render.fps * SLOW / DT), len(runs[off]) - 1)
        q = runs[off][k]
        kit.pose(joints, f, q)
        p = ball_at(q)
        kit.key(ball, f, loc=(bx + p[0], 0, BH + p[1]))
kit.camera((0.0, -3.1, 1.5), (0.0, 0, 0.68), lens=50)
kit.render(__file__)
