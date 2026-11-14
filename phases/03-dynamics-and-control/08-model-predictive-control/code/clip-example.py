# 레슨 03/08 예시 클립: 같은 한계 0.5 에서 MPC 가 앞을 2 step, 10 step, 20 step 내다보면 정지선을 넘는 거리가 1.27 m, 0.78 m, 0.31 m 로 줄어든다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import numpy as np

import kit

m = kit.lesson_main(__file__)
DT, N, S, UMAX, SPEED, CS = 0.1, 120, 0.85, 0.5, 2.0, 1.3      # the lesson's step and 12 s run, played at 2x; 1 m is drawn as 0.85 m; the cars are drawn 1.3 times larger
A, B = m.double_integrator(DT)
Q, R = np.diag([1.0, 0.1]), np.array([[0.1]])
horizons = (("two", 2, "blue", 1.0), ("ten", 10, "blue", 0.0), ("twenty", 20, "green", -1.0))        # plan length in steps, colour, lane
runs = {name: m.simulate([4.0, 0.0], N, A, B, Q, R, h, UMAX)[0][:, 0] for name, h, _, _ in horizons}

sc = kit.setup(N * DT / SPEED)
kit.stripe(-4.0, 1.9, -1.5, 1.5, "road")
kit.stripe(-0.03, 0.03, -1.5, 1.5, "white", z=0.004)           # the stop line
for name, _, colour, y in horizons:
    root, wheels, _ = kit.car(name, colour, CS)
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = min(int((f - 1) / 24 * SPEED / DT), N - 1)
        kit.drive(root, wheels, f, -S * runs[name][k] - 0.3 * CS, y, radius=0.09 * CS)
kit.camera((-1.0, -5.4, 4.6), (-1.0, 0.05, 0.1), lens=34)
kit.render(__file__)
