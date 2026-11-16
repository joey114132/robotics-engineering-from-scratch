# 레슨 16/03 예시 클립: 같은 학습 정책에 한 step 짜리 40 Nm spike 가 들어온다. 파란 팔은 wrapper 없음, 초록 팔은 있음
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SLOW, TARGET, QLIM, BH, SPIKE, FLASH, OVER = 1.8, 1.0, 1.3, 0.35, 30, 8, 4.0   # 0.56x speed; reach 1 rad; limit 1.3 rad; shoulder height; the lesson's spike step; the arrow stays 8 frames; the part past the limit is drawn 4 times larger
pi = m.fit(*m.demos())
runs = {w: m.rollout(pi, TARGET, safety=m.Safety() if w else None, glitch={SPIKE: 40.0}) for w in (False, True)}   # the lesson's spike run

sc = kit.setup(150 * m.DT * SLOW)
for bx, w, col in ((-1.0, False, "blue"), (0.8, True, "green")):
    root, joints = kit.arm("arm", (0.8,), col, base_height=BH)
    root.location = (bx, 0, 0)
    limit = kit.empty("limit", (bx, 0.12, BH))
    limit.rotation_euler = (0, -QLIM, 0)
    kit.box("limit-bar", (0.95, 0.05, 0.05), (0.575, 0, 0), "#d9541e", bevel=0.008, parent=limit)   # the 1.3 rad joint limit, a fat bar behind the arm
    kit.ball("target", 0.05, (bx + 0.88 * math.cos(TARGET), 0, BH + 0.88 * math.sin(TARGET)), kit.ghost("amber", 0.4))
    push = kit.arrow("push", "red", shaft=0.06)                          # the torque the joint really receives at the spike step, 0.015 m per Nm
    u = float(runs[w]["u"][SPIKE])
    f0 = 1 + int(SPIKE * m.DT * SLOW * sc.render.fps)
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = min(int((f - 1) / sc.render.fps / SLOW / m.DT), 149)
        q = float(runs[w]["q"][k])
        q = QLIM + OVER * (q - QLIM) if q > QLIM else q                  # what is past the limit is drawn OVER times larger, or a 3 degree overshoot cannot be seen
        kit.pose(joints, f, [q])
        tip = (bx + 0.8 * math.cos(q), 0, BH + 0.8 * math.sin(q))
        on = f0 <= f < f0 + FLASH
        push.scale = (max(0.015 * u, 0.001) if on else 0.001, 1, 1)
        push.keyframe_insert("scale", frame=f)
        kit.key(push, f, loc=tip, rot=(0, -(q + math.pi / 2), 0))
kit.camera((0.33, -3.7, 2.3), (0.33, 0, 0.55), lens=43)
kit.render(__file__)
