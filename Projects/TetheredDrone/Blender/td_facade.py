# The washing scene: a glass curtain wall ten storeys up, dirty glass that the spray cleans,
# a sky, the buildings across the street (seen only in the glass), sun, probes and the camera.
# The facade's glass face is the plane y = 0, facing -Y, towards the drone.

COL_W = 1.5           # mullion spacing
FLOOR_H = 3.6
SPANDREL = 0.45       # half-height of the opaque band at each floor slab
FLOORS = range(5, 12)
COLUMNS = range(-5, 8)
WORK_Z = 30.62        # the drone's working height, middle of the 9th-floor glass


def clean_controls(nt):
    """Value nodes the render script drives every frame."""
    vals = {}
    for k, (name, v) in enumerate((('XStart', 0.0), ('XNow', -99.0), ('ZC', WORK_Z), ('H', 0.3), ('Wet', 0.0), ('Spray', 0.0))):
        n = add(nt, 'ShaderNodeValue', (-2600, 600 - k * 120))
        n.name = n.label = name
        n.outputs[0].default_value = v
        vals[name] = n.outputs[0]
    return vals


def smooth(nt, edge0, edge1, x, loc):
    """smoothstep from edge0 to edge1 (either order)."""
    mr = add(nt, 'ShaderNodeMapRange', loc)
    mr.interpolation_type = 'SMOOTHSTEP'
    mr.clamp = True
    for sock_name, v in (('From Min', edge0), ('From Max', edge1)):
        if isinstance(v, (int, float)):
            mr.inputs[sock_name].default_value = v
        else:
            link(nt, v, mr.inputs[sock_name])
    link(nt, x, mr.inputs['Value'])
    return mr.outputs[0]


def glass_material():
    """Coated glass with grime and streaks. A band the spray has passed is clean and wet, and water runs down from it."""
    m, nt, out = node_mat('TD_FacadeGlass')
    v = clean_controls(nt)
    geo = add(nt, 'ShaderNodeNewGeometry', (-2600, -200))
    sep = add(nt, 'ShaderNodeSeparateXYZ', (-2400, -200))
    link(nt, geo.outputs['Position'], sep.inputs[0])
    X, Z = sep.outputs['X'], sep.outputs['Z']
    tc = add(nt, 'ShaderNodeTexCoord', (-2600, -500))
    gsep = add(nt, 'ShaderNodeSeparateXYZ', (-2400, -500))
    link(nt, tc.outputs['Generated'], gsep.inputs[0])
    gz = gsep.outputs['Z']
    oi = add(nt, 'ShaderNodeObjectInfo', (-2600, -800))

    # ---- dirt: broad blotches, vertical streaks from the transom above, and dust collected low on each pane
    n1 = add(nt, 'ShaderNodeTexNoise', (-2100, 300))
    n1.inputs['Scale'].default_value = 1.6
    n1.inputs['Detail'].default_value = 6
    n1.inputs['Roughness'].default_value = 0.6
    link(nt, geo.outputs['Position'], n1.inputs['Vector'])
    blot = smooth(nt, 0.38, 0.72, n1.outputs['Fac'], (-1900, 300))
    smp = add(nt, 'ShaderNodeMapping', (-2200, 0))
    smp.inputs['Scale'].default_value = (14, 1, 0.55)
    link(nt, geo.outputs['Position'], smp.inputs['Vector'])
    n2 = add(nt, 'ShaderNodeTexNoise', (-2000, 0))
    n2.inputs['Scale'].default_value = 3.0
    n2.inputs['Detail'].default_value = 3
    link(nt, smp.outputs[0], n2.inputs['Vector'])
    streak = smooth(nt, 0.55, 0.75, n2.outputs['Fac'], (-1800, 0))
    top_fade = smooth(nt, 0.35, 0.95, gz, (-1800, -300))
    streaks = math_node(nt, 'MULTIPLY', streak, top_fade, (-1600, 0))
    low = smooth(nt, 0.3, 0.0, gz, (-1800, -450))
    d1 = math_node(nt, 'MULTIPLY', blot, 0.4, (-1600, 300))
    d2 = math_node(nt, 'ADD', d1, math_node(nt, 'MULTIPLY', streaks, 0.5, (-1600, 150)), (-1450, 200))
    d3 = math_node(nt, 'ADD', d2, math_node(nt, 'MULTIPLY', low, 0.6, (-1600, -450)), (-1300, 150))
    base_dirt = math_node(nt, 'ADD', d3, 0.34, (-1150, 150))
    dirt0 = math_node(nt, 'MINIMUM', base_dirt, 1.0, (-1000, 150))
    # fine speckle
    n3 = add(nt, 'ShaderNodeTexNoise', (-2000, -1000))
    n3.inputs['Scale'].default_value = 60
    n3.inputs['Detail'].default_value = 2
    link(nt, geo.outputs['Position'], n3.inputs['Vector'])
    speck = smooth(nt, 0.5, 0.75, n3.outputs['Fac'], (-1800, -1000))

    # ---- the cleaned band
    dz = math_node(nt, 'ABSOLUTE', math_node(nt, 'SUBTRACT', Z, v['ZC'], (-2100, 900)), None, (-1950, 900))
    n4 = add(nt, 'ShaderNodeTexNoise', (-2300, 1100))
    n4.inputs['Scale'].default_value = 5
    link(nt, geo.outputs['Position'], n4.inputs['Vector'])
    wob = math_node(nt, 'MULTIPLY', math_node(nt, 'SUBTRACT', n4.outputs['Fac'], 0.5, (-2100, 1100)), 0.12, (-1950, 1100))
    Hw = math_node(nt, 'ADD', v['H'], wob, (-1800, 1100))
    H_in = math_node(nt, 'SUBTRACT', Hw, 0.05, (-1650, 1150))
    band = smooth(nt, Hw, H_in, dz, (-1500, 950))
    lead_a = math_node(nt, 'ADD', v['XNow'], 0.05, (-1800, 800))
    lead_b = math_node(nt, 'SUBTRACT', v['XNow'], 0.05, (-1800, 700))
    ahead = smooth(nt, lead_a, lead_b, X, (-1500, 750))
    st_a = math_node(nt, 'SUBTRACT', v['XStart'], 0.06, (-1800, 600))
    behind = smooth(nt, st_a, v['XStart'], X, (-1500, 600))
    swept = math_node(nt, 'MULTIPLY', ahead, behind, (-1300, 700))
    clean = math_node(nt, 'MULTIPLY', swept, band, (-1150, 850))
    # water running down from the band: longer the longer ago the spray passed
    since = math_node(nt, 'MAXIMUM', math_node(nt, 'SUBTRACT', v['XNow'], X, (-1800, 450)), 0.0, (-1650, 450))
    run_len = math_node(nt, 'MINIMUM', math_node(nt, 'MULTIPLY', since, 1.4, (-1500, 450)), 2.2, (-1350, 450))
    rmp = add(nt, 'ShaderNodeMapping', (-2200, 300 - 900))
    rmp.inputs['Scale'].default_value = (11, 1, 0.35)
    link(nt, geo.outputs['Position'], rmp.inputs['Vector'])
    n5 = add(nt, 'ShaderNodeTexNoise', (-2000, -600))
    n5.inputs['Scale'].default_value = 2.0
    n5.inputs['Distortion'].default_value = 0.6
    link(nt, rmp.outputs[0], n5.inputs['Vector'])
    rivulet = smooth(nt, 0.58, 0.68, n5.outputs['Fac'], (-1800, -600))
    rl = math_node(nt, 'MULTIPLY', run_len, n5.outputs['Fac'], (-1200, 450))
    bottom = math_node(nt, 'SUBTRACT', v['ZC'], v['H'], (-1500, 300))
    depth = math_node(nt, 'SUBTRACT', bottom, Z, (-1350, 300))
    below = math_node(nt, 'MULTIPLY', smooth(nt, -0.02, 0.03, depth, (-1200, 300)), smooth(nt, rl, math_node(nt, 'SUBTRACT', rl, 0.08, (-1150, 200)), depth, (-1050, 300)), (-900, 350))
    started = smooth(nt, v['XStart'], math_node(nt, 'ADD', v['XStart'], 0.1, (-1300, 150)), X, (-1050, 150))
    runoff = math_node(nt, 'MULTIPLY', math_node(nt, 'MULTIPLY', below, rivulet, (-750, 350)), started, (-600, 350))
    run_c = math_node(nt, 'MULTIPLY', runoff, 0.8, (-450, 350))
    clean_all = math_node(nt, 'MINIMUM', math_node(nt, 'ADD', clean, run_c, (-300, 600)), 1.0, (-150, 600))
    wet = math_node(nt, 'MINIMUM', math_node(nt, 'ADD', math_node(nt, 'MULTIPLY', clean, v['Wet'], (-300, 800)), runoff, (-150, 800)), 1.0, (0, 800))
    dirt = math_node(nt, 'MULTIPLY', dirt0, math_node(nt, 'SUBTRACT', 1.0, clean_all, (0, 300)), (150, 200))
    dirt_s = math_node(nt, 'MINIMUM', math_node(nt, 'ADD', dirt, math_node(nt, 'MULTIPLY', speck, math_node(nt, 'MULTIPLY', dirt, 0.25, (-150, -1000)), (0, -1000)), (150, 0)), 1.0, (300, 100))

    # ---- what is behind the glass: dark offices, with blinds lowered on some panes
    rnd = math_node(nt, 'GREATER_THAN', oi.outputs['Random'], 0.62, (-1800, -800))
    bl = add(nt, 'ShaderNodeTexWave', (-1800, -1300), wave_type='BANDS', bands_direction='Z')
    bl.inputs['Scale'].default_value = 60
    link(nt, tc.outputs['Generated'], bl.inputs['Vector'])
    blind_h = smooth(nt, 0.55, 0.5, gz, (-1600, -1300))
    blinds = math_node(nt, 'MULTIPLY', math_node(nt, 'MULTIPLY', rnd, blind_h, (-1400, -1200)), math_node(nt, 'ADD', math_node(nt, 'MULTIPLY', bl.outputs['Fac'], 0.4, (-1600, -1450)), 0.6, (-1450, -1450)), (-1250, -1250))
    interior = add(nt, 'ShaderNodeMix', (-900, -1200), data_type='RGBA')
    sock(interior.inputs, 'A_Color').default_value = (0.006, 0.008, 0.01, 1)
    sock(interior.inputs, 'B_Color').default_value = (0.09, 0.09, 0.085, 1)
    link(nt, blinds, sock(interior.inputs, 'Factor_Float'))

    # ---- shading: a coated, reflective pane, a dull grime film over it, and a wet sheen
    glass = add(nt, 'ShaderNodeBsdfPrincipled', (600, 400))
    link(nt, sock(interior.outputs, 'Result_Color'), glass.inputs['Base Color'])
    glass.inputs['Roughness'].default_value = 0.0
    glass.inputs['IOR'].default_value = 1.52
    glass.inputs['Specular IOR Level'].default_value = 1.0
    glass.inputs['Coat Weight'].default_value = 1.0
    glass.inputs['Coat Roughness'].default_value = 0.0
    glass.inputs['Coat Tint'].default_value = (0.75, 0.86, 0.92, 1)
    rough = add(nt, 'ShaderNodeMapRange', (450, 0))
    rough.inputs['To Min'].default_value = 0.0
    rough.inputs['To Max'].default_value = 0.06
    link(nt, dirt_s, rough.inputs['Value'])
    link(nt, rough.outputs[0], glass.inputs['Coat Roughness'])
    link(nt, rough.outputs[0], glass.inputs['Roughness'])
    film = add(nt, 'ShaderNodeBsdfPrincipled', (600, -200))
    film.inputs['Base Color'].default_value = (0.4, 0.37, 0.32, 1)
    film.inputs['Roughness'].default_value = 0.8
    film_amt = math_node(nt, 'MULTIPLY', dirt_s, 0.64, (450, -350))
    mix = add(nt, 'ShaderNodeMixShader', (850, 200))
    link(nt, film_amt, mix.inputs['Fac'])
    link(nt, glass.outputs[0], mix.inputs[1])
    link(nt, film.outputs[0], mix.inputs[2])
    # water: beads and a thin sheet that catch the sky
    vor = add(nt, 'ShaderNodeTexVoronoi', (-300, -1600), feature='SMOOTH_F1')
    vor.inputs['Scale'].default_value = 160
    link(nt, geo.outputs['Position'], vor.inputs['Vector'])
    bump = add(nt, 'ShaderNodeBump', (300, -900))
    bump.inputs['Distance'].default_value = 0.0006
    link(nt, wet, bump.inputs['Strength'])
    bead = math_node(nt, 'MULTIPLY', vor.outputs['Distance'], wet, (0, -1500))
    link(nt, bead, bump.inputs['Height'])
    link(nt, bump.outputs['Normal'], glass.inputs['Coat Normal'])
    sheen = add(nt, 'ShaderNodeBsdfGlossy', (850, -200))
    sheen.inputs['Roughness'].default_value = 0.04
    sheen.inputs['Color'].default_value = (0.5, 0.55, 0.6, 1)
    link(nt, bump.outputs['Normal'], sheen.inputs['Normal'])
    lw = add(nt, 'ShaderNodeLayerWeight', (600, -500))
    lw.inputs['Blend'].default_value = 0.35
    link(nt, bump.outputs['Normal'], lw.inputs['Normal'])
    sheen_amt = math_node(nt, 'MULTIPLY', wet, math_node(nt, 'ADD', math_node(nt, 'MULTIPLY', lw.outputs['Fresnel'], 0.5, (750, -650)), 0.12, (900, -650)), (1050, -500))
    add_s = add(nt, 'ShaderNodeMixShader', (1100, 100))
    link(nt, sheen_amt, add_s.inputs['Fac'])
    link(nt, mix.outputs[0], add_s.inputs[1])
    link(nt, sheen.outputs[0], add_s.inputs[2])
    link(nt, add_s.outputs[0], out.inputs[0])
    out.location = (1300, 100)
    return m


def facade_materials(m):
    m['mullion'] = brushed('TD_Mullion', (0.16, 0.165, 0.17), rough=0.3, aniso=0.3, scale=400)
    m['spandrel'] = principled('TD_Spandrel', (0.03, 0.04, 0.05), 0.0, 0.18, spec=0.9, coat=1.0, coat_rough=0.05)
    m['slab'] = principled('TD_Slab', (0.35, 0.34, 0.32), 0.0, 0.8)
    m['glass'] = glass_material()
    m['city'] = city_material()


def city_material():
    """Buildings across the street: concrete frames with rows of windows, seen only in reflections."""
    m, nt, out = node_mat('TD_City')
    tc = add(nt, 'ShaderNodeTexCoord', (-900, 0))
    br = add(nt, 'ShaderNodeTexBrick', (-650, 0))
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.35
    br.inputs['Brick Width'].default_value = 1.6
    br.inputs['Row Height'].default_value = 3.4
    br.inputs['Color1'].default_value = (0.1, 0.13, 0.17, 1)
    br.inputs['Color2'].default_value = (0.16, 0.18, 0.2, 1)
    br.inputs['Mortar'].default_value = (0.55, 0.52, 0.47, 1)
    br.offset = 0.0
    mp = add(nt, 'ShaderNodeMapping', (-800, 0))
    mp.inputs['Rotation'].default_value = (math.pi / 2, 0, 0)
    link(nt, tc.outputs['Object'], mp.inputs['Vector'])
    link(nt, mp.outputs[0], br.inputs['Vector'])
    p = add(nt, 'ShaderNodeBsdfPrincipled', (-300, 0))
    p.inputs['Roughness'].default_value = 0.5
    link(nt, br.outputs['Color'], p.inputs['Base Color'])
    link(nt, p.outputs[0], out.inputs[0])
    return m


def sky_world():
    w = bpy.data.worlds.get('TD_SkyWorld') or bpy.data.worlds.new('TD_SkyWorld')
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = add(nt, 'ShaderNodeOutputWorld', (900, 0))
    bg = add(nt, 'ShaderNodeBackground', (700, 0))
    tc = add(nt, 'ShaderNodeTexCoord', (-900, 0))
    sep = add(nt, 'ShaderNodeSeparateXYZ', (-700, 0))
    link(nt, tc.outputs['Generated'], sep.inputs[0])
    # world directions run from -1 (straight down) to 1 (straight up); the ramp wants 0 to 1, horizon at 0.5
    hz = add(nt, 'ShaderNodeMapRange', (-600, 0))
    hz.inputs['From Min'].default_value = -1.0
    link(nt, sep.outputs['Z'], hz.inputs['Value'])
    ramp = add(nt, 'ShaderNodeValToRGB', (-450, 0))
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.2, 0.2, 0.21, 1)
    e[1].position, e[1].color = 1.0, (0.09, 0.2, 0.48, 1)
    for pos, c in ((0.48, (0.42, 0.44, 0.46, 1)), (0.505, (0.82, 0.86, 0.9, 1)), (0.6, (0.42, 0.56, 0.78, 1))):
        el = e.new(pos)
        el.color = c
    link(nt, hz.outputs[0], ramp.inputs['Fac'])
    # soft clouds in the upper sky
    n = add(nt, 'ShaderNodeTexNoise', (-700, -300))
    n.inputs['Scale'].default_value = 2.2
    n.inputs['Detail'].default_value = 8
    n.inputs['Roughness'].default_value = 0.62
    mp = add(nt, 'ShaderNodeMapping', (-900, -300))
    mp.inputs['Scale'].default_value = (1, 1, 3.5)
    link(nt, tc.outputs['Generated'], mp.inputs['Vector'])
    link(nt, mp.outputs[0], n.inputs['Vector'])
    cl = smooth(nt, 0.5, 0.72, n.outputs['Fac'], (-450, -300))
    up = smooth(nt, 0.52, 0.62, hz.outputs[0], (-450, -500))
    cmask = math_node(nt, 'MULTIPLY', cl, up, (-250, -350))
    mix = add(nt, 'ShaderNodeMix', (200, 0), data_type='RGBA')
    sock(mix.inputs, 'B_Color').default_value = (0.95, 0.96, 0.98, 1)
    link(nt, ramp.outputs['Color'], sock(mix.inputs, 'A_Color'))
    link(nt, math_node(nt, 'MULTIPLY', cmask, 0.85, (0, -350)), sock(mix.inputs, 'Factor_Float'))
    link(nt, sock(mix.outputs, 'Result_Color'), bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.0
    link(nt, bg.outputs[0], out.inputs[0])
    w.use_fake_user = True   # kept in the file while the studio world is active
    return w


def build_facade(m):
    col = coll('TD Facade')
    facade_materials(m)
    rng = random.Random(5)
    x0, x1 = COLUMNS.start * COL_W, (COLUMNS.stop - 1) * COL_W
    z0, z1 = FLOORS.start * FLOOR_H, (FLOORS.stop - 1) * FLOOR_H
    # panes: one object each, every one tilted a hair differently, like real insulated units
    for j in COLUMNS:
        for k in FLOORS:
            if k == FLOORS.stop - 1:
                continue
            xa, xb = j * COL_W + 0.03, (j + 1) * COL_W - 0.03
            za, zb = k * FLOOR_H + SPANDREL, (k + 1) * FLOOR_H - SPANDREL
            if j == COLUMNS.stop - 1:
                continue
            bm = bmesh.new()
            vs = [bm.verts.new(p) for p in ((xa, 0, za), (xb, 0, za), (xb, 0, zb), (xa, 0, zb))]
            bm.faces.new(vs)
            me = to_mesh(f'TD_Pane{j}_{k}', bm, smooth=False, mats=[m['glass']])
            ob = obj(f'TD_Pane{j}_{k}', me, col)
            c = Vector(((xa + xb) / 2, 0, (za + zb) / 2))
            me.transform(Matrix.Translation(-c))
            ob.location = c
            ob.rotation_euler = (math.radians(rng.uniform(-0.12, 0.12)), 0, math.radians(rng.uniform(-0.18, 0.18)))
            sub = ob.modifiers.new('sub', 'SUBSURF')
            sub.levels = sub.render_levels = 0
    # spandrel bands
    bm = bmesh.new()
    for k in FLOORS:
        box(bm, (x1 - x0, 0.02, 2 * SPANDREL), loc=((x0 + x1) / 2, 0.012, k * FLOOR_H))
    part('TD_Spandrels', bm, col, m['spandrel'], smooth=False)
    # mullions: a pressure cap and a deeper fin
    bm = bmesh.new()
    for j in COLUMNS:
        x = j * COL_W
        box(bm, (0.065, 0.06, z1 - z0 + 1.0), loc=(x, -0.03, (z0 + z1) / 2))
        box(bm, (0.02, 0.16, z1 - z0 + 1.0), loc=(x, -0.12, (z0 + z1) / 2))
    for k in FLOORS:
        for s in (-1, 1):
            box(bm, (x1 - x0, 0.05, 0.06), loc=((x0 + x1) / 2, -0.025, k * FLOOR_H + s * SPANDREL))
    mul = part('TD_Mullions', bm, col, m['mullion'], bevel=0.004, segs=2)
    # the city behind the camera, reflected in the glass
    for k, (x, y, w, d, h) in enumerate(((-34, -70, 26, 14, 14), (-4, -78, 22, 16, 19), (26, -66, 20, 12, 11),
                                           (-14, -120, 30, 20, 26), (52, -100, 26, 18, 22), (-62, -92, 24, 16, 17),
                                           (12, -150, 18, 18, 34))):
        bm = bmesh.new()
        box(bm, (w, d, h), loc=(x, y, h / 2))
        part(f'TD_City{k}', bm, col, m['city'], smooth=False)
    bm = bmesh.new()
    box(bm, (400, 400, 0.2), loc=(0, -100, -0.1))
    part('TD_Street', bm, col, m['slab'], smooth=False)
    # light: sun from the front left and a little behind the camera
    sun_data = bpy.data.lights.get('TD_Sun') or bpy.data.lights.new('TD_Sun', 'SUN')
    sun_data.energy = 4.2
    sun_data.angle = math.radians(1.2)
    sun_data.color = (1.0, 0.95, 0.88)
    sun = obj('TD_Sun', sun_data, col)
    sun.rotation_euler = Vector((0.55, 0.72, -0.42)).to_track_quat('-Z', 'Y').to_euler()
    # probes: a plane on the glass for its reflections, and a sphere around the drone
    pp = bpy.data.lightprobes.get('TD_GlassProbe') or bpy.data.lightprobes.new('TD_GlassProbe', 'PLANE')
    pp.influence_distance = 0.25
    probe = obj('TD_GlassProbe', pp, col, loc=(1.5, -0.002, WORK_Z), rot=(math.pi / 2, 0, 0), scale=(9, 6, 1))
    sp = bpy.data.lightprobes.get('TD_DroneProbe') or bpy.data.lightprobes.new('TD_DroneProbe', 'SPHERE')
    sp.influence_distance = 3.5
    obj('TD_DroneProbe', sp, col, loc=(1.6, -1.6, WORK_Z))
    # camera
    cd = bpy.data.cameras.get('TD_WashCam') or bpy.data.cameras.new('TD_WashCam')
    cd.lens = 32
    cd.clip_start = 0.05
    cd.clip_end = 600
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = 5.6
    cam = obj('TD_WashCam', cd, col, loc=(-1.6, -4.2, WORK_Z - 0.7))
    tgt = empty('TD_WashTarget', col, loc=(0.6, -0.8, WORK_Z))
    c = cam.constraints.new('TRACK_TO')
    c.target = tgt
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
    cd.dof.focus_object = bpy.data.objects['TD_Drone']
    return col


def set_clean(x_start, x_now, zc, h, wet, spray):
    nt = bpy.data.materials['TD_FacadeGlass'].node_tree
    for name, v in (('XStart', x_start), ('XNow', x_now), ('ZC', zc), ('H', h), ('Wet', wet), ('Spray', spray)):
        nt.nodes[name].outputs[0].default_value = v
