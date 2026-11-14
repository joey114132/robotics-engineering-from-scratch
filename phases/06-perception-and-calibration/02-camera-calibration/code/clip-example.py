# 레슨 06/02 예시 클립: 카메라 두 대 앞에서 체커보드를 네 번 놓는다. 파란 쪽은 밀기만 해서 calibrate() 가 degenerate 로 거부하고, 초록 쪽은 매번 다르게 기울여서 K 가 풀린다
import pathlib
import sys

import numpy as np
from mathutils import Matrix

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
K = dict(fx=620.0, fy=580.0, cx=330.0, cy=235.0)
LENS = np.array([0.0, 0.0, 0.6])
MCW = np.array([[0, 0, 1.0], [-1, 0, 0], [0, -1, 0]])          # camera frame (x right, y down, z forward) to world
cases = {}
for tilt, colour, y in ((0.0, "blue", -0.75), (0.5, "green", 0.75)):   # the lesson's test case: 4 views, seed 3, shifted only or tilted
    views = m.make_views(K, 4, 0.0, 3, tilt=tilt)
    try:
        m.calibrate([m.homography_dlt(xy, uv) for xy, uv in views])
        solved = True
    except ValueError:
        solved = False
    rng, poses = np.random.default_rng(3), []                   # the same draws make_views used for each board pose
    for _ in range(4):
        poses.append((m.rodrigues(rng.uniform(-tilt, tilt, 3)), np.array([*rng.uniform(-0.05, 0.05, 2), rng.uniform(0.5, 0.9)])))
        rng.normal(0, 0.0, (35, 2))
    cases[colour] = (y, poses, solved)
assert (cases["blue"][2], cases["green"][2]) == (False, True)

sc = kit.setup(5)
for colour, (y, poses, solved) in cases.items():
    cam = np.array([0.0, y, 0.0])
    kit.cyl("stand", 0.02, 0.6, tuple(cam + (0, 0, 0.3)), "z", "grey"); kit.cyl("foot", 0.15, 0.02, tuple(cam + (0, 0, 0.01)), "z", "dark", bevel=0.008)
    kit.box("cam", (0.14, 0.1, 0.08), tuple(cam + (-0.02, 0, 0.6)), "dark", bevel=0.015); kit.cyl("lens", 0.032, 0.06, tuple(cam + (0.08, 0, 0.6)), "x", "grey")
    board = kit.empty("board-" + colour)
    kit.box("sheet", (0.48, 0.36, 0.01), (0, 0, 0), "pearl", bevel=0, parent=board)
    kit.cyl("handle", 0.016, 0.26, (0, -0.31, 0), "y", colour, parent=board)
    for sx, sy, w, h in ((0, 0.19, 0.5, 0.02), (0, -0.19, 0.5, 0.02), (0.25, 0, 0.02, 0.4), (-0.25, 0, 0.02, 0.4)):
        kit.box("rim", (w, h, 0.014), (sx, sy, 0), colour, bevel=0, parent=board)
    for i in range(8):
        for j in range(6):
            if (i + j) % 2 == 0:
                for s in (1, -1):
                    kit.box("sq", (0.06, 0.06, 0.002), ((i - 3.5) * 0.06, (j - 2.5) * 0.06, s * 0.0055), "dark", bevel=0, parent=board)
    board.rotation_mode = "QUATERNION"
    prev = None
    for k, (R, t) in enumerate(poses):
        q = Matrix((MCW @ R).tolist()).to_quaternion()
        if prev is not None:
            q.make_compatible(prev)
        prev = q
        for f in (8 + 20 * k, 16 + 20 * k):                     # arrive, then hold still while the camera takes the picture
            board.location, board.rotation_quaternion = tuple(cam + LENS + MCW @ t), q
            board.keyframe_insert("location", frame=f)
            board.keyframe_insert("rotation_quaternion", frame=f)
    marks = [kit.ball("solved", 0.07, tuple(cam + (0, 0, 1.2)), "green")] if solved else \
        [kit.box("cross", (0.012, 0.22, 0.05), tuple(cam + (0, 0, 1.2)), "red", bevel=0.004) for _ in (0, 1)]
    for n, ob in enumerate(marks):                              # the verdict appears after the fourth view: a green ball, or a red cross
        if not solved:
            ob.rotation_euler = (0.7854 * (1 if n else -1), 0, 0)
        ob.scale = (0.001,) * 3; ob.keyframe_insert("scale", frame=84)
        ob.scale = (1, 1, 1); ob.keyframe_insert("scale", frame=92)
        ob.keyframe_insert("rotation_euler", frame=84) if not solved else None
kit.camera((-2.3, 0.0, 1.7), (0.6, 0.0, 0.72), lens=36)
kit.render(__file__)
