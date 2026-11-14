# 레슨 00/04 클립: 컵을 따라가는 팔 두 대. 파란 팔은 queue depth 50이라 오래된 메시지를 읽고, 초록 팔은 depth 1이라 최신을 읽는다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, L1, L2, H = 5.0, 0.4, 0.4, 0.4
ages = {d: m.run(100, 40, d, 6.0)["ages"] for d in (50, 1)}   # age of the message each 40 Hz read gets, in seconds
tick = np.arange(len(ages[1])) / 40.0

def smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)

def cup_x(t):                                           # where the cup really is, measured from the arm base
    return 0.5 + 0.17 * math.sin(2 * math.pi * t / 1.6) * (1 - smooth((t - 2.4) / 1.2))

def reach(x):                                           # two-link IK, elbow up, for a hand hovering over a cup at x
    px, pz = x - 0.05, 0.4 + 0.09 + 0.12 - (H + 0.3)
    c2 = (px * px + pz * pz - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    q2 = -math.acos(min(1.0, max(-1.0, c2)))
    return [math.atan2(pz, px) - math.atan2(L2 * math.sin(q2), L1 + L2 * math.cos(q2)), q2]

sc = kit.setup(SECONDS)
kit.table((2.5, 0.7), H, (-0.1, 0))
sta = {}
for depth, bx, colour in ((50, -1.05, "blue"), (1, 0.15, "green")):
    root, joints = kit.arm(f"arm{depth}", (L1, L2), colour)
    root.location = (bx, 0, H)
    kit.box("rail", (0.55, 0.03, 0.006), (bx + 0.5, 0, H + 0.003), "grey", bevel=0)
    cup = kit.cyl("cup", 0.032, 0.09, (0, 0, H + 0.045), "z", "amber")
    seen = kit.cyl("believed-cup", 0.032, 0.09, (0, 0, H + 0.045), "z", kit.ghost("amber", 0.4)) if depth == 50 else None
    sta[depth] = (bx, joints, cup, seen)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps
    for depth, (bx, joints, cup, seen) in sta.items():
        belief = cup_x(t - float(np.interp(t, tick, ages[depth])))   # the arm aims at the cup as it was when the message was sent
        kit.key(cup, f, loc=(bx + cup_x(t), 0, H + 0.045))
        if seen:
            kit.key(seen, f, loc=(bx + belief, 0, H + 0.045))
        kit.pose(joints, f, reach(belief))
kit.camera((-0.1, -3.2, 1.9), (-0.1, 0, 0.5), lens=40)
kit.render(__file__)
