# 레슨 07/02 예시 클립: 같은 위치 읽기(호박색 핀)가 와도 센서 잡음이 큰 쪽(파랑)은 조금만, 작은 쪽(초록)은 절반 움직이는 한 번의 Kalman 보정
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SCALE, TRUTH, READ, SECONDS = 0.4, 1.0, 3.0, 5.0              # 1 m drawn as 0.4 m; the car is really at 1 m and the reading says 3 m
lanes = {}
for colour, y, r in (("blue", 0.85, 6.0), ("green", -0.85, 2.0)):   # sensor noise std 6 m (noisy) and 2 m (the lesson's sensor)
    F, H, Q, R = m.model(r=r)
    K = m.gain(m.P0, H, R)                                     # first correction of the lesson's prior [position 0 m +-2 m, speed 1 m/s]
    x = m.X0 + (K @ (np.array([[READ]]) - H @ m.X0[:, None])).ravel()
    P = (np.eye(2) - K @ H) @ m.P0
    lanes[colour] = (y, float(x[0]), 4 * float(np.sqrt(P[0, 0])), 4 * float(np.sqrt(m.P0[0, 0])))   # new estimate, band width after and before
    print(colour, "K", K[0, 0], "estimate", x[0], "band width", lanes[colour][2:])

sc = kit.setup(SECONDS)
kit.stripe(-2.2, 2.2, -1.5, 1.5, "road")
for y in (0.85, -0.85):
    for x in np.arange(-2.0, 2.0, 0.6):
        kit.stripe(x, x + 0.25, y - 0.015, y + 0.015, "white", z=0.004)
rig = {}
for colour, (y, est, w1, w0) in lanes.items():
    car, wheels, _ = kit.car("real", "grey", 1.1)
    kit.drive(car, wheels, 1, TRUTH * SCALE, y, 0.0, 0.09 * 1.1)
    band = kit.box("band", (1.0, 0.8, 0.01), (0, y, 0.008), kit.ghost(colour, 0.6), bevel=0)
    pin = (kit.ball(colour + "-ball", 0.1, (0, y - 0.45, 1.0), colour), kit.cyl(colour + "-stem", 0.014, 1.0, (0, y - 0.45, 0), "z", colour))
    zin = (kit.ball("read-ball", 0.1, (READ * SCALE, y - 0.45, 0.75), "amber"), kit.cyl("read-stem", 0.014, 1.0, (READ * SCALE, y - 0.45, 0), "z", "amber"))
    rig[colour] = (y, est, w1, w0, band, pin, zin)


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps
    drop, glide = ease((t - 0.6) / 0.8), ease((t - 1.9) / 1.5)
    for colour, (y, est, w1, w0, band, pin, zin) in rig.items():
        e = est * glide
        kit.key(band, f, loc=(e * SCALE, y, 0.008))
        band.scale = ((w0 + (w1 - w0) * glide) * SCALE, 1, 1)
        band.keyframe_insert("scale", frame=f)
        kit.key(pin[0], f, loc=(e * SCALE, y - 0.45, 1.0))
        kit.key(pin[1], f, loc=(e * SCALE, y - 0.45, 0.5))
        pin[1].scale = (1, 1, 1.0)
        pin[1].keyframe_insert("scale", frame=f)
        top = 0.75 + 0.4 * (1 - drop) if t >= 0.6 else -1.0       # the reading drops in from above, hidden under the floor before
        kit.key(zin[0], f, loc=(READ * SCALE, y - 0.45, top))
        kit.key(zin[1], f, loc=(READ * SCALE, y - 0.45, top / 2))
        zin[1].scale = (1, 1, abs(top))
        zin[1].keyframe_insert("scale", frame=f)
kit.camera((0, -3.9, 2.7), (0, -0.1, 0.3), lens=38)
kit.render(__file__)
