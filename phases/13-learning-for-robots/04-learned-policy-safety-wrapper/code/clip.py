# 레슨 13/04 클립: 같은 불안정한 정책이 모는 장난감 자동차 두 대. 파랑은 정책 출력을 그대로, 초록은 안전 래퍼를 거쳐 모터로 보낸다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
TICKS, PER_TICK, END = 78, 1.5, 125                                  # the first 3.9 s of the lesson's run, played 1.25 times slower
runs = {False: (0.55, "blue"), True: (-0.55, "green")}                 # the lesson's simulate(wrapped) with and without the wrapper

sc = kit.setup(END / 24)
kit.stripe(-3.8, 0.8, -1.05, 1.05, "road")
kit.box("zone", (2.2, 2.1, 0.004), (-2.7, 0, 0.004), kit.ghost("red", 0.45), bevel=0)   # the zone behind the start, which the wrapper never lets x reach
kit.stripe(-0.03, 0.03, -1.05, 1.05, "white", z=0.006)               # the stop mark at x = 0
for wrapped, (y, col) in runs.items():
    x = -m.simulate(wrapped)["x"][:TICKS + 1]                        # state x drawn as -x metres, so the car drives forward toward 0
    root, wheels, _ = kit.car("car", col, 1.3)
    for f in range(1, END + 1):
        kit.drive(root, wheels, f, float(np.interp((f - 1) / PER_TICK, np.arange(len(x)), x)), y, radius=0.117)
kit.camera((-1.6, -5.6, 3.9), (-1.6, 0.0, 0.05), lens=42)
kit.render(__file__)
