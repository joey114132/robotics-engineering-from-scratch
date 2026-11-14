# 레슨 11/01 클립: 마찰계수 0.5인 두 경사면 위의 블록. 25도(tan 0.47)에서는 멈춰 있고 35도(tan 0.70)에서는 미끄러진다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
MU, T, SLOW, L, H, S0 = 0.5, 1.6, 3.0, 1.7, 0.21, 0.4      # friction, simulated seconds, slow-down, ramp length, block half size, start
RAMPS = ((25, -1.85, "green"), (35, 0.25, "blue"))          # degrees, x of the high end, ramp colour
runs = {d: m.simulate(math.radians(d), MU, T) for d, _, _ in RAMPS}

sc = kit.setup(T * SLOW)
blocks = []
for deg, x0, col in RAMPS:
    th = math.radians(deg)
    d, nr = (math.cos(th), 0, -math.sin(th)), (math.sin(th), 0, math.cos(th))
    top = 0.12 + L * math.sin(th)
    at = lambda s, h=0.0, x0=x0, d=d, nr=nr, top=top: (x0 + s * d[0] + h * nr[0], 0, top + s * d[2] + h * nr[2])   # point s down the slope, h above it
    slab = kit.box("ramp", (L, 0.9, 0.06), at(L / 2, -0.03), col, bevel=0.01)
    slab.rotation_euler = (0, th, 0)
    stop = kit.box("stop", (0.06, 0.9, 0.16), at(L - 0.03, 0.08), "grey", bevel=0.01)
    stop.rotation_euler = (0, th, 0)
    for s in (0.15, L - 0.2):                                # two legs from the floor to the underside
        z = at(s, -0.06)[2]
        kit.box("leg", (0.07, 0.5, z), (at(s, -0.06)[0], 0, z / 2), "dark", bevel=0.01)
    blk = kit.crate("block", 2 * H, (0, 0, 0))
    blk.rotation_euler = (0, th, 0)
    blocks.append((blk, runs[deg], at))

for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / m.DT), int(T / m.DT) - 1)
    for blk, r, at in blocks:
        kit.key(blk, f, loc=at(min(S0 + r["s"][i], L - 0.06 - H - 0.0), H))   # clamp at the stop block
kit.camera((-0.1, -4.6, 2.1), (-0.1, 0, 0.55), lens=38)
kit.render(__file__)
