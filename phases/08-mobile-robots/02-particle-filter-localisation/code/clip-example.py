# 레슨 08/02 예시 클립: 로버가 다른 구석으로 옮겨진 뒤 파란 일반 구름은 옛 자리에 남고 초록 구름(5% 무작위 particle)은 따라온다
import pathlib
import sys

import bpy
import numpy as np
from bpy_extras import anim_utils

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, SHOWN, N, KID = 0.25, 4, 1000, 40                            # drawing scale 1 m -> 0.25 m; every 4th of 1000 particles is drawn; the robot is carried at step 40


def run(inject):
    """The lesson's kidnap run (same seeds and noise as figure.py): returns the cloud, the estimate and the true pose after every step."""
    rng, rz = np.random.default_rng(0), np.random.default_rng(100)
    truth = np.array([[2.0, 3.0, 0.3]])
    P = np.column_stack([rng.uniform(0, 10, (N, 2)), rng.uniform(-np.pi, np.pi, N)])
    out = []
    for t in range(100):
        if t == KID:
            truth = np.array([[8.0, 7.0, -2.0]])
        truth = m.move(truth, 0.8, 0.15, 0.1)
        P = m.pf_step(P, 0.8, 0.15, 0.1, m.ranges(truth)[0] + rz.normal(0, 0.3, 4), 0.3, rng, sv=0.1, sw=0.3, inject=inject)
        out.append((P.copy(), m.estimate(P), truth[0].copy()))
    return out


runs = {"plain": run(0.0), "inject": run(0.05)}
# frame of each step shown: steps 36-39 two frames each, a pause for the carry, steps 40-43 slowed, the rest one frame each
when, f = {}, 1
for t in range(36, 40):
    when[t], f = f, f + 2
carry = f
f += 26
for t in range(40, 44):
    when[t], f = f, f + 8
for t in range(44, 100):
    when[t], f = f, f + 1
sc = kit.setup((f + 12) / 24)
for (a, b), (c, d) in (((0, 0), (10, 0)), ((10, 0), (10, 10)), ((10, 10), (0, 10)), ((0, 10), (0, 0))):
    kit.stripe(min(a, c) * S - 0.02, max(a, c) * S + 0.02, min(b, d) * S - 0.02, max(b, d) * S + 0.02, "road")
for x, y in m.LANDMARKS * S:
    kit.cyl("post", 0.03, 0.34, (x, y, 0.17), "z", "dark")
    kit.ball("post-top", 0.05, (x, y, 0.37), "amber")
root, wheels = kit.rover("truth", "amber")
root.scale = (0.8,) * 3
clouds = {}
for name, colour, height, radius in (("plain", "blue", 0.3, 0.012), ("inject", "green", 0.18, 0.02)):
    proto = kit.cyl("proto-" + name, radius, height, (0, 0, height / 2), "z", colour, segments=8)
    proto.hide_render = True
    dots = [bpy.data.objects.new(name, proto.data) for _ in range(N // SHOWN)]
    for d in dots:
        bpy.context.scene.collection.objects.link(d)
    clouds[name] = (dots, kit.ball("estimate-" + name, 0.055, (0, 0, 0.42), colour), height / 2)
for name, (dots, est, z) in clouds.items():
    for t, fr in when.items():
        P, e, _ = runs[name][t]
        for d, (x, y, th) in zip(dots, P[::SHOWN]):
            kit.key(d, fr, loc=(x * S, y * S, z))
        kit.key(est, fr, loc=(e[0] * S, e[1] * S, 0.42))
A, B = runs["plain"][39][2], runs["plain"][40][2]
kit.key(root, 1, loc=(*(A[:2] * S), 0), rot=(0, 0, A[2]))
kit.key(root, carry, loc=(*(A[:2] * S), 0), rot=(0, 0, A[2]))
kit.key(root, carry + 8, loc=(*(A[:2] * S), 0.45), rot=(0, 0, A[2]))                           # lifted
kit.key(root, carry + 18, loc=(*(B[:2] * S), 0.45), rot=(0, 0, B[2]))
kit.key(root, carry + 26, loc=(*(B[:2] * S), 0), rot=(0, 0, B[2]))
for t in range(41, 100):                                                                         # then it drives on as in the lesson
    kit.key(root, when[t], loc=(*(runs["plain"][t][2][:2] * S), 0), rot=(0, 0, runs["plain"][t][2][2]))
def interpolate(objs, kind):
    """Set the interpolation of every key (the new-key preference has no effect in background Blender)."""
    for ob in objs:
        ad = ob.animation_data
        for fcu in anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves:
            for kp in fcu.keyframe_points:
                kp.interpolation = kind


interpolate([d for dots, est, _ in clouds.values() for d in (*dots, est)], "CONSTANT")   # a resampled cloud jumps, it does not glide
interpolate([root], "LINEAR")
kit.camera((1.25, -1.9, 3.3), (1.25, 1.2, 0.0), lens=34)
kit.render(__file__)
