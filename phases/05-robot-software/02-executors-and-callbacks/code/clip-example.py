# 레슨 05/02 예시 클립: 스레드가 둘씩인 차 두 대. 파랑은 timer 와 느린 callback 이 같은 group 이라 지붕의 두 번째 램프가 꺼진 채 차가 멈추고 초록은 group 이 따로라 멈추지 않는다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
HORIZON, SLOW, TIMEOUT, V, GLOW = 1000, 5, 25, 2.6, 8                # ms simulated, played 5x slower; watchdog 25 ms; 2.6 m/s; a lamp glows 8 ms after a job starts
cbs = lambda g: [("timer", 10, 1, g, 1), ("slow", 100, 60, "slow", 0)]  # the lesson's heartbeat timer and 60 ms callback; g is the timer's group


def threads(log, n):
    """Give each job the lowest free thread, as the executor does; returns [(thread, start, end)]."""
    free, out = [0] * n, []
    for _, _, s, e in sorted(log, key=lambda j: j[2]):
        i = next(i for i in range(n) if free[i] <= s)
        free[i] = e
        out.append((i, s, e))
    return out


sc = kit.setup(HORIZON / 1000 * SLOW)
kit.stripe(-1.9, 2.4, -0.95, 0.95, "road")
kit.stripe(1.77, 1.83, -0.95, 0.95, "white", z=0.004)
runs = {}
for colour, group, y in (("blue", "slow", 0.5), ("green", "fast", -0.5)):
    log = m.simulate(cbs(group), 2, HORIZON)
    assert max(m.latencies(log, "timer")) == (59 if group == "slow" else 0)   # the numbers in the doc
    starts = sorted(s for name, _, s, _ in log if name == "timer")
    x, xs, go = -1.2, [], []
    for t in range(HORIZON + 1):
        go.append(t - max([s for s in starts if s <= t] or [0]) <= TIMEOUT)
        xs.append(x)
        x += V * 0.001 * go[-1]
    car = kit.car(colour, colour, 1.3)
    lamps = []
    for i in range(2):                                                # one lamp per thread on the car's roof
        off, on = (kit.ball("lamp", r, (-0.17 + 0.2 * i, 0, 0.37), c, parent=car[0]) for r, c in ((0.055, "dark"), (0.06, "amber")))
        lamps.append((on, [j for j in threads(log, 2) if j[0] == i]))
    runs[colour] = (car, xs, go, y, lamps)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = min(int((f - 1) / 24 / SLOW * 1000), HORIZON)
    for (root, wheels, brake), xs, go, y, lamps in runs.values():
        kit.drive(root, wheels, f, xs[t], y)
        for b in brake:
            b.scale = (1,) * 3 if go[t] else (2.2,) * 3
            b.keyframe_insert("scale", frame=f)
        for on, jobs in lamps:
            on.scale = (1,) * 3 if any(s <= t < e + GLOW for _, s, e in jobs) else (0.001,) * 3
            on.keyframe_insert("scale", frame=f)
kit.camera((0.15, -4.4, 2.6), (0.15, 0.0, 0.1), lens=38)
kit.render(__file__)
