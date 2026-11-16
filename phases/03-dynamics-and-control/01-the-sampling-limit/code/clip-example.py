# 레슨 03/01 예시 클립: 같은 kd=30 을 가벼운 팔(r=1.5)과 끝에 무게를 단 팔(r=0.5)에 걸면 가벼운 팔만 매 tick 방향이 뒤집힌다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import math

import kit

m = kit.lesson_main(__file__)
DT, N, TICK, H, KD = 0.001, 7, 12, 1.4, 30.0     # the lesson's dt; N ticks of 12 frames each (0.5 s); 1 rad/s is drawn as 1.4 rad of turn per tick, so the later, smaller reversals still show
A0 = math.pi - 2 * H                              # start angle: the green arm's total turn is 2 H, so it ends level, pointing left
J = {"blue": 0.02, "green": 0.06}                  # r = dt*kd/J = 1.5 and 0.5; the green arm carries a weight that triples J
runs = {c: m.simulate_damper(1.0, j, KD, DT, N) for c, j in J.items()}

sc = kit.setup(N * TICK / 24)
kit.table((3.2, 0.8), 0.4)
arms = {}
for c, x in (("blue", -0.7), ("green", 0.7)):
    root, joints = kit.arm(c, (0.4, 0.4), c)
    root.location = (x, 0, 0.4)
    arms[c] = joints
kit.ball("weight", 0.085, (0.5, 0, 0), kit.mat("amber", kind="plastic"), parent=arms["green"][1])   # the extra mass at the tip: a plain shaded sphere, a physical weight
angle = {c: [H * sum(v[:k]) for k in range(N + 1)] for c, v in runs.items()}
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / TICK
    i, fr = min(int(t), N - 1), t - min(int(t), N - 1)
    for c, joints in arms.items():
        kit.pose(joints, f, [A0 + angle[c][i] * (1 - fr) + angle[c][i + 1] * fr, 0.0])
kit.camera((0, -4.1, 3.1), (0, 0, 0.95), lens=46)
kit.render(__file__)
