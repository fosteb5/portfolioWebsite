# Shared helpers for the tethered drone model: meshes, materials and objects.
# Loaded with exec() by td_build.py and the render script, so everything here is plain functions.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

ROOT = r"C:\Users\foste\OneDrive\Resume\portfolioWebsite\Projects\TetheredDrone\Blender"
TAU = math.tau


# ---------------------------------------------------------------- collections and objects

def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def _drop(name):
    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)


def obj(name, data, col, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    _drop(name)
    ob = bpy.data.objects.new(name, data)
    col.objects.link(ob)
    ob.parent = parent
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    return ob


def empty(name, col, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), size=0.05):
    ob = obj(name, None, col, parent, loc, rot)
    ob.empty_display_size = size
    ob.empty_display_type = 'PLAIN_AXES'
    return ob


def finish(me, smooth=True, angle=35):
    """Shade smooth with sharp edges above `angle`, the way a machined or moulded part catches light."""
    if smooth:
        me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
        me.set_sharp_from_angle(angle=math.radians(angle))
    return me


def to_mesh(name, bm, smooth=True, angle=35, mats=()):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    return finish(me, smooth, angle)


def part(name, bm, col, mats, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), smooth=True, angle=35, bevel=0.0, segs=2):
    """A finished part: mesh, materials, parent and an optional small bevel so its edges catch highlights."""
    if not isinstance(mats, (list, tuple)):
        mats = [mats]
    ob = obj(name, to_mesh(name, bm, smooth, angle, mats), col, parent, loc, rot)
    if bevel:
        bev(ob, bevel, segs)
    return ob


def bev(ob, width, segs=2, angle=40):
    m = ob.modifiers.new('Bevel', 'BEVEL')
    m.width = width
    m.segments = segs
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    m.harden_normals = True
    m.miter_outer = 'MITER_ARC'
    return m


# ---------------------------------------------------------------- bmesh primitives

def M(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    return Matrix.LocRotScale(Vector(loc), Euler(rot), Vector(scale))


def box(bm, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=0):
    r = bmesh.ops.create_cube(bm, size=1.0, matrix=M(loc, rot, size))
    _mat(r['verts'], mat)
    return r['verts']


def cyl(bm, r, depth, loc=(0, 0, 0), rot=(0, 0, 0), segs=32, r2=None, mat=0, caps=True):
    """A cylinder along local Z, centred on `loc`."""
    res = bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segs, radius1=r,
                                radius2=r if r2 is None else r2, depth=depth, matrix=M(loc, rot))
    _mat(res['verts'], mat)
    return res['verts']


def sphere(bm, r, loc=(0, 0, 0), scale=(1, 1, 1), segs=24, rings=12, mat=0, rot=(0, 0, 0)):
    res = bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r, matrix=M(loc, rot, scale))
    _mat(res['verts'], mat)
    return res['verts']


def tube(bm, r_out, r_in, depth, loc=(0, 0, 0), rot=(0, 0, 0), segs=32, mat=0):
    """A hollow cylinder along local Z."""
    mtx = M(loc, rot)
    h = depth / 2
    rings = []
    for (rad, z) in ((r_out, -h), (r_out, h), (r_in, h), (r_in, -h)):
        rings.append([bm.verts.new(mtx @ Vector((rad * math.cos(TAU * i / segs), rad * math.sin(TAU * i / segs), z))) for i in range(segs)])
    faces = []
    for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
        for i in range(segs):
            j = (i + 1) % segs
            faces.append(bm.faces.new((rings[a][i], rings[a][j], rings[b][j], rings[b][i])))
    for f in faces:
        f.material_index = mat
    return [v for ring in rings for v in ring]


def prism(bm, outline, z0, z1, mat=0, holes=()):
    """Extrude a 2D outline (counter-clockwise, list of (x, y)) from z0 to z1. Holes are cut afterwards with cut_holes()."""
    bot = [bm.verts.new((x, y, z0)) for x, y in outline]
    top = [bm.verts.new((x, y, z1)) for x, y in outline]
    n = len(outline)
    fs = [bm.faces.new(top), bm.faces.new(list(reversed(bot)))]
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((bot[i], bot[j], top[j], top[i])))
    for f in fs:
        f.material_index = mat
    return bot + top


def rounded_poly(points, radius, segs=6):
    """Round the corners of a closed 2D polygon."""
    out = []
    n = len(points)
    for i in range(n):
        p0, p1, p2 = Vector(points[i - 1]), Vector(points[i]), Vector(points[(i + 1) % n])
        a = (p0 - p1).normalized()
        b = (p2 - p1).normalized()
        ang = math.acos(max(-1, min(1, a.dot(b))))
        d = radius / math.tan(ang / 2)
        d = min(d, (p0 - p1).length * 0.45, (p2 - p1).length * 0.45)
        rr = d * math.tan(ang / 2)
        s, e = p1 + a * d, p1 + b * d
        bis = (a + b).normalized()
        c = p1 + bis * math.sqrt(d * d + rr * rr)
        a0 = math.atan2(s.y - c.y, s.x - c.x)
        a1 = math.atan2(e.y - c.y, e.x - c.x)
        da = (a1 - a0 + math.pi) % TAU - math.pi
        for k in range(segs + 1):
            t = a0 + da * k / segs
            out.append((c.x + rr * math.cos(t), c.y + rr * math.sin(t)))
    return out


def _mat(verts, mat):
    if not mat:
        return
    vs = set(verts)
    for v in vs:
        for f in v.link_faces:
            if all(w in vs for w in f.verts):
                f.material_index = mat


def cut(ob, cutters, solver='EXACT'):
    """Boolean-subtract the cutter objects from `ob`, bake the result into its mesh, and delete the cutters."""
    for c in cutters:
        m = ob.modifiers.new('cut', 'BOOLEAN')
        m.operation = 'DIFFERENCE'
        m.solver = solver
        m.object = c
        c.hide_render = True
        c.hide_viewport = True
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    for m in list(ob.modifiers):
        if m.type == 'BOOLEAN':
            ob.modifiers.remove(m)
    old = ob.data
    ob.data = me
    me.name = old.name
    bpy.data.meshes.remove(old)
    for c in cutters:
        d = c.data
        bpy.data.objects.remove(c, do_unlink=True)
        if d and d.users == 0:
            bpy.data.meshes.remove(d)
    return ob


def cutter(name, bm, col):
    return obj(name, to_mesh(name, bm, smooth=False), col)


# ---------------------------------------------------------------- materials

def node_mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (600, 0)
    return m, nt, out


def principled(name, color=(0.5, 0.5, 0.5), metal=0.0, rough=0.4, coat=0.0, coat_rough=0.05,
               emit=None, emit_strength=0.0, alpha=1.0, transmission=0.0, ior=1.45, aniso=0.0, spec=0.5,
               sss=0.0):
    m, nt, out = node_mat(name)
    p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    p.inputs['Coat Weight'].default_value = coat
    p.inputs['Coat Roughness'].default_value = coat_rough
    p.inputs['IOR'].default_value = ior
    p.inputs['Specular IOR Level'].default_value = spec
    p.inputs['Transmission Weight'].default_value = transmission
    p.inputs['Anisotropic'].default_value = aniso
    p.inputs['Alpha'].default_value = alpha
    if sss:
        p.inputs['Subsurface Weight'].default_value = sss
    if emit:
        p.inputs['Emission Color'].default_value = (*emit, 1)
        p.inputs['Emission Strength'].default_value = emit_strength
    nt.links.new(p.outputs[0], out.inputs[0])
    if alpha < 1 or transmission > 0:
        m.surface_render_method = 'BLENDED' if alpha < 1 else 'DITHERED'
    return m


def sock(sockets, identifier):
    """Look a socket up by identifier. The Mix node has several sockets called 'A' and 'Result', one per data type."""
    return next(s for s in sockets if s.identifier == identifier)


def add(nt, kind, loc=(0, 0), **props):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in props.items():
        setattr(n, k, v)
    return n


def link(nt, a, b):
    nt.links.new(a, b)


def math_node(nt, op, a=None, b=None, loc=(0, 0), clamp=False):
    n = nt.nodes.new('ShaderNodeMath')
    n.operation = op
    n.location = loc
    n.use_clamp = clamp
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def get_principled(m):
    return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def carbon(name='TD_Carbon', scale=260.0, tint=(0.018, 0.019, 0.021), coat=1.0, coat_rough=0.07, rough=(0.22, 0.42), spec=0.5):
    """Twill-weave carbon fibre under a clear coat. Weave from two wave textures picked by a checker."""
    m = principled(name, tint, 0.0, 0.32, coat=coat, coat_rough=coat_rough, spec=spec)
    nt = m.node_tree
    p = get_principled(m)
    tc = add(nt, 'ShaderNodeTexCoord', (-1200, 0))
    mp = add(nt, 'ShaderNodeMapping', (-1000, 0))
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    link(nt, tc.outputs['Object'], mp.inputs['Vector'])
    chk = add(nt, 'ShaderNodeTexChecker', (-760, 200))
    chk.inputs['Scale'].default_value = 1.0
    link(nt, mp.outputs[0], chk.inputs['Vector'])
    w1 = add(nt, 'ShaderNodeTexWave', (-760, -60), wave_type='BANDS', bands_direction='X')
    w2 = add(nt, 'ShaderNodeTexWave', (-760, -300), wave_type='BANDS', bands_direction='Y')
    for w in (w1, w2):
        w.inputs['Scale'].default_value = 2.0
        w.inputs['Distortion'].default_value = 0.0
        link(nt, mp.outputs[0], w.inputs['Vector'])
    mix = add(nt, 'ShaderNodeMix', (-500, 0), data_type='FLOAT')
    link(nt, chk.outputs['Fac'], sock(mix.inputs, 'Factor_Float'))
    link(nt, w1.outputs['Fac'], sock(mix.inputs, 'A_Float'))
    link(nt, w2.outputs['Fac'], sock(mix.inputs, 'B_Float'))
    rr = add(nt, 'ShaderNodeMapRange', (-300, 0))
    rr.inputs['To Min'].default_value = rough[0]
    rr.inputs['To Max'].default_value = rough[1]
    link(nt, sock(mix.outputs, 'Result_Float'), rr.inputs['Value'])
    link(nt, rr.outputs[0], p.inputs['Roughness'])
    col = add(nt, 'ShaderNodeMix', (-300, -200), data_type='RGBA')
    sock(col.inputs, 'A_Color').default_value = (*tint, 1)
    sock(col.inputs, 'B_Color').default_value = (tint[0] * 2.6, tint[1] * 2.6, tint[2] * 2.8, 1)
    link(nt, sock(mix.outputs, 'Result_Float'), sock(col.inputs, 'Factor_Float'))
    link(nt, sock(col.outputs, 'Result_Color'), p.inputs['Base Color'])
    return m


def brushed(name, color, rough=0.28, aniso=0.2, scale=900.0):
    """Anodised or bare aluminium with fine machining marks."""
    m = principled(name, color, 1.0, rough, aniso=aniso)
    nt = m.node_tree
    p = get_principled(m)
    tc = add(nt, 'ShaderNodeTexCoord', (-900, 0))
    n = add(nt, 'ShaderNodeTexNoise', (-700, 0))
    n.inputs['Scale'].default_value = scale
    n.inputs['Detail'].default_value = 4
    mp = add(nt, 'ShaderNodeMapping', (-800, 0))
    mp.inputs['Scale'].default_value = (1, 1, 0.02)
    link(nt, tc.outputs['Object'], mp.inputs['Vector'])
    link(nt, mp.outputs[0], n.inputs['Vector'])
    rr = add(nt, 'ShaderNodeMapRange', (-450, 0))
    rr.inputs['To Min'].default_value = rough * 0.75
    rr.inputs['To Max'].default_value = rough * 1.3
    link(nt, n.outputs['Fac'], rr.inputs['Value'])
    link(nt, rr.outputs[0], p.inputs['Roughness'])
    return m
