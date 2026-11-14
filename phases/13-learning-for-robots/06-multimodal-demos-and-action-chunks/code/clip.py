# 레슨 13/06 클립: 두 갈래 시연을 평균 내면(파랑) 기둥으로 직진해 부딪히고, 청크 표본기(초록)는 한쪽을 골라 끝까지 돈다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)


def play(root, wheels, path, f0, df, end, s=0.8, k=2):
    """Key a rover along an (n, 2) path, one point every df frames: heading from the motion, wheels from the distance each rolls."""
    p = np.asarray(path, float)
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
        kit.key(root, f, loc=(*q[i], 0), rot=(0, 0, h[i]))
        for w, r in zip(wheels, roll):
            kit.key(w, f, rot=(0, r[i], 0))


END, STEPS, DF, START = 130, 42, 1.8, np.array([-1.0, 0.0])
P, A = m.demos(6, np.random.default_rng(0))             # six demonstrations over the disc and six mirrored under it
blue = m.rollout_mean(m.mean_policy(P, A), START)       # the averaged policy
blue = blue[:np.argmax(np.linalg.norm(blue, axis=1) < m.R_OBST) + 1]                          # it stops where it touches the pillar
greens = [m.rollout_chunks(P, A, START, 8, 4, np.random.default_rng(s))[:STEPS] for s in (0, 1)]   # two samples of the chunk sampler

sc = kit.setup(END / 24)
kit.cyl("keepout", m.R_OBST, 0.004, (0, 0, 0.003), "z", kit.ghost("grey", 0.45))
kit.cyl("pillar", m.R_OBST - 0.16, 0.22, (0, 0, 0.11), "z", "dark")
kit.cyl("goal", 0.1, 0.008, (*m.GOAL, 0.004), "z", "amber")
for p in P:
    kit.tube("demo", [(x, y, 0.012) for x, y in p], 0.007, "grey")
play(*kit.rover("mean", "blue"), blue, 6, DF, END)             # all three play at 1.8 frames per step
for i, g in enumerate(greens):                           # the second sampler run starts 9 steps later, so the two never overlap
    root, wheels = kit.rover(f"chunk{i}", "green")
    f0 = 34 + 16 * i
    play(root, wheels, g, f0, DF, END)
    for f, sc_ in ((1, 0.0), (f0 - 6, 0.0), (f0, 0.8)):      # each run appears when its turn starts
        root.scale = (sc_,) * 3
        root.keyframe_insert("scale", frame=f)
kit.camera((0.0, -2.7, 2.5), (0.0, 0.0, 0.0), lens=42)
kit.render(__file__)
