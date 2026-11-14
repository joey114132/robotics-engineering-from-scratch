# 레슨 03/03 클립: 같은 K 의 임피던스 관절을 같은 힘으로 누른다. 파란 팔은 damping 이 약해 출렁이고, 초록 팔은 zeta=1 로 한 번에 멈춘다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import math

import kit

m = kit.lesson_main(__file__)
J, K, F, DT, N, SHOW, PUSH, SLOW = 1.0, 100.0, 2.0, 1e-3, 2500, 12.0, 4, 2.5     # the lesson's joint; deflection drawn 12 times larger; push at frame 4; played at 0.4 speed
runs = {z: m.simulate(J, K, m.damping_for_zeta(K, J, z), F, DT, N) for z in (0.2, 1.0)}
Z0 = 0.4 + 0.5                                                          # joint height: table plus a tall pedestal

sc = kit.setup(5.0)
kit.table((2.5, 0.8), 0.4, (0.05, 0))
for z, c, x in ((0.2, "blue", -1.0), (1.0, "green", 0.2)):
    root, joints = kit.arm(c, (0.4, 0.4), c, base_height=0.5)
    root.location = (x, 0, 0.4)
    rest = -SHOW * F / K                                                # where the push alone (F / K) holds the arm
    kit.ball(c + "-rest", 0.035, (x + 0.94 * math.cos(rest), 0, Z0 + 0.94 * math.sin(rest)), kit.ghost("amber", 0.55))
    push = kit.arrow(c + "-push", "red")
    push.rotation_euler = (0, math.pi / 2, 0)
    for f in range(sc.frame_start, sc.frame_end + 1):
        q = -SHOW * runs[z][min(int((f - PUSH) / 24 / SLOW / DT), N - 1)] if f >= PUSH else 0.0
        kit.pose(joints, f, [q, 0.0])
        push.scale = (0.45, 1, 1) if f >= PUSH else (1e-3,) * 3
        push.location = (x + 0.8 * math.cos(q), 0, Z0 + 0.8 * math.sin(q) + 0.07 + 0.45)   # its tip rests on the hand
        for p in ("location", "scale"):
            push.keyframe_insert(p, frame=f)
kit.camera((0.05, -2.9, 2.3), (0.05, 0, 0.85), lens=40)
kit.render(__file__)
