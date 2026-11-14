# 레슨 14/01 클립: 같은 배치에서 탐욕 배정(파란 로봇)과 Hungarian 배정(초록 로봇)이 각자 일을 찾아 같은 속도로 달린다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
N, SEED, SIDE, V, SECONDS, LEAD = 5, 3875, 2.7, 0.52, 5.5, 0.3          # a 1 x 1 layout drawn as 2.7 m; every robot drives 0.52 m/s
rng = np.random.default_rng(SEED)
R, T = rng.random((N, 2)), rng.random((N, 2))
C = m.cost_matrix(R, T)
plans = {"blue": m.greedy(C), "green": m.hungarian(C)}

sc = kit.setup(SECONDS)
for colour, cx in (("blue", -1.65), ("green", 1.65)):
    kit.box("pad", (SIDE + 0.4, SIDE + 0.4, 0.02), (cx, SIDE / 2, 0.01), "#e6ecee", bevel=0.01)
    at = lambda p: (cx - SIDE / 2 + p[0] * SIDE, p[1] * SIDE)
    for j in range(N):
        kit.cyl("task", 0.25, 0.02, (*at(T[j]), 0.03), "z", "amber", segments=32)
    for i, j in enumerate(plans[colour]):
        a, b = at(R[i]), at(T[j])
        kit.tube("route", [(*a, 0.045), (*b, 0.045)], 0.02, "sky" if colour == "blue" else "#a6dcbd")
        root, wheels = kit.rover(f"{colour}{i}", colour)
        root.scale = (1.3,) * 3
        yaw, dist = math.atan2(b[1] - a[1], b[0] - a[0]), math.dist(a, b)
        for f in range(sc.frame_start, sc.frame_end + 1):
            s = min(max((f - 1) / sc.render.fps - LEAD, 0.0) * V, dist)
            kit.key(root, f, loc=(a[0] + s / dist * (b[0] - a[0]), a[1] + s / dist * (b[1] - a[1]), 0), rot=(0, 0, yaw))
            for w in wheels:
                kit.key(w, f, rot=(0, s / (0.075 * 1.3), 0))
kit.camera((0, -3.25, 4.15), (0, 1.0, 0), lens=26)
kit.render(__file__)
