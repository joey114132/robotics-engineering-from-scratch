# 레슨 13/01 예시 클립: 같은 3-NN 규칙이라도 시연 1개로 배운 로버(파랑)는 기둥에 부딪히고 시연 10개로 배운 로버(초록)는 기둥을 돈다
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


SLOW, STEPS, END = 1.5, 62, 125                              # the first 3.1 s of each rollout play 1.5 times slower
runs = {"one": (1, 0.25, "blue", "#4f8df0"), "ten": (10, -0.25, "green", "#86d3a5")}   # (demonstrations, start y, rover colour, colour of its demo lines)

sc = kit.setup(END / 24)
kit.cyl("keepout", m.R_OBST, 0.004, (0, 0, 0.003), "z", kit.ghost("grey", 0.45))
kit.cyl("pillar", m.R_OBST - 0.16, 0.22, (0, 0, 0.11), "z", "dark")
kit.cyl("goal", 0.1, 0.008, (*m.GOAL, 0.004), "z", "amber")
for name, (n, y0, col, line) in runs.items():
    rng = np.random.default_rng(0)
    X, A = m.collect(rng, n)                                  # the n demonstrations this rover learns from
    for x0 in m.random_starts(np.random.default_rng(0), n):
        kit.tube("demo", [(x, y, 0.012) for x, y in m.rollout(m.expert, x0)[0]], 0.011, line)
    xs, _ = m.rollout(m.fit_knn(X, A), [-1.3, y0], T=STEPS)
    hit = np.nonzero(np.linalg.norm(xs - m.OBST, axis=1) < m.R_OBST)[0]
    xs = xs[:hit[0] + 1] if len(hit) else xs                  # a rover that touches the pillar stops
    play(*kit.rover(name, col), xs, 6, 24 * m.DT * SLOW, END)
kit.camera((0.0, -2.7, 2.5), (0.0, 0.0, 0.0), lens=40)
kit.render(__file__)
