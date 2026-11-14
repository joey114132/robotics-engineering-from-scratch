# 레슨 09/02 예시 클립: 같은 노드(11번)에서 시작하는 RRT 걸음 두 번, 11번째 반복은 바위 안에서 끝나 버려지고(빨강) 17번째 반복은 비어 있어 남는다(초록)
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, FPS, STEP, SECONDS = 2.0, 24, 0.4, 5.0                         # 1 lesson unit drawn as 2 m: a close-up of node 11, so one step is two rover widths (the lead clip draws 0.4 m)
ROCK, RR = np.array([5.0, 5.0]), 2.0                              # the demo's big rock
nodes, parent, _ = m.rrt([1, 1], np.array([9.0, 9.0]), [(ROCK, RR), (np.array([3.0, 7.5]), 1.2), (np.array([7.5, 3.0]), 1.2)], (np.zeros(2), np.full(2, 10.0)))
rng = np.random.default_rng(0)                                    # replay the lesson's random draws to get its samples back
draws = [np.array([9.0, 9.0]) if rng.random() < 0.1 else rng.uniform(np.zeros(2), np.full(2, 10.0)) for _ in range(18)]
NB, S1, S2 = nodes[11], draws[11], draws[17]                      # iterations 11 and 17 both pull node 11
RED, GREEN = "#d3101c", "#12a050"                                   # saturated, so they read at phone width
unit = lambda v: v / np.linalg.norm(v)
new1 = NB + unit(S1 - NB) * STEP
new2 = NB + unit(S2 - NB) * STEP
k2 = int(np.argmin(np.linalg.norm(nodes - new2, axis=1)))         # the node that step 17 added
assert np.allclose(nodes[k2], new2) and not m.seg_free(NB, new1, [(ROCK, RR)]) and m.seg_free(NB, new2, [(ROCK, RR)])
w = lambda p, z=0.28: (S * (p[0] - 3.3), S * (p[1] - 4.3), z)         # paths float above the rock's top so they stay visible


def vis(ob, on, off=None):
    for f, hidden in ((1, True), (on, False), (off, True)):
        if f:
            ob.hide_render = hidden
            ob.keyframe_insert("hide_render", frame=f)


def pull(sample, on, off, length):                                 # an amber arrow from node 11 toward the sample, which lies off the picture
    ar = kit.arrow("pull", "amber", shaft=0.03)
    ar.rotation_euler = (0, 0, math.atan2(*(sample - NB)[::-1]))
    ar.scale = (length, 1, 1)
    ar.location = w(NB, 0.28)
    vis(ar.children[0], int(on * FPS), int(off * FPS))
    vis(ar.children[1], int(on * FPS), int(off * FPS))


def mark(ob, on, off=None):
    vis(ob, int(on * FPS), int(off * FPS) if off else None)


sc = kit.setup(SECONDS)
kit.stripe(-4.0, 4.0, -2.5, 2.5, "pearl")
kit.cyl("rock", RR * S, 0.22, (*w(ROCK)[:2], 0.11), "z", "dark", bevel=0.02, segments=64)
kit.cyl("rock-top", RR * S * 0.94, 0.02, (*w(ROCK)[:2], 0.23), "z", "grey", segments=64)   # a lighter top, so the rock reads as a solid boulder
for i in range(1, 12):                                            # the tree as it stands at iteration 11
    kit.tube("edge", [w(nodes[parent[i]]), w(nodes[i])], 0.02, "grey")
kit.ball("node-11", 0.05, w(NB), "grey")
pull(S1, 0.3, 3.6, 2.2)
pull(S2, 1.9, 3.6, 1.5)
mark(kit.tube("try-1", [w(NB), w(new1)], 0.03, "amber"), 0.7, 1.2)                # a candidate step is amber until it is judged
mark(kit.tube("bad-edge", [w(NB), w(new1)], 0.03, RED), 1.2, 3.9)               # ends inside the rock: dropped
mark(kit.ball("bad-step", 0.12, w(new1, 0.7), RED), 1.2, 3.9)
mark(kit.cyl("bad-pole", 0.02, 0.8, (*w(new1)[:2], 0.4), "z", RED, segments=12), 1.2, 3.9)
mark(kit.tube("try-2", [w(NB), w(new2)], 0.03, "amber"), 2.3, 2.8)
mark(kit.tube("edge-new", [w(NB), w(new2)], 0.04, GREEN), 2.8)                  # clear: kept
mark(kit.ball("node-new", 0.12, w(new2), GREEN), 2.8)
mark(kit.cyl("good-pole", 0.02, 0.8, (*w(new2)[:2], 0.4), "z", GREEN, segments=12), 2.8, 3.9)
mark(kit.ball("good-top", 0.12, w(new2, 0.7), GREEN), 2.8, 3.9)

rover, wheels = kit.rover("rover", "green")
rover.scale = (1.0, 1.0, 1.0)
yaw1, yaw2 = math.atan2(*(S1 - NB)[::-1]), math.atan2(*(S2 - NB)[::-1])
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    a = float(np.clip((t - 2.8) / 0.7, 0, 1))                     # the kept step is driven from 2.8 s to 3.5 s
    turn = float(np.clip((t - 1.9) / 0.4, 0, 1))
    p = NB + a * (new2 - NB)
    kit.key(rover, f, loc=(*w(p)[:2], 0), rot=(0, 0, yaw1 + turn * (yaw2 - yaw1)))
    for wh in wheels:
        kit.key(wh, f, rot=(0, a * STEP * S / 0.0375, 0))
kit.camera((0.25, -1.6, 5.4), (0.25, 0.1, 0), lens=40)
kit.render(__file__)
