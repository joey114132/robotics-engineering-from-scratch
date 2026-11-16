# 레슨 00/03 예시 클립: elbow 와 wrist 의 offset 두 개를 x 방향으로 잇고(초록과 파랑이 겹친다) 어깨 origin 의 90도 회전이 일어나면 초록은 돌아간 frame 을 따라가고 파랑은 방 기준 x 에 남는다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, SECONDS = 2.0, 5.0                                   # drawing scale: 1 m of the URDF is drawn as 2 m
links, joints = m.parse_urdf(m.URDF)
ch = m.chain(joints, m.find_root(links, joints), "hand")
yaw = float(joints["shoulder"]["rpy"][2])               # the 90 degree turn written in the shoulder <origin>
z0 = float(joints["shoulder"]["xyz"][2]) * S
L1, L2 = float(joints["elbow"]["xyz"][0]) * S, float(joints["wrist"]["xyz"][0]) * S   # the two offsets, each written along its parent's x
true = m.link_positions(ch, {"shoulder": 0.0, "elbow": 0.0})["hand"] * S
naive = m.naive_position(ch) * S
assert np.allclose(np.array([0.0, 0.0, z0]) + (L1 + L2) * np.array([math.cos(yaw), math.sin(yaw), 0.0]), true) and np.allclose(naive, [L1 + L2, 0.0, z0])   # the drawn chains end exactly where the lesson's two functions put the hands


def smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def hand(name, palm, fingers):
    h = kit.empty(name)
    kit.box(name + "-palm", (0.06, 0.16, 0.1), (0.03, 0, 0), palm, bevel=0.01, parent=h)
    for y in (0.05, -0.05):
        kit.box(name + "-finger", (0.14, 0.04, 0.05), (0.13, y, 0), fingers, bevel=0.008, parent=h)
    return h


def offsets(name, colour, parent):                      # two arrows laid end to end along the parent frame's x
    a, b = kit.arrow(name + "1", colour, 0.026), kit.arrow(name + "2", colour, 0.026)
    a.parent, b.parent = parent, parent
    b.location = (L1, 0, 0)
    return a, b


sc = kit.setup(SECONDS)
fps = sc.render.fps
kit.cyl("foot", 0.18, 0.03, (0, 0, 0.015), "z", "dark", bevel=0.01)
kit.cyl("post", 0.07, z0, (0, 0, z0 / 2), "z", "grey")
kit.cyl("shoulder", 0.1, 0.1, (0, 0, z0), "z", "dark", bevel=0.01)
THIN = 0.45                                             # the two frames' axes are slim, so the green and blue offsets are what the eye lands on
room = kit.empty("room", (0, 0, z0))                    # the room's own axes, standing still
for name, rot, length in (("room-x", 0.0, 0.8), ("room-y", math.pi / 2, 0.6)):
    a = kit.arrow(name, "grey", 0.012)
    a.parent, a.rotation_euler, a.scale = room, (0, 0, rot), (length, THIN, THIN)
turned = kit.empty("turned", (0, 0, z0))                # the upper link's frame: it turns by the origin's yaw
for name, rot, length in (("link-x", 0.0, 0.7), ("link-y", math.pi / 2, 0.5)):
    a = kit.arrow(name, "dark", 0.016)
    a.parent, a.rotation_euler, a.scale = turned, (0, 0, rot), (length, THIN, THIN)
flat = kit.empty("flat", (0, 0, z0))                    # the naive reading never turns
g1, g2 = offsets("g", "green", turned)
n1, n2 = offsets("n", "blue", flat)
hg, hn = hand("hand", "dark", "green"), hand("n-hand", kit.mat("blue", kind="plastic"), kit.mat("blue", kind="plastic"))
gap = kit.cyl("gap", 0.02, 1.0, axis="x", colour="red", segments=12)
origin = np.array([0.0, 0.0, z0])
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / fps
    yaw_t = yaw * smooth((t - 2.4) / 1.5)                            # first both chains lie along x, then the frame turns and only the green one follows
    kit.key(turned, f, rot=(0, 0, yaw_t))
    lens = (L1 * smooth((t - 0.5) / 0.9), L2 * smooth((t - 1.2) / 0.8))
    for (a, b) in ((g1, g2), (n1, n2)):
        for arrow, length in ((a, lens[0]), (b, lens[1])):
            thick = min(1.0, length / 0.12)                    # an arrow that has not started growing is a point, not a disc
            arrow.scale = (max(length, 1e-4), max(thick, 1e-4), max(thick, 1e-4))
        a.keyframe_insert("scale", frame=f)
        b.keyframe_insert("scale", frame=f)
    reach = lens[0] + lens[1]                                     # each hand rides the end of its own chain
    pg = origin + reach * np.array([math.cos(yaw_t), math.sin(yaw_t), 0.0])
    pn = origin + reach * np.array([1.0, 0.0, 0.0])
    kit.key(hg, f, loc=tuple(pg), rot=(0, 0, yaw_t))
    kit.key(hn, f, loc=tuple(pn), rot=(0, 0, 0))
    d = pn - pg
    gap.scale = (max(float((d ** 2).sum() ** 0.5), 1e-4), 1, 1)
    gap.keyframe_insert("scale", frame=f)
    kit.key(gap, f, loc=(pn + pg) / 2, rot=(0, 0, math.atan2(d[1], d[0])))
kit.camera((0.45, -0.95, 3.35), (0.45, 0.58, 0.05), lens=46)   # high enough that the turned hand's fingertips stay inside the top edge
kit.render(__file__)
