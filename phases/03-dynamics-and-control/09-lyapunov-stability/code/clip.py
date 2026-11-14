# 레슨 03/09 클립: 같은 PD 진자 팔 둘. 초록 팔은 속도를 바로 보고 V 가 줄며 멈추고, 파란 팔은 속도를 0.5 s 늦게 봐서 V 가 늘며 위로 넘어간다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import math

import bpy
import numpy as np

import kit

m = kit.lesson_main(__file__)
DT, T, SLOW = 1e-3, 3.0, 3.0 / 5.0           # the first 3 s, up to the swing over the top, played over 5 s
runs = {}
for c, delay in (("green", 0.0), ("blue", 0.5)):
    x, hist, out = np.array([1.0, 0.0]), [0.0] * (int(round(delay / DT)) + 1), []
    for _ in range(int(T / DT)):                             # the loop inside m.simulate, keeping the state: the controller sees the rate from `delay` ago
        out.append(x)
        a = m.f(x, m.DEFAULT, vel_cmd=hist[0])[1]
        x = np.array([x[0] + DT * (x[1] + DT * a), x[1] + DT * a])
        hist = hist[1:] + [x[1]]
    assert np.allclose([m.V(s, m.DEFAULT) for s in out], m.simulate(m.DEFAULT, [1.0, 0.0], T=T, delay=delay))   # same run as the lesson's own
    runs[c] = [s[0] for s in out]

sc = kit.setup(5.0)
for c, x in (("green", -1.0), ("blue", 1.0)):
    root, joints = kit.arm(c, (0.5, 0.5), c, base_height=1.45)
    root.location = (x, 0, 0)
    for ob in bpy.data.objects:
        if ob.name.startswith((c + "-post", c + "-foot")):
            ob.hide_render = True                              # the arm hangs from its joint, so the stand is replaced by a wall bracket
    kit.box(c + "-mast", (0.08, 0.08, 1.5), (x, 0.75, 0.75), "grey", bevel=0.01)       # a mast behind the swing plane and a boom that reaches over to the joint
    kit.box(c + "-boom", (0.08, 0.7, 0.08), (x, 0.4, 1.45), "grey", bevel=0.01)
    kit.box(c + "-base", (0.4, 0.4, 0.04), (x, 0.75, 0.02), "dark", bevel=0.01)
    for f in range(sc.frame_start, sc.frame_end + 1):
        kit.pose(joints, f, [-math.pi / 2 + runs[c][min(int((f - 1) / 24 * SLOW / DT), len(runs[c]) - 1)], 0.0])
kit.camera((0, -5.8, 4.0), (0, 0, 1.55), lens=38)
kit.render(__file__)
