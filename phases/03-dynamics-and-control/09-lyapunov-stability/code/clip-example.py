# 레슨 03/09 예시 클립: kd=-1 인 같은 PD 진자 팔을 정지 상태에서 시작하면 그대로 멈춰 있고 0.1 rad 건드리면 흔들림이 커진다. kd=2 로 건드린 팔은 가라앉는다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import math

import bpy
import numpy as np

import kit

m = kit.lesson_main(__file__)
DT, T, SLOW = 1e-3, 8.0, 1.5                 # 8 s of the lesson's pendulum, played at 1.5x speed
CASES = (("rest", "blue", -1.0, 0.0, -1.6), ("nudged", "blue", -1.0, 0.1, 0.0), ("damped", "green", 2.0, 0.1, 1.6))   # name, colour, kd, start angle, x on the bench
runs = {}
for name, _, kd, q0, _ in CASES:
    p = dict(m.DEFAULT, kd=kd)
    x, out = np.array([q0, 0.0]), []
    for _ in range(int(T / DT)):             # the loop inside m.simulate, keeping the angle
        out.append(x)
        a = m.f(x, p)[1]
        x = np.array([x[0] + DT * (x[1] + DT * a), x[1] + DT * a])
    assert np.allclose([m.V(s, p) for s in out], m.simulate(p, [q0, 0.0], T=T))   # same run as the lesson's own
    runs[name] = [s[0] for s in out]

sc = kit.setup(T / SLOW)
kit.box("bench", (5.2, 1.6, 0.04), (0, 0.5, 0.02), "pearl", bevel=0.01)
for name, c, _, _, x in CASES:
    root, joints = kit.arm(name, (0.35, 0.35), c, base_height=1.1)
    root.location = (x, 0, 0)
    for ob in bpy.data.objects:
        if ob.name.startswith((name + "-post", name + "-foot")):
            ob.hide_render = True                              # the arm hangs from its joint, so the stand is replaced by a wall bracket
    kit.box(name + "-mast", (0.08, 0.08, 1.15), (x, 0.75, 0.575), "grey", bevel=0.01)       # a mast behind the swing plane and a boom that reaches over to the joint
    kit.box(name + "-boom", (0.08, 0.7, 0.08), (x, 0.4, 1.1), "grey", bevel=0.01)
    for f in range(sc.frame_start, sc.frame_end + 1):
        kit.pose(joints, f, [-math.pi / 2 + runs[name][min(int((f - 1) / 24 * SLOW / DT), len(runs[name]) - 1)], 0.0])
kit.camera((0, -4.7, 2.9), (0, 0, 1.05), lens=34)
kit.render(__file__)
