# 레슨 13/05 예시 클립: 구덩이 바로 오른쪽 타일의 로버. 네 방향 화살표가 sweep 마다 backup 한 행동별 점수를 보여 주고, 가장 높은 점수의 화살표가 초록이 되면 로버가 그쪽으로 한 칸 간다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
LAYOUT, GAMMA, TILE, RIPPLE, END, CELL = ["......G", ".##.##.", "...X...", ".#.##..", "......."], 0.9, 0.62, 72, 135, (2, 4)
model = m.gridworld(LAYOUT, slip=0.2)
V, hist, sweeps = m.value_iteration(model, GAMMA)                  # hist[k] is V after k sweeps
xy = lambda c: ((c[1] - 3) * TILE, (2 - c[0]) * TILE)
height = lambda v: 0.02 + 0.15 * v                                 # drawn height of a tile: 0.15 m per unit of value
sweep_at = lambda f: int(round(sweeps * min(1.0, (f - 1) / RIPPLE)))
s = model.idx[CELL]                                                # the tile just right of the pit
DIRS = [(0, 1), (0, -1), (-1, 0), (1, 0)]                          # up, down, left, right as drawn (x, y): the order of m.MOVES
LEN = 0.5                                                          # a score of 1 is drawn as an arrow 0.5 m long

sc = kit.setup(END / 24)
good, pale = kit._rgb(kit.PAL["green"]), kit._rgb(kit.PAL["pearl"])
for (i, j), t_ in model.idx.items():
    cell = LAYOUT[i][j]
    t = kit.box("tile", (TILE * 0.94, TILE * 0.94, 0.3), (*xy((i, j)), 0), {"X": "red", "G": "amber"}.get(cell, "pearl"), bevel=0.03)
    t.location.z = {"X": 0.02, "G": 0.2}.get(cell, 0) - 0.15
    if cell == ".":
        t.data.materials[0] = mat = kit.mat("pearl").copy()
        bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        for f in range(1, RIPPLE + 2, 2):
            v = hist[sweep_at(f)][t_]
            t.location.z = height(v) - 0.15
            t.keyframe_insert("location", index=2, frame=f)
            bsdf.inputs["Base Color"].default_value = [a + (b - a) * v / V.max() for a, b in zip(pale, good)]
            bsdf.inputs["Base Color"].keyframe_insert("default_value", frame=f)
for i, row in enumerate(LAYOUT):
    for j, cell in enumerate(row):
        if cell == "#":
            kit.box("wall", (TILE * 0.94, TILE * 0.94, 0.3), (*xy((i, j)), 0.15), "dark", bevel=0.03)

cx, cy = xy(CELL)
arrows = {(a, col): kit.arrow(f"q{a}{col}", col, 0.03) for a in range(4) for col in ("blue", "red", "green")}
for (a, col), ob in arrows.items():
    ob.rotation_euler = (0, 0, np.arctan2(DIRS[a][1], DIRS[a][0]))
for f in range(1, RIPPLE + 2, 2):                                  # each move's score Q[a, s] after the sweeps so far, as an arrow along the move
    k = sweep_at(f)
    Q = m.backup(model, hist[k], GAMMA)[:, s]
    best = int(np.argmax(Q)) if k == sweeps else -1
    for (a, col), ob in arrows.items():
        show = a == best if col == "green" else (a != best and (Q[a] >= 0) == (col == "blue"))
        ob.location = (cx + DIRS[a][0] * 0.2, cy + DIRS[a][1] * 0.2, height(hist[k][s]) + 0.05)
        ob.keyframe_insert("location", frame=f)
        ob.scale = (max(abs(Q[a]) * LEN, 0.04), 1, 1) if show else (1e-3, 1e-3, 1e-3)    # a hidden arrow shrinks on every axis, so no arrow head is left behind
        ob.keyframe_insert("scale", frame=f)

root, wheels = kit.rover("agent", "green")                        # it stands on the tile, faces the pit, then turns to the best move and takes it
root.scale = (0.8,) * 3
x1, y1 = xy((2, 5))
z0, z1 = height(V[s]), height(V[model.idx[(2, 5)]])
for f in range(1, RIPPLE + 9, 2):
    kit.key(root, f, loc=(cx, cy, height(hist[sweep_at(f)][s])), rot=(0, 0, np.pi))
kit.key(root, RIPPLE + 30, loc=(cx, cy, z0), rot=(0, 0, 0.0))
kit.key(root, END, loc=(x1, y1, z1), rot=(0, 0, 0.0))
for w in wheels:
    kit.key(w, RIPPLE + 30, rot=(0, 0, 0))
    kit.key(w, END, rot=(0, TILE / (0.075 * 0.8), 0))
kit.camera((0.55, -2.5, 2.6), (0.55, 0.0, 0.1), lens=36)
kit.render(__file__)
