# 레슨 06/03 클립: 스탠드 위 depth 카메라가 비스듬한 책상을 점군으로 만들고, 최소제곱 평면(파랑)과 RANSAC 평면(초록)에 맞춰 세운 블록이 얼마나 다르게 서는지 보인다
import math
import pathlib
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Quaternion, Vector

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
K, H, V0 = (150.0, 150.0, 80.0, 60.0), 0.4, 3
c, s = 0.5, math.sqrt(0.75)                                    # the camera looks 60 degrees down at a table 1 m away (n . X = 1)
RCW = np.column_stack([[0, -1, 0], [-s, 0, -c], [c, 0, -s]])   # camera frame (x right, y down, z forward) to world
CAM = np.array([0.0, 0.0, H + 1.0])
world = lambda P: CAM + np.asarray(P) @ RCW.T
depth, truth = m.make_scene(1)
P = m.depth_to_points(depth, *K)
n_ls, d_ls = m.fit_plane(P)
n_rs, d_rs, _ = m.ransac_plane(P, 0.012, 150)
V = m.voxel_downsample(P, 0.05)                                # about 1300 points drawn
bad = np.abs(V @ n_rs - d_rs) >= 0.012                         # outliers of the RANSAC plane: the box top and the flyers
clean = m.make_scene(1, noise=0.0, flyers=0.0)[0]
top = np.zeros(clean.shape, bool); top[40:80, 60:110] = True   # the box rows and columns used by make_scene
bt, tab = world(m.depth_to_points(np.where(top, clean, np.nan), *K)), world(m.depth_to_points(np.where(top, np.nan, clean), *K))

sc = kit.setup(5)
kit.table(tuple(np.ptp(tab[:, :2], axis=0)), H, tuple(tab[:, :2].mean(0)))
kit.box("box", tuple(np.ptp(bt[:, :2], axis=0)) + (bt[:, 2].mean() - H,), (*bt[:, :2].mean(0), (bt[:, 2].mean() + H) / 2), "sky", bevel=0.01)
rig = kit.empty("rig", tuple(CAM)); rig.rotation_euler = (0, math.radians(60), 0)
kit.box("cam", (0.16, 0.14, 0.1), (0, 0, 0), "dark", bevel=0.015, parent=rig); kit.cyl("lens", 0.035, 0.06, (0.1, 0, 0), "x", "grey", parent=rig)
kit.cyl("stand", 0.025, CAM[2], (-0.1, 0, CAM[2] / 2), "z", "grey"); kit.cyl("foot", 0.18, 0.02, (-0.1, 0, 0.01), "z", "dark", bevel=0.008)

mesh = {}
for name, col, rad in (("grey", "grey", 0.016), ("red", "red", 0.032)):     # the red points are the ones to see at phone width
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rad)
    mesh[name] = bpy.data.meshes.new("pt-" + name); bm.to_mesh(mesh[name]); bm.free(); mesh[name].materials.append(kit.mat(col))
W = world(V)
for w, b, r in zip(W, bad, np.argsort(np.argsort(np.linalg.norm(V, axis=1)))):   # the scan sweeps from the near points to the far ones
    ob = bpy.data.objects.new("pt", mesh["red" if b else "grey"]); sc.collection.objects.link(ob); ob.location = tuple(w)
    f0 = 4 + 30 * r / len(V)
    kit.key(ob, 1, loc=tuple(w)); ob.scale = (0.001,) * 3; ob.keyframe_insert("scale", frame=f0); ob.scale = (1, 1, 1); ob.keyframe_insert("scale", frame=f0 + 3)

def plane(n, d, xy):                                           # world up-normal and the height of the camera-frame plane n . X = d over xy
    nw = RCW @ n
    return -nw, CAM[2] + (d - nw[:2] @ (np.asarray(xy) - CAM[:2])) / nw[2]
def lay(ob, up, centre, f0, f1, lift=0.0):                      # tilt a body to the up-normal and key it from `lift` above to its place
    ob.rotation_mode = "QUATERNION"; q = Vector((0, 0, 1)).rotation_difference(Vector(up))
    for f, h in ((f0, lift), (f1, 0.0)):
        ob.location, ob.rotation_quaternion = (centre[0], centre[1], centre[2] + h), q
        ob.keyframe_insert("location", frame=f); ob.keyframe_insert("rotation_quaternion", frame=f)

mid = tab[:, :2].mean(0)
for name, (n, d), colour, dx, dy in (("ls", (n_ls, d_ls), "blue", -0.4, -0.5), ("ransac", (n_rs, d_rs), "green", 0.4, 0.5)):
    up, zc = plane(n, d, mid)
    sheet = kit.box(name + "-plane", (1.1, 1.7, 0.004), (0, 0, 0), kit.ghost(colour, 0.35), bevel=0)
    lay(sheet, up, (*mid, zc + (0.003 if name == "ransac" else 0)), 38, 38)
    sheet.scale = (0.01,) * 3; sheet.keyframe_insert("scale", frame=38); sheet.scale = (1, 1, 1); sheet.keyframe_insert("scale", frame=46)
    xy = mid + (dx, dy); up, zc = plane(n, d, xy)               # the place pose is commanded from this plane: its height and its normal
    block = kit.box(name + "-block", (0.12, 0.12, 0.9), (0, 0, 0), colour, bevel=0.015)    # a tall block, 0.9 m, shows the lean
    lay(block, up, np.array([*xy, zc]) + up * 0.45, 56, 92, lift=0.5)
    block.scale = (0.001,) * 3; block.keyframe_insert("scale", frame=54); block.scale = (1, 1, 1); block.keyframe_insert("scale", frame=56)
    plumb = kit.cyl(name + "-plumb", 0.012, 0.9, (xy[0] + 0.17, xy[1], H + 0.45), "z", "dark")    # a plumb post, truly vertical, beside the block to read the lean against
    plumb.scale = (0.001,) * 3; plumb.keyframe_insert("scale", frame=54); plumb.scale = (1, 1, 1); plumb.keyframe_insert("scale", frame=56)
cam = kit.camera((2.4, -3.9, 1.9), (0.7, 0.0, 0.62), lens=38)
for f, pos, tgt, lens in ((1, (2.4, -3.9, 1.9), (0.7, 0.0, 0.62), 38), (46, (2.4, -3.9, 1.9), (0.7, 0.0, 0.62), 38),   # wide for the scan, then in on the two blocks, side-on to the lean
                          (70, (mid[0] + 1.2, mid[1] - 3.7, H + 0.55), (mid[0], mid[1], H + 0.36), 50)):
    cam.location, cam.data.lens = pos, lens
    cam.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    cam.data.dof.focus_distance = (Vector(tgt) - Vector(pos)).length
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f); cam.data.dof.keyframe_insert("focus_distance", frame=f)
kit.render(__file__)
