# Spray: three flat fans of water from the nozzles to the glass, drawn as droplet streaks (as a camera
# with a fast shutter would catch them), a liquid sheet close to each nozzle, and splash coming off the glass.
# Everything is recomputed for each frame from the drone's position, so a scroll scrub stays consistent.
import numpy as np

NOZZLE_LOCAL = [(0.0, LANCE_END + 0.007 + 0.026, LANCE_Z + dz) for dz in NOZZLE_DZ]
FAN = math.radians(33)
GLASS_Y = 0.0
GRAV = np.array((0.0, 0.0, -9.81))


def streak_group():
    ng = bpy.data.node_groups.get('TD_SprayStreaks')
    if ng:
        bpy.data.node_groups.remove(ng)
    ng = bpy.data.node_groups.new('TD_SprayStreaks', 'GeometryNodeTree')
    ng.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    nd = ng.nodes
    gi = nd.new('NodeGroupInput')
    go = nd.new('NodeGroupOutput')
    m2c = nd.new('GeometryNodeMeshToCurve')
    rad = nd.new('GeometryNodeInputNamedAttribute')
    rad.data_type = 'FLOAT'
    rad.inputs['Name'].default_value = 'rad'
    prof = nd.new('GeometryNodeCurvePrimitiveCircle')
    prof.inputs['Resolution'].default_value = 4
    prof.inputs['Radius'].default_value = 1.0
    c2m = nd.new('GeometryNodeCurveToMesh')
    sm = nd.new('GeometryNodeSetMaterial')
    sm.inputs['Material'].default_value = bpy.data.materials['TD_Water']
    L = ng.links
    L.new(gi.outputs[0], m2c.inputs['Mesh'])
    # Curve to Mesh scales the profile by its Scale input, not by the curve radius
    L.new(m2c.outputs[0], c2m.inputs['Curve'])
    L.new(rad.outputs['Attribute'], c2m.inputs['Scale'])
    L.new(prof.outputs['Curve'], c2m.inputs['Profile Curve'])
    L.new(c2m.outputs[0], sm.inputs['Geometry'])
    L.new(sm.outputs[0], go.inputs[0])
    return ng


def water_materials(m):
    w = principled('TD_Water', (0.82, 0.9, 0.97), 0.0, 0.06, alpha=0.6, emit=(0.75, 0.85, 0.95), emit_strength=0.35, spec=0.8)
    w.surface_render_method = 'DITHERED'
    m['water'] = w
    # the liquid sheet: dense by the nozzle, breaking up towards the glass
    mm, nt, out = node_mat('TD_Mist')
    mm.surface_render_method = 'BLENDED'
    mm.use_transparency_overlap = True
    uv = add(nt, 'ShaderNodeUVMap', (-1100, 0))
    sep = add(nt, 'ShaderNodeSeparateXYZ', (-900, 0))
    link(nt, uv.outputs['UV'], sep.inputs[0])
    u, v = sep.outputs['X'], sep.outputs['Y']
    near = math_node(nt, 'POWER', math_node(nt, 'SUBTRACT', 1.0, u, (-700, 100)), 2.2, (-550, 100))
    edge = math_node(nt, 'MULTIPLY', math_node(nt, 'SUBTRACT', 1.0, math_node(nt, 'ABSOLUTE', math_node(nt, 'SUBTRACT', math_node(nt, 'MULTIPLY', v, 2.0, (-900, -200)), 1.0, (-750, -200)), None, (-600, -200)), (-450, -200)), 1.0, (-300, -200))
    nz = add(nt, 'ShaderNodeTexNoise', (-900, -450))
    nz.inputs['Scale'].default_value = 9
    nz.inputs['Detail'].default_value = 4
    mp = add(nt, 'ShaderNodeMapping', (-1100, -450))
    mp.inputs['Scale'].default_value = (1.2, 28, 1)
    link(nt, uv.outputs['UV'], mp.inputs['Vector'])
    link(nt, mp.outputs[0], nz.inputs['Vector'])
    streak = add(nt, 'ShaderNodeMapRange', (-700, -450))
    streak.inputs['From Min'].default_value = 0.35
    streak.inputs['From Max'].default_value = 0.8
    link(nt, nz.outputs['Fac'], streak.inputs['Value'])
    a1 = math_node(nt, 'MULTIPLY', near, math_node(nt, 'POWER', edge, 0.6, (-150, -200)), (-150, 100))
    a2 = math_node(nt, 'MULTIPLY', a1, streak.outputs[0], (0, 0))
    a3 = math_node(nt, 'MULTIPLY', a2, 0.9, (150, 0))
    amt = add(nt, 'ShaderNodeValue', (0, 250))
    amt.name = amt.label = 'Amount'
    amt.outputs[0].default_value = 1.0
    alpha = math_node(nt, 'MULTIPLY', a3, amt.outputs[0], (300, 0))
    p = add(nt, 'ShaderNodeBsdfPrincipled', (300, 300))
    p.inputs['Base Color'].default_value = (0.86, 0.92, 0.98, 1)
    p.inputs['Roughness'].default_value = 0.25
    p.inputs['Emission Color'].default_value = (0.8, 0.88, 0.96, 1)
    p.inputs['Emission Strength'].default_value = 0.6
    link(nt, alpha, p.inputs['Alpha'])
    link(nt, p.outputs[0], out.inputs[0])
    m['mist'] = mm


def build_spray(m):
    col = coll('TD Spray')
    water_materials(m)
    ng = streak_group()
    me = bpy.data.meshes.get('TD_SprayPts') or bpy.data.meshes.new('TD_SprayPts')
    ob = obj('TD_Spray', me, col)
    mod = ob.modifiers.new('streaks', 'NODES')
    mod.node_group = ng
    for k in range(3):
        mm = bpy.data.meshes.get(f'TD_MistFan{k}') or bpy.data.meshes.new(f'TD_MistFan{k}')
        if not mm.materials:
            mm.materials.append(m['mist'])
        obj(f'TD_MistFan{k}', mm, col)
    return ob


def _fan_mesh(me, apex, fwd, up, side, reach, nseg=28, nrad=14):
    """A fan from the nozzle to where its edge meets the glass, with UV u = distance and v = across."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new('UVMap')
    grid = []
    for i in range(nrad + 1):
        row = []
        for j in range(nseg + 1):
            a = -FAN + 2 * FAN * j / nseg
            d = fwd * math.cos(a) + up * math.sin(a)
            t_hit = (GLASS_Y - apex.y) / max(1e-4, d.y)
            r = t_hit * reach * (i / nrad)
            # a slight thickening across the sheet so it is not a razor edge side-on
            row.append(bm.verts.new(apex + d * r + side * 0.004 * (i / nrad) * math.sin(j * 1.7)))
        grid.append(row)
    for i in range(nrad):
        for j in range(nseg):
            f = bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
            for lp, (ii, jj) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))):
                lp[uvl].uv = (ii / nrad, jj / nseg)
    bm.to_mesh(me)
    bm.free()


def set_spray(amount, seed, shutter=0.0032):
    """amount 0 (off) to 1 (full). While it starts up, the fans grow out from the nozzles towards the glass."""
    me = bpy.data.meshes['TD_SprayPts']
    root = bpy.data.objects['TD_Drone']
    Mw = root.matrix_world
    R3 = Mw.to_3x3().normalized()
    fwd, up, side = R3 @ Vector((0, 1, 0)), R3 @ Vector((0, 0, 1)), R3 @ Vector((1, 0, 0))
    me.clear_geometry()
    for k in range(3):
        fm = bpy.data.meshes[f'TD_MistFan{k}']
        fm.clear_geometry()
        bpy.data.objects[f'TD_MistFan{k}'].hide_render = amount <= 0.001
    if amount <= 0.001:
        return
    reach = min(1.0, amount * 1.6)
    rng = np.random.default_rng(seed)
    starts, ends, rads = [], [], []
    F, U, S = np.array(fwd), np.array(up), np.array(side)
    for k, nl in enumerate(NOZZLE_LOCAL):
        apex = Mw @ Vector(nl)
        _fan_mesh(bpy.data.meshes[f'TD_MistFan{k}'], apex, fwd, up, side, reach)
        A = np.array(apex)
        n = int(1700 * min(1.0, amount * 1.3))
        a = rng.uniform(-FAN, FAN, n)
        a = np.where(rng.random(n) < 0.25, np.sign(a) * FAN * rng.uniform(0.82, 1.0, n), a)  # heavier edges, as flat fans have
        b = rng.normal(0, 0.035, n)
        spd = rng.normal(9.0, 0.9, n)
        d = (np.outer(np.cos(a) * np.cos(b), F) + np.outer(np.sin(a), U) + np.outer(np.sin(b), S))
        v = d * spd[:, None]
        t_hit = (GLASS_Y - A[1]) / np.maximum(1e-4, v[:, 1])
        # droplets only exist once the sheet has broken up, a few centimetres out
        tau = rng.uniform(0.15, 1.0, n) * t_hit * reach
        pos = A + v * tau[:, None] + 0.5 * GRAV * (tau ** 2)[:, None]
        tail = A + v * np.maximum(0, tau - shutter)[:, None] + 0.5 * GRAV * (np.maximum(0, tau - shutter) ** 2)[:, None]
        starts.append(tail)
        ends.append(pos)
        rads.append(rng.uniform(0.0004, 0.0011, n))
        if reach >= 0.999:
            # splash: off the glass along the line where the fan lands
            ns = int(900 * amount)
            aa = rng.uniform(-FAN, FAN, ns)
            dd = np.outer(np.cos(aa), F) + np.outer(np.sin(aa), U)
            th = (GLASS_Y - A[1]) / np.maximum(1e-4, dd[:, 1])
            hit = A + dd * th[:, None]
            hit[:, 1] = GLASS_Y - 0.004
            sv = (np.outer(rng.normal(0, 0.7, ns), S) - np.outer(rng.uniform(0.3, 1.8, ns), F)
                  + np.outer(rng.normal(0.1, 0.8, ns), U))
            st = rng.uniform(0, 0.11, ns)
            p2 = hit + sv * st[:, None] + 0.5 * GRAV * (st ** 2)[:, None]
            p1 = hit + sv * np.maximum(0, st - shutter * 2)[:, None] + 0.5 * GRAV * (np.maximum(0, st - shutter * 2) ** 2)[:, None]
            p2[:, 1] = np.minimum(p2[:, 1], GLASS_Y - 0.002)
            p1[:, 1] = np.minimum(p1[:, 1], GLASS_Y - 0.002)
            starts.append(p1)
            ends.append(p2)
            rads.append(rng.uniform(0.0003, 0.0008, ns))
    P0 = np.concatenate(starts)
    P1 = np.concatenate(ends)
    R = np.concatenate(rads)
    n = len(P0)
    verts = np.empty((2 * n, 3), np.float32)
    verts[0::2] = P0
    verts[1::2] = P1
    edges = np.arange(2 * n, dtype=np.int32).reshape(n, 2)
    me.vertices.add(2 * n)
    me.vertices.foreach_set('co', verts.ravel())
    me.edges.add(n)
    me.edges.foreach_set('vertices', edges.ravel())
    at = me.attributes.get('rad') or me.attributes.new('rad', 'FLOAT', 'POINT')
    at.data.foreach_set('value', np.repeat(R, 2).astype(np.float32))
    me.update()
