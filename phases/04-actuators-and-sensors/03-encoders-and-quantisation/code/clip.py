# 레슨 04/03 클립: 느리게 도는 encoder 디스크 한 장과 속도계 두 개. 파란 속도계는 1 kHz 한 칸 차분이라 튀고, 초록은 20칸 창이라 잔잔하다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
FS, CPR, W0, NWIN, T0, SECONDS, SLOW, FULL = 1000.0, 4096, 0.1, 20, 0.5, 0.08, 60.0, 2.0   # 80 ms of the slow ramp, 60 times slower
c = m.counts(W0 * np.arange(int(1 * FS) + 1) / FS, CPR)
v1, vn = m.diff_velocity(c, CPR, 1 / FS), m.window_velocity(c, CPR, 1 / FS, NWIN)
deg = lambda v: math.radians(210 - 240 * v / FULL)                  # needle angle: 0 at lower left, FULL at lower right

sc = kit.setup(SECONDS * SLOW)
kit.box("panel", (2.3, 0.04, 1.15), (0, 0.3, 0.575), "pearl")
kit.cyl("motor", 0.17, 0.3, (-0.66, 0.2, 0.5), "y", "grey")
disc = kit.empty("disc", (-0.66, 0.0, 0.5))
kit.cyl("plate", 0.34, 0.03, (0, 0, 0), "y", "pearl", parent=disc)
for k in range(18):                                                   # 18 slits, 10 degrees each: one count drawn as one 10 degree edge
    s = kit.empty("slit", (0, 0, 0), disc)
    s.rotation_euler = (0, -math.radians(20 * k + 5), 0)
    kit.box("slit", (0.1, 0.034, 0.045), (0.23, 0, 0), "dark", bevel=0.004, parent=s)
kit.box("pointer", (0.014, 0.05, 0.16), (-0.66, -0.03, 0.5 + 0.23), "amber", bevel=0.004)   # the fixed reader at 12 o'clock
needles = []
for x, colour in ((0.0, "blue"), (0.68, "green")):
    kit.cyl("bezel", 0.3, 0.06, (x, 0.0, 0.5), "y", colour, bevel=0.012)
    kit.cyl("face", 0.265, 0.06, (x, -0.01, 0.5), "y", "pearl")
    for k in range(9):
        t = kit.empty("tick", (x, -0.045, 0.5))
        t.rotation_euler = (0, -deg(k * FULL / 8), 0)
        kit.box("tick", (0.05, 0.01, 0.014), (0.215, 0, 0), "dark", bevel=0, parent=t)
    true = kit.empty("true", (x, -0.05, 0.5))
    true.rotation_euler = (0, -deg(W0), 0)
    kit.box("true", (0.07, 0.012, 0.03), (0.2, 0, 0), "amber", bevel=0.004, parent=true)   # the true speed
    n = kit.empty("needle", (x, -0.06, 0.5))
    kit.box("needle", (0.23, 0.012, 0.02), (0.1, 0, 0), "dark", bevel=0.004, parent=n)
    kit.ball("hub", 0.03, (0, 0, 0), "dark", parent=n)
    needles.append(n)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = T0 + (f - 1) / sc.render.fps / SLOW
    i = int(t * FS + 1e-9)
    kit.key(disc, f, rot=(0, -math.radians(10) * t * W0 * CPR / (2 * math.pi), 0))   # one count turns the disc one slit edge (10 degrees)
    kit.key(needles[0], f, rot=(0, -deg(v1[i - 1]), 0))
    kit.key(needles[1], f, rot=(0, -deg(vn[i - NWIN]), 0))
kit.camera((0, -2.9, 0.55), (0, 0, 0.5), lens=50)
kit.render(__file__)
