# 레슨 13/05 클립: 격자 위 로버. 타일의 높이와 색이 value iteration 의 V 를 따라 목표에서 퍼지고, 로버가 미끄러지며 탐욕 정책을 따라간다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)


def play(root, wheels, path, f0, df, end, s=0.8, k=2, zs=None):
    """Key a rover along an (n, 2) path, one point every df frames: heading from the motion, wheels from the distance each rolls."""
    p = np.asarray(path, float)
    zs = np.zeros(len(p)) if zs is None else zs
    q = np.array([p[max(0, i - k):i + k + 1].mean(0) for i in range(len(p))])
    v = np.vstack([q[1:] - q[:-1], [0, 0]])
    h = np.where(np.hypot(*v.T) > 1e-4, np.arctan2(v[:, 1], v[:, 0]), np.nan)
    h[:np.argmax(~np.isnan(h))] = h[np.argmax(~np.isnan(h))]
    for i in range(1, len(h)):
        h[i] = h[i - 1] if np.isnan(h[i]) else h[i]
    h = np.unwrap(h)
    d, dh = np.r_[0, np.hypot(*(q[1:] - q[:-1]).T)], np.r_[0, np.diff(h)]
    roll = [np.cumsum(d - dh * 0.2 * s) / (0.075 * s), np.cumsum(d + dh * 0.2 * s) / (0.075 * s)]
    root.scale = (s,) * 3
    for f, i in [(1, 0)] * (f0 > 1) + [(int(f0 + i * df), i) for i in range(len(q))] + [(end, len(q) - 1)]:
        kit.key(root, f, loc=(*q[i], zs[i]), rot=(0, 0, h[i]))
        for w, r in zip(wheels, roll):
            kit.key(w, f, rot=(0, r[i], 0))


LAYOUT, GAMMA, TILE, END, RIPPLE, STEP = ["......G", ".##.##.", "...X...", ".#.##..", "......."], 0.9, 0.62, 125, 48, 5
model = m.gridworld(LAYOUT, slip=0.2)
V, hist, sweeps = m.value_iteration(model, GAMMA)                  # hist[k] is V after k sweeps; all 29 play in the first 2 s
pi = m.greedy(model, V, GAMMA)
xy = lambda c: ((c[1] - 3) * TILE, (2 - c[0]) * TILE)
height = lambda v: 0.02 + 0.15 * v                                 # drawn height of a tile: 0.15 m per unit of value
sweep_at = lambda f: int(round(sweeps * min(1.0, (f - 1) / RIPPLE)))

sc = kit.setup(END / 24)
good, pale = kit._rgb(kit.PAL["green"]), kit._rgb(kit.PAL["pearl"])
for (i, j), s in model.idx.items():
    cell = LAYOUT[i][j]
    t = kit.box("tile", (TILE * 0.94, TILE * 0.94, 0.3), (*xy((i, j)), 0), {"X": "red", "G": "amber"}.get(cell, "pearl"), bevel=0.03)
    t.location.z = {"X": 0.02, "G": 0.2}.get(cell, 0) - 0.15
    if cell == ".":
        t.data.materials[0] = mat = kit.mat("pearl").copy()
        bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        for f in range(1, RIPPLE + 2, 2):
            v = hist[sweep_at(f)][s]
            t.location.z = height(v) - 0.15
            t.keyframe_insert("location", index=2, frame=f)
            bsdf.inputs["Base Color"].default_value = [a + (b - a) * v / V.max() for a, b in zip(pale, good)]
            bsdf.inputs["Base Color"].keyframe_insert("default_value", frame=f)
for i, row in enumerate(LAYOUT):
    for j, cell in enumerate(row):
        if cell == "#":
            kit.box("wall", (TILE * 0.94, TILE * 0.94, 0.3), (*xy((i, j)), 0.15), "dark", bevel=0.03)
rng, s = np.random.default_rng(30), model.idx[(4, 0)]               # one slippery run of the greedy policy, sampled from the lesson's P
path = [s]
while not model.term[s]:
    s = rng.choice(model.n, p=model.P[pi[s], s])
    path.append(s)
play(*kit.rover("agent", "green")[:2], [xy(model.cells[s]) for s in path], RIPPLE + 2, STEP, END, s=1.0, k=0, zs=[0.2 if model.term[s] else height(V[s]) for s in path])
kit.camera((0.0, -3.3, 4.2), (0.0, -0.05, 0.0), lens=34)
kit.render(__file__)
