# 레슨 12/04 예시 클립: 같은 무작위 관절 12개에 폭 0.3 에서 맞춘 gain(초록)과 폭 0.6 에서 맞춘 gain(파랑)을 준다. 둘 다 도착하지만 넓게 맞춘 쪽이 늦다
import pathlib
import sys

import bpy
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
N, SIM, SLOW = 12, 0.75, 7.0                                           # the same 12 random plants of width 0.3, the first 0.75 s at 1/7 speed
P = m.sample(0.3, N, np.random.default_rng(0))
groups = {"wide": (m.tune(0.6, 40, 1), -1.15, "#4f8df0"), "matched": (m.tune(0.3, 60, 1), 1.15, "#2f9e62")}
runs = {k: m.simulate(P, np.full(N, g[0]), np.full(N, g[1])) for k, (g, _, _) in groups.items()}
ok = {k: m.score(q) for k, q in runs.items()}
print("success", {k: int(v[0].sum()) for k, v in ok.items()}, "mean settle s", {k: float(v[1].mean().round(3)) for k, v in ok.items()}, "settled by 0.5 s", {k: int((v[1] <= 0.5).sum()) for k, v in ok.items()})

sc = kit.setup(SIM * SLOW)
kit.box("wall", (7.0, 0.05, 3.0), (0.15, 0.3, 1.5), kit.mat("floor", rough=0.9, emit=0.2), bevel=0.01)
COLS, DX, DZ = 4, 0.47, 0.6                                             # each group is a 4 x 3 grid: twelve separate arms that can be counted
lamp_on = kit.mat("white", emit=1.5)


def joint(name, x, z, colour):
    root, (j,) = kit.arm(name, (0.4,), colour)
    for o in list(root.children):                                       # a pendulum that hangs from its motor: drop the pedestal, its flange and bolts, keep only the joint
        if o is not j:
            bpy.data.objects.remove(o)
    root.location = (x, 0.0, z - 0.3)                                   # the motor sits 0.3 m above the root
    return j


arms = []
for k, (_, gx, col) in groups.items():
    for n in range(N):
        x, z = gx + (n % COLS - (COLS - 1) / 2) * DX, 1.9 - (n // COLS) * DZ
        kit.ball(f"target-{k}{n}", 0.045, (x + 0.54 * np.cos(m.REF - 1.5708), -0.03, z + 0.54 * np.sin(m.REF - 1.5708)), "amber")   # where the step should end
        arms.append((k, n, joint(f"{k}{n}", x, z, col)))
        lamp = kit.ball(f"settled-{k}{n}", 0.07, (x, -0.06, z + 0.19), lamp_on)   # a white lamp over the arm that lights at the arm's own settle time, from the lesson's score()
        f_on = 1 + ok[k][1][n] * SLOW * sc.render.fps
        for f, v in ((1, 1e-3), (int(f_on), 1e-3), (int(f_on) + 3, 1.0)):
            lamp.scale = (v,) * 3
            lamp.keyframe_insert("scale", frame=f)
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / m.DT), len(runs["wide"]) - 1)
    for k, n, j in arms:
        kit.pose([j], f, [runs[k][i, n] - 1.5708])
kit.camera((0.15, -4.9, 1.3), (0.15, 0, 1.25), lens=38)
kit.render(__file__)
