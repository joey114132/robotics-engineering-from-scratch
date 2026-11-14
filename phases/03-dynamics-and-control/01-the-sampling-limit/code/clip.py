# 레슨 03/01 클립: 같은 관절 damper 를 켠 두 팔. 초록 팔은 r=0.5 로 가라앉고, 파란 팔은 r>2 라 매 tick 부호가 뒤집히며 흔들림이 커진다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import math

import kit

m = kit.lesson_main(__file__)
J, DT, N, TICK, H = 0.02, 0.001, 40, 3, 0.4     # the lesson's J and dt; N control ticks, each drawn 3 frames long; 1 rad/s is drawn as 0.4 rad per tick
KD = {"green": 10.0, "blue": 41.0}                # r = dt*kd/J = 0.5 and 2.05, just past m.max_stable_kd(J, DT) = 40
runs = {c: m.simulate_damper(1.0, J, kd, DT, N) for c, kd in KD.items()}

sc = kit.setup(N * TICK / 24)
kit.table((2.5, 0.8), 0.4)
arms = {}
for c, x in (("green", -0.8), ("blue", 0.8)):
    root, joints = kit.arm(c, (0.4, 0.4), c)
    root.location = (x, 0, 0.4)
    arms[c] = joints
angle = {c: [0.0] for c in KD}                    # shaft angle after each tick = sum of the velocities so far
for c, v in runs.items():
    angle[c] = [H * sum(v[:k]) for k in range(N + 1)]
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / TICK
    i, fr = min(int(t), N - 1), t - min(int(t), N - 1)
    for c, joints in arms.items():
        kit.pose(joints, f, [math.pi / 2 + angle[c][i] * (1 - fr) + angle[c][i + 1] * fr, 0.0])
kit.camera((0, -3.6, 2.8), (0, 0, 0.95), lens=40)
kit.render(__file__)
