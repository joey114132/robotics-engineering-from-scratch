# 레슨 12/01 클립: 같은 토크 명령을 받는 벽걸이 관절. 단색 팔은 마찰·모터 지연이 있는 실제, 유령 팔은 그것들을 뺀 시뮬
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS = 5.5                                                         # the first 5.5 s of the lesson's run, real time
real = m.simulate(m.REAL, m.command, SECONDS)[:, 0]                   # friction and motor lag (the sensor delay shifts only the reported angle, so it is not drawn)
sim = m.simulate({**m.REAL, "b": 0.0, "c": 0.0, "Tm": 0.0, "delay": 0.0}, m.command, SECONDS)[:, 0]   # none of them

sc = kit.setup(SECONDS)
kit.box("wall", (4.4, 0.05, 1.7), (0, 0.16, 0.85), kit.mat("floor", rough=0.9, emit=0.2), bevel=0.01)      # a test rig: the joint is bolted to a wall


def joint(name, y, colour, ghosted):
    root, (j,) = kit.arm(name, (0.4,), colour)
    for o in list(root.children):                                     # drop the pedestal: this pendulum hangs from its motor
        if o.name.startswith((name + "-foot", name + "-post")):
            bpy.data.objects.remove(o)
    root.location = (0, y, 0.65)
    if ghosted:
        g = kit.ghost("dark", 0.5)
        for o in root.children_recursive:
            if o.type == "MESH":
                o.data.materials.clear()
                o.data.materials.append(g)
    return j


jr, js = joint("real", 0.07, "blue", False), joint("sim", 0.0, "dark", True)
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / m.DT), len(real) - 1)
    kit.pose([jr], f, [real[i] - 1.5708])                             # q is measured from hanging straight down
    kit.pose([js], f, [sim[i] - 1.5708])
kit.camera((0, -1.55, 1.25), (0, 0, 0.7), lens=38)
kit.render(__file__)
