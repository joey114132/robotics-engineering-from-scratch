# 레슨 08/04 클립: 같은 경로를 세 lookahead 거리로 따라가는 자동차 세 대를 나란한 세 차선에 그린다. 짧으면 흔들리고 길면 코너를 자른다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, PLAY, FPS, D, CAR = 0.5, 5.2, 24, 1.2, 1.5                    # 1 m drawn as 0.5 m; played at 4x; lane spacing; car drawn 1.5 times larger
CORNERS = [(0, 0), (10, 0), (10, 6)]                              # the lesson's corner, with a shorter second leg to fit the frame
path = m.dense(CORNERS)
lanes = {4.0: 0, 1.5: 1, 0.4: 2}                                  # lookahead -> lane; the corner-cutting car gets the inside lane
colour = {0.4: "blue", 1.5: "green", 4.0: "red"}
runs = {ld: m.follow(CORNERS, ld) for ld in lanes}
shift = {ld: np.array([k * D, -k * D]) for ld, k in lanes.items()}   # each lane is the same L moved 1.2 down and right

sc = kit.setup(PLAY + 0.8)
for ld, (ox, oy) in shift.items():
    kit.stripe(ox - 0.5, ox + 5.6, oy - 0.5, oy + 0.7, "road")    # a road along each lane's path
    kit.stripe(ox + 4.4, ox + 5.6, oy - 0.5, oy + 3.4, "road")
    kit.tube(f"path{ld}", [(x * S + ox, y * S + oy, 0.006) for x, y in CORNERS], 0.02, "white")
cars = {ld: kit.car(f"ld{ld}", colour[ld], CAR) for ld in runs}
goals = {ld: kit.ball(f"goal{ld}", 0.05, (0, 0, 0.5), "amber") for ld in runs}
arc = {ld: np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(t[:, :2], axis=0), axis=1))]) * S for ld, t in runs.items()}
N = max(len(t) for t in runs.values()) - 1
for f in range(sc.frame_start, sc.frame_end + 1):
    for ld, t in runs.items():
        i = min(int((f - 1) / FPS / PLAY * N), len(t) - 1)
        root, wheels, brake = cars[ld]
        kit.key(root, f, loc=(*(t[i, :2] * S + shift[ld]), 0), rot=(0, 0, t[i, 2]))
        for w in wheels:
            kit.key(w, f, rot=(0, arc[ld][i] / (0.09 * CAR), 0))
        g = m.lookahead_point(path, t[i, :2], ld) * S + shift[ld]
        kit.key(goals[ld], f, loc=(g[0], g[1], 0.5))
for ld, t in runs.items():                                        # a breadcrumb every 0.25 m of drawing, dropped as the car passes
    for j in range(25, len(t), 25):
        d = kit.ball("crumb", 0.04, (*(t[j, :2] * S + shift[ld]), 0.03), colour[ld])
        f = int(np.ceil(j / N * PLAY * FPS)) + 1
        d.scale = (0, 0, 0)
        d.keyframe_insert("scale", frame=f - 1)
        d.scale = (1, 1, 1)
        d.keyframe_insert("scale", frame=f)
kit.camera((3.5, -1.0, 9.2), (3.5, 0.45, 0.0), lens=28)
kit.render(__file__)
