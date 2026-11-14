# 레슨 14/03 예시 클립: reserve 규칙의 네 대를 크게 본다. 앞칸이 비어 있어도 경로 전체가 비지 않으면 밖에서 기다리고 빨간 막대가 그 자리를 막는다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
JOBS = [((0, 0), (1, 1)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))]   # the lesson's four-robot loop
TICK, TICKS, S, LEAD = 0.7, 7, 1.15, 0.3                                          # one tick per 0.7 s (slower than the lead clip); 1 grid unit drawn as 1.15 m
SECONDS = LEAD + TICK * TICKS + 0.6

sc = kit.setup(SECONDS)
fps = sc.render.fps
node = lambda u, v: ((u - 0.5) * S, 1.1 + (v - 0.5) * S)
kit.box("pad", (4.5, 4.5, 0.02), (0, 1.1, 0.01), "#e6ecee", bevel=0.01)
for k in (0, 1):                                                                  # two roads each way, crossing at four intersections
    kit.box("road", (4.3, 0.55, 0.01), (0, node(0, k)[1], 0.025), "road", bevel=0)
    kit.box("road", (0.55, 4.3, 0.01), (node(k, 0)[0], 1.1, 0.025), "road", bevel=0)
pads = {(u, v): kit.cyl("held", 0.34, 0.012, (*node(u, v), 0.04), "z", "amber", segments=32) for u in (0, 1) for v in (0, 1)}

sim = m.Sim(JOBS, 4, "reserve")
paths, wp = sim.paths, []
for r, p in enumerate(paths):                                                     # per robot: a hold spot outside, the route, a parking spot past the goal
    d0 = (p[1][0] - p[0][0], p[1][1] - p[0][1])
    d1 = (p[-1][0] - p[-2][0], p[-1][1] - p[-2][1])
    park = {0: 1.4, 1: 0.7}.get(r, 0.9)                                             # robots 0 and 1 both leave through (1, 1): every car gets its own spot, 0.8 m or more apart
    wp.append([(p[0][0] - 1.0 * d0[0], p[0][1] - 1.0 * d0[1])] + list(p) + [(p[-1][0] + park * d1[0], p[-1][1] + park * d1[1])])
state, held, waiting = [[0.0] * 4], [set()], [set(range(4))]
for t in range(TICKS):
    before = set(sim.res)
    sim.step()
    state.append([float(len(paths[r]) + 1) if r not in sim.at and r not in sim.queue else float(sim.at[r] + 1) if r in sim.at else 0.0 for r in range(4)])
    held.append(before | set(sim.res))
    waiting.append(set(sim.queue))

def at_tick(k):                                                                   # the clip frame where tick k begins to play
    return int((LEAD + k * TICK) * fps) + 1

for pad_xy, pad in pads.items():
    for k in range(TICKS):
        pad.hide_render = pad_xy not in held[k + 1]
        pad.keyframe_insert("hide_render", frame=at_tick(k))
    pad.hide_render = True
    pad.keyframe_insert("hide_render", frame=at_tick(TICKS))

for r in range(4):                                                                # a red bar in front of each car that is waiting outside
    a, b = wp[r][0], wp[r][1]
    ax, ay = node(*a)
    bx, by = node(*b)
    mx, my, yaw = (ax + bx) / 2, (ay + by) / 2, math.atan2(by - ay, bx - ax)
    bar = kit.box("stop", (0.09, 0.6, 0.2), (mx, my, 0.11), "red", bevel=0.02)
    bar.rotation_euler = (0, 0, yaw)
    for k in range(TICKS + 1):
        bar.hide_render = r not in waiting[k]
        bar.keyframe_insert("hide_render", frame=1 if k == 0 else at_tick(k - 1))

for r in range(4):
    root, wheels = kit.rover(f"car{r}", "green")
    root.scale = (1.35,) * 3
    yaw, travelled, last = None, 0.0, None
    for f in range(sc.frame_start, sc.frame_end + 1):
        tt = max((f - 1) / fps - LEAD, 0.0) / TICK
        k = min(int(tt), TICKS - 1)
        prog = state[k][r] + (state[k + 1][r] - state[k][r]) * (min(tt, TICKS) - k)
        i = min(int(prog), len(wp[r]) - 2)
        a, b = wp[r][i], wp[r][i + 1]
        u = prog - i
        x, y = node(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
        ax, ay = node(*a)
        bx, by = node(*b)
        want = math.atan2(by - ay, bx - ax)
        if yaw is None:
            yaw = want
        yaw += max(-0.3, min(0.3, (want - yaw + math.pi) % (2 * math.pi) - math.pi))   # turn at corners, not instantly
        if last:
            travelled += math.dist(last, (x, y))
        last = (x, y)
        kit.key(root, f, loc=(x, y, 0), rot=(0, 0, yaw))
        for w in wheels:
            kit.key(w, f, rot=(0, travelled / (0.075 * 1.35), 0))
kit.camera((0, -2.9, 3.9), (0, 1.25, 0), lens=26)
kit.render(__file__)
