# 레슨 07/03 예시 클립: 가만히 선 로봇을 gyro 가 점점 기울었다고 믿어서(호박색 유령) 중력의 가짜 옆 성분(빨간 화살표)이 생기고 유령이 비탈을 구르듯 미끄러진다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
DT, N, BG, RS, X0 = 0.01, 1000, 0.01, 1.7, -0.85               # the lesson's gyro bias 0.01 rad/s, 10 s run
RATE, DRAW, TILT_X, ARROW = 2.0, 0.10, 5.0, 0.3               # 10 s played in 5 s; 1 m drawn as 0.1 m; tilt drawn 5 times larger; 1 m/s^2 drawn as 0.3 m
t = DT * np.arange(1, N + 1)
tilt = BG * t                                                   # the estimated tilt, b t
fake_a = m.G * np.sin(tilt)                                     # gravity read as a sideways acceleration
pos = m.leaked_position(BG, N, DT)

sc = kit.setup(5.5)
kit.stripe(-1.3, 1.9, -0.8, 0.8, "road")
for x in np.arange(-0.85, 1.9, 0.4):
    kit.stripe(x - 0.01, x + 0.01, -0.8, 0.8, "white", z=0.004)    # a mark every 4 m of estimated travel
kit.stripe(X0 - 0.02, X0 + 0.02, -0.8, 0.8, "amber", z=0.005)       # where the robot really is


def robot(name, colour=None, ghost=None):
    root, _ = kit.rover(name, colour or "grey")
    root.scale = (RS,) * 3
    root.location = (X0, 0, 0)
    if ghost:
        for ob in root.children_recursive:
            if ob.type == "MESH":
                ob.data.materials.clear()
                ob.data.materials.append(ghost)
    return root


robot("real", "green")
est = robot("estimate", ghost=kit.ghost("amber", 0.6))
push = kit.arrow("fake-push", "red", shaft=0.03)
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps * RATE / DT), N - 1)
    kit.key(est, f, loc=(X0 + pos[i] * DRAW, 0, 0), rot=(0, TILT_X * float(tilt[i]), 0))
    kit.key(push, f, loc=(X0 + pos[i] * DRAW + 0.45, -0.6, 0.3))
    push.scale = (max(ARROW * float(fake_a[i]), 0.001), 1, 1)
    push.keyframe_insert("scale", frame=f)
kit.camera((0.35, -3.2, 2.0), (0.35, 0.0, 0.15), lens=36)
kit.render(__file__)
