# 레슨 12/01 예시 클립: 같은 명령을 받는 실제 팔(단색)과 효과를 하나씩 뺀 시뮬 팔(유령) 셋. 마찰을 뺀 쪽만 눈에 띄게 어긋난다
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
T0, SECONDS = 0.0, 5.0                                                # the first 5 s of the lesson's run, real time
drop = {"friction": dict(b=0.0, c=0.0), "motor lag": dict(Tm=0.0), "sensor delay": dict(delay=0.0)}
i0 = round(T0 / m.DT)
real = m.measured(m.REAL, m.command, T0 + SECONDS)[i0:]                # every arm shows the angle the encoder reports, as in effect_costs()
sims = {k: m.measured({**m.REAL, **o}, m.command, T0 + SECONDS)[i0:] for k, o in drop.items()}

sc = kit.setup(SECONDS)
kit.box("wall", (5.2, 0.05, 3.2), (0, 0.16, 1.6), kit.mat("floor", rough=0.9, emit=0.2), bevel=0.01)


def joint(name, x, y, colour, ghosted):
    root, (j,) = kit.arm(name, (0.4,), colour)
    for o in list(root.children):                                     # drop the pedestal: this pendulum hangs from its motor
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


rigs = {k: (joint("real-" + k, x, 0.07, "blue", False), joint("sim-" + k, x, 0.0, "dark", True)) for k, x in zip(drop, (-1.1, 0.0, 1.1))}
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / m.DT), len(real) - 1)
    for k, (jr, js) in rigs.items():
        kit.pose([jr], f, [real[i] - 1.5708])                         # q is measured from hanging straight down
        kit.pose([js], f, [sims[k][i] - 1.5708])
kit.camera((0, -4.0, 1.45), (0, 0, 0.72), lens=38)
kit.render(__file__)
