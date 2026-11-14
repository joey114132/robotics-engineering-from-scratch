# 레슨 03/07 예시 클립: 두 관절이 함께 돌 때의 운동에너지는 각 관절만 돌 때의 합과 다르고, 그 차이가 M12 이며 팔꿈치 각도에 따라 변한다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import numpy as np

import kit

m = kit.lesson_main(__file__)
P = dict(m1=1.0, m2=1.5, l1=0.5, lc1=0.2, lc2=0.3, I1=0.03, I2=0.05)   # the lesson's figure arm
SECONDS, Q0, E, GAUGE = 6.0, np.array([0.3, 1.0]), np.eye(2), 1.0      # both joints turn at 1 rad/s for 6 s; a 1 m bar is 1.05 J of kinetic energy

sc = kit.setup(SECONDS)
kit.table((4.6, 2.4), 0.4, (0.25, 0))
root = kit.empty("arm")
root.location = (-0.9, 0, 0.4)
j0 = kit.empty("j0", (0, 0, 0.42), root)
j1 = kit.empty("j1", (0.5, 0, 0.07), j0)
kit.cyl("post", 0.06, 0.42, (0, 0, 0.21), "z", "grey", parent=root)
kit.cyl("m0", 0.075, 0.1, (0, 0, 0), "z", "dark", parent=j0)
kit.cyl("m1", 0.06, 0.08, (0, 0, 0), "z", "dark", parent=j1)
kit.box("l0", (0.52, 0.07, 0.05), (0.25, 0, 0.035), "blue", bevel=0.01, parent=j0)
kit.box("l1", (0.52, 0.06, 0.04), (0.25, 0, 0.03), "sky", bevel=0.01, parent=j1)
bars = {"alone0": kit.box("alone0", (0.25, 0.25, 1.0), (1.0, 0, 0.9), "blue", bevel=0.01),     # energy of joint 1 turning alone
        "alone1": kit.box("alone1", (0.25, 0.25, 1.0), (1.0, 0, 0.9), "sky", bevel=0.01),      # energy of joint 2 turning alone, stacked on it
        "both": kit.box("both", (0.25, 0.25, 1.0), (1.5, 0, 0.9), "amber", bevel=0.01)}        # energy with both turning
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / 24
    q = Q0 + t
    kit.key(j0, f, rot=(0, 0, q[0]))
    kit.key(j1, f, rot=(0, 0, q[1]))
    h = [GAUGE * m.kinetic(q, v, P) / 1.05 for v in (E[0], E[1], E[0] + E[1])]
    for name, (z0, hh, x) in {"alone0": (0.4, h[0], 1.0), "alone1": (0.4 + h[0], h[1], 1.0), "both": (0.4, h[2], 1.5)}.items():
        bars[name].scale, bars[name].location = (1, 1, hh), (x, 0, z0 + hh / 2)
        for p in ("scale", "location"):
            bars[name].keyframe_insert(p, frame=f)
kit.camera((0.3, -3.5, 2.7), (0.3, -0.1, 0.6), lens=32)
kit.render(__file__)
