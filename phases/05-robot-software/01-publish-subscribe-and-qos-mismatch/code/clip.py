# 레슨 05/01 클립: 로봇 위치를 메시지로 받아 따라가는 팔 두 대. 파란 쪽은 QoS가 맞지 않아 아무것도 도착하지 않는다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
FPS, SECONDS, L = 24, 5.0, 0.55
lanes = {"blue": (m.Qos("best_effort"), m.Qos("reliable"), 0.8), "green": (m.Qos("reliable"), m.Qos("reliable"), -0.8)}
xr = lambda t: 0.4 + 0.55 * (3 * min(1, t / 4.4) ** 2 - 2 * min(1, t / 4.4) ** 3)   # the rover eases to a stop at 0.95 m
fr = lambda t: int(round(t * FPS)) + 1


def ik(x, z=0.1):
    """Planar two-link reach, elbow up, to a point x ahead of the shoulder and z above it."""
    a = math.acos(min(1.0, math.hypot(x, z) / (2 * L)))
    return math.atan2(z, x) + a, -2 * a


sc = kit.setup(SECONDS)
for name, (pub, sub, y) in lanes.items():
    root, joints = kit.arm(name + "-arm", (L, L), name, base_height=0.3)
    root.location = (0, y, 0)
    rover, wheels = kit.rover(name + "-rover", name)
    ks = [k for k in range(18) if m.run(pub, sub, [1] * (k + 1))["delivered"] == k + 1]   # which messages arrive
    kit.pose(joints, 1, (1.7, 2.4))
    for f in range(1, fr(SECONDS) + 1):
        kit.drive(rover, wheels, f, xr((f - 1) / FPS), y, radius=0.075)
    for k in range(18):
        t0, t1 = 0.3 + 0.25 * k, 0.55 + 0.25 * k
        p = kit.ball(f"{name}-msg{k}", 0.06, (0, 0, 0), "amber" if k in ks else "red")
        a, b = (xr(t0), y, 0.3), (0.0, y, 0.55)
        kit.key(p, fr(t0) - 1, loc=a)
        p.scale = (0.001,) * 3
        p.keyframe_insert("scale", frame=fr(t0) - 1)
        p.scale = (1, 1, 1)
        p.keyframe_insert("scale", frame=fr(t0))
        kit.key(p, fr(t0), loc=a)
        if k in ks:
            kit.key(p, fr((t0 + t1) / 2), loc=((a[0] + b[0]) / 2, y, 0.62))
            kit.key(p, fr(t1), loc=b)
            p.scale = (0.001,) * 3
            p.keyframe_insert("scale", frame=fr(t1) + 1)
            kit.pose(joints, fr(t1), ik(xr(t0) - 0.05))   # the arm moves to where the rover was when it published
        else:   # the pair never matched: the packet drops to the floor and stays there
            kit.key(p, fr(t0 + 0.12), loc=(a[0] * 0.6, y, 0.45))
            kit.key(p, fr(t0 + 0.28), loc=(a[0] * 0.5, y, 0.04))
kit.camera((0.5, -3.6, 2.8), (0.4, -0.05, 0.25), lens=42)
kit.render(__file__)
