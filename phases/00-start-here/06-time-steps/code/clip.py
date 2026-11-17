# 레슨 00/06 클립: 같은 가속 운동을 큰 스텝(파랑, 뛰엄뛰엄 앞서 감)과 작은 스텝(초록, 매끈하게 정답 선 근처)으로 계산한 장난감 자동차 둘
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, ACCEL, SIM, X0 = 5.0, 2.0, 2.0, -2.4
BIG, SMALL = 0.5, 0.05
path = {"blue": (BIG, m.positions(ACCEL, SIM, BIG)), "green": (SMALL, m.positions(ACCEL, SIM, SMALL))}
exact = m.exact_distance(ACCEL, SIM)

sc = kit.setup(SECONDS)
fps = sc.render.fps
kit.stripe(X0 - 0.5, X0 + 6.2, -0.9, 0.9, "road")
kit.box("exact-line", (0.08, 1.8, 0.02), (X0 + exact + 0.3, 0, 0.01), "amber", bevel=0)   # where the car's nose should end up
cars = {}
for name, y in (("blue", 0.45), ("green", -0.45)):
    cars[name] = (kit.car(name, name)[:2], y)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / fps
    s = min(t / 4.4, 1.0) * SIM            # simulated seconds shown at this frame; no lead-in, so motion starts at once
    for name, ((root, wheels), y) in cars.items():
        dt, pos = path[name]
        n = min(int(s / dt + 1e-9), len(pos) - 1)             # steps finished so far: the car only moves when a step ends
        kit.drive(root, wheels, f, X0 + pos[n], y)
kit.camera((0.2, -4.9, 3.6), (0.2, 0, 0.1), lens=30)
kit.render(__file__)
