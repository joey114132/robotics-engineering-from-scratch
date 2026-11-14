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
groups = {"nominal": (m.tune(0.0, 1, 1), -0.52, "blue"), "randomised": (m.tune(0.3, 60, 1), 0.52, "green")}
runs = {k: m.simulate(P, np.full(N, g[0]), np.full(N, g[1])) for k, (g, _, _) in groups.items()}
ok = {k: m.score(q)[0] for k, q in runs.items()}
print("success", {k: int(v.sum()) for k, v in ok.items()})

sc = kit.setup(SIM * SLOW)
kit.box("wall", (4.8, 0.05, 1.7), (0, 0.16, 0.85), kit.mat("floor", rough=0.9, emit=0.2), bevel=0.01)
ghosts = {"blue": kit.ghost("blue", 0.4), "green": kit.ghost("green", 0.4), "red": kit.ghost("red", 0.6)}


def joint(name, x, y, colour):
    root, (j,) = kit.arm(name, (0.4,), "blue")
    for o in list(root.children):                                       # a pendulum that hangs from its motor, no pedestal
        if o.name.startswith((name + "-foot", name + "-post")):
            bpy.data.objects.remove(o)
    root.location = (x, y, 0.65)
    for o in root.children_recursive:
        if o.type == "MESH":
            o.data.materials.clear()
            o.data.materials.append(ghosts[colour])
    return j


arms = []
for k, (_, x, col) in groups.items():
    kit.ball("target-" + k, 0.035, (x + 0.54 * np.cos(m.REF - 1.5708), -0.03, 0.95 + 0.54 * np.sin(m.REF - 1.5708)), "amber")   # where the step should end
    arms += [(k, n, joint(f"{k}{n}", x, 0.004 * n + (0 if ok[k][n] else 0.05), col if ok[k][n] else "red")) for n in range(N)]
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / m.DT), len(runs["nominal"]) - 1)
    for k, n, j in arms:
        q = runs[k][i, n]
        kit.pose([j], f, [q + (OVER - 1) * max(q - m.REF, 0.0) - 1.5708])
kit.camera((0.28, -2.0, 1.45), (0.28, 0, 0.88), lens=38)
kit.render(__file__)
