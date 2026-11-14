# 레슨 11/02 클립: 같은 스펀지를 10 N으로 누르는 두 팔. 파란 팔은 가정한 강성으로 깊이를 정해 1.6 N만 누르고 초록 팔은 힘을 재서 10 N에 맞춘다
import math
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
KE, T, SLOW, S, L2, SH, TOP, HS = 1e3, 2.5, 2.0, 10.0, 0.36, 0.55, 0.3, 0.2   # true sponge stiffness N/m, sim s, slow-down, drawn scale of depth, link, shoulder z, sponge top z, sponge height
ARMS = (("position", "blue", -0.8, 1), ("force", "green", 0.8, -1))              # lesson mode, colour, base x, +1 faces +x
runs = {mode: m.probe(mode, KE, T=T) for mode, *_ in ARMS}

sc = kit.setup(T * SLOW)
kit.table((2.1, 0.8), TOP, (0, 0))
rigs = []
for mode, col, bx, fl in ARMS:
    x0 = bx + fl * 0.5                                           # the sponge sits 0.5 m in front of the arm base
    sponge = kit.box("sponge", (0.3, 0.3, HS), (x0, 0, TOP + HS / 2), "amber", bevel=0.03)
    root, js = kit.arm("arm-" + mode, (L2, L2), col, SH - TOP)
    root.location, root.rotation_euler = (bx, 0, TOP), (0, 0, 0 if fl > 0 else math.pi)
    hand = bpy.data.objects["arm-%s-hand" % mode]
    for ob in [o for o in bpy.data.objects if o.name.startswith("arm-%s-finger" % mode)]:
        bpy.data.objects.remove(ob)
    kit.cyl("probe", 0.025, 0.22, (0.14, 0, 0), "x", "dark", parent=hand)
    kit.ball("tip", 0.03, (0.25, 0, 0), "pearl", parent=hand)
    push = kit.arrow("push-" + mode, "red")                      # the force the sponge pushes back with
    push.rotation_euler = (0, -math.pi / 2, 0)
    rigs.append((mode, sponge, js, hand, push, x0, bx, fl))

for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / 1e-3), runs["force"]["x"].size - 1)
    for mode, sponge, js, hand, push, x0, bx, fl in rigs:
        dip = (runs[mode]["x"][i] - m.XS) * S                    # lesson depth past the sponge surface, drawn 10 times larger
        tip_z = TOP + HS - dip                                   # the tip rests on the sponge at dip 0; before contact it is above
        sponge.scale = (1, 1, 1 - max(dip, 0) / HS)
        kit.key(sponge, f, loc=(x0, 0, TOP + HS / 2 - max(dip, 0) / 2), rot=(0, 0, 0))
        sponge.keyframe_insert("scale", frame=f)
        px, pz = fl * (x0 - bx), tip_z + 0.28 - SH               # wrist above the tip: hand 0.03 palm + 0.25 probe
        b = math.acos(math.hypot(px, pz) / (2 * L2))
        q1, q2 = math.atan2(pz, px) + b, -2 * b
        kit.pose(js, f, (q1, q2))
        kit.key(hand, f, rot=(0, -(-math.pi / 2 - q1 - q2), 0))
        n = runs[mode]["f"][i]
        push.location = (x0 + 0.2, 0, tip_z)
        push.scale = (n * 0.03, min(1, n * 0.12), min(1, n * 0.12)) if n > 0.05 else (1e-4, 1e-4, 1e-4)   # no arrow before contact; a short arrow is thin too
        kit.key(push, f, loc=push.location)
        push.keyframe_insert("scale", frame=f)
kit.camera((0, -2.4, 1.3), (0, 0, 0.55), lens=40)
kit.render(__file__)
