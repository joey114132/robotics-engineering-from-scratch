# 레슨 07/01 예시 클립: 위치를 전혀 모르는 로봇(평평한 belief)이 문 신호 하나, 이동, 신호 하나씩 받으며 초록 기둥을 한 칸에 모으는 과정
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
STEPS, SECONDS, H, RS, RL, START = 5, 5.8, 1.7, 1.5, 1.55, 7     # a bar of height H m means probability 1; the robot really starts at cell 7
cells = [(START + k) % m.N for k in range(STEPS + 1)]               # it moves one cell at a time and every reading is correct
reads = [int(m.DOORS[c]) for c in cells]
beliefs = [np.full(m.N, 1 / m.N)]                                    # know nothing: all 20 cells equally likely
phases = []                                                          # (start s, end s, from belief, to belief, rover cell from, to, lamp)
t = 0.4
post = m.update(beliefs[0], reads[0])
phases.append((t, t + 0.5, beliefs[0], post, cells[0], cells[0], reads[0]))
t += 0.5
for k in range(1, STEPS + 1):
    pred = m.predict(post, 1)
    phases.append((t, t + 0.45, post, pred, cells[k - 1], cells[k], None))
    post = m.update(pred, reads[k])
    phases.append((t + 0.45, t + 0.85, pred, post, cells[k], cells[k], reads[k]))
    t += 0.85

sc = kit.setup(SECONDS)


def at(r, i, z=0.0):
    return (r * math.cos(2 * math.pi * i / m.N), r * math.sin(2 * math.pi * i / m.N), z)


bars = []
for i in range(m.N):
    yaw = 2 * math.pi * i / m.N + math.pi / 2
    lane = kit.box("lane", (0.55, 0.76, 0.004), at(RL, i, 0.002), "road", bevel=0)
    lane.rotation_euler = (0, 0, yaw)
    wall = kit.box("wall", (0.44, 0.08, 0.28 if m.DOORS[i] else 0.1), at(RL - 0.42, i, 0.14 if m.DOORS[i] else 0.05), "amber" if m.DOORS[i] else "grey", bevel=0.01)
    wall.rotation_euler = (0, 0, yaw)
    root = kit.empty(f"bar{i}", at(RL + 0.6, i))
    root.rotation_euler = (0, 0, yaw)
    b = kit.box("bar", (0.3, 0.24, 1.0), (0, 0, 0.5), "green", bevel=0, parent=root)
    for p in b.data.polygons:
        p.use_smooth = False
    bars.append(root)

rover, wheels = kit.rover("robot", "navy")
rover.scale = (RS,) * 3
lamps = {1: kit.ball("seen-door", 0.12, (0, 0, 0.62), "amber", parent=rover), 0: kit.ball("seen-wall", 0.12, (0, 0, 0.62), "grey", parent=rover)}


def ease(u):
    return u * u * (3 - 2 * u)


for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps
    bel, cell, lamp = beliefs[0], float(cells[0]), None
    for a, b, b0, b1, c0, c1, lm in phases:
        if t >= b:
            bel, cell, lamp = b1, float(c1), lm
        elif t >= a:
            w = ease((t - a) / (b - a))
            bel, cell, lamp = b0 * (1 - w) + b1 * w, c0 + (c1 - c0) * w, lm
            break
    th = 2 * math.pi * cell / m.N
    kit.key(rover, f, loc=(RL * math.cos(th), RL * math.sin(th), 0), rot=(0, 0, th + math.pi / 2))
    for wh in wheels:
        kit.key(wh, f, rot=(0, RL * th / (0.075 * RS), 0))
    for i, root in enumerate(bars):
        root.scale = (1, 1, max(H * float(bel[i]), 0.004))
        root.keyframe_insert("scale", frame=f)
    for key_, lamp_ob in lamps.items():
        lamp_ob.scale = (1,) * 3 if lamp == key_ else (0.001,) * 3
        lamp_ob.keyframe_insert("scale", frame=f)
kit.camera((0, -5.6, 5.4), (0, -0.55, 0.6), lens=42)
kit.render(__file__)
