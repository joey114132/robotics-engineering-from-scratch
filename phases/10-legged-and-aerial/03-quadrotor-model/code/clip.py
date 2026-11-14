# 레슨 10/03 클립: 같은 쿼드로터 둘. 파란 쪽은 추력을 10% 올리면 위로만 오르고 초록 쪽은 토크를 주면 기울어진 뒤에야 옆으로 간다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
M, I, TAU, TEND, SLOW, PRE, Z0, S = 0.5, 0.004, 0.002, 1.4, 2.0, 12, 0.5, 1.6    # the lesson's two steps, played at half speed after 0.5 s of hover
hover = m.hover_thrust(M)
runs = {"thrust": m.simulate(np.zeros(6), lambda t, s: (1.1 * hover, 0.0), M, I, 1e-3, TEND),
        "torque": m.simulate(np.zeros(6), lambda t, s: (hover, TAU), M, I, 1e-3, TEND)}
sc = kit.setup(PRE / 24 + TEND * SLOW + 1.2)
quads = {}
for name, (colour, x0) in {"thrust": ("blue", 0.85), "torque": ("green", -0.85)}.items():
    root, props = kit.drone(name, colour)
    root.scale = (S, S, S)                                                      # drawn 1.6 times larger so it reads from the camera
    kit.ball("start", 0.06, (x0, 0, Z0), kit.mat("white", emit=1.0))                # a solid white ball where it started, left behind when it moves
    quads[name] = (root, props, x0)

for f in range(1, sc.frame_end + 1):
    i = int(round(min(max(f - 1 - PRE, 0) / 24 / SLOW, TEND) / 1e-3))
    for name, (root, props, x0) in quads.items():
        s = runs[name][1][i]                                                    # [x, z, pitch, ...]
        kit.key(root, f, loc=(x0 + s[0], 0, Z0 + s[1]), rot=(0, float(s[2]), 0))
        for j, p in enumerate(props):
            kit.key(p, f, rot=(0, 0, (1 if j % 2 else -1) * 0.55 * f))
kit.camera((0, -2.6, 3.5), (0, 0, 1.2), lens=38)
kit.render(__file__)
