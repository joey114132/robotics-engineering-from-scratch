# 레슨 11/01 예시 클립: 판자를 천천히 기울이면 블록은 arctan(0.5)=26.6도까지 붙어 있다가 그 각도를 넘는 순간부터 미끄러진다
import math
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
MU, RATE, T0, SECONDS, L, H = 0.5, math.radians(12), 0.4, 5.4, 2.0, 0.15   # friction, tilt rate rad/s, flat time, clip seconds, plank length, block half size
HINGE, TH_MAX, SUB = (1.05, 0.0, 0.12), math.radians(40), 20                # hinge point, final tilt, physics steps per frame

sc = kit.setup(SECONDS)
d = lambda th: (-math.cos(th), 0.0, math.sin(th))                         # up the plank, away from the hinge
n = lambda th: (math.sin(th), 0.0, math.cos(th))                          # plank normal
at = lambda th, dist, h=0.0: tuple(HINGE[i] + dist * d(th)[i] + h * n(th)[i] for i in range(3))   # dist along the plank from the hinge, h above it
plank = kit.box("plank", (L, 0.9, 0.06), (0, 0, 0), "blue", bevel=0.01)
stop = kit.box("stop", (0.06, 0.9, 0.16), (0, 0, 0), "grey", bevel=0.01)
block = kit.crate("block", 2 * H, (0, 0, 0), "amber")
rod = kit.cyl("rod", 0.03, 1.0, (0, 0, 0.5), "z", "dark")
kit.cyl("hinge", 0.05, 0.5, HINGE, "y", "dark")
crit = m.critical_angle(MU)                                              # the lesson's sticking limit, marked as a see-through plank
mark = kit.box("limit", (L, 0.9, 0.06), at(crit, L / 2, -0.03), kit.ghost("amber", 0.35), bevel=0.01)
mark.rotation_euler = (0, crit, 0)

s = v = 0.0
smax = L - 0.06 - H
for f in range(sc.frame_start, sc.frame_end + 1):
    for k in range(SUB):                                                  # advance the sliding state with the lesson's slip_accel
        t = ((f - 1) + k / SUB) / sc.render.fps
        th = min(max(t - T0, 0.0) * RATE, TH_MAX)
        if m.slides(th, MU) or v > 0:
            v += m.slip_accel(th, MU) * 1.0 / (sc.render.fps * SUB)
            s = min(s + v / (sc.render.fps * SUB), smax)
            v = 0.0 if s >= smax else v
    th = min(max((f - 1) / sc.render.fps - T0, 0.0) * RATE, TH_MAX)
    for ob, loc in ((plank, at(th, L / 2, -0.03)), (stop, at(th, 0.03, 0.08)), (block, at(th, L - H - s - 0.0, H))):
        kit.key(ob, f, loc=loc, rot=(0, th, 0))
    top = at(th, L)
    kit.key(rod, f, loc=(top[0], 0, (top[2] - 0.06) / 2))
    rod.scale = (1, 1, top[2] - 0.06)
    rod.keyframe_insert("scale", frame=f)
kit.camera((-0.1, -4.6, 2.1), (-0.1, 0, 0.5), lens=38)
kit.render(__file__)
