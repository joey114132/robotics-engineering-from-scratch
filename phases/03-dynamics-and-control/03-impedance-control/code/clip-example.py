# 레슨 03/03 예시 클립: 같은 힘으로 눌러도 K 가 두 배인 팔(초록)은 처짐이 절반이다. 둘 다 zeta=1 이라 넘치지 않는다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import math

import kit

m = kit.lesson_main(__file__)
J, F, DT, N, SHOW, PUSH, SLOW = 1.0, 2.0, 1e-3, 1500, 15.0, 12, 3     # the lesson's joint and push; deflection drawn 15 times larger; push at frame 12; played at one-third speed
KS = {"blue": 100.0, "green": 200.0}                                   # F / K = 0.02 and 0.01 rad; zeta = 1 for both, so D = 2 sqrt(K J)
runs = {c: m.simulate(J, K, m.damping_for_zeta(K, J, 1.0), F, DT, N) for c, K in KS.items()}
Z0 = 0.4 + 0.5                                                          # joint height: table plus a tall pedestal

sc = kit.setup(3.5)
kit.table((2.5, 0.8), 0.4, (0.05, 0))
for c, x in (("blue", -1.0), ("green", 0.2)):
    root, joints = kit.arm(c, (0.4, 0.4), c, base_height=0.5)
    root.location = (x, 0, 0.4)
    rest = -SHOW * F / KS[c]                                            # where the push alone (F / K) holds the arm
    kit.ball(c + "-rest", 0.035, (x + 0.94 * math.cos(rest), 0, Z0 + 0.94 * math.sin(rest)), kit.ghost("amber", 0.55))
    push = kit.arrow(c + "-push", "red")
    push.rotation_euler = (0, math.pi / 2, 0)
    for f in range(sc.frame_start, sc.frame_end + 1):
        q = -SHOW * runs[c][min(int((f - PUSH) / 24 / SLOW / DT), N - 1)] if f >= PUSH else 0.0
        kit.pose(joints, f, [q, 0.0])
        push.scale = (0.45, 1, 1) if f >= PUSH else (1e-3,) * 3
        push.location = (x + 0.8 * math.cos(q), 0, Z0 + 0.8 * math.sin(q) + 0.07 + 0.45)   # its tip rests on the hand
        for p in ("location", "scale"):
            push.keyframe_insert(p, frame=f)
kit.camera((0.05, -2.9, 2.3), (0.05, 0, 0.85), lens=40)
kit.render(__file__)
