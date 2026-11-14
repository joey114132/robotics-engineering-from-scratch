# 레슨 08/04 예시 클립: 경로 옆 0.6 m에서 출발한 자동차 두 대의 첫 조향. 짧은 lookahead는 급한 원, 긴 lookahead는 완만한 원을 그린다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
CORNERS = [(0, 0), (10, 0), (10, 10)]
path = m.dense(CORNERS)
FPS, HOLD, PLAY, END = 24, 0.6, 3.2, 0.8                         # seconds: look at the arcs, drive at real speed, settle
lanes = {0.4: ("blue", 0.0), 1.5: ("green", 1.9)}                  # lookahead -> (colour, lane offset in y); both lanes use the lesson's real lengths
runs = {ld: m.follow(CORNERS, ld) for ld in lanes}
arc = {ld: np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(t[:, :2], axis=0), axis=1))]) for ld, t in runs.items()}

sc = kit.setup(HOLD + PLAY + END)
kit.stripe(-0.9, 3.9, -0.7, 2.9, "road")
cars, goals = {}, {}
for ld, (colour, oy) in lanes.items():
    kit.stripe(-0.6, 3.6, oy - 0.02, oy + 0.02, "white", z=0.004)       # the path: a straight line for the first 3.6 m
    start = runs[ld][0]
    target = m.lookahead_point(path, start[:2], ld)
    k = m.curvature(start, target)                                       # the circle the first steering command follows
    R, c = 1 / abs(k), np.array([start[0], start[1] - 1 / abs(k)])
    a1 = np.arctan2(*(target - c)[::-1])
    a1 = a1 - 2 * np.pi if a1 > np.pi / 2 else a1
    pts = [(c[0] + R * np.cos(a), c[1] + R * np.sin(a) + oy, 0.02) for a in np.linspace(np.pi / 2, a1, 40)]
    kit.tube("arc", pts, 0.014, colour)
    cars[ld] = kit.car(f"car{ld}", colour)
    goals[ld] = kit.ball("target", 0.06, (0, 0, 0.5), "amber")
for f in range(sc.frame_start, sc.frame_end + 1):
    t = min(max((f - 1) / FPS - HOLD, 0.0), PLAY)
    for ld, (colour, oy) in lanes.items():
        tr = runs[ld]
        i = int(round(t / 0.02))
        root, wheels, brake = cars[ld]
        kit.key(root, f, loc=(tr[i, 0], tr[i, 1] + oy, 0), rot=(0, 0, tr[i, 2]))
        for w in wheels:
            kit.key(w, f, rot=(0, arc[ld][i] / 0.09, 0))
        g = m.lookahead_point(path, tr[i, :2], ld)
        kit.key(goals[ld], f, loc=(g[0], g[1] + oy, 0.45))
kit.camera((1.35, -1.9, 4.6), (1.35, 1.0, 0.0), lens=32)
kit.render(__file__)
