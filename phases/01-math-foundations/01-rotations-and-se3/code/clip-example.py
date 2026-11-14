# 레슨 01/01 예시 클립: 같은 사분의 일 회전과 같은 이동 (1, 2, 0). 초록 드론은 제자리에서 돈 뒤 이동하고 파란 드론은 이동한 뒤 돌아서 원점 둘레를 돈다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, FPS, K, Z0 = 5.0, 24, 1.4, 0.25
U = 0.34 * K                                   # drawing scale: 1 lesson unit is the distance from the drone's centre to its nose point
P = np.array([1.0, 2.0, 0.0])                  # the lesson's offset
sc = kit.setup(SECONDS)
kit.camera((-0.04, -1.55, 2.6), (-0.24, 0.35, 0.2), lens=40)


def ease(s):
    s = min(max(s, 0.0), 1.0)
    return s * s * (3 - 2 * s)


def drone(name, colour):
    root, props = kit.drone(name, colour)
    root.scale = (K,) * 3
    kit.cyl(name + "-rod", 0.008, 0.3, (0.17, 0, 0), "x", "dark", parent=root)
    kit.ball(name + "-point", 0.036, (0.34, 0, 0), "amber", parent=root)       # the point (1, 0, 0) carried by the pose
    return root, props


kit.cyl("origin-post", 0.012, Z0 - 0.07, (0, 0, (Z0 - 0.07) / 2), "z", "dark")            # the origin, where both drones start
kit.ball("target", 0.13, (U * P[0], U * P[1], Z0 + U * P[2]), kit.ghost("grey", 0.45))       # the place the pose T is meant to reach
fleet = {"green": drone("turn-then-shift", "green"), "blue": drone("shift-then-turn", "blue")}
for f in range(sc.frame_start, sc.frame_end + 1):
    t = f / FPS
    first, second = ease((t - 0.4) / 1.3), ease((t - 2.2) / 1.3)
    for k, (root, props) in fleet.items():
        if k == "green":       # R x + p: the turn happens in place, then the shift
            a, s = first * np.pi / 2, second
            T = m.make_T(m.rot_z(a), s * P)
            pos, rot = T[:3, 3], a
        else:                  # the factors swapped: shift first, then the turn swings the drone about the origin
            s, a = first, second * np.pi / 2
            pos, rot = m.rot_z(a) @ (s * P), a
        kit.key(root, f, loc=(U * pos[0], U * pos[1], Z0 + U * pos[2]), rot=(0, 0, rot))
        if f % 2 == 0:                                                         # a dot of the drone's centre leaves its path behind
            dot = kit.ball(k + "-trail", 0.022, (U * pos[0], U * pos[1], Z0 + U * pos[2]), "navy" if k == "blue" else "green")
            dot.scale = (0, 0, 0)
            dot.keyframe_insert("scale", frame=max(f - 1, 1))
            dot.scale = (1, 1, 1)
            dot.keyframe_insert("scale", frame=f)
        for i, pr in enumerate(props):
            kit.key(pr, f, rot=(0, 0, (-1) ** i * f * 1.6))
kit.render(__file__)
