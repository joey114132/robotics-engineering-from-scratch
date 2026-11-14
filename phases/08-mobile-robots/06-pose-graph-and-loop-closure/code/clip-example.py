# 레슨 08/06 예시 클립: 같은 표류 그래프에 틀린 폐쇄 edge(파랑)와 맞는 폐쇄 edge(초록)를 넣고 풀면 파랑은 더 휘고 초록은 정사각형으로 닫힌다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
truth, edges, X0 = m.world(np.random.default_rng(0))             # the lesson's world: 21 poses, a heading bias of 0.02 rad every step
i, j, z, w = edges[-1]
solved = {"wrong": m.solve(X0, edges[:-1] + [(i, j, z + np.array([3.0, -2.0, 0.8]), w)])[0],   # the test's false closure: 3 m and 2 m off, 0.8 rad
          "right": m.solve(X0, edges)[0]}
panels = {"wrong": (0.0, "blue"), "right": (7.2, "green")}       # panel offset in x, node colour
T0, T1, N = 24, 76, 124                                          # frames: stretched springs held, relax, final hold
yaw0 = np.unwrap(X0[:, 2])

sc = kit.setup(N / 24)
kit.stripe(-1.4, 13.0, -2.8, 6.2, "road")
parts = {}
for k, (ox, colour) in panels.items():
    kit.tube("truth-" + k, [(x + ox, y, 0.01) for x, y in truth[:, :2]], 0.03, "white")        # the square the rover really drove
    nodes = [kit.ball("node", 0.09, (0, 0, 0.1), colour) for _ in X0]
    springs = [kit.cyl("spring", 0.02, 1.0, (0, 0, 0), "x", "dark", segments=8) for _ in range(len(X0) - 1)]
    closure = kit.cyl("closure", 0.05, 1.0, (0, 0, 0), "x", "amber", segments=12)
    root, wheels = kit.rover("rover-" + k, colour)
    root.scale = (1.4,) * 3
    parts[k] = (nodes, springs, closure, root)


def edge(ob, a, b, ox, zz):
    v = b - a
    ob.location, ob.rotation_euler, ob.scale = (*(a + v / 2 + [ox, 0]), zz), (0, 0, float(np.arctan2(v[1], v[0]))), (max(float(np.hypot(*v)), 1e-3), 1, 1)
    for p in ("location", "rotation_euler", "scale"):
        ob.keyframe_insert(p, frame=f)


for f in range(1, N + 1):
    s = float(np.clip((f - T0) / (T1 - T0), 0, 1))
    s = s * s * (3 - 2 * s)                                       # the solver has no time axis: every node slides from its odometry pose to its solved pose
    for k, (ox, colour) in panels.items():
        nodes, springs, closure, root = parts[k]
        P = X0[:, :2] + s * (solved[k][:, :2] - X0[:, :2])
        for n, p in zip(nodes, P):
            kit.key(n, f, loc=(p[0] + ox, p[1], 0.1))
        for a, spring in enumerate(springs):
            edge(spring, P[a], P[a + 1], ox, 0.05)
        edge(closure, P[0], P[-1], ox, 0.07)
        yaw = yaw0[-1] + s * (np.unwrap(solved[k][:, 2])[-1] - yaw0[-1])
        kit.key(root, f, loc=(P[-1, 0] + ox, P[-1, 1], 0), rot=(0, 0, yaw))
kit.camera((5.7, -0.4, 11.4), (5.7, 1.3, 0.0), lens=28)
kit.render(__file__)
