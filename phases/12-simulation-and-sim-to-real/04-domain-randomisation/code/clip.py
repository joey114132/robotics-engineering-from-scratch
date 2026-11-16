# 레슨 12/04 클립: 같은 PD gain으로 무작위 관절 12개를 1 rad로 움직인다. 왼쪽은 nominal에서 맞춘 gain(파랑), 오른쪽은 폭 0.3에서 맞춘 gain(초록), 실패한 관절은 빨강
import pathlib
import sys

import bpy
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
N, SIM, SLOW, OVER = 12, 1.6, 3.0, 6.0                                  # 12 random plants of width 0.3, first 1.6 s at 1/3 speed, overshoot past the target drawn 6 times larger
P = m.sample(0.3, N, np.random.default_rng(0))
groups = {"nominal": (m.tune(0.0, 1, 1), -1.15, "#4f8df0"), "randomised": (m.tune(0.3, 60, 1), 1.15, "#2f9e62")}
runs = {k: m.simulate(P, np.full(N, g[0]), np.full(N, g[1])) for k, (g, _, _) in groups.items()}
ok = {k: m.score(q)[0] for k, q in runs.items()}
print("success", {k: int(v.sum()) for k, v in ok.items()})

sc = kit.setup(SIM * SLOW)
kit.box("wall", (7.0, 0.05, 3.0), (0.15, 0.3, 1.5), kit.mat("floor", rough=0.9, emit=0.2), bevel=0.01)
COLS, DX, DZ = 4, 0.47, 0.6                                             # each group is a 4 x 3 grid: twelve separate arms that can be counted


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
        arms.append((k, n, joint(f"{k}{n}", x, z, col if ok[k][n] else "#d9541e")))   # a failing joint is red from the start to the end
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / m.DT), len(runs["nominal"]) - 1)
    for k, n, j in arms:
        q = runs[k][i, n]
        kit.pose([j], f, [q + (OVER - 1) * max(q - m.REF, 0.0) - 1.5708])
kit.camera((0.15, -4.9, 1.3), (0.15, 0, 1.25), lens=38)
kit.render(__file__)
