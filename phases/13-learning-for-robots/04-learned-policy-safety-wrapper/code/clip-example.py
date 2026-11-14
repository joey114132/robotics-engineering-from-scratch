# 레슨 13/04 예시 클립: 정책이 8.0 을 8 tick 외치는 구간을 천천히 본다. 자동차 위의 주황색 화살표는 모터가 받는 명령이다. 파랑은 8.0 그대로, 초록은 clip 과 변화율 제한을 거친 값
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
T0, PER_TICK, END = 17, 4.5, 110                                   # ticks 17 to 36 of the lesson's run (the burst is ticks 20 to 27), 4.5 frames a tick: 3.7 times slower than real time
runs = {False: (0.55, "blue"), True: (-0.55, "green")}             # the lesson's simulate(wrapped) without and with the wrapper
LEN = 0.16                                                         # an arrow of 1 m is a command of 6.25

sc = kit.setup(END / 24)
kit.stripe(-3.8, 0.8, -1.05, 1.05, "road")
kit.box("zone", (2.2, 2.1, 0.004), (-2.7, 0, 0.004), kit.ghost("red", 0.45), bevel=0)   # the zone behind the start
kit.stripe(-0.03, 0.03, -1.05, 1.05, "white", z=0.006)               # the stop mark at x = 0
for wrapped, (y, col) in runs.items():
    r = m.simulate(wrapped)
    x, u = -r["x"], r["out"]                                         # state x drawn as -x metres, so the car drives forward toward 0
    root, wheels, _ = kit.car("car", col, 1.3)
    push = kit.arrow("command", "amber", 0.03)                       # the command the motor receives: positive drives the car backward (toward -x)
    for f in range(1, END + 1):
        t = T0 + (f - 1) / PER_TICK
        kit.drive(root, wheels, f, float(np.interp(t, np.arange(len(x)), x)), y, radius=0.117)
        c = float(u[min(int(t), len(u) - 1)])
        kit.key(push, f, loc=(float(np.interp(t, np.arange(len(x)), x)), y, 0.62), rot=(0, 0, np.pi if c > 0 else 0.0))
        push.scale = (max(abs(c) * LEN, 0.02), 1, 1)
        push.keyframe_insert("scale", frame=f)
kit.camera((-1.9, -6.0, 4.1), (-1.9, 0.0, 0.05), lens=40)
kit.render(__file__)
