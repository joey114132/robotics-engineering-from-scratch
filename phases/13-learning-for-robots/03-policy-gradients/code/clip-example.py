# 레슨 13/03 예시 클립: 같은 곳에서 출발한 네 번의 시도(자동차 넷). 위의 화살표가 먼저 원점수(모두 비슷하게 큼)를, 다음에 다른 시도 평균과의 차이를 보여 준다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)


class Fixed:                                           # a stand-in rng: start at x = 0.8, exploration noise from a fixed seed
    def __init__(self, seed):
        self.r = np.random.default_rng(seed)

    uniform = lambda self, a, b: 0.8
    standard_normal = lambda self: self.r.standard_normal()


fx = Fixed(2)
tries = [m.episode(np.zeros(2), fx) for _ in range(4)]               # four tries of the untrained policy (the lesson's episode())
G = np.array([r.sum() for _, _, r in tries])                         # return of each try: 35.9, 34.9, 27.6, 27.3
diff = G - (G.sum() - G) / 3                                         # return minus the average of the other three: +6.0, +4.6, -5.1, -5.6
LANES, END, T0 = (1.05, 0.35, -0.35, -1.05), 150, 20

sc = kit.setup(END / 24)
kit.stripe(-2.0, 0.9, -1.6, 1.6, "road")
kit.stripe(-0.04, 0.04, -1.6, 1.6, "amber", z=0.004)                 # the mark where the reward is highest (x = 0)


def size(arrow, f, length):
    """Key an arrow's size at frame f: `length` metres along the arrow, or nothing at all (every axis shrunk) when length is 0."""
    arrow.scale = (length, 1, 1) if length > 0 else (1e-3, 1e-3, 1e-3)
    arrow.keyframe_insert("scale", frame=f)


def grow(arrow, f0, f1, length, up):
    """An arrow along z (up or down) that grows from nothing at frame f0 to `length` metres at f1 and stays."""
    arrow.rotation_euler = (0, -np.pi / 2 if up else np.pi / 2, 0)
    for f, v in ((1, 0), (f0, 0), (f1, length)):
        size(arrow, f, v)


for (xs, acts, _), y, g, d in zip(tries, LANES, G, diff):
    xs = np.append(xs, xs[-1] + m.DT * acts[-1])
    root, wheels, _ = kit.car("car", "grey", 1.0)
    for f in range(1, END + 1):
        x = -np.interp((f - T0) / 24 / m.DT, np.arange(len(xs)), xs)  # state x drawn as -x metres, so the car drives forward
        kit.drive(root, wheels, f, x, y)
    xf = -xs[-1]
    raw = kit.arrow("raw", "blue", 0.035)                             # the whole return as a push: nearly the same for every try
    raw.location = (xf, y, 0.55)
    grow(raw, 92, 104, g / G.max() * 1.1, True)
    centred = kit.arrow("centred", "green" if d > 0 else "red", 0.035)   # the return minus the others' average: up for better, down for worse
    centred.location = (xf, y, 1.1)
    grow(centred, 118, 130, abs(d) * 0.13, d > 0)
    size(raw, 114, g / G.max() * 1.1)                                 # the raw arrow shrinks away before the next one grows
    size(raw, 118, 0)
kit.camera((-0.9, -4.8, 3.2), (-0.9, 0.0, 0.6), lens=38)
kit.render(__file__)
