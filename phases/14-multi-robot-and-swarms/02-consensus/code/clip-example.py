# 레슨 14/02 예시 클립: 링에서 이웃 둘만 보는 자동차 한 대(x = 7)가 한 tick에 6.4 쪽으로 돌고, 이어서 이웃 쪽으로 계속 돈다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
X0, EPS, STEPS, UNIT = np.array([4.0, -1.0, 2.0, 7.0, 0.0, 3.0, -5.0, 1.0]), 0.05, 20, 0.25   # the lesson's ring of 8; the clip shows cars 2, 3, 4 of it
LEAD, FIRST, EACH, HOLD = 0.8, 0.8, 0.12, 0.7                                                # the first tick is slowed to 0.8 s so the 7 -> 6.4 turn can be seen
traj = m.run(X0, m.ring(8), EPS, STEPS)
T_END = LEAD + FIRST + (STEPS - 1) * EACH


def tick_at(t):
    """Fractional tick number at clip time t."""
    if t < LEAD:
        return 0.0
    if t < LEAD + FIRST:
        return (t - LEAD) / FIRST
    return min(1 + (t - LEAD - FIRST) / EACH, STEPS)


sc = kit.setup(T_END + HOLD)
kit.box("pad", (4.0, 2.2, 0.02), (0, 0, 0.01), "#e6ecee", bevel=0.01)
spots = {2: (-1.2, 0.0), 3: (0.0, 0.0), 4: (1.2, 0.0)}
for a, b in ((2, 3), (3, 4)):
    kit.tube("link", [(*spots[a], 0.05), (*spots[b], 0.05)], 0.012, "grey")                  # the radio links of car 3
ghost = kit.arrow("start", "grey", 0.03)                                                    # car 3's heading at the start, left in place
ghost.location, ghost.rotation_euler, ghost.scale = (*spots[3], 0.04), (0, 0, UNIT * X0[3]), (1.15, 1, 1)
for ch in ghost.children:
    ch.data.materials[0] = kit.ghost("grey", 0.55)
for i, (x, y) in spots.items():
    root, wheels = kit.rover(f"car{i}", "blue" if i != 3 else "green")
    root.scale = (1.6,) * 3
    pointer = kit.arrow(f"heading{i}", "amber", 0.03)
    pointer.parent, pointer.location, pointer.scale = root, (0, 0, 0.26), (0.42, 1, 1)
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = tick_at((f - 1) / sc.render.fps)
        lo = min(int(k), STEPS - 1)
        th = UNIT * (traj[lo, i] + (traj[lo + 1, i] - traj[lo, i]) * (k - lo))
        kit.key(root, f, loc=(x, y, 0), rot=(0, 0, th))
        kit.key(wheels[0], f, rot=(0, -(th - UNIT * X0[i]) * 0.2 / 0.075, 0))                 # turning in place: the two wheels roll opposite ways
        kit.key(wheels[1], f, rot=(0, (th - UNIT * X0[i]) * 0.2 / 0.075, 0))
kit.camera((0, -2.7, 2.5), (0, 0.0, 0.1), lens=28)
kit.render(__file__)
