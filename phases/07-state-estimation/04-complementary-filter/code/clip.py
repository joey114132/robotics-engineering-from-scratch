# 레슨 07/04 클립: 흔들리는 판의 기울기를 gyro만(파랑), 가속도계만(호박색), 상보 필터(초록)로 읽을 때 각 추정 판과 실제 판(회색 유령)의 차이
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
DT, B, SA, SG, N = 0.01, 0.01, 0.05, 0.02, 2000            # the lesson's figure values
T0 = 12.0                                                    # show seconds 12 to 17.5 of the 20 s run, in real time
t = DT * np.arange(N)[:, None]
truth, omega = 0.3 * np.sin(1.9 * t), 0.3 * 1.9 * np.cos(1.9 * t)
gyro, acc = m.sensors(truth, omega, B, SG, SA, np.random.default_rng(4))
est = {"blue": m.integrate(gyro, DT), "amber": acc, "green": m.complementary(gyro, acc, DT, m.best_tau(DT, B, SA))}

sc = kit.setup(5.5)
gm = kit.ghost("grey", 0.35)
rigs = {}
for x, colour in zip((-1.6, 0.0, 1.6), est):
    kit.cyl("foot", 0.22, 0.04, (x, 0, 0.02), "z", "dark", bevel=0.01)
    kit.cyl("post", 0.05, 0.6, (x, 0, 0.3), "z", "grey")
    piv, tpiv = kit.empty("piv", (x, 0, 0.62)), kit.empty("true", (x, 0, 0.62))
    kit.box("board", (1.1, 0.5, 0.04), (0, 0, 0.04), colour, bevel=0.012, parent=piv)
    kit.box("imu", (0.14, 0.14, 0.06), (0, 0, 0.1), "dark", bevel=0.01, parent=piv)
    kit.box("truth", (1.2, 0.56, 0.08), (0, 0, 0.04), gm, bevel=0.02, parent=tpiv)
    rigs[colour] = (piv, tpiv)
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int(T0 / DT) + int((f - 1) / sc.render.fps / DT), N - 1)
    for colour, (piv, tpiv) in rigs.items():
        kit.key(piv, f, rot=(0, -float(est[colour][i, 0]), 0))
        kit.key(tpiv, f, rot=(0, -float(truth[i, 0]), 0))
kit.camera((0, -5.4, 2.9), (0, 0, 0.7), lens=40)
kit.render(__file__)
