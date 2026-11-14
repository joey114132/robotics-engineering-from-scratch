# 레슨 03/04 예시 클립: 정지선에 선 자동차 두 대를 일정한 힘이 뒤로 민다. P+D 는 밀린 채 서 있고 P+I+D 는 선으로 돌아온다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
DT, T0, SECONDS = 0.001, 4.6, 4.4            # the lesson's load case: 20 steps in at 5 s; the clip shows 4.6 s to 9 s at real speed
runs = {name: m.simulate(1.0, 2.0, *gains, DT, 10000, load=20.0, t_load=5.0)[0] for name, gains in (("pd", (100, 0, 20)), ("pid", (100, 200, 20)))}

sc = kit.setup(SECONDS)
kit.stripe(-0.9, 2.3, -0.75, 0.75, "road")                       # 1 unit is the lesson's 1 rad drawn as 1 m; the target is at 1 m
for x in (-0.75, -0.25, 0.25, 0.75, 1.25, 1.75):
    kit.stripe(x, x + 0.22, -0.02, 0.02, "white", z=0.004)
kit.stripe(0.98, 1.02, -0.75, 0.75, "white", z=0.004)             # the line both cars are told to hold
cars = {"pd": (kit.car("pd", "blue"), 0.38), "pid": (kit.car("pid", "green"), -0.38)}
pushes = {}
for name, ((root, wheels, _), y) in cars.items():                 # the steady push: a red arrow on each car's nose, pointing back
    a = kit.arrow("push-" + name, "red")
    a.rotation_euler = (0, 0, 3.14159265)
    pushes[name] = a
for f in range(sc.frame_start, sc.frame_end + 1):
    t = T0 + (f - 1) / sc.render.fps
    i = min(int(t / DT), 9999)
    for name, ((root, wheels, _), y) in cars.items():
        x = float(runs[name][i])
        kit.drive(root, wheels, f, x - 0.3, y=y)
        kit.key(pushes[name], f, loc=(x + 0.45, y, 0.17) if t >= 5.0 else (x + 0.45, y, -1.0))   # under the floor until the load arrives
        pushes[name].scale = (0.42, 1, 1)
kit.camera((0.75, -3.1, 1.9), (0.75, 0.05, 0.12), lens=42)
kit.render(__file__)
