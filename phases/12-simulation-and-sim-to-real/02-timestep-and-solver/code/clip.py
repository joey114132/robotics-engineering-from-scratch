# 레슨 12/02 클립: 같은 높이에서 떨군 상자 두 개가 단단한 패드에서 튄다. 파란 상자는 explicit Euler, 초록 상자는 semi-implicit Euler
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
DT, T, SLOW, SC, SIZE, PAD = 3e-3, 0.43, 10.0, 2.2, 0.28, 0.05     # lesson step (s), real time shown, slow-motion factor, drawing scale (1 m drawn as 2.2 m)
acc = lambda x: -m.G + m.K_CONTACT * max(-x, 0.0)                    # the lesson's penalty contact
runs = {}
for meth in ("euler", "semi"):
    x, v, xs = m.H0, 0.0, []
    for _ in range(round(T / DT) + 1):
        xs.append(x)
        x, v = m.step(meth, x, v, acc, DT)
    runs[meth] = np.array(xs)

sc = kit.setup(T * SLOW)
kit.box("wall", (6, 0.05, 3), (0, 0.9, 1.5), kit.mat("floor", rough=0.9, emit=0.2), bevel=0.01)   # a plain backdrop
side = {"euler": (-0.55, "blue"), "semi": (0.55, "green")}
for meth, (x0, col) in side.items():
    kit.box("pad-" + meth, (0.5, 0.5, PAD), (x0, 0, PAD / 2), "grey", bevel=0.01)
    kit.box("mark-" + meth, (SIZE * 1.6, SIZE * 1.6, 0.012), (x0, 0, PAD + SC * m.H0 - 0.006), kit.ghost("amber", 0.6), bevel=0.004)   # the drop height: a correct bounce comes back to this shelf
    runs[meth] = (kit.box("crate-" + meth, (SIZE,) * 3, (x0, 0, 1), col, bevel=0.03), runs[meth])
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps / SLOW
    for meth, (ob, xs) in runs.items():
        kit.key(ob, f, loc=(side[meth][0], 0, PAD + SC * np.interp(t, np.arange(len(xs)) * DT, xs) + SIZE / 2))
kit.camera((0, -2.15, 0.85), (0, 0, 0.5), lens=38)
kit.render(__file__)
