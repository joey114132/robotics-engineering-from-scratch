# Blender 장면 키트: 레슨 클립(code/clip.py)이 쓰는 조명, 바닥, 재질, 자동차, 팔, 렌더 도우미
"""Shared parts for lesson clips. A clip script runs inside Blender:

    blender -b -P phases/<phase>/<lesson>/code/clip.py

It imports this file, builds a small scene from real objects (a toy car, a bench arm), keys them with numbers
computed by the lesson's own code/main.py, and calls render(). Clips carry no text: captions live in the page,
so one clip serves every language.
"""
import math
import os
import pathlib
import subprocess
import sys
import tempfile

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = pathlib.Path(__file__).resolve().parents[2]
# the site's light-theme colours, so a clip sits in the page like the drawn scenes
PAL = {"blue": "#4f8df0", "navy": "#1f5fd6", "sky": "#a9c8fb", "green": "#2f9e62", "red": "#d9541e", "amber": "#f0a530",
       "dark": "#27343c", "grey": "#9fb1ba", "pearl": "#f4f6f7", "floor": "#dfe8ec", "road": "#aebdc5", "white": "#ffffff", "wood": "#d9b78c"}
_mats = {}
# CLIP_LOOK=real renders with the ray tracer, an environment light that ships with Blender, real materials (painted metal,
# brushed aluminium, rubber, concrete, asphalt) and a shallow depth of field. The default look is the quick toy-studio one.
REAL = os.environ.get("CLIP_LOOK") == "real"
_REAL_SURFACE = {   # kind or palette name: (metallic, roughness, coat weight, colour override or None)
    "grey": (1.0, 0.4, 0.0, "#c3c6ca"), "alu": (1.0, 0.45, 0.0, "#aab4c0"), "steel": (1.0, 0.3, 0.0, "#8d9196"),
    "dark": (0.0, 0.55, 0.0, "#141618"), "motor": (0.0, 0.42, 0.0, "#17191b"), "tyre": (0.0, 0.8, 0.0, "#0e0e0f"), "tyre75": (0.0, 0.8, 0.0, "#0e0e0f"),
    "glass": (0.0, 0.05, 1.0, "#07090c"), "pearl": (0.0, 0.35, 1.0, "#e9e7e0"), "white": (0.0, 0.55, 0.0, "#e9e7e0"),
    "floor": (0.0, 0.8, 0.0, "#9b9a95"), "road": (0.0, 0.92, 0.0, "#34363a"), "wood": (0.0, 0.42, 0.35, "#a9794a"),
    "line": (0.0, 0.72, 0.0, "#e8e4d8"), "wall": (0.0, 0.85, 0.0, "#d9d5cb"), "plastic": (0.0, 0.38, 0.25, None), "matte": (0.0, 0.85, 0.0, None),
    "enamel": (0.0, 0.5, 0.35, None), "marker": (0.0, 0.45, 0.2, None)}


def lesson_main(clip_file):
    """Import code/main.py that sits next to the clip script."""
    here = pathlib.Path(clip_file).resolve().parent
    sys.path.insert(0, str(here))
    import importlib
    return importlib.import_module("main")


def _rgb(hexs):
    h = hexs.lstrip("#")
    return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4)) + (1.0,)   # sRGB to linear


def mat(name, rough=0.42, emit=0.0, kind=None):
    """Toy-plastic material in a palette colour (or any #rrggbb). kind picks a real-look surface recipe (REAL only)."""
    key = (name, rough, emit, kind)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    col = _rgb(PAL.get(name, name))
    if REAL:   # painted parts get a glossy clear coat; named surfaces get their own metal, rubber or stone values
        metal, rough, coat, override = _REAL_SURFACE.get(kind or name, (0.0, 0.35, 1.0, None))
        override = None if kind == "line" and name != "white" else override   # painted lines keep their own hue
        col = _rgb(override) if override else col
        bsdf.inputs["Metallic"].default_value = metal
        bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Base Color"].default_value = col
    bsdf.inputs["Roughness"].default_value = rough
    if REAL:
        _texture(m, bsdf, col, kind or name, rough)
        if kind in ("marker", "line") and not emit:   # teaching marks glow a little so they hold against the textured floor and room
            bsdf.inputs["Emission Color"].default_value = bsdf.inputs["Base Color"].default_value if kind == "marker" else col
            bsdf.inputs["Emission Strength"].default_value = 0.6 if kind == "marker" else (0.1 if name in ("white", "pearl") else 0.3)
    if emit:
        bsdf.inputs["Emission Color"].default_value = col
        bsdf.inputs["Emission Strength"].default_value = emit
    _mats[key] = m
    return m


class _G:
    """A tiny shader-node builder: g.n(kind, {input: value or socket}, attr=value) returns the node."""

    def __init__(self, m):
        self.nt = m.node_tree
        co = self.nt.nodes.new("ShaderNodeTexCoord")
        self.obj, self.nrm = co.outputs["Object"], co.outputs["Normal"]
        self.pos = self.nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]

    def set(self, sock, v):
        if isinstance(v, bpy.types.NodeSocket):
            self.nt.links.new(v, sock)
        elif isinstance(v, (int, float)) and sock.type == "RGBA":
            sock.default_value = (v, v, v, 1.0)
        else:
            sock.default_value = v

    def n(self, kind, inp=None, **attrs):
        nd = self.nt.nodes.new(kind)
        for k, v in attrs.items():
            setattr(nd, k, v)
        for k, v in (inp or {}).items():
            self.set(nd.inputs[k], v)
        return nd

    def math(self, op, a, b=None, c=None, clamp=False):
        nd = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b, c)):
            if v is not None:
                self.set(nd.inputs[i], v)
        return nd.outputs[0]

    def rng(self, v, a, b, lo=0.0, hi=1.0):   # v from a..b mapped to lo..hi, clamped (a > b is allowed: the map is reversed)
        return self.n("ShaderNodeMapRange", {"Value": v, "From Min": a, "From Max": b, "To Min": lo, "To Max": hi}, clamp=True).outputs["Result"]

    def mix(self, a, b, fac, blend="MIX"):
        return self.n("ShaderNodeMixRGB", {"Fac": fac, "Color1": a, "Color2": b}, blend_type=blend).outputs["Color"]

    def noise(self, scale, detail=5.0, rough=0.6, vec=None):
        return self.n("ShaderNodeTexNoise", {"Vector": self.obj if vec is None else vec, "Scale": scale, "Detail": detail, "Roughness": rough}).outputs["Fac"]

    def stretch(self, sx, sy, sz):   # the object coordinates squeezed per axis: brushed metal, wood grain
        return self.n("ShaderNodeMapping", {"Vector": self.obj, "Scale": (sx, sy, sz)}).outputs["Vector"]

    def bump(self, h, strength, dist=0.02):
        return self.n("ShaderNodeBump", {"Height": h, "Strength": strength, "Distance": dist}).outputs["Normal"]

    def xyz(self, vec):
        nd = self.n("ShaderNodeSeparateXYZ", {"Vector": vec})
        return nd.outputs["X"], nd.outputs["Y"], nd.outputs["Z"]

    def stones(self, scale, vec=None):
        """Voronoi cells as pebbles: returns (stone mask 0..1, stone shade 0..1, round height 0..1)"""
        v = self.n("ShaderNodeTexVoronoi", {"Vector": self.obj if vec is None else vec, "Scale": scale, "Randomness": 1.0}, feature="F1")
        sep = self.n("ShaderNodeSeparateColor", {"Color": v.outputs["Color"]})
        pick = self.rng(sep.outputs["Red"], 0.5, 0.52)
        height = self.rng(v.outputs["Distance"], 0.2, 0.55, 1.0, 0.0)
        return self.math("MULTIPLY", pick, self.rng(v.outputs["Distance"], 0.3, 0.44, 1.0, 0.0)), sep.outputs["Green"], self.math("MULTIPLY", height, pick)


def _rgbv(hexs, k=1.0):
    return tuple(min(1.0, c * k) for c in _rgb(hexs)[:3]) + (1.0,)


def _texture(m, bsdf, col, kind, rough):
    """Texture work for the real look, all procedural (no image files). Concrete slabs with joints, oil and cracks; asphalt with
    stones; worn road paint; planked lacquered wood; brushed aluminium; black housings with edge wear; tyres with tread; plaster."""
    g = _G(m)
    link = m.node_tree.links.new
    def put(sock, v):
        g.set(bsdf.inputs[sock], v)

    if kind == "floor":
        slab = g.n("ShaderNodeTexBrick", {"Vector": g.obj, "Color1": _rgbv("#8f8c86"), "Color2": _rgbv("#605e5b"), "Mortar": _rgbv("#2a2927"), "Scale": 1.0,
                                        "Mortar Size": 0.006, "Mortar Smooth": 0.2, "Brick Width": 1.3, "Row Height": 1.3}, offset=0.0)
        joint = slab.outputs["Fac"]
        halo = g.n("ShaderNodeTexBrick", {"Vector": g.obj, "Color1": (0, 0, 0, 1), "Color2": (0, 0, 0, 1), "Mortar": (1, 1, 1, 1), "Scale": 1.0,
                                        "Mortar Size": 0.07, "Mortar Smooth": 1.0, "Brick Width": 1.3, "Row Height": 1.3}, offset=0.0).outputs["Fac"]   # grime collects along the joints
        stains = g.rng(g.noise(0.55, 5.0), 0.3, 0.7, 0.5, 1.15)
        blotch = g.rng(g.noise(4.0, 5.0, 0.7), 0.3, 0.7, 0.7, 1.12)
        grain_n = g.noise(70.0, 8.0, 0.7)
        speck = g.rng(grain_n, 0.4, 0.65, 0.7, 1.2)
        oil = g.rng(g.noise(1.1, 3.0, 0.5), 0.6, 0.67)              # dark glossy patches
        crack_d = g.n("ShaderNodeTexVoronoi", {"Vector": g.obj, "Scale": 0.75}, feature="DISTANCE_TO_EDGE").outputs["Distance"]
        crack = g.math("MULTIPLY", g.rng(crack_d, 0.0, 0.008, 1.0, 0.0), g.rng(g.noise(0.35, 2.0), 0.6, 0.66))
        c = g.mix(slab.outputs["Color"], (1, 1, 1, 1), 0.0)
        for f, blend in ((stains, "MULTIPLY"), (blotch, "MULTIPLY"), (speck, "MULTIPLY"), (g.math("SUBTRACT", 1.0, g.math("MULTIPLY", halo, 0.45)), "MULTIPLY")):
            c = g.mix(c, f, 1.0, blend)
        c = g.mix(c, _rgbv("#1a1918"), g.math("MULTIPLY", oil, 0.55))
        c = g.mix(c, _rgbv("#101010"), g.math("MULTIPLY", crack, 0.85))
        put("Base Color", c)
        r = g.rng(stains, 0.62, 1.12, 0.92, 0.55)
        r = g.mix(r, 0.32, oil)
        put("Roughness", g.math("MAXIMUM", r, g.math("MULTIPLY", joint, 1.0)))
        tile = g.math("SUBTRACT", 1.0, joint)
        put("Normal", g.bump(g.math("ADD", g.math("MULTIPLY", grain_n, 0.25), g.math("MULTIPLY", tile, 0.9)), 0.8, 0.01))
    elif kind == "road":
        stone, shade, rnd = g.stones(70.0)
        dirt = g.rng(g.noise(1.6, 5.0), 0.3, 0.7, 0.75, 1.2)
        fine = g.noise(150.0, 6.0, 0.7)
        base = g.mix(col, (1, 1, 1, 1), 0.0)
        base = g.mix(base, dirt, 1.0, "MULTIPLY")
        base = g.mix(base, g.rng(fine, 0.35, 0.65, 0.65, 1.3), 1.0, "MULTIPLY")
        stone_col = g.mix(_rgbv("#2f2e2c"), _rgbv("#615f5b"), shade)
        put("Base Color", g.mix(base, stone_col, g.math("MULTIPLY", stone, 0.8)))
        put("Roughness", g.mix(0.93, 0.62, stone))
        put("Normal", g.bump(g.math("ADD", g.math("MULTIPLY", rnd, 0.75), g.math("MULTIPLY", fine, 0.25)), 1.0, 0.006))
    elif kind == "line":      # worn road paint: grime, chips and the asphalt texture showing through
        wear = g.rng(g.noise(14.0, 6.0, 0.7), 0.42, 0.62)
        chip = g.rng(g.noise(85.0, 4.0), 0.52, 0.7)
        stone, shade, rnd = g.stones(70.0)
        c = g.mix(col, _rgbv("#5a5650"), g.math("MULTIPLY", wear, 0.6))
        c = g.mix(c, _rgbv("#3a3936"), g.math("MULTIPLY", chip, 0.7))
        put("Base Color", c)
        put("Roughness", g.mix(0.72, 0.9, wear))
        put("Normal", g.bump(g.math("ADD", g.math("MULTIPLY", rnd, 0.6), g.math("MULTIPLY", chip, 0.5)), 0.8, 0.004))
    elif kind == "wood":      # lacquered planks with grain
        planks = g.n("ShaderNodeTexBrick", {"Vector": g.obj, "Color1": _rgbv("#a97a4c"), "Color2": _rgbv("#7d5430"), "Mortar": _rgbv("#2b1a0e"), "Scale": 1.0,
                                          "Mortar Size": 0.003, "Mortar Smooth": 0.1, "Brick Width": 0.9, "Row Height": 0.115}, offset=0.37)
        grain = g.noise(3.0, 3.0, 0.5, g.stretch(1.0, 28.0, 28.0))
        c = g.mix(planks.outputs["Color"], g.rng(grain, 0.3, 0.7, 0.6, 1.25), 1.0, "MULTIPLY")
        put("Base Color", c)
        put("Roughness", g.rng(grain, 0.3, 0.7, 0.34, 0.5))
        put("Coat Roughness", 0.16)
        put("Normal", g.bump(g.math("SUBTRACT", g.math("MULTIPLY", grain, 0.05), g.math("MULTIPLY", planks.outputs["Fac"], 0.4)), 0.7, 0.004))
    elif kind in ("grey", "alu"):    # brushed aluminium: fine grain along the part, a little oxide, never a mirror
        brush = g.noise(40.0, 2.0, 0.5, g.stretch(1.0, 1.0, 70.0))
        ox = g.rng(g.noise(6.0, 3.0), 0.3, 0.7, 0.8, 1.12)
        put("Base Color", g.mix(col, ox, 1.0, "MULTIPLY"))
        put("Roughness", g.rng(brush, 0.2, 0.8, 0.34, 0.56))
        put("Normal", g.bump(brush, 0.05, 0.004))
    elif kind == "steel":
        put("Roughness", g.rng(g.noise(30.0, 2.0), 0.3, 0.7, 0.22, 0.4))
    elif kind == "motor":     # black anodised housing, bare metal showing on the edges
        edge = g.n("ShaderNodeNewGeometry").outputs["Pointiness"]      # convex edges of the bevelled mesh (no ray tracing in the shader)
        wear = g.math("MULTIPLY", g.rng(edge, 0.53, 0.62), g.rng(g.noise(14.0, 4.0), 0.3, 0.6, 0.35, 1.0))
        put("Base Color", g.mix(col, _rgbv("#9a9da1"), wear))
        put("Metallic", wear)
        put("Roughness", g.mix(g.rng(g.noise(25.0, 2.0), 0.3, 0.7, 0.36, 0.5), 0.34, wear))
    elif kind.startswith("tyre"):   # rubber with a tread of staggered blocks; the pattern turns with the wheel
        R = 0.075 if kind == "tyre75" else 0.09
        x, y, z = g.xyz(g.obj)
        ang = g.math("ARCTAN2", z, x)
        arc = g.math("MULTIPLY", ang, R)
        vec = g.n("ShaderNodeCombineXYZ", {"X": arc, "Y": y, "Z": 0.0}).outputs["Vector"]
        tread = g.n("ShaderNodeTexBrick", {"Vector": vec, "Color1": (1, 1, 1, 1), "Color2": (1, 1, 1, 1), "Mortar": (0, 0, 0, 1), "Scale": 1.0,
                                           "Mortar Size": 0.0055, "Mortar Smooth": 0.3, "Brick Width": 2 * math.pi * R / 22, "Row Height": 0.0235}, offset=0.5)
        side = g.rng(g.math("ABSOLUTE", g.xyz(g.nrm)[1]), 0.55, 0.8)          # 1 on the flat faces of the tyre
        h = g.math("MULTIPLY", g.math("SUBTRACT", 1.0, tread.outputs["Fac"]), g.math("SUBTRACT", 1.0, side))
        put("Roughness", g.mix(0.9, 0.7, side))
        put("Normal", g.bump(g.math("ADD", h, g.math("MULTIPLY", g.noise(80.0, 3.0), 0.15)), 1.0, 0.004))
    elif kind == "glass":     # dark tinted glass: nearly a mirror at a grazing angle
        put("Roughness", 0.05)
    elif kind == "wall":      # plaster over a painted dado, soft grime, a little stucco
        z = g.xyz(g.pos)[2]
        lower = g.rng(z, 1.31, 1.29)
        dado = _rgbv("#4d5256")
        c = g.mix(col, dado, lower)
        c = g.mix(c, g.rng(g.noise(0.9, 5.0), 0.3, 0.7, 0.8, 1.08), 1.0, "MULTIPLY")
        c = g.mix(c, g.rng(z, 0.0, 1.0, 0.72, 1.0), 1.0, "MULTIPLY")
        put("Base Color", c)
        put("Roughness", g.mix(0.88, 0.5, lower))
        put("Normal", g.bump(g.noise(30.0, 6.0, 0.6), 0.25, 0.004))
    else:                     # paint, plastic: fingerprints and dust change the shine a little
        smudge = g.noise(9.0, 3.0)
        put("Roughness", g.rng(smudge, 0.3, 0.7, max(0.04, rough - 0.08), min(1.0, rough + 0.14)))


def _obj(name, bm, colour, smooth=True, bevel=0.0, parent=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if REAL and isinstance(colour, str) and colour.startswith("#"):   # a colour the lesson picked itself marks something: keep it readable
        colour = mat(colour, kind="marker")
    if colour:
        me.materials.append(colour if not isinstance(colour, str) else mat(colour))
    if bevel:
        b = ob.modifiers.new("bevel", "BEVEL")
        b.width, b.segments, b.limit_method = bevel, 4, "ANGLE"
        ob.modifiers.new("normals", "WEIGHTED_NORMAL").keep_sharp = True
    if parent is not None:
        ob.parent = parent
    return ob


def _k(name, kind):
    """The palette colour `name` in the real look's `kind` of surface; just the plain name in the quick look."""
    return mat(name, kind=kind) if REAL and isinstance(name, str) else name   # a material made by the script is used as it is


def _bolts(parent, n, ring, axis, at, r=0.006, depth=0.006, kind="steel", name="bolt"):
    """A circle of n bolt heads (real look only) on a face: ring radius `ring`, face centre `at`, facing along +/- `axis`."""
    if not REAL:
        return
    for i in range(n):
        a = 2 * math.pi * i / n
        u, v = ring * math.cos(a), ring * math.sin(a)
        loc = {"y": (at[0] + u, at[1], at[2] + v), "z": (at[0] + u, at[1] + v, at[2]), "x": (at[0], at[1] + u, at[2] + v)}[axis]
        cyl(name, r, depth, loc, axis, _k("grey", kind), parent=parent, segments=6)


def box(name, size, loc=(0, 0, 0), colour="blue", bevel=0.02, parent=None):
    """A rounded block; size is the full extent (x, y, z)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    ob = _obj(name, bm, colour, bevel=min(bevel, min(size) * 0.45), parent=parent)
    ob.location = loc
    return ob


def cyl(name, radius, depth, loc=(0, 0, 0), axis="z", colour="dark", bevel=0.0, parent=None, segments=40):
    """A cylinder along x, y or z."""
    bm = bmesh.new()
    if REAL and isinstance(colour, str) and colour.startswith("#") and radius < 0.018:
        radius = 0.018   # a thin marker post must still show at 350 px
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=radius, radius2=radius, depth=depth)
    if axis == "x":
        bmesh.ops.rotate(bm, matrix=Matrix.Rotation(math.pi / 2, 3, "Y"), verts=bm.verts)
    elif axis == "y":
        bmesh.ops.rotate(bm, matrix=Matrix.Rotation(math.pi / 2, 3, "X"), verts=bm.verts)
    ob = _obj(name, bm, colour, bevel=bevel, parent=parent)
    if not bevel:
        ob.modifiers.new("normals", "WEIGHTED_NORMAL").keep_sharp = True
        e = ob.modifiers.new("edges", "EDGE_SPLIT")
        e.split_angle = math.radians(40)
    ob.location = loc
    return ob


def ball(name, radius, loc=(0, 0, 0), colour="amber", parent=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=radius)
    if REAL and colour in ("amber", "red", "green", "blue", "navy"):   # a coloured ball is a marker
        colour = mat(colour, kind="marker")
    ob = _obj(name, bm, colour, parent=parent)
    ob.location = loc
    return ob


def empty(name, loc=(0, 0, 0), parent=None):
    ob = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if parent is not None:
        ob.parent = parent
    return ob


def setup(seconds, fps=24, res=(800, 450), samples=12):   # about 1 s a frame on a laptop GPU
    """Empty scene with a bright studio: soft key light, sky fill, pale floor. Returns the scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.fps = fps
    sc.frame_start, sc.frame_end = 1, int(round(seconds * fps))
    sc.eevee.taa_render_samples = samples
    sc.view_settings.view_transform = "Standard"
    sc.eevee.use_raytracing = True   # contact shading under wheels and feet
    if REAL:
        _real_render(sc, samples)
    world = bpy.data.worlds.new("studio")
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = _rgb("#eef3f5")
    bg.inputs["Strength"].default_value = 0.55
    sc.world = world
    if REAL:   # light and reflections from a real room: one of the environment images that ship with Blender
        env = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(str(pathlib.Path(bpy.utils.resource_path("LOCAL")) / "datafiles" / "studiolights" / "world" / "interior.exr"))
        world.node_tree.links.new(env.outputs["Color"], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = 0.3
    sun = bpy.data.objects.new("key", bpy.data.lights.new("key", "SUN"))
    sun.data.energy, sun.data.angle = 2.4, math.radians(4)
    sun.rotation_euler = (math.radians(50), 0, math.radians(150))   # from behind and to the right, so shadows fall toward the camera
    if REAL:   # late-morning sun through a window: warm, strong, with a crisp shadow
        sun.data.energy, sun.data.angle, sun.data.color = 5.5, math.radians(2.5), (1.0, 0.95, 0.86)
    sc.collection.objects.link(sun)
    fill = bpy.data.objects.new("fill", bpy.data.lights.new("fill", "AREA"))
    fill.data.energy, fill.data.size = (45 if REAL else 90), 6
    fill.location, fill.rotation_euler = (-3, -4, 4), (math.radians(55), 0, math.radians(-35))
    sc.collection.objects.link(fill)
    floor = box("floor", (60, 60, 0.02), (0, 0, -0.01), mat("floor", rough=0.9), bevel=0)
    return sc


def _real_render(sc, samples):
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = kind
            prefs.get_devices()
            for d in prefs.devices:
                d.use = d.type == kind
            sc.cycles.device = "GPU"
            break
        except TypeError:
            continue
    sc.cycles.samples = max(48, samples * 4)
    sc.cycles.max_bounces, sc.cycles.diffuse_bounces, sc.cycles.glossy_bounces = 6, 3, 4   # a small set needs no more; this is a quarter of the cost
    sc.cycles.transmission_bounces, sc.cycles.transparent_max_bounces, sc.cycles.volume_bounces = 3, 6, 0
    sc.cycles.sample_clamp_indirect = 8.0                                                  # stops fireflies from the bright windows
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPTIX"          # on the GPU: the default CPU denoiser took 5 s of every 6 s frame
    except TypeError:
        pass
    sc.render.use_persistent_data = True       # keep the scene on the GPU between frames
    sc.render.use_motion_blur = True          # a moving car or arm smears a little, as it does on a real camera
    sc.render.motion_blur_shutter = 0.35
    sc.view_settings.view_transform = "AgX"
    looks = [i.identifier for i in type(sc.view_settings).bl_rna.properties["look"].enum_items]
    sc.view_settings.look = next((name for name in looks if "Medium High Contrast" in name), sc.view_settings.look)
    sc.view_settings.exposure = -0.3


def camera(pos, target, lens=50):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens = lens
    if REAL:   # a real lens: the subject is sharp, the room behind it is soft
        cam.data.dof.use_dof = True
        cam.data.dof.focus_distance = (Vector(target) - Vector(pos)).length
        cam.data.dof.aperture_fstop = 2.8
    cam.location = pos
    cam.rotation_euler = (Vector(target) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


def key(ob, frame, loc=None, rot=None):
    """Keyframe location and/or rotation (Euler XYZ, radians) at a frame."""
    if loc is not None:
        ob.location = loc
        ob.keyframe_insert("location", frame=frame)
    if rot is not None:
        ob.rotation_euler = rot
        ob.keyframe_insert("rotation_euler", frame=frame)


def car(name, colour="blue", scale=1.0):
    """A toy car about 0.6 long, nose toward +x. Move the returned root; `wheels` spin about y, `brake` lamps."""
    root = empty(name)
    box(name + "-body", (0.6, 0.3, 0.13), (0, 0, 0.155), colour, bevel=0.045, parent=root)
    box(name + "-cabin", (0.3, 0.25, 0.13), (-0.05, 0, 0.28), "pearl", bevel=0.045, parent=root)
    box(name + "-glass", (0.306, 0.256, 0.055), (-0.05, 0, 0.285), _k("dark", "glass"), bevel=0.012, parent=root)   # a band of windows
    wheels = []
    for x in (0.19, -0.19):
        for y in (0.155, -0.155):
            w = cyl(name + "-wheel", 0.09, 0.07, (x, y, 0.09), "y", _k("dark", "tyre"), bevel=0.015, parent=root)
            if REAL:   # steel rim with five bolts
                cyl(name + "-hub", 0.052, 0.073, (0, 0, 0), "y", _k("grey", "steel"), parent=w)
                cyl(name + "-cap", 0.016, 0.077, (0, 0, 0), "y", "dark", parent=w)
                for s_ in (1, -1):
                    _bolts(w, 5, 0.033, "y", (0, s_ * 0.037, 0), r=0.0045, depth=0.004)
            else:
                cyl(name + "-hub", 0.045, 0.075, (0, 0, 0), "y", "pearl", parent=w)
                box(name + "-spoke", (0.02, 0.078, 0.07), (0, 0, 0), "grey", bevel=0, parent=w)
            wheels.append(w)
    if REAL:   # bumpers, door seams, handles, lamp bezels
        for x in (0.3, -0.3):
            box(name + "-bumper", (0.016, 0.27, 0.022), (x, 0, 0.1), _k("grey", "steel"), bevel=0.007, parent=root)
        for y in (0.1508, -0.1508):
            for sx in (0.02, -0.17):
                box(name + "-seam", (0.0025, 0.002, 0.105), (sx, y, 0.165), "dark", bevel=0, parent=root)
            box(name + "-handle", (0.03, 0.008, 0.008), (0.045, y * 1.02, 0.19), _k("grey", "steel"), bevel=0.003, parent=root)
        for y in (0.09, -0.09):
            cyl(name + "-bezel", 0.036, 0.012, (0.288, y, 0.165), "x", _k("grey", "steel"), parent=root)
    for y in (0.09, -0.09):
        ball(name + "-lamp", 0.028, (0.3, y, 0.165), mat("white", emit=1.5), parent=root)
    brake = [ball(name + "-brake", 0.026, (-0.3, y, 0.165), mat("red", emit=0.2), parent=root) for y in (0.09, -0.09)]
    root.scale = (scale,) * 3
    return root, wheels, brake


def drive(root, wheels, frame, x, y=0.0, yaw=0.0, radius=0.09):
    """Key a car at (x, y) and roll its wheels by the distance x."""
    key(root, frame, loc=(x, y, 0), rot=(0, 0, yaw))
    for w in wheels:
        key(w, frame, rot=(0, x / radius, 0))


def arm(name, lengths=(0.4, 0.4), colour="blue", base_height=0.3):
    """A bench arm that moves in the x-z plane: pedestal, one motor per joint, round links, a two-finger gripper.
    Returns (root, joints); set joints[i].rotation_euler.y = -q[i] (q counter-clockwise from +x, relative to the link before)."""
    root = empty(name)
    cyl(name + "-foot", 0.11, 0.03, (0, 0, 0.015), "z", _k("dark", "motor"), bevel=0.01, parent=root)
    _bolts(root, 6, 0.088, "z", (0, 0, 0.032), r=0.01, depth=0.008)
    cyl(name + "-post", 0.06, base_height, (0, 0, base_height / 2), "z", "grey", parent=root)
    if REAL:
        cyl(name + "-flange", 0.075, 0.012, (0, 0, 0.036), "z", _k("grey", "steel"), bevel=0.003, parent=root)
    joints, parent, at = [], root, (0, 0, base_height)
    for i, L in enumerate(lengths):
        j = empty(f"{name}-j{i}", at, parent)
        r = 0.075 - 0.012 * i
        cyl(f"{name}-motor{i}", r, r * 1.7, (0, 0, 0), "y", _k("dark", "motor"), bevel=0.012, parent=j)
        cyl(f"{name}-cap{i}", r * 0.55, r * 1.74, (0, 0, 0), "y", "amber", parent=j)
        for s_ in (1, -1):
            _bolts(j, 6, r * 0.78, "y", (0, s_ * r * 0.85, 0), r=0.0055, depth=0.005)
        cyl(f"{name}-link{i}", 0.036 - 0.006 * i, L, (L / 2, 0, 0), "x", colour if i == 0 else _k("sky", "alu"), bevel=0.01, parent=j)
        joints.append(j)
        parent, at = j, (L, 0, 0)
    hand = empty(name + "-hand", at, parent)
    box(name + "-palm", (0.03, 0.1, 0.13), (0.015, 0, 0), _k("dark", "motor"), bevel=0.01, parent=hand)
    for z in (0.045, -0.045):
        box(name + "-finger", (0.11, 0.05, 0.02), (0.085, 0, z), "grey", bevel=0.008, parent=hand)
    return root, joints


def pose(joints, frame, q):
    """Key an arm's joint angles (radians, counter-clockwise from +x, each relative to the link before)."""
    for j, a in zip(joints, q):
        key(j, frame, rot=(0, -float(a), 0))


def rover(name, colour="blue"):
    """A two-wheel mobile robot about 0.4 across, front toward +x, with a sensor puck on top. Returns (root, wheels)."""
    root = empty(name)
    cyl(name + "-body", 0.19, 0.1, (0, 0, 0.11), "z", colour, bevel=0.02, parent=root)
    cyl(name + "-puck", 0.065, 0.05, (0, 0, 0.185), "z", _k("dark", "motor"), bevel=0.008, parent=root)
    box(name + "-front", (0.05, 0.12, 0.03), (0.17, 0, 0.13), "amber", bevel=0.01, parent=root)
    wheels = [cyl(name + "-wheel", 0.075, 0.04, (0, y, 0.075), "y", _k("dark", "tyre75"), bevel=0.01, parent=root) for y in (0.2, -0.2)]
    for w in wheels:
        if REAL:
            cyl(name + "-hub", 0.042, 0.043, (0, 0, 0), "y", _k("grey", "steel"), parent=w)
            for s_ in (1, -1):
                _bolts(w, 5, 0.026, "y", (0, s_ * 0.0215, 0), r=0.004, depth=0.004)
        else:
            box(name + "-spoke", (0.02, 0.045, 0.1), (0, 0, 0), "grey", bevel=0, parent=w)
    ball(name + "-caster", 0.03, (-0.14, 0, 0.03), "grey", parent=root)
    return root, wheels


def drone(name, colour="blue", arm_len=0.22):
    """A quadrotor about 0.5 across. Returns (root, props); spin a prop with key(prop, frame, rot=(0, 0, angle))."""
    root = empty(name)
    box(name + "-body", (0.16, 0.16, 0.06), (0, 0, 0), colour, bevel=0.025, parent=root)
    props = []
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        x, y = sx * arm_len * 0.71, sy * arm_len * 0.71
        bar = box(name + "-arm", (arm_len, 0.025, 0.02), (x / 2, y / 2, 0), _k("dark", "motor"), bevel=0.006, parent=root)
        bar.rotation_euler = (0, 0, math.atan2(y, x))
        cyl(name + "-motor", 0.028, 0.05, (x, y, 0.02), "z", "grey", parent=root)
        prop = empty(name + "-prop", (x, y, 0.052), root)
        box(name + "-blade", (0.2, 0.024, 0.006), (0, 0, 0), "amber" if i < 2 else "pearl", bevel=0.002, parent=prop)
        props.append(prop)
    return root, props


def arrow(name, colour="red", shaft=0.018):
    """A unit arrow along +x from the origin. Scale x for its length: ob.scale = (length, 1, 1); rotate to aim it."""
    root = empty(name)
    colour = _k(colour, "marker")
    shaft = max(shaft, 0.026) if REAL else shaft   # a real-look arrow must still read at 350 px
    cyl(name + "-shaft", shaft, 0.8, (0.4, 0, 0), "x", colour, parent=root, segments=16)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=20, radius1=shaft * 2.6, radius2=0, depth=0.2)
    bmesh.ops.rotate(bm, matrix=Matrix.Rotation(math.pi / 2, 3, "Y"), verts=bm.verts)
    _obj(name + "-head", bm, colour, parent=root).location = (0.9, 0, 0)
    return root


def tube(name, points, radius=0.012, colour="blue"):
    """A round line through 3D points: a path, a trail, a cable."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", radius * (1.4 if REAL and radius < 0.03 else 1.0), 3
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for p, xyz in zip(sp.points, points):
        p.co = (*xyz, 1.0)
    ob = bpy.data.objects.new(name, cu)
    cu.materials.append(mat(colour, kind="marker") if REAL else mat(colour))
    bpy.context.scene.collection.objects.link(ob)
    return ob


def ghost(colour="grey", alpha=0.3):
    """A see-through material for a target pose or a remembered position."""
    m = bpy.data.materials.new("ghost-" + colour)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = _rgb(PAL.get(colour, colour))
    if REAL:   # more opaque and a little self-lit, so a target or a remembered pose does not melt into the room
        alpha = alpha + (1 - alpha) * 0.25
        bsdf.inputs["Emission Color"].default_value = bsdf.inputs["Base Color"].default_value
        bsdf.inputs["Emission Strength"].default_value = 0.5
    bsdf.inputs["Alpha"].default_value = alpha
    m.surface_render_method = "BLENDED"
    return m


def table(size=(1.2, 0.7), height=0.4, loc=(0, 0)):
    """A work table whose top surface is at z = height. Stand an arm on it with root.location = (x, y, height)."""
    top = box("table-top", (size[0], size[1], 0.04), (loc[0], loc[1], height - 0.02), "wood" if REAL else "pearl", bevel=0.012)
    for sx in (1, -1):
        for sy in (1, -1):
            box("table-leg", (0.05, 0.05, height - 0.04), (loc[0] + sx * (size[0] / 2 - 0.06), loc[1] + sy * (size[1] / 2 - 0.06), (height - 0.04) / 2), "grey", bevel=0.008)
    return top


def crate(name, size=0.12, loc=(0, 0, 0), colour="amber"):
    """A small block to pick up, push or weigh; loc is its centre."""
    return box(name, (size, size, size), loc, colour, bevel=size * 0.12)


def stripe(x0, x1, y0, y1, colour="white", z=0.002):
    """A flat painted mark on the floor (a lane, a stop line)."""
    paint = mat(colour, rough=0.8, kind="line") if REAL and colour not in ("road", "floor") else mat(colour, rough=0.8)
    return box("stripe", (x1 - x0, y1 - y0, 0.004), ((x0 + x1) / 2, (y0 + y1) / 2, z), paint, bevel=0)


def _dress_set():
    """Real look only, called by render() once the clip has built everything: a workshop around the action. The walls go where the
    camera can just see their foot, with shelves, a bench with drawers, crates and windows against them; the lens aperture is chosen
    so that this background is a soft blur and the subject stays sharp."""
    import random
    rnd = random.Random(11)
    sc = bpy.context.scene
    cam = sc.camera
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for f in sorted({sc.frame_start, (sc.frame_start + sc.frame_end) // 2, sc.frame_end}):
        sc.frame_set(f)
        for ob in sc.objects:
            if ob.type not in ("MESH", "CURVE") or ob.name == "floor" or max(ob.dimensions) > 20:
                continue
            for c in ob.bound_box:
                w = ob.matrix_world @ Vector(c)
                lo = Vector(map(min, lo, w))
                hi = Vector(map(max, hi, w))
    sc.frame_set(sc.frame_start)
    cpos = cam.matrix_world.translation
    up = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
    ax = 0 if abs(up.x) > abs(up.y) else 1          # the wall the camera looks toward is perpendicular to this world axis
    sg = 1.0 if up[ax] > 0 else -1.0
    lt = 1 - ax
    width = sc.render.resolution_x
    sens_w = cam.data.sensor_width
    vfov = 2 * math.atan((sens_w * sc.render.resolution_y / width / 2) / cam.data.lens)
    hfov = 2 * math.atan(sens_w / 2 / cam.data.lens)
    # where the top edge of the picture meets the floor, measured along the wall axis
    top = (cam.matrix_world.to_3x3() @ Vector((0, math.tan(vfov / 2) * 0.55, -1))).normalized()   # a ray a quarter of the way down
    reach = (-cpos.z / top.z * top[ax] * sg) if top.z < -0.02 else None
    far = max(hi[ax] * sg, lo[ax] * sg) + 1.1                    # the wall stays this far behind the action
    here = cpos[ax] * sg
    if reach is None:
        W = far + 3.0
    else:
        W = min(far + 3.5, max(far, here + reach))
    foot = W                                                     # wall face, as a coordinate along sg
    lat_c = (lo[lt] + hi[lt]) / 2
    half = min(12.0, max(5.5, math.tan(hfov / 2) * max(foot - here, 2.0) * 1.3 + 2.0, (hi[lt] - lo[lt]) / 2 + 4.0))

    # lens: blur disc of about 8 px at the wall, but no more than 2 px on the front and back of the action
    S1 = cam.data.dof.focus_distance
    f_ = cam.data.lens / 1000.0
    dist_wall = max(S1 + 0.5, (foot - here) / max(abs(fwd[ax]) + 0.35, 0.35))
    px_per_m = width / (sens_w / 1000.0)
    n_wall = f_ * f_ / (8.0 / px_per_m) / (S1 - f_) * (dist_wall - S1) / dist_wall
    depth = max(0.3, abs(hi[ax] - lo[ax]) / 2)
    n_sub = f_ * f_ / (2.0 / px_per_m) / (S1 - f_) * depth / S1
    cam.data.dof.aperture_fstop = min(2.8, max(0.5, n_wall, n_sub))
    print("SET axis", ax, sg, "wall", round(foot, 2), "action far", round(far - 1.1, 2), "reach", reach and round(reach, 2), "f/", round(cam.data.dof.aperture_fstop, 2), "n_wall", round(n_wall, 2), "n_sub", round(n_sub, 2))

    def world(lat, deep, z):       # lat: along the wall, deep: out from the wall face toward the room
        p = [0.0, 0.0, z]
        p[ax] = (foot - deep) * sg
        p[lt] = lat_c + lat
        return tuple(p)

    def piece(name, size, lat, deep, z0, colour, bevel=0.01):
        """size = (along the wall, out from the wall, height); (lat, deep) the centre; z0 the bottom"""
        w, d, h = size
        ob = box(name, (w, d, h), world(lat, deep, z0 + h / 2), colour, bevel=bevel)
        ob.rotation_euler.z = 0.0 if ax == 1 else math.pi / 2
        ob.visible_shadow = False
        return ob

    plaster = mat("#d9d5cb", kind="wall")
    # four walls: the back one and the sides are built to the same limits, the one behind the camera is for reflections only
    piece("wall-back", (2 * half + 1, 0.4, 8.0), 0, -0.2, 0.0, plaster, bevel=0)
    for sd in (-1, 1):
        ob = box("wall-side", (0.4, foot - here + 5.0, 8.0), (0, 0, 4.0), plaster, bevel=0)
        pos = [0.0, 0.0, 4.0]
        pos[lt] = lat_c + sd * (half + 0.2)
        pos[ax] = (here - 5.0 + (foot - here + 5.0) / 2) * sg
        ob.location = pos
        if ax == 0:
            ob.rotation_euler.z = math.pi / 2
        ob.visible_shadow = False
    ob = box("wall-front", (2 * half + 1, 0.4, 8.0), (0, 0, 4.0), plaster, bevel=0)
    pos = [0.0, 0.0, 4.0]
    pos[lt], pos[ax] = lat_c, (here - 4.5) * sg
    ob.location = pos
    ob.rotation_euler.z = 0.0 if ax == 1 else math.pi / 2
    ob.visible_shadow = False
    base = mat("#262b30", kind="enamel")
    piece("baseboard", (2 * half, 0.04, 0.14), 0, 0.02, 0.0, base, bevel=0.005)
    piece("rail", (2 * half, 0.05, 0.05), 0, 0.025, 1.3, mat("#c8c4ba", kind="matte"), bevel=0.01)

    # windows high on the wall: light and soft bright shapes
    glow = bpy.data.materials.new("window")
    glow.use_nodes = True
    nt = glow.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    em, out = nt.nodes.new("ShaderNodeEmission"), nt.nodes.new("ShaderNodeOutputMaterial")
    em.inputs["Color"].default_value, em.inputs["Strength"].default_value = (1.0, 0.93, 0.8, 1.0), 14.0
    nt.links.new(em.outputs[0], out.inputs[0])
    frame_m = mat("#2a2d30", kind="enamel")
    wlat = -half + 2.0
    while wlat < half - 2.0:
        ww = rnd.choice((1.8, 2.4, 3.0))
        piece("window", (ww, 0.02, 1.5), wlat + ww / 2, 0.015, 1.95, glow, bevel=0)
        for k in range(1, int(ww / 0.6)):
            piece("mullion", (0.045, 0.04, 1.54), wlat + k * 0.6, 0.03, 1.93, frame_m, bevel=0.004)
        piece("transom", (ww, 0.04, 0.05), wlat + ww / 2, 0.03, 2.7, frame_m, bevel=0.004)
        wlat += ww + rnd.choice((1.2, 2.0, 3.2))

    # furniture along the wall
    cardboard = [mat(c, kind="matte") for c in ("#8e8a83", "#7a766f", "#a09b93", "#6e6b66")]   # neutral, so nothing behind shares the palette's hues
    grey_bin = [mat(c, kind="enamel") for c in ("#585a5c", "#3d3f41", "#7b7d7f", "#5f6163", "#c9c7c2")]
    steel = mat("grey", kind="alu")
    lat = -half + 0.5
    while lat < half - 0.8:
        kind_ = rnd.choice(("rack", "rack", "bench", "bench", "gap", "crates"))
        w = rnd.choice((1.6, 2.0, 2.4))
        c = lat + w / 2
        if kind_ == "rack":
            for sx in (-w / 2 + 0.03, w / 2 - 0.03):
                piece("post", (0.05, 0.05, 2.5), c + sx, 0.45, 0.0, steel, bevel=0.005)
            for z0 in (0.12, 0.85, 1.55, 2.2):
                piece("shelf", (w, 0.5, 0.04), c, 0.27, z0, base, bevel=0.004)
                x = c - w / 2 + 0.1
                while x < c + w / 2 - 0.3:
                    bw, bh, bd = rnd.uniform(0.25, 0.55), rnd.uniform(0.2, 0.55), rnd.uniform(0.3, 0.45)
                    if x + bw > c + w / 2 - 0.05:
                        break
                    if rnd.random() < 0.85:
                        piece("carton", (bw, bd, bh), x + bw / 2, 0.28, z0 + 0.04, rnd.choice(cardboard + grey_bin), bevel=0.012)
                    x += bw + rnd.uniform(0.03, 0.2)
        elif kind_ == "bench":
            piece("bench-top", (w, 0.75, 0.05), c, 0.4, 0.9, mat("#7c776f", kind="matte"), bevel=0.01)
            piece("bench-body", (w - 0.05, 0.62, 0.86), c, 0.38, 0.02, mat(rnd.choice(("#5d6063", "#636460", "#535658", "#5f6366")), kind="enamel"), bevel=0.006)
            n = int(w / 0.5)
            for i in range(n):
                for r in range(3):
                    piece("drawer", (w / n - 0.012, 0.02, 0.26), c - w / 2 + (i + 0.5) * w / n, 0.7, 0.05 + r * 0.285, mat("#6c6f72", kind="enamel"), bevel=0.006)
                    piece("handle", (0.14, 0.03, 0.015), c - w / 2 + (i + 0.5) * w / n, 0.72, 0.28 + r * 0.285, steel, bevel=0.004)
            x = c - w / 2 + 0.15
            while x < c + w / 2 - 0.4:
                bw = rnd.uniform(0.15, 0.4)
                bh = rnd.uniform(0.1, 0.4)
                piece("box", (bw, rnd.uniform(0.2, 0.4), bh), x + bw / 2, 0.35, 0.95, rnd.choice(cardboard + grey_bin), bevel=0.01)
                x += bw + rnd.uniform(0.1, 0.5)
        elif kind_ == "crates":
            for i in range(rnd.randint(2, 4)):
                cs = rnd.uniform(0.4, 0.7)
                lx = c + rnd.uniform(-w / 2 + cs / 2, w / 2 - cs / 2)
                for h in range(rnd.randint(1, 3)):
                    piece("crate", (cs, cs, cs * 0.75), lx + rnd.uniform(-0.04, 0.04), 0.5 + cs / 2, h * cs * 0.75, rnd.choice(cardboard + grey_bin[:3]), bevel=0.015)
        lat += w + rnd.choice((0.0, 0.3, 0.8))

    # a second, softer light from above: a big softbox over the action
    soft = bpy.data.objects.new("softbox", bpy.data.lights.new("softbox", "AREA"))
    soft.data.energy, soft.data.size, soft.data.color = 90, 5.0, (1.0, 0.96, 0.9)
    soft.location = ((lo.x + hi.x) / 2 - sg * 0.8 * (1 - ax), (lo.y + hi.y) / 2 - sg * 0.8 * ax, 5.5)
    sc.collection.objects.link(soft)


def render(clip_file, width=640, crf=30):
    """Render every frame, then write assets/<script name>.mp4 (H.264, no audio) and .jpg (poster) next to the lesson:
    code/clip.py makes clip.mp4, code/clip-example.py makes clip-example.mp4."""
    out = pathlib.Path(clip_file).resolve().parents[1] / "assets"
    name = pathlib.Path(clip_file).stem
    tmp = pathlib.Path(os.environ.get("CLIP_TMP") or tempfile.gettempdir()) / f"{name}-{out.parent.name}"
    tmp.mkdir(parents=True, exist_ok=True)
    sc = bpy.context.scene
    if REAL:
        _dress_set()
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = str(tmp / "f")
    if os.environ.get("CLIP_STILL"):   # one frame for a quick look: CLIP_STILL=<frame>
        sc.frame_set(int(os.environ["CLIP_STILL"]))
        sc.render.filepath = str(tmp / "still.png")
        bpy.ops.render.render(write_still=True)
        print("STILL", tmp / "still.png")
        return
    bpy.ops.render.render(animation=True)
    ff = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(sc.render.fps), "-i", str(tmp / "f%04d.png")]
    film = ",vignette=PI/7,noise=alls=5:allf=t" if REAL else ""   # the real look ends with a soft lens vignette and film grain
    subprocess.run(ff + ["-vf", f"scale={width}:-2:flags=lanczos{film}", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p",
                         "-movflags", "+faststart", "-an", str(out / f"{name}.mp4")], check=True)
    poster = int(os.environ.get("CLIP_POSTER", sc.frame_end * 2 // 3))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp / f"f{poster:04d}.png"), "-vf", f"scale={width}:-2:flags=lanczos", "-q:v", "4", str(out / f"{name}.jpg")], check=True)
    for f in tmp.glob("f*.png"):
        f.unlink()
    print("CLIP", out / f"{name}.mp4", (out / f"{name}.mp4").stat().st_size)
