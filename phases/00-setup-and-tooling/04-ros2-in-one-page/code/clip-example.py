# 레슨 00/04 예시 클립: 같은 컵을 따라가는 팔 셋. queue depth 가 1(초록), 10(연한 파랑), 50(파랑)일 때 읽는 메시지가 낡은 만큼 팔이 예전 컵 자리를 향한다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, L1, L2, H = 5.0, 0.4, 0.4, 0.4
DEPTHS = ((1, -1.1, "green"), (10, 0.0, "sky"), (50, 1.1, "navy"))     # base x of each arm, left to right
ages = {d: m.run(100, 40, d, 6.0)["ages"] for d, _, _ in DEPTHS}       # age of the message each 40 Hz read gets, in seconds
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
kit.table((3.5, 0.7), H, (0.35, 0))
rows = {}
for depth, bx, colour in DEPTHS:
    root, joints = kit.arm(f"arm{depth}", (L1, L2), colour)
    root.location = (bx, 0, H)
    for part in root.children_recursive:                       # one colour for the whole arm, so the three depths are easy to tell apart
        if part.name.startswith(f"arm{depth}-link"):
            part.data.materials[0] = kit.mat(colour)
    kit.box("rail", (0.55, 0.03, 0.006), (bx + 0.5, 0, H + 0.003), "grey", bevel=0)
    cup = kit.cyl("cup", 0.06, 0.11, (0, 0, H + 0.055), "z", "amber")
    seen = kit.cyl("believed-cup", 0.066, 0.115, (0, 0, H + 0.058), "z", kit.ghost("amber", 0.6)) if depth > 1 else None
    rows[depth] = (bx, joints, cup, seen)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps
    for depth, (bx, joints, cup, seen) in rows.items():
        belief = cup_x(t - float(np.interp(t, tick, ages[depth])))   # the arm aims at the cup as it was when the message was sent
        kit.key(cup, f, loc=(bx + cup_x(t), 0, H + 0.055))
        if seen:
            kit.key(seen, f, loc=(bx + belief, 0, H + 0.058))
        kit.pose(joints, f, reach(belief))
kit.camera((0.35, -4.0, 2.2), (0.35, 0.0, 0.55), lens=40)
kit.render(__file__)
