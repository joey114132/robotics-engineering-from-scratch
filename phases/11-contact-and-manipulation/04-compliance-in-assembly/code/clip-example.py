# 레슨 11/04 예시 클립: peg 를 가까이서 본다. 같은 1 mm 어긋남에서 뻣뻣한 손목은 구멍이 좁아지면 옆힘이 커져 peg 가 wedge 되고 jam 이 걸리며 부드러운 손목은 옆힘이 작아 들어간다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
K, R, ZM, SECONDS, T0, MOVE, AR, TILT = 9.0, 0.03, 0.5, 4.8, 0.4, 3.6, 0.06, 4.0   # drawing scale (lesson metre -> drawn m), peg radius (drawn fat so it reads at 350 px), hole mouth height, clip s, start s, insertion s, arrow m per newton
CASES = (("stiff", 1e5, "#4f8df0", -0.3), ("soft", 1e3, "#2f9e62", 0.3))       # name, kx, colour, x of the hole
runs = {n: m.insert(dict(m.P0, kx=kx)) for n, kx, *_ in CASES}
h, L = m.P0["h"], m.P0["L"]
STEPS = max(len(r["zt"]) for r in runs.values())

sc = kit.setup(SECONDS)
rigs = []
for n, kx, col, x0 in CASES:
    w = 2 * h * K + 2 * R                                                    # hole width: the lesson's clearance plus the peg's own thickness
    for s in (-1, 1):
        kit.box("wall", (0.12, 0.3, 0.42), (x0 + s * (w / 2 + 0.06), 0, ZM - 0.21), kit.mat("#6b777e", kind="matte"), bevel=0.01)   # solid, matte and dull: the walls beside the slot must not outshine the peg
    kit.box("base", (w + 0.28, 0.3, 0.08), (x0, 0, ZM - 0.46), "grey", bevel=0.01)
    peg = kit.cyl("peg", R, L * K, (0, 0, 0), "z", col, segments=24)         # the peg takes its wrist's colour: blue is the stiff wrist, green the soft one
    kit.box("grip", (0.14, 0.14, 0.1), (0, 0, L * K / 2 + 0.05), "dark", bevel=0.012, parent=peg)   # the wrist holds the peg top
    kit.cyl("stem", 0.03, 0.12, (0, 0, L * K / 2 + 0.16), "z", "dark", parent=peg)
    side = kit.arrow("side-" + n, "red", 0.04)                                   # the wrist's sideways force on the peg
    rigs.append((n, peg, side, x0))

for f in range(sc.frame_start, sc.frame_end + 1):
    for n, peg, side, x0 in rigs:
        r = runs[n]
        i = min(int(max((f - 1) / sc.render.fps - T0, 0) / MOVE * STEPS), len(r["zt"]) - 1)
        zt, fx = r["zt"][i], r["Fx"][i]
        th = TILT * min(math.atan2(2 * h, zt), r["th_free"])                  # the lesson's lean of the peg at this depth (the wrist's own lean until the edge catches it), drawn 4 times larger (it is under 2 degrees at the jam)
        u = (math.sin(th), math.cos(th))
        tip = (x0 - h * K, ZM - zt * K)
        kit.key(peg, f, loc=(tip[0] + u[0] * L * K / 2, 0, tip[1] + u[1] * L * K / 2), rot=(0, th, 0))
        top = (tip[0] + u[0] * (L * K + 0.04), tip[1] + u[1] * (L * K + 0.04))
        kit.key(side, f, loc=(top[0], -0.1, top[1]), rot=(0, 0, 0 if fx > 0 else math.pi))
        ln = max(abs(fx) * AR, 0.03)                                         # arrow length follows the force (a stub is left so the arrow never vanishes)
        side.scale = (ln, min(1.0, ln / 0.3), min(1.0, ln / 0.3))          # a short arrow shrinks all round, so it stays an arrow and not a flat disc
        side.keyframe_insert("scale", frame=f)
kit.camera((0, -1.95, 1.1), (0, 0, 0.56), lens=38)
kit.render(__file__)
