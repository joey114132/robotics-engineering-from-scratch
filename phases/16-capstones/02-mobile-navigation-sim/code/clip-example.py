# 레슨 16/02 예시 클립: 열린 바닥에서 로버 두 대가 직선으로 달린다. 파란 로버의 믿음은 갈수록 벗어나고 초록 로버는 1초마다 보정한다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, RS, DT, SPEED, T_END, SECONDS = 0.55, 1.0, 0.05, 10.0 / 4.6, 10.0, 5.5   # 1 m drawn as 0.55; plays 2.2x; the clip shows driving seconds 0 to 10, then holds
BAD = dict(scale_err=0.03, w_bias=0.03, sigma=0.02)                          # the lesson's `bad` wheel error
START, LANE = (1.5, 1.5), 1.0                                                # straight 10 m route along +x; the two lanes are 1 m apart
lane_y = {False: START[1] - LANE / 2, True: START[1] + LANE / 2}
runs = {fix: m.drive([(START[0], lane_y[fix]), (START[0] + 10.0, lane_y[fix])], (START[0], lane_y[fix], 0.0),
                     **BAD, **({"landmarks": m.LANDMARKS} if fix else {})) for fix in (False, True)}

sc = kit.setup(SECONDS)
for fix in (False, True):                                                    # the planned route of each rover, a thin line on the floor
    kit.tube("route", [(START[0] * S, lane_y[fix] * S, 0.012), ((START[0] + 7.0) * S, lane_y[fix] * S, 0.012)], 0.012, "sky")
    kit.cyl("start", 0.05, 0.012, (START[0] * S, lane_y[fix] * S, 0.006), "z", "amber")
ghosts = {False: kit.ghost("blue", 0.55), True: kit.ghost("green", 0.55)}
for fix, col in ((False, "blue"), (True, "green")):
    traj, belief = runs[fix]
    root, wheels = kit.rover("rover", col)
    root.scale = (RS,) * 3
    bel, _ = kit.rover("belief", col)
    bel.scale = (RS,) * 3
    for ob in bel.children_recursive:
        ob.data.materials.clear()
        ob.data.materials.append(ghosts[fix])
    yaw = np.unwrap(traj[:, 2])
    turn = np.r_[np.diff(yaw) / DT, 0.0]
    spin = [np.cumsum((S * 0.6 + sgn * turn * 0.2 * RS) * DT) / (0.075 * RS) for sgn in (-1, 1)]
    for s in range(1, 11):                                                   # one dark mark per second where the real rover was
        k = int(s / DT) - 1
        mark = kit.cyl("mark", 0.035, 0.01, (traj[k, 0] * S, traj[k, 1] * S, 0.005), "z", "dark")
        f0 = 1 + int(round(s / SPEED * sc.render.fps))
        for f, v in ((max(f0 - 1, 1), 0.001), (f0, 1.0)):
            mark.scale = (v, v, v)
            mark.keyframe_insert("scale", frame=f)
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = min(int(min((f - 1) / sc.render.fps * SPEED, T_END) / DT), len(traj) - 1)
        kit.key(root, f, loc=(traj[k, 0] * S, traj[k, 1] * S, 0), rot=(0, 0, traj[k, 2]))
        for w, a in zip(wheels, (spin[0][k], spin[1][k])):
            kit.key(w, f, rot=(0, a, 0))
        kit.key(bel, f, loc=(belief[k, 0] * S, belief[k, 1] * S, 0), rot=(0, 0, belief[k, 2]))
kit.camera((2.45, -2.0, 4.0), (2.45, 0.6, 0.0), lens=36)
kit.render(__file__)
