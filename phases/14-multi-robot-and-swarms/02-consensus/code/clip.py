# 레슨 14/02 클립: 같은 시작 방향의 로봇 여덟 대가 이웃 방향만 보고 합의한다. 링(파란색)은 천천히, 완전 그래프(초록색)는 금방 한 방향으로 모인다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
X0, EPS, FRAMES, UNIT, LEAD, HOLD = np.array([4.0, -1.0, 2.0, 7.0, 0.0, 3.0, -5.0, 1.0]), 0.05, 116, 0.25, 4, 12   # state x_i drawn as a heading of 0.25 rad per unit
graphs = {"blue": m.ring(8), "green": m.complete(8)}

sc = kit.setup((LEAD + FRAMES + HOLD) / 24)
for colour, cx in (("blue", -1.65), ("green", 1.65)):
    A, traj = graphs[colour], m.run(X0, graphs[colour], EPS, 100)
    kit.box("pad", (2.8, 2.8, 0.02), (cx, 1.2, 0.01), "#e6ecee", bevel=0.01)
    spot = [(cx + 1.0 * math.cos(2 * math.pi * i / 8), 1.2 + 1.0 * math.sin(2 * math.pi * i / 8)) for i in range(8)]
    for i in range(8):
        for j in range(i + 1, 8):
            if A[i, j]:                                                           # a radio link between neighbours
                kit.tube("link", [(*spot[i], 0.05), (*spot[j], 0.05)], 0.012, "grey")
    ghost = kit.arrow("average", "grey", 0.03)                                    # the initial average, which consensus keeps
    ghost.location, ghost.rotation_euler, ghost.scale = (cx - 0.4, 1.2, 0.04), (0, 0, UNIT * X0.mean()), (0.8, 1, 1)
    for ch in ghost.children:
        ch.data.materials[0] = kit.ghost("grey", 0.55)
    for i in range(8):
        root, wheels = kit.rover(f"{colour}{i}", colour)
        root.scale = (1.1,) * 3
        pointer = kit.arrow(f"heading{i}", "amber", 0.03)
        pointer.parent, pointer.location, pointer.scale = root, (0, 0, 0.26), (0.55, 1, 1)
        for f in range(sc.frame_start, sc.frame_end + 1):
            u = 0.2 * (n := min(max(f - 1 - LEAD, 0), FRAMES)) + 0.0045 * n * n   # updates so far: 5 frames each at first, more than 1 a frame at the end
            th = UNIT * np.interp(u, np.arange(len(traj)), traj[:, i])
            kit.key(root, f, loc=(*spot[i], 0), rot=(0, 0, th))
            kit.key(wheels[0], f, rot=(0, -(th - UNIT * X0[i]) * 0.2 / 0.075, 0))   # turning in place: the two wheels roll opposite ways
            kit.key(wheels[1], f, rot=(0, (th - UNIT * X0[i]) * 0.2 / 0.075, 0))
kit.camera((0, -3.25, 4.15), (0, 1.0, 0), lens=26)
kit.render(__file__)
