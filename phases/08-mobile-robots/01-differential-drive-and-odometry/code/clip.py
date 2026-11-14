# 레슨 08/01 클립: 같은 바퀴 명령으로 2 m 정사각형을 도는 로버. 실제 로버는 윤거가 5% 크고, 오도메트리는 닫힌 사각형을 믿는다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
R, B, DT, ZOOM = 0.05, 0.30, 0.01, 1.1            # lesson wheel radius, track width, step; the rover is drawn 1.1 times larger
WR = 0.075 * ZOOM                                  # drawn wheel radius
wl, wr = m.square_wheels(2.0, 0.5, DT, R, B)
real = m.dead_reckon(wl, wr, DT, R, B * 1.05)      # what the wheels really did: track width 5% larger than the config says
spin = [np.concatenate([[0], np.cumsum(w) * DT * R / WR]) for w in (wl, wr)]   # wheel angles, rolling without slip
FPS, PLAY, N = 24, 4.4, len(real) - 1

sc = kit.setup(5.0)
kit.stripe(-0.7, 2.7, -0.7, 2.7, "road")
for a, b in (((0, 2), (0, 0.02)), ((0, 2), (1.98, 2)), ((0, 0.02), (0, 2)), ((1.98, 2), (0, 2))):   # the square the odometry believes in
    kit.stripe(a[0], a[1], b[0], b[1], "white", z=0.004)
root, wheels = kit.rover("real", "blue")
root.scale = (ZOOM,) * 3
belief = kit.cyl("belief", 0.19, 0.1, (0, 0, 0.11), "z", kit.ghost("green", 0.45))   # where odometry says the rover is
kit.box("belief-nose", (0.05, 0.12, 0.03), (0.17, 0, 0.13), "amber", parent=belief)
belief.scale = (ZOOM,) * 3
est = m.dead_reckon(wl, wr, DT, R, B)
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / FPS / PLAY * N), N)
    kit.key(root, f, loc=(*real[i, :2], 0), rot=(0, 0, real[i, 2]))
    kit.key(belief, f, loc=(*est[i, :2], 0.0), rot=(0, 0, est[i, 2]))
    for w, a in zip(wheels, (spin[0][min(i, N - 1)], spin[1][min(i, N - 1)])):
        kit.key(w, f, rot=(0, a, 0))
for j in range(60, N, 60):                                         # a breadcrumb every 0.3 m or so, dropped when the rover passes
    f = int(np.ceil(j / N * PLAY * FPS)) + 1
    d = kit.ball("crumb", 0.04, (*real[j, :2], 0.03), "blue")
    d.scale = (0, 0, 0)
    d.keyframe_insert("scale", frame=f - 1)
    d.scale = (1, 1, 1)
    d.keyframe_insert("scale", frame=f)
gap = real[-1, :2]
bar = kit.box("gap", (float(np.linalg.norm(gap)), 0.05, 0.03), (*(gap / 2), 0.02), "amber", bevel=0.005)
bar.rotation_euler = (0, 0, float(np.arctan2(gap[1], gap[0])))
bar.scale = (0, 0, 0); bar.keyframe_insert("scale", frame=int(PLAY * FPS)); bar.scale = (1, 1, 1); bar.keyframe_insert("scale", frame=int(PLAY * FPS) + 8)
kit.camera((0.95, -1.4, 4.4), (0.95, 1.05, 0.0), lens=33)
kit.render(__file__)
