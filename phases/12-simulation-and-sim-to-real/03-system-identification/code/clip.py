# 레슨 12/03 클립: 놓아 준 관절의 실제 낙하(단색 팔)와 기록으로 맞춘 모델의 예측(유령 팔). 왼쪽은 느린 한 번의 기록, 오른쪽은 풍부한 기록으로 맞춘 모델
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SIM, SLOW, Q0 = 0.85, 5.5, 1.2                                        # coast test: released at 1.2 rad with no torque, 0.85 s shown at 1/5.5 speed
est = {a: m.fit(m.record(m.experiment(a), 0.01, 1e-4, 1))[0] for a in (0.0, 1.0)}   # the lesson's fit of the slow run (a=0) and the rich run (a=1)
coast = lambda p: m.run(p, lambda t, q, w: 0.0, SIM, (Q0, 0.0, 0.0))[:, 2]
real = coast(m.TRUE)
model = {a: coast(e) for a, e in est.items()}

sc = kit.setup(SIM * SLOW)
kit.box("wall", (4.8, 0.05, 1.7), (0, 0.16, 0.85), kit.mat("floor", rough=0.9, emit=0.2), bevel=0.01)


def joint(name, x, y, colour, ghosted):
    root, (j,) = kit.arm(name, (0.4,), colour)
    for o in list(root.children):                                       # a pendulum that hangs from its motor, no pedestal
        if o.name.startswith((name + "-foot", name + "-post")):
            bpy.data.objects.remove(o)
    root.location = (x, y, 0.65)
    if ghosted:
        g = kit.ghost("dark", 0.5)
        for o in root.children_recursive:
            if o.type == "MESH":
                o.data.materials.clear()
                o.data.materials.append(g)
    return j


pairs = {0.0: (-0.52, "blue"), 1.0: (0.52, "green")}
rigs = {a: (joint(f"real{a}", x, 0.07, c, False), joint(f"model{a}", x, 0.0, "dark", True)) for a, (x, c) in pairs.items()}
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / m.DT), len(real) - 1)
    for a, (jr, jm) in rigs.items():
        kit.pose([jr], f, [real[i] - 1.5708])                           # q is measured from hanging straight down
        kit.pose([jm], f, [model[a][i] - 1.5708])
kit.camera((0, -2.3, 1.55), (0, 0, 0.95), lens=38)
kit.render(__file__)
