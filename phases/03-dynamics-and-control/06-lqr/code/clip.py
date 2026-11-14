# 레슨 03/06 클립: 같은 LQR 로 정지선까지 가는 장난감 자동차 둘. 파란 차는 노력이 싸서(R=0.01) 빨리 세게 밀고, 초록 차는 비싸서(R=10) 살살 민다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import math

import numpy as np

import kit

m = kit.lesson_main(__file__)
DT, N, S, ARROW = 0.05, 120, 1.5, 0.15              # the lesson's step and 6 s horizon; 1 m is drawn as 1.5 m; the red arrow is 0.15 m per m/s^2 of push
A, B = m.double_integrator(DT)
Q = np.diag([1.0, 0.1])
runs = {}
for c, r in (("blue", 0.01), ("green", 10.0)):
    R = np.array([[r]])
    runs[c] = m.rollout(A, B, m.dare(A, B, Q, R)[0], [1.0, 0.0], N, Q, R)[:2]     # states (position error, velocity) and pushes u

sc = kit.setup(N * DT)
kit.stripe(-3.0, 1.6, -0.75, 0.75, "road")
kit.stripe(-0.03, 0.03, -0.75, 0.75, "white", z=0.004)           # the stop line
for c, y in (("blue", 0.4), ("green", -0.4)):
    root, wheels, brake = kit.car(c, c)
    push = kit.arrow(c + "-push", "red")
    xs, us = runs[c]
    for f in range(sc.frame_start, sc.frame_end + 1):
        i = min(int((f - 1) / 24 / DT), N - 1)
        x = -S * xs[i, 0] - 0.3                                   # the nose is the measured point
        kit.drive(root, wheels, f, x, y)
        a = -float(us[i, 0])                                      # u pulls the error down, so the car speeds up when u < 0
        push.scale, push.rotation_euler, push.location = (ARROW * abs(a),) * 3, (0, 0, 0 if a > 0 else math.pi), (x, y, 0.62)
        for p in ("scale", "rotation_euler", "location"):
            push.keyframe_insert(p, frame=f)
kit.camera((-0.9, -3.1, 2.1), (-0.9, 0.05, 0.1), lens=40)
kit.render(__file__)
