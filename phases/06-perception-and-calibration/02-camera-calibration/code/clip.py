# 레슨 06/02 클립: 스탠드 위 카메라 앞에서 체커보드가 기울어진 여섯 자세를 거치고, 보정한 K 와 카탈로그 K 가 같은 픽셀을 3D 로 되돌린 위치를 비교한다
import pathlib
import sys

import numpy as np
from mathutils import Matrix

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
TRUE = dict(fx=620.0, fy=580.0, cx=330.0, cy=235.0)
NOMINAL = dict(fx=600.0, fy=600.0, cx=320.0, cy=240.0)         # what a datasheet would say
views = m.make_views(TRUE, 6, 0.5, 1)                          # the lesson's own six views (seed 1, 0.5 px noise)
est = m.calibrate([m.homography_dlt(xy, uv) for xy, uv in views])
LENS = np.array([0.0, 0.0, 0.6])
MCW = np.array([[0, 0, 1.0], [-1, 0, 0], [0, -1, 0]])          # camera frame (x right, y down, z forward) to world
rng = np.random.default_rng(1)                                 # the same draws make_views used for each board pose
poses = []
for _ in range(6):
    R = m.rodrigues(rng.uniform(-0.5, 0.5, 3))
    poses.append((R, np.array([*rng.uniform(-0.05, 0.05, 2), rng.uniform(0.5, 0.9)])))
    rng.normal(0, 0.5, (35, 2))
xy, uv = views[0]
chk = np.array([[TRUE["fx"], 0, TRUE["cx"]], [0, TRUE["fy"], TRUE["cy"]], [0, 0, 1.0]]) @ (poses[0][0][:, :2] @ xy.T + poses[0][1][:, None])
assert np.abs((chk[:2] / chk[2]).T - uv).max() < 3, "poses do not match the lesson's views"

sc = kit.setup(6)
kit.cyl("stand", 0.02, 0.6, (0, 0, 0.3), "z", "grey"); kit.cyl("foot", 0.15, 0.02, (0, 0, 0.01), "z", "dark", bevel=0.008)
kit.box("cam", (0.14, 0.1, 0.08), (-0.02, 0, 0.6), "dark", bevel=0.015); kit.cyl("lens", 0.032, 0.06, (0.08, 0, 0.6), "x", "grey")
board = kit.empty("board")
kit.box("sheet", (0.48, 0.36, 0.01), (0, 0, 0), "pearl", bevel=0, parent=board)
kit.cyl("handle", 0.016, 0.26, (0, -0.31, 0), "y", "grey", parent=board)   # a paddle handle, so the board is held by something
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
    for f in (8 + 18 * k, 14 + 18 * k):                        # arrive, then hold still while the camera takes the picture
        board.location, board.rotation_quaternion = tuple(LENS + MCW @ t), q
        board.keyframe_insert("location", frame=f)
        board.keyframe_insert("rotation_quaternion", frame=f)
px = (600.0, 441.6)                                            # one pixel near the image edge, depth 1.6 m, on the floor
for name, K, colour, f0 in (("true", TRUE, "amber", 112), ("nominal", NOMINAL, "blue", 118), ("calibrated", est, "green", 124)):
    p = LENS + MCW @ np.array([(px[0] - K["cx"]) * 1.6 / K["fx"], (px[1] - K["cy"]) * 1.6 / K["fy"], 1.6])
    b = kit.ball(name, 0.04, tuple(p), colour)
    kit.key(b, f0 - 1, loc=tuple(p)); b.scale = (0.001,) * 3; b.keyframe_insert("scale", frame=f0 - 1)
    b.scale = (1, 1, 1); b.keyframe_insert("scale", frame=f0 + 6)
kit.camera((-1.15, -0.65, 1.35), (0.9, -0.12, 0.5), lens=34)
kit.render(__file__)
