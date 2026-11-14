# 레슨 01/05 클립: 3축 gimbal 위의 카메라가 pitch 를 60도에서 120도까지 매끄럽게 기울인다. 90도를 지나면 R_to_euler 가 yaw 링과 roll 링을 180도 뒤집는다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import bpy
import kit

m = kit.lesson_main(__file__)
SECONDS, FPS, D, CZ = 6.0, 24, math.pi / 180, 0.85
sc = kit.setup(SECONDS)
kit.camera((-1.8, -2.3, 2.1), (0.0, 0.0, CZ - 0.2), lens=38)


def circle(name, r, plane, parent, colour, bead=None):
    """A ring of radius r in the plane ('yz', 'xy' or 'xz'), with an amber bead at 45 degrees round it, off every axle."""
    pts = [(0, r * math.cos(a), r * math.sin(a)) if plane == "yz" else (r * math.cos(a), r * math.sin(a), 0) if plane == "xy" else (r * math.cos(a), 0, r * math.sin(a))
           for a in [i * math.pi / 45 for i in range(91)]]
    ring = kit.tube(name, pts, 0.016, colour)
    ring.parent = parent
    if bead:
        kit.ball(name + "-bead", 0.045, pts[11], "amber", parent=parent)


def pin(name, a, b, parent, r=0.012):          # a short axle between two rings
    mid = [(u + v) / 2 for u, v in zip(a, b)]
    ln = math.dist(a, b)
    axis = "x" if abs(a[0] - b[0]) > 1e-6 else "y" if abs(a[1] - b[1]) > 1e-6 else "z"
    kit.cyl(name, r, ln, mid, axis, "dark", parent=parent)


kit.cyl("stand-foot", 0.25, 0.04, (0, 0, 0.02), "z", "dark", bevel=0.01)
kit.cyl("stand-post", 0.06, CZ - 0.5, (0, 0, (CZ - 0.5) / 2 + 0.04), "z", "grey")
yaw = kit.empty("yaw-axis", (0, 0, CZ))
circle("outer", 0.62, "yz", yaw, "navy", bead=True)                       # the yaw ring: turns about the vertical axis
pitch = kit.empty("pitch-axis", (0, 0, 0), yaw)
circle("middle", 0.5, "xy", pitch, "blue", bead=True)                     # the pitch ring: axle along y
pin("pitch-axle+", (0, 0.5, 0), (0, 0.62, 0), pitch)
pin("pitch-axle-", (0, -0.5, 0), (0, -0.62, 0), pitch)
roll = kit.empty("roll-axis", (0, 0, 0), pitch)
circle("inner", 0.38, "xz", roll, "sky", bead=True)                       # the roll ring: axle along x
pin("roll-axle+", (0.38, 0, 0), (0.5, 0, 0), roll)
pin("roll-axle-", (-0.38, 0, 0), (-0.5, 0, 0), roll)
kit.box("camera-body", (0.22, 0.16, 0.14), (0, 0, 0), "dark", bevel=0.02, parent=roll)      # the tool: a camera that looks along the roll axis
kit.cyl("camera-lens", 0.06, 0.14, (0.17, 0, 0), "x", "pearl", bevel=0.008, parent=roll)
kit.box("camera-fin", (0.08, 0.02, 0.1), (-0.05, 0, 0.11), "amber", bevel=0.005, parent=roll)

bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"      # the angle reader jumps between two frames, so nothing may ease across the jump
for f in range(sc.frame_start, sc.frame_end + 1):
    s = min(max((f / FPS - 0.4) / 5.2, 0.0), 1.0)
    true_pitch = (60 + 60 * s) * D                       # a smooth tilt about y, roll and yaw both zero
    r, p, y, locked = m.R_to_euler(m.euler_to_R(0.0, true_pitch, 0.0))      # what the angle reader reports for that pose
    kit.key(yaw, f, rot=(0, 0, y))
    kit.key(pitch, f, rot=(0, p, 0))
    kit.key(roll, f, rot=(r, 0, 0))
kit.render(__file__)
