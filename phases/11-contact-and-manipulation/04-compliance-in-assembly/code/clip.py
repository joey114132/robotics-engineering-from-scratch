# 레슨 11/04 클립: 같은 5 N 밀기로 slot에 peg를 꽂는 두 팔. 손목이 뻣뻣하면(kx=1e5) 중간에서 jam이 걸리고 부드러우면(kx=1e3) 끝까지 들어간다
import math
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
K, R, ZM, SHOULDER, L2, SECONDS, T0, MOVE = 9.0, 0.014, 0.5, 0.66, 0.36, 4.8, 0.4, 3.6   # drawing scale (lesson metre -> drawn m), peg radius, slot mouth height, shoulder height, link length
CASES = (("stiff", 1e5, "blue", -0.62, 1), ("soft", 1e3, "green", 0.62, -1))            # name, kx, colour, arm base x, +1 faces +x, -1 faces -x
runs = {n: m.insert(dict(m.P0, kx=kx)) for n, kx, *_ in CASES}
h, L = m.P0["h"], m.P0["L"]
STEPS = max(len(r["zt"]) for r in runs.values())     # the soft wrist inserts for the most steps; the stiff one stops at its jam

sc = kit.setup(SECONDS)
rigs = []
for n, kx, col, bx, fl in CASES:
    x0 = bx + fl * 0.45                     # the slot sits 0.45 m in front of the arm base
    w = 2 * h * K + 2 * R                                                # slot width: the lesson's clearance plus the peg's own thickness
    for s in (-1, 1):
        kit.box("wall", (0.12, 0.3, 0.42), (x0 + s * (w / 2 + 0.06), 0, ZM - 0.21), kit.ghost("grey", 0.28), bevel=0.01)   # see-through walls, so the peg shows
    kit.box("base", (w + 0.28, 0.3, 0.08), (x0, 0, ZM - 0.46), "grey", bevel=0.01)
    peg = kit.cyl("peg", R, L * K, (0, 0, 0), "z", "amber", segments=16)
    root, js = kit.arm("arm-" + n, (L2, L2), col, SHOULDER)
    root.location, root.rotation_euler = (bx, 0, 0), (0, 0, 0 if fl > 0 else math.pi)
    hand = bpy.data.objects["arm-%s-hand" % n]
    for ob in [o for o in bpy.data.objects if o.name.startswith("arm-%s-finger" % n)]:
        bpy.data.objects.remove(ob)
    for z in (0.024, -0.024):                                            # fingers that close on the peg
        kit.box("finger", (0.11, 0.05, 0.02), (0.085, 0, z), "grey", bevel=0.008, parent=hand)
    push = kit.arrow("push-" + n, "red")                                 # the same downward push on both arms
    push.rotation_euler, push.scale = (0, math.pi / 2, 0), (0.18, 1, 1)
    rigs.append((n, peg, js, hand, push, x0, bx, fl))

for f in range(sc.frame_start, sc.frame_end + 1):
    for n, peg, js, hand, push, x0, bx, fl in rigs:
        zt = runs[n]["zt"]
        zt = zt[min(int(max((f - 1) / sc.render.fps - T0, 0) / MOVE * STEPS), len(zt) - 1)]
        th = math.atan2(2 * h, zt)                                       # the lesson's tilt of the peg for this tip depth
        u = (math.sin(th), math.cos(th))                                 # up the peg (x, z)
        tip = (x0 - h * K, ZM - zt * K)
        kit.key(peg, f, loc=(tip[0] + u[0] * L * K / 2, 0, tip[1] + u[1] * L * K / 2), rot=(0, th, 0))
        wr = (tip[0] + u[0] * (L * K + 0.03), tip[1] + u[1] * (L * K + 0.03))   # wrist origin just above the peg top
        px, pz = fl * (wr[0] - bx), wr[1] - SHOULDER
        d = math.hypot(px, pz)
        b = math.acos(d / (2 * L2))
        q1, q2 = math.atan2(pz, px) + b, -2 * b
        kit.key(push, f, loc=(wr[0] + u[0] * 0.24, -0.1, wr[1] + u[1] * 0.24))
        kit.pose(js, f, (q1, q2))
        kit.key(hand, f, rot=(0, -(math.atan2(-u[1], -fl * u[0]) - q1 - q2), 0))    # hand points down the peg
kit.camera((0, -2.1, 1.25), (0, 0, 0.56), lens=38)
kit.render(__file__)
