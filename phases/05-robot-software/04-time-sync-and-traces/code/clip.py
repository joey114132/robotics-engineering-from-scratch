# 레슨 05/04 클립: 센서 B(카메라) 시계가 30 ms 앞선 차(파랑)와 offset 을 뺀 차(초록). 떠 있는 호박색 차는 filter 가 stamp 를 믿고 놓은 위치
import bisect
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
A = [0.02 * i for i in range(50)]                                    # sensor A (IMU): every 20 ms
B = [0.02 * i + 0.01 for i in range(50)]                             # sensor B (camera): 10 ms later, but its clock runs 30 ms ahead
OFF, V, SLOW, SECONDS = 0.03, 8.0, 10, 0.4                           # the car drives at 8 m/s for 0.4 s, played 10x slower
arrivals = sorted([(t, 0) for t in A] + [(t, 1) for t in B])         # samples in the order they arrive: (true time, is camera)
runs = {}
for colour, y, corr in (("blue", 1.0, 0.0), ("green", -1.0, OFF + 0.001)):   # green removes an offset estimate that is 1 ms off
    stamp = [t + (OFF - corr) * cam for t, cam in arrivals]          # the stamp each sample carries, as in order_errors()
    runs[colour] = (y, stamp, m.order_errors(A, B, OFF, corr))
assert (runs["blue"][2], runs["green"][2]) == (8, 0)                 # slots out of order, the numbers in the caption
sc = kit.setup(SECONDS * SLOW + 0.5)                                 # 0.5 s hold at the end
kit.stripe(-2.2, 2.0, -1.5, 1.5, "road")
for colour, (y, stamp, _) in runs.items():
    truth, wheels_t, _ = kit.car(colour, colour, 1.5)                 # solid car on the road: where the car really is
    belief, wheels_b, _ = kit.car("belief-" + colour, colour, 1.5)    # amber glass car floating above it: where the filter puts the car
    for ob in belief.children_recursive:
        if ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(kit.ghost("amber", 0.8))
    for f in range(sc.frame_start, sc.frame_end + 1):
        t = min((f - 1) / 24 / SLOW, SECONDS)
        kit.drive(truth, wheels_t, f, -1.7 + V * t, y)
        x = -1.7 + V * stamp[max(bisect.bisect_right([a for a, _ in arrivals], t) - 1, 0)]
        kit.key(belief, f, loc=(x, y, 0.6), rot=(0, 0, 0))
        for w in wheels_b:
            kit.key(w, f, rot=(0, x / 0.09, 0))
kit.camera((-0.1, -4.2, 3.4), (-0.1, 0.0, 0.45), lens=31)
kit.render(__file__)
