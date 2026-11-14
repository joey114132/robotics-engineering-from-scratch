# 레슨 00/03 클립: 레슨의 URDF 팔이 어깨를 돌린다. origin을 부모 frame에서 이어 붙인 손(초록)과 그냥 더한 손(파란 ghost)이 점점 벌어진다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, SECONDS = 2.0, 5.0                                   # drawing scale: 1 m of the URDF is drawn as 2 m
links, joints = m.parse_urdf(m.URDF)
root = m.find_root(links, joints)
ch_hand, ch_cam = m.chain(joints, root, "hand"), m.chain(joints, root, "camera")
naive = m.naive_position(ch_hand) * S                   # every origin added as if it were in the world frame

def bar(name, length, radius, colour):
    return kit.cyl(name, radius, length, axis="x", colour=colour)

def hand(name, palm, fingers):
    h = kit.empty(name)
    kit.box(name + "-palm", (0.06, 0.16, 0.1), (0.03, 0, 0), palm, bevel=0.01, parent=h)
    for y in (0.05, -0.05):
        kit.box(name + "-finger", (0.14, 0.04, 0.05), (0.13, y, 0), fingers, bevel=0.008, parent=h)
    return h

sc = kit.setup(SECONDS)
ghost = kit.ghost("blue", 0.4)
kit.cyl("foot", 0.18, 0.03, (0, 0, 0.015), "z", "dark", bevel=0.01)
kit.cyl("post", 0.07, 0.2, (0, 0, 0.1), "z", "grey")
kit.cyl("shoulder", 0.1, 0.1, (0, 0, 0.2), "z", "dark", bevel=0.01)
kit.cyl("shoulder-cap", 0.055, 0.12, (0, 0, 0.2), "z", "amber")
upper, fore = bar("upper", 0.3 * S, 0.04, "green"), bar("fore", 0.2 * S, 0.032, "green")
elbow = kit.cyl("elbow", 0.075, 0.1, axis="z", colour="dark", bevel=0.01)
kit.cyl("elbow-cap", 0.042, 0.12, (0, 0, 0), "z", "amber", parent=elbow)
palm = hand("hand", "dark", "green")
cam = kit.empty("camera")                               # the URDF's cam_mount: it turns with the upper arm
kit.box("cam-body", (0.1, 0.08, 0.08), (0, 0, 0), "dark", bevel=0.01, parent=cam)
kit.cyl("cam-lens", 0.025, 0.05, (0.06, 0, 0), "x", "amber", parent=cam)

bar("n-upper", 0.3 * S, 0.04, ghost).location = (0.3 * S / 2, 0, 0.1 * S)       # the naive arm lies along x
bar("n-fore", 0.2 * S, 0.032, ghost).location = (0.3 * S + 0.2 * S / 2, 0, 0.1 * S)
hand("n-hand", ghost, ghost).location = naive
gap = kit.cyl("gap", 0.012, 1.0, axis="x", colour="red", segments=12)

def smooth(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)

for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps
    q = -math.pi / 2 * (1 - smooth((t - 0.6) / 2.8))   # shoulder from -90 deg (arm along x) to 0 (the origin's own 90 deg yaw)
    pos = m.link_positions(ch_hand, {"shoulder": q, "elbow": 0.0})
    p_up, p_fore, p_hand = (pos[n] * S for n in ("upper", "fore", "hand"))
    yaw = math.atan2(p_fore[1] - p_up[1], p_fore[0] - p_up[0])
    kit.key(upper, f, loc=(p_up + p_fore) / 2, rot=(0, 0, yaw))
    kit.key(fore, f, loc=(p_fore + p_hand) / 2, rot=(0, 0, yaw))
    kit.key(elbow, f, loc=p_fore)
    kit.key(palm, f, loc=p_hand, rot=(0, 0, yaw))
    kit.key(cam, f, loc=m.link_positions(ch_cam, {"shoulder": q, "elbow": 0.0})["camera"] * S, rot=(0, 0, yaw))
    d = naive - p_hand
    gap.scale = (max(float((d ** 2).sum() ** 0.5), 1e-4), 1, 1)
    gap.keyframe_insert("scale", frame=f)
    kit.key(gap, f, loc=(naive + p_hand) / 2, rot=(0, 0, math.atan2(d[1], d[0])))
kit.camera((-0.9, -1.9, 2.5), (0.45, 0.5, 0.1), lens=46)
kit.render(__file__)
