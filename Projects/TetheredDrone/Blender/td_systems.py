# Water and tether: the swivel hub the tether plugs into, the solenoid valve, hoses, the spray lance
# with its three fan nozzles, the landing gear, and the tether itself (a power cable and a water hose twisted together).

HUB_TOP = UNDER - 0.0045
LANCE_Z = -0.036
LANCE_END = 0.80
NOZZLE_DZ = (-0.06, 0.0, 0.06)


def rod(bm, p0, p1, r, segs=24, mat=0, hollow=None):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    rot = d.to_track_quat('Z', 'Y').to_euler()
    mid = (p0 + p1) / 2
    if hollow:
        return tube(bm, r, hollow, d.length, loc=mid, rot=rot, segs=segs, mat=mat)
    return cyl(bm, r, d.length, loc=mid, rot=rot, segs=segs, mat=mat)


def build_hub(m, col, root):
    grp = empty('TD_GrpHub', col, root, loc=(0, 0, HUB_TOP))
    bm = bmesh.new()
    cyl(bm, 0.03, 0.004, loc=(0, 0, -0.002), segs=64)
    part('TD_HubFlange', bm, col, m['gunmetal'], grp, bevel=0.0008)
    bm = bmesh.new()
    for k in range(6):
        a = TAU * k / 6 + 0.26
        cyl(bm, 0.0025, 0.0025, loc=(0.025 * math.cos(a), 0.025 * math.sin(a), -0.0052), segs=20)
    part('TD_HubScrews', bm, col, m['black_steel'], grp, bevel=0.0003)
    bm = bmesh.new()
    cyl(bm, 0.022, 0.03, loc=(0, 0, -0.019), segs=64)
    part('TD_HubBody', bm, col, m['alu'], grp, bevel=0.0012, segs=3)
    bm = bmesh.new()
    tube(bm, 0.0226, 0.021, 0.004, loc=(0, 0, -0.012), segs=64)
    tube(bm, 0.0226, 0.021, 0.0025, loc=(0, 0, -0.03), segs=64)
    part('TD_HubBands', bm, col, m['gold'], grp)
    bm = bmesh.new()
    cyl(bm, 0.019, 0.006, loc=(0, 0, -0.037), segs=64)
    part('TD_HubBearing', bm, col, m['black_steel'], grp, bevel=0.0008)
    # strain relief bellows where the tether leaves
    bm = bmesh.new()
    for k in range(9):
        r = 0.0135 - k * 0.0005
        z = -0.042 - k * 0.0052
        cyl(bm, r, 0.0034, loc=(0, 0, z), segs=40)
        cyl(bm, r - 0.0022, 0.0022, loc=(0, 0, z - 0.0027), segs=40)
    part('TD_HubBellows', bm, col, m['rubber'], grp, bevel=0.0009)
    # water out to the valve, power in to the converter
    bm = bmesh.new()
    rod(bm, (0, 0.018, -0.02), (0, 0.03, -0.02), 0.0055, segs=6)
    part('TD_HubWaterPort', bm, col, m['brass'], grp, bevel=0.0006)
    bm = bmesh.new()
    rod(bm, (0, -0.018, -0.02), (0, -0.032, -0.02), 0.0068, segs=6)
    part('TD_HubPowerGland', bm, col, m['plastic'], grp, bevel=0.0008)
    return grp


def build_water(m, col, root):
    grp = empty('TD_GrpWater', col, root)
    # solenoid valve
    vz = HUB_TOP - 0.013
    bm = bmesh.new()
    box(bm, (0.022, 0.032, 0.018), loc=(0, 0.066, vz))
    part('TD_ValveBody', bm, col, m['brass'], grp, bevel=0.0015, segs=3)
    bm = bmesh.new()
    box(bm, (0.024, 0.024, 0.024), loc=(0, 0.066, vz - 0.021))
    part('TD_ValveCoil', bm, col, m['plastic'], grp, bevel=0.002, segs=3)
    bm = bmesh.new()
    cyl(bm, 0.004, 0.006, loc=(0, 0.066, vz - 0.036), segs=6)
    part('TD_ValveNut', bm, col, m['steel'], grp, bevel=0.0004)
    fit = bmesh.new()
    collet = bmesh.new()
    for y, s in ((0.047, -1), (0.085, 1)):
        rod(fit, (0, y, vz), (0, y + s * 0.012, vz), 0.0065, segs=6)
        rod(collet, (0, y + s * 0.012, vz), (0, y + s * 0.0145, vz), 0.0058, segs=32)
    part('TD_ValveFittings', fit, col, m['plastic'], grp, bevel=0.0006)
    part('TD_ValveCollets', collet, col, m['wire_blue'], grp, bevel=0.0004)
    for k, mat in enumerate(('wire_red', 'wire_black')):
        dx = (k - 0.5) * 0.006
        wire(f'TD_ValveWire{k}', [(dx, 0.054, vz - 0.024), (dx * 1.5, 0.046, vz - 0.02), (dx * 2, 0.04, HUB_TOP - 0.002)], 0.0009, m[mat], col, grp)
    # hoses: hub to valve, valve to lance
    wire('TD_HoseA', [(0, 0.03, HUB_TOP - 0.02), (0, 0.035, HUB_TOP - 0.018), (0, 0.032, vz - 0.0), (0, 0.0335, vz)], 0.005, m['hose'], col, grp)
    wire('TD_HoseB', [(0, 0.0995, vz), (0, 0.108, vz - 0.006), (0, 0.104, LANCE_Z - 0.003), (0, 0.112, LANCE_Z)], 0.005, m['hose'], col, grp)

    # lance, its bracket and struts
    bm = bmesh.new()
    rod(bm, (0, 0.112, LANCE_Z), (0, LANCE_END, LANCE_Z), 0.008, segs=40, hollow=0.0065)
    part('TD_Lance', bm, col, m['carbon_tube'], grp, angle=20)
    bm = bmesh.new()
    box(bm, (0.03, 0.016, LANCE_Z + 0.008 - UNDER + 0.002), loc=(0, 0.118, (UNDER + LANCE_Z + 0.008) / 2 - 0.001))
    rod(bm, (0, 0.11, LANCE_Z), (0, 0.126, LANCE_Z), 0.0115, segs=40)
    br = part('TD_LanceBracket', bm, col, m['gunmetal'], grp, bevel=0.0012)
    bm = bmesh.new()
    rod(bm, (0, 0.1, LANCE_Z), (0, 0.14, LANCE_Z), 0.0081, segs=40)
    cut(br, [cutter('cut_lb', bm, col)])
    st = bmesh.new()
    clamps = bmesh.new()
    for sx in (-1, 1):
        a = math.radians(60 if sx > 0 else 120)
        p0 = Vector((0.204 * math.cos(a), 0.204 * math.sin(a), ARM_Z - TUBE_R - 0.004))
        p1 = Vector((sx * 0.011, 0.45, LANCE_Z))
        rod(st, p0, p1, 0.0045, segs=24, hollow=0.0035)
        box(clamps, (0.016, 0.016, 0.012), loc=p0 + Vector((0, 0, -0.002)))
        box(clamps, (0.03, 0.02, 0.022), loc=(0, 0.45, LANCE_Z))
    part('TD_Struts', st, col, m['carbon_tube'], grp, angle=20)
    cl = part('TD_StrutClamps', clamps, col, m['gunmetal'], grp, bevel=0.0012)
    bm = bmesh.new()
    rod(bm, (0, 0.43, LANCE_Z), (0, 0.47, LANCE_Z), 0.0081, segs=40)
    cut(cl, [cutter('cut_sc', bm, col)])

    # spray head: a tee, a vertical manifold and three fan nozzles
    y = LANCE_END + 0.007
    bm = bmesh.new()
    box(bm, (0.018, 0.018, 0.018), loc=(0, y, LANCE_Z))
    rod(bm, (0, y, LANCE_Z - 0.078), (0, y, LANCE_Z + 0.078), 0.0062, segs=32)
    for z in (-0.078, 0.078):
        cyl(bm, 0.0075, 0.006, loc=(0, y, LANCE_Z + z), segs=6)
    part('TD_SprayManifold', bm, col, m['brass'], grp, bevel=0.0008)
    noz = bmesh.new()
    tips = bmesh.new()
    for dz in NOZZLE_DZ:
        z = LANCE_Z + dz
        rod(noz, (0, y + 0.005, z), (0, y + 0.014, z), 0.0068, segs=6)
        rod(noz, (0, y + 0.014, z), (0, y + 0.021, z), 0.0052, segs=32)
        rod(tips, (0, y + 0.021, z), (0, y + 0.026, z), 0.0048, segs=32)
    part('TD_Nozzles', noz, col, m['steel'], grp, bevel=0.0005)
    t = part('TD_NozzleTips', tips, col, m['nozzle_tip'], grp, bevel=0.0006)
    cuts = []
    for dz in NOZZLE_DZ:
        bm = bmesh.new()
        box(bm, (0.0016, 0.004, 0.014), loc=(0, y + 0.027, LANCE_Z + dz))
        cuts.append(cutter(f'cut_slot{dz}', bm, col))
    cut(t, cuts)
    return grp


def build_gear(m, col, root):
    grp = empty('TD_GrpGear', col, root)
    top = UNDER - 0.0045
    legs, joints, foam = bmesh.new(), bmesh.new(), bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            p0 = Vector((sx * 0.072, sy * 0.06, top - 0.012))
            p1 = Vector((sx * 0.17, sy * 0.1, -0.292))
            rod(legs, p0, p1, 0.007, segs=28, hollow=0.0058)
            box(joints, (0.024, 0.022, 0.016), loc=p0 + Vector((0, 0, 0.004)))
            box(joints, (0.022, 0.026, 0.024), loc=(sx * 0.17, sy * 0.1, -0.298))
        rod(legs, (sx * 0.17, -0.215, -0.3), (sx * 0.17, 0.215, -0.3), 0.008, segs=32, hollow=0.0068)
        for sy in (-1, 1):
            rod(foam, (sx * 0.17, sy * 0.215, -0.3), (sx * 0.17, sy * 0.245, -0.3), 0.0105, segs=32)
    for sy in (-1, 1):
        mid = Vector((0.121, sy * 0.08, -0.152))
        rod(legs, (-mid.x, mid.y, mid.z), mid, 0.0042, segs=20, hollow=0.0034)
        for sx in (-1, 1):
            box(joints, (0.016, 0.016, 0.014), loc=(sx * mid.x, mid.y, mid.z))
    part('TD_GearTubes', legs, col, m['carbon_tube'], grp, angle=20)
    part('TD_GearJoints', joints, col, m['gunmetal'], grp, bevel=0.0015)
    part('TD_GearFoam', foam, col, m['foam'], grp, bevel=0.002, segs=3)
    return grp


# ---------------------------------------------------------------- tether

TETHER_N = 160


def build_tether(m):
    col = coll('TD Tether')
    objs = []
    for name, r, mat in (('TD_TetherCable', 0.0046, m['cable']), ('TD_TetherHose', 0.0052, m['hose'])):
        cu = bpy.data.curves.get(name) or bpy.data.curves.new(name, 'CURVE')
        cu.splines.clear()
        cu.dimensions = '3D'
        cu.bevel_depth = r
        cu.bevel_resolution = 4
        cu.use_fill_caps = True
        cu.materials.clear()
        cu.materials.append(mat)
        sp = cu.splines.new('POLY')
        sp.points.add(TETHER_N - 1)
        objs.append(obj(name, cu, col))
    me = bpy.data.meshes.get('TD_TetherClips') or bpy.data.meshes.new('TD_TetherClips')
    if not me.materials:
        me.materials.append(m['plastic'])
    objs.append(obj('TD_TetherClips', me, col))
    return objs


def bezier(P, t):
    return (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t * t * P[2] + t ** 3 * P[3]


def set_tether(top, c1, c2, end, phase=0.0, pitch=0.32, sep=0.0052):
    """The tether hangs from `top` along a bezier to `end`; its two strands twist around each other."""
    P = [Vector(top), Vector(c1), Vector(c2), Vector(end)]
    # sample evenly by arc length
    raw = [bezier(P, k / 600) for k in range(601)]
    acc = [0.0]
    for k in range(1, 601):
        acc.append(acc[-1] + (raw[k] - raw[k - 1]).length)
    total = acc[-1]
    pts = []
    j = 0
    for k in range(TETHER_N):
        s = total * k / (TETHER_N - 1)
        while j < 599 and acc[j + 1] < s:
            j += 1
        f = (s - acc[j]) / max(1e-9, acc[j + 1] - acc[j])
        pts.append((raw[j].lerp(raw[j + 1], f), s))
    strands = ([], [])
    ref = Vector((1, 0, 0))
    clips = bmesh.new()
    next_clip = 0.12
    for k, (p, s) in enumerate(pts):
        a = pts[max(0, k - 1)][0]
        b = pts[min(TETHER_N - 1, k + 1)][0]
        T = (b - a).normalized()
        N = T.cross(ref).normalized()
        B = T.cross(N)
        th = TAU * s / pitch + phase
        off = (math.cos(th) * N + math.sin(th) * B) * sep
        # the first few centimetres come straight out of the bellows side by side
        w = min(1.0, s / 0.05)
        strands[0].append(p + off * w)
        strands[1].append(p - off * w)
        if s > next_clip:
            next_clip += 0.4
            rot = T.to_track_quat('Z', 'Y').to_euler()
            tube(clips, 0.0118, 0.0102, 0.007, loc=p, rot=rot, segs=24)
    for name, st in zip(('TD_TetherCable', 'TD_TetherHose'), strands):
        sp = bpy.data.curves[name].splines[0]
        for pt, v in zip(sp.points, st):
            pt.co = (v.x, v.y, v.z, 1)
    me = bpy.data.meshes['TD_TetherClips']
    clips.to_mesh(me)
    clips.free()
    finish(me)


def build_systems(m, root):
    col = coll('TD Drone')
    m['nozzle_tip'] = principled('TD_NozzleTip', (0.75, 0.08, 0.04), 0.0, 0.38)
    hub = build_hub(m, col, root)
    water = build_water(m, col, root)
    gear = build_gear(m, col, root)
    build_tether(m)
    return hub, water, gear
