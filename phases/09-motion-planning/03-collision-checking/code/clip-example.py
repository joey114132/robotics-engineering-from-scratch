# 레슨 09/03 예시 클립: 기둥 중심에서 0.2 비껴 지나는 경로를 0.5 간격 말뚝으로 검사한다. 기본 검사(파랑)는 놓쳐 차가 기둥을 스치고 s/2 패딩 검사(초록)는 잡아 차가 서 있다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
R, STEP, OFF, FPS = 0.25, 0.5, 0.2, 24                                                          # post radius, peg spacing (= 2r), how far the path passes from the post centre
C = np.array([3.5, 0.0])
A, B = np.array([0.25, OFF]), np.array([6.25, OFF])                                             # pegs fall at 0.25 + 0.5 k: 3.25 and 3.75 sit either side of the post centre
LANES = {"blue": (0.0, 1.05), "green": (STEP / 2, -1.05)}                                       # colour: (padding, lane y)
SWEEP0, SWEEP1, GO, HIT, SECONDS = 0.3, 1.8, 2.0, 3.2, 5.0
X0, X1 = 2.0, 5.0


def appear(ob, frame):
    ob.hide_render = True
    ob.keyframe_insert("hide_render", frame=1)
    ob.hide_render = False
    ob.keyframe_insert("hide_render", frame=frame)


sc = kit.setup(SECONDS)
ring = kit.ghost("amber", 0.55)
for colour, (pad, y) in LANES.items():
    kit.stripe(-2.5, 1.8, y - 0.38, y + 0.38, "road")
    pivot = kit.empty("post-" + colour, (0.0, y, 0.0))
    kit.cyl("post", R, 0.55, (0, 0, 0.275), "z", "dark", bevel=0.01, parent=pivot, segments=48)
    if pad:
        kit.cyl("padding", R + pad, 0.01, (0, y, 0.006), "z", ring, segments=64)                # the circle grown by s/2
    pts = A + np.linspace(0, 1, int(np.ceil(np.linalg.norm(B - A) / STEP)) + 1)[:, None] * (B - A)
    for p in pts[(pts[:, 0] >= X0 - 1e-9) & (pts[:, 0] <= X1 + 1e-9)]:
        col = "red" if m.in_circle(p, C, R + pad) else "white"
        f = int(1 + (SWEEP0 + (SWEEP1 - SWEEP0) * (p[0] - X0) / (X1 - X0)) * FPS)
        appear(kit.cyl("peg", 0.012, 0.65, (p[0] - 3.5, y + OFF, 0.325), "z", col, segments=12), f)
        appear(kit.ball("peg-top", 0.055, (p[0] - 3.5, y + OFF, 0.65), col), f)
    car, wheels, _ = kit.car("car-" + colour, colour)
    clear = not m.swept_hits(A, B, C, R, STEP, pad=pad)                                          # this lane's verdict; the exact test says the segment hits either way
    assert m.seg_hits(A, B, C, R) and clear == (pad == 0.0)
    start = X0 - 3.5 - 0.4
    stop = -math.sqrt(R**2 - (OFF - 0.15) ** 2) - 0.3                                            # the car's near front corner (0.15 to the side of its middle) touches the post
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = float(np.clip(((f - 1) / FPS - GO) / (HIT - GO), 0, 1)) if clear else 0.0
        kit.drive(car, wheels, f, start + k * (stop - start), y + OFF)
    if clear:
        band = kit.cyl("hit", R * 1.06, 0.07, (0, 0, 0.46), "z", "red", parent=pivot, segments=48)
        appear(band, int(HIT * FPS))
        for f, tilt in ((1, 0.0), (int(HIT * FPS), 0.0), (int(HIT * FPS) + 5, 0.22), (int(HIT * FPS) + 12, 0.16)):
            kit.key(pivot, f, rot=(0, tilt, 0))
kit.camera((-0.35, -6.0, 4.4), (-0.35, 0.0, 0.3), lens=55)
kit.render(__file__)
