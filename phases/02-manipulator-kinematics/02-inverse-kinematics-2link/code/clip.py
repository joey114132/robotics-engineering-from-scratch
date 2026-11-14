# 레슨 02/02 클립: 같은 표적을 elbow-down(파랑)과 elbow-up(초록) 팔이 함께 찍고, 표적이 멀어지면 ik()가 거절해 팔이 멈춘다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, HOLD, SLIDE = 5.5, 0.8, 3.4          # touch the lesson's target (0.6, 0.3), then slide it outward along y = 0.3
L, Y, X0, X1 = (0.5, 0.4), 0.3, 0.6, 1.0
sc = kit.setup(SECONDS)
kit.table((3.0, 0.7), 0.4, (-0.15, 0))
arms = {}
for elbow, colour, x in (("down", "blue", -1.3), ("up", "green", 0.0)):
    root, js = kit.arm(elbow, L, colour)
    root.location = (x, 0, 0.4)
    arms[elbow] = (js, x, kit.ball(elbow + "-goal", 0.05, colour="amber"), kit.ball(elbow + "-lost", 0.05, colour="red"))
last, refused = {e: m.ik((X0, Y), L, e) for e in arms}, None
for f in range(sc.frame_start, sc.frame_end + 1):
    s = np.clip(((f - 1) / sc.render.fps - HOLD) / SLIDE, 0, 1)
    x = X0 + (X1 - X0) * s * s * (3 - 2 * s)                  # the target slides out; the ball rides a little past it
    for elbow, (js, base, goal, lost) in arms.items():
        try:
            last[elbow] = m.ik((x, Y), L, elbow)
        except ValueError:                                    # out of reach: ik() refuses, the arm keeps its last answer
            refused = refused or f
        q = last[elbow]
        kit.pose(js, f, q)
        ball = (base + x + 0.04, 0, 0.7 + Y)
        for b, on in ((goal, refused is None), (lost, refused is not None)):
            b.location, b.scale = ball, (1 if on else 0,) * 3
            b.keyframe_insert("location", frame=f)
            b.keyframe_insert("scale", frame=f)
kit.camera((-0.15, -3.75, 2.1), (-0.15, 0, 0.95), lens=50)
kit.render(__file__)
