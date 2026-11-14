# 레슨 10/03 예시 클립: 20도 기울인 쿼드로터 둘. 파란 쪽은 추력 m g 라서 가라앉고 초록 쪽은 m g / cos(theta) 라서 높이를 지킨다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
M, I, TILT, TEND, SLOW, PRE, Z0, S = 0.5, 0.004, math.radians(20), 1.0, 2.5, 12, 0.6, 1.6   # the lesson's drone held at 20 degrees for 1 s, played 2.5x slower
hover = m.hover_thrust(M)
s0 = np.array([0, 0, TILT, 0, 0, 0.0])
runs = {"sink": m.simulate(s0, lambda t, s: (hover, 0.0), M, I, 1e-3, TEND),
        "hold": m.simulate(s0, lambda t, s: (hover / math.cos(s[2]), 0.0), M, I, 1e-3, TEND)}   # same tilt, thrust raised to m g / cos(theta)
sc = kit.setup(PRE / 24 + TEND * SLOW + 1.2)
quads = {}
kit.tube("level", [(-2.4, 0, Z0), (2.2, 0, Z0)], 0.012, "dark")      # one level line across both drones, to see who keeps height
for name, (colour, x0) in {"sink": ("blue", -1.4), "hold": ("green", -0.5)}.items():
    root, props = kit.drone(name, colour)
    root.scale = (S, S, S)                                                      # drawn 1.6 times larger so it reads from the camera
    kit.ball("start", 0.08, (x0, 0, Z0), "amber")                            # a solid ball at the height it started at
    quads[name] = (root, props, x0)

for f in range(1, sc.frame_end + 1):
    i = int(round(min(max(f - 1 - PRE, 0) / 24 / SLOW, TEND) / 1e-3))
    for name, (root, props, x0) in quads.items():
        s = runs[name][1][i]                                                    # [x, z, pitch, ...]
        kit.key(root, f, loc=(x0 + s[0], 0, Z0 + s[1]), rot=(0, float(s[2]), 0))
        for j, p in enumerate(props):
            kit.key(p, f, rot=(0, 0, (1 if j % 2 else -1) * 0.55 * f))
kit.camera((-0.05, -4.3, 1.9), (-0.05, 0, Z0), lens=38)   # nearly side-on, so sinking reads as vertical motion
kit.render(__file__)
