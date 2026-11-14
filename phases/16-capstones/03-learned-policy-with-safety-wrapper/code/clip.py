# 레슨 16/03 클립: 카메라 프레임이 끊긴 동안 같은 학습 정책이 두 팔을 움직인다. 파란 팔은 wrapper 없음, 초록 팔은 있음
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SLOW, TARGET, QLIM, BH = 2.0, 1.0, 1.3, 0.35                          # half speed; reach target 1 rad; joint limit 1.3 rad; shoulder height
pi = m.fit(*m.demos())
runs = {w: m.rollout(pi, TARGET, safety=m.Safety() if w else None, drop=range(10, 36)) for w in (False, True)}   # the lesson's lost-observation run

sc = kit.setup(150 * m.DT * SLOW)
kit.cyl("stand", 0.02, 0.8, (0.35, 0.7, 0.4), "z", "grey")
kit.box("body", (0.18, 0.1, 0.1), (0.35, 0.7, 0.85), "dark", bevel=0.02)
kit.cyl("lens", 0.04, 0.05, (0.35, 0.64, 0.85), "y", "grey")
lamps = [kit.ball("lamp", 0.045, (0.35, 0.7, 0.96), c) for c in (kit.mat("amber", emit=2.0), kit.mat("grey"))]   # amber while frames arrive, grey while they are lost
for bx, w, col in ((-1.0, False, "blue"), (0.8, True, "green")):
    root, joints = kit.arm("arm", (0.8,), col, base_height=BH)
    root.location = (bx, 0, 0)
    limit = kit.empty("limit", (bx, 0.12, BH))
    limit.rotation_euler = (0, -QLIM, 0)
    kit.box("limit-bar", (1.0, 0.025, 0.025), (0.6, 0, 0), "red", bevel=0.004, parent=limit)   # the 1.3 rad joint limit, behind the arm
    kit.ball("target", 0.05, (bx + 0.88 * math.cos(TARGET), 0, BH + 0.88 * math.sin(TARGET)), kit.ghost("amber", 0.4))
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = min(int((f - 1) / sc.render.fps / SLOW / m.DT), 149)
        kit.pose(joints, f, [runs[w]["q"][k]])
        if not w:
            lost = 10 <= k < 36
            for lamp, on in zip(lamps, (not lost, lost)):
                lamp.scale = (1, 1, 1) if on else (0.001,) * 3
                lamp.keyframe_insert("scale", frame=f)
kit.camera((0.33, -3.7, 2.3), (0.33, 0, 0.55), lens=43)
kit.render(__file__)
