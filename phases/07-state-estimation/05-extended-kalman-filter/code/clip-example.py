# 레슨 07/05 예시 클립: heading 을 1 rad 틀리게 시작한 같은 로봇이 기둥 하나만 볼 때(파랑)는 EKF 추정이 멀어지는데도 작은 원(2 sigma)을 믿고, 기둥 넷을 볼 때(초록)는 로봇 위에 겹친다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
STEPS, RATE, RS, OFFSET, DS = 80, 1.5, 1.8, 1.0, 0.5
RING = [(math.cos(a), math.sin(a), 0.0) for a in np.linspace(0, 2 * math.pi, 49)]   # a unit circle, scaled to the 2-sigma radius     # 80 steps of 0.1 s at 1.5x; heading 1 rad wrong; 1 m drawn as 0.5 m
runs = {"blue": (-2.75, m.LMS[:1]), "green": (2.65, m.LMS)}          # one post, then all four
sc = kit.setup(5.5)
kit.stripe(-5.6, 5.6, -3.2, 2.6, "road")


def world(cx, p, z=0.0):
    return (cx + DS * p[0], DS * (p[1] - 3.3), z)


rig = {}
for colour, (cx, lms) in runs.items():
    tr, ek, _, Ps = m.run(np.random.default_rng(0), STEPS, OFFSET, lms)
    kit.tube("track", [world(cx, p, 0.012) for p in tr], 0.03, "grey")
    for lm in lms:
        kit.cyl("post", 0.06, 0.6, world(cx, lm, 0.3), "z", "dark")
        kit.ball("post-top", 0.1, world(cx, lm, 0.65), "amber")
    real, _ = kit.rover("real", "grey")
    est, _ = kit.rover("ekf", colour)
    for root, ghost, grow in ((real, None, 1.0), (est, kit.ghost(colour, 0.85), 1.2)):
        root.scale = (RS * grow,) * 3
        for ob in root.children_recursive if ghost else []:
            if ob.type == "MESH":
                ob.data.materials.clear()
                ob.data.materials.append(ghost)
    disc = kit.tube("two-sigma", RING, 0.09, "white")                 # the filter's own 2 sigma: a bright opaque ring held above the ghost
    rays = []
    for _ in lms:
        r = kit.empty("ray")
        kit.cyl("ray", 0.01, 1.0, (0.5, 0, 0), "x", "amber", parent=r, segments=8)
        rays.append(r)
    rig[colour] = (cx, lms, tr, ek, Ps, real, est, disc, rays)

for f in range(sc.frame_start, sc.frame_end + 1):
    s = min((f - 1) / sc.render.fps * RATE / m.DT, STEPS - 1e-6)
    k, w = int(s), s - int(s)
    for colour, (cx, lms, tr, ek, Ps, real, est, disc, rays) in rig.items():
        for ob, path in ((real, tr), (est, ek)):
            p = path[k] * (1 - w) + path[k + 1] * w
            kit.key(ob, f, loc=world(cx, p), rot=(0, 0, p[2]))
        pe = ek[k] * (1 - w) + ek[k + 1] * w
        r2 = 2 * float(np.sqrt(np.linalg.eigvalsh(Ps[k][:2, :2]).max())) * DS
        kit.key(disc, f, loc=world(cx, pe, 0.45))
        disc.scale = (r2, r2, 1)
        disc.keyframe_insert("scale", frame=f)
        p = tr[k] * (1 - w) + tr[k + 1] * w
        for ray, lm in zip(rays, lms):
            d = lm - p[:2]
            dist = float(np.hypot(*d))
            kit.key(ray, f, loc=world(cx, p, 0.05), rot=(0, 0, math.atan2(d[1], d[0])))
            ray.scale = (dist * DS if dist < 8.0 else 0.001, 1, 1)
            ray.keyframe_insert("scale", frame=f)
kit.camera((0, -3.4, 8.8), (0, 0.2, 0), lens=30)
kit.render(__file__)
