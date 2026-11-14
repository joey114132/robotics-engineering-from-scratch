# 레슨 03/02 클립: 같은 kp 와 같은 지령의 두 팔. 파란 팔은 중력 모델이 20% 가벼워 처지고, 초록 팔은 모델이 맞아 수평을 지킨다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import math

import kit

m = kit.lesson_main(__file__)
P = dict(m1=2.0, m2=1.0, l1=0.4, lc1=0.2, lc2=0.2)       # the lesson's arm
SECONDS, KP0, KP1, SHOW = 5.0, 400.0, 30.0, 4.0           # kp falls 400 to 30 Nm/rad over 4 s; sag is drawn 4 times larger

sc = kit.setup(SECONDS)
kit.table((2.5, 0.8), 0.4, (0.05, 0))
arms = {}
for c, x, ff in (("blue", -1.0, 0.8), ("green", 0.2, 1.0)):    # ff = how much of the true gravity torque the model feeds forward
    root, joints = kit.arm(c, (0.4, 0.4), c)
    root.location = (x, 0, 0.4)
    kit.ball(c + "-target", 0.035, (x + 0.95, 0, 0.7), kit.ghost("amber", 0.55))   # where the fingertip was commanded
    arms[c] = (joints, ff)
for f in range(sc.frame_start, sc.frame_end + 1):
    kp = KP0 * (KP1 / KP0) ** min((f - 1) / 96, 1.0)
    for joints, ff in arms.values():
        kit.pose(joints, f, SHOW * m.sag([0.0, 0.0], [kp, kp], ff, **P))
kit.camera((0.05, -2.9, 2.0), (0.05, 0, 0.6), lens=40)
kit.render(__file__)
