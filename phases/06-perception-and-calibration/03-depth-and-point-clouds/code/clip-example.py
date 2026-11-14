# 레슨 06/03 예시 클립: RANSAC 세 번의 회차. 무작위 점 세 개(주황)로 평면을 만들고 1.2 cm 안의 점(초록)을 센다. 처음 두 회차는 빗나가고 마지막 회차가 책상을 찾는다
import math
import pathlib
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
K, H, THR = (150.0, 150.0, 80.0, 60.0), 0.4, 0.012
c, s = 0.5, math.sqrt(0.75)                                    # the camera looks 60 degrees down at a table 1 m away (n . X = 1)
RCW = np.column_stack([[0, -1, 0], [-s, 0, -c], [c, 0, -s]])   # camera frame (x right, y down, z forward) to world
CAM = np.array([0.0, 0.0, H + 1.0])
world = lambda P: CAM + np.asarray(P) @ RCW.T
depth, truth = m.make_scene(1)
P = m.depth_to_points(depth, *K)
V = m.voxel_downsample(P, 0.05)                                # about 1300 points drawn
rng, picks = np.random.default_rng(0), {}                      # the draws of ransac_plane(P, 0.012, 150): rounds 1, 24 and 20 of the run
for it in range(25):
    idx = rng.choice(len(P), 3, replace=False)
    if it in (1, 24, 20):
        picks[it] = P[idx]
rounds = []
for it, colour in ((1, "blue"), (24, "blue"), (20, "green")):
    a, b, cc = picks[it]
    n = np.cross(b - a, cc - a); n /= np.linalg.norm(n)
    d = float(n @ a)
    n, d = (n, d) if d >= 0 else (-n, -d)
    print("round", it, "inliers", int((np.abs(P @ n - d) < THR).sum()), "tilt", round(float(np.degrees(np.arccos(abs(n @ truth)))), 1))
    rounds.append((picks[it], n, d, colour))

sc = kit.setup(5)
clean = m.make_scene(1, noise=0.0, flyers=0.0)[0]
top = np.zeros(clean.shape, bool); top[40:80, 60:110] = True   # the box rows and columns used by make_scene
bt, tab = world(m.depth_to_points(np.where(top, clean, np.nan), *K)), world(m.depth_to_points(np.where(top, np.nan, clean), *K))
kit.table(tuple(np.ptp(tab[:, :2], axis=0)), H, tuple(tab[:, :2].mean(0)))
kit.box("box", tuple(np.ptp(bt[:, :2], axis=0)) + (bt[:, 2].mean() - H,), (*bt[:, :2].mean(0), (bt[:, 2].mean() + H) / 2), "sky", bevel=0.01)
rig = kit.empty("rig", tuple(CAM)); rig.rotation_euler = (0, math.radians(60), 0)
kit.box("cam", (0.16, 0.14, 0.1), (0, 0, 0), "dark", bevel=0.015, parent=rig); kit.cyl("lens", 0.035, 0.06, (0.1, 0, 0), "x", "grey", parent=rig)
kit.cyl("stand", 0.025, CAM[2], (-0.1, 0, CAM[2] / 2), "z", "grey"); kit.cyl("foot", 0.18, 0.02, (-0.1, 0, 0.01), "z", "dark", bevel=0.008)

def appear(ob, f0, f1=None):                                   # pop in at f0 and, if f1 is given, shrink away again at f1
    for f, k in ((f0 - 3, 0.001), (f0, 1.0)) + (((f1, 1.0), (f1 + 3, 0.001)) if f1 else ()):
        ob.scale = (k,) * 3; ob.keyframe_insert("scale", frame=f)

mesh = {}
for name in ("grey", "green", "blue", "amber"):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.014 if name != "amber" else 0.045)
    mesh[name] = bpy.data.meshes.new("pt-" + name); bm.to_mesh(mesh[name]); bm.free(); mesh[name].materials.append(kit.mat(name))
for w in world(V):
    ob = bpy.data.objects.new("pt", mesh["grey"]); sc.collection.objects.link(ob); ob.location = tuple(w)
for r, (tri, n, d, colour) in enumerate(rounds):
    f0, last = 8 + 36 * r, r == len(rounds) - 1
    f1 = None if last else f0 + 30
    for p in world(tri):
        ob = bpy.data.objects.new("pick", mesh["amber"]); sc.collection.objects.link(ob); ob.location = tuple(p); appear(ob, f0, f1)
    nw = RCW @ n                                               # the plane n . X = d seen from the world: up-normal and height over the table middle
    mid = tab[:, :2].mean(0)
    zc = CAM[2] + (d - nw[:2] @ (mid - CAM[:2])) / nw[2]
    sheet = kit.box("plane", (1.1, 1.7, 0.004), (0, 0, 0), kit.ghost(colour, 0.35), bevel=0)
    sheet.rotation_mode = "QUATERNION"; sheet.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(-nw))
    sheet.location = (*mid, zc); sheet.keyframe_insert("location", frame=1); appear(sheet, f0 + 6, f1)
    inl = np.abs(V @ n - d) < THR
    for w in world(V)[inl]:
        ob = bpy.data.objects.new("in", mesh["green"]); sc.collection.objects.link(ob); ob.location = tuple(w); ob.scale = (1.2,) * 3; appear(ob, f0 + 14, f1)
kit.camera((3.1, -2.4, 2.1), (0.7, 0.0, 0.6), lens=34)
kit.render(__file__)
