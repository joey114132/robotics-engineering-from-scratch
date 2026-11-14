# 레슨 00/03 예시 클립: 어깨 origin 이 frame 을 90도 돌린 뒤 elbow 와 wrist 의 offset 을 차례로 잇는다. 초록은 돌아간 frame 을 따라가고 파란 ghost 는 방 기준 x 로만 간다
import math
import pathlib
import sys

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
ghost = kit.ghost("blue", 0.55)
kit.cyl("foot", 0.18, 0.03, (0, 0, 0.015), "z", "dark", bevel=0.01)
kit.cyl("post", 0.07, z0, (0, 0, z0 / 2), "z", "grey")
kit.cyl("shoulder", 0.1, 0.1, (0, 0, z0), "z", "dark", bevel=0.01)
room = kit.empty("room", (0, 0, z0))                    # the room's own axes, standing still
for name, rot, length in (("room-x", 0.0, 1.0), ("room-y", math.pi / 2, 0.7)):
    a = kit.arrow(name, "grey", 0.012)
    a.parent, a.rotation_euler, a.scale = room, (0, 0, rot), (length, 1, 1)
turned = kit.empty("turned", (0, 0, z0))                # the upper link's frame: it turns by the origin's yaw
for name, rot, length in (("link-x", 0.0, 0.85), ("link-y", math.pi / 2, 0.55)):
    a = kit.arrow(name, "dark", 0.016)
    a.parent, a.rotation_euler, a.scale = turned, (0, 0, rot), (length, 1, 1)
flat = kit.empty("flat", (0, 0, z0))                    # the naive reading never turns
g1, g2 = offsets("g", "green", turned)
n1, n2 = offsets("n", ghost, flat)
hg, hn = hand("hand", "dark", "green"), hand("n-hand", ghost, ghost)
gap = kit.cyl("gap", 0.012, 1.0, axis="x", colour="red", segments=12)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / fps
    kit.key(turned, f, rot=(0, 0, yaw * smooth((t - 0.6) / 1.3)))
    for (a, b) in ((g1, g2), (n1, n2)):
        for arrow, length in ((a, L1 * smooth((t - 2.0) / 1.2)), (b, L2 * smooth((t - 3.2) / 1.0))):
            thick = min(1.0, length / 0.12)                    # an arrow that has not started growing is a point, not a disc
            arrow.scale = (max(length, 1e-4), max(thick, 1e-4), max(thick, 1e-4))
        a.keyframe_insert("scale", frame=f)
        b.keyframe_insert("scale", frame=f)
    shown = t >= 4.3
    kit.key(hg, f, loc=tuple(true) if shown else (0, 0, -1), rot=(0, 0, math.atan2(true[1], true[0])))
    kit.key(hn, f, loc=tuple(naive) if shown else (0, 0, -1), rot=(0, 0, 0))
    d = naive - true
    gap.scale = (max(float((d ** 2).sum() ** 0.5) * smooth((t - 4.4) / 0.5), 1e-4), 1, 1)
    gap.keyframe_insert("scale", frame=f)
    kit.key(gap, f, loc=(naive + true) / 2, rot=(0, 0, math.atan2(d[1], d[0])))
kit.camera((-0.9, -1.9, 2.5), (0.45, 0.5, 0.1), lens=46)
kit.render(__file__)
