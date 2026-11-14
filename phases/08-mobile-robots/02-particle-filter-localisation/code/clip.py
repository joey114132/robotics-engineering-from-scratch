# 레슨 08/02 클립: 알려진 기둥 네 개와 거리 측정만으로 로버의 위치를 찾는 particle 구름이 한 점으로 모인다
import pathlib
import sys

import bpy
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, STEPS, SHOWN = 0.25, 40, 4                                   # drawing scale 1 m -> 0.25 m; every 4th of 1000 particles is drawn
rng, rz = np.random.default_rng(0), np.random.default_rng(100)
truth = np.array([[2.0, 3.0, 0.3]])
P = np.column_stack([rng.uniform(0, 10, (1000, 2)), rng.uniform(-np.pi, np.pi, 1000)])
frames = [(P.copy(), truth.copy())]                           # the lesson's own filter: move, weigh by ranges, resample
for _ in range(STEPS):
    truth = m.move(truth, 0.8, 0.15, 0.1)
    z = m.ranges(truth)[0] + rz.normal(0, 0.3, 4)
    P = m.pf_step(P, 0.8, 0.15, 0.1, z, 0.3, rng)
    frames.append((P.copy(), truth.copy()))
when = np.cumsum([12] + [6] * 6 + [2] * (STEPS - 6))             # frame of each step: the first six are slowed so the collapse is visible

sc = kit.setup(when[-1] / 24 + 0.8)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
for (a, b), (c, d) in (((0, 0), (10, 0)), ((10, 0), (10, 10)), ((10, 10), (0, 10)), ((0, 10), (0, 0))):
    kit.stripe(min(a, c) * S - 0.02, max(a, c) * S + 0.02, min(b, d) * S - 0.02, max(b, d) * S + 0.02, "road")
for x, y in m.LANDMARKS * S:
    kit.cyl("post", 0.03, 0.34, (x, y, 0.17), "z", "dark")
    kit.ball("post-top", 0.05, (x, y, 0.37), "amber")
root, wheels = kit.rover("truth", "blue")
root.scale = (0.55,) * 3
mark = kit.cyl("proto", 0.014, 0.26, (0, 0, 0.13), "z", "navy", segments=8)   # one particle: a thin post standing on its position
dots = [bpy.data.objects.new("p", mark.data) for _ in range(1000 // SHOWN)]
for d in dots:
    bpy.context.scene.collection.objects.link(d)
mark.hide_render = True
est = kit.ball("estimate", 0.05, (0, 0, 0.36), "green")
lines = [kit.cyl("range", 0.005, 1.0, (0, 0, 0.1), "x", "sky") for _ in range(4)]
for f, (Pk, tk) in zip(when, frames):
    kit.key(root, int(f), loc=(*(tk[0, :2] * S), 0), rot=(0, 0, tk[0, 2]))
    for d, (x, y, th) in zip(dots, Pk[::SHOWN]):
        kit.key(d, int(f), loc=(x * S, y * S, 0.13))
    e = m.estimate(Pk)
    kit.key(est, int(f), loc=(e[0] * S, e[1] * S, 0.36))
    for ln, lm in zip(lines, m.LANDMARKS * S):
        v = lm - tk[0, :2] * S
        ln.location, ln.rotation_euler, ln.scale = (*(tk[0, :2] * S + v / 2), 0.1), (0, 0, float(np.arctan2(v[1], v[0]))), (float(np.hypot(*v)), 1, 1)
        for p in ("location", "rotation_euler", "scale"):
            ln.keyframe_insert(p, frame=int(f))
kit.camera((1.25, -1.9, 3.3), (1.25, 1.2, 0.0), lens=34)
kit.render(__file__)
