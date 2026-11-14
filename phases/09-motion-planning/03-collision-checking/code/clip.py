# 레슨 09/03 클립: 얇은 기둥 앞에서 샘플 간격 1.0(파랑)은 놓쳐 차가 들이받고, 간격 0.25(초록)는 잡아 차가 출발하지 않는다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
A, B, C, R, FPS = np.array([0.0, 0.0]), np.array([6.0, 0.0]), np.array([3.5, 0.0]), 0.25, 24   # the lesson's segment and post; 1 unit = 1 m
LANES = {"blue": (1.0, 1.05), "green": (0.25, -1.05)}                                          # colour: (sample step, lane y)
SWEEP0, SWEEP1, GO, HIT, SECONDS = 0.3, 1.8, 2.0, 3.2, 5.0
X0, X1 = 2.0, 5.0                                                                              # only this stretch of the 6 m segment is in frame


def appear(ob, frame):
    ob.hide_render = True
    ob.keyframe_insert("hide_render", frame=1)
    ob.hide_render = False
    ob.keyframe_insert("hide_render", frame=frame)


sc = kit.setup(SECONDS)
for colour, (step, y) in LANES.items():
    kit.stripe(-2.5, 1.8, y - 0.38, y + 0.38, "road")
    pivot = kit.empty("post-" + colour, (0.0, y, 0.0))
    kit.cyl("post", R, 0.55, (0, 0, 0.275), "z", "dark", bevel=0.01, parent=pivot, segments=48)
    pts = A + np.linspace(0, 1, int(np.ceil(np.linalg.norm(B - A) / step)) + 1)[:, None] * (B - A)   # the checker's sample points
    for p in pts[(pts[:, 0] >= X0 - 1e-9) & (pts[:, 0] <= X1 + 1e-9)]:
        col, f = "red" if m.in_circle(p, C, R) else "white", int(1 + (SWEEP0 + (SWEEP1 - SWEEP0) * (p[0] - X0) / (X1 - X0)) * FPS)
        appear(kit.cyl("peg", 0.012, 0.65, (p[0] - 3.5, y, 0.325), "z", col, segments=12), f)      # a peg marks each point the checker tests
        appear(kit.ball("peg-top", 0.055, (p[0] - 3.5, y, 0.65), col), f)
    car, wheels, _ = kit.car("car-" + colour, colour)
    clear = not m.swept_hits(A, B, C, R, step)                  # the checker's verdict; the exact test says the segment hits either way
    start = X0 - 3.5 - 0.4                                       # the car waits a little before the first peg
    stop = (C[0] - R - 3.5) - 0.3                                # nose touches the post: root x = post edge minus the nose offset
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = float(np.clip(((f - 1) / FPS - GO) / (HIT - GO), 0, 1)) if clear and m.seg_hits(A, B, C, R) else 0.0
        kit.drive(car, wheels, f, start + k * (stop - start), y)
    if clear:
        band = kit.cyl("hit", R * 1.06, 0.07, (0, 0, 0.46), "z", "red", parent=pivot, segments=48)
        appear(band, int(HIT * FPS))
        for f, tilt in ((1, 0.0), (int(HIT * FPS), 0.0), (int(HIT * FPS) + 5, 0.22), (int(HIT * FPS) + 12, 0.16)):
            kit.key(pivot, f, rot=(0, tilt, 0))
kit.camera((-0.35, -6.0, 4.4), (-0.35, 0.0, 0.3), lens=55)
kit.render(__file__)
