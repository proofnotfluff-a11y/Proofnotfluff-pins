"""3D look test (Todd, live chat, Nov 9, 2026, 10:38 pm: "Go"): the turned-down-8k story as a Blender film built in code.

Everything is a function of film seconds, like the 2D studio: `apply(t)` places every object, light and camera for
time t, so any frame range renders on its own (many machines can each take a slice).

  python3 film.py --res 1080 --spp 32 --start 0 --end 731 --out /tmp/frames      full quality, frames f0000.png ...
  python3 film.py --res 270 --spp 6 --step 12 --out /tmp/prev --jpg              a quick preview sheet's frames

Needs `pip install bpy` (Blender as a Python module, free). No GPU: Cycles on the CPU.
"""
import argparse, math, os, sys, time
import bpy, bmesh
from mathutils import Vector

FPS = 24
DUR = 30.5
HERE = os.path.dirname(os.path.abspath(__file__))
X0 = 40.0     # the street set sits 40 m to the right of the desk set
DZ = 0.75     # desk top height

S = None
SETS = {"int": [], "ext": []}
A = {}        # named things apply() moves


# ---------- small helpers ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp(x); return x * x
def back_out(x, s=1.9): x = clamp(x) - 1; return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, u): return a + (b - a) * u
def lerp3(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))
def rad(d): return math.radians(d)


def link(o, which, parent=None):
    S.collection.objects.link(o)
    if parent is not None: o.parent = parent
    if which: SETS[which].append(o)
    return o


def mat(name, color, rough=0.5, metal=0.0, emit=None, estr=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = estr
    return m


def bsdf(m): return m.node_tree.nodes["Principled BSDF"]


def tex_mat(name, kind, c1, c2, rough=0.6, scale=4.0, bump=0.08):
    """A material with a little procedural texture; falls back to flat colour if a node name changed."""
    m = mat(name, c1, rough)
    try:
        nt = m.node_tree; b = bsdf(m)
        tc = nt.nodes.new("ShaderNodeTexCoord"); ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
        if kind == "wood":
            tx = nt.nodes.new("ShaderNodeTexWave"); tx.wave_type = "BANDS"; tx.bands_direction = "Y"
            tx.inputs["Scale"].default_value = scale; tx.inputs["Distortion"].default_value = 4.0
            tx.inputs["Detail"].default_value = 4.0; tx.inputs["Detail Scale"].default_value = 1.6
            fac = tx.outputs["Fac"]
        elif kind == "brick":
            tx = nt.nodes.new("ShaderNodeTexBrick"); tx.inputs["Scale"].default_value = scale
            tx.inputs["Mortar Size"].default_value = 0.012; tx.inputs["Brick Width"].default_value = 0.55
            tx.inputs["Row Height"].default_value = 0.26
            tx.inputs["Color1"].default_value = (*c1, 1); tx.inputs["Color2"].default_value = (*c2, 1)
            tx.inputs["Mortar"].default_value = (c1[0] * 0.4, c1[1] * 0.4, c1[2] * 0.4, 1)
            nt.links.new(tc.outputs["Object"], tx.inputs["Vector"])
            nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
            bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
            nt.links.new(tx.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
            return m
        else:
            tx = nt.nodes.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = scale
            tx.inputs["Detail"].default_value = 6.0
            fac = tx.outputs["Fac"]
        nt.links.new(tc.outputs["Object"], tx.inputs["Vector"])
        nt.links.new(fac, ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        nt.links.new(fac, bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    except Exception as e:
        print("tex_mat fallback", name, e)
    return m


def mesh_obj(name, bm, m, which, loc=(0, 0, 0), rot=(0, 0, 0), smooth_=False, bevel=0.0, parent=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth_:
        for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot
    if m: me.materials.append(m)
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 3; md.limit_method = "ANGLE"
    return link(o, which, parent)


def box(name, size, loc, m, which, rot=(0, 0, 0), bevel=0.004, parent=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    return mesh_obj(name, bm, m, which, loc, rot, False, bevel, parent)


def cyl(name, r, h, loc, m, which, rot=(0, 0, 0), v=40, r2=None, parent=None, bevel=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=v, radius1=r, radius2=r if r2 is None else r2, depth=h)
    return mesh_obj(name, bm, m, which, loc, rot, True, min(r, h) * 0.1 if bevel is None else bevel, parent)


def ball(name, r, loc, m, which, scale=(1, 1, 1), flat=False, sub=2, parent=None):
    bm = bmesh.new()
    if flat: bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    else: bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=r)
    o = mesh_obj(name, bm, m, which, loc, (0, 0, 0), not flat, 0.0, parent); o.scale = scale
    return o


def dome(name, r, loc, m, which, scale=(1, 1, 1), thick=0.004, parent=None):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=r)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context="VERTS")
    o = mesh_obj(name, bm, m, which, loc, (0, 0, 0), True, 0.0, parent); o.scale = scale
    if thick: o.modifiers.new("s", "SOLIDIFY").thickness = thick
    return o


def empty(name, loc, which, parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, None); o.location = loc; o.rotation_euler = rot
    return link(o, which, parent)


FONTS = {}
def font(kind):
    if kind not in FONTS:
        p = os.path.join(HERE, "fonts", {"bold": "Poppins-Bold.ttf", "semi": "Poppins-Medium.ttf"}[kind])
        FONTS[kind] = bpy.data.fonts.load(p) if os.path.exists(p) else None
    return FONTS[kind]


def text(body, size, loc, m, which, rot=(0, 0, 0), kind="bold", align="CENTER", parent=None, extrude=0.0, spacing=1.0):
    cu = bpy.data.curves.new("t", "FONT"); cu.body = body; cu.size = size; cu.align_x = align; cu.align_y = "CENTER"
    cu.extrude = extrude; cu.space_line = spacing
    f = font(kind)
    if f: cu.font = f
    cu.materials.append(m)
    o = bpy.data.objects.new("t", cu); o.location = loc; o.rotation_euler = rot
    return link(o, which, parent)


def light(kind, name, loc, energy, color, which=None, size=0.1, rot=(0, 0, 0), spot=None):
    d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = color
    if kind == "AREA": d.size = size
    if kind in ("POINT", "SPOT"): d.shadow_soft_size = size
    if kind == "SPOT" and spot: d.spot_size = rad(spot); d.spot_blend = 0.5
    if kind == "SUN": d.angle = rad(size)
    o = bpy.data.objects.new(name, d); o.location = loc; o.rotation_euler = rot
    return link(o, which)


def aim(o, direction):
    o.rotation_euler = Vector(direction).normalized().to_track_quat("-Z", "Y").to_euler()


def show(o, on):
    if o.hide_render == on: o.hide_render = not on
    if o.hide_viewport == on: o.hide_viewport = not on


def show_tree(o, on):
    show(o, on)
    for c in o.children_recursive: show(c, on)


# ---------- the desk set ----------
def build_desk():
    I = "int"
    wood = tex_mat("wood", "wood", (0.22, 0.115, 0.05), (0.30, 0.165, 0.075), 0.42, 5.0, 0.04)
    wallm = tex_mat("wall", "noise", (0.60, 0.55, 0.47), (0.66, 0.60, 0.52), 0.92, 14.0, 0.02)
    paper = mat("paper", (0.92, 0.90, 0.85), 0.75); ink = mat("ink", (0.035, 0.035, 0.05), 0.6)
    grayink = mat("grayink", (0.55, 0.55, 0.57), 0.7)
    brass = mat("brass", (0.83, 0.58, 0.22), 0.25, 1.0); cream = mat("cream", (0.86, 0.83, 0.75), 0.55)
    dark = mat("dark", (0.03, 0.03, 0.035), 0.4); yellow = mat("yellow", (0.92, 0.62, 0.02), 0.35)
    red = mat("red", (0.62, 0.04, 0.03), 0.5); whitep = mat("whitep", (0.95, 0.95, 0.93), 0.6)
    sticky = mat("sticky", (0.98, 0.83, 0.22), 0.7); redink = mat("redink", (0.72, 0.03, 0.03), 0.55)
    kraft = mat("kraft", (0.58, 0.40, 0.22), 0.8); bluep = mat("bluep", (0.74, 0.83, 0.92), 0.75)
    greenp = mat("greenp", (0.78, 0.90, 0.78), 0.75); greenink = mat("greenink", (0.015, 0.13, 0.07), 0.6)
    shingle = tex_mat("shingle_s", "brick", (0.10, 0.10, 0.11), (0.16, 0.15, 0.15), 0.85, 22.0, 0.5)
    black = mat("black", (0, 0, 0), 1.0)

    box("desk", (1.9, 0.86, 0.05), (0, 0, DZ - 0.025), wood, I, bevel=0.006)
    box("deskfront", (1.9, 0.03, 0.5), (0, -0.4, DZ - 0.3), mat("deskside", (0.13, 0.07, 0.035), 0.5), I, bevel=0.004)
    box("wall", (6, 0.05, 3.4), (0, 0.455, 1.7), wallm, I, bevel=0)
    box("floor", (6, 6, 0.02), (0, -2, 0), mat("floor", (0.09, 0.065, 0.05), 0.7), I, bevel=0)
    # the window: a wall the camera never sees, with an opening the low sun comes through
    gx = -1.35
    for nm, sz, lc in (("g_lo", (0.03, 7, 1.12), (gx, 0, 0.56)), ("g_hi", (0.03, 7, 3.0), (gx, 0, 3.72)),
                       ("g_f", (0.03, 2.4, 1.1), (gx, -2.32, 1.67)), ("g_b", (0.03, 3.0, 1.1), (gx, 1.82, 1.67)),
                       ("g_m1", (0.03, 0.045, 1.1), (gx, -0.66, 1.67)), ("g_m2", (0.03, 0.045, 1.1), (gx, -0.2, 1.67)),
                       ("g_mh", (0.03, 1.5, 0.045), (gx, -0.4, 1.66))):
        box(nm, sz, lc, black, I, bevel=0).visible_camera = False

    # the estimate
    est = box("estimate", (0.21, 0.297, 0.0008), (0.0, -0.03, DZ + 0.0006), paper, I, rot=(0, 0, rad(3)), bevel=0)
    z = 0.00045
    text("ESTIMATE", 0.021, (-0.088, 0.118, z), ink, None, align="LEFT", parent=est)
    text("ROOF JOB", 0.0105, (-0.088, 0.096, z), grayink, None, kind="semi", align="LEFT", parent=est)
    for i, wd in enumerate((0.17, 0.15, 0.165, 0.12, 0.155)):
        box("line", (wd, 0.0035, 0.0002), (-0.088 + wd / 2, 0.066 - i * 0.021, z), grayink, None, bevel=0, parent=est)
    box("rule", (0.176, 0.0012, 0.0002), (0, -0.062, z), ink, None, bevel=0, parent=est)
    text("TOTAL", 0.012, (-0.088, -0.098, z), ink, None, kind="semi", align="LEFT", parent=est)
    text("$8,000", 0.04, (0.09, -0.1, z), ink, None, align="RIGHT", parent=est)

    # the sticky note with the ask, and the stamp mark that lands on it
    st = box("sticky", (0.078, 0.078, 0.0006), (0.05, -0.012, DZ + 0.0019), sticky, I, rot=(0, 0, rad(-7)), bevel=0)
    text("$200 off?", 0.0155, (0, 0.02, 0.00035), ink, None, parent=st)
    no = empty("no", (0.004, -0.014, 0.0004), None, parent=st, rot=(0, 0, rad(-11)))
    text("NO", 0.027, (0, 0, 0), redink, None, parent=no)
    for sz, lc in (((0.062, 0.003, 0.0001), (0, 0.0175, 0)), ((0.062, 0.003, 0.0001), (0, -0.0175, 0)),
                   ((0.003, 0.032, 0.0001), (-0.0295, 0, 0)), ((0.003, 0.032, 0.0001), (0.0295, 0, 0))):
        box("nob", sz, lc, redink, None, bevel=0, parent=no)
    A["sticky"], A["no"] = st, no
    A["sticky_rest"] = (Vector(st.location), st.rotation_euler.z)

    stamp = empty("stamp", (0, 0, 0), I)
    box("stampbase", (0.07, 0.046, 0.018), (0, 0, 0.009), mat("rubber", (0.35, 0.05, 0.04), 0.6), None, bevel=0.002, parent=stamp)
    cyl("stamphandle", 0.011, 0.05, (0, 0, 0.043), wood, None, v=24, parent=stamp)
    ball("stampknob", 0.019, (0, 0, 0.075), wood, None, parent=stamp)
    A["stamp"] = stamp

    # the two lower bids
    for i, (pm, x, y, rz) in enumerate(((bluep, -0.07, 0.245, -6), (greenp, 0.1, 0.255, 7))):
        b = box("bid%d" % i, (0.17, 0.235, 0.0008), (x, y, DZ + 0.0006 + 0.001 * (i + 1)), pm, I, rot=(0, 0, rad(rz)), bevel=0)
        text("BID %d" % (i + 2), 0.016, (-0.068, 0.09, z), ink, None, align="LEFT", parent=b)
        for k, wd in enumerate((0.13, 0.11, 0.12)):
            box("line", (wd, 0.003, 0.0002), (-0.068 + wd / 2, 0.055 - k * 0.019, z), grayink, None, bevel=0, parent=b)
        text("LOWER", 0.04, (0, -0.045, z), ink, None, parent=b)
        A["bid%d" % i] = b; A["bid%d_rest" % i] = (Vector(b.location), b.rotation_euler.z)

    # the red flag on the estimate
    flag = empty("flag", (-0.07, 0.085, 0.001), None, parent=est)
    cyl("flagbase", 0.016, 0.006, (0, 0, 0.003), dark, None, v=24, parent=flag)
    cyl("flagpole", 0.0022, 0.15, (0, 0, 0.078), whitep, None, v=12, parent=flag)
    fl = box("flagcloth", (0.118, 0.0012, 0.07), (0.061, 0, 0.116), red, None, bevel=0, parent=flag)
    text("PROBLEM\nJOB", 0.0165, (0, -0.0009, 0), mat("flagtext", (0.97, 0.95, 0.9), 0.6), None, rot=(rad(90), 0, 0), parent=fl, spacing=0.8)
    A["flag"] = flag

    # standing cards
    def card(name, body, loc, cm, tm, w=0.15, h=0.085, size=0.022, tilt=12, yaw=0, which=I):
        hinge = empty(name, loc, which, rot=(rad(-tilt), 0, rad(yaw)))
        c = box(name + "_c", (w, 0.003, h), (0, 0, h / 2), cm, None, bevel=0.0008, parent=hinge)
        text(body, size, (0, -0.0019, 0), tm, None, rot=(rad(90), 0, 0), parent=c, spacing=0.85)
        box(name + "_foot", (w * 0.5, 0.04, 0.002), (0, 0.02, 0.001), cm, None, bevel=0, parent=hinge)
        return hinge
    A["price"] = card("price", "PRICE", (-0.42, -0.15, DZ), kraft, ink, w=0.13, h=0.075, size=0.027, yaw=3)
    A["quality"] = card("quality", "QUALITY", (-0.38, 0.2, DZ + 0.033), whitep, greenink, w=0.16, h=0.075, size=0.03, yaw=2)
    for i in range(3):
        box("sample%d" % i, (0.26, 0.17, 0.011), (-0.385 + 0.012 * i, 0.185 - 0.008 * i, DZ + 0.0055 + 0.011 * i), shingle, I,
            rot=(0, 0, rad(4 * i - 5)), bevel=0.001)
    A["smart"] = card("smart", "SMART\nCALL", (-0.1, -0.27, DZ), whitep, greenink, w=0.17, h=0.105, size=0.032, yaw=6)
    A["pride"] = card("pride", "PRIDE?", (0.1, -0.27, DZ), whitep, redink, w=0.17, h=0.105, size=0.04, yaw=-6)
    src = box("source", (0.1, 0.07, 0.0008), (0.185, -0.1, DZ + 0.0006), kraft, I, rot=(0, 0, rad(-4)), bevel=0)
    text("HIS ACCOUNT,\nVIA THE\nDAILY DOT", 0.011, (0, 0, 0.0007), ink, None, kind="semi", parent=src, spacing=0.85)
    A["source"] = src

    # dressing: lamp, hard hat, tape, mug, pencil, a framed roof on the wall
    lx, ly = -0.66, 0.27
    cyl("lampbase", 0.065, 0.012, (lx, ly, DZ + 0.006), brass, I)
    cyl("lampstem", 0.006, 0.34, (lx, ly, DZ + 0.18), brass, I, v=16)
    dome("lampshade", 0.12, (lx, ly, DZ + 0.34), cream, I, scale=(1, 1, 0.72))
    A["lamp"] = light("POINT", "lamp", (lx, ly, DZ + 0.33), 0, (1.0, 0.62, 0.32), size=0.03)
    hx, hy = 0.6, 0.17
    dome("hat", 0.115, (hx, hy, DZ + 0.012), yellow, I, scale=(1.0, 1.18, 0.82), thick=0.003)
    cyl("hatbrim", 0.128, 0.006, (hx, hy - 0.012, DZ + 0.013), yellow, I).scale = (1.0, 1.22, 1)
    box("hatridge", (0.022, 0.2, 0.012), (hx, hy, DZ + 0.104), yellow, I, bevel=0.004)
    cyl("tape", 0.043, 0.04, (0.47, -0.27, DZ + 0.02), yellow, I); cyl("tapehub", 0.017, 0.042, (0.47, -0.27, DZ + 0.02), dark, I)
    cyl("mug", 0.04, 0.09, (0.7, -0.14, DZ + 0.045), cream, I); cyl("coffee", 0.034, 0.004, (0.7, -0.14, DZ + 0.088), mat("coffee", (0.05, 0.02, 0.01), 0.1), I)
    cyl("pencil", 0.0038, 0.17, (-0.2, -0.06, DZ + 0.004), yellow, I, rot=(rad(90), 0, rad(24)), v=6, bevel=0.0)
    box("frame", (0.5, 0.02, 0.38), (0.42, 0.42, 1.42), dark, I, bevel=0.004)
    box("framein", (0.44, 0.012, 0.32), (0.42, 0.408, 1.42), mat("sky", (0.55, 0.68, 0.8), 0.8), I, bevel=0)
    box("fh", (0.2, 0.012, 0.11), (0.42, 0.4, 1.345), cream, I, bevel=0)
    bm = bmesh.new()
    for v in ((-0.135, 0, 0), (0.135, 0, 0), (0, 0, 0.1)): bm.verts.new(v)
    bm.faces.new(bm.verts)
    mesh_obj("froof", bm, mat("froofm", (0.32, 0.12, 0.08), 0.7), I, loc=(0.42, 0.398, 1.4))
    A["fill"] = light("AREA", "fill", (0.5, -1.4, 1.75), 6, (0.55, 0.65, 1.0), size=1.4)
    aim(A["fill"], (-0.3, 1.0, -0.72))
    A["qspot"] = light("SPOT", "qspot", (-0.1, -0.15, 1.5), 0, (1.0, 0.86, 0.7), size=0.02, spot=26)
    aim(A["qspot"], Vector((-0.38, 0.2, DZ + 0.07)) - Vector((-0.1, -0.15, 1.5)))
    A["ckey"] = light("SPOT", "ckey", (0, -1.3, 1.6), 0, (1.0, 0.9, 0.8), size=0.06, spot=30)


# ---------- the street set ----------
def build_street():
    E = "ext"
    grass = tex_mat("grass", "noise", (0.07, 0.19, 0.04), (0.16, 0.30, 0.07), 0.9, 2.5, 0.25)
    siding = mat("siding", (0.80, 0.74, 0.62), 0.75); trim = mat("trim", (0.93, 0.92, 0.88), 0.6)
    shingle = tex_mat("shingle", "brick", (0.11, 0.11, 0.125), (0.18, 0.17, 0.17), 0.85, 2.2, 0.6)
    doorm = mat("door", (0.05, 0.25, 0.27), 0.45); asphalt = tex_mat("asphalt", "noise", (0.035, 0.035, 0.04), (0.06, 0.06, 0.065), 0.85, 30, 0.15)
    walk = mat("walk", (0.5, 0.49, 0.46), 0.85); trunk = mat("trunk", (0.16, 0.09, 0.05), 0.8)
    leaf = [mat("leaf%d" % i, c, 0.85) for i, c in enumerate(((0.06, 0.25, 0.07), (0.10, 0.32, 0.08), (0.16, 0.36, 0.10)))]
    alu = mat("alu", (0.75, 0.76, 0.78), 0.35, 0.9); white = mat("truckwhite", (0.9, 0.9, 0.88), 0.3)
    glass = mat("glass", (0.02, 0.03, 0.04), 0.08); tire = mat("tire", (0.02, 0.02, 0.02), 0.8)
    signw = mat("signw", (0.95, 0.94, 0.9), 0.6); navy = mat("navy", (0.03, 0.05, 0.16), 0.5)
    redm = mat("ridered", (0.78, 0.05, 0.04), 0.5); whitet = mat("whitet", (0.98, 0.97, 0.94), 0.6)
    A["winm"] = mat("winglow", (0.08, 0.08, 0.1), 0.2, 0, (1.0, 0.72, 0.38), 0.3)
    A["tailm"] = mat("tail", (0.4, 0.02, 0.02), 0.3, 0, (1.0, 0.05, 0.03), 0.5)
    A["headm"] = mat("head", (0.9, 0.9, 0.8), 0.3, 0, (1.0, 0.9, 0.7), 0.3)

    box("ground", (160, 160, 0.1), (X0, 20, -0.05), grass, E, bevel=0)
    box("road", (160, 6.4, 0.04), (X0, -5.6, 0.0), asphalt, E, bevel=0)
    box("walk", (160, 1.3, 0.08), (X0, -1.75, 0.02), walk, E, bevel=0)
    for i in range(-8, 9): box("dash", (1.6, 0.14, 0.01), (X0 + i * 4.2, -5.6, 0.026), mat("dashy", (0.75, 0.62, 0.1), 0.7) if i == -8 else bpy.data.materials["dashy"], E, bevel=0)
    box("path", (1.3, 4.2, 0.05), (X0, 1.0, 0.03), walk, E, bevel=0)

    # the house: 8 m wide, 6 m deep, front wall at y = 3
    box("house", (8, 6, 3), (X0, 6, 1.5), siding, E, bevel=0.01)
    th = math.atan2(2.2, 3.5); L = math.hypot(3.5, 2.2) + 0.55
    for sgn in (-1, 1):
        box("roof", (9.1, L, 0.14), (X0, 6 + sgn * 1.75 * 1.04, 3 + 1.1 + 0.02), shingle, E, rot=(-sgn * th, 0, 0), bevel=0.01)
    for sx in (-4, 4):
        bm = bmesh.new()
        for v in ((0, -3, 0), (0, 3, 0), (0, 0, 2.2)): bm.verts.new(v)
        bm.faces.new(bm.verts); mesh_obj("gable", bm, siding, E, loc=(X0 + sx, 6, 3))
    box("ridge", (9.1, 0.25, 0.1), (X0, 6, 5.27), mat("ridgem", (0.08, 0.08, 0.09), 0.8), E, bevel=0.01)
    box("chimney", (0.7, 0.7, 1.6), (X0 + 2.6, 7.2, 4.9), mat("brick", (0.42, 0.16, 0.11), 0.85), E, bevel=0.02)
    box("door", (1.05, 0.08, 2.15), (X0, 2.97, 1.1), doorm, E, bevel=0.01)
    box("doorframe", (1.25, 0.06, 2.3), (X0, 2.985, 1.15), trim, E, bevel=0.01)
    cyl("knob", 0.045, 0.05, (X0 + 0.38, 2.9, 1.05), mat("knobm", (0.85, 0.65, 0.25), 0.25, 1.0), E, rot=(rad(90), 0, 0), v=16)
    box("step", (1.8, 0.9, 0.18), (X0, 2.5, 0.09), walk, E, bevel=0.01)
    for sx in (-2.35, 2.35):
        box("win", (1.5, 0.05, 1.25), (X0 + sx, 2.985, 1.75), A["winm"], E, bevel=0)
        box("winframe", (1.72, 0.06, 1.47), (X0 + sx, 2.995, 1.75), trim, E, bevel=0.01)
        box("winbar", (0.05, 0.07, 1.25), (X0 + sx, 2.97, 1.75), trim, E, bevel=0); box("winbar2", (1.5, 0.07, 0.05), (X0 + sx, 2.97, 1.75), trim, E, bevel=0)
        box("sill", (1.85, 0.2, 0.07), (X0 + sx, 2.93, 1.07), trim, E, bevel=0.01)
        for k in range(3): ball("bush", 0.42, (X0 + sx - 0.6 + k * 0.6, 2.45, 0.32), leaf[k % 3], E, scale=(1.1, 0.9, 0.85), flat=True)
    box("fascia", (9.1, 0.06, 0.2), (X0, 2.42, 2.93), trim, E, bevel=0)

    # ladder on the front eave
    def ladder(name, length, which, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
        root = empty(name, loc, which, parent=parent, rot=rot)
        for sx in (-0.21, 0.21): box(name + "rail", (0.045, 0.03, length), (sx, 0, length / 2), alu, None, bevel=0.004, parent=root)
        n = int(length / 0.3)
        for i in range(1, n): cyl(name + "rung", 0.013, 0.42, (0, 0, i * 0.3), alu, None, rot=(0, rad(90), 0), v=10, parent=root, bevel=0.0)
        return root
    ladder("ladder", 3.9, E, loc=(X0 - 1.05, 1.5, 0.02), rot=(rad(-17.5), 0, 0))

    # trees and a mailbox
    for (tx, ty, s) in ((-6.6, 4.6, 1.0), (7.2, 8.5, 1.25), (-9.5, 11, 1.4), (10.5, 3.5, 0.9), (-13, 5, 1.1), (15, 9, 1.3)):
        cyl("trunk", 0.2 * s, 2.2 * s, (X0 + tx, ty, 1.1 * s), trunk, E, v=10)
        for k, (dx, dz, r) in enumerate(((0, 2.9, 1.5), (0.6, 3.7, 1.1), (-0.5, 3.9, 1.0))):
            ball("leaf", r * s, (X0 + tx + dx * s, ty, dz * s), leaf[k], E, flat=True)
    box("mailpost", (0.09, 0.09, 1.1), (X0 + 3.6, -1.1, 0.55), trunk, E, bevel=0.01)
    box("mailbox", (0.22, 0.45, 0.22), (X0 + 3.6, -1.1, 1.18), mat("mailm", (0.55, 0.08, 0.06), 0.4), E, bevel=0.04)

    # the yard sign
    sx, sy = X0 - 2.6, -0.75
    sign = empty("sign", (sx, sy, 0), E, rot=(0, 0, rad(-13)))
    for dx in (-0.62, 0.62): box("stake", (0.07, 0.05, 1.9), (dx, 0.04, 0.95), trim, None, bevel=0.006, parent=sign)
    box("board", (1.6, 0.05, 1.18), (0, 0, 1.28), signw, None, bevel=0.012, parent=sign)
    text("$8,000", 0.44, (0, -0.032, 1.56), navy, None, rot=(rad(90), 0, 0), parent=sign, extrude=0.004)
    text("ROOF JOB", 0.215, (0, -0.032, 1.2), navy, None, rot=(rad(90), 0, 0), parent=sign, extrude=0.004)
    rider = empty("rider", (0, -0.05, 0.9), None, parent=sign, rot=(0, rad(5), 0))
    box("riderplate", (1.5, 0.03, 0.3), (0, 0, 0), redm, None, bevel=0.008, parent=rider)
    text("TURNED DOWN", 0.165, (0, -0.02, 0), whitet, None, rot=(rad(90), 0, 0), parent=rider, extrude=0.003)
    A["rider"] = rider

    # the truck, pointing along +x
    tr = empty("truck", (X0 - 3, -4.3, 0), E)
    box("t_body", (5.3, 1.95, 0.62), (0, 0, 0.83), white, None, bevel=0.08, parent=tr)
    box("t_cab", (1.75, 1.85, 0.78), (0.35, 0, 1.5), white, None, bevel=0.14, parent=tr)
    box("t_wind", (0.06, 1.6, 0.52), (1.215, 0, 1.52), glass, None, bevel=0.01, parent=tr)
    box("t_back", (0.06, 1.6, 0.5), (-0.52, 0, 1.52), glass, None, bevel=0.01, parent=tr)
    for sy_ in (-0.93, 0.93): box("t_side", (1.3, 0.04, 0.48), (0.35, sy_, 1.54), glass, None, bevel=0.01, parent=tr)
    box("t_bedhole", (2.0, 1.65, 0.3), (-1.55, 0, 1.03), mat("bed", (0.12, 0.12, 0.13), 0.7), None, bevel=0.02, parent=tr)
    box("t_stripe", (5.32, 1.97, 0.09), (0, 0, 0.78), mat("stripe", (0.9, 0.38, 0.04), 0.4), None, bevel=0, parent=tr)
    for wx in (-1.65, 1.7):
        for wy in (-0.93, 0.93):
            cyl("t_wheel", 0.43, 0.3, (wx, wy, 0.43), tire, None, rot=(rad(90), 0, 0), v=28, parent=tr, bevel=0.05)
            cyl("t_hub", 0.2, 0.32, (wx, wy, 0.43), alu, None, rot=(rad(90), 0, 0), v=16, parent=tr, bevel=0.02)
    for wy in (-0.72, 0.72):
        box("t_tail", (0.05, 0.3, 0.2), (-2.66, wy, 0.95), A["tailm"], None, bevel=0.01, parent=tr)
        box("t_head", (0.05, 0.36, 0.2), (2.66, wy, 0.92), A["headm"], None, bevel=0.01, parent=tr)
    for rx in (-2.3, -0.75):
        for wy in (-0.9, 0.9): box("t_rackpost", (0.05, 0.05, 0.85), (rx, wy, 1.55), dark_mat(), None, bevel=0.005, parent=tr)
        box("t_rackbar", (0.05, 1.9, 0.05), (rx, 0, 1.98), dark_mat(), None, bevel=0.005, parent=tr)
    ladder("t_ladder", 3.3, None, parent=tr, loc=(-3.1, 0.35, 2.04), rot=(0, rad(90), 0))
    A["truck"] = tr


def dark_mat():
    return bpy.data.materials.get("rackdark") or mat("rackdark", (0.04, 0.04, 0.045), 0.45, 0.6)


# ---------- world, sun, camera ----------
def build_world():
    w = bpy.data.worlds.new("w"); S.world = w; w.use_nodes = True
    nt = w.node_tree; bg = nt.nodes["Background"]
    try:
        tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ")
        mr = nt.nodes.new("ShaderNodeMapRange"); ramp = nt.nodes.new("ShaderNodeValToRGB")
        mr.inputs["From Min"].default_value = -1.0; mr.inputs["From Max"].default_value = 1.0
        nt.links.new(tc.outputs["Generated"], sp.inputs[0]); nt.links.new(sp.outputs["Z"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
        e = ramp.color_ramp.elements; e[0].position = 0.49; e[1].position = 0.95; e.new(0.6)
        A["sky"] = ramp.color_ramp
    except Exception as ex:
        print("sky fallback", ex); A["sky"] = None
    A["bg"] = bg
    A["sun"] = light("SUN", "sun", (0, 0, 10), 3.0, (1, 0.6, 0.35), size=1.2)
    cd = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cd); S.collection.objects.link(co); S.camera = co
    cd.sensor_width = 24; cd.dof.use_dof = True; cd.clip_start = 0.02; cd.clip_end = 400
    A["cam"] = co


def set_sky(horizon, mid, zenith, strength):
    A["bg"].inputs["Strength"].default_value = strength
    r = A["sky"]
    if r is None: A["bg"].inputs["Color"].default_value = (*mid, 1); return
    els = sorted(r.elements, key=lambda e: e.position)
    for e, c in zip(els, (horizon, mid, zenith)): e.color = (*c, 1)


def cam_set(pos, target, lens, fstop, focus=None):
    co = A["cam"]; pos = Vector(pos); target = Vector(target)
    co.location = pos; aim(co, target - pos)
    co.data.lens = lens; co.data.dof.aperture_fstop = fstop
    co.data.dof.focus_distance = (Vector(focus) - pos).length if focus is not None else (target - pos).length


def mix(a, b, u): return tuple(lerp(a[i], b[i], u) for i in range(len(a)))


# ---------- the film: everything as a function of seconds ----------
CUTS = (3.78, 10.14, 14.22, 16.44, 20.76, 23.26, 25.31)


def apply(t):
    ext = t < 3.78 or 23.26 <= t < 25.31
    for o in SETS["int"]: show(o, not ext)
    for o in SETS["ext"]: show(o, ext)
    sun = A["sun"]

    # ---- light ----
    if ext:
        dusk = t >= 23.26
        el = 2.5 if dusk else 13.0
        aim(sun, (math.cos(rad(el)) * 0.72, math.cos(rad(el)) * 0.66, -math.sin(rad(el))))
        sun.data.energy = 0.7 if dusk else 4.3; sun.data.color = (1.0, 0.42, 0.26) if dusk else (1.0, 0.7, 0.45)
        if dusk: set_sky((1.0, 0.40, 0.20), (0.42, 0.26, 0.45), (0.05, 0.08, 0.22), 0.55)
        else: set_sky((1.0, 0.66, 0.36), (0.74, 0.66, 0.66), (0.24, 0.42, 0.78), 1.0)
        bsdf(A["winm"]).inputs["Emission Strength"].default_value = 7.0 if dusk else 0.35
        bsdf(A["tailm"]).inputs["Emission Strength"].default_value = 14.0 if dusk else 0.4
        bsdf(A["headm"]).inputs["Emission Strength"].default_value = 9.0 if dusk else 0.3
    else:
        night = t >= 25.31
        u = seg(t, 3.78, 23.26)
        el = lerp(31.0, 8.0, u)
        aim(sun, (math.cos(rad(el)) * 0.95, math.cos(rad(el)) * 0.3, -math.sin(rad(el))))
        sun.data.energy = 0.0 if night else lerp(5.0, 1.6, u)
        sun.data.color = mix((1.0, 0.72, 0.46), (1.0, 0.38, 0.2), u)
        b = (0.20, 0.30, 0.62)
        set_sky(b, b, b, 0.035 if night else lerp(0.22, 0.09, u))
        A["lamp"].data.energy = 26.0 if night else 13.0 * smooth(seg(t, 12.0, 19.0))
        A["fill"].data.energy = 2.2 if night else lerp(6.5, 3.5, u)
        A["qspot"].data.energy = 0.0 if (t < 16.44 or t >= 20.76) else 55.0 * (1 - smooth(seg(t, 19.45, 19.85)))
        ck = A["ckey"]
        if 16.44 <= t < 20.76:
            ck.location = (-0.3, -1.15, 1.35); aim(ck, Vector((-0.41, -0.02, 0.8)) - Vector(ck.location)); ck.data.energy = 30.0
        elif night:
            ck.location = (0.0, -1.35, 1.65); aim(ck, Vector((0.0, -0.2, DZ + 0.04)) - Vector(ck.location)); ck.data.energy = 26.0
        else: ck.data.energy = 0.0

    # ---- things that move ----
    show_tree(A["rider"], t >= 1.22)
    k = back_out(seg(t, 1.22, 1.42), 2.6); A["rider"].scale = (lerp(1.7, 1.0, k),) * 3
    A["rider"].rotation_euler.y = rad(lerp(-9, 5, k))

    st = A["sticky"]; rest, rz = A["sticky_rest"]
    show_tree(st, t >= 4.12)
    f = ease_in(seg(t, 4.12, 4.52)); settle = math.sin(seg(t, 4.52, 4.8) * math.pi) * 0.004
    st.location = rest + Vector((0.03 * (1 - f), -0.02 * (1 - f), 0.2 * (1 - f) + settle))
    st.rotation_euler = (rad(22) * (1 - f), rad(-10) * (1 - f), rz + rad(-35) * (1 - f))
    show_tree(A["no"], t >= 13.06)

    for i, (a, b_) in enumerate(((7.9, 8.45), (8.3, 8.85))):
        bo = A["bid%d" % i]; rest, rz = A["bid%d_rest" % i]
        f = ease_out(seg(t, a, b_)); show_tree(bo, t >= a)
        bo.location = rest + Vector((0.75 * (1 - f), 0.05 * (1 - f), 0)); bo.rotation_euler.z = rz + rad(14) * (1 - f)

    sp = A["stamp"]; hit = Vector((0.0535, -0.0265, DZ + 0.0026))
    show_tree(sp, 12.5 <= t < 13.9)
    if t < 13.06: h = 0.26 * (1 - ease_in(seg(t, 12.62, 13.06)))
    elif t < 13.2: h = 0.0
    else: h = 0.34 * ease_in(seg(t, 13.2, 13.75))
    sp.location = hit + Vector((0, 0.1 * ease_in(seg(t, 13.2, 13.75)), h)); sp.rotation_euler = (0, 0, rad(-18))

    fl = A["flag"]; show_tree(fl, t >= 20.92)
    k = back_out(seg(t, 20.92, 21.3), 2.2); fl.scale = (k, k, k); fl.rotation_euler.z = rad(lerp(-70, 12, ease_out(seg(t, 20.92, 21.4))))

    A["truck"].location.x = X0 - 3 + (17.0 * ease_in(seg(t, 23.3, 25.7)) if t >= 23.26 else 5.5)
    A["truck"].location.y = -4.3

    for nm, a in (("smart", 25.36), ("pride", 26.12)):
        c = A[nm]; show_tree(c, t >= a)
        c.rotation_euler.x = rad(lerp(-85, -12, back_out(seg(t, a, a + 0.42), 1.6)))
    show_tree(A["source"], t < 25.31)

    # ---- camera ----
    shake = Vector((0, 0, 0))
    if 13.06 <= t < 13.4:
        d = (t - 13.06); shake = Vector((math.sin(d * 95) * 0.0016, 0, math.cos(d * 80) * 0.0014)) * (1 - d / 0.34)
    if t < 3.78:                      # the yard sign, golden hour
        u = smooth(seg(t, 0, 3.78))
        cam_set(mix((X0 - 3.75, -6.1, 1.5), (X0 - 3.55, -5.35, 1.58), u), (X0 - 2.5, -0.75, 1.02), 29, 2.4, focus=(X0 - 2.6, -0.75, 1.3))
    elif t < 10.14:                   # the estimate, then the camera lifts as the bids slide in
        u = smooth(seg(t, 3.78, 6.2)); v = smooth(seg(t, 6.28, 8.3))
        p = mix(mix((0.03, -0.5, 1.62), (0.03, -0.47, 1.56), u), (0.03, -0.44, 2.3), v)
        tg = mix((0.02, -0.13, DZ), (0.03, -0.06, DZ), v)
        cam_set(p, tg, 35, 4.0)
    elif t < 14.22:                   # close on the ask, the stamp lands
        u = smooth(seg(t, 10.14, 13.0))
        cam_set(Vector(mix((0.078, -0.31, 1.14), (0.07, -0.28, 1.1), u)) + shake, (0.055, -0.06, DZ), 50, 4.0, focus=(0.05, -0.012, DZ))
    elif t < 16.44:                   # it wasn't the two hundred: the mark and whose account this is
        u = smooth(seg(t, 14.22, 16.44))
        cam_set(mix((0.122, -0.36, 1.42), (0.128, -0.37, 1.47), u), (0.122, -0.1, DZ), 35, 4.0)
    elif t < 20.76:                   # price, not quality
        u = smooth(seg(t, 16.44, 20.76)); r = smooth(seg(t, 17.3, 17.85))
        fp = mix((-0.38, 0.2, 0.82), (-0.42, -0.15, 0.79), r)
        cam_set(mix((-0.4, -0.86, 1.0), (-0.4, -0.8, 0.99), u), (-0.4, 0.1, 0.70), 50, 2.0, focus=fp)
    elif t < 23.26:                   # the red flag
        u = smooth(seg(t, 20.76, 23.26))
        cam_set(mix((0.28, -0.6, 1.08), (0.24, -0.56, 1.06), u), (-0.02, 0.03, 0.814), 45, 2.8, focus=(-0.03, 0.06, 0.875))
    elif t < 25.31:                   # the truck leaves at dusk
        u = smooth(seg(t, 23.26, 25.31))
        cam_set(mix((X0 - 7.6, -14.6, 2.2), (X0 - 7.2, -14.1, 2.25), u), (X0 - 1.5, -1.0, 0.9), 30, 4.0, focus=(X0 - 1.5, -3.0, 1.0))
    else:                             # the question, at night
        u = smooth(seg(t, 25.31, 30.0))
        cam_set(mix((0.0, -1.12, 1.25), (0.0, -1.0, 1.2), u), (0.0, -0.12, 0.75), 32, 4.0, focus=(0.0, -0.2, DZ + 0.04))


def setup(res, spp):
    global S
    bpy.ops.wm.read_factory_settings(use_empty=True)
    S = bpy.context.scene
    build_world(); build_desk(); build_street()
    S.render.engine = "CYCLES"; c = S.cycles; c.device = "CPU"; c.samples = spp
    c.use_adaptive_sampling = True; c.adaptive_threshold = 0.03 if spp >= 24 else 0.08
    c.use_denoising = True; c.max_bounces = 5; c.diffuse_bounces = 2; c.glossy_bounces = 2; c.transmission_bounces = 2
    c.caustics_reflective = False; c.caustics_refractive = False
    S.render.use_persistent_data = True
    S.render.resolution_x = res; S.render.resolution_y = round(res * 16 / 9); S.render.resolution_percentage = 100
    S.render.fps = FPS
    try: S.view_settings.view_transform = "AgX"; S.view_settings.look = "AgX - Medium High Contrast"
    except Exception as e: print("view", e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=int, default=1080); ap.add_argument("--spp", type=int, default=32)
    ap.add_argument("--start", type=int, default=0); ap.add_argument("--end", type=int, default=int(DUR * FPS) - 1)
    ap.add_argument("--step", type=int, default=1); ap.add_argument("--out", default="/tmp/frames")
    ap.add_argument("--jpg", action="store_true"); ap.add_argument("--times", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    setup(a.res, a.spp)
    S.render.image_settings.file_format = "JPEG" if a.jpg else "PNG"
    if a.jpg: S.render.image_settings.quality = 90
    frames = [round(float(x) * FPS) for x in a.times.split(",")] if a.times else range(a.start, a.end + 1, a.step)
    t0 = time.time(); n = 0
    for f in frames:
        p = os.path.join(a.out, "f%04d.%s" % (f, "jpg" if a.jpg else "png"))
        if os.path.exists(p): continue
        S.frame_set(f); apply(f / FPS)
        S.render.filepath = p
        bpy.ops.render.render(write_still=True); n += 1
        print("FRAME %d t=%.2f done, %.1f s a frame so far" % (f, f / FPS, (time.time() - t0) / n), flush=True)
    print("DONE %d frames in %.0f s" % (n, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
