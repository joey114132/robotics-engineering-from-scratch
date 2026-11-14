# 레슨 13/02 예시 클립: 같은 노이즈를 받는 두 로버와 각자 가장 가까운 기록 상태까지의 주황색 선. 단순 복제(파랑)는 선이 길어지고 DAgger(초록)는 짧다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)


def play(root, wheels, path, f0, df, end, s=0.8, k=2):
    """Key a rover along an (n, 2) path, one point every df frames. Returns (frames, smoothed positions) so a tether can follow it."""
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
    frames = [1] * (f0 > 1) + [int(f0 + i * df) for i in range(len(q))] + [end]
    idx = [0] * (f0 > 1) + list(range(len(q))) + [len(q) - 1]
    for f, i in zip(frames, idx):
        kit.key(root, f, loc=(*q[i], 0), rot=(0, 0, h[i]))
        for w, r in zip(wheels, roll):
            kit.key(w, f, rot=(0, r[i], 0))
    return np.array(frames), q[idx]


SLOW, STEPS, END = 1.6, 52, 125                        # the first 2.6 s of each noisy rollout play 1.6 times slower
plain, X_plain = m.dagger(np.random.default_rng(0), 4, 0)    # 4 demonstrations, cloned as they are
fixed, X_dagger = m.dagger(np.random.default_rng(0), 4, 4)   # the same plus 4 rounds of expert relabelling (its data holds the visited states)
runs = {"plain": (plain, X_plain, 0.25, 5, "blue"), "dagger": (fixed, X_dagger, -0.25, 2, "green")}

sc = kit.setup(END / 24)
kit.cyl("keepout", m.R_OBST, 0.004, (0, 0, 0.003), "z", kit.ghost("grey", 0.45))
kit.cyl("pillar", m.R_OBST - 0.16, 0.22, (0, 0, 0.11), "z", "dark")
kit.cyl("goal", 0.15, 0.008, (*m.GOAL, 0.004), "z", "amber")
for x0 in m.starts(np.random.default_rng(0), 4):                                           # the four clean demonstrations
    kit.tube("demo", [(x, y, 0.012) for x, y in m.rollout(m.expert, x0, np.random.default_rng(0), noise=0.0)], 0.007, "grey")
for x, y in X_dagger[480::24]:                                                             # states the DAgger learner visited, one in 24 shown
    if np.hypot(x - m.GOAL[0], y - m.GOAL[1]) > 0.25:
        kit.ball("visited", 0.02, (x, y, 0.02), "#6fcf97")
for name, (pol, X, y0, seed, col) in runs.items():
    xs = m.rollout(pol, [-1.3, y0], np.random.default_rng(seed))[:STEPS]
    hit = np.nonzero(np.linalg.norm(xs - m.OBST, axis=1) < m.R_OBST)[0]
    xs = xs[:hit[0] + 1] if len(hit) else xs
    frames, q = play(*kit.rover(name, col), xs, 6, 24 * m.DT * SLOW, END)
    tether = kit.box("tether", (1.0, 0.045, 0.045), (0, 0, 0.14), "amber", bevel=0.01)
    for f in range(1, END + 1):                                                            # a line from the rover to the nearest recorded state
        p = np.array([np.interp(f, frames, q[:, 0]), np.interp(f, frames, q[:, 1])])
        n = X[np.argmin(((X - p) ** 2).sum(1))]
        ang = np.arctan2(n[1] - p[1], n[0] - p[0])
        kit.key(tether, f, loc=((p[0] + n[0]) / 2, (p[1] + n[1]) / 2, 0.14), rot=(0, 0, ang))
        tether.scale = (max(np.linalg.norm(n - p), 1e-3), 1, 1)
        tether.keyframe_insert("scale", frame=f)
kit.camera((0.0, -2.7, 2.5), (0.0, 0.0, 0.0), lens=40)
kit.render(__file__)
