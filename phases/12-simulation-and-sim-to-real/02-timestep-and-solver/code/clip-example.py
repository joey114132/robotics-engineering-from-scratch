# 레슨 12/02 예시 클립: 같은 explicit Euler 로 상자를 떨어뜨리되 time step 만 3 ms, 1 ms, 0.1 ms. 각 상자는 첫 반발의 꼭대기에서 멈추고 step 이 작을수록 처음 높이에 가깝다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
T, SLOW, HOLD, SC, SIZE, PAD = 0.42, 10.0, 1.0, 2.2, 0.28, 0.05     # real time shown, slow-motion factor, seconds held at the end, drawing scale (1 m drawn as 2.2 m)
acc = lambda x: -m.G + m.K_CONTACT * max(-x, 0.0)                    # the lesson's penalty contact
runs = {}
for dt in (3e-3, 1e-3, 1e-4):
    x, v, xs = m.H0, 0.0, []
    for _ in range(round(T / dt) + 1):
        xs.append(x)
        x, v = m.step("euler", x, v, acc, dt)
    xs = np.array(xs)
    hit = int(np.argmax(xs < 0))
    top = hit + int(np.argmax(xs[hit:]))                             # the top of the first rebound: the crate stays there for the rest of the clip
    runs[dt] = (xs[: top + 1], dt)

sc = kit.setup(T * SLOW + HOLD)
kit.box("wall", (7.5, 0.05, 3), (0, 0.9, 1.5), kit.mat("floor", rough=0.9, emit=0.2), bevel=0.01)
side = {3e-3: (-0.7, "blue"), 1e-3: (0.0, "blue"), 1e-4: (0.7, "green")}
crates = {}
for dt, (x0, col) in side.items():
    kit.box(f"pad-{dt}", (0.5, 0.5, PAD), (x0, 0, PAD / 2), "grey", bevel=0.01)
    for s in (-1, 1):                                                # two amber ticks level with the drop height, one each side of the crate
        kit.box(f"mark-{dt}-{s}", (0.14, 0.03, 0.014), (x0 + s * 0.27, 0, PAD + SC * m.H0), "amber", bevel=0.004)
    crates[dt] = kit.box(f"crate-{dt}", (SIZE,) * 3, (x0, 0, 1), col, bevel=0.03)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps / SLOW
    for dt, ob in crates.items():
        xs, step = runs[dt]
        kit.key(ob, f, loc=(side[dt][0], 0, PAD + SC * np.interp(t, np.arange(len(xs)) * step, xs) + SIZE / 2))
kit.camera((0, -2.4, 0.75), (0, 0, 0.47), lens=38)
kit.render(__file__)
