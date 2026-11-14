# 레슨 07/03 클립: 가만히 서 있는 실제 로봇(초록)과, 가속도 bias(파란 유령)와 gyro bias(호박색 유령)를 적분해 미끄러지는 위치 추정
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
DT, N, BA, BG, RS, X0 = 0.01, 500, 0.05, 0.01, 1.3, -1.0      # the lesson's biases, 5 s drawn 1 m as 1 m
_, pos_acc = m.accel_position(np.zeros(N), BA, 0.0, DT, np.random.default_rng(0))
pos_acc = pos_acc[:, 0]
pos_gyr = m.leaked_position(BG, N, DT)

sc = kit.setup(5.5)
kit.stripe(-1.4, 1.5, -1.1, 1.1, "road")
for x in np.arange(-1.0, 1.5, 0.5):
    kit.stripe(x - 0.01, x + 0.01, -1.1, 1.1, "white", z=0.004)    # a mark every 0.5 m
kit.stripe(X0 - 0.02, X0 + 0.02, -1.1, 1.1, "amber", z=0.005)       # where the robot really is


def robot(name, y, colour=None, ghost=None):
    root, _ = kit.rover(name, colour or "grey")
    root.scale = (RS,) * 3
    root.location = (X0, y, 0)
    if ghost:
        for ob in root.children_recursive:
            if ob.type == "MESH":
                ob.data.materials.clear()
                ob.data.materials.append(ghost)
    return root


robot("real", 0.0, "green")
est_a = robot("accel", 0.78, ghost=kit.ghost("blue", 0.5))       # accelerometer bias integrated twice
est_g = robot("gyro", -0.78, ghost=kit.ghost("amber", 0.6))      # gyro bias, leaked into position through gravity
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / DT), N - 1)
    kit.key(est_a, f, loc=(X0 + pos_acc[i], 0.78, 0))
    kit.key(est_g, f, loc=(X0 + pos_gyr[i], -0.78, 0))
kit.camera((0.05, -3.4, 2.3), (0.05, 0.05, 0.15), lens=34)
kit.render(__file__)
