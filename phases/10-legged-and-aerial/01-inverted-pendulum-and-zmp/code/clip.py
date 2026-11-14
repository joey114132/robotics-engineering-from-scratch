# 레슨 10/01 클립: 같은 밀침을 받은 보행자 둘. 파란 쪽은 발목만 써서 넘어가고 초록 쪽은 capture point 에 한 걸음 내디뎌 선다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
H, HALF, V0, DT, TEND, SLOW, PRE = 0.9, 0.05, 0.4, 1e-3, 1.0, 3.0, 12      # the lesson's push, played 3x slower after 0.5 s of standing
runs = {s: m.fall_or_recover(V0, H, HALF, s, T=TEND, dt=DT) for s in (False, True)}
zmps = {s: m.zmp(r[1], np.gradient(r[2], DT), H) for s, r in runs.items()}   # where the ankle pressure sits on the foot
LAND = float(zmps[True][-1])                                                 # the capture point the second foot lands on

sc = kit.setup(PRE / 24 + TEND * SLOW + 1.2)
walkers = {}
for step, (colour, x0) in {False: ("blue", 0.35), True: ("green", -0.95)}.items():
    pel = kit.box("pelvis", (0.16, 0.3, 0.14), (0, 0, 0), colour, bevel=0.04)
    kit.box("torso", (0.14, 0.26, 0.3), (0, 0, 0.22), colour, bevel=0.04, parent=pel)
    kit.ball("head", 0.08, (0, 0, 0.45), "pearl", parent=pel)
    legs = [kit.empty("leg") for _ in (0, 1)]
    for lg in legs:
        kit.cyl("bone", 0.035, 1.0, (0.5, 0, 0), "x", "dark", parent=lg, segments=20)   # scaled in x to the leg length: the model holds body height fixed
    feet = [kit.box("foot", (2 * HALF, 0.08, 0.04), (0, 0, 0), "dark", bevel=0.01) for _ in (0, 1)]
    walkers[step] = (x0, pel, legs, feet, kit.ball("zmp", 0.04, (0, 0, 0), kit.mat("amber", emit=0.6)), kit.arrow("push", "red"))

for f in range(1, sc.frame_end + 1):
    t = min(max(f - 1 - PRE, 0) / 24 / SLOW, TEND)
    i = int(round(t / DT))
    for step, (x0, pel, legs, feet, mark, push) in walkers.items():
        x = x0 + runs[step][1][i]
        s = min(t / 0.1, 1.0)
        fx = [0.0, LAND * (3 * s * s - 2 * s ** 3) if step else 0.0]                 # the second foot swings out to the capture point in the first 0.1 s
        fz = [0.0, 0.12 * math.sin(math.pi * s) if step else 0.0]
        kit.key(pel, f, loc=(x, 0, H))
        for k, dy in enumerate((0.09, -0.09)):
            a, b = (x0 + fx[k], dy, fz[k] + 0.04), (x, dy, H - 0.05)
            legs[k].scale = (math.hypot(b[0] - a[0], b[2] - a[2]), 1, 1)
            legs[k].keyframe_insert("scale", frame=f)
            kit.key(legs[k], f, loc=a, rot=(0, -math.atan2(b[2] - a[2], b[0] - a[0]), 0))
            kit.key(feet[k], f, loc=(a[0], dy, fz[k] + 0.02))
        kit.key(mark, f, loc=(x0 + float(zmps[step][i]), 0.09 if not step or t < 0.1 else -0.09, 0.065))
        push.scale = (0.3, 1.6, 1.6) if f <= PRE + 1 else (1e-4,) * 3
        push.keyframe_insert("scale", frame=f)
        kit.key(push, f, loc=(x0 - 0.5, 0, H + 0.1))
kit.camera((0.15, -3.5, 2.2), (0.15, 0, 0.62), lens=38)
kit.render(__file__)
