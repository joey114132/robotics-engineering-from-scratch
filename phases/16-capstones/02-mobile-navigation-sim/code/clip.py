# 레슨 16/02 클립: 같은 경로를 두 로버가 간다. 파란 로버는 오도메트리만 믿고 첫 벽에 닿고, 초록 로버는 landmark 보정으로 틈을 지나간다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, RS, T0, SPEED, DT, START, GOAL = 0.45, 0.7, 7.0, 1.0, 0.05, (1.5, 1.5), (9.0, 8.5)   # 1 m drawn as 0.45; rover drawn at 0.7 size; the clip shows driving seconds 7 to 12.5 at real speed; the lesson's start and goal
BAD = dict(scale_err=0.03, w_bias=0.03, sigma=0.02)
world = m.make_world()
occ = m.inflate(world)
path = m.plan(occ, START, GOAL)[1]
runs = {fix: m.drive(path, (START[0], START[1] + (0.5 if fix else -0.5), 0.0), **BAD, **({"landmarks": m.LANDMARKS} if fix else {})) for fix in (False, True)}   # side by side, 1 m apart
wc = np.argwhere(world)
lo = wc[:, ::-1] * m.RES                                                # x, y of each wall cell's corner
gap = lambda p: np.hypot(*np.maximum(np.maximum(lo - p, p - lo - m.RES), 0).T).min()   # distance from p to the nearest wall cell
crash = next(k for k, q in enumerate(runs[False][0][:, :2]) if gap(q) < 0.19 * RS / S)   # the blue body touches a wall: stop it there

sc = kit.setup(5.5)
seen = np.zeros_like(world)
for r, c in zip(*np.nonzero(world)):                                    # the room: the wall cells merged into a few blocks
    if seen[r, c]:
        continue
    c1 = c
    while c1 + 1 < world.shape[1] and world[r, c1 + 1] and not seen[r, c1 + 1]:
        c1 += 1
    r1 = r
    while r1 + 1 < world.shape[0] and world[r1 + 1, c:c1 + 1].all() and not seen[r1 + 1, c:c1 + 1].any():
        r1 += 1
    seen[r:r1 + 1, c:c1 + 1] = True
    kit.box("wall", ((c1 - c + 1) * m.RES * S, (r1 - r + 1) * m.RES * S, 0.2), ((c + c1 + 1) / 2 * m.RES * S, (r + r1 + 1) / 2 * m.RES * S, 0.1), "grey", bevel=0.01)
kit.tube("route", [(x * S, y * S, 0.012) for x, y in path], 0.012, "sky")
kit.cyl("goal", 0.13, 0.012, (GOAL[0] * S, GOAL[1] * S, 0.006), "z", "amber")
for p in m.LANDMARKS:
    kit.cyl("beacon", 0.02, 0.4, (p[0] * S, p[1] * S, 0.2), "z", "dark")
    kit.ball("beacon-top", 0.05, (p[0] * S, p[1] * S, 0.42), "navy")

ghost = kit.ghost("blue", 0.55)
for fix, col in ((False, "blue"), (True, "green")):
    traj, belief = runs[fix]
    root, wheels = kit.rover("rover", col)
    root.scale = (RS,) * 3
    yaw = np.unwrap(traj[:, 2])
    turn = np.r_[np.diff(yaw) / DT, 0.0]
    spin = [np.cumsum((S * 0.6 + sgn * turn * 0.2 * RS) * DT) / (0.075 * RS) for sgn in (-1, 1)]   # wheel rim speeds from the lesson's speed and turn rate
    if not fix:
        bel, _ = kit.rover("belief", "blue")
        bel.scale = (RS,) * 3
        for ob in bel.children_recursive:
            ob.data.materials.clear()
            ob.data.materials.append(ghost)
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = min(int((T0 + (f - 1) / sc.render.fps * SPEED) / DT), len(traj) - 1, crash if not fix else 10**9)
        kit.key(root, f, loc=(traj[k, 0] * S, traj[k, 1] * S, 0), rot=(0, 0, traj[k, 2]))
        for w, a in zip(wheels, (spin[0][k], spin[1][k])):
            kit.key(w, f, rot=(0, a, 0))
        if not fix:
            kit.key(bel, f, loc=(belief[k, 0] * S, belief[k, 1] * S, 0), rot=(0, 0, belief[k, 2]))
kit.camera((1.6, 0.87, 0.99), (1.6, 2.45, 0.0), lens=42)   # fixed on the first wall
kit.render(__file__)
