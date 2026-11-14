# 레슨 08/03 예시 클립: 로버가 벽 쪽으로 조금씩 다가가며 네 번 scan하면 칸의 log-odds가 쌓인다. 주황 기둥은 점유, 초록 기둥은 비어 있음
import pathlib
import sys

import bpy
import numpy as np
from bpy_extras import anim_utils

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, H = 0.5, 0.06                                                # 1 m drawn as 0.5 m; a pillar is 0.06 high per unit of |log-odds|
cs = m.RES * S
world = m.make_world()
fan = np.linspace(-0.6, 0.6, 41)                                # the beams of one scan, relative to the heading
poses = [(5.0, 7.0 + 0.2 * k, np.pi / 2) for k in range(4)]     # the rover creeps 0.2 m toward the far wall between scans
scan_at = [14, 44, 74, 104]
Ls, L = [], np.zeros((m.N, m.N))
for p in poses:                                                 # the lesson's own update, one scan at a time
    L = m.update(L, p, m.scan(world, p, fan), fan)
    Ls.append(L.copy())
box_x, box_y = 5.0 * S, 7.0 * S                                 # the camera looks at the patch of room around the rover
sc = kit.setup(5.4)
for ix in range(8, 33):                                         # the floor under the patch and the true wall as a flat strip
    for iy in range(26, 40):
        kit.box("floor-cell", (cs * 0.96, cs * 0.96, 0.01), ((ix + 0.5) * cs, (iy + 0.5) * cs, 0.005), "grey" if world[iy, ix] else "pearl", bevel=0)
root, wheels = kit.rover("rover", "blue")
root.scale = (0.8,) * 3
pillars = {}
touched = [(r, c) for r in range(26, 40) for c in range(8, 33) if any(abs(x[r, c]) > 0 for x in Ls)]
for r, c in touched:
    for kind, colour in (("occ", "amber"), ("free", "green")):
        t = kit.box(f"{kind}", (cs * 0.8, cs * 0.8, 1.0), ((c + 0.5) * cs, (r + 0.5) * cs, 0.0), colour, bevel=0.004)
        t.scale = (1, 1, 0.001)
        t.keyframe_insert("scale", frame=1)
        pillars[kind, r, c] = t
beams = [kit.cyl("beam", 0.006, 1.0, (0, 0, 0), "x", "red", segments=8) for _ in range(len(fan[::4]))]
for b in beams:
    b.scale = (0, 1, 1)
    b.keyframe_insert("scale", frame=1)
for k, (p, f0, Lk) in enumerate(zip(poses, scan_at, Ls)):
    kit.key(root, f0 - 8, loc=(*(np.array(poses[max(k - 1, 0)][:2]) * S), 0), rot=(0, 0, p[2]))
    kit.key(root, f0 - 2, loc=(*(np.array(p[:2]) * S), 0), rot=(0, 0, p[2]))
    for (kind, r, c), t in pillars.items():                     # pillars grow to the new log-odds over 10 frames
        v = Lk[r, c]
        h = max(v if kind == "occ" else -v, 0.0) * H + 0.001
        t.scale = (1, 1, h)
        t.location.z = h / 2
        t.keyframe_insert("scale", frame=f0 + 10)
        t.keyframe_insert("location", frame=f0 + 10)
        if k == 0:
            t.location.z = 0.0005
            t.keyframe_insert("location", frame=1)
    for b, a in zip(beams, fan[::4]):                           # a few beams flash from the rover to where each one ended
        rng_ = float(m.scan(world, p, np.array([a]))[0]) * S
        ang = p[2] + a
        o = np.array(p[:2]) * S
        b.location = (*(o + rng_ / 2 * np.array([np.cos(ang), np.sin(ang)])), 0.14)
        b.rotation_euler = (0, 0, ang)
        for fr, s in ((f0 - 1, 0.0), (f0, rng_), (f0 + 6, rng_), (f0 + 7, 0.0)):
            b.scale = (s, 1, 1)
            b.keyframe_insert("scale", frame=fr)
        b.keyframe_insert("location", frame=f0)
        b.keyframe_insert("rotation_euler", frame=f0)
for b in beams:                                                  # beams blink: no gliding between scale keys (the new-key preference has no effect in background Blender)
    for fcu in anim_utils.action_get_channelbag_for_slot(b.animation_data.action, b.animation_data.action_slot).fcurves:
        for kp in fcu.keyframe_points:
            kp.interpolation = "CONSTANT"
kit.camera((box_x, 1.8, 3.0), (box_x, 4.2, 0.0), lens=36)
kit.render(__file__)
