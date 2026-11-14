# 레슨 04/01 예시 클립: 같은 모터에 같은 flywheel 을 달고 N=1 과 N=100 을 견준다. N=1 은 pinion 이 기어가고 N=100 은 부하 없는 것처럼 달린다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
M = dict(kt=0.05, R=1.0, V=24.0)
JR, JL, DT, T, SLOW = 2e-5, 2e-3, 1e-5, 0.05, 100.0      # the lesson's rotor and flywheel; the first 50 ms of the spin-up, played 100 times slower


def gear(r, teeth, depth, colour, parent):
    kit.cyl("gear", r, depth, (0, 0, 0), "y", colour, parent=parent)
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        t = kit.box("tooth", (0.026, depth, 0.032), ((r + 0.008) * math.cos(a), 0, (r + 0.008) * math.sin(a)), colour, bevel=0.004, parent=parent)
        t.rotation_euler = (0, -a, 0)


sc = kit.setup(T * SLOW)
kit.box("panel", (1.6, 0.04, 0.8), (-0.1, 0.32, 0.45), "pearl")
spins = []                                                # (rotor pivot, output pivot, N, rotor angle array)
for xr, N, colour, r_in, r_out in ((-0.5, 1.0, "blue", 0.08, 0.08), (0.12, 100.0, "green", 0.06, 0.1)):
    z, xo = 0.45, xr + 0.16                                # both pairs of gears sit 0.16 apart
    kit.cyl("can", 0.135, 0.2, (xr, 0.2, z), "y", colour, bevel=0.01)
    rot, out = kit.empty("rotor", (xr, 0.04, z)), kit.empty("output", (xo, 0.04, z))
    gear(r_in, 10 if N == 1.0 else 8, 0.03, "pearl", rot)                # the motor's pinion with a long mark
    kit.box("mark", (r_in, 0.036, 0.024), (r_in / 2, 0, 0), "dark", bevel=0.004, parent=rot)
    gear(r_out, 10 if N == 1.0 else 12, 0.03, "grey", out)               # the output gear
    kit.box("mark", (r_out, 0.036, 0.024), (r_out / 2, 0, 0), "dark", bevel=0.004, parent=out)
    kit.cyl("flywheel", 0.17, 0.04, (0, 0.045, 0), "y", "amber", parent=out)   # the same flywheel J_L on both
    _, w = m.spin_up(N, JR, JL, 0.0, T, DT, **M)
    spins.append((rot, out, N, np.cumsum(w) * DT))
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / DT), len(spins[0][3]) - 1)
    for rot, out, N, th in spins:
        kit.key(rot, f, rot=(0, -th[i], 0))
        kit.key(out, f, rot=(0, th[i] / N, 0))                # meshed gears turn opposite ways, N times slower
kit.camera((-0.1, -1.85, 0.5), (-0.1, 0, 0.45), lens=50)
kit.render(__file__)
