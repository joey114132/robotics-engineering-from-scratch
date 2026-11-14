# 레슨 00/02 클립: 같은 진자를 explicit Euler(파랑)와 semi-implicit Euler(초록)로 계산해 매단 두 추. 파란 추만 점점 높이 올라간다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
DT, TH0, SECONDS = 0.04, 0.5, 5.0       # dt = 0.04 s, the coarsest step of the lesson's step-size sweep
runs = {s: m.simulate(TH0, DT, 14.0, scheme=s) for s in ("explicit", "semi")}
turn = [i for i in range(1, len(runs["explicit"]) - 1) if abs(runs["explicit"][i]) >= abs(runs["explicit"][i - 1]) and abs(runs["explicit"][i]) > abs(runs["explicit"][i + 1])]
END = max(i for i in turn if i * DT <= 6.0)            # stop the blue bob at the top of a swing, about 5 s of simulation
SPEED = END * DT / SECONDS                             # simulated seconds per clip second

sc = kit.setup(SECONDS)
L, PIVOT_Z, X = 0.8, 1.2, 1.05
kit.box("beam", (2 * X + 2.8, 0.12, 0.1), (0, 0, PIVOT_Z + 0.06), "dark")
for sx in (-1, 1):
    kit.box("leg", (0.1, 0.5, PIVOT_Z + 0.1), (sx * (X + 1.3), 0, (PIVOT_Z + 0.1) / 2), "grey", bevel=0.01)
level = kit.box("release-level", (2 * X + 1.4, 0.02, 0.03), (0, 0.1, PIVOT_Z - L * math.cos(TH0)), kit.ghost("amber", 0.8), bevel=0)   # height the bob started at
bobs = {}
for s, x, colour in (("explicit", -X, "blue"), ("semi", X, "green")):
    pivot = kit.empty(s, (x, 0, PIVOT_Z))
    kit.cyl("hub", 0.045, 0.16, (0, 0, 0), "y", "grey", parent=pivot)
    kit.cyl("rod", 0.022, L, (0, 0, -L / 2), "z", "dark", parent=pivot)
    kit.ball("bob", 0.11, (0, 0, -L), colour, parent=pivot)
    bobs[s] = pivot
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int(round((f - 1) / sc.render.fps * SPEED / DT)), END)
    for s, pivot in bobs.items():
        kit.key(pivot, f, rot=(0, -float(runs[s][i]), 0))   # theta from the lesson's simulate(), positive toward +x
kit.camera((0, -5.0, 2.9), (0, 0, 0.75), lens=35)
kit.render(__file__)
