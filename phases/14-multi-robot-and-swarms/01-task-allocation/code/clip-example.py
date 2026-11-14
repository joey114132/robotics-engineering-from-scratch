# 레슨 14/01 예시 클립: 같은 다섯 대가 차례로 한 대씩 달린다. 파란 쪽은 greedy 배정이라 마지막 5번 자동차가 바닥을 가로지르고, 초록 쪽은 hungarian 배정이라 모두 짧다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
N, SEED, SIDE, V, LEAD, HOLD = 5, 3875, 2.7, 1.2, 0.3, 0.7     # the lead clip's layout (2.7 m floor); the cars go one after another in index order at 1.2 m/s
rng = np.random.default_rng(SEED)
R, T = rng.random((N, 2)), rng.random((N, 2))
C = m.cost_matrix(R, T)
plans = {"blue": m.greedy(C), "green": m.hungarian(C)}
trips = {c: [C[i, j] * SIDE for i, j in enumerate(p)] for c, p in plans.items()}
SECONDS = LEAD + max(sum(t) for t in trips.values()) / V + HOLD

sc = kit.setup(SECONDS)
for colour, cx in (("blue", -1.65), ("green", 1.65)):
    kit.box("pad", (SIDE + 0.4, SIDE + 0.4, 0.02), (cx, SIDE / 2, 0.01), "#e6ecee", bevel=0.01)
    at = lambda p: (cx - SIDE / 2 + p[0] * SIDE, p[1] * SIDE)
    for j in range(N):
        kit.cyl("task", 0.25, 0.02, (*at(T[j]), 0.03), "z", "amber", segments=32)
    start = LEAD
    for i, j in enumerate(plans[colour]):
        a, b = at(R[i]), at(T[j])
        kit.tube("route", [(*a, 0.045), (*b, 0.045)], 0.02, "sky" if colour == "blue" else "#a6dcbd")
        root, wheels = kit.rover(f"{colour}{i}", colour)
        root.scale = (1.3,) * 3
        yaw, dist = math.atan2(b[1] - a[1], b[0] - a[0]), math.dist(a, b)
        for f in range(sc.frame_start, sc.frame_end + 1):
            s = min(max((f - 1) / sc.render.fps - start, 0.0) * V, dist)
            kit.key(root, f, loc=(a[0] + s / dist * (b[0] - a[0]), a[1] + s / dist * (b[1] - a[1]), 0), rot=(0, 0, yaw))
            for w in wheels:
                kit.key(w, f, rot=(0, s / (0.075 * 1.3), 0))
        start += dist / V                                                                  # the next car sets off when this one has arrived
kit.camera((0, -3.25, 4.15), (0, 1.0, 0), lens=26)
kit.render(__file__)
