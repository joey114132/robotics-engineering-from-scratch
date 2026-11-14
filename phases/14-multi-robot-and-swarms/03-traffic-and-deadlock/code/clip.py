# 레슨 14/03 클립: 사거리 네 모서리의 로봇 네 대. 파란 쪽은 "비면 간다"로 서로 물고 멈추고, 초록 쪽은 경로 예약으로 차례로 지나간다
import importlib.util
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
JOBS = [((0, 0), (1, 1)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))]   # the lesson's four-robot loop (its test and __main__)
TICK, TICKS, S, LEAD = 0.65, 7, 1.0, 0.3                                          # one grid step per 0.65 s; 1 grid unit drawn as 1.0 m
SECONDS = LEAD + TICK * TICKS + 0.65

sc = kit.setup(SECONDS)
fps = sc.render.fps
panels = {"naive": ("blue", -1.75), "reserve": ("green", 1.75)}
for policy, (colour, cx) in panels.items():
    node = lambda u, v: (cx + (u - 0.65) * S, 1.2 + (v - 0.65) * S)
    kit.box("pad", (3.1, 3.6, 0.02), (cx, 1.45, 0.01), "#e6ecee", bevel=0.01)
    for k in (0, 1):                                                              # the grid: two roads each way, crossing at four intersections
        kit.box("road", (3.0 * S, 0.5, 0.01), (cx, node(0, k)[1], 0.025), "road", bevel=0)
        kit.box("road", (0.5, 3.3 * S, 0.01), (node(k, 0)[0], node(0, 0.775)[1], 0.025), "road", bevel=0)
    pads = {(u, v): kit.cyl("held", 0.3, 0.012, (*node(u, v), 0.04), "z", "amber", segments=32) for u in (0, 1) for v in (0, 1)}

    # replay the lesson's own Sim, tick by tick
    sim = m.Sim(JOBS, 4, policy)
    paths = sim.paths
    wp = []                                                                       # per robot: hold spot, the route, a parking spot past the goal
    for r, p in enumerate(paths):
        d0 = (p[1][0] - p[0][0], p[1][1] - p[0][1])
        d1 = (p[-1][0] - p[-2][0], p[-1][1] - p[-2][1])
        park = 1.2 if r == 0 else 0.6                                            # robots 0 and 1 both leave through (1, 1): the first one parks farther
        wp.append([(p[0][0] - 0.6 * d0[0], p[0][1] - 0.6 * d0[1])] + list(p) + [(p[-1][0] + park * d1[0], p[-1][1] + park * d1[1])])
    state = [[0.0] * 4]                                                           # progress along wp[r] after each tick (0 = holding outside)
    held, cycle = [set()], None
    for t in range(TICKS):
        before = set(sim.res)
        sim.step()
        state.append([float(len(paths[r]) + 1) if r not in sim.at and r not in sim.queue else float(sim.at[r] + 1) if r in sim.at else 0.0 for r in range(4)])
        held.append(before | set(sim.res))
        cycle = cycle or (m.find_cycle(sim.wait_for()), sim.wait_for(), dict(sim.at))
    for pad_xy, pad in pads.items():
        for k in range(TICKS):
            pad.hide_render = pad_xy not in held[k + 1]
            pad.keyframe_insert("hide_render", frame=int((LEAD + k * TICK) * fps) + 1)
        pad.hide_render = True
        pad.keyframe_insert("hide_render", frame=int((LEAD + TICKS * TICK) * fps) + 1)

    for r in range(4):
        root, wheels = kit.rover(f"{policy}{r}", colour)
        root.scale = (1.2,) * 3
        yaw = None
        travelled = 0.0
        last = None
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
            yaw += max(-0.3, min(0.3, (want - yaw + math.pi) % (2 * math.pi) - math.pi))      # turn at corners, not instantly
            if last:
                travelled += math.dist(last, (x, y))
            last = (x, y)
            kit.key(root, f, loc=(x, y, 0), rot=(0, 0, yaw))
            for w in wheels:
                kit.key(w, f, rot=(0, travelled / (0.075 * 1.2), 0))

    if cycle and cycle[0]:                                                        # red arrows along the wait-for loop, drawn once everyone has stopped
        _, g, at = cycle
        for r in cycle[0]:
            (ax, ay), (bx, by) = node(*paths[r][at[r]]), node(*paths[g[r]][at[g[r]]])
            L, yaw = math.dist((ax, ay), (bx, by)) - 0.7, math.atan2(by - ay, bx - ax)
            arr = kit.arrow("waits-for", "red", 0.035)
            arr.location, arr.rotation_euler = (ax + 0.35 * math.cos(yaw), ay + 0.35 * math.sin(yaw), 0.07), (0, 0, yaw)
            f0 = int((LEAD + TICK * 1.1) * fps)
            for f, sx in ((f0, 0.001), (f0 + 8, 1.0)):
                arr.scale = (sx * L, sx, sx)
                arr.keyframe_insert("scale", frame=f)
kit.camera((0, -3.25, 4.15), (0, 1.0, 0), lens=26)
kit.render(__file__)
