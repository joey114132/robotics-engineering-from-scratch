# 레슨 04/03 예시 클립: 가속하는 축을 속도계 두 개가 읽는다. 파란 바늘(한 칸 차분)은 참 속도를 따라가고 초록 바늘(20칸 창)은 n*dt/2 = 10 ms 늦다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
FS, A, NWIN, FINE, T0, SECONDS, SLOW, FULL, SPIN = 1000.0, 2.0, 20, 10_000_000, 0.02, 0.1, 50.0, 0.25, 100.0   # the lesson's lag test: 2 rad/s^2, 20 samples at 1 kHz; 0.02 s to 0.12 s played 50 times slower
t = np.arange(int(0.3 * FS) + 1) / FS
c = m.counts(0.5 * A * t**2, FINE)                                     # a very fine encoder, so only the delay is visible
v1, vn = m.diff_velocity(c, FINE, 1 / FS), m.window_velocity(c, FINE, 1 / FS, NWIN)
deg = lambda v: math.radians(210 - 240 * v / FULL)                      # needle angle: 0 at lower left, FULL at lower right

sc = kit.setup(SECONDS * SLOW)
kit.box("panel", (2.3, 0.04, 1.15), (0, 0.3, 0.575), "pearl")
kit.cyl("motor", 0.17, 0.3, (-0.66, 0.2, 0.5), "y", "grey")
disc = kit.empty("disc", (-0.66, 0.0, 0.5))
kit.cyl("plate", 0.34, 0.03, (0, 0, 0), "y", "pearl", parent=disc)
for k in range(18):
    s = kit.empty("slit", (0, 0, 0), disc)
    s.rotation_euler = (0, -math.radians(20 * k + 5), 0)
    kit.box("slit", (0.1, 0.034, 0.045), (0.23, 0, 0), "dark", bevel=0.004, parent=s)
kit.box("pointer", (0.014, 0.05, 0.16), (-0.66, -0.03, 0.5 + 0.23), "amber", bevel=0.004)
needles, trues = [], []
for x, colour in ((0.0, "blue"), (0.68, "green")):
    kit.cyl("bezel", 0.3, 0.06, (x, 0.0, 0.5), "y", colour, bevel=0.012)
    kit.cyl("face", 0.265, 0.06, (x, -0.01, 0.5), "y", "pearl")
    for k in range(9):
        tk = kit.empty("tick", (x, -0.045, 0.5))
        tk.rotation_euler = (0, -deg(k * FULL / 8), 0)
        kit.box("tick", (0.05, 0.01, 0.014), (0.215, 0, 0), "dark", bevel=0, parent=tk)
    tr = kit.empty("true", (x, -0.05, 0.5))
    kit.box("true", (0.07, 0.012, 0.03), (0.2, 0, 0), "amber", bevel=0.004, parent=tr)   # the true speed, A * t
    n = kit.empty("needle", (x, -0.06, 0.5))
    kit.box("needle", (0.23, 0.012, 0.02), (0.1, 0, 0), "dark", bevel=0.004, parent=n)
    kit.ball("hub", 0.03, (0, 0, 0), "dark", parent=n)
    needles.append(n)
    trues.append(tr)
for f in range(sc.frame_start, sc.frame_end + 1):
    tt = T0 + (f - 1) / sc.render.fps / SLOW
    i = int(tt * FS + 1e-9)
    kit.key(disc, f, rot=(0, -SPIN * 0.5 * A * tt**2, 0))                # drawn turning 100 times faster than real
    for tr in trues:
        kit.key(tr, f, rot=(0, -deg(A * tt), 0))
    kit.key(needles[0], f, rot=(0, -deg(v1[i - 1]), 0))
    kit.key(needles[1], f, rot=(0, -deg(vn[i - NWIN]), 0))
kit.camera((0, -2.9, 0.55), (0, 0, 0.5), lens=50)
kit.render(__file__)
