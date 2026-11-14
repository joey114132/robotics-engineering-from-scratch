# 레슨 02/05 클립: 3링크 팔이 solve_ik 의 반복 한 번마다 표적으로 다가간다. 닿는 표적(초록)은 수렴하고 안 닿는 표적(파랑)은 최선에서 멈춘다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, STEPS, PER = 5.0, 10, 10                # 10 iterations of the lesson's solver, 10 frames each, then hold
L, LO, HI, Q0 = (0.4, 0.3, 0.2), np.array([-np.pi, -2.5, -2.5]), np.array([np.pi, 2.5, 2.5]), np.array([1.06, -0.41, 0.38])
sc = kit.setup(SECONDS)
kit.table((3.2, 0.7), 0.4, (-0.15, 0))
for name, colour, x, target in (("reach", "green", -1.25, (0.5, 0.3)), ("far", "blue", -0.1, (1.15, 0.15))):   # the second one is beyond the 0.9 m reach
    root, js = kit.arm(name, L, colour)
    root.location = (x, 0, 0.4)
    q = [m.solve_ik(target, L, Q0, LO, HI, iters=k)[0] for k in range(STEPS + 1)]   # q after k damped Newton steps
    hand = np.array([np.cos(q[-1].sum()), np.sin(q[-1].sum())])
    ball = np.array(target) + 0.085 * hand                      # the target is the wrist point; the ball sits where the fingers would close
    kit.ball(name + "-goal", 0.04, (x + ball[0], 0, 0.7 + ball[1]), "amber" if colour == "green" else "red")
    for f in range(sc.frame_start, sc.frame_end + 1):
        k, w = divmod((f - 1) / PER, 1)
        k = int(k)
        kit.pose(js, f, q[STEPS] if k >= STEPS else (1 - w) * q[k] + w * q[k + 1])
kit.camera((-0.05, -3.9, 2.1), (-0.05, 0, 0.95), lens=50)
kit.render(__file__)
