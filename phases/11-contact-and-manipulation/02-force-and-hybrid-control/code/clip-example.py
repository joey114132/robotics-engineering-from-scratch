# 레슨 11/02 예시 클립: 같은 깊이를 명령한 위치 제어 팔 세 대가 1000, 5000, 25000 N/m 스펀지를 누른다. 깊이는 같은데 힘이 1.6, 8, 40 N으로 다르다
import math
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
T, SLOW, S, L2, SH, TOP, HS, AR = 2.5, 2.0, 20.0, 0.36, 0.55, 0.3, 0.2, 0.016   # sim s, slow-down, drawn scale of depth, link, shoulder z, sponge top z, sponge height, bar height m per newton
SPONGES = ((1e3, -0.8, "#f7d58b"), (5e3, 0.0, "#f0a530"), (2.5e4, 0.8, "#b9741a"))   # true stiffness N/m, arm base x, sponge colour (darker is stiffer)
runs = {ke: m.probe("position", ke, T=T) for ke, *_ in SPONGES}

sc = kit.setup(T * SLOW)
kit.table((3.0, 0.8), TOP, (0.3, 0))
rigs = []
for ke, bx, col in SPONGES:
    x0 = bx + 0.5                                                # the sponge sits 0.5 m in front of the arm base
    sponge = kit.box("sponge", (0.3, 0.3, HS), (x0, 0, TOP + HS / 2), col, bevel=0.03)
    root, js = kit.arm("arm-%d" % ke, (L2, L2), "blue", SH - TOP)
    root.location = (bx, 0, TOP)
    hand = bpy.data.objects["arm-%d-hand" % ke]
    for ob in [o for o in bpy.data.objects if o.name.startswith("arm-%d-finger" % ke)]:
        bpy.data.objects.remove(ob)
    kit.cyl("probe", 0.025, 0.22, (0.14, 0, 0), "x", "dark", parent=hand)
    kit.ball("tip", 0.03, (0.25, 0, 0), "pearl", parent=hand)
    push = kit.cyl("push-%d" % ke, 0.02, 1.0, (0, 0, 0), "z", "red", segments=16)   # the force the sponge pushes back with, a bar 1.6 cm tall per newton
    rigs.append((ke, sponge, js, hand, push, x0, bx))

for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / 1e-3), runs[1e3]["x"].size - 1)
    for ke, sponge, js, hand, push, x0, bx in rigs:
        dip = (runs[ke]["x"][i] - m.XS) * S                      # lesson depth past the sponge surface, drawn 20 times larger
        tip_z = TOP + HS - dip
        sponge.scale = (1, 1, 1 - max(dip, 0) / HS)
        kit.key(sponge, f, loc=(x0, 0, TOP + HS / 2 - max(dip, 0) / 2), rot=(0, 0, 0))
        sponge.keyframe_insert("scale", frame=f)
        px, pz = x0 - bx, tip_z + 0.28 - SH                      # wrist above the tip: hand 0.03 palm + 0.25 probe
        b = math.acos(math.hypot(px, pz) / (2 * L2))
        q1, q2 = math.atan2(pz, px) + b, -2 * b
        kit.pose(js, f, (q1, q2))
        kit.key(hand, f, rot=(0, -(-math.pi / 2 - q1 - q2), 0))
        n = runs[ke]["f"][i]
        h = n * AR if n > 0.05 else 0.0                          # no bar before the probe touches the sponge
        kit.key(push, f, loc=(x0 + 0.1, 0, tip_z + h / 2 if h else -1.0))
        push.scale = (1, 1, max(h, 0.001))
        push.keyframe_insert("scale", frame=f)
kit.camera((0.3, -2.9, 1.6), (0.3, 0, 0.55), lens=40)
kit.render(__file__)
