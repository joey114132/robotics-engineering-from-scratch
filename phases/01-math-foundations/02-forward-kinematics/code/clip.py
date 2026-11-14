# 레슨 01/02 클립: 같은 관절각을 받는 두 팔. 링크 [1,1] 팔의 손끝은 원판을, [3,1] 팔의 손끝은 가운데가 빈 고리를 채운다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, FPS, U, BASE_H, SWEEP = 6.0, 24, 0.22, 0.95, 125     # drawing scale: 1 lesson unit is 0.22 m; both arms sit on posts tall enough to turn full circles
sc = kit.setup(SECONDS)
kit.camera((0.38, -3.9, 2.55), (0.38, 0.0, 0.85), lens=38)
arms = {}
for name, L, x in (("disc", [1.0, 1.0], -0.65), ("ring", [3.0, 1.0], 0.95)):     # the lesson's two arms: links [1, 1] and [3, 1]
    root, joints = kit.arm(name, [l * U for l in L], "blue", BASE_H)
    root.location = (x, 0, 0)
    arms[name] = (root, joints, L, x)
    lo, hi = m.reach_bounds(L)
    for r in (lo, hi):          # dashed bounds of the lesson, drawn as thin rings behind the arm
        if r > 0:
            pts = [(x + r * U * math.cos(a), 0.2, BASE_H + r * U * math.sin(a)) for a in [i * math.pi / 60 for i in range(121)]]
            kit.tube(name + "-bound", pts, 0.006, "grey")
for f in range(sc.frame_start, sc.frame_end + 1):
    for sub in (0.0, 0.25, 0.5, 0.75):          # four dots per frame, so the path reads as a filled region
        g = f - 1 + sub
        s = min(g / (SWEEP - 1), 1.0)
        q = (2 * math.pi * 2 * s + 0.8, math.radians(172) * math.sin(2 * math.pi * 5 * s))     # both arms get the same joint angles, then rest
        for name, (root, joints, L, x) in arms.items():
            if sub == 0.0:
                kit.pose(joints, f, q)
            if g > SWEEP - 1:
                continue
            tx, ty, _ = m.fk_planar(L, q)       # the tip the lesson computes; a dot is left where it lands
            d = kit.ball(name + "-dot", 0.016, (x + tx * U, 0.2, BASE_H + ty * U), "amber")
            d.scale = (0, 0, 0)
            d.keyframe_insert("scale", frame=max(f - 1, 1))
            d.scale = (1, 1, 1)
            d.keyframe_insert("scale", frame=f)
kit.render(__file__)
