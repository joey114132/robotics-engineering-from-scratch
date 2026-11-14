# 레슨 05/01 예시 클립: 로버가 위치 메시지 8개를 한꺼번에 보낸다. 칸이 하나인 선반(파랑)은 7개를 바닥에 흘리고 칸이 여덟 개인 선반(초록)은 모두 받는다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
FPS, SECONDS, L, BURST = 24, 5.4, 0.55, 8
fr = lambda t: int(round(t * FPS)) + 1
xr = lambda k: 0.45 + 0.5 * k / (BURST - 1)      # where the rover was when it published message k
t_pub = lambda k: 0.3 + 0.1 * k                  # the burst: 8 messages in 0.7 s (the callback waits for 1.8 s)


def ik(x, z=0.1):
    """Planar two-link reach, elbow up, to a point x ahead of the shoulder and z above it."""
    a = math.acos(min(1.0, math.hypot(x, z) / (2 * L)))
    return math.atan2(z, x) + a, -2 * a


def held(depth):
    """The messages a keep-last queue still holds after the burst, oldest first (the lesson's Queue)."""
    q = m.Queue(depth)
    for k in range(BURST):
        q.push(k)
    assert len(q.items) == m.run(m.Qos(), m.Qos(depth=depth), [BURST] + [0] * 9)["delivered"]
    return q.items


def vis(ob, t, on):
    ob.scale = (1,) * 3 if on else (0.001,) * 3
    ob.keyframe_insert("scale", frame=fr(t))


sc = kit.setup(SECONDS)
for depth, colour, xo in ((1, "blue", -1.4), (8, "green", 0.25)):   # two lanes side by side; xo shifts every x of a lane
    y, keep, ys = 0.0, held(depth), -0.45
    root, joints = kit.arm(colour + "-arm", (L, L), colour, base_height=0.3)
    root.location = (xo, y, 0)
    rover, wheels = kit.rover(colour + "-rover", colour)
    for f in range(1, sc.frame_end + 1):
        t = (f - 1) / FPS
        kit.drive(rover, wheels, f, xo + xr(0) + (xr(BURST - 1) - xr(0)) * min(1, max(0, (t - 0.3) / 0.7)), y, radius=0.075)
    slot = lambda k: xo + 0.35 + 0.1 * (k if depth == BURST else 0)
    kit.box("shelf", (0.1 * depth + 0.04, 0.14, 0.03), (xo + 0.35 + 0.05 * (depth - 1), ys, 0.015), "pearl", bevel=0.006)
    for i in range(depth + 1):
        kit.box("slot", (0.012, 0.14, 0.05), (xo + 0.3 + 0.1 * i, ys, 0.04), "grey", bevel=0.003)
    kit.pose(joints, 1, (1.7, 2.4))
    for j, k in enumerate(keep):                 # the callback takes one message per tick, oldest first
        tc = 1.8 + 0.4 * j
        kit.pose(joints, fr(tc - 0.3), (1.7, 2.4) if j == 0 else ik(xr(keep[j - 1]) - 0.05))
        kit.pose(joints, fr(tc), ik(xr(k) - 0.05))
    for k in range(BURST):
        t0, t1 = t_pub(k), t_pub(k) + 0.25
        ok = k in keep
        p = kit.ball(f"{colour}-msg{k}", 0.04, (0, 0, 0), "amber" if ok else "red")
        a, b = (xo + xr(k), y, 0.3), (slot(k), ys, 0.075)
        vis(p, t0 - 0.05, False)
        vis(p, t0, True)
        kit.key(p, fr(t0), loc=a)
        kit.key(p, fr((t0 + t1) / 2), loc=((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.55))
        kit.key(p, fr(t1), loc=b)
        if ok:
            tc = 1.8 + 0.4 * keep.index(k)
            kit.key(p, fr(tc), loc=b)
            vis(p, tc, True)
            vis(p, tc + 0.05, False)
        else:                                    # pushed off the one-slot shelf by the next message
            ts = t_pub(k + 1) + 0.25
            kit.key(p, fr(ts), loc=b)
            kit.key(p, fr(ts + 0.2), loc=(xo + 0.2 + 0.1 * k, ys - 0.28, 0.04))
kit.camera((-0.25, -4.0, 2.5), (-0.25, -0.2, 0.25), lens=42)
kit.render(__file__)
