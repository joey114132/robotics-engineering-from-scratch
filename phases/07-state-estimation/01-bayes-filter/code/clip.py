# 레슨 07/01 클립: 고리 복도를 도는 로봇 한 대와, 센서를 쓴 belief(초록 기둥)와 모션만 쓴 belief(파란 기둥)의 높이 비교
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
STEPS, SECONDS, H, RS, RL = 25, 5.5, 0.9, 1.5, 1.55                      # lesson's 25 moves; a bar of height H m means probability 1
moves = [1] * STEPS
truth, zs = m.simulate(m.DOORS, 7, moves, np.random.default_rng(2))
start = np.zeros(m.N)
start[7] = 1.0                                        # both filters start sure of the cell, as in the lesson's dead-reckoning figure
b_filter = m.run(m.DOORS, zs, moves, bel0=start)      # motion + sensor
b_motion = m.run(m.DOORS, zs, moves, use_update=False, bel0=start)  # motion only
ang = np.unwrap(np.array([7] + truth) * 2 * math.pi / m.N)   # where the robot is, as an angle on the ring

sc = kit.setup(SECONDS)


def at(r, i, z=0.0):
    return (r * math.cos(2 * math.pi * i / m.N), r * math.sin(2 * math.pi * i / m.N), z)


bars = {}
for i in range(m.N):
    yaw = 2 * math.pi * i / m.N + math.pi / 2
    lane = kit.box("lane", (0.55, 0.76, 0.004), at(RL, i, 0.002), "road", bevel=0)
    lane.rotation_euler = (0, 0, yaw)
    for p in lane.data.polygons:
        p.use_smooth = False
    wall = kit.box("wall", (0.44, 0.08, 0.28 if m.DOORS[i] else 0.1), at(RL - 0.42, i, 0.14 if m.DOORS[i] else 0.05), "amber" if m.DOORS[i] else "grey", bevel=0.01)
    wall.rotation_euler = (0, 0, yaw)
    for tag, r, colour in (("f", RL + 0.6, "green"), ("m", RL - 0.95, "blue")):
        root = kit.empty(f"bar-{tag}{i}", at(r, i), None)
        root.rotation_euler = (0, 0, yaw)
        b = kit.box("bar", (0.3 if tag == "f" else 0.15, 0.24 if tag == "f" else 0.15, 1.0), (0, 0, 0.5), colour, bevel=0, parent=root)
        for p in b.data.polygons:
            p.use_smooth = False
        bars[tag, i] = root

rover, wheels = kit.rover("robot", "navy")
rover.scale = (RS,) * 3
for f in range(sc.frame_start, sc.frame_end + 1):
    s = min((f - 1) / (24 * 5.0) * STEPS, STEPS - 1e-6)   # 25 moves in 5 s, then hold
    k, w = int(s), s - int(s)
    th = ang[k] * (1 - w) + ang[k + 1] * w
    kit.key(rover, f, loc=(RL * math.cos(th), RL * math.sin(th), 0), rot=(0, 0, th + math.pi / 2))
    for wh in wheels:
        kit.key(wh, f, rot=(0, RL * th / (0.075 * RS), 0))
    for (tag, i), root in bars.items():
        bel = b_filter if tag == "f" else b_motion
        root.scale = (1, 1, max(H * (bel[k][i] * (1 - w) + bel[k + 1][i] * w), 0.004))
        root.keyframe_insert("scale", frame=f)
kit.camera((0, -5.4, 5.2), (0, -0.55, 0.3), lens=34)
kit.render(__file__)
