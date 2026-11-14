# 레슨 02/05 예시 클립: 같은 표적에 서로 다른 두 시작 자세(seed)에서 solve_ik 를 돌리면 팔꿈치 모양이 다른 답에 닿는다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, PER, HOLD = 5.5, 10, 8                  # each damped Newton step is spread over 10 frames, after an 8 frame pause on the start poses
L, LO, HI, TARGET = (0.4, 0.3, 0.2), np.array([-np.pi, -2.5, -2.5]), np.array([np.pi, 2.5, 2.5]), (0.5, 0.3)
rng = np.random.default_rng(0)                   # the same seeds as ik_restarts(): seed 2 and seed 0 of the lesson's 20
seeds = [rng.uniform(LO, HI) for _ in range(6)]
sc = kit.setup(SECONDS)
kit.table((3.2, 0.7), 0.4, (-0.1, 0))
for name, x, q0 in (("seed2", -1.3, seeds[2]), ("seed0", 0.0, seeds[0])):
    root, js = kit.arm(name, L, "green")
    root.location = (x, 0, 0.4)
    kit.ball(name + "-goal", 0.04, (x + TARGET[0], 0, 0.7 + TARGET[1]), "amber")
    q = [m.solve_ik(TARGET, L, q0, LO, HI, iters=k)[0] for k in range(16)]   # q after k damped Newton steps
    for f in range(sc.frame_start, sc.frame_end + 1):
        k, w = divmod(max(f - 1 - HOLD, 0) / PER, 1)
        k = int(k)
        kit.pose(js, f, q[min(k, 15)] if k >= 15 else (1 - w) * q[k] + w * q[k + 1])
kit.camera((-0.65, -3.9, 2.1), (-0.65, 0, 0.95), lens=50)
kit.render(__file__)
