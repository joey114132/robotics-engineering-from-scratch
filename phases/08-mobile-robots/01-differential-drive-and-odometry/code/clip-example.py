# 레슨 08/01 예시 클립: 두 바퀴가 같은 속도면 직선, 오른쪽이 더 빠르면 지름 1.8 m 원을 그린다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
R, B, DT, ZOOM = 0.05, 0.30, 0.01, 1.1            # lesson wheel radius, track width, step; the rover is drawn 1.1 times larger
WR = 0.075 * ZOOM
N, PLAY, FPS = 440, 4.4, 24                       # 4.4 s of lesson time at real speed
runs = {"straight": (10.0, 10.0), "curve": (10.0, 14.0)}   # (left, right) wheel speed in rad/s
paths = {k: m.dead_reckon(np.full(N, l), np.full(N, r), DT, R, B) for k, (l, r) in runs.items()}

sc = kit.setup(5.2)
kit.stripe(-0.8, 2.8, -1.3, 2.1, "road")
rovers = {}
for name, colour, y0 in (("straight", "blue", -0.8), ("curve", "green", 0.0)):
    root, wheels = kit.rover(name, colour)
    root.scale = (ZOOM,) * 3
    pts = [(p[0], p[1] + y0, 0.012) for p in paths[name][::10]]
    kit.tube(name + "-trail", pts, 0.012, colour)
    rovers[name] = (root, wheels, y0)
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / FPS / PLAY * N), N)
    for name, (root, wheels, y0) in rovers.items():
        p = paths[name][i]
        kit.key(root, f, loc=(p[0], p[1] + y0, 0), rot=(0, 0, p[2]))
        for w, speed in zip(wheels, runs[name]):
            kit.key(w, f, rot=(0, speed * DT * i * R / WR, 0))
kit.camera((1.0, -1.8, 4.8), (1.0, 0.45, 0.0), lens=33)
kit.render(__file__)
