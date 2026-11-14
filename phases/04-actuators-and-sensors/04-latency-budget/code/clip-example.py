# 레슨 04/04 예시 클립: 지연은 5.5 ms 로 같고 kd 만 다른 PD 팔 두 대. kd=2 인 초록 팔은 가라앉고 kd=30 인 파란 팔은 margin 이 모자라 진동이 폭주한다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
J, KP, DELAY, DT, SECONDS, SLOW, SCALE, CAP = 0.05, 100.0, 5.5e-3, 1e-4, 0.1, 48.0, 2.0, 0.8   # the lesson's 5.5 ms budget; the first 0.1 s at 1/48 speed; angle drawn 2 times larger, softly capped at 0.8 rad
runs = {kd: m.simulate(KP, kd, J, DELAY, T=SECONDS, dt=DT) for kd in (2.0, 30.0)}

sc = kit.setup(SECONDS * SLOW)
kit.table((1.9, 0.7), 0.4)
rigs = []
for kd, x, colour in ((2.0, -0.55, "green"), (30.0, 0.4, "blue")):
    root, joints = kit.arm(f"kd{kd}", (0.4,), colour, base_height=0.5)
    root.location = (x, 0, 0.4)
    kit.ball("target", 0.03, (x + 0.55, 0, 0.9), "amber")             # where the hand should settle
    rigs.append((runs[kd], joints))
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / DT), len(runs[2.0]) - 1)
    for q, joints in rigs:
        kit.pose(joints, f, [float(CAP * np.tanh(SCALE * q[i] / CAP))])   # only the drawing is capped, so the hand stays above the table
kit.camera((0.2, -2.8, 1.8), (0.2, 0, 0.9), lens=50)
kit.render(__file__)
