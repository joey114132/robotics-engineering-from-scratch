# 레슨 04/01 클립: 같은 모터와 감속기 네 벌. N=10 줄은 부하를 단 rotor가 뒤처지고, N=100 줄은 두 rotor가 같이 돈다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
M = dict(kt=0.05, R=1.0, V=24.0)
JR, JL, DT, T, SLOW = 2e-5, 2e-3, 1e-5, 0.02, 240.0      # the first 20 ms of the spin-up, played 240 times slower


def gear(r, teeth, depth, colour, parent):
    kit.cyl("gear", r, depth, (0, 0, 0), "y", colour, parent=parent)
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        t = kit.box("tooth", (0.026, depth, 0.032), ((r + 0.008) * math.cos(a), 0, (r + 0.008) * math.sin(a)), colour, bevel=0.004, parent=parent)
        t.rotation_euler = (0, -a, 0)


sc = kit.setup(T * SLOW)
kit.box("panel", (3.2, 0.04, 1.15), (0, 0.32, 0.575), "pearl")
spins = []                                                # (rotor pivot, output pivot, N, rotor angle array)
for z, N, colour in ((0.75, 10.0, "blue"), (0.27, 100.0, "green")):
    for xr, xo, loaded in ((-0.1, -0.27, False), (0.1, 0.27, True)):    # the two rotors sit side by side in the middle
        kit.cyl("can", 0.09, 0.2, (xr, 0.2, z), "y", colour, bevel=0.01)
        rot, out = kit.empty("rotor", (xr, 0.04, z)), kit.empty("output", (xo, 0.04, z))
        gear(0.06, 8, 0.03, "pearl", rot)                               # the motor's pinion with a long mark
        kit.box("mark", (0.06, 0.036, 0.024), (0.03, 0, 0), "dark", bevel=0.004, parent=rot)
        gear(0.1, 12, 0.03, "grey", out)                                # the output gear
        kit.box("mark", (0.1, 0.036, 0.024), (0.05, 0, 0), "dark", bevel=0.004, parent=out)
        if loaded:
            kit.cyl("flywheel", 0.17, 0.04, (0, 0.045, 0), "y", "amber", parent=out)   # the load's inertia J_L
        _, w = m.spin_up(N, JR, JL if loaded else 0.0, 0.0, T, DT, **M)
        spins.append((rot, out, N, np.cumsum(w) * DT))
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / DT), len(spins[0][3]) - 1)
    for rot, out, N, th in spins:
        kit.key(rot, f, rot=(0, -th[i], 0))
        kit.key(out, f, rot=(0, th[i] / N, 0))                # meshed gears turn opposite ways, N times slower
kit.camera((0.12, -2.5, 0.9), (0.12, 0, 0.52), lens=50)
kit.render(__file__)
