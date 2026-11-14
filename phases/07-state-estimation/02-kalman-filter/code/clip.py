# 레슨 07/02 클립: 실제 자동차(회색), 흔들리는 위치 측정(호박색 핀), 필터 추정(초록 핀과 2시그마 띠)
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
W0, W1, SCALE, RATE, CS = 20, 40, 0.17, 4.0, 1.4   # show steps 20..40, 1 m drawn as 0.17 m, 4 steps a second, car scale
truth, zs = m.simulate(60, 1, np.random.default_rng(31))
xs, Ps = m.kalman(zs)
truth, zs, xs, sig = truth[:, :, 0], zs[:, 0], xs[:, :, 0], np.sqrt(Ps[:, 0, 0])
X0 = (truth[W0, 0] + truth[W1, 0]) / 2   # centre the drive in the frame
wx = lambda p: (p - X0) * SCALE

sc = kit.setup(5.5)
kit.stripe(-3.4, 3.4, -0.55, 0.55, "road")
for x in np.arange(-3.2, 3.2, 0.6):
    kit.stripe(x, x + 0.25, -0.015, 0.015, "white", z=0.004)
car, wheels, _ = kit.car("real", "grey", CS)
band = kit.box("band", (1.0, 0.8, 0.01), (0, 0, 0.008), kit.ghost("green", 0.6), bevel=0)      # estimate +/- 2 sigma, on the road
pins = {}
for colour, top in (("amber", 0.75), ("green", 1.0)):
    pins[colour] = (kit.ball(colour + "-ball", 0.1, (0, -0.35, top), colour), kit.cyl(colour + "-stem", 0.014, 1.0, (0, -0.35, 0), "z", colour))

for f in range(sc.frame_start, sc.frame_end + 1):
    t = min(W0 + (f - 1) / sc.render.fps * RATE, W1)
    k = int(t)
    w = t - k
    p = truth[k, 0] * (1 - w) + truth[k + 1, 0] * w
    e = xs[k, 0] + xs[k, 1] * w                   # between readings the estimate coasts on its own velocity
    kit.drive(car, wheels, f, wx(p), 0.0, 0.0, 0.09 * CS)
    kit.key(band, f, loc=(wx(e), 0, 0.008))
    band.scale = (4 * sig[k] * SCALE, 1, 1)
    band.keyframe_insert("scale", frame=f)
    for colour, x, top in (("amber", zs[k], 0.75), ("green", e, 1.0)):
        ball, stem = pins[colour]
        kit.key(ball, f, loc=(wx(x), -0.35, top))
        kit.key(stem, f, loc=(wx(x), -0.35, top / 2))
        stem.scale = (1, 1, top)
        stem.keyframe_insert("scale", frame=f)
kit.camera((0, -4.4, 2.9), (0, 0, 0.25), lens=28)
kit.render(__file__)
