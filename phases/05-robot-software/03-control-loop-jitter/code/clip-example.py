# 레슨 05/03 예시 클립: i*T 까지 자는 loop 의 팔. 호박색 공은 제시간에 도착했을 명령, 팔은 실제 wake-up 시각의 명령을 따른다. 1.5 ms 늦은 한 번에 팔만 뒤처진다
import bisect
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
N, T, SLOW, I0, STEPS = 5000, 1e-3, 450, 2094, 10                   # the lesson's seeded run; 11 cycles around its worst wake-up, played 450x slower
s, _ = m.simulate(N, T=T, spike_p=0.003)                            # relative=False: sleep until i*T
late = (s - np.arange(N) * T)[I0:I0 + STEPS + 1]
assert abs(late.max() - 1.5e-3) < 1e-4 and late.argmax() == 4       # cycle 2098 wakes 1.5 ms late, the others under 0.1 ms
wake = s[I0:I0 + STEPS + 1] - I0 * T                                # when each command really goes out, from the first cycle's slot
Q0, Q1 = np.array([0.0, 0.8]), np.array([1.75, -0.9])               # the sweep is drawn as 10 cycles long so that 1.5 ms is visible
q = lambda i: Q0 + (Q1 - Q0) * i / STEPS
hand = lambda a: (0.4 * np.cos(a[0]) + 0.51 * np.cos(a.sum()), 0.25 + 0.4 * np.sin(a[0]) + 0.51 * np.sin(a.sum()))
sc = kit.setup((STEPS + 1) * T * SLOW + 0.5)
root, joints = kit.arm("arm", (0.4, 0.4), "blue", 0.25)
goal = kit.ball("goal", 0.06, (0, 0, 0), "amber")
for f in range(sc.frame_start, sc.frame_end + 1):
    t = min((f - 1) / 24 / SLOW, (STEPS + 1) * T)
    on_time = min(int(t / T), STEPS)                                # the command that should have gone out by now
    sent = max(bisect.bisect_right(wake, t) - 1, 0)                 # the command that really has
    kit.pose(joints, f, q(sent))
    x, z = hand(q(on_time))
    kit.key(goal, f, loc=(x, -0.14, z))
kit.camera((0.4, -2.4, 1.7), (0.4, 0.0, 0.62), lens=40)
kit.render(__file__)
