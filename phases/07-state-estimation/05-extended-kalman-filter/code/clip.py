# 레슨 07/05 클립: 원을 도는 실제 로봇(회색), 랜드마크로 보정하는 EKF 추정(초록 유령), 보정 없는 dead reckoning(파란 유령)
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
LMS = m.LMS[:3]                                  # the first three landmarks
STEPS, RATE, RS, OFFSET = 80, 1.5, 2.4, 0.6      # 80 steps of 0.1 s played at 1.5x; the filter starts 0.6 rad wrong about its heading
tr, ek, dr, _ = m.run(np.random.default_rng(3), STEPS, OFFSET, LMS)

sc = kit.setup(5.5)
kit.tube("track", [(p[0], p[1], 0.012) for p in tr], 0.05, "road")
for x, y in LMS:
    kit.cyl("landmark", 0.1, 0.9, (x, y, 0.45), "z", "dark")
    kit.ball("landmark-top", 0.16, (x, y, 0.95), "amber")


def robot(name, colour, ghost=None, grow=1.0):
    root, wheels = kit.rover(name, colour)
    root.scale = (RS * grow,) * 3
    for ob in root.children_recursive if ghost else []:
        if ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(ghost)
    return root


real, est, dead = robot("real", "grey"), robot("ekf", "green", kit.ghost("green", 0.55), 1.12), robot("dead", "blue", kit.ghost("blue", 0.5))
rays = []
for i in range(len(LMS)):
    root = kit.empty(f"ray{i}")
    kit.cyl("ray", 0.012, 1.0, (0.5, 0, 0), "x", "amber", parent=root, segments=8)
    rays.append(root)

for f in range(sc.frame_start, sc.frame_end + 1):
    s = min((f - 1) / sc.render.fps * RATE / m.DT, STEPS - 1e-6)
    k, w = int(s), s - int(s)
    for ob, path in ((real, tr), (est, ek), (dead, dr)):
        p = path[k] * (1 - w) + path[k + 1] * w
        kit.key(ob, f, loc=(p[0], p[1], 0), rot=(0, 0, p[2]))
    p = tr[k] * (1 - w) + tr[k + 1] * w
    for ray, lm in zip(rays, LMS):
        d = lm - p[:2]
        r = float(np.hypot(*d))
        kit.key(ray, f, loc=(p[0], p[1], 0.05), rot=(0, 0, math.atan2(d[1], d[0])))
        ray.scale = (r if r < 8.0 else 0.001, 1, 1)
        ray.keyframe_insert("scale", frame=f)
kit.camera((0, -7.0, 12.6), (0, 2.5, 0), lens=38)
kit.render(__file__)
