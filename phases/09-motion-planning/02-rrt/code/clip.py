# 레슨 09/02 클립: RRT 트리가 자라고 경로가 잡힌 뒤 shortcut 으로 곧게 펴지면, 탐사 로봇이 그 경로를 따라 간다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, PAD, FPS = 0.4, 0.3, 24                                       # 1 lesson unit drawn as 0.4 m; obstacles grown by the rover's radius for planning
OBS = [(np.array([5.0, 5.0]), 2.0), (np.array([3.0, 7.5]), 1.2), (np.array([7.5, 3.0]), 1.2)]
nodes, parent, path = m.rrt(np.array([1.0, 1.0]), np.array([9.0, 9.0]), [(c, r + PAD) for c, r in OBS], (np.zeros(2), np.full(2, 10.0)), seed=0)
short = m.shortcut(path, [(c, r + PAD) for c, r in OBS], seed=0)
w = lambda p, z=0.03: (S * (p[0] - 5), S * (p[1] - 5), z)         # lesson plane -> floor
T_GROW, T_RAW, T_SHORT, T_GO, SECONDS = 0.3, 1.9, 2.7, 3.0, 5.8


def appear(ob, frame):
    ob.hide_render = True
    ob.keyframe_insert("hide_render", frame=1)
    ob.hide_render = False
    ob.keyframe_insert("hide_render", frame=frame)


sc = kit.setup(SECONDS)
kit.stripe(-2.1, 2.1, -2.1, 2.1, "pearl")
for c, r in OBS:
    kit.cyl("rock", r * S, 0.24, (*w(c)[:2], 0.12), "z", "dark", bevel=0.01, segments=64)
kit.cyl("goal", 0.1, 0.01, (*w((9, 9))[:2], 0.01), "z", "amber")
kit.ball("goal-flag", 0.06, (*w((9, 9))[:2], 0.3), "amber")
kit.cyl("goal-pole", 0.01, 0.3, (*w((9, 9))[:2], 0.15), "z", "amber")
for i in range(1, len(nodes)):                                    # the tree: one thin grey edge per node, shown in growth order
    appear(kit.tube("edge", [w(nodes[parent[i]]), w(nodes[i])], 0.007, "grey"), int(1 + (T_GROW + (T_RAW - 0.2 - T_GROW) * i / len(nodes)) * FPS))
appear(kit.tube("raw", [w(p, 0.04) for p in path], 0.016, "blue"), int(T_RAW * FPS))
appear(kit.tube("short", [w(p, 0.06) for p in short], 0.02, "green"), int(T_SHORT * FPS))

rover, wheels = kit.rover("rover", "green")
rover.scale = (0.5, 0.5, 0.5)
P = np.array([w(p)[:2] for p in short])
seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
yaw = math.atan2(*(P[1] - P[0])[::-1])
for f in range(sc.frame_start, sc.frame_end + 1):
    s = np.clip(((f - 1) / FPS - T_GO) / (SECONDS - 0.4 - T_GO), 0, 1) * seg.sum()   # distance driven, constant speed
    k = min(int(np.searchsorted(np.cumsum(seg), s)), len(seg) - 1)
    u = (s - (np.cumsum(seg) - seg)[k]) / seg[k]
    pos = P[k] + u * (P[k + 1] - P[k])
    want = math.atan2(*(P[k + 1] - P[k])[::-1])
    yaw += max(-0.2, min(0.2, (want - yaw + math.pi) % (2 * math.pi) - math.pi))   # turn toward the segment, at most 0.2 rad a frame
    kit.key(rover, f, loc=(pos[0], pos[1], 0), rot=(0, 0, yaw))
    for wh in wheels:
        kit.key(wh, f, rot=(0, s / 0.0375, 0))
kit.camera((0, -5.4, 4.7), (0, 0.1, 0), lens=40)
kit.render(__file__)
