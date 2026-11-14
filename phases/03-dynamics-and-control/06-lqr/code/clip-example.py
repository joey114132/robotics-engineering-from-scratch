# 레슨 03/06 예시 클립: Riccati 반복을 1번, 10번, P 가 일정해질 때까지 돌려 얻은 게인으로 같은 차를 모는 장면. 반복이 쌓일수록 게인이 자라 차가 선에 선다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import numpy as np

import kit

m = kit.lesson_main(__file__)
DT, N, S = 0.05, 120, 1.5                            # the lesson's step and a 6 s run at real speed; 1 m is drawn as 1.5 m
A, B = m.double_integrator(DT)
Q, R = np.diag([1.0, 0.1]), np.array([[1.0]])        # R = 1; the gains come from dare() stopped after 1 loop, after 10 loops and when P is steady
runs = {}
for name, loops in (("one", 1), ("ten", 10), ("steady", 100000)):
    runs[name] = m.rollout(A, B, m.dare(A, B, Q, R, max_iter=loops)[0], [1.0, 0.0], N, Q, R)[0]

sc = kit.setup(N * DT)
kit.stripe(-3.0, 1.6, -1.15, 1.15, "road")
kit.stripe(-0.03, 0.03, -1.15, 1.15, "white", z=0.004)           # the stop line
for name, colour, y in (("one", "blue", 0.75), ("ten", "blue", 0.0), ("steady", "green", -0.75)):
    root, wheels, _ = kit.car(name, colour)
    for f in range(sc.frame_start, sc.frame_end + 1):
        i = min(int((f - 1) / 24 / DT), N - 1)
        kit.drive(root, wheels, f, -S * runs[name][i, 0] - 0.3, y)   # the nose is the measured point
kit.camera((-0.9, -3.5, 2.4), (-0.9, 0.05, 0.1), lens=40)
kit.render(__file__)
