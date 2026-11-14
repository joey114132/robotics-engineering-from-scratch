# 레슨 00/02 예시 클립: 0.5 rad 에서 놓은 같은 진자 셋. explicit Euler 는 dt 를 줄여도 올라가고(파랑, 연한 파랑) semi-implicit 은 선에 머문다(초록)
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
TH0, SECONDS, T_END = 0.5, 5.0, 10.0
cases = (("coarse", "explicit", 0.04, -1.25, "blue"), ("fine", "explicit", 0.01, 0.0, "#7aa8f2"), ("semi", "semi", 0.04, 1.25, "green"))
runs, ends = {}, {}
for name, scheme, dt, _, _ in cases:
    th = m.simulate(TH0, dt, T_END, scheme=scheme)
    turn = [i for i in range(1, len(th) - 1) if abs(th[i]) >= abs(th[i - 1]) and abs(th[i]) > abs(th[i + 1])]
    runs[name], ends[name] = th, turn[-1]                 # stop each pendulum at the top of its last swing before 10 s
SPEED = max(ends[n] * dt for n, _, dt, _, _ in cases) / SECONDS   # simulated seconds per clip second, about 1.8

sc = kit.setup(SECONDS)
L, PIVOT_Z, FRONT = 0.6, 1.2, -0.22                       # rods swing in a plane in front of the beam, so a 140 degree swing clears it
kit.box("beam", (5.0, 0.12, 0.1), (0, 0, PIVOT_Z + 0.06), "dark")
for sx in (-1, 1):
    kit.box("leg", (0.1, 0.5, PIVOT_Z + 0.1), (sx * 2.45, 0, (PIVOT_Z + 0.1) / 2), "grey", bevel=0.01)
kit.box("release-level", (4.2, 0.02, 0.03), (0, 0.1, PIVOT_Z - L * math.cos(TH0)), kit.ghost("amber", 0.8), bevel=0)   # the height all three were released from
bobs = {}
for name, scheme, dt, x, colour in cases:
    pivot = kit.empty(name, (x, FRONT, PIVOT_Z))
    kit.box("bracket", (0.05, -FRONT - 0.06, 0.05), (x, FRONT / 2 - 0.03, PIVOT_Z), "dark", bevel=0.005)
    kit.cyl("hub", 0.045, 0.16, (0, 0, 0), "y", "grey", parent=pivot)
    kit.cyl("rod", 0.022, L, (0, 0, -L / 2), "z", "dark", parent=pivot)
    kit.ball("bob", 0.12, (0, 0, -L), colour, parent=pivot)
    bobs[name] = (pivot, dt)
for f in range(sc.frame_start, sc.frame_end + 1):
    for name, (pivot, dt) in bobs.items():
        i = min(int(round((f - 1) / sc.render.fps * SPEED / dt)), ends[name])
        kit.key(pivot, f, rot=(0, -float(runs[name][i]), 0))    # theta from the lesson's simulate(), positive toward +x
kit.camera((0, -4.8, 2.7), (0, 0, 0.9), lens=35)
kit.render(__file__)
