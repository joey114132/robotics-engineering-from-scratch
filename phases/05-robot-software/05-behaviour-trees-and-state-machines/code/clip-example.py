# 레슨 05/05 예시 클립: Fallback 이 먼저 bin A 를 확인하고 가득 차 있어 실패하자 bin B 로 간다. 다음 tick 에는 A 를 다시 묻지 않고 B 로 가던 길을 이어 간다
import math
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
L, GRIP, TOP, SHO, OPEN, HOLD = 0.4, 0.085, 0.4, 0.7, 0.075, 0.045   # link length, finger centre, table top, shoulder height, finger gaps
H, A_X, B_X, TICKS, DUR, SECONDS = (0.35, 0.12), 0.72, -0.5, (0.5, 1.3, 2.1), 0.8, 4.8
R, S = m.RUNNING, m.SUCCESS
check, go_a = m.condition("A has room", lambda: False), m.scripted("go A", [R, S])   # bin A is full
go_b = m.scripted("go B", [R, R, S])
tree = m.Fallback("place", [m.Sequence("bin A", [check, go_a, m.scripted("release A", [S])]), m.Sequence("bin B", [go_b, m.scripted("release B", [S])])])
ticks = m.run(tree)
assert [s for _, s in ticks] == [R, R, S] and (check.calls, go_a.calls, go_b.calls) == (1, 0, 3)   # A asked once, never visited; B visited every tick
assert [n for n, _ in ticks[1][0]] == ["go B", "bin B", "place"]                                    # tick 2 resumes at go B
clamp = lambda x: min(1.0, max(0.0, x))
lerp = lambda a, b, u: tuple(x + (y - x) * u for x, y in zip(a, b))
fr = lambda t: int(round(t * 24)) + 1


def ik(p, side=1):
    """Elbow-up joint angles that put the finger centre at p = (x, z) from the shoulder; side=-1 reaches behind the post."""
    w = p
    for _ in range(5):
        a = math.acos(min(1.0, math.hypot(*w) / (2 * L)))
        phi = math.atan2(w[1], w[0]) % (2 * math.pi) if side < 0 else math.atan2(w[1], w[0])
        q = (phi + side * a, -side * 2 * a)
        w = (p[0] - GRIP * math.cos(q[0] + q[1]), p[1] - GRIP * math.sin(q[0] + q[1]))
    return q


fk = lambda q: (L * math.cos(q[0]) + (L + GRIP) * math.cos(q[0] + q[1]), L * math.sin(q[0]) + (L + GRIP) * math.sin(q[0] + q[1]))
qs, qe = ik(H), ik((B_X, -0.12), -1)
sc = kit.setup(SECONDS)
kit.table((1.8, 0.7), TOP)
root, joints = kit.arm("arm", (L, L), "blue", 0.3)
root.location = (0, 0, TOP)
fingers = sorted((o for o in bpy.data.objects if o.name.startswith("arm-finger")), key=lambda o: o.location.z)
crate = kit.crate("crate", 0.07, (0, 0, 0))
for bx in (A_X, B_X):
    kit.box("bin", (0.22, 0.22, 0.01), (bx, 0, TOP + 0.005), "grey", bevel=0.004)
    for sx, sy, dx, dy in ((0.02, 0.22, 0.1, 0), (0.02, 0.22, -0.1, 0), (0.22, 0.02, 0, 0.1), (0.22, 0.02, 0, -0.1)):
        kit.box("bin", (sx, sy, 0.09), (bx + dx, dy, TOP + 0.045), "grey", bevel=0.004)
for dx in (-0.05, 0.05):                                            # bin A is full: a 2 x 2 layer of crates
    for dy in (-0.05, 0.05):
        kit.crate("full", 0.085, (A_X + dx, dy, TOP + 0.055))
flash = [kit.box("flash", s, (A_X + d[0], d[1], TOP + 0.095), "red", bevel=0.003) for s, d in (((0.26, 0.02, 0.012), (0, 0.12)), ((0.26, 0.02, 0.012), (0, -0.12)), ((0.02, 0.26, 0.012), (0.12, 0)), ((0.02, 0.26, 0.012), (-0.12, 0)))]
for f in range(1, sc.frame_end + 1):
    t = (f - 1) / 24
    q = lerp(qs, qe, sum(clamp((t - k) / DUR) for k in TICKS) / 3)
    gap = HOLD + (OPEN - HOLD) * clamp((t - 2.9) / 0.3)
    x, z = fk(q)
    held = (x, 0, SHO + z)
    drop = clamp((t - 3.2) / 0.5) ** 2
    kit.pose(joints, f, q)
    for fg, sgn in zip(fingers, (-1, 1)):
        kit.key(fg, f, loc=(0.085, 0, sgn * gap))
    kit.key(crate, f, loc=held if t < 3.2 else (held[0], 0, held[2] + (TOP + 0.045 - held[2]) * drop))
    for b in flash:
        b.scale = (1,) * 3 if TICKS[0] <= t < 1.2 else (0.001,) * 3   # tick 1: the check on bin A fails
        b.keyframe_insert("scale", frame=f)
kit.camera((0, -3.0, 2.1), (0, 0, 0.9), lens=42)
kit.render(__file__)
