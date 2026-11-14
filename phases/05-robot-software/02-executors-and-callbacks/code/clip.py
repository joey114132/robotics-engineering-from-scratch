# 레슨 05/02 클립: 같은 callback 구성을 스레드 1개(파랑)와 2개(초록)로 돌린 두 대의 차. 타이머가 굶으면 watchdog 이 차를 세운다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
CBS = [("timer", 10, 1, "fast", 1), ("slow", 100, 60, "slow", 0)]   # the lesson's heartbeat timer and its 60 ms slow callback
HORIZON, SLOW, TIMEOUT, V = 1000, 5, 25, 2.6                        # ms simulated, played 5x slower; watchdog trips after 25 ms; 2.6 m/s
sc = kit.setup(HORIZON / 1000 * SLOW)
kit.stripe(-1.9, 2.4, -0.95, 0.95, "road")
kit.stripe(1.77, 1.83, -0.95, 0.95, "white", z=0.004)               # the line the green car reaches
runs = {}
for n, colour, y in ((1, "blue", 0.5), (2, "green", -0.5)):
    starts = sorted(s for name, _, s, _ in m.simulate(CBS, n, HORIZON) if name == "timer")
    x, last, xs, go = -1.2, 0, [], []
    for t in range(HORIZON + 1):
        last = max([s for s in starts if s <= t] or [0])
        go.append(t - last <= TIMEOUT)                              # fresh heartbeat: the car drives, stale: the watchdog stops it
        xs.append(x)
        x += V * 0.001 * go[-1]
    runs[n] = (kit.car(colour, colour, 1.3), xs, go, y)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = min(int((f - 1) / 24 / SLOW * 1000), HORIZON)
    for (root, wheels, brake), xs, go, y in runs.values():
        kit.drive(root, wheels, f, xs[t], y)
        for b in brake:
            b.scale = (1,) * 3 if go[t] else (2.2,) * 3
            b.keyframe_insert("scale", frame=f)
kit.camera((0.15, -4.4, 2.6), (0.15, 0.0, 0.1), lens=38)
kit.render(__file__)
