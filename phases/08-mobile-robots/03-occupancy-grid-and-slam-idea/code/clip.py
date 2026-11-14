# 레슨 08/03 클립: 같은 방을 도는 로버 두 대. 초록은 알려진 자세로, 파랑은 heading이 번진 자세로 occupancy grid를 쌓는다
import pathlib
import sys

import bpy
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, GAP, PLAY, FPS = 0.25, 3.0, 4.4, 24                          # 1 m drawn as 0.25 m; x offset of the second room
world, tp = m.make_world(), m.loop_poses()
est = {"good": tp, "drift": m.drift(tp, 0.003)}                 # the lesson's drift: 0.003 rad more heading error every step
ang, rng = np.linspace(-np.pi, np.pi, 180, endpoint=False), {k: np.random.default_rng(0) for k in est}
cs = m.RES * S                                                  # drawn cell size

sc = kit.setup(PLAY + 0.8)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "CONSTANT"
rooms = {"good": 0.0, "drift": GAP}
for ox in rooms.values():                                       # the true walls, flat on the floor: the map should land on them
    kit.stripe(ox, ox + 10 * S, 0, 10 * S, "road")
    kit.stripe(ox + cs, ox + 10 * S - cs, cs, 10 * S - cs, "floor")
    kit.stripe(ox + 4 * S, ox + 6 * S, 4 * S, 6 * S, "road")
rovers = {"good": kit.rover("good", "green"), "drift": kit.rover("drift", "blue")}
belief = kit.cyl("belief", 0.19, 0.1, (0, 0, 0.11), "z", kit.ghost("blue", 0.6))
for r, _ in rovers.values():
    r.scale = (0.8,) * 3
belief.scale = (0.8,) * 3
tiles, L = {}, {k: np.zeros((m.N, m.N)) for k in est}
last = {k: np.zeros(m.N * m.N, bool) for k in est}
n_frames = int(PLAY * FPS)
done = 0
for f in range(1, sc.frame_end + 1):
    target = min(int((f / n_frames) * len(tp)), len(tp))         # scans taken so far
    for k in est:
        for i in range(done, target):
            L[k] = m.update(L[k], est[k][i], m.scan(world, tp[i], ang, sigma=0.03, rng=rng[k]), ang)
        occ = (L[k] > 0).ravel()
        for c in np.nonzero(occ != last[k])[0]:
            if (k, c) not in tiles:
                t = kit.box("tile", (cs * 0.95, cs * 0.95, 0.04), (rooms[k] + (c % m.N + 0.5) * cs, (c // m.N + 0.5) * cs, 0.02), "amber", bevel=0)
                t.scale = (0, 0, 0)
                t.keyframe_insert("scale", frame=1)
                tiles[k, c] = t
            tiles[k, c].scale = (1, 1, 1) if occ[c] else (0, 0, 0)
            tiles[k, c].keyframe_insert("scale", frame=f)
        last[k] = occ
    done = max(done, target)
    i = min(target, len(tp) - 1)
    for k, (root, wheels) in rovers.items():
        kit.key(root, f, loc=(rooms[k] + tp[i, 0] * S, tp[i, 1] * S, 0), rot=(0, 0, tp[i, 2]))
    kit.key(belief, f, loc=(rooms["drift"] + est["drift"][i, 0] * S, est["drift"][i, 1] * S, 0), rot=(0, 0, est["drift"][i, 2]))
kit.camera((GAP / 2 + 1.25, -0.9, 6.7), (GAP / 2 + 1.25, 1.25, 0.0), lens=37)
kit.render(__file__)
