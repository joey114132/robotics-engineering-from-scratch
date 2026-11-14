# 레슨 05/03 클립: 같은 궤적을 iteration 번호로 따라가는 팔 두 대. 파란 팔은 일 끝나고 T 를 쉬는 loop, 초록 팔은 i*T 까지 자는 loop
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
N, T, SLOW = 1000, 1e-3, 4.2                                         # 1000 cycles of the lesson's 1 kHz loop, played 4.2x slower
starts = {rel: m.simulate(N, T=T, relative=rel)[0] for rel in (True, False)}   # relative=True sleeps T after the work
Q0, Q1 = np.array([0.0, 0.8]), np.array([1.75, -0.9])                # the arm sweeps from low to up as the iteration count runs 0..N-1
sc = kit.setup(starts[True][-1] * SLOW + 0.5)
arms = {rel: kit.arm("arm", (0.4, 0.4), "blue" if rel else "green", 0.25) for rel in (True, False)}
for rel, (root, _) in arms.items():
    root.location = (-0.95 if rel else 0.95, 0, 0)
    hand = (0.4 * np.cos(Q1[0]) + 0.51 * np.cos(Q1.sum()), 0.25 + 0.4 * np.sin(Q1[0]) + 0.51 * np.sin(Q1.sum()))   # where the sweep ends
    kit.ball("goal", 0.05, (root.location.x + hand[0], 0, hand[1]), "amber")
for f in range(sc.frame_start, sc.frame_end + 1):
    for rel, (root, joints) in arms.items():
        i = max(int(np.searchsorted(starts[rel], (f - 1) / 24 / SLOW, "right")) - 1, 0)   # the cycle the loop has reached
        u = i / (N - 1)
        kit.pose(joints, f, Q0 + (Q1 - Q0) * (3 * u * u - 2 * u ** 3))
kit.camera((0.3, -3.1, 2.2), (0.3, 0.0, 0.45), lens=40)
kit.render(__file__)
