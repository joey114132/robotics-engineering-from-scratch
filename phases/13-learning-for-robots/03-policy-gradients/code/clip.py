# 레슨 13/03 클립: 같은 시드로 40번 학습한 두 정책이 표시선(보상이 가장 큰 곳)까지 간다. 파랑은 raw return, 초록은 기준선 사용
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)


class Fixed:                                           # a stand-in rng: start at x = 0.8 and no exploration noise
    uniform = lambda self, a, b: 0.8
    standard_normal = lambda self: 0.0


def train(baseline, iters=40, lr=0.006):
    rng, theta = np.random.default_rng(1), np.zeros(2)
    for _ in range(iters):
        theta = theta + lr * m.grad_estimate(theta, rng, 32, baseline)[0]
    return theta


END, lanes = 120, {False: (0.45, "blue"), True: (-0.45, "green")}
sc = kit.setup(END / 24)
kit.stripe(-1.3, 1.3, -0.8, 0.8, "road")
kit.stripe(-0.04, 0.04, -0.8, 0.8, "amber", z=0.004)                    # the mark where the reward is highest (x = 0)
for baseline, (y, col) in lanes.items():
    theta = train(baseline)
    xs, acts, _ = m.episode(theta, Fixed(), sigma=0.0)
    xs = np.append(xs, xs[-1] + m.DT * acts[-1])                        # 15 steps of 0.2 s, played in real time
    root, wheels, _ = kit.car("car", col)
    for f in range(1, END + 1):
        x = -np.interp((f - 20) / 24 / m.DT, np.arange(len(xs)), xs)   # state x drawn as -x metres, so the car drives forward
        kit.drive(root, wheels, f, x, y)
kit.camera((0.0, -3.1, 2.0), (0.0, 0.0, 0.1), lens=38)
kit.render(__file__)
