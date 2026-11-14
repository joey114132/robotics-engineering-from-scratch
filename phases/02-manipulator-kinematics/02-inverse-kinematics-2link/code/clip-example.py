# 레슨 02/02 예시 클립: 표적이 밑동 둘레를 같은 거리 r 로 돌면 두 elbow 팔의 q2 는 그대로이고 q1 만 따라 돈다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, HOLD, SWEEP = 5.5, 0.6, 4.0          # the target (0.6, 0.3) is r = 0.671 m from the base; it swings from 20 to 77 degrees at that same r
L, PHI0, PHI1, Y = (0.5, 0.4), 0.35, 1.35, 0.1
R = float(np.hypot(0.6, 0.3))
sc = kit.setup(SECONDS)
kit.table((1.9, 0.7), 0.4, (0.15, 0))
arms = {}
for elbow, colour, y in (("down", "blue", -Y), ("up", "green", Y)):   # both bases stand at x = 0, side by side so the two elbows can be told apart
    root, js = kit.arm(elbow, L, colour)
    root.location = (0, y, 0.4)
    arms[elbow] = js
ball = kit.ball("goal", 0.05, colour="amber")
ray = kit.box("r", (R, 0.012, 0.012), (0, 0, 0.7), "dark", bevel=0)   # the third side of the triangle, r, from the base to the target
ray.location = (0, 0, 0.7)
for f in range(sc.frame_start, sc.frame_end + 1):
    s = np.clip(((f - 1) / sc.render.fps - HOLD) / SWEEP, 0, 1)
    phi = PHI0 + (PHI1 - PHI0) * s * s * (3 - 2 * s)
    p = (R * np.cos(phi), R * np.sin(phi))
    for elbow, js in arms.items():
        kit.pose(js, f, m.ik(p, L, elbow))
    kit.key(ball, f, loc=(p[0], 0, 0.7 + p[1]))
    ray.rotation_euler = (0, -phi, 0)
    ray.keyframe_insert("rotation_euler", frame=f)
    ray.location = (R / 2 * np.cos(phi), 0, 0.7 + R / 2 * np.sin(phi))
    ray.keyframe_insert("location", frame=f)
kit.camera((0.22, -2.7, 1.95), (0.22, 0, 0.95), lens=50)
kit.render(__file__)
