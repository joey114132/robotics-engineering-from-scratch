# 레슨 04/04 클립: 같은 PD 팔 두 대, 지연만 다르다. 초록 팔은 delay margin의 0.6배라 가라앉고, 파란 팔은 1.5배라 진동이 커져 stop에 부딪힌다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
J, KP, KD, DT, SECONDS, SLOW, SCALE, CAP = 0.05, 100.0, 2.0, 1e-4, 0.28, 17.0, 1.6, 0.9   # the first 0.28 s of the response at 1/17 speed; angle drawn 1.6 times larger, softly capped at 0.9 rad
dm = m.delay_margin(KP, KD, J)
runs = {f: m.simulate(KP, KD, J, f * dm, T=SECONDS, dt=DT) for f in (0.6, 1.5)}

sc = kit.setup(SECONDS * SLOW)
kit.table((1.9, 0.7), 0.4)
rigs = []
for f0, x, colour in ((0.6, -0.55, "green"), (1.5, 0.4, "blue")):
    root, joints = kit.arm(f"d{f0}", (0.4,), colour, base_height=0.5)
    root.location = (x, 0, 0.4)
    kit.ball("target", 0.03, (x + 0.55, 0, 0.9), "amber")             # where the hand should settle
    rigs.append((runs[f0], joints))
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / DT), len(runs[0.6]) - 1)
    for q, joints in rigs:
        kit.pose(joints, f, [float(CAP * np.tanh(SCALE * q[i] / CAP))])   # the simulated angle keeps growing; only the drawing is capped, so the hand stays above the table
kit.camera((0.2, -2.8, 1.8), (0.2, 0, 0.9), lens=50)
kit.render(__file__)
