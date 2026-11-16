# 레슨 03/08 예시 클립: 같은 한계 0.5 에서 MPC 가 앞을 2 step, 10 step, 20 step 내다보면 정지선을 넘는 거리가 1.27 m, 0.78 m, 0.31 m 로 줄어든다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import numpy as np

import kit

m = kit.lesson_main(__file__)
DT, N, S, UMAX, SPEED, CS = 0.1, 120, 0.6, 0.5, 2.0, 1.6      # the lesson's step and 12 s run, played at 2x; 1 m is drawn as 0.6 m; the cars are drawn 1.6 times larger
A, B = m.double_integrator(DT)
Q, R = np.diag([1.0, 0.1]), np.array([[0.1]])
horizons = (("two", 2, "blue", 0.8), ("ten", 10, "blue", 0.0), ("twenty", 20, "green", -0.8))        # plan length in steps, colour, lane
runs = {name: m.simulate([4.0, 0.0], N, A, B, Q, R, h, UMAX)[0][:, 0] for name, h, _, _ in horizons}

sc = kit.setup(N * DT / SPEED)
kit.stripe(-3.9, 1.5, -1.25, 1.25, "road")
kit.stripe(-0.05, 0.05, -1.25, 1.25, "white", z=0.004)           # the stop line
for name, _, colour, y in horizons:
    root, wheels, _ = kit.car(name, colour, CS)
    gauge = kit.box(name + "-slide", (1.0, 0.07, 0.03), (0, y - 0.34, 0.02), "amber", bevel=0.005)   # beside the car: how far its nose has slid past the line, so the three overshoots read as three bar lengths
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = min(int((f - 1) / 24 * SPEED / DT), N - 1)
        kit.drive(root, wheels, f, -S * runs[name][k] - 0.3 * CS, y, radius=0.09 * CS)
        past = S * max(0.0, -float(runs[name][:k + 1].min()))
        gauge.scale, gauge.location = (max(past, 1e-3), 1, 1), (past / 2, y - 0.34, 0.02)
        for prop in ("scale", "location"):
            gauge.keyframe_insert(prop, frame=f)
kit.camera((-1.5, -3.6, 2.9), (-1.5, 0.0, 0.1), lens=34)
kit.render(__file__)
