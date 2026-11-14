# 레슨 07/04 예시 클립: 가만히 놓인 판을 tau 가 작으면(파랑) 가속도계 떨림이, tau 가 크면(파랑) gyro bias 의 기울어짐이 생기고 알맞은 tau(초록)는 둘 다 작다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
DT, B, SA, SG, N, T0, X = 0.01, 0.01, 0.05, 0.02, 2000, 12.0, 10.0   # the lesson's values; seconds 12 to 17.5 in real time; errors drawn 10 times larger
t = DT * np.arange(N)[:, None]
truth = np.zeros_like(t)                                              # the board is level and does not move
gyro, acc = m.sensors(truth, truth, B, SG, SA, np.random.default_rng(4))
taus = (("blue", -1.5, 0.05), ("green", 0.0, m.best_tau(DT, B, SA)), ("blue", 1.5, 2.0))     # trusts the accelerometer, the best tau, trusts the gyro
est = [m.complementary(gyro, acc, DT, tau) for _, _, tau in taus]

sc = kit.setup(5.5)
piv = []
for (colour, x, tau), series in zip(taus, est):
    kit.cyl("foot", 0.22, 0.04, (x, 0, 0.02), "z", "dark", bevel=0.01)
    kit.cyl("post", 0.05, 0.6, (x, 0, 0.3), "z", "grey")
    p = kit.empty("piv", (x, 0, 0.62))
    kit.box("board", (1.1, 0.5, 0.04), (0, 0, 0.04), colour, bevel=0.012, parent=p)
    kit.box("imu", (0.14, 0.14, 0.06), (0, 0, 0.1), "dark", bevel=0.01, parent=p)
    kit.box("level", (1.3, 0.02, 0.02), (x, 0.36, 0.62), kit.ghost("grey", 0.5), bevel=0)    # the true level of the board, for comparison
    piv.append(p)
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int(T0 / DT) + int((f - 1) / sc.render.fps / DT), N - 1)
    for p, series in zip(piv, est):
        kit.key(p, f, rot=(0, -X * float(series[i, 0]), 0))
kit.camera((0, -5.0, 2.5), (0, 0, 0.62), lens=36)
kit.render(__file__)
