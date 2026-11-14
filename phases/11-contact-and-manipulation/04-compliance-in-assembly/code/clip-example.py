# 레슨 11/04 예시 클립: peg 를 가까이서 본다. 같은 1 mm 어긋남에서 뻣뻣한 손목은 옆으로 약 112 N 으로 peg 를 벽에 밀고 jam 이 걸리며 부드러운 손목은 1.1 N 이라 들어간다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
K, R, ZM, SECONDS, T0, MOVE, AR = 9.0, 0.01, 0.5, 4.8, 0.4, 3.6, 0.0022   # drawing scale (lesson metre -> drawn m), peg radius, hole mouth height, clip s, start s, insertion s, arrow m per newton
CASES = (("stiff", 1e5, "blue", -0.3), ("soft", 1e3, "green", 0.3))       # name, kx, colour, x of the hole
runs = {n: m.insert(dict(m.P0, kx=kx)) for n, kx, *_ in CASES}
h, L = m.P0["h"], m.P0["L"]
STEPS = max(len(r["zt"]) for r in runs.values())

sc = kit.setup(SECONDS)
rigs = []
for n, kx, col, x0 in CASES:
    w = 2 * h * K + 2 * R                                                    # hole width: the lesson's clearance plus the peg's own thickness
    for s in (-1, 1):
        kit.box("wall", (0.12, 0.3, 0.42), (x0 + s * (w / 2 + 0.06), 0, ZM - 0.21), kit.ghost("grey", 0.3), bevel=0.01)   # see-through, so the tilt shows
    kit.box("base", (w + 0.28, 0.3, 0.08), (x0, 0, ZM - 0.46), "grey", bevel=0.01)
    peg = kit.cyl("peg", R, L * K, (0, 0, 0), "z", "amber", segments=16)
    kit.box("grip", (0.09, 0.12, 0.1), (0, 0, L * K / 2 + 0.05), col, bevel=0.012, parent=peg)   # the wrist holds the peg top
    kit.cyl("stem", 0.025, 0.3, (0, 0, L * K / 2 + 0.25), "z", "dark", parent=peg)
    side = kit.arrow("side-" + n, "red")                                     # the wrist's sideways force on the peg
    rigs.append((n, peg, side, x0))

for f in range(sc.frame_start, sc.frame_end + 1):
    for n, peg, side, x0 in rigs:
        r = runs[n]
        i = min(int(max((f - 1) / sc.render.fps - T0, 0) / MOVE * STEPS), len(r["zt"]) - 1)
        zt, fx = r["zt"][i], r["Fx"][i]
        th = math.atan2(2 * h, zt)                                           # the lesson's tilt of the peg for this tip depth
        u = (math.sin(th), math.cos(th))
        tip = (x0 - h * K, ZM - zt * K)
        kit.key(peg, f, loc=(tip[0] + u[0] * L * K / 2, 0, tip[1] + u[1] * L * K / 2), rot=(0, th, 0))
        top = (tip[0] + u[0] * (L * K + 0.04), tip[1] + u[1] * (L * K + 0.04))
        kit.key(side, f, loc=(top[0], -0.1, top[1]), rot=(0, 0, 0 if fx > 0 else math.pi))
        side.scale = (max(abs(fx) * AR, 0.02), 1, 1)
        side.keyframe_insert("scale", frame=f)
kit.camera((0, -1.75, 1.05), (0, 0, 0.52), lens=38)
kit.render(__file__)
