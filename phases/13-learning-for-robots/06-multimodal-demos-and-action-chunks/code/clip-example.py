# 레슨 13/06 예시 클립: 같은 출발점에서 한 걸음씩 시연을 다시 고르는 표본기(파랑, H=1)는 흔들리고 8걸음 청크를 따라가는 표본기(초록)는 매끄럽게 간다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)


def play(root, wheels, path, f0, df, end, s=0.8, k=1):
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


END, DF, STEPS, START = 118, 2.9, 32, np.array([-1.0, 0.0])   # the first 32 steps, 2.9 frames a step; they stop short of the goal, where the two rovers would overlap
P, A = m.demos(6, np.random.default_rng(0))             # six demonstrations over the disc and six mirrored under it
single = m.rollout_chunks(P, A, START, 1, 0, np.random.default_rng(3))[:STEPS + 1]    # chunk length 1: a new demonstration is picked every step (jitter 0.037 over 60 steps)
chunked = m.rollout_chunks(P, A, START, 8, 4, np.random.default_rng(9))[:STEPS + 1]   # chunk length 8, overlap 4 (jitter 0.011 over 60 steps)

sc = kit.setup(END / 24)
kit.cyl("keepout", m.R_OBST, 0.004, (0, 0, 0.003), "z", kit.ghost("grey", 0.45))
kit.cyl("pillar", m.R_OBST - 0.16, 0.22, (0, 0, 0.11), "z", "dark")
kit.cyl("goal", 0.1, 0.008, (*m.GOAL, 0.004), "z", "amber")
for p in P:
    kit.tube("demo", [(x, y, 0.012) for x, y in p], 0.007, "grey")
play(*kit.rover("single", "blue"), single, 6, DF, END, k=0)               # no smoothing: the heading shows every flip of the sampled action
play(*kit.rover("chunked", "green"), chunked, 6, DF, END)
kit.camera((0.0, -2.7, 2.5), (0.0, 0.0, 0.0), lens=42)
kit.render(__file__)
